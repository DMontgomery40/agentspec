# Suggested Commands

Setup
- Verify Python: `python3 --version` (requires >= 3.10)
- Install (core): `pip install -e .`
- Install with providers: `pip install -e .[anthropic]` / `pip install -e .[openai]` / `pip install -e .[all]`

Environment (LLM)
- Claude: `export ANTHROPIC_API_KEY=...`
- OpenAI cloud: `export OPENAI_API_KEY=...`
- OpenAI-compatible (e.g., Ollama): `export OPENAI_BASE_URL=http://localhost:11434/v1`

CLI Basics
- Help: `agentspec --help`
- Lint: `agentspec lint agentspec/ [--strict]`
- Extract to Markdown: `agentspec extract agentspec/ --format markdown`
- Extract (agent context): `agentspec extract agentspec/ --format agent-context`
- Generate docstrings: `agentspec generate agentspec/ --model claude-haiku-4-5 --force-context`
- Update existing specs after code changes: `agentspec generate agentspec/ --update-existing`

Quality & Tests
- Ruff (via tox env): `tox -e lint` (runs `ruff check agentspec/`)
- Pytest: `pytest -v`
- Tox (all supported interpreters): `tox`
- Specific Python via tox: `tox -e py310` / `tox -e py311` / `tox -e py312`

Pre-commit (optional)
- Create hook: add script from README under `.git/hooks/pre-commit` and `chmod +x .git/hooks/pre-commit`

Release/Packaging (local)
- Editable install already provides CLI. For builds, standard setuptools flow applies if needed.
