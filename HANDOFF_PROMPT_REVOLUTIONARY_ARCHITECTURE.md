# ✅ UPDATE 2025-11-02 — Corrections to Handoff Architecture (READ FIRST)

This update clarifies the final, enforceable architecture and fixes earlier mistakes. It is the authoritative addendum; all implementers must follow it exactly.

## Core Corrections

- Base Prompt Policy
  - `agentspec/prompts/base_prompt.md` MUST be example‑free. It defines role, mission, slop detection, format rules, wrapping rules, and output contract only.
  - Examples are appended at runtime from `agentspec/prompts/examples.json` to form the full developer message.

- Examples Dataset Schema (REQUIRED)
  - `code_snippet`: REQUIRED inline string of the actual code. Do NOT provide file paths for the model to read.
  - `code_context`: metadata only `{ file, function, subject_function, lines }` (for analytics, not for model reading)
  - `bad_documentation`: `{ text, why_bad, pattern }`
  - `good_documentation`: `{ what, why, guardrails[] }` — include ASK USER where intent is ambiguous
  - `lesson`: string

- Prompt Composition Flow (OpenAI path)
  1) Load `base_prompt.md` (no examples)
  2) Load `examples.json`; for each example, format:
     - Title + Language
     - ```<language>\n<code_snippet>\n```
     - ❌ BAD: text + Why Bad
     - ✅ GOOD: YAML (what|why|guardrails) including ASK USER when appropriate
     - Lesson
  3) Developer message = base + formatted examples
  4) User message = “Document this code from <file_path>:” + fenced code

- CFG Enforcement (OpenAI Responses API only)
  - Tools: `[{ type: "custom", name: "agentspec_yaml", format: { type: "grammar", syntax: "lark", definition: <grammar> } }]`
  - Required fences: `---agentspec` / `---/agentspec`
  - Required sections and order: `what: |`, `why: |`, `guardrails:`
  - Guardrail types: `DO NOT` | `ALWAYS` | `NOTE` | `ASK USER` (include rich examples of ASK USER)
  - Indentation: 2 spaces under each section; free‑text lines allowed
  - Line length: hard cap ~200 chars. Soft wrap at ~100–120. Prefer short bullets over long paragraphs; comply with readability (Black/Flake8/Ruff style expectations).
  - Line length: hard cap per linter (Black/Flake8/Ruff project max). Wrap long sentences proactively; prefer short bullets over long paragraphs; comply with Black/Flake8/Ruff style expectations.

- Multi‑Provider Routing (Not One‑Solution)
  - OpenAI (GPT‑5): Responses API + CFG for `as_agentspec_yaml`
  - Anthropic (Claude/Haiku): Messages API with Claude‑adapted prompts (no CFG)
  - OpenAI‑compatible (e.g., Ollama, qwen): Chat Completions fallback (no CFG)
  - Selection is by provider + model + base_url. Do not break non‑OpenAI routes.

- CLI Flags Proposal (document now; implement later)
  - `--provider openai-cloud` → `https://api.openai.com/v1` (GPT‑5, Responses+CFG)
  - `--provider openai` → `https://api.openai.com/v1` (GPT‑5, Responses+CFG)
  - `--provider local` → custom base-url (e.g., Ollama) using Chat Completions
  - `--provider claude` → Claude Messages API
  - Auto‑route by model prefix when `--provider` omitted (`gpt-5*`→openai; `claude*`→claude; else → local if base_url present)
  - No extra flags for CFG; turns on automatically on `openai` when `--agentspec-yaml`.
  - Improve `--help`: provider modes, permanent file examples, actionable errors.

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

## Enforceable Lark Grammar (Draft)

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

TEXTLINE: /[^\n]{1,200}/    // hard cap per line; recommend wrapping at ~100–120
GUARD_TEXT: /[^\n]{1,200}/

INDENT: /[ ]{2}/
DEDENT: /(?<!\G)/        // placeholder; indentation checked by tool runtime
NEWLINE: /\n/
WS: /[ \t]/
%ignore /\t/
```

## Docstring Wrappers (Inserter Responsibility)
- Python: wrap the YAML block in triple quotes
- JS/TS: wrap the YAML block in a JSDoc comment `/** ... */`

- Standard regression (local): provider local, base_url `http://localhost:11434/v1`, model `qwen3-coder:30b/32b`, flags: `--terse --force-context --agentspec-yaml --update-existing`
- CFG demonstration (cloud): provider openai-cloud, base_url `https://api.openai.com/v1`, model `gpt-5` or `gpt-5-mini`, same flags; CFG auto-enabled

