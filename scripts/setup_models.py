"""Run with Python 3.12/3.13 to install the isolated local inference environment."""

from pathlib import Path
import json
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
AGENT_REVISION = "a965ca8ff06ccabc0c796dca5447b55cc2069cee"


def main():
    if not (3, 12) <= sys.version_info[:2] < (3, 14):
        raise SystemExit("Run this setup with Python 3.12 or 3.13 (Kev's supported versions).")
    for name in ("models", "modern", "wev"):
        env = ROOT / f".venv-{name}"
        if not env.exists():
            venv.create(env, with_pip=True)
        python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(ROOT / f"requirements-{name}.txt")], check=True)
    source = ROOT / ".cache/sources/agent-jev"
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "https://github.com/malevrigns/agent-jev.git", str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", AGENT_REVISION], check=True)
    circuit = json.loads((ROOT / "models.json").read_text())["circuit"]
    source = ROOT / ".cache/sources/circuit"
    if not source.exists():
        subprocess.run(["git", "clone", circuit["source"], str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "fetch", "origin", circuit["source_revision"]], check=True)
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", circuit["source_revision"]], check=True)
    print("Ready. Start the app, or run .venv/bin/python compare.py --suite examples/refund-cases.json")


if __name__ == "__main__":
    main()
