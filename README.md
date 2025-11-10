# Deep Agent

This repo is prepped to use [uv](https://github.com/astral-sh/uv) for dependency and virtual environment management. The lone `workbook.ipynb` notebook lives at the project root for now; feel free to reorganize into a dedicated `notebooks/` directory once you start collecting more experiments.

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

## Managing dependencies
- Add runtime packages with `uv add <package>`; use `uv add --dev <package>` for tooling / notebook extras.
- When you need optional notebook tooling without dev extras, install via `uv sync --extra notebooks`.
- The `pyproject.toml` is the single source of truth; uv will maintain `uv.lock` automatically the first time you run `uv sync`.

## Project layout
```
.
├── pyproject.toml     # uv + PEP 621 metadata
├── src/deep_agent/    # package code (ready for expansion)
└── workbook.ipynb     # starter notebook
```

Feel free to extend the package under `src/deep_agent` and import it inside the notebook once functionality stabilizes.
