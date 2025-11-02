# Agentspec Quality Review Rubric (Master)

Purpose
- Programmatic and manual checklist to assess generated AgentSpec YAML for accuracy, honesty, structure, readability, and guardrails. Used by Codex/Serena during proof runs. Not a Python unit test, but a deterministic review workflow.

Scope
- Apply to outputs inserted into permanent files:
  - /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx
  - /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py
  - /Users/davidmontgomery/agro/gui/js/indexing.js

Core Structural Checks (Automatable)
- Fences present: ---agentspec (start) and ---/agentspec (end)
- Required sections present in order: what: |, why: |, guardrails:
- Guardrail lines begin with "- " and start with one of: DO NOT | ALWAYS | NOTE | ASK USER
- Line lengths obey project linters (Black/Flake8/Ruff) and proactively wrap long lines
- No deps or changelog sections inside LLM output (they are injected deterministically elsewhere)
- No stray JSDoc/Python quoting issues (wrapper applied correctly per language)

Honesty and Non‑Hallucination (Manual + Heuristics)
- The "what" section describes only behavior evidenced in the code; no claims that are not present
- The "why" section is a 2–3 sentence rationale consistent with code/commit intent; no speculative narratives
- The guardrails reflect real risks and include ASK USER when intent is ambiguous (e.g., key-existence checks that do not validate content quality)
- No self‑congratulation, no "No AI slop" claims, no unverifiable performance or security assertions

Readability and Brevity
- Match documentation length to complexity; avoid line‑by‑line narration
- Prefer short bullets over long paragraphs; wrap long sentences appropriately
- No duplicated content; explicit notes when tests are weak or non-semantic

Context‑Sensitive Checks
- Python: YAML block wrapped in triple quotes; indentation correct; no syntax breakage
- JS/TS: YAML block wrapped in JSDoc /** ... */; placement before function/class; no nested comment confusion

Review Procedure (Codex/Serena)
1) Extract generated spec to Markdown for each permanent file:
   - agentspec extract <FILE> --format markdown > agentspec/.reports/<name>_extract.md
2) Run structural checks:
   - Use rg to verify fences/sections; run a small lark parse if available
3) Manual rubric pass:
   - Read what/why/guardrails; mark any hallucination or claims not supported by code
   - Confirm ASK USER present when ambiguity exists
   - Confirm readability/wrap and guardrail clarity
4) Summarize findings:
   - Write a short report per file: PASS/FAIL and notes
5) If FAIL:
   - Add an example via agentspec prompts --add-example, capturing the mistake and corrected form
   - Re-run generate and repeat review

Pass Criteria (all must be true)
- Structural checks pass (fences/sections/guardrails/line wrap obeyed)
- No hallucinated claims; what/why are grounded
- Guardrails meaningful; ASK USER present where appropriate
- Language‑specific wrappers correct; file compiles/parses
- Reviewer notes no readability regressions

Documentation
- Include review summaries in agentspec/.reports and in CHANGELOG if policy requires
