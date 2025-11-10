# Deep Agent + uv

This repo is prepped to use [uv](https://github.com/astral-sh/uv) for dependency and virtual environment management. The reusable agent logic lives in `src/deep_agent/agent.py`, and the `workbook.ipynb` notebook simply imports it for interactive exploration.

## Requirements
- Python 3.11+ (uv can manage toolchains with `uv python install 3.11`)
- `uv` CLI (install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`)

## Getting started
1. Create a uv-managed virtual environment:
   ```sh
   uv venv --python 3.11
   ```
2. Activate it (uv automatically writes `.venv`):
   ```sh
   source .venv/bin/activate
   ```
3. Install dependencies defined in `pyproject.toml` (and dev deps for notebooks):
   ```sh
   uv sync --dev
   ```
4. Launch Jupyter Lab directly:
   ```sh
   uv run jupyter lab
   ```

## Running the research agent
1. Supply API keys via `.env` (loaded automatically) or export them in your shell:
   ```sh
   export TAVILY_API_KEY=...
   export GOOGLE_API_KEY=...
   ```
   If `GOOGLE_API_KEY` is missing at runtime, `deep_agent.agent` will prompt once using `getpass`.
2. Execute the packaged agent from anywhere inside the repo:
   ```sh
   uv run deep-agent "What is LangGraph?"
   ```
   Leave off the question to drop into an interactive loop—type new prompts until you enter `quit`/`exit`. Each turn is stateless (no memory), so include prior context in your next question. You can also pass `--model <name>` to switch LLMs or `--no-google-prompt` to skip interactive key entry. The same helpers remain available for import in scripts/notebooks.

## Managing dependencies
- Add runtime packages with `uv add <package>`; use `uv add --dev <package>` for tooling / notebook extras.
- When you need optional notebook tooling without dev extras, install via `uv sync --extra notebooks`.
- The `pyproject.toml` is the single source of truth; uv will maintain `uv.lock` automatically the first time you run `uv sync`.

## Project layout
```
.
├── pyproject.toml     # uv + PEP 621 metadata
├── src/deep_agent/    # package code + research agent
└── workbook.ipynb     # thin UI around the packaged agent
```

Feel free to extend the package under `src/deep_agent` and import it inside the notebook once functionality stabilizes.
