"""Local Laya refund-intent inference, shared by the CLI and browser demo."""

import argparse
import json
import os
from pathlib import Path
from time import perf_counter

# Keep downloaded weights in the project; no hosted inference or API key needed.
os.environ.setdefault("HF_HOME", str(Path(__file__).parent / ".cache" / "huggingface"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

EXAMPLES = {
    "Refund request": "I bought a pair of wireless headphones last week, but the left earbud doesn't work. I'd like to return them and get a full refund, please.",
    "Replacement only": "The headphones arrived broken. Please send a replacement. I do not want a refund.",
    "Product question": "Are these headphones compatible with my laptop? I haven't purchased them yet.",
    "Uncertain intent": "I'm disappointed with these headphones. What are my options?",
}
QUESTIONS = {
    "refund_requested": {
        "type": "noul",
        "instructions": "Does the user request a refund or ask for their money back for a product?",
    }
}


def create_router(device="auto"):
    from laya import Router

    return Router(device=None if device == "auto" else device)


def predict_refund(router, message):
    if not message.strip():
        raise ValueError("Enter a customer message before running the demo.")
    started = perf_counter()
    raw = router.predict(message.strip(), QUESTIONS, model="english")
    answer = raw["answers"]["refund_requested"]
    probability = float(answer["noul"])
    return {
        "message": message.strip(),
        "wants_refund": probability >= 0.5,
        "decision_threshold": 0.5,
        "probability_yes": probability,
        "probability_no": round(1.0 - probability, 4),
        "confidence": answer["confidence"],
        "answer_confidence": answer["answer_confidence"],
        "elapsed_seconds_including_load": round(perf_counter() - started, 3),
        "device": str(router.load("english").device),
        "raw_response": raw,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", default=EXAMPLES["Refund request"])
    parser.add_argument("--device", choices=["auto", "cpu", "mps", "cuda"], default="auto")
    args = parser.parse_args()
    if not args.message.strip():
        parser.error("message must not be empty")
    print(json.dumps(predict_refund(create_router(args.device), args.message), indent=2))


if __name__ == "__main__":
    main()