## Logging & Help
- `agentspec/cli.py` must present provider modes, permanent-file examples, and errors with direct fixes (keys, URLs, models)
- Generate proof logs: provider, base_url, model, CFG tool used (y/n), token budgets

END OF UPDATE

# 🚨 HANDOFF: Revolutionary AgentSpec Architecture Rewrite

**Date**: 2025-11-02
**Status**: CRITICAL - Complete architectural overhaul required
**Priority**: P0 - Current prompts are fundamentally broken

---

## 📋 Executive Summary

The current AgentSpec generation system produces **AI slop documentation that lies about what code does**. This handoff documents a revolutionary new architecture that:

1. Uses **CFG (Context-Free Grammar)** to enforce YAML structure
2. Uses **OpenAI Responses API with freeform function calling** for generation
3. Implements **single living examples.json** that users can update programmatically
4. Provides **advanced parsing tool** for users to turn bad outputs into training examples
## CLI: Prompts Core Utility

- Introduce a new core CLI command: `agentspec prompts`
  - Add example to dataset: `agentspec prompts --add-example --file <path> [--function <name>] [--subject-function <fqfn>] --bad-output "..." [--correction "..."] [--require-ask-user] [--dry-run]`
  - Add good-only example: `agentspec prompts --add-example --file <path> [--function <name>] [--subject-function <fqfn>] --good-output "..." [--require-ask-user] [--dry-run]`
  - Future subcommands (document only for now): `--list-examples`, `--lint-examples`, `--extract-examples`
- Behavior
  - Extract snippet and store as `code_snippet`; `code_context` retained as metadata
  - LLM-in-the-middle analysis (Temp=0.0; reasoning=minimal) outputs JSON fields: why_bad, good_what, good_why, good_guardrails[], lesson, pattern_type
  - Enforce ASK USER guardrail when requested; enforce good_ratio ≥ 0.6 by default
- Docs
  - Update CLI_QUICKREF.md, README.md, and agentspec/prompts/README.md with examples and troubleshooting

---

## 🔥 Critical Pain Points (Why Current System is Broken)

### Pain Point #1: Documentation That Lies

**Example from production:**
```python
# THE CODE:
def test_extract_from_jsdoc_agentspec_block():
    specs = extract.extract_from_js_file(fixture)
    assert specs
    assert s.name in {"demo", "(anonymous)"}
    assert s.raw_block
    assert isinstance(s.parsed_data, dict)
    assert "what" in s.parsed_data  # ← ONLY checks key exists

# THE LIE (generated by current prompt):
"""
Assertion 4: confirms that JSDoc parsing correctly identified
and extracted the AgentSpec YAML/structured data (not just raw text)
"""
```

**Reality**: Test only checks `"what" in dict`. Doesn't validate content quality. This would pass:
```yaml
what: garbage code lol
```

**Root Cause**: Prompts say "be verbose and thorough" which leads to:
- Line-by-line explanations of obvious code
- Extrapolating intent instead of describing reality
- Self-congratulatory statements ("No AI slop detected")
- Metadata leakage (deps sections still present)

### Pain Point #2: Bloated Output

**Current metrics:**
- 8 lines of test code → 54 lines of documentation
- "Terse" mode uses MORE tokens than verbose mode (6301 vs 5880 prompt tokens, 1282 vs 1077 output)
- Reasoning requirement in terse mode makes it LESS terse

**Why this happened**: "Be verbose and thorough" instruction combined with "think deeply BEFORE writing" creates maximum verbosity.

### Pain Point #3: No Format Enforcement

Current system uses `.format()` to inject code into prompt template. This leads to:
- Brace escaping nightmares (`{username}` → `{{username}}`)
- No guarantee of valid YAML output
- Manual post-processing required
- Format drift over time

### Pain Point #4: Static Examples That Don't Match User Codebases

Current examples are hardcoded in prompts. User has React codebase with specific patterns, but examples show Python Flask. Result: Generic documentation that doesn't match their code style.

### Pain Point #5: No Mechanism for Improvement

