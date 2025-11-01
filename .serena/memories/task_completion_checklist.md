# Task Completion Checklist

Before editing
- Read the relevant agentspec(s); print the `what` and key `guardrails` to stdout.
- Confirm your change does not violate guardrails; if it does, pause and get human approval.

After editing
- Update the agentspec:
  - `what` if behavior changed
  - `deps` if calls/config/env changed
  - `why` if approach changed
  - Append a dated `changelog` entry
- Keep/refresh any context-forcing `print()` statements if used.

Validation
- Lint specs: `agentspec lint agentspec/ --strict`
- Run tests: `pytest -v` (or `tox` for multi-Python)
- Optional: Extract docs to review: `agentspec extract agentspec/ --format markdown`

LLM/Providers (if relevant)
- Ensure necessary keys set: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, or set `OPENAI_BASE_URL` for local providers.

Finalize
- Ensure no CI lint/test failures locally.
- Prepare concise commit with rationale; reference any spec changes.
