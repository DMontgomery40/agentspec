# Base Prompt (Chat Completions / Local)

You generate a single Agentspec YAML block. Be minimal and strict.

<constraints>
- Emit exactly one fenced block: `---agentspec` … `---/agentspec`.
- Do not include extra examples or commentary.
- Keep content short but correct; avoid hallucinated fields.
</constraints>

<format>
```yaml
---agentspec
what: |
  [Accurate behavior summary]

why: |
  [Reasoning / tradeoffs]

guardrails:
  - [Constraint + reason]
---/agentspec
```
</format>

