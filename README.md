# agentspec
Structured, enforceable, and extractable docstrings for AI-assisted codebases.

Goal:
Add, lint, extract, and maintain structured “agent spec” blocks inside comments/docstrings so LLM agents don’t break code they edit.

🏗️ Repo layout
```
agentspec/
├─ pyproject.toml           # Makes it pip-installable
├─ README.md
├─ LICENSE
├─ agentspec/
│  ├─ __init__.py
│  ├─ cli.py                # CLI entry point
│  ├─ lint.py               # Lint rule logic (based on your check_verbose_comments.py)
│  ├─ extract.py            # Comment extractor (your extract_comments.py evolved)
│  ├─ autofill.py           # Optional call-graph auto-fill logic
│  └─ utils/
│     ├─ parser.py          # AST/tree-sitter helpers
│     └─ schema.py          # Defines YAML schema keys + validation
├─ tests/
│  ├─ test_lint.py
│  ├─ test_extract.py
│  └─ sample_code/
│     └─ demo.py
├─ .github/
│  └─ workflows/
│     ├─ lint.yml           # runs `agentspec lint .`
│     └─ extract.yml        # runs `agentspec extract . --markdown`
└─ setup.cfg                # black, flake8, mypy configs
```
