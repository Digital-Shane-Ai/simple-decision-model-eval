#!/usr/bin/env python3
"""Recreate README charts from comparison.json using only Python's standard library.

No model imports, requests, inference, or browser access. Writes only adjacent SVG
assets and overview.json. Values are recomputed from answer rows, then checked
against the captured summary; every chart uses those unrounded values.
"""

import hashlib
import html
import json
import math
import re
import statistics
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "comparison.json"
EXPECTED_SHA256 = "e2b08136498a417ae763d201af2e4f8e8eac216c8de4e5a50ccbb15055e159d6"
WIDTH = 940
LEFT = 278
PLOT_WIDTH = 450
RIGHT = 916
INK = "#182a3b"
MUTED = "#526272"
GRID = "#d9e2e9"
LOCAL = "#176b8a"
HOSTED = "#ac4b13"


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)


def collect(raw):
    data = json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "This generator is for the saved October 5 run."
    assert len(data["cases"]) == 12 and len(data["questions"]) == 1 and len(data["models"]) == 19
    question = data["questions"]["request_type"]
    assert question["type"] == "choice" and len(question["criteria"]) == 5
    choices = list(question["criteria"])
    cases = {c["id"]: c for c in data["cases"]}
    summary = {s["model"]: s for s in data["summary"]}
    records = []
    assert len(data["results"]) == 228
    for key, model in data["models"].items():
        rows = [r for r in data["results"] if r["model_key"] == key]
        assert len(rows) == 12 and len({(r["case_id"], r["question_id"]) for r in rows}) == 12
        assert all(r["status"] == "ok" and r["question_type"] == "choice" for r in rows)
        assert all(r["question_id"] == "request_type" for r in rows)
        scores, losses, zeros = [], [], 0
        for row in rows:
            assert row["expected"] == cases[row["case_id"]]["expected_answers"]["request_type"]
            assert row["correct"] == (row["decision"] == row["expected"])
            p = row["probabilities"]
            assert set(p) == set(choices) and all(0 <= v <= 1 for v in p.values())
            close(sum(p.values()), 1)
            scores.append(sum((p[c] - int(c == row["expected"])) ** 2 for c in choices))
            assert 0 <= scores[-1] <= 2
            truth_probability = p[row["expected"]]
            assert row["log_loss_scored"] == 1
            if truth_probability == 0:
                zeros += 1
                assert row["log_loss"] is None and row["log_loss_status"] == "infinite"
                assert row["log_loss_zero_probability_count"] == 1
            else:
                loss = -math.log(truth_probability)
                losses.append(loss)
                close(row["log_loss"], loss)
                assert row["log_loss_status"] == "finite" and row["log_loss_zero_probability_count"] == 0
        correct = sum(r["correct"] for r in rows)
        brier = statistics.mean(scores)
        # One call per context, not per question. This run has one question.
        times = {r["case_id"]: r["inference_seconds"] for r in rows}
        mean = statistics.mean(times.values())
        load = rows[0]["load_seconds"]
        assert all(r["load_seconds"] == load for r in rows)
        s = summary[model["name"]]
        assert s["cases"] == s["contexts"] == s["answered"] == s["labelled"] == 12
        assert s["correct"] == correct and s["errors"] == 0
        close(s["accuracy_on_answered"], correct / 12)
        close(s["correct_over_labelled"], correct / 12)
        close(s["coverage"], 1)
        close(s["choice_brier_score"], brier)
        log_loss = None if zeros else statistics.mean(losses)
        log_loss_status = "infinite" if zeros else "finite"
        assert s["log_loss_status"] == log_loss_status and s["log_loss_scored"] == 12
        assert s["log_loss_zero_probability_count"] == zeros
        if zeros:
            assert s["log_loss"] is None
        else:
            close(s["log_loss"], log_loss)
        close(s["mean_inference_seconds"], mean)
        assert s["brier_score"] is None and s["load_seconds"] == load
        execution = rows[0]["execution"]
        assert all(r["execution"] == execution for r in rows)
        if execution == "hosted":
            assert load is None
            assert all(r["timing_scope"] == "API round trip including network and provider queue" for r in rows)
        else:
            assert execution == "local" and load is not None
            assert rows[0]["device"] in {"mps", "mps:0", "mlx:gpu"}
        slug = re.sub(r"[^a-z0-9]+", "-", model["name"].lower()).strip("-")
        records.append({
            "model_key": key, "model": model["name"], "execution": execution,
            "report": "../" + slug + ".md", "device": rows[0]["device"],
            "answered": 12, "labelled": 12, "correct": correct, "errors": 0,
            "accuracy": correct / 12, "coverage": 1.0, "choice_brier_score": brier,
            "log_loss": log_loss, "log_loss_status": log_loss_status,
            "log_loss_scored": 12, "log_loss_zero_probability_count": zeros,
            "mean_call_ms": mean * 1000, "load_seconds": load,
        })
    assert sum(r["correct"] == 12 for r in records) == 11
    assert sum(r["correct"] for r in records) == 211
    assert sum(r["execution"] == "local" for r in records) == 16
    assert [(r["model_key"], r["case_id"]) for r in data["results"] if r["log_loss_status"] == "infinite"] == [("fragment2", "before-purchase")]
    return data, records


