 End-to-End Flow

  - Entry: agentspec/generate.py:2340 loads .env, sets prov based on --provider and model, falls back to openai with local base URL if no API key.
  - File loop: agentspec/generate.py:2391 iterates files, calls process_file (Python) or process_js_file (JS/TS).
  - Per-function doc generation: agentspec/generate.py:1141 builds system prompt + examples and (if YAML mode) loads the Lark grammar. Calls llm.generate_chat with messages=[{'role':'system'},
    {'role':'user'}].
  - LLM router:
      - Anthropic path: agentspec/llm.py:134 uses messages.create but concatenates system+user into a single user message and does not pass system=. No CFG.
      - OpenAI-compatible path: agentspec/llm.py:193 tries Responses API first with max_output_tokens, reasoning, text.verbosity, and CFG tools if grammar_lark is provided. If that raises, it falls
        back to chat.completions.create (no CFG) at agentspec/llm.py:200+.
  - Post-process: Generation code intentionally does not strip model content and forcibly injects deterministic metadata (deps, changelog, diff) into whatever the model returned (see “NEVER TRY TO
    STRIP LLM CONTENT” in agentspec/generate.py:2328 context).

  Why Prompt/Echo Leakage Happens

  - Full examples are now included in the system prompt on YAML runs: agentspec/generate.py:1149–1170. They contain actual YAML bodies and even “bcrypt” guardrails from earlier mistakes. This was
    intentional and useful for Responses+CFG.
  - Anthropic path has no CFG and is not using system=. It collapses system+user into user content (agentspec/llm.py:141–152). That makes echoing example content into outputs more likely.
  - Local/Ollama/Qwen uses the Chat Completions fallback (no CFG). Same echo risk if Responses is unavailable or errors.
  - Because we never strip content and only inject deterministic sections, if the model emits multiple fenced YAML blocks or pasted prompt text, those land in docstrings as-is. You can
    see “I’m ready to generate AgentSpec…” strings that were emitted previously and are now baked into the code: agentspec/generate.py:1472, agentspec/generate.py:1256, agentspec/tests/
    test_diff_summary_wiring.py:49.

  Provider Expectations vs Current Behavior

  - OpenAI GPT‑5: Should use Responses API with CFG, FFC, reasoning/verbosity. Current code does this on the first path (agentspec/llm.py:193–201), and tests verify CFG injection: agentspec/tests/
    test_generate_responses_controls.py:94–118.
  - Ollama/local: Must use Chat Completions. Current fallback does that — but no CFG, so prompt echo risk is real.
  - Anthropic (Claude): Must use Messages API with proper system=. Current code does not use system= and concatenates system+user into one user prompt (agentspec/llm.py:141–152). Reference for
    correct form is in your docs: docs/CLAUDE_PROMPT_GUIDES/give-claude-a-role.md:30.

  System vs User placement for examples

  - Responses path collapses system+user into a single input string anyway, so moving examples from “system” to “user” won’t change much there. CFG is the real safety net for OpenAI.
  - Anthropic and Chat fallback do distinguish roles. Moving examples out of system can reduce their “authority” and may slightly reduce echoing, but it won’t eliminate it without either:
      - Using system= correctly for Anthropic, and
      - Adding output validation/selection logic for non‑Responses paths.

  Your “examples → lints” idea

  - This is strong. Instead of relying on the model to internalize examples, compile them into deterministic lint rules that block bad generations from being written.
  - Today’s linter (agentspec/lint.py) validates YAML shape/keys/length, but not:
      - Multiple ---agentspec blocks,
      - Prompt-echo phrases (“I’m ready…”, “Please share the code…”),
      - Provider API specifics (e.g., banning max_tokens for Responses docs).
  - It already has helpers and structure to extend: see extraction and YAML checks (agentspec/lint.py:560–604, agentspec/lint.py:300–420). A JSON-driven lint rules file produced by your notebook
    would let you add new, precise checks without touching prompt content. This directly enforces precision at commit time.

  What changed “recently” that increased leakage

  - Inclusion of FULL examples into the system prompt (agentspec/generate.py:1157–1170) → more raw content in context to be echoed.
  - Router enhancements added Responses + CFG but only for OpenAI-compatible providers; Anthropic and fallback remain unconstrained.
  - Anthropic path lost the system separation, which degrades instruction hygiene.

  Recommendations (research-backed, no code yet)

  - Per-provider base prompts:
      - base_prompt_openai_responses.md: minimal, rely on CFG; avoid embedding full example bodies — they’re redundant when CFG is strong.
      - base_prompt_anthropic.md: optimized for Anthropic with a concise role prompt in system= and only meta-lessons/guardrails (not full YAML bodies) to reduce echo. Use separate user message
        for code.
      - base_prompt_chat_local.md: minimal, and add strict output validation on our side (see below).
  - Anthropic messages: switch to passing system= (see docs/CLAUDE_PROMPT_GUIDES/give-claude-a-role.md:30) and send only one user message with code. Stop concatenating system into user.
  - Validation for non‑Responses paths:
      - Parse output and extract exactly one agentspec block by validating against the Lark grammar. If multiple appear, pick the one that parses and passes lints, else retry or fail with explicit
        diagnostics. This is not “first block wins”; it’s grammar-validated selection.
  - Turn examples into lint rules:
      - Extend agentspec/lint.py to error out on:
          - Multiple agentspec fenced blocks in a single docstring.
          - Presence of “prompt echo” phrases (configurable list from a rules JSON).
          - Provider/API‑specific mistakes you’ve observed (e.g., forbidden fields, duplicated sections).
      - Let your notebook export agentspec/prompts/lint_rules.json so adding a new bad pattern is a one-liner update in the notebook.

  Why this is safer and more precise

  - OpenAI Responses path stays precise by design (CFG/FFC/verbosity/reasoning). The base prompt can be slim.
  - Anthropic path regains correct semantics via system= and leaner examples (role instructions + lessons, not raw YAML).
  - Local/Chat fallback gets defensive selection and lint enforcement, preventing polluted outputs from landing in code.
  - Lints turn your growing set of “bad cases” into deterministic, testable gates — and they scale better than inflating the prompt.