# HANDOFF MASTER: Revolutionary AgentSpec Architecture (Consolidated, Context-Rich)
refer to @/HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md
Purpose
- This master document consolidates prior updates and the exhaustive recovery plan into a single, context-rich source. It removes outdated/ambiguous guidance, aligns provider semantics, and documents end-to-end steps to implement, validate, and operate the new architecture.

Background (Why this change)
- The legacy prompting produced verbose, inaccurate docs and format drift. Tests did not always validate the code paths changed. We are moving to:
  - Base prompt (example-free) + living examples.json
  - Enforced YAML format via CFG (Responses API tool) on the OpenAI path
  - Anchored examples with inline code_snippet and ASK USER guardrails
  - add-example (LLM-in-the-middle) for rapid dataset improvement
  - Multi-provider routing preserved (OpenAI, Anthropic, local/OpenAI-compatible)

Core Policies
- Base Prompt: agentspec/prompts/base_prompt.md contains principles, role, and format rules only; NO examples inside
- Examples: agentspec/prompts/examples.json is the living dataset; append at runtime to form the full developer message
- CFG Enforcement: OpenAI Responses API only; other providers follow adapted prompts without grammar
- Provider Semantics (CLI):
  - --provider openai → https://api.openai.com/v1 (GPT‑5, Responses/CFG)
  - --provider local → custom base-url (e.g., Ollama) using Chat Completions (no CFG)
  - --provider claude → Anthropic Messages API (no CFG)
  - Auto-routing by model prefix if --provider omitted: gpt‑5*→openai; claude*→claude; else → local if base_url present
- Output Wrapping: Generator emits YAML only. Inserters wrap appropriately: Python triple quotes; JS/TS JSDoc /** ... */
- Line Length / Wrapping: Honor project linters (Black/Flake8/Ruff); proactively wrap long lines and prefer concise bullets

Examples Dataset Schema (REQUIRED)
- code_snippet: REQUIRED, inline string with actual code (never a file path for the model to read)
- code_context: metadata only { file, function, subject_function, lines }
- bad_documentation: { text, why_bad, pattern }
- good_documentation: { what, why, guardrails[] } — include ASK USER when intent is ambiguous
- lesson: string

Anchored Example (Corrected)
{
  "id": "weak_test_assertion_jsdoc_extract",
  "type": "negative_then_positive",
  "language": "python",
  "code_snippet": "assert \"what\" in s.parsed_data",
  "code_context": {
    "file": "tests/test_extract_javascript_agentspec.py",
    "function": "test_extract_from_jsdoc_agentspec_block",
    "subject_function": "agentspec.extract.extract_from_js_file",
    "lines": "(inline snippet)"
  },
  "bad_documentation": {
    "text": "Assertion confirms that JSDoc parsing correctly identified and extracted AgentSpec structured data",
    "why_bad": "Claims semantic validation that does not occur; only checks key existence",
    "pattern": "lie_about_validation"
  },
  "good_documentation": {
    "what": "Checks presence of the 'what' key in parsed_data. WARNING: Does not validate content quality; any YAML with 'what' passes.",
    "why": "Integration sanity check: ensures extraction returned a dict with expected keys; not a semantic validation of YAML contents.",
    "guardrails": [
      "ASK USER: Before editing extract_from_js_file or this test, confirm whether the goal is content quality vs. key existence",
      "DO NOT conflate key-existence checks with semantic validation",
      "ALWAYS add separate tests for YAML quality if required"
    ]
  },
  "lesson": "Document actual checks performed; add ASK USER guardrails when intent is ambiguous."
}

Prompt Composition (OpenAI path)
1) Load base_prompt.md (no examples)
2) Load examples.json; for each example, format:
   - Title + Language
   - Code fence with code_snippet
   - ❌ BAD: text + Why Bad
   - ✅ GOOD: YAML (what|why|guardrails) including ASK USER
   - Lesson
3) Developer message = base + formatted examples
4) User message = fenced code of the target file

CFG Enforcement (OpenAI Responses API Only)
- Tools: [{ type: "custom", name: "agentspec_yaml", format: { type: "grammar", syntax: "lark", definition: <grammar> } }]
- Required fences: ---agentspec / ---/agentspec
- Required sections: what: |, why: |, guardrails:
- Guardrail types: DO NOT | ALWAYS | NOTE | ASK USER
- Indentation: 2 spaces; free-text allowed; obey linter wrapping
- Retries: On grammar failure, retry once with explicit instruction; no continuation hacks

Lark Grammar (Enforceable Draft)
start: block

block: START what_section why_section guardrails_section END

