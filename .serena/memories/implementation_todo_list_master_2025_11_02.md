# Implementation TODO List (Programmatic, Executable by Humans and Agents)

Legend
- [ ] pending, [x] done, [!] blocker, [~] needs review

Prereqs
- [ ] Ensure OPENAI_API_KEY in .env for GPT‑5
- [ ] Ensure Ollama endpoint at http://localhost:11434/v1 for qwen
- [ ] Decide provider by flags: --provider openai | local | claude

A. Generator: Prompt Composition + CFG (OpenAI path)
- [ ] Add compose_full_prompt(code: str, file_path: str) in agentspec/generate.py
  - [ ] Load prompts/base_prompt.md (must be example‑free)
  - [ ] Load prompts/examples.json and format examples with inline code_snippet
  - [ ] Return (developer_content, user_content) strings
- [ ] Add generate_agentspec_yaml_cfg(code, file_path) in agentspec/generate.py
  - [ ] Build Responses API request with tools=[{ name: agentspec_yaml, grammar lark from prompts/agentspec_yaml.lark }]
  - [ ] Set reasoning.effort minimal for ≤12 LOC else low/medium; text.verbosity low when --terse
  - [ ] Extract YAML tool output; on grammar failure, retry once with explicit instruction
- [ ] Integrate: if as_agentspec_yaml=True and provider=openai with base_url api.openai.com → call CFG path

B. Multi‑Provider Routing
- [ ] Restore llm.py routing for openai/local/claude
  - [ ] openai → Responses API (CFG if as_agentspec_yaml)
  - [ ] local → Chat Completions fallback (no CFG)
  - [ ] claude → Anthropic Messages API (no CFG)
  - [ ] Auto‑route by model prefix when --provider omitted: gpt‑5*→openai; claude*→claude; else → local if base_url present
- [ ] Add unit tests for each branch with monkeypatch to assert correct client/method

C. Examples Dataset
- [ ] Update prompts/examples.json schema to require code_snippet; keep code_context as metadata
- [ ] Replace weak example with corrected anchored example including ASK USER guardrail
- [ ] Enforce loader validation (raise if code_snippet missing)

D. CLI: Prompts Core Utility
- [ ] Add CLI command: agentspec prompts
  - [ ] Option: --add-example with args: --file, --function, --subject-function, --bad-output/--good-output, --correction, --require-ask-user, --dry-run, --strict-ratio
  - [ ] Extract snippet (AST for Python; proximity/window for JS/TS)
  - [ ] LLM middle call: Temp=0.0; reasoning=minimal; strict JSON fields (why_bad, good_what, good_why, good_guardrails[], lesson, pattern_type)
  - [ ] Append to examples.json unless --dry-run; enforce good_ratio ≥ 0.6 by default
  - [ ] Help text with examples; add to CLI_QUICKREF.md, README.md, prompts/README.md

E. JS/TS Insertion Validation Fix
- [ ] Ensure JSDoc /** ... */ wrapper for YAML block
- [ ] Correct insertion point (before function/class); avoid nested comments
- [ ] Add verification to reject invalid insert; rollback on failure
- [ ] Add targeted tests that confirm agentspec blocks appear in Dashboard.tsx and indexing.js

F. Lark Grammar (Strengthen and Align)
- [ ] Finalize prompts/agentspec_yaml.lark with fences, what/why/guardrails order, guardrail types, line limits, indentation
- [ ] Add instructions to wrap lines proactively per linter caps

G. Proof Runs (No Stubs)
- [ ] Local (qwen via Ollama):
  - [ ] agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx --provider local --base-url http://localhost:11434/v1 --model qwen3-coder:32b --terse --force-context --agentspec-yaml --update-existing
  - [ ] agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py --provider local --base-url http://localhost:11434/v1 --model qwen3-coder:32b --terse --force-context --agentspec-yaml --update-existing
  - [ ] agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js --provider local --base-url http://localhost:11434/v1 --model qwen3-coder:32b --terse --force-context --agentspec-yaml --update-existing
- [ ] GPT‑5 (CFG OpenAI):
  - [ ] agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
  - [ ] agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
  - [ ] agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js --provider openai --base-url https://api.openai.com/v1 --model gpt-5-mini --terse --force-context --agentspec-yaml --update-existing
- [ ] Save logs to agentspec/.reports/generate_[dashboard|phaxio|indexing]_(local|openai).txt
- [ ] Verify with ripgrep: rg -- '---agentspec' -- <file>
- [ ] agentspec lint agentspec/ --strict

H. Agentspec Quality Review (Manual + Heuristics)
- [ ] Extract to Markdown: agentspec extract <FILE> --format markdown > agentspec/.reports/<name>_extract.md
- [ ] Run structural checks (fences/sections/guardrails; lark parse optional)
- [ ] Manual rubric pass using memory: agentspec_quality_rubric_master_2025_11_02
- [ ] Summarize PASS/FAIL per file with notes in agentspec/.reports/<name>_review.txt
- [ ] If FAIL: add corrected examples via agentspec prompts --add-example and regenerate

I. Telemetry & Logging
- [ ] For each generate call, log: provider, base_url, model, CFG used (y/n), token budgets

J. Documentation
- [ ] Update HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md (already updated; ensure pointer to master memory)
- [ ] Update CLI_QUICKREF.md with provider modes and exact commands
- [ ] Update README.md with prompts CLI and dual proof track
- [ ] Update agentspec/prompts/README.md with examples schema and composition

K. Acceptance & Sign‑off
- [ ] Permanent-file proof runs pass (both tracks)
- [ ] rg checks show agentspec blocks in all three files
- [ ] agentspec lint agentspec/ --strict passes
- [ ] Quality rubric PASS for all files (no hallucinations, ASK USER guardrails present, readable)
- [ ] Provider routing tests pass (openai/local/claude)
- [ ] Handoff + docs updated and consistent
