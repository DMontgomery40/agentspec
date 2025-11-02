# HANDOFF: Revolutionary AgentSpec Architecture Rewrite — Updates (Proposed)

This update replaces flawed example structures, clarifies prompt composition, documents multi‑provider routing, and specifies CFG enforcement details.

## Core Corrections

- Base Prompt Policy
  - base_prompt.md must be example‑free. It contains: role, mission, slop detection guidance, format requirements, and explicit wrapping rules.
  - Examples are appended at runtime from prompts/examples.json (living dataset) to form the full developer message.

- Examples Dataset Schema (REQUIRED)
  - code_snippet: REQUIRED, inline string with the actual code used to teach the model — never a file path. The model cannot read local paths.
  - code_context: metadata only { file, function, subject_function, lines }
  - bad_documentation: { text, why_bad, pattern }
  - good_documentation: { what, why, guardrails[] } — include ASK USER when intent is ambiguous
  - lesson: string

- Prompt Composition Flow (OpenAI path)
  1) Load base_prompt.md (no examples)
  2) Load examples.json, format each example as:
     - Language and Title
     - ```<language>\n<code_snippet>\n```
     - ❌ BAD: text + Why Bad
     - ✅ GOOD: YAML what|why|guardrails (with ASK USER when relevant)
     - Lesson
  3) Developer message = base + formatted examples
  4) User message = “Document this code from <file_path>:” + fenced code

- CFG Enforcement (OpenAI Responses API only)
  - Tools: [{ type: "custom", name: "agentspec_yaml", format: { type: "grammar", syntax: "lark", definition: <grammar> } }]
  - Required fences: ---agentspec / ---/agentspec
  - Required sections and order: what: |, why: |, guardrails:
  - Allowed guardrail types: DO NOT | ALWAYS | NOTE | ASK USER (provide rich examples of ASK USER)
  - Indentation: 2 spaces under each section; free‑text lines allowed
  - Line length: hard cap (e.g., 200 chars). Also instruct when to wrap: wrap sentences > 100–120 chars; prefer shorter bullets over long paragraphs; comply with Black/Flake8/Ruff readability conventions
  - Docstring syntax: Generation emits only the YAML block; the inserter wraps it in the target language’s docstring/JSDoc form (triple quotes for Python; /** … */ for JS/TS)

- Multi‑Provider Routing (Not One‑Solution)
  - OpenAI (GPT‑5): Responses API with CFG for as_agentspec_yaml
  - Anthropic (Claude/Haiku): messages.create with Claude‑optimized prompts (no CFG); adapt instructions to Messages API
  - OpenAI‑compatible (e.g., Ollama): Chat Completions fallback (no CFG); reuse prompts adapted to completions
  - Behavior: select path based on provider+base_url+model; do not break existing flows

- CLI Flags Proposal (to document; implement later)
  - Clarify provider semantics:
    - --provider openai-cloud → api.openai.com (GPT‑5, Responses API, CFG)
    - --provider openai-compatible → custom base-url (e.g., Ollama) using Chat Completions
    - --provider anthropic → Claude Messages API
  - Auto‑routing by model prefix when provider not set: gpt-5*→openai-cloud; claude*→anthropic; else → openai-compatible if base_url provided
  - No extra flags for CFG; enabled automatically on openai-cloud when as_agentspec_yaml
  - Improve --help: clear examples per provider; show exact commands for permanent files

## Anchored Example (Corrected)

```json
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
```

## Lark Grammar (Enforceable Draft)

```lark
start: block

block: START what_section why_section guardrails_section END

START: "---agentspec" NEWLINE
END: "---/agentspec" NEWLINE?

what_section: "what:" WS? "|" NEWLINE INDENT (TEXTLINE NEWLINE)+ DEDENT
why_section:  "why:"  WS? "|" NEWLINE INDENT (TEXTLINE NEWLINE)+ DEDENT
guardrails_section: "guardrails:" NEWLINE INDENT (GUARDRAIL NEWLINE)+ DEDENT

GUARDRAIL: "-" WS GUARD_TYPE ":" WS? GUARD_TEXT?
GUARD_TYPE: "DO NOT" | "ALWAYS" | "NOTE" | "ASK USER"

// Wrapped lines to keep readability; hard cap at ~200 chars; recommend wrapping > 100–120
TEXTLINE: /[^\n]{1,200}/
GUARD_TEXT: /[^\n]{1,200}/

INDENT: /[ ]{2}/
DEDENT: /(?<!\G)/    // Logical placeholder; enforced by tool runtime
NEWLINE: /\n/
WS: /[ \t]/
%ignore /\t/
```

## add-example LLM-in-the-Middle

- Purpose: Convert user provided good/bad docs + code context into a structured training example using an LLM middle layer
- Required behavior:
  - Temperature 0.0
  - Reasoning: minimal
  - Output: strict JSON with fields: why_bad, good_what, good_why, good_guardrails[], lesson, pattern_type
  - Prefer Responses API; if unavailable, fall back to Chat Completions; for Claude, adapt prompts to Messages API
  - Encourage **Freeform Function Calling** for raw‑text payloads to custom tools when JSON isn’t needed; for this path we still require JSON (deterministic)

## Proof Runs (Two Tracks)

- Standard regression (local):
  - Provider: openai-compatible (Ollama)
  - Base URL: http://localhost:11434/v1
  - Model: qwen3-coder:30b (or 32b per your note)
  - Flags: --terse --force-context --agentspec-yaml --update-existing
- CFG demonstration (cloud):
  - Provider: openai-cloud
  - Base URL: https://api.openai.com/v1
  - Model: gpt-5 (or gpt-5-mini)
  - Flags: same as above; CFG auto-enabled for as_agentspec_yaml

## Logging and Help Improvements

- CLI --help must show:
  - Provider modes, example commands for each (openai-cloud, anthropic, openai-compatible)
  - Permanent file commands exactly
  - Error messages with actionable fixes (keys, base_url, model)
- Generate proof logs: provider, base_url, model, CFG tool used (y/n), token budgets

## Docstring Wrappers
- Generator emits only the YAML block; inserter applies language-specific wrappers:
  - Python: triple quotes around YAML block
  - JS/TS: JSDoc /** ... */ around YAML block

END OF UPDATE
