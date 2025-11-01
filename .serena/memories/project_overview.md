# Project Overview — Agentspec

Purpose
- Structured, enforceable, and extractable docstrings ("agentspecs") embedded in code to give AI agents and humans rich context, dependencies, guardrails, and change history.
- Provides CLI to generate, lint, and extract specs; supports Python and JavaScript/TypeScript (via tree-sitter).

Tech Stack
- Language: Python 3.10+ (3.11+ recommended)
- Packaging: `pyproject.toml` + setuptools; console script `agentspec = agentspec.cli:main`
- CLI UI: `rich`, `rich-argparse`
- Optional LLM providers: `anthropic`, `openai`; optional JS parsing: `tree-sitter`, `tree-sitter-languages`
- Tests: `pytest`, `tox`
- Lint/quality: `ruff` (via tox), `flake8` config present, `isort` (profile black)

Key Commands (high level)
- Generate docstrings: `agentspec generate <path> [--model <model>] [--update-existing] [--force-context]`
- Lint specs: `agentspec lint <path> [--strict]`
- Extract specs: `agentspec extract <path> --format {markdown,json,agent-context}`

Environment Vars (LLM)
- `ANTHROPIC_API_KEY` for Claude
- `OPENAI_API_KEY` for OpenAI cloud-compatible
- `OPENAI_BASE_URL` to point to OpenAI-compatible servers (e.g., Ollama at http://localhost:11434/v1)

Repository Structure (high level)
- `agentspec/` — library + CLI implementation (cli.py, lint.py, extract.py, generate.py, utils.py, langs/*)
- `tests/` — pytest suite; includes JS fixtures and adapter tests
- `docs/` — additional docs (if present)
- `assets/` — screenshots/assets for README
- Root docs: `README.md`, `AGENTS.md`, `TOOLS.md`, `RETROFIT_GUIDE.md`, `IMPLEMENTATION_SUMMARY.md`, `CHANGELOG.md`
- Config: `pyproject.toml`, `setup.cfg`, `tox.ini`, `.agentspecignore`

Notable Conventions
- Agentspec blocks live inside docstrings under `---agentspec ... ---/agentspec`.
- Guardrails are mandatory; changelog recommended per function.
- Printing selected spec lines before edits is encouraged for AI agents consuming the code.

Entry Points
- CLI: `agentspec` (installed from this repo via `pip install -e .`)
