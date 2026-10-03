"""One isolated model per process. Only message/question input reaches the model."""

import argparse
import contextlib
import json
import os
from pathlib import Path
import sys
import time

from model_config import is_hosted, model_eligibility

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def device_name(requested):
    import torch
    if requested != "auto":
        if requested == "mps" and not torch.backends.mps.is_available():
            raise RuntimeError("Mac GPU is unavailable to this process. Launch Streamlit from a normal macOS terminal or with Metal access outside the sandbox.")
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def snapshot(spec):
    from huggingface_hub import snapshot_download
    return snapshot_download(
        spec["repo"], revision=spec["revision"],
        allow_patterns=["*.json", "*.safetensors", "*.py", "*.txt", "*.pt", "*.jinja", "*.model"],
        ignore_patterns=["browser/*", "assets/*"],
    )


def agentjev_predict(engine, state, questions):
    native_questions = []
    for qid, question in questions.items():
        if question["type"] not in {"noul", "choice"}:
            raise ValueError("AgentJev adapter supports noul and choice only.")
        q = {"id": qid, "type": "boolean" if question["type"] == "noul" else "choice",
             "question": question["instructions"]}
        if question["type"] == "choice":
            q["options"] = {key: f"{key}: {meaning}" for key, meaning in question["criteria"].items()}
        native_questions.append(q)
    raw = engine.evaluate({"state": state, "questions": native_questions})
    answers = {}
    for answer in raw["results"][0]["answers"]:
        qid = answer["id"]
        answers[qid] = ({"noul": answer["probability"]} if questions[qid]["type"] == "noul"
                        else {"choice": answer["value"], "probabilities": answer["distribution"]})
    return {"answers": answers, "native_response": raw, "temperatures": engine.temperatures}


def load_model(key, spec, device):
    import torch
    if key in {"verqen", "fragment2", "circuit", "circuit8b", "wev", "wev4b", "wev8b", "openthai"}:
        from additional_models import load_model as load_additional
        return load_additional(key, spec, device)
    if key == "laya":
        from laya import Router
        router = Router(device=device, revisions={"english": spec["revision"]})
        agent = router.load("english")
        if device == "mps" and agent.device.type != "mps":
            raise RuntimeError("Laya could not load on the requested Mac GPU.")
        def predict(state, questions):
            before = agent.cpu_fallback_count
            raw = router.predict(state, questions, model="english")
            if agent.cpu_fallback_count > before:
                raise RuntimeError("Laya fell back to CPU during prediction; refusing to label this a GPU result.")
            return raw
        return predict, str(agent.device)
    if key in {"kev", "kev9b", "kev27b"}:
        from kev.checkpoint import Checkpoint, LoadOptions
        from kev.api import SystemOneRequest, to_record, to_answers
        checkpoint = Checkpoint(f"{spec['repo']}@{spec['revision']}")
        options = LoadOptions(backend="auto", dtype=torch.bfloat16 if device == "mps" else None)
        backend = checkpoint.backend(device, options)
        if backend == "mlx":
            import mlx.core as mx
            mx.set_default_device(mx.gpu)
        tokenizer, model = checkpoint.load(device, options)
        def predict(state, questions):
            request = SystemOneRequest(state=state, questions=questions)
            record, meta = to_record(request)
            encoded = model.encode(tokenizer, record, strict=True)
            probabilities = [p.tolist() for p in model.probs(encoded)]
            return {"answers": to_answers(probabilities, meta), "temperature": checkpoint.meta.temperature}
        return predict, "mlx:gpu" if backend == "mlx" else str(model.device)
    if key in {"lumma", "lumma9b"}:
        import lumma_fev
        model = lumma_fev.load(snapshot(spec), device=device)
        return lambda state, questions: {"answers": model.decide(state, questions)}, device
    if key == "mojev":
        from mojev.serve import Engine
        engine = Engine(snapshot(spec), device=device)
        if device == "mps":
            # Its packed attention mask is float32; MPSGraph rejects a mixed
            # bf16/float32 attention add. Keep this small model in float32.
            engine.model.float()
        def predict(state, questions):
            answers, usage = engine.answer(state, questions)
            return {"answers": answers, "usage": usage}
        return predict, device
    if key == "agentjev":
        source = ROOT / ".cache/sources/agent-jev"
        if not source.exists():
            raise RuntimeError("AgentJev source is missing. Run python3.13 scripts/setup_models.py.")
        sys.path.insert(0, str(source))
        from huggingface_hub import snapshot_download
        from safetensors.torch import load_file
        from jev_service.engine import DecisionEngine
        folder = Path(snapshot(spec))
        base = snapshot_download(
            "Qwen/Qwen3-0.6B", revision="c1899de289a04d12100db370d81485cdf75e47ca",
            allow_patterns=["*.json", "*.safetensors", "*.txt"],
        )
        # The upstream loader accepts a torch bundle; convert the published safe
        # tensor file once without changing any trained parameters.
        checkpoint = ROOT / ".cache" / f"agentjev-{spec['revision']}.pt"
        if not checkpoint.exists():
            temporary = checkpoint.with_suffix(f".{os.getpid()}.tmp")
            torch.save({"state_dict": load_file(str(folder / "model.safetensors"))}, temporary)
            temporary.replace(checkpoint)
        engine = DecisionEngine(str(checkpoint), base, device=device,
                                temperatures=str(folder / "temperatures.json"))
        engine.checkpoint_name = f"{spec['repo']}@{spec['revision']}"
        def predict(state, questions):
            return agentjev_predict(engine, state, questions)
        return predict, device
    raise ValueError(f"Unknown model: {key}")


def synchronize(device):
    import torch
    if device.startswith("cuda"):
        torch.cuda.synchronize()
    elif device.startswith("mps"):
        torch.mps.synchronize()
    elif device == "mlx:gpu":
        import mlx.core as mx
        mx.synchronize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "mps", "cuda"])
    args = parser.parse_args()
    specs = json.loads((ROOT / "models.json").read_text())
    if args.model not in specs:
        parser.error("Unknown model.")
    spec = specs[args.model]
    if is_hosted(spec):
        parser.error(model_eligibility(spec).error or "Hosted models must run through compare.py.")
    payload = json.load(sys.stdin)
    # Third-party loaders sometimes print diagnostics. Keep stdout machine-readable.
    with contextlib.redirect_stdout(sys.stderr):
        device = device_name(args.device)
        start = time.perf_counter()
        predict, device = load_model(args.model, spec, device)
        synchronize(device)
        load_seconds = time.perf_counter() - start
        results = []
        for message in payload["messages"]:
            try:
                synchronize(device)
                start = time.perf_counter()
                raw = predict(message, payload["questions"])
                synchronize(device)
                results.append({"status": "ok", "raw_response": raw,
                                "inference_seconds": time.perf_counter() - start})
            except Exception as exc:
                results.append({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    import torch
    print(json.dumps({"results": results, "load_seconds": load_seconds, "device": device,
                      "runtime": {"python": sys.version.split()[0], "torch": torch.__version__}}, allow_nan=False))


if __name__ == "__main__":
    main()
