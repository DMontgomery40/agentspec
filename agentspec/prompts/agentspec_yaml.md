# AgentSpec YAML Block Generation Prompt

You are helping to document a Python codebase by creating an embedded agentspec YAML block inside a Python docstring.

Deterministic metadata collected from the repository (if any):
{hard_data}

Instructions for using deterministic metadata:
- Use deps.calls/imports directly when present.
- If any field contains a placeholder beginning with "No metadata found;", still produce a complete section based on the function code and context.
- If changelog contains an item that begins with "- Current implementation:", complete that line with a concise, concrete one‑sentence summary of the function's current behavior (do not leave it blank).

Deterministic metadata collected from the repository (if any):
{hard_data}

Requirements:
- Output ONLY the YAML block fenced by the following exact delimiters:
  ---agentspec
  ... YAML content here ...
  ---/agentspec
- Follow this schema with verbose content (deps and changelog will be injected by code):
  what: |
    Detailed multi-line explanation of behavior, inputs, outputs, edge-cases
  why: |
    Rationale for approach and tradeoffs
  guardrails:
    - DO NOT ... (explain why)
    - ...

Context:
- Function to document:

```python
{code}
```

- File path: {filepath}

Important:
- Produce strictly valid YAML under the delimiters.
- Do NOT include triple quotes or any prose outside the fenced YAML.
- Be comprehensive and specific.