When documentation is bad, there's no path for users to:
1. Highlight the bad output
2. Explain what's wrong
3. Add it to training set
4. Improve future generations

System can't learn from mistakes.

---

## 🎯 The Revolutionary New Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GENERATION FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. User runs: agentspec generate file.py

2. generate.py loads:
   ├── agentspec/prompts/base_prompt.md          (lightweight core)
   ├── agentspec/prompts/agentspec_yaml.lark     (CFG grammar)
   └── agentspec/prompts/examples.json           (living dataset)

3. generate.py calls OpenAI Responses API:
   {
     "model": "gpt-5",
     "input": [
       {"role": "developer", "content": base_prompt + examples},
       {"role": "user", "content": code_to_document}
     ],
     "tools": [{
       "type": "custom",
       "name": "agentspec_yaml",
       "format": {
         "type": "grammar",
         "syntax": "lark",
         "definition": agentspec_yaml_grammar
       }
     }],
     "reasoning": {"effort": "medium"}  # or "minimal" for simple code
   }

4. Response is GUARANTEED valid YAML (enforced by CFG)

5. If user finds bad output → add_example.py tool

┌─────────────────────────────────────────────────────────────┐
│                   IMPROVEMENT FLOW                           │
└─────────────────────────────────────────────────────────────┘

User sees bad documentation:
  "confirms that JSDoc parsing correctly identified..."

User runs:
  python agentspec/tools/add_example.py \
    --file tests/test_extract.py \
    --bad-output "confirms that JSDoc parsing correctly identified..." \
    --correction "Only checks 'what' key exists, doesn't validate content"

add_example.py:
  1. Extracts code context
  2. Identifies what's wrong
  3. Generates corrected example
  4. Appends to examples.json:
     {
       "type": "negative_then_positive",
       "code": "assert \"what\" in s.parsed_data",
       "bad_doc": "confirms JSDoc parsing correctly identified...",
       "why_bad": "Claims validation that doesn't happen",
       "good_doc": "Checks 'what' key exists. NOTE: Doesn't validate content quality.",
       "lesson": "Don't extrapolate intent. Describe what code ACTUALLY does."
     }

Next generation: System learns from this mistake.
```

---

## 📁 File Structure Changes

### New Files to Create

```
agentspec/
├── prompts/
│   ├── base_prompt.md                    # NEW: Lightweight core (no examples)
│   ├── agentspec_yaml.lark              # NEW: CFG grammar for YAML
│   ├── examples.json                     # NEW: Single living dataset
│   └── [KEEP] agentspec_yaml.md         # OLD: Backup/reference
│
├── tools/
│   └── add_example.py                    # NEW: Advanced example parser
│
└── generate.py                           # MODIFY: Use Responses API
```

### Files to Modify

**agentspec/generate.py**
- Switch from Chat Completions API to Responses API
- Load base_prompt.md + examples.json
- Use CFG for format enforcement
- Add reasoning effort parameter
- Remove `.format()` string substitution (CFG handles structure)

**agentspec/prompts.py**
- Add `load_examples()` function
- Add `load_grammar()` function
- Modify `get_agentspec_yaml_prompt()` to return base + examples

---

## 🔧 Implementation Details

### 1. Base Prompt (base_prompt.md)

**Design Principles:**
- **Honesty First**: Describe what code ACTUALLY does, not what it tries to do
- **Brevity**: 10 lines of code = max 10 lines of docs
- **Call Out Weakness**: If test is weak, say so explicitly
- **No Line-by-Line**: Only explain non-obvious parts
- **ASK USER Pattern**: When intent unclear, add guardrail asking for clarification

**Structure:**
```markdown
# AgentSpec YAML Generator

You are documenting code for AI agents that will edit it later.

## Core Rules

1. HONESTY: Describe what code ACTUALLY does
   - ✅ "Checks 'what' key exists"
   - ❌ "Validates agentspec content quality"

2. BREVITY: Match documentation length to code complexity
   - 10 lines of code → max 10 lines of docs
   - Simple test → simple docs

3. WEAKNESS: Call out weak tests/code
   - "WARNING: Only checks key existence, not content"
   - "NOTE: No input validation, accepts garbage"

4. ASK USER: When intent unclear, don't guess
   - guardrails:
     - ASK USER: "Was this test designed to validate content quality?"

## Output Format

Generate YAML using the agentspec_yaml tool (CFG-enforced).