class SVG:
    def __init__(self, name, title, description, height):
        self.name = name
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
            f"<title id=\"title\">{html.escape(title)}</title>",
            f"<desc id=\"desc\">{html.escape(description)}</desc>",
            '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#182a3b} .muted{fill:#526272} .value{font-variant-numeric:tabular-nums}</style>',
            f'<rect width="{WIDTH}" height="{height}" fill="#ffffff"/>',
        ]

    def text(self, x, y, value, size=16, anchor="start", weight=400, color=INK):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}" style="fill:{color}">{html.escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, width=1, dashed=False):
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(f'<line x1="{x1:.4f}" y1="{y1:.4f}" x2="{x2:.4f}" y2="{y2:.4f}" stroke="{color}" stroke-width="{width}"{dash}/>')

    def rect(self, x, y, width, height, color, radius=0):
        self.parts.append(f'<rect x="{x:.6f}" y="{y:.6f}" width="{width:.9f}" height="{height:.6f}" rx="{radius}" fill="{color}"/>')

    def point(self, x, y, color):
        self.parts.append(f'<circle cx="{x:.9f}" cy="{y:.6f}" r="4.5" fill="{color}"/>')

    def header(self, title, subtitle):
        self.text(24, 29, "SAVED SCREENING RUN · 05 OCT 2026", 12, weight=700, color=MUTED)
        self.text(24, 61, title, 26, weight=700)
        self.text(24, 88, subtitle, 16, color=MUTED)

    def legend(self, y=119):
        self.rect(24, y - 11, 12, 12, LOCAL, 2)
        self.text(44, y, "Local GPU", 15)
        self.rect(161, y - 11, 12, 12, HOSTED, 2)
        self.text(181, y, "Hosted API", 15)

    def axes(self, top, bottom, maximum, ticks, formatter, label):
        for tick in ticks:
            x = LEFT + PLOT_WIDTH * tick / maximum
            self.line(x, top, x, bottom)
            self.text(x, bottom + 25, formatter(tick), 14, anchor="middle", color=MUTED)
        self.text(LEFT + PLOT_WIDTH / 2, bottom + 53, label, 15, anchor="middle", color=MUTED)

    def rows(self, records, top, field, maximum, value, dot=False, row_height=29):
        for i, record in enumerate(records):
            y = top + i * row_height
            if i % 2 == 0:
                self.rect(18, y - 12, WIDTH - 36, row_height, "#f4f7fa")
            label = "API · " + record["model"] if record["execution"] == "hosted" else record["model"]
            self.text(24, y + 9, label, 15)
            self.text(RIGHT, y + 9, value(record), 16, anchor="end", weight=600)
            color = LOCAL if record["execution"] == "local" else HOSTED
            x = LEFT + PLOT_WIDTH * record[field] / maximum
            if dot:
                self.line(LEFT, y + 3, x, y + 3, color, 2)
                self.point(x, y + 3, color)
            else:
                self.rect(LEFT, y - 5, x - LEFT, 17, color, 2)

    def save(self):
        self.parts.append("</svg>\n")
        (HERE / self.name).write_text("\n".join(self.parts), encoding="utf-8")


