"""Native binary and choice adapters for additional model families."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile

from model_worker import ROOT, snapshot


def require_supported(questions):
    if any(q["type"] not in {"noul", "choice"} for q in questions.values()):
        raise ValueError("This eval adapter supports noul and choice questions.")


def verqen_predict(model, state, questions):
    require_supported(questions)
    native, answers = {}, {}
    for qid, q in questions.items():
        if q["type"] == "noul":
            answer = model.decide(state=state, question=q["instructions"], question_type="noul")
            answers[qid] = {"noul": answer["p_true"], "confidence": answer["p_correct"]}
        else:
            # VerQen uses option text as keys. Keep names and meanings in the
            # native options, then map its output back to the caller's names.
            options = {key: f"{key}: {meaning}" for key, meaning in q["criteria"].items()}
            if len(set(options.values())) != len(options):
                raise ValueError("Choice descriptions rendered ambiguously.")
            answer = model.decide(state=state, question=q["instructions"], options=list(options.values()), question_type="choice")
            reverse = {v: k for k, v in options.items()}
            answers[qid] = {"choice": reverse[answer["selected"]],
                            "probabilities": {key: answer["probabilities"][value] for key, value in options.items()},
                            "confidence": answer["p_correct"]}
        native[qid] = answer
    return {"answers": answers, "native_response": native}


def circuit_predict(scorer, state, questions):
    from s1proto.schema import NoulQuestion, ChoiceQuestion
    from s1proto.template import render_noul, render_choice
    require_supported(questions)
    prompts = [(render_noul(state, NoulQuestion(**q), layout=scorer.layout) if q["type"] == "noul"
                else render_choice(state, ChoiceQuestion(**q), layout=scorer.layout)) for q in questions.values()]
    results = scorer.score(prompts)
    # Circuit's native noul template orders options as yes, no.
    answers = {}
    for (qid, question), result in zip(questions.items(), results, strict=True):
        if question["type"] == "noul":
            answers[qid] = {"noul": result.probabilities[0]}
        else:
            probabilities = dict(zip(question["criteria"], result.probabilities, strict=True))
            answers[qid] = {"choice": max(probabilities, key=probabilities.get), "probabilities": probabilities}
    return {"answers": answers,
            "native_response": {qid: {"probabilities": r.probabilities, "logits": r.logits,
                                      "input_tokens": r.input_tokens}
                                for qid, r in zip(questions, results, strict=True)}}


def load_circuit(spec, device):
    source = ROOT / ".cache/sources/circuit"
    if not source.exists():
        raise RuntimeError("Circuit source is missing. Run just setup.")
    sys.path.insert(0, str(source))
    from s1proto.scorer import LoRAScorer
    folder = Path(snapshot(spec))
    base = snapshot(spec["base"])
    cfg = json.loads((folder / "config.json").read_text())
    if cfg["base"] != spec["base"]["repo"]:
        raise ValueError("Circuit base does not match the pinned registry entry.")
    # Upstream accepts a path, not a base revision. A temporary view redirects
    # only the base path; the cached adapter, head, and original config are intact.
    with tempfile.TemporaryDirectory(prefix="circuit-") as directory:
        view = Path(directory)
        for child in folder.iterdir():
            if child.name != "config.json":
                (view / child.name).symlink_to(child, target_is_directory=child.is_dir())
        cfg["base"] = base
        (view / "config.json").write_text(json.dumps(cfg))
        scorer = LoRAScorer(str(view), device=device)
    return lambda state, questions: circuit_predict(scorer, state, questions), str(scorer.device)


def load_model(key, spec, device):
    if key in {"circuit", "circuit8b"}:
        return load_circuit(spec, device)
    folder = snapshot(spec)
    if key == "verqen":
        from verqen import Verqen
        model = Verqen.from_pretrained(folder, device=device)
        return lambda state, questions: verqen_predict(model, state, questions), str(model.engine.device)
    if key == "fragment2":
        module_spec = importlib.util.spec_from_file_location("fragment2_runtime", Path(folder) / "f3.py")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        model = module.Fragment.from_pretrained(folder)
        model.net.to(device)
        # The published runtime constructs its input on CPU. Move only that
        # tensor at the network boundary, retaining native tokenization/readout.
        model.net.register_forward_pre_hook(lambda net, args: (args[0].to(device),))
        return model.decide, str(next(model.net.parameters()).device)
    if key in {"wev", "wev4b", "wev8b"}:
        import wev
        model = wev.load(folder, device=device)
        return model.predict, str(next(model.model.parameters()).device)
    if key == "openthai":
        from openthai_systemone import SystemOneClient
        model = SystemOneClient(folder, device=device, model_name=spec["repo"])
        return lambda state, questions: model.system_one(state, questions).model_dump(mode="json"), str(model.device)
    raise ValueError(f"Unknown additional model: {key}")
