"""Supported Streamlit launcher with configuration diagnostics before startup."""

import json
from pathlib import Path
import sys

from model_config import print_startup_diagnostics

ROOT = Path(__file__).resolve().parent


def main(args=None):
    args = sys.argv[1:] if args is None else args
    print_startup_diagnostics(json.loads((ROOT / "models.json").read_text()))
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", str(ROOT / "app.py"), *args]
    return cli.main()


if __name__ == "__main__":
    main()
