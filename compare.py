"""Compare binary and multiple-choice decisions against supplied contexts."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

from openrouter_backend import predict_messages
from cloudflare_backend import predict_messages as predict_cloudflare
from model_config import (default_model_keys as configured_defaults,
                          model_eligibility, is_hosted)
from refund_demo import EXAMPLES, QUESTIONS

ROOT = Path(__file__).resolve().parent
MODELS = json.loads((ROOT / "models.json").read_text())
QUESTION = QUESTIONS["refund_requested"]["instructions"]


def default_model_keys():
    """Configured models only; optional integrations remain unselected."""
    return configured_defaults(MODELS)


def validate_questions(questions=None):
    questions = QUESTIONS if questions is None else questions
    if not isinstance(questions, dict) or not questions:
        raise ValueError("Provide at least one question.")
    clean = {}
    for qid, question in questions.items():
        if not isinstance(qid, str) or not qid.strip() or qid != qid.strip():
            raise ValueError("Question IDs must be nonempty strings without surrounding spaces.")
        if not isinstance(question, dict) or question.get("type", "noul") not in {"noul", "choice"}:
            raise ValueError(f"Question {qid}: supported types are noul (yes/no) and choice.")
        instructions = question.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError(f"Question {qid}: enter a question.")
        kind = question.get("type", "noul")
        clean[qid] = {"type": kind, "instructions": instructions.strip()}
        if kind == "choice":
            criteria = question.get("criteria")
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= 255:
                raise ValueError(f"Question {qid}: provide 2–255 named choices.")
            if any(not isinstance(k, str) or not k.strip() or k != k.strip() for k in criteria):
                raise ValueError(f"Question {qid}: choice names must be nonempty, without surrounding spaces.")
            if any(not isinstance(v, str) or not v.strip() for v in criteria.values()):
                raise ValueError(f"Question {qid}: every choice needs a meaning.")
            clean[qid]["criteria"] = {k: v.strip() for k, v in criteria.items()}
    return clean


def validate_cases(cases, questions=None):
    questions = validate_questions(questions)
    if not isinstance(cases, list) or not cases:
        raise ValueError("Provide at least one case.")
    ids = set()
    clean = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"Case {index + 1} must be an object.")
        name = case.get("id", str(index + 1))
        message = case.get("message")
        if not isinstance(name, str) or not name.strip() or name.strip() in ids:
            raise ValueError("Case IDs must be unique, nonempty strings.")
        name = name.strip()
        if not isinstance(message, str) or not message.strip():
            raise ValueError(f"Case {name}: enter a context.")
        labels = case.get("expected_answers")
        if labels is None:
            expected = case.get("expected")
            if expected is not None and type(expected) is not bool:
                raise ValueError(f"Case {name}: expected must be true, false, or null.")
            if expected is not None and questions != QUESTIONS:
                raise ValueError(f"Case {name}: use expected_answers keyed by question ID for custom questions.")
            labels = {"refund_requested": expected} if questions == QUESTIONS else {}
        if not isinstance(labels, dict) or set(labels) - set(questions):
            raise ValueError(f"Case {name}: expected_answers must use the current question IDs.")
        for qid, value in labels.items():
            if value is None:
                continue
            question = questions[qid]
            if question["type"] == "noul" and type(value) is not bool:
                raise ValueError(f"Case {name}, {qid}: expected must be true, false, or null.")
            if question["type"] == "choice" and (not isinstance(value, str) or value not in question["criteria"]):
                raise ValueError(f"Case {name}, {qid}: expected must be one of its choice names or null.")
        labels = {qid: labels.get(qid) for qid in questions}
        ids.add(name)
        clean.append({"id": name, "message": message.strip(), "expected_answers": labels,
                      "expected": labels.get("refund_requested") if questions == QUESTIONS else None})
    return clean


def display_answer(value):
    return "Unknown" if value is None else ("Yes" if value else "No") if type(value) is bool else str(value)


LOG_LOSS_DESCRIPTION = (
    "mean -ln P(expected) in nats over valid labeled successes; "
    "zero truth probability is infinite (null value with explicit status and count)"
)


def log_loss_fields(rows):
    """JSON-safe log loss, derived from normalized probabilities, including legacy rows.

    Null values mean either infinite or unavailable, distinguished by status.
    Exact zero probabilities are counted, never clipped. Failures are not scored.
    """
    losses, zeros = [], 0
    for row in rows:
        expected = row.get("expected")
        if row.get("status") != "ok" or expected is None:
            continue
        kind = row.get("question_type", "noul")
        if kind == "choice" and isinstance(expected, str):
            probabilities = row.get("probabilities")
            probability = probabilities.get(expected) if isinstance(probabilities, dict) else None
        elif kind == "noul" and type(expected) is bool:
            probability = row.get("probability_yes")
        else:
            continue
        if (isinstance(probability, bool) or not isinstance(probability, (int, float))
                or not math.isfinite(probability) or not 0 <= probability <= 1):
            continue
        if kind == "noul" and not expected:
            probability = 1 - probability
        if probability == 0:
            zeros += 1
        else:
            losses.append(0.0 if probability == 1 else -math.log(probability))
    count = len(losses) + zeros
    status = "infinite" if zeros else "finite" if count else "unavailable"
    return {"log_loss": statistics.mean(losses) if status == "finite" else None,
            "log_loss_status": status, "log_loss_scored": count,
            "log_loss_zero_probability_count": zeros}


def display_log_loss(value, status):
    return "∞" if status == "infinite" else f"{value:.6g}" if status == "finite" else "Unavailable"


def add_log_loss(comparison):
    """Enrich a new or saved export without changing its inputs or timestamp."""
    data = deepcopy(comparison)
    data["results"] = [{**row, **log_loss_fields([row])} for row in data["results"]]
    data["summary"] = summarize(data["results"])
    data["question_summaries"] = {
        qid: summarize([r for r in data["results"] if r.get("question_id", "refund_requested") == qid])
        for qid in data.get("questions") or {"refund_requested": None}
    }
    data.setdefault("scoring", {})["log_loss"] = LOG_LOSS_DESCRIPTION
    return data


def normalize_result(raw, question_id="refund_requested", question=None):
    answer = raw["answers"][question_id]
    if question is not None and question["type"] == "choice":
        supplied = answer.get("probabilities")
        criteria = question["criteria"]
        if not isinstance(supplied, dict) or set(supplied) != set(criteria):
            raise ValueError("Choice probabilities must contain exactly the supplied choice names.")
        probabilities = {}
        for name in criteria:
            value = supplied[name]
            if isinstance(value, bool):
                raise ValueError("A boolean is not a choice probability.")
            p = float(value)
            if not math.isfinite(p) or not 0 <= p <= 1:
                raise ValueError("Invalid choice probability.")
            probabilities[name] = p
        total = sum(probabilities.values())
        # Several native runtimes round each probability to four decimals.
        if total <= 0 or abs(total - 1) > max(.001, len(criteria) * .000051):
            raise ValueError("Choice probabilities must sum to one (within native rounding tolerance).")
        decision = answer.get("choice")
        if not isinstance(decision, str) or decision not in criteria:
            raise ValueError("Model selected an unknown or missing choice.")
        if probabilities[decision] < max(probabilities.values()) - 1e-6:
            raise ValueError("Selected choice does not match the largest probability.")
        probabilities = {k: p / total for k, p in probabilities.items()}
        return {"decision": decision, "probabilities": probabilities,
                "selected_probability": probabilities[decision],
                "returned_confidence": answer.get("confidence"),
                "returned_answer_confidence": answer.get("answer_confidence")}
    value = answer["noul"]
    if isinstance(value, bool):
        raise ValueError("A boolean decision is not a probability.")
    probability = float(value)
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("Model returned an invalid yes probability.")
    result = {
        "probability_yes": probability, "probability_no": 1 - probability,
        "decision": probability >= 0.5, "selected_probability": max(probability, 1 - probability),
        "returned_confidence": answer.get("confidence"),
        "returned_answer_confidence": answer.get("answer_confidence"),
    }
    # Retain the old refund export field only for the refund question.
    if question_id == "refund_requested":
        result["wants_refund"] = result["decision"]
    return result


def run_model(key, cases, device="auto", timeout=1800, questions=None):
    """Load once per model and evaluate every question for each context."""
    if key not in MODELS:
        raise ValueError(f"Unknown model {key}")
    questions = validate_questions(questions)
    cases = validate_cases(cases, questions)
    environment = MODELS[key].get("environment", ".venv" if key == "laya" else ".venv-models")
    python = ROOT / environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    common = {"model_key": key, **MODELS[key]}
    error, packet, log_path, diagnostic = None, {}, None, ""
    try:
        configuration = model_eligibility(MODELS[key])
        if not configuration.enabled:
            packet = {"results": [{"status": "error", "error": configuration.error} for _ in cases],
                      "device": configuration.provider, "load_seconds": None}
        elif MODELS[key].get("backend") == "openrouter":
            packet = predict_messages([c["message"] for c in cases], questions, MODELS[key]["repo"])
        elif MODELS[key].get("backend") == "cloudflare":
            packet = predict_cloudflare([c["message"] for c in cases], questions, MODELS[key]["repo"])
        else:
            log_dir = ROOT / ".cache/logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w+", prefix=f"{key}-", suffix=".log", dir=log_dir, delete=False) as log:
                log_path = log.name
                completed = subprocess.run(
                    [str(python), str(ROOT / "model_worker.py"), key, "--device", device],
                    input=json.dumps({"messages": [c["message"] for c in cases], "questions": questions}),
                    text=True, stdout=subprocess.PIPE, stderr=log, cwd=ROOT, timeout=timeout,
                )
                log.flush()
                if completed.returncode:
                    raise RuntimeError(f"Model worker exited with code {completed.returncode}.")
                packet = json.loads(completed.stdout)
        if not isinstance(packet.get("results"), list) or len(packet["results"]) != len(cases):
            raise ValueError("Model returned the wrong number of context results.")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        if not isinstance(packet, dict):
            packet = {}
    if log_path:
        diagnostic = Path(log_path).read_text(errors="replace")[-6000:]
    rows = []
    for index, case in enumerate(cases):
        result = packet["results"][index] if not error else {}
        for qid, question in questions.items():
            expected = case["expected_answers"][qid]
            row = {**common, "case_id": case["id"], "message": case["message"],
                   "question_id": qid, "question": question["instructions"], "question_type": question["type"],
                   "criteria": question.get("criteria"), "expected": expected,
                   "status": "error", "device": packet.get("device"), "load_seconds": packet.get("load_seconds"),
                   "runtime": packet.get("runtime"), "log_path": log_path,
                   "execution": "hosted" if is_hosted(MODELS[key]) else "local"}
            if error:
                row.update(error=error)
            elif not isinstance(result, dict) or result.get("status") not in {"ok", "error"}:
                row.update(error="Invalid model output: missing or invalid status.")
            else:
                row.update(result)
                if result["status"] == "ok":
                    try:
                        row.update(normalize_result(result["raw_response"], qid, question))
                        if question["instructions"] != QUESTION:
                            row.pop("wants_refund", None)
                        row["correct"] = None if expected is None else row["decision"] == expected
                    except Exception as exc:
                        row.update(status="error", error=f"Invalid model output for {qid}: {exc}")
            if row["status"] == "error":
                row["diagnostics"] = diagnostic
            row.update(log_loss_fields([row]))
            rows.append(row)
    return rows


def ordered_model_keys(keys):
    """Use registry family/size order regardless of selection or arrival order."""
    return [key for key in MODELS if key in keys]


def ordered_results(rows):
    rank = {key: index for index, key in enumerate(MODELS)}
    return sorted(rows, key=lambda row: rank[row["model_key"]])


def summarize(rows):
    """Failures stay in coverage and correct/total denominators; count answer pairs."""
    summary = []
    for key in ordered_model_keys({r["model_key"] for r in rows}):
        group = [r for r in rows if r["model_key"] == key]
        successful = [r for r in group if r["status"] == "ok"]
        labelled = [r for r in group if r["expected"] is not None]
        scored = [r for r in successful if r["expected"] is not None]
        binary_scored = [r for r in scored if r.get("question_type", "noul") == "noul"]
        choice_scored = [r for r in scored if r.get("question_type") == "choice"]
        correct = sum(r["correct"] for r in scored)
        # All questions share one timed call per context. Count it once.
        timings = {}
        for row in successful:
            if row.get("inference_seconds") is not None:
                timings.setdefault(row["case_id"], row["inference_seconds"])
        summary.append({
            "model": MODELS[key]["name"], "cases": len(group), "contexts": len({r["case_id"] for r in group}),
            "answered": len(successful), "errors": len(group) - len(successful),
            "labelled": len(labelled), "correct": correct,
            "accuracy_on_answered": correct / len(scored) if scored else None,
            "correct_over_labelled": correct / len(labelled) if labelled else None,
            "coverage": len(successful) / len(group),
            "brier_score": statistics.mean((r["probability_yes"] - int(r["expected"])) ** 2 for r in binary_scored) if binary_scored else None,
            "choice_brier_score": statistics.mean(sum((p - int(k == r["expected"])) ** 2 for k, p in r["probabilities"].items()) for r in choice_scored) if choice_scored else None,
            **log_loss_fields(group),
            "mean_inference_seconds": statistics.mean(timings.values()) if timings else None,
            "load_seconds": group[0].get("load_seconds"),
        })
    return summary


def report(cases, keys, rows, questions=None):
    questions = validate_questions(questions)
    cases = validate_cases(cases, questions)
    keys, rows = ordered_model_keys(keys), ordered_results(rows)
    return add_log_loss({"schema_version": 3, "created_at": datetime.now(timezone.utc).isoformat(),
                     "question": next(iter(questions.values()))["instructions"] if len(questions) == 1 else None,
                     "questions": questions, "threshold": 0.5,
                     "scoring": {"noul": "mean (P(yes) - label)^2", "choice": "mean sum over choices (probability - one_hot_label)^2"}, "cases": cases,
                     "models": {k: MODELS[k] for k in keys}, "results": rows})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", default=EXAMPLES["Refund request"], help="Context to evaluate")
    parser.add_argument("--suite", type=Path, help="JSON cases with id, message, expected_answers; legacy refund expected is supported")
    question_group = parser.add_mutually_exclusive_group()
    question_group.add_argument("--question", help="One custom yes/no question (ID: question_1)")
    question_group.add_argument("--questions", type=Path, help="JSON question definitions: type, instructions, and criteria for choice")
    parser.add_argument("--models", nargs="+", choices=list(MODELS), default=default_model_keys(),
                        help="Configured models; optional integrations must be selected explicitly")
    parser.add_argument("--expected", help="Single-question label: yes/no/unknown for binary, or an exact choice name")
    parser.add_argument("--device", choices=["auto", "cpu", "mps", "cuda"], default="auto")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    configurations = [(key, model_eligibility(MODELS[key])) for key in args.models]
    blocked = [(key, eligibility) for key, eligibility in configurations if not eligibility.enabled]
    if blocked:
        parser.error("Unavailable models: " + " ".join(
            f"{MODELS[key]['name']}: {eligibility.error}" for key, eligibility in blocked))
    if not args.models:
        parser.error("No configured models available.")
    try:
        questions = validate_questions(json.loads(args.questions.read_text()) if args.questions else
                                       {"question_1": {"instructions": args.question}} if args.question else None)
        expected = None
        if args.expected is not None:
            if len(questions) != 1:
                raise ValueError("Use --suite with expected_answers to label multiple questions.")
            if next(iter(questions.values()))["type"] == "noul":
                if args.expected not in {"yes", "no", "unknown"}:
                    raise ValueError("A binary expected label must be yes, no, or unknown.")
                expected = {"yes": True, "no": False, "unknown": None}[args.expected]
            else:
                expected = args.expected
        if len(questions) > 1 and expected is not None:
            raise ValueError("Use --suite with expected_answers to label multiple questions.")
        cases = validate_cases(json.loads(args.suite.read_text()) if args.suite else [
            {"id": "message", "message": args.message, "expected_answers": {qid: expected for qid in questions}}
        ], questions)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    rows = []
    for key in ordered_model_keys(args.models):
        print(f"Running {MODELS[key]['name']}…", file=sys.stderr, flush=True)
        rows.extend(run_model(key, cases, args.device, questions=questions))
    data = json.dumps(report(cases, args.models, rows, questions), indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data + "\n")
    print(data)
    if any(r["status"] == "error" for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