## Examples

[Examples from examples.json will be appended here]
```

### 2. CFG Grammar (agentspec_yaml.lark)

```lark
// AgentSpec YAML Grammar
// Enforces structure, prevents format drift

start: yaml_block

yaml_block: "---agentspec" NEWLINE what_section why_section guardrails_section "---/agentspec"

what_section: "what: |" NEWLINE (INDENT line NEWLINE)+
why_section: "why: |" NEWLINE (INDENT line NEWLINE)+
guardrails_section: "guardrails:" NEWLINE (INDENT guardrail NEWLINE)+

guardrail: "- " guardrail_type ": " text
guardrail_type: "DO NOT" | "ALWAYS" | "NOTE" | "ASK USER"

line: /[^\n]{0,200}/  // Max 200 chars per line (prevents bloat)
text: /[^\n]{0,300}/

INDENT: "  "
NEWLINE: "\n"

%import common.WS
%ignore WS
```

**Key Features:**
- Max line length (200 chars) prevents bloat
- Enforces exact structure (what, why, guardrails required)
- `ASK USER` as valid guardrail type
- Strict delimiters (---agentspec / ---/agentspec)

### 3. Examples JSON (examples.json)

**Structure:**
```json
{
  "version": "1.0",
  "last_updated": "2025-11-02",
  "examples": [
    {
      "id": "weak_test_assertion",
      "type": "negative_then_positive",
      "language": "python",
      "code": "assert \"what\" in s.parsed_data",
      "context": "Test checking if agentspec was extracted",
      "bad_documentation": {
        "what": "Assertion 4: confirms that JSDoc parsing correctly identified and extracted the AgentSpec YAML/structured data (not just raw text)",
        "why_bad": "Claims validation that doesn't happen - test only checks key existence"
      },
      "good_documentation": {
        "what": "Checks 'what' key exists in parsed_data dict. WARNING: Doesn't validate content quality. Garbage agentspecs pass this test.",
        "why": "Test validates parser doesn't crash and returns dict with expected key, not that content is valid."
      },
      "lesson": "Don't extrapolate validation. Describe ACTUAL checks performed."
    },
    {
      "id": "stub_function",
      "type": "ai_slop_detection",
      "language": "python",
      "code": "def authenticate(username, password):\n    # TODO: Implement OAuth2\n    return True",
      "good_documentation": {
        "what": "Stub authentication that always grants access. Comment indicates OAuth2 never implemented. Returns True regardless of credentials.",
        "why": "Walking skeleton from abandoned OAuth2 refactor (6 months old per git). 'TODO' in production = critical vulnerability.",
        "guardrails": [
          "DO NOT call for production auth; always returns True",
          "ALWAYS implement real authentication before deployment",
          "NOTE: CRITICAL - zero authentication, anyone can access system"
        ]
      },
      "lesson": "Stubs must be flagged explicitly with severity."
    },
    {
      "id": "react_missing_loading_state",
      "type": "ai_slop_detection",
      "language": "typescript",
      "code": "function Dashboard() {\n  const [data, setData] = useState(null);\n  useEffect(() => { fetchData().then(setData); }, []);\n  return <h1>Welcome {data.user.name}</h1>;\n}",
      "good_documentation": {
        "what": "Dashboard that crashes on mount. Initializes data=null, then renders {data.user.name} before fetch completes. Crashes: 'Cannot read property user of null'.",
        "why": "AI-generated happy-path-only component. Missing loading/error states = vibe-coded UI never tested in browser.",
        "guardrails": [
          "DO NOT deploy; crashes 100% of the time",
          "ALWAYS add: if (!data) return <Loading />",
          "NOTE: Classic AI slop - test in browser before committing"
        ]
      },
      "lesson": "UI components need loading/error state checks. AI forgets async lifecycle."
    }
  ]
}
```

**Fields:**
- `type`: `positive` | `negative_then_positive` | `ai_slop_detection`
- `language`: Helps match to user's codebase
- `lesson`: Extractable principle for the LLM to learn

### 4. Advanced Example Parser (add_example.py)

**Purpose**: Let users turn bad outputs into training examples with ONE command.

**Usage:**
```bash
# Highlight bad output, run this:
python agentspec/tools/add_example.py \
  --file tests/test_extract.py \
  --function test_extract_from_jsdoc_agentspec_block \
  --bad-output "confirms that JSDoc parsing correctly identified and extracted the AgentSpec YAML/structured data" \
  --correction "Only checks 'what' key exists, doesn't validate content"