START: "---agentspec" NEWLINE
END: "---/agentspec" NEWLINE?

what_section: "what:" WS? "|" NEWLINE INDENT (TEXTLINE NEWLINE)+ DEDENT
why_section:  "why:"  WS? "|" NEWLINE INDENT (TEXTLINE NEWLINE)+ DEDENT
guardrails_section: "guardrails:" NEWLINE INDENT (GUARDRAIL NEWLINE)+ DEDENT

GUARDRAIL: "-" WS GUARD_TYPE ":" WS? GUARD_TEXT?
GUARD_TYPE: "DO NOT" | "ALWAYS" | "NOTE" | "ASK USER"

TEXTLINE: /[^\n]{1,200}/
GUARD_TEXT: /[^\n]{1,200}/

INDENT: /[ ]{2}/
DEDENT: /(?<!\G)/       
NEWLINE: /\n/
WS: /[ \t]/
%ignore /\t/

Multi‑Provider Routing (Preserved)
- OpenAI (GPT‑5): Responses API; CFG for as_agentspec_yaml; reasoning.effort minimal/low; text.verbosity low when --terse
- Claudе: Messages API; prompts adapted (no CFG); preserve functionality
- Local/OpenAI‑compatible (Ollama/qwen): Chat Completions fallback (no CFG); preserve functionality

add-example (LLM in the Middle via CLI)
- New core CLI: agentspec prompts
  - Add example: agentspec prompts --add-example --file <path> [--function <name>] [--subject-function <fqfn>] --bad-output "..." [--correction "..."] [--require-ask-user] [--dry-run]
  - Good-only: agentspec prompts --add-example --file <path> [--function <name>] [--subject-function <fqfn>] --good-output "..." [--require-ask-user] [--dry-run]
- Behavior: Extract snippet to code_snippet; analyze with LLM (Temp=0.0, minimal); output why_bad, good_what, good_why, good_guardrails[], lesson, pattern_type; enforce ASK USER when requested; maintain good_ratio ≥ 0.6

Proof Runs (Two Tracks; no stubs)
- Local regression:
  - Provider: local; Base URL: http://localhost:11434/v1; Model: qwen3-coder:30b/32b
  - Flags: --terse --force-context --agentspec-yaml --update-existing
- CFG demonstration (cloud):
  - Provider: openai; Base URL: https://api.openai.com/v1; Model: gpt‑5 or gpt‑5‑mini
  - Same flags; CFG auto-enabled
- Verify: rg -- '---agentspec' -- <file>; agentspec lint agentspec/ --strict; save logs under agentspec/.reports

Telemetry & Logging
- Log per run: provider, base_url, model, CFG used (y/n), token budgets; store in agentspec/.reports

Troubleshooting
- Overthinking: set reasoning.effort minimal/low; add stop conditions
- Too verbose: lower text.verbosity; prefer bullets
- Tool overload: cap tool calls; answer from context first
- Malformed calls: analyze system prompt/tool config for contradictions; fix

Guardrails
- Do NOT embed examples in base_prompt.md
- ALWAYS embed code_snippet; never rely on paths
- DO NOT break Anthropic or local providers; CFG is OpenAI-only
- DO NOT claim success without permanent-file proof runs (no stubs)
- ALWAYS quote ripgrep patterns or use --
- ALWAYS update agentspecs and changelogs for behavior changes

Runbook (Implementation Steps)
1) Implement compose_full_prompt() and generate_agentspec_yaml_cfg() (OpenAI path)
2) Restore multi-provider routing for openai/local/claude; auto-route by model prefix
3) Update examples.json schema (code_snippet required); fix weak example
4) Expose agentspec prompts --add-example CLI; document in CLI_QUICKREF.md, README.md, prompts/README.md
5) Fix TS/JS insertion validation (JSDoc wrappers, position); add targeted tests for Dashboard.tsx and indexing.js
6) Author routing/CFG unit tests; author TS/JS insertion tests
7) Run local proof (qwen via Ollama) and GPT‑5 proof (OpenAI)
8) Collect logs, run agentspec lint agentspec/ --strict; finalize

Acceptance Criteria
- Strict YAML via CFG on OpenAI path
- Multi-provider routes functional (openai/local/claude)
- Examples dataset anchored with code_snippet; ASK USER guardrails present
- Prompts CLI add-example works and documented
- Permanent-file proof runs pass; rg shows agentspec blocks; lint passes

References
- .serena/memories/gpt5_new_params_and_tools
- .serena/memories/gpt5_troubleshooting_and_tuning
- docs/OPENAI_PROMPT_GUIDES/responses_example.ipynb
- AGENTS.md (permanent files & testing rules)
