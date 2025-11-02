# Handoff Architecture Recovery Plan (Exhaustive)

Context
- Must follow AGENTS.md: permanent files only; prove with agentspec generate + required flags; no temp tests; no stubs.
- Base prompt must be example-free; examples.json appended at runtime.
- CFG must be enforced through OpenAI Responses API tool with Lark grammar on the OpenAI path.
- Preserve multi-provider routing (Anthropic / OpenAI / OpenAI-compatible), not a one-solution platform.

Objectives
- Wire CFG-enforced YAML generation for as_agentspec_yaml.
- Compose prompts as base + examples.json (with code_snippet embedded).
- Keep Anthropic + OpenAI-compatible paths operational.
- Fix JSDoc/TSX insertion validation for TSX/JS permanent files.
- Provide add-example CLI UX and docs.
- Update the handoff doc to match reality and feedback.

Deliverables
1) New generator functions: compose_full_prompt(), generate_agentspec_yaml_cfg()
2) llm.py provider routing preserved (Anthropic/OpenAI/OpenAI-compatible)
3) examples.json schema with code_snippet and anchored example updated
4) CLI subcommand: agentspec add-example (with help)
5) Fixed TS/JS insertion; targeted tests for Dashboard.tsx and indexing.js
6) Updated HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md (bad examples replaced, CFG clarified)
7) Proof runs on permanent files with required flags (no stubs) and logs

Guardrails
- DO NOT embed examples inside base_prompt.md
- DO NOT expect LLM to read files referenced in examples.json; ALWAYS embed code_snippet
- DO NOT remove Anthropic or OpenAI-compatible support; CFG only on OpenAI Responses path
- DO NOT claim success without permanent-file generate proof runs (no stubs)
- ALWAYS quote ripgrep regex like '---agentspec' or use `--` to avoid flag confusion
- ALWAYS update related agentspecs (changelog) when behavior changes

Runbooks

A) Prompt Composition + CFG (OpenAI path)
1. Add compose_full_prompt(code: str, file_path: str) in agentspec/generate.py
   - Load prompts/base_prompt.md.
   - Load prompts/examples.json; for each example, format the section:
     - Title: Example: <id> (Language: <lang>)
     - Code fence using example.code_snippet (```<lang>)
     - If negative_then_positive: show BAD text and why_bad; then GOOD (what|why|guardrails) with ASK USER guardrail if given
     - Lesson line
   - Return (developer_content: base + formatted examples, user_content: "Document this code from <file_path>:\n```\n<code>\n```")
2. Add generate_agentspec_yaml_cfg(code, file_path) in agentspec/generate.py
   - client = OpenAI(base_url=https://api.openai.com/v1)
   - tools=[{"type":"custom","name":"agentspec_yaml","format":{"type":"grammar","syntax":"lark","definition": load_agentspec_yaml_grammar()}}]
   - input = [ {role:"developer", content: developer_content}, {role:"user", content: user_content} ]
   - reasoning.effort: minimal if len(code.splitlines())<=12 else low/medium; text.verbosity: low for --terse
   - response = client.responses.create(...)
   - Extract tool output as YAML; if grammar mismatch detected, retry once with explicit instruction, else fail with actionable error
3. Integrate: In generate_docstring(), when as_agentspec_yaml=True and provider='openai' (api.openai.com), call generate_agentspec_yaml_cfg; otherwise fall back to narrative + deterministic metadata injection (no CFG on non-OpenAI paths)

B) Multi-Provider Routing Restoration (llm.py)
1. Anthropic path: unchanged, anthropic.messages.create
2. OpenAI path:
   - If base_url == https://api.openai.com/v1 → Responses API; support CFG tool when caller requests as_agentspec_yaml=True
   - Else (OpenAI-compatible) → Chat Completions fallback (no CFG)
3. Add environment override but do not override explicit base_url; provider flag respected
4. Tests: three small unit tests verifying routing branches and arguments

C) examples.json Schema Update
1. Replace entries to include:
   - id, type, language
   - code_snippet: REQUIRED
   - code_context: { file, function, subject_function, lines } (metadata only)
   - bad_documentation: { text, why_bad, pattern }
   - good_documentation: { what, why, guardrails[] }
   - lesson
2. Correct the weak JS extraction example:
   - Embed the exact code snippet demonstrating `assert "what" in s.parsed_data` in context; include ASK USER guardrail
3. Update loader to validate code_snippet is present

D) add-example UX
1. Expose as CLI subcommand: agentspec add-example
2. --file/--function/--subject-function/--bad-output/--good-output/--correction/--require-ask-user/--dry-run/--strict-ratio
3. Extract AST-snippet for Python or capture around function signature for JS/TS; store as code_snippet
4. LLM analysis produces why_bad, good_what, good_why, good_guardrails, lesson, pattern_type; enforce ASK USER if requested
5. Update examples.json accordingly (append) unless --dry-run
6. Docs: Add to TOOLS or README; `agentspec add-example --help`

E) TS/JS Insertion Fix
1. Ensure YAML is wrapped inside valid JSDoc (/** ... */)
2. Insert before function/class; avoid nested comment issues
3. Validate compile/run after insertion (basic syntax checks); rollback if invalid
4. Tests: verify at least one inserted block with '---agentspec' in Dashboard.tsx and indexing.js using required flags

F) Handoff Doc Update (HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md)
1. Replace flawed example schema with code_snippet REQ
2. Clarify: base_prompt.md contains no examples; compose at runtime
3. Document routing: OpenAI (Responses+CFG), Anthropic (messages), OpenAI-compatible (chat.completions); CFG only on OpenAI
4. Replace placeholder grammar with realistic Lark grammar (fences, required sections, guardrails types, line caps)
5. Add troubleshooting (verbosity/minimal reasoning, persistence, parallelization, caching) and your noted failure case

G) Proof Runs (no stubs)
1. Commands:
   - agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
   - agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
   - agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
2. Verify:
   - rg -- '---agentspec' -- <file>
   - agentspec lint agentspec/ --strict
   - Save logs in agentspec/.reports/generate_[dashboard|phaxio|indexing].txt

H) Telemetry
- For each generate call, log: provider, base_url, model, CFG tool present (y/n), prompt_tokens_est, output_tokens_est

I) Rollback & Compatibility
- Keep existing Anthropic and OpenAI-compatible flows functioning for narrative mode and YAML (no CFG)
- Env and flags to force provider routing when needed

Checklists
- Pre-change: read agentspecs, guardrails
- Post-change: update agentspecs (what/why/deps/changelog); run lint/tests; provide proof logs

End of plan.
