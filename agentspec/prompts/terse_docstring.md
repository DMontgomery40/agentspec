# Terse Docstring Generation Prompt

You are helping to document a Python codebase with concise docstrings for LLM consumption.

Analyze this function and generate a TERSE docstring following this EXACT format:

"""
Brief one-line description.

WHAT:
- Core behavior (2-3 bullets max, one line each)
- Key edge cases only

WHY:
- Main rationale (2-3 bullets max)
- Critical tradeoffs only

GUARDRAILS:
- DO NOT [critical constraints, one line each]
- ALWAYS [essential requirements, one line each]
"""

Here's the function to document:

```python
{code}
```

File context: {filepath}

Generate ONLY the docstring content. Be CONCISE but include ALL sections above.
