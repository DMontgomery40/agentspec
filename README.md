# 🧠 Agentspec

**Structured, enforceable, and extractable docstrings for AI-assisted codebases.**

---

## ✨ What it does
Agentspec enforces a structured YAML-style fenced block inside Python docstrings so human devs and AI agents always share the same context about *what*, *why*, *dependencies*, and *guardrails*.

---

## 🚀 Quick start

```bash
pip install -e .
agentspec lint src/
agentspec extract src/ --json
```

## 📄 Example

```
def process_embeddings(text: str):
    """
    ---agentspec
    what: Takes text → 1536-dim embedding using gpt-5
    deps:
      calls:
        - openai_client.create_embedding
      called_by:
        - rag_engine.chunk_and_embed
    why: Needs larger context window for code embeddings
    guardrails:
      - DO NOT rename model unless gpt-5 deprecated
      - DO NOT remove rate limiting
    ---/agentspec
    """
```

## 🧩 Commands

| Command | Description |
|----------|-------------|
| `agentspec lint` | Validate required sections and schema |
| `agentspec extract --json` | Extract all specs to `agent_specs.json` |
| `agentspec extract` | Extract to Markdown |


## 🛠️ GitHub Action

Add to your repo:
```
.github/workflows/agentspec.yml → runs lint & extract automatically on every push.
```

## 🧩 Test (skeleton) 


```python
from agentspec import lint, extract
from pathlib import Path

def test_lint_runs():
    result = lint.run("agentspec/")
    assert isinstance(result, int)

def test_extract_runs():
    result = extract.run("agentspec/", "markdown")
    assert isinstance(result, int)
```

## 🧱 Roadmap

- Multi-language parsing via Tree-sitter
- Automatic dependency mapping
- VS Code / Cursor integration
- Org-wide pre-commit hook
