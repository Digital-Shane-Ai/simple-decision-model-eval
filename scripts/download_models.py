"""Cache pinned local checkpoints without loading models or requiring a GPU."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Share inference's cache location and checkpoint file filters.
from model_worker import snapshot


def download(key, spec):
    from huggingface_hub import snapshot_download

    if key == "laya":
        snapshot_download(spec["repo"], revision=spec["revision"], allow_patterns=[
            "rl_agent_config.json", "model.safetensors", "tokenizer/*", "encoder/*",
        ])
    elif key in {"kev", "kev9b", "kev27b"}:
        from kev.checkpoint import Checkpoint, resolve_run
        checkpoint = Checkpoint(f"{spec['repo']}@{spec['revision']}")
        if not checkpoint.full:
            if not checkpoint.meta.base_revision:
                raise ValueError("Kev base checkpoint is missing its pinned revision")
            resolve_run(f"{checkpoint.meta.base}@{checkpoint.meta.base_revision}")
    else:
        snapshot(spec)
        if "base" in spec:
            snapshot(spec["base"])
        if key == "agentjev":
            snapshot_download(
                "Qwen/Qwen3-0.6B", revision="c1899de289a04d12100db370d81485cdf75e47ca",
                allow_patterns=["*.json", "*.safetensors", "*.txt"],
            )


def main():
    models = json.loads((ROOT / "models.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="*", help="Model keys (default: all local models)")
    args = parser.parse_args()
    unknown = set(args.models) - models.keys()
    if unknown:
        parser.error(f"Unknown models: {', '.join(sorted(unknown))}. Choices: {', '.join(models)}")
    selected = args.models or [k for k, s in models.items() if s.get("backend") in {None, "local"}]
    failed = []
    for key in dict.fromkeys(selected):
        spec = models[key]
        if spec.get("backend") not in {None, "local"}:
            print(f"Skipping {spec['name']}: hosted API, no local weights.", flush=True)
            continue
        print(f"Downloading {spec['name']}…", flush=True)
        try:
            download(key, spec)
        except Exception as exc:
            failed.append(key)
            print(f"Failed {spec['name']} ({type(exc).__name__}). Check repository access, HF_TOKEN, network, and disk space.", file=sys.stderr)
        else:
            print(f"Cached {spec['name']}.", flush=True)
    if failed:
        raise SystemExit(f"Downloads failed: {', '.join(failed)}. Rerun to resume cached downloads.")


if __name__ == "__main__":
    main()
