# Verbose Docstring Generation Prompt

You are helping to document a Python codebase with extremely verbose docstrings designed for AI agent consumption.

Deterministic metadata collected from the repository (if any):
{hard_data}

Instructions for using deterministic metadata:
- Use deps.calls/imports directly when present.
- If any field contains a placeholder beginning with "No metadata found;", still produce a complete section based on the function code and context.
- If changelog contains an item that begins with "- Current implementation:", complete that line with a concise, concrete one‑sentence summary of the function's current behavior (do not leave it blank).

Deterministic metadata collected from the repository (if any):
{hard_data}

Analyze this function and generate a comprehensive docstring following this EXACT format:

"""
Brief one-line description.

WHAT THIS DOES:
- Detailed explanation of what this function does (3-5 lines)
- Include edge cases, error handling, return values
- Be specific about types and data flow

WHY THIS APPROACH:
- Explain why this implementation was chosen
- Note any alternatives that were NOT used and why
- Document performance considerations
- Explain any "weird" or non-obvious code

AGENT INSTRUCTIONS:
- DO NOT [list things agents should not change]
- ALWAYS [list things agents must preserve]
- NOTE: [any critical warnings about this code]
"""

Here's the function to document:

```python
{code}
```

File context: {filepath}

Generate ONLY the docstring content (without the triple quotes themselves). Be extremely verbose and thorough.
