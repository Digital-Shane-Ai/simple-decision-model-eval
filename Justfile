set positional-arguments

python := env_var_or_default("PYTHON", "python3.13")

# Show available commands.
default:
    @just --list

# Install isolated Python runtimes and pinned model sources (Python 3.12/3.13).
setup:
    test -d .venv || {{ quote(python) }} -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    {{ quote(python) }} scripts/setup_models.py

# Download all local checkpoints and their bases, or selected model keys.
download-models *models:
    .venv-models/bin/python scripts/download_models.py "$@"

# Launch the comparison app; optional arguments are passed to Streamlit.
serve *args:
    .venv/bin/python serve.py "$@"
