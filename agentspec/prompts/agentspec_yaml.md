# AgentSpec YAML Block Generation Prompt

You are helping to document a Python codebase by creating an embedded agentspec YAML block inside a Python docstring.



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
