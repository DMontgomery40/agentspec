# Code Style and Conventions

Python
- Target Python >= 3.10 (PEP 604 union types may be used).
- Line length: 100 (`flake8` max-line-length=100; `isort` line_length=100, profile=black).
- Lint config ignores: `E203`, `W503`, `E501` (consistent with Black formatting conventions).
- Prefer type hints across the codebase.

Agentspec (Docstrings)
- Every new/modified function or class must include a YAML agentspec block between `---agentspec` and `---/agentspec`.
- Required fields: `what`, `deps` (calls, called_by, config, environment), `why`, `guardrails`.
- Recommended fields: `changelog`, `testing`, `performance`.
- Optional fields: `security`, `monitoring`, `known_issues`.
- Before editing a function, print key lines from its spec (what + guardrails) to stdout.
- After changes: update relevant spec fields and append a dated changelog entry.

Guardrails (from AGENTS.md)
- Do not delete "unused" code without checking `called_by` (dynamic imports/config-driven dispatch may reference it).
- Do not "fix" model names or other choices without reading the `why` section.
- Do not parallelize or remove checks unless the spec explicitly allows it.

Tools and Quality Gates
- `agentspec lint <path>` must pass (use `--strict` for CI parity).
- `ruff check agentspec/` for code quality (configured in `tox.ini`).
- `pytest` tests should pass locally.

Docs/Reading Guidance (Serena)
- Prefer symbolic exploration over reading whole files; scan only what’s necessary.
- Use top-level overviews and targeted symbol reads when exploring code.