def accuracy(records):
    records = sorted(records, key=lambda r: -r["accuracy"])
    desc = "All 19 models, sorted by accuracy descending; exact ties retain captured order. API models are orange and prefixed API. Accuracy = correct / 12 answered labeled cases. 100% coverage and no errors. "
    desc += "; ".join(f"{r['model']}: {r['correct']}/12 ({r['accuracy']*100:.1f}%)" for r in records)
    svg = SVG("accuracy.svg", "Accuracy on 12 customer-support messages", desc, 820)
    svg.header("Which models answered correctly?", "11 of 19 models scored 12/12 · One answer changes accuracy by 8.33 points")
    svg.legend()
    svg.text(24, 155, "MODEL", 12, weight=700, color=MUTED)
    svg.text(RIGHT, 155, "ACCURACY / CORRECT", 12, anchor="end", weight=700, color=MUTED)
    top, bottom = 181, 181 + 18 * 29 + 18
    svg.rows(records, top, "accuracy", 1, lambda r: f"{r['accuracy']*100:.1f}%  ({r['correct']}/12)")
    svg.axes(top - 14, bottom, 1, [0, .25, .5, .75, 1], lambda v: f"{v*100:.0f}%", "Accuracy · highest first · ties retain captured order")
    baseline = LEFT + PLOT_WIDTH / 2
    svg.line(baseline, top - 14, baseline, bottom, MUTED, 1.4, dashed=True)
    svg.text(24, 794, "Dashed line: always choose refund = 6/12 (50%) · Full 0–100% scale", 15, color=MUTED)
    svg.save()


def format_brier(value):
    """Display Brier scores rounded to eight decimal places."""
    return f"{value:.8f}"


def brier(records):
    records = sorted(records, key=lambda r: r["choice_brier_score"])
    perfect = sorted((r for r in records if r["correct"] == 12), key=lambda r: r["choice_brier_score"])
    desc = "Choice Brier = mean over 12 labeled answers of the sum of five squared errors, range 0 to 2; sorted lowest first with exact ties in captured order. API models are orange and prefixed API. "
    desc += "; ".join(f"{r['model']}: {r['choice_brier_score']:.12g}" for r in records)
    desc += ". A separate panel shows only the 11 models with 12/12 accuracy, on a linear 0 to 0.06 scale."
    svg = SVG("brier.svg", "Choice Brier: all models and a separate detail view", desc, 1428)
    svg.header("How close were the probabilities to the labels?", "All five choices count · Mean over 12 labeled answers · Lower is better")
    svg.legend()
    svg.text(24, 155, "ALL 19 MODELS · FULL 0–2 SCALE", 14, weight=700)
    svg.text(RIGHT, 155, "MEAN CHOICE BRIER", 12, anchor="end", weight=700, color=MUTED)
    top, bottom = 183, 183 + 18 * 29 + 18
    svg.rows(records, top, "choice_brier_score", 2, lambda r: format_brier(r['choice_brier_score']), dot=True)
    svg.axes(top - 14, bottom, 2, [0, .5, 1, 1.5, 2], lambda v: f"{v:g}", "Choice Brier · full 0–2 scale · lowest first")
    svg.text(24, 797, "Labels are rounded to eight decimal places; the saved data retains full precision.", 15, color=MUTED)
    svg.line(24, 827, WIDTH - 24, 827)
    svg.text(24, 865, "DETAIL · THE 11 MODELS WITH 12/12 ACCURACY", 17, weight=700)
    svg.text(24, 892, "Independent linear 0–0.06 scale · Sorted by Brier within this captured sample", 16, color=MUTED)
    svg.text(24, 929, "MODEL", 12, weight=700, color=MUTED)
    svg.text(RIGHT, 929, "MEAN CHOICE BRIER", 12, anchor="end", weight=700, color=MUTED)
    top2, bottom2 = 957, 957 + 10 * 29 + 18
    svg.rows(perfect, top2, "choice_brier_score", .06, lambda r: format_brier(r['choice_brier_score']), dot=True)
    svg.axes(top2 - 14, bottom2, .06, [0, .015, .03, .045, .06], lambda v: f"{v:.3f}", "Choice Brier · detail 0–0.06 scale · lowest first")
    svg.text(24, 1351, "Perfect accuracy can conceal different probability quality. Brier is not an accuracy percentage.", 15, color=MUTED)
    svg.text(24, 1381, "One small run cannot establish calibration or a universal model ranking.", 15, color=MUTED)
    svg.save()


