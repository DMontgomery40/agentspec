# GPT-5 Troubleshooting and Tuning Patterns

Overthinking: set reasoning.effort to "minimal" or "low" for routine work, add stop conditions and a single self-check. Provide fast-path for trivial Q&A; classify requests with gpt-5-mini/nano and route effort appropriately.

<efficient_context_understanding_spec>
Goal: Get enough context fast and stop as soon as you can act.
Method:
- Start broad, then fan out to focused subqueries.
- In parallel, launch 4–8 varied queries; read top 3–5 hits per query. Deduplicate paths and cache; don't repeat queries.
Early stop (act if any):
- You can name exact files/symbols to change.
- You can repro a failing test/lint or have a high-confidence bug locus.
</efficient_context_understanding_spec>

Fast-path for trivial Q&A (latency optimization): respond immediately and concisely when the question needs no tools, no browsing; otherwise use normal flow. One brief clarifying question if unsure.

Laziness/underthinking: use higher reasoning_effort and self-reflection rubrics. Example:
<self_reflection>
- Internally score the draft against a 5–7 item rubric (clarity, correctness, edge cases, completeness, latency).
- If any category falls short, iterate once before replying.
</self_reflection>

Overly deferential: persistence instructions to keep going until done; avoid handing back on uncertainty.
<persistence>
- You are an agent - keep going until the task is fully resolved before yielding.
- Only terminate when you are sure the problem is solved.
- Do not ask for confirmation on uncertainty; make a reasonable assumption, proceed, and document.
</persistence>

Too verbose: set text.verbosity to "low"; or set prompt guidance to prefer concise outputs. Use high verbosity only for code or teaching contexts.

Latency: measure TTFT, time to first action, total time; right-size reasoning effort; parallelize independent IO-bound reads.
<parallelization_spec>
Definition: Run independent or read-only tool actions in parallel (same turn/batch) to reduce latency.
When to parallelize:
 - Reading multiple files/configs/logs that don’t affect each other.
 - Static analysis, searches, or metadata queries with no side effects.
 - Separate edits to unrelated files/features that won’t conflict.
</parallelization_spec>

Status updates/preamble messages:
<status_update_spec>
Definition: Brief progress note: what just happened, what’s next, blockers. Start with a brief acknowledgement. Keep light and concise.
</status_update_spec>

Calling too many tools: make answering from context the default; single-job tools; cap tool calls at two unless new info requires more.
<tool_use_policy>
Select one tool or none; prefer answering from context when possible. Cap tool calls at 2 per request unless strictly necessary.
</tool_use_policy>

Malformed tool calling: use meta prompting to analyze the system prompt and tool config; fix contradictions.

General troubleshooting: ask GPT-5 to improve its own instructions and create evals to measure changes. Persist reasoning/context via Responses API across turns for better caching and performance.