# OR: Interactive mode
python agentspec/tools/add_example.py --interactive
# Prompts: Paste the code, paste the bad doc, what's wrong?
```

**Implementation:**
```python
#!/usr/bin/env python3
"""
Advanced example parser for AgentSpec.

Lets users programmatically add examples to examples.json by:
1. Providing code + bad documentation
2. Parser extracts what's wrong
3. Generates corrected example
4. Appends to examples.json

Usage:
    # From bad output
    python add_example.py \
        --file path/to/file.py \
        --function func_name \
        --bad-output "text that was wrong" \
        --correction "what it should say"

    # Interactive mode
    python add_example.py --interactive
"""

import json
import ast
from pathlib import Path
from typing import Dict, Any
import click
from openai import OpenAI

EXAMPLES_FILE = Path(__file__).parent.parent / "prompts" / "examples.json"

class ExampleParser:
    """Parses bad documentation and creates training examples."""

    def __init__(self):
        self.client = OpenAI()

    def extract_code_context(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """Extract code, line numbers, language from file."""
        file = Path(file_path)
        content = file.read_text()

        # Detect language
        language = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript'
        }.get(file.suffix, 'unknown')

        # Extract function (simple version - can be enhanced)
        if language == 'python':
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    start = node.lineno
                    end = node.end_lineno
                    lines = content.splitlines()[start-1:end]
                    code = '\n'.join(lines)
                    return {
                        'code': code,
                        'language': language,
                        'file': str(file),
                        'lines': f'{start}-{end}'
                    }

        # Fallback: return whole file (user can edit later)
        return {
            'code': content,
            'language': language,
            'file': str(file),
            'lines': 'full file'
        }

    def analyze_bad_documentation(
        self,
        code: str,
        bad_doc: str,
        correction: str
    ) -> Dict[str, Any]:
        """Use LLM to analyze what's wrong and generate corrected example."""

        prompt = f"""Analyze this bad documentation and create a training example.

CODE:
{code}

BAD DOCUMENTATION:
{bad_doc}

USER'S CORRECTION:
{correction}

Generate a JSON object with:
1. "why_bad": Explain in 1 sentence what's wrong with the bad documentation
2. "good_what": Rewrite the 'what' section correctly (honest, brief, accurate)
3. "good_why": Write the 'why' section (2-3 sentences explaining reasoning)
4. "good_guardrails": List 2-4 guardrails for AI agents editing this code
5. "lesson": Extract the general principle (1 sentence)
6. "pattern_type": Classify the error (lie_about_validation | line_by_line_bloat | extrapolate_intent | stub_not_flagged | missing_edge_cases)

Return ONLY valid JSON, no markdown formatting.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def add_example(
        self,
        code_context: Dict[str, Any],
        bad_doc: str,
        correction: str
    ) -> None:
        """Add example to examples.json."""

        # Analyze with LLM
        analysis = self.analyze_bad_documentation(
            code_context['code'],
            bad_doc,
            correction
        )

        # Load existing examples
        examples_data = json.loads(EXAMPLES_FILE.read_text())

        # Create new example
        new_example = {
            "id": f"user_example_{len(examples_data['examples']) + 1}",
            "type": "negative_then_positive",
            "language": code_context['language'],
            "code": code_context['code'],
            "source_file": code_context['file'],
            "source_lines": code_context['lines'],
            "bad_documentation": {
                "text": bad_doc,
                "why_bad": analysis['why_bad'],
                "pattern": analysis['pattern_type']
            },
            "good_documentation": {
                "what": analysis['good_what'],
                "why": analysis['good_why'],
                "guardrails": analysis['good_guardrails']
            },
            "lesson": analysis['lesson'],
            "added_by": "user",
            "date_added": "2025-11-02"  # Would use actual date
        }

        # Append and save
        examples_data['examples'].append(new_example)
        examples_data['last_updated'] = "2025-11-02"  # Would use actual date

        EXAMPLES_FILE.write_text(json.dumps(examples_data, indent=2))

        print(f"✅ Added example to {EXAMPLES_FILE}")
        print(f"   Pattern: {analysis['pattern_type']}")
        print(f"   Lesson: {analysis['lesson']}")


@click.command()
@click.option('--file', help='Path to file containing code')
@click.option('--function', help='Function name to document')
@click.option('--bad-output', help='The bad documentation text')
@click.option('--correction', help='What it should say instead')
@click.option('--interactive', is_flag=True, help='Interactive mode')
def main(file, function, bad_output, correction, interactive):
    """Add bad documentation as a training example."""

    parser = ExampleParser()

    if interactive:
        # Interactive prompts
        print("📝 Interactive Example Creator")
        file = input("File path: ")
        function = input("Function name (or leave empty): ")
        print("Paste bad documentation (Ctrl+D when done):")
        bad_output = sys.stdin.read()
        correction = input("What should it say instead?: ")

    # Extract code
    code_context = parser.extract_code_context(file, function)

    # Add example
    parser.add_example(code_context, bad_output, correction)


if __name__ == '__main__':
    main()
```

**Key Features:**
- One command adds example to training set
- Uses LLM to analyze what's wrong
- Extracts code context automatically
- Interactive mode for quick additions
- Classifies error patterns for learning

### 5. Modified generate.py

**Key Changes:**

```python
from openai import OpenAI
import json
from pathlib import Path

def load_base_prompt() -> str:
    """Load lightweight core prompt."""
    return (Path(__file__).parent / "prompts" / "base_prompt.md").read_text()

def load_examples() -> str:
    """Load examples.json and format for prompt."""
    examples_file = Path(__file__).parent / "prompts" / "examples.json"
    examples_data = json.loads(examples_file.read_text())

    # Format examples for prompt
    formatted = "\n\n## Examples from Your Codebase\n\n"

    for ex in examples_data['examples']:
        formatted += f"### Example: {ex['id']}\n\n"
        formatted += f"**Language:** {ex['language']}\n\n"
        formatted += f"**Code:**\n```{ex['language']}\n{ex['code']}\n```\n\n"

        if ex['type'] == 'negative_then_positive':
            formatted += f"**❌ BAD Documentation:**\n{ex['bad_documentation']['text']}\n\n"
            formatted += f"**Why Bad:** {ex['bad_documentation']['why_bad']}\n\n"
            formatted += f"**✅ GOOD Documentation:**\n```yaml\nwhat: |\n  {ex['good_documentation']['what']}\n```\n\n"

        formatted += f"**Lesson:** {ex['lesson']}\n\n"
        formatted += "---\n\n"

    return formatted

def load_grammar() -> str:
    """Load CFG grammar."""
    return (Path(__file__).parent / "prompts" / "agentspec_yaml.lark").read_text()

def generate_agentspec_yaml(code: str, file_path: str) -> str:
    """Generate agentspec YAML using Responses API with CFG."""

    client = OpenAI()

    # Construct prompt
    base_prompt = load_base_prompt()
    examples = load_examples()
    full_prompt = base_prompt + "\n\n" + examples

    # Load grammar
    grammar = load_grammar()

    # Determine reasoning effort based on code complexity
    line_count = len(code.splitlines())
    reasoning_effort = "minimal" if line_count < 10 else "medium"

    # Call Responses API
    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "developer", "content": full_prompt},
            {"role": "user", "content": f"Document this code from {file_path}:\n\n```\n{code}\n```"}
        ],
        tools=[
            {
                "type": "custom",
                "name": "agentspec_yaml",
                "description": "Generate agentspec YAML block. REASON HEAVILY to ensure output obeys grammar and is honest about what code does.",
                "format": {
                    "type": "grammar",
                    "syntax": "lark",
                    "definition": grammar
                }
            }
        ],
        reasoning={"effort": reasoning_effort},
        parallel_tool_calls=False
    )

    # Extract YAML from tool call
    tool_call = response.output[1]  # First item is reasoning, second is tool call
    yaml_output = tool_call.input

    return yaml_output
```

---

## 🎯 Why This Solves Everything

### Problem 1: Documentation That Lies
**Solution**:
- Base prompt emphasizes HONESTY FIRST
- Examples show negative→positive corrections
- CFG prevents format drift
- `add_example.py` lets users fix lies and add to training set

### Problem 2: Bloated Output
**Solution**:
- Base prompt: "10 lines of code = max 10 lines of docs"
- CFG enforces max line length (200 chars)
- Minimal reasoning for simple code
- Examples show brevity

### Problem 3: No Format Enforcement
**Solution**:
- CFG grammar GUARANTEES valid YAML
- No brace escaping needed
- Structure enforced at token level

### Problem 4: Static Examples
**Solution**:
- Single examples.json (easy to update)
- Users add their code patterns
- Language-specific examples
- Living dataset that grows

### Problem 5: No Improvement Path
**Solution**:
- `add_example.py` turns bad output → training example
- One command: highlight, run tool, done
- System learns from mistakes
- Patterns classified for analysis

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)
1. ✅ Write this handoff document
2. Create `base_prompt.md` (lightweight, honesty-first)
3. Create `agentspec_yaml.lark` (CFG grammar)
4. Create `examples.json` (initial seed examples)
5. Test CFG with OpenAI Playground

### Phase 2: Core Integration (Week 2)
1. Modify `generate.py` to use Responses API
2. Implement `load_examples()`, `load_grammar()`
3. Add reasoning effort logic
4. Test with real codebases
5. Verify YAML output validity

### Phase 3: Example Parser (Week 3)
1. Create `add_example.py` tool
2. Implement code extraction
3. Implement LLM analysis
4. Add interactive mode
5. Test workflow: bad output → training example

### Phase 4: Testing & Refinement (Week 4)
1. Run on permanent test files
2. Collect bad outputs
3. Use `add_example.py` to add them
4. Iterate on base prompt
5. Measure improvement

### Phase 5: Documentation & Release
1. Update README
2. Write user guide for `add_example.py`
3. Create video demo
4. Announce new architecture

---

## 📊 Success Metrics

**Before (Current System):**
- 54 lines for 8 lines of code
- Documentation lies about validation
- Terse mode MORE verbose than regular
- No path to improvement
- Static examples

**After (New System):**
- ≤10 lines for simple code
- Honest documentation ("WARNING: Only checks key exists")
- CFG-enforced format
- Users can add examples in one command
- Living dataset grows

**Specific Targets:**
- Docs/code ratio: <2:1 for simple functions
- Honesty rate: 100% (no false claims)
- Format validity: 100% (CFG-enforced)
- User contribution: ≥1 example/week from active users

---

## 🎓 Key Lessons Learned

1. **"Be verbose" instructions create bloat** → Use CFG line limits instead
2. **LLMs extrapolate intent** → Emphasize "describe ACTUAL behavior"
3. **Static examples don't match user code** → Living dataset per codebase
4. **No feedback loop = no improvement** → `add_example.py` closes loop
5. **String formatting is fragile** → CFG handles structure at token level

---

## 🔗 References

- OpenAI Responses API: `/Users/davidmontgomery/agentspec/docs/OPENAI_PROMPT_GUIDES/gpt-5_new_params_and_tools.ipynb`
- CFG Documentation: https://github.com/guidance-ai/llguidance/blob/main/docs/syntax.md
- Lark Grammar: https://lark-parser.readthedocs.io/en/stable/

---

## ⚠️ Critical Notes for Implementation

1. **Don't make separate examples per prompt** → Single examples.json for all modes
2. **CFG syntax is strict** → Test thoroughly in playground first
3. **add_example.py must be effortless** → One command, no manual JSON editing
4. **Base prompt must be lightweight** → Examples provide bulk, prompt provides principles
5. **Reasoning effort matters** → Use "minimal" for simple code to save tokens

---

## 🤝 Handoff Checklist

For the next developer implementing this:

- [ ] Read this entire document
- [ ] Understand why current prompts fail (Pain Points section)
- [ ] Study OpenAI Responses API notebook (CFG examples)
- [ ] Review Lark grammar syntax
- [ ] Start with Phase 1 (Foundation)
- [ ] Test CFG grammar in playground BEFORE integrating
- [ ] Keep examples.json simple initially (3-5 examples)
- [ ] Build add_example.py incrementally (basic version first)
- [ ] Measure before/after metrics
- [ ] Don't skip the "why this solves everything" validation

---

**END OF HANDOFF**

This document represents a complete architectural overhaul based on:
1. Real production failures (test validation lie)
2. Token usage analysis (terse mode bloat)
3. OpenAI's latest capabilities (CFG, Responses API)
4. User feedback loops (add_example.py)

The new system is not just an incremental improvement—it's a fundamental rethinking of how AI generates code documentation.