def log_loss(records):
    records = sorted(records, key=lambda r: math.inf if r["log_loss_status"] == "infinite" else r["log_loss"])
    desc = "Mean -ln P(expected) over 12 labeled answers, in nats; sorted lowest first. Zero truth probability gives infinite loss without clipping. API models are orange and prefixed API. "
    desc += "; ".join(f"{r['model']}: {r['log_loss']:.12g}" if r["log_loss_status"] == "finite" else f"{r['model']}: infinite ({r['log_loss_zero_probability_count']} zero-probability truth)" for r in records)
    svg = SVG("log-loss.svg", "Log loss: probability assigned to the expected answer", desc, 880)
    svg.header("How much probability went to the expected answer?", "Mean negative natural log · 12 labeled answers per model · Lower is better")
    svg.legend()
    svg.text(24, 155, "MODEL", 12, weight=700, color=MUTED)
    svg.text(RIGHT, 155, "MEAN LOG LOSS (nats)", 12, anchor="end", weight=700, color=MUTED)
    top, bottom = 181, 181 + 17 * 29 + 18
    svg.rows([r for r in records if r["log_loss_status"] == "finite"], top, "log_loss", 1.2, lambda r: f"{r['log_loss']:.8f}", dot=True)
    svg.axes(top - 14, bottom, 1.2, [0, .3, .6, .9, 1.2], lambda v: f"{v:g}", "Log loss (nats) · finite values · lowest first")
    svg.line(24, 778, WIDTH - 24, 778)
    svg.text(24, 806, "Fragment-2", 15)
    svg.text(RIGHT, 806, "∞ · 1 zero-probability truth", 16, anchor="end", weight=600)
    svg.text(24, 844, "Fragment-2 assigned P(other) = 0 on before-purchase. Infinite loss has no finite plotted point.", 15, color=MUTED)
    svg.save()


def timing(records):
    records = sorted(records, key=lambda r: r["mean_call_ms"])
    desc = "Mean of 12 timed calls per model. All 19 models share a linear 0 to 600 ms axis, sorted lowest first; exact ties retain captured order. "
    desc += "; ".join(f"{r['model']} ({r['execution']}): {r['mean_call_ms']:.6f} ms" for r in records)
    desc += ". Local GPU calls exclude model loading and include the first call. Hosted API models are orange and prefixed API; their times include network and provider queue."
    svg = SVG("timing.svg", "Observed call times for local GPU and hosted API models", desc, 910)
    svg.header("How long did a call take?", "One run · Mean of 12 calls per model · Sorted lowest first; exact ties retain captured order")
    svg.legend()
    svg.text(24, 155, "MODEL", 12, weight=700, color=MUTED)
    svg.text(RIGHT, 155, "MEAN CALL (ms)", 12, anchor="end", weight=700, color=MUTED)
    top, bottom = 181, 181 + 18 * 29 + 18
    svg.rows(records, top, "mean_call_ms", 600, lambda r: f"{r['mean_call_ms']:.3f}")
    svg.axes(top - 14, bottom, 600, [0, 100, 200, 300, 400, 500, 600], lambda v: str(v), "Observed elapsed time (ms) · no hardware normalization")
    svg.text(24, 810, "Local GPU: model loading excluded · First prediction included · No separate warm-up", 15, color=MUTED)
    svg.text(24, 839, "Hosted service latency: network and provider queue included · Different execution environment", 15, color=MUTED)
    svg.text(24, 868, "Load times are in the table. Hardware specifications and repeat timings were not recorded.", 15, color=MUTED)
    svg.save()


def main():
    data, records = collect(SOURCE.read_bytes())
    overview = {
        "source": "../comparison.json", "source_sha256": EXPECTED_SHA256,
        "completed_at": data["created_at"], "contexts": 12, "questions": 1, "models": 19,
        "answers": 228, "errors": 0, "correct": 211, "incorrect": 17,
        "perfect_accuracy_models": 11, "perfect_local_models": 8, "perfect_hosted_models": 3,
        "choice_brier_formula": "mean over answered labeled pairs of sum over five choices (p - one_hot_label)^2",
        "choice_brier_denominator": 12, "choice_brier_range": [0, 2],
        "choice_brier_class_divisor": 1, "probabilities": "normalized by compare.py; native confidence fields are not scored",
        "log_loss_formula": "mean over answered labeled pairs of -ln P(expected)",
        "log_loss_denominator": 12, "log_loss_units": "nats",
        "log_loss_zero_probability_policy": "infinite; null value with explicit status and count; no clipping",
        "uniform_probability_baseline_brier": .8, "always_refund_accuracy": .5,
        "always_certain_refund_brier": 1.0, "rows": records,
    }
    (HERE / "overview.json").write_text(json.dumps(overview, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    accuracy(records)
    brier(records)
    log_loss(records)
    timing(records)
    print("Verified 228 answers; generated 19-model accuracy, Brier, log loss, and timing SVGs and full precision overview.json.")


if __name__ == "__main__":
    main()
