#!/usr/bin/env python3
"""
Auto-generate verbose agentspec docstrings using Claude.
"""
import ast
import sys
import json
import os
import re
from pathlib import Path
from typing import Dict, Any
from agentspec.utils import collect_source_files, load_env_from_dotenv
from agentspec.collect import collect_metadata
from agentspec.prompts import (
    get_verbose_docstring_prompt,
    get_terse_docstring_prompt,
    get_agentspec_yaml_prompt,
)
# Per-run generation metrics (estimated tokens and continuation counts)
GEN_METRICS: list[dict] = []

def _get_client():
    # Ensure .env is loaded so ANTHROPIC_API_KEY is present if available
    """
    ---agentspec
    what: |
      Initializes and returns a singleton Anthropic client instance. The function performs environment setup by loading variables from a .env file (if present) to ensure ANTHROPIC_API_KEY is available in the environment, then lazily imports the Anthropic class and instantiates it. The Anthropic constructor automatically reads the ANTHROPIC_API_KEY from environment variables. Returns an Anthropic client object ready for API calls.

      Inputs: None
      Outputs: anthropic.Anthropic instance configured with credentials from environment

      Edge cases:
      - If ANTHROPIC_API_KEY is not set in environment or .env file, Anthropic() will raise an authentication error
      - If .env file does not exist, load_env_from_dotenv() handles gracefully without raising
      - Lazy import means anthropic package must be installed; ImportError raised if missing
        deps:
          calls:
            - Anthropic
            - load_env_from_dotenv
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      Lazy importing the Anthropic class defers the dependency load until the client is actually needed, reducing startup time for code paths that don't use the API. Loading .env first ensures credentials are available before instantiation, supporting both explicit environment variables and .env file-based configuration. This pattern centralizes client creation logic, making it easier to manage authentication and swap implementations if needed.

    guardrails:
      - DO NOT call this function multiple times in tight loops; consider caching the result since creating new client instances is unnecessary overhead
      - DO NOT assume ANTHROPIC_API_KEY is set; always handle potential authentication errors from Anthropic() constructor
      - DO NOT modify this function to hardcode API keys; rely exclusively on environment variables for security
      - DO NOT remove the load_env_from_dotenv() call; it is essential for .env file support in development environments

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
          - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API (7baa9a8)"
        ---/agentspec
    """
    load_env_from_dotenv()
    from anthropic import Anthropic  # Imported only when needed
    return Anthropic()  # Reads ANTHROPIC_API_KEY from env

# Prompts are now loaded from separate .md files in agentspec/prompts/
# See: agentspec/prompts.py for the loading functions

def extract_function_info(filepath: Path, require_agentspec: bool = False, update_existing: bool = False) -> list[tuple[int, str, str]]:
    """
    ---agentspec
    what: |
      Extracts function definitions from a Python source file and returns metadata for functions requiring documentation. Parses the AST to identify all function and async function definitions, evaluates whether each needs an agentspec docstring based on three modes: (1) require_agentspec=True checks for missing docstrings or absence of "---agentspec" marker, (2) require_agentspec=False checks for missing or undersized docstrings (< 5 lines), (3) update_existing=True forces processing of all functions regardless of existing documentation. Returns a list of tuples containing line number, function name, and extracted source code. Results are sorted in descending line order to enable safe top-down insertion of docstrings without invalidating subsequent line numbers.
        deps:
          calls:
            - ast.get_docstring
            - ast.parse
            - ast.walk
            - existing.split
            - f.read
            - functions.append
            - functions.sort
            - isinstance
            - join
            - len
            - open
            - source.split
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      Reverse sorting by line number prevents line number drift during batch docstring insertion—when docstrings are added to functions, earlier insertions would shift line numbers of functions below them. Processing bottom-to-top preserves the validity of cached line numbers. The dual-mode checking (agentspec-specific vs. general docstring quality) allows flexible workflows: strict mode enforces agentspec compliance, while lenient mode targets underdocumented functions. The update_existing flag enables regeneration of existing documentation without re-parsing, supporting iterative refinement workflows.

    guardrails:
      - DO NOT rely on line numbers after insertion without re-parsing, as the returned list is only valid for the original source state.
      - DO NOT use this function on files with syntax errors; ast.parse() will raise SyntaxError and halt processing.
      - DO NOT assume docstring presence correlates with quality; require_agentspec=False may skip functions with minimal or placeholder docstrings.
      - DO NOT process extremely large files without memory consideration; ast.walk() traverses the entire tree and source is held in memory.
      - DO NOT mix update_existing=True with require_agentspec=True in the same call; update_existing bypasses all skip logic, making require_agentspec ineffective.

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors (bab4295)"
        ---/agentspec
    """
    with open(filepath, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # PROGRAMMATIC: update_existing flag bypasses skip logic
            if update_existing:
                needs = True  # Force processing ALL functions
            else:
                # Normal check if needs docstring
                existing = ast.get_docstring(node)
                if require_agentspec:
                    needs = (not existing) or ("---agentspec" not in existing)
                else:
                    needs = (not existing) or (len(existing.split('\n')) < 5)
            if needs:
                # Get source code
                lines = source.split('\n')
                func_lines = lines[node.lineno - 1:node.end_lineno]
                code = '\n'.join(func_lines)
                functions.append((node.lineno, node.name, code))

    # Sort by line number DESCENDING (bottom to top)
    # This way inserting docstrings doesn't invalidate later line numbers
    functions.sort(key=lambda x: x[0], reverse=True)

    return functions

def inject_deterministic_metadata(llm_output: str, metadata: Dict[str, Any], as_agentspec_yaml: bool) -> str:
    """
    ---agentspec
    what: |
      Injects deterministic metadata (dependencies and changelog) into LLM-generated documentation output. Accepts an LLM output string, a metadata dictionary containing 'deps' (with 'calls' and 'imports' keys) and 'changelog' (list of git history entries), and a format flag. When as_agentspec_yaml is True, formats metadata as YAML and injects it into an agentspec block by locating the "why:" section and inserting deps before it, then forcefully replaces any existing changelog section with deterministic data before the closing "---/agentspec" tag. When as_agentspec_yaml is False, strips any existing LLM-emitted CHANGELOG and DEPENDENCIES sections using regex boundary detection, then appends deterministic versions at the end in consistent order (deps then changelog). Returns the modified output string with deterministic metadata guaranteed to override any LLM-generated equivalents.
        deps:
          calls:
            - changelog_yaml.strip
            - deps_data.get
            - join
            - llm_output.endswith
            - metadata.get
            - output.rfind
            - re.sub
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      Deterministic metadata from code analysis and git history must always take precedence over LLM-generated content to ensure documentation accuracy and consistency. Separating concerns between LLM narrative generation (what/why/guardrails) and deterministic metadata injection prevents hallucination of dependencies or changelog entries. The dual-format approach (YAML and plain text) accommodates both structured agentspec blocks and human-readable documentation. Forceful replacement rather than conditional merging ensures metadata integrity regardless of LLM behavior or output variations.
      
      Using callable replacements (lambda functions) in re.sub calls instead of string replacements prevents Python from interpreting backslashes in injected metadata as escape sequences, avoiding "bad escape" errors when processing code containing backslash-u sequences or other escape-like patterns.

    guardrails:
      - DO NOT attempt to strip or validate LLM-generated narrative content (what/why/guardrails sections); only strip and replace metadata sections (CHANGELOG, DEPENDENCIES, deps, changelog keys) to maintain separation of concerns and preserve LLM creativity in narrative generation.
      - DO NOT conditionally inject metadata based on LLM output quality or presence of placeholder text; always forcefully overwrite deterministic sections to guarantee metadata correctness and prevent stale or hallucinated entries from persisting.
      - DO NOT merge LLM-generated and deterministic metadata lists; always replace entirely to avoid duplication and ensure single source of truth from code analysis and git history.
      - DO NOT assume agentspec block structure exists; handle both cases where "---/agentspec" is present and absent, and gracefully append metadata when closing tag is missing.
      - DO NOT use greedy regex patterns without explicit boundaries; employ non-greedy matching and lookahead assertions to prevent over-stripping adjacent sections in plain-text format.
      - ALWAYS use callable replacements (lambda) in re.sub when injecting metadata to prevent backslash interpretation errors.

        changelog:
          - "- 2025-11-01: fix(critical): use callable replacements in re.sub to prevent 'bad escape \\u' errors when processing JS/TS"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        ---/agentspec
    """
    if not metadata:
        return llm_output

    deps_data = metadata.get('deps', {})
    changelog_data = metadata.get('changelog', [])

    if as_agentspec_yaml:
        # YAML format: inject deps and changelog sections
        # Build deps section from actual metadata
        deps_yaml = "\n    deps:\n"
        if deps_data.get('calls'):
            deps_yaml += "      calls:\n"
            for call in deps_data['calls']:
                deps_yaml += f"        - {call}\n"
        if deps_data.get('imports'):
            deps_yaml += "      imports:\n"
            for imp in deps_data['imports']:
                deps_yaml += f"        - {imp}\n"

        # Build changelog section from actual git history
        changelog_yaml = "\n    changelog:\n"
        if changelog_data:
            for entry in changelog_data:
                changelog_yaml += f"      - \"{entry}\"\n"
        else:
            changelog_yaml += "      - \"No git history available\"\n"

        # Inject into LLM output
        # Strategy: Look for "why:" and inject deps before it
        # USE CALLABLE REPLACEMENT to avoid backslash interpretation in deps_yaml
        if "why:" in llm_output or "why |" in llm_output:
            # Inject deps before why
            output = re.sub(
                r'(\n\s*why[:\|])',
                lambda m: deps_yaml + m.group(1),
                llm_output,
                count=1
            )
        else:
            # Fallback: inject after what section
            output = re.sub(
                r'(\n\s*what:.*?\n(?:\s+.*\n)*)',
                lambda m: m.group(1) + deps_yaml,
                llm_output,
                count=1,
                flags=re.DOTALL
            )

        # NEVER TRY TO STRIP LLM CONTENT - this violates separation of concerns
        # The injection process must ALWAYS overwrite with deterministic metadata
        # regardless of what the LLM generates. No stripping, no conditional logic.

        # FORCEFULLY INJECT changelog - replace any existing changelog sections with deterministic ones
        # This ensures deterministic metadata ALWAYS wins, regardless of LLM behavior
        # USE CALLABLE REPLACEMENT to avoid backslash interpretation in changelog_yaml
        if "---/agentspec" in output:
            # If there's already a changelog section, replace it
            if "changelog:" in output:
                output = re.sub(
                    r'changelog:.*?(?=---/agentspec)',
                    lambda m: changelog_yaml.strip(),
                    output,
                    flags=re.DOTALL
                )
            else:
                # Inject before closing tag
                last_pos = output.rfind("---/agentspec")
                output = output[:last_pos] + changelog_yaml + "    " + output[last_pos:]
        else:
            output += changelog_yaml

        return output
    else:
        # Regular format: FORCEFULLY REPLACE any CHANGELOG sections with deterministic ones
        # NEVER strip LLM content - just overwrite it with deterministic metadata

        # FORCEFULLY REPLACE any existing CHANGELOG sections
        # Build the deterministic changelog content
        changelog_content = "CHANGELOG (from git history):\n"
        if changelog_data:
            for entry in changelog_data:
                changelog_content += f"{entry}\n"
        else:
            changelog_content += "No git history available\n"

        # Strip any existing LLM-emitted CHANGELOG section(s) entirely, then append deterministic one.
        # Robust boundary: stop at the next non-indented header (line starting at column 1) or end-of-text.
        llm_output = re.sub(
            r'(?ms)^\s*CHANGELOG \(from git history\):\s*\n.*?(?=^(?:FUNCTION CODE DIFF SUMMARY|DEPENDENCIES \(from code analysis\):|WHAT:|WHY:)|\Z)',
            '',
            llm_output,
        )

        # Also strip any existing LLM-emitted DEPENDENCIES section(s) to prevent duplication, then append ours.
        llm_output = re.sub(
            r'(?ms)^\s*DEPENDENCIES \(from code analysis\):\s*\n.*?(?=^(?:CHANGELOG \(from git history\):|FUNCTION CODE DIFF SUMMARY|WHAT:|WHY:)|\Z)',
            '',
            llm_output,
        )

        # Build deterministic deps section
        deps_text = "DEPENDENCIES (from code analysis):\n"
        if deps_data.get('calls'):
            deps_text += "Calls: " + ", ".join(deps_data['calls']) + "\n"
        if deps_data.get('imports'):
            deps_text += "Imports: " + ", ".join(deps_data['imports']) + "\n"

        # Append deterministic sections at the end in a consistent order: deps then changelog
        if not llm_output.endswith("\n"):
            llm_output += "\n"
        llm_output += "\n" + deps_text + "\n" + changelog_content

        return llm_output


def strip_js_agentspec_blocks(filepath: Path, *, dry_run: bool = False, mode: str = "all") -> int:
    """
    ---agentspec
    what: |
      Scans a JavaScript/TypeScript file and removes JSDoc comment blocks (/** ... */) that contain agentspec-related markers or metadata. The function identifies candidate blocks by searching for specific keywords: "---agentspec", "---/agentspec", "DEPENDENCIES (from code analysis):", "CHANGELOG (from git history):", and "AGENTSPEC_CONTEXT:". It processes the file line-by-line, collecting multi-line JSDoc blocks and testing each against the marker set. Matching blocks are either logged (dry_run=True) or deleted (dry_run=False). The function preserves file line-ending style and returns a count of removed blocks. Non-matching JSDoc blocks and all other content remain untouched. Malformed blocks (missing closing */) are kept as-is.
        deps:
          calls:
            - any
            - block.append
            - endswith
            - filepath.read_text
            - filepath.write_text
            - is_agentspec_block
            - join
            - len
            - out.append
            - out.extend
            - print
            - strip
            - text.endswith
            - text.splitlines
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      Agentspec metadata blocks are auto-generated and may become stale or redundant during development. This function provides a cleanup mechanism to strip embedded documentation without manual editing. The dry_run mode allows safe preview before destructive changes. Marker-based detection is resilient to formatting variations while remaining specific enough to avoid false positives on regular documentation. Line-by-line processing with explicit block collection handles multi-line JSDoc syntax correctly and preserves file structure integrity.

    guardrails:
      - DO NOT remove JSDoc blocks that do not contain any of the five agentspec markers, as they may be legitimate API documentation unrelated to agentspec.
      - DO NOT modify the file if dry_run=True; only print what would be removed to allow safe inspection before committing changes.
      - DO NOT assume well-formed JSDoc; gracefully keep malformed blocks (missing */) to avoid data loss on corrupted input.
      - DO NOT strip trailing newlines if the original file did not have them; preserve exact line-ending semantics to avoid spurious diffs.
      - DO NOT process files that cannot be read (encoding errors, permission denied); silently return 0 to allow batch operations to continue.

        changelog:
          - "- no git history available"
        ---/agentspec
    """
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0

    lines = text.splitlines()
    n = len(lines)
    i = 0
    removed = 0
    out: list[str] = []

    def is_agentspec_block(block_lines: list[str]) -> bool:
        """
        ---agentspec
        what: |
          Detects whether a list of text lines constitutes an agentspec block by checking for the presence of any marker strings that indicate agentspec content. The function joins the input lines into a single string and searches for five specific markers: the opening fence "---agentspec", the closing fence "---/agentspec", the dependency section header "DEPENDENCIES (from code analysis):", the changelog section header "CHANGELOG (from git history):", and the context marker "AGENTSPEC_CONTEXT:". Returns True if any single marker is found anywhere in the joined content, False otherwise. This is a simple substring-based detection mechanism with no positional or structural validation.
            deps:
              calls:
                - any
                - join
              imports:
                - agentspec.collect.collect_metadata
                - agentspec.utils.collect_python_files
                - agentspec.utils.collect_source_files
                - agentspec.utils.load_env_from_dotenv
                - ast
                - json
                - os
                - pathlib.Path
                - re
                - sys
                - typing.Any
                - typing.Dict


        why: |
          This function provides a lightweight heuristic for identifying agentspec blocks during parsing or filtering operations. Rather than performing full YAML validation or structural parsing, substring matching offers fast O(n) detection that works across fragmented input (lines that may not yet be reassembled). The choice of markers balances specificity—markers are unlikely to appear in unrelated documentation—with simplicity, avoiding regex or stateful parsing overhead. This approach is suitable for preprocessing steps where only presence/absence matters, not content integrity.

        guardrails:
          - DO NOT rely on this function for validation of agentspec block structure or YAML correctness; it only confirms presence of markers, not well-formedness.
          - DO NOT use this as a security boundary; markers can appear in comments or quoted strings within the block, leading to false positives.
          - DO NOT assume marker presence guarantees a complete or properly closed block; only one marker may be present (e.g., opening fence without closing).
          - DO NOT call this on extremely large line lists without considering memory impact of the join operation; for streaming scenarios, check markers incrementally instead.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        content = "\n".join(block_lines)
        markers = [
            "---agentspec",
            "---/agentspec",
            "DEPENDENCIES (from code analysis):",
            "CHANGELOG (from git history):",
            "AGENTSPEC_CONTEXT:",
        ]
        return any(m in content for m in markers)

    while i < n:
        line = lines[i]
        if "/**" in line:
            # Collect the block until '*/'
            start_idx = i
            block: list[str] = [line]
            i += 1
            found_end = False
            while i < n:
                block.append(lines[i])
                if lines[i].strip().endswith("*/"):
                    found_end = True
                    i += 1
                    break
                i += 1
            if not found_end:
                # Malformed block; keep as-is
                out.extend(block)
                continue
            # Decide deletion
            if is_agentspec_block(block):
                removed += 1
                if dry_run:
                    print(f"  ✂️  Would remove agentspec JSDoc block at lines {start_idx+1}-{start_idx+len(block)}")
                # Skip writing this block
                continue
            else:
                out.extend(block)
        else:
            out.append(line)
            i += 1

    if removed and not dry_run:
        filepath.write_text("\n".join(out) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    return removed


def generate_docstring(code: str, filepath: str, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', terse: bool = False, diff_summary: bool = False) -> str:
    """
    ---agentspec
    what: |
      Generates narrative-only docstrings (or agentspec YAML) for a function. Implements continuation for
      long YAML by detecting incomplete fences/sections and issuing follow-up calls (max 2). Provides
      per-call token budgeting with environment overrides and emits per-function proof logs. Honors
      AGENTSPEC_GENERATE_STUB=1 to force deterministic narrative for testing (no provider calls).

    guardrails:
      - DO NOT include deps/changelog here; injected in a separate phase
      - ALWAYS produce YAML-only output when as_agentspec_yaml=True (no prose outside fences)
      - ALWAYS validate YAML fences and required sections; continue generation if incomplete
    changelog:
      - "2025-11-01: Add continuation + token budgeting + proof logs + stub toggle"
      - "2025-11-02: feat(cfg): Pass grammar_lark for YAML on OpenAI path and compose system prompt from base + examples"
    ---/agentspec
    """
    import re, os

    def _estimate_tokens(s: str) -> int:
        """
        ---agentspec
        what: |
          Estimates the token count of a string using a simple character-based heuristic.

          Takes a string input and returns an integer representing an approximate token count.
          The estimation divides the string length by 4, based on the assumption that an average
          token represents approximately 4 characters of text. This is a rough approximation
          commonly used for quick token budgeting without invoking a full tokenizer.

          Returns a minimum of 1 token even for empty or very short strings, ensuring that
          any non-null input is counted as at least one token. This prevents zero-token
          estimates which could cause issues in downstream token accounting or budget checks.
        deps:
          calls:
            - len
            - max
        ---/agentspec
        """
        try:
            return max(1, len(s) // 4)
        except Exception:
            return 1

    def _yaml_complete(text: str) -> bool:
        return "---agentspec" in text and "---/agentspec" in text

    def _yaml_has_core_sections(text: str) -> bool:
        return (re.search(r"(?m)^what:\s*\|", text) is not None and
                re.search(r"(?m)^why:\s*\|", text) is not None and
                re.search(r"(?m)^guardrails:\s*$", text) is not None)

    # Build prompting content
    if as_agentspec_yaml:
        # Compose system prompt from base rules + (lightweight) examples summary
        try:
            from agentspec.prompts import load_base_prompt, load_examples_json, load_agentspec_yaml_grammar
            base_prompt_text = load_base_prompt()
            examples = load_examples_json().get("examples", [])
            # Include FULL examples (not just IDs) so LLM learns from them
            examples_text = ""
            for ex in examples[:5]:
                examples_text += f"\n<example id=\"{ex.get('id', 'unknown')}\">\n"
                examples_text += f"CODE: {ex.get('code', ex.get('code_snippet', 'N/A'))}\n"
                if 'bad_documentation' in ex:
                    examples_text += f"BAD DOC: {ex['bad_documentation'].get('what', 'N/A')}\n"
                if 'good_documentation' in ex:
                    examples_text += f"GOOD DOC: {ex['good_documentation'].get('what', 'N/A')}\n"
                    if 'guardrails' in ex['good_documentation']:
                        examples_text += f"GUARDRAILS: {', '.join(ex['good_documentation']['guardrails'][:2])}\n"
                examples_text += f"LESSON: {ex.get('lesson', 'N/A')}\n"
                examples_text += "</example>\n"
            system_text = f"{base_prompt_text}\n\n<examples>\n{examples_text}\n</examples>"
            grammar_lark = load_agentspec_yaml_grammar()
        except Exception:
            system_text = "Generate Agentspec YAML."
            grammar_lark = None
        user_content = code
    else:
        from agentspec.prompts import (
            get_verbose_docstring_prompt,
            get_terse_docstring_prompt,
        )
        prompt = get_terse_docstring_prompt() if terse else get_verbose_docstring_prompt()
        system_text = "You are a precise documentation generator. Generate ONLY narrative sections (what/why/guardrails). DO NOT generate deps or changelog sections."
        user_content = prompt.format(code=code, filepath=filepath, hard_data="(deterministic metadata will be injected by code)")
        grammar_lark = None

    # Compute token budget with env overrides
    prompt_tokens_est = _estimate_tokens(system_text + "\n\n" + user_content)
    context_cap = int(os.getenv('AGENTSPEC_CONTEXT_TOKENS', '0') or '0')
    out_base = 1500 if terse else 2000
    out_env = int(os.getenv('AGENTSPEC_MAX_OUTPUT_TOKENS', '0') or '0')
    buffer = int(os.getenv('AGENTSPEC_TOKEN_BUFFER', '500') or '500')
    max_out = out_base
    if out_env > 0:
        max_out = min(max_out, out_env)
    if context_cap > 0:
        avail = max(256, context_cap - prompt_tokens_est - buffer)
        max_out = min(max_out, avail)

    from agentspec.llm import generate_chat

    def _call_llm(user_content: str, max_tokens: int) -> str:
        # Choose GPT-5 controls when available
        try:
            code_lines = len(code.splitlines())
        except Exception:
            code_lines = 0
        effort = 'minimal' if terse or code_lines <= 12 else None
        verbosity = 'low' if terse else 'medium'

        return generate_chat(
            model=model,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0 if terse else 0.2,
            max_tokens=max_out,
            base_url=base_url,
            provider=provider,
            reasoning_effort=effort,
            verbosity=verbosity,
            grammar_lark=grammar_lark if as_agentspec_yaml else None,
        )

    # Emit proof log (pre-call)
    try:
        m = re.search(r"def\s+(\w+)", code)
        func_name = m.group(1) if m else "(unknown)"
    except Exception:
        func_name = "(unknown)"
    print(f"[PROOF] func={func_name} provider={(provider or 'auto')} model={model} prompt_tokens≈{prompt_tokens_est} max_out={max_out} as_yaml={as_agentspec_yaml}")

    # Stub path for tests
    if os.getenv('AGENTSPEC_GENERATE_STUB'):
        if as_agentspec_yaml:
            return (
                "---agentspec\n"
                "what: |\n  stub\n\n"
                "why: |\n  stub\n\n"
                "guardrails:\n  - NOTE: stub\n---/agentspec\n"
            )
        return """\nDocstring (stub).\n"""

    text = _call_llm(user_content, max_out)

    # YAML continuation if needed
    attempts = 0
    if as_agentspec_yaml and (not _yaml_complete(text) or not _yaml_has_core_sections(text)):
        continuation_prompt = (
            "Continue the YAML agentspec block you were generating.\n"
            "Do not repeat content already produced.\n"
            "Finish any missing sections and CLOSE with ---/agentspec.\n"
            "Output ONLY YAML (no prose)."
        )
        while (not _yaml_complete(text) or not _yaml_has_core_sections(text)) and attempts < 2:
            more = _call_llm(continuation_prompt, max_out)
            if more.strip().startswith('---agentspec'):
                more = more.split('---agentspec', 1)[-1]
            text = text.rstrip() + "\n" + more.strip() + "\n"
            attempts += 1

    # Record metrics
    try:
        from statistics import mean as _mean  # noqa: F401
        GEN_METRICS.append({
            'prompt_tokens': prompt_tokens_est,
            'output_tokens': _estimate_tokens(text),
            'continuations': attempts if as_agentspec_yaml else 0,
            'yaml': bool(as_agentspec_yaml),
            'provider': provider or 'auto',
        })
    except Exception:
        pass

    # Optional diff summary (no-op here to avoid heavy git ops in core path)
    if diff_summary:
        pass

    return text

def insert_docstring_at_line(filepath: Path, lineno: int, func_name: str, docstring: str, force_context: bool = False) -> bool:
    """
    ---agentspec
    what: |
      Inserts or replaces a docstring for a specified function in a Python file at a given line number.

      **Inputs:**
      - `filepath`: Path object pointing to the target Python file
      - `lineno`: Approximate line number where the function is defined (1-based)
      - `func_name`: Name of the function to document
      - `docstring`: The docstring content to insert (plain text, without delimiters)
      - `force_context`: Boolean flag to append a context print statement after the docstring

      **Outputs:**
      - Returns `True` if insertion succeeded and file was written; `False` if syntax validation failed

      **Behavior:**
      1. Reads the entire file into memory as a list of lines
      2. Locates the function definition using regex pattern matching on `func_name`, falling back to the provided `lineno` if not found
      3. Uses AST parsing to robustly identify the function node and its first statement, handling multi-line signatures, annotations, and decorators
      4. Detects and removes any existing docstring (Expr node containing a Constant or Str value) using AST line number metadata
      5. Also removes any trailing `[AGENTSPEC_CONTEXT]` print statement if present
      6. Determines appropriate indentation from the function definition line
      7. Selects delimiter (`\"""` or `'''`) based on content, preferring triple-double unless it appears in the docstring and triple-single does not
      8. Escapes conflicting delimiters within the docstring content
      9. Formats the new docstring with proper indentation and line breaks
      10. If `force_context=True`, extracts up to 3 bullet points (lines starting with `-`) and appends a print statement with escaped content
      11. Performs a compile-test on a temporary file to validate syntax before writing
      12. Writes the modified file only if compilation succeeds

      **Edge cases:**
      - Multi-line function signatures: AST parsing handles these robustly
      - Existing docstrings: Detected and deleted using AST node boundaries (1-based to 0-based index conversion)
      - Docstring content containing delimiters: Escaped or delimiter switched to avoid breakage
      - AST parsing failure: Falls back to textual scanning using parenthesis depth tracking and colon detection
      - Syntax errors in candidate: Rejected with warning; original file left untouched
      - Empty or missing function body: Inserts after function definition line
        deps:
          calls:
            - abs
            - ast.parse
            - ast.walk
            - candidate.insert
            - candidates.append
            - docstring.split
            - enumerate
            - f.readlines
            - f.writelines
            - func_line.lstrip
            - hasattr
            - isinstance
            - join
            - len
            - line.count
            - line.startswith
            - line.strip
            - list
            - max
            - min
            - new_lines.append
            - open
            - os.close
            - os.remove
            - path.exists
            - pattern.match
            - print
            - print_content.replace
            - py_compile.compile
            - re.compile
            - re.escape
            - replace
            - reversed
            - safe_doc.replace
            - safe_doc.split
            - sections.append
            - strip
            - tempfile.mkstemp
            - tf.writelines
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      AST-based approach provides robustness against complex Python syntax (decorators, type hints, multi-line signatures) that regex or simple textual scanning cannot reliably handle. The 1-based to 0-based index conversion is critical because Python's `ast` module reports line numbers as 1-based (matching editor conventions) while Python lists are 0-indexed.

      Compile-testing before write prevents leaving the file in a broken state due to escaping errors or malformed docstring formatting. Fallback to textual scanning ensures graceful degradation if AST parsing encounters unsupported syntax or edge cases.

      Delimiter selection logic avoids breaking docstrings that contain triple quotes. Context print extraction and escaping supports downstream tooling that parses `[AGENTSPEC_CONTEXT]` markers while preventing quote/backslash injection attacks.

    guardrails:
      - DO NOT assume AST line numbers are 0-based; they are always 1-based per Python spec. Failure to convert causes off-by-one deletion of wrong lines.
      - DO NOT write to the file without first validating syntax via `py_compile`; this prevents corrupting the source file if docstring formatting is malformed.
      - DO NOT skip escaping triple quotes in docstring content; unescaped delimiters will break the syntax of the inserted docstring.
      - DO NOT assume the function definition is always on a single line; use AST to find the actual first statement in the function body, not just `lineno + 1`.
      - DO NOT leave temporary files behind; always clean up in a `finally` block to avoid disk space leaks.
      - DO NOT assume existing docstrings are always single-line; use AST `end_lineno` to correctly identify multi-line docstring boundaries.

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
        ---/agentspec
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find the function definition line more robustly using the function name,
    # falling back to the provided line number if not found.
    import re
    pattern = re.compile(rf"^\s*def\s+{re.escape(func_name)}\s*\(")
    func_line_idx = None
    for i, l in enumerate(lines):
        if pattern.match(l):
            func_line_idx = i
            break
    if func_line_idx is None:
        func_line_idx = max(0, lineno - 1)

    # Prefer AST to locate the first statement in the function body and place
    # the docstring immediately before it. This is robust to multi-line
    # signatures, annotations, and decorators.
    insert_idx = func_line_idx + 1
    target = None

    try:
        import ast
        src = ''.join(lines)
        tree = ast.parse(src)
        candidates = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                candidates.append(node)
        # Choose the closest by lineno to the provided lineno if multiple
        if candidates:
            target = min(candidates, key=lambda n: abs((n.lineno or 0) - lineno))

        # ROBUST: Check for and delete existing docstring using AST
        if target and target.body:
            first_stmt = target.body[0]
            # Check if first statement is a docstring (Expr node with Constant/Str)
            is_docstring = False
            docstring_end_line = None

            if isinstance(first_stmt, ast.Expr):
                if isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                    is_docstring = True
                    docstring_end_line = first_stmt.end_lineno
                elif hasattr(ast, 'Str') and isinstance(first_stmt.value, ast.Str):  # Python 3.7 compat
                    is_docstring = True
                    docstring_end_line = first_stmt.end_lineno

            if is_docstring and docstring_end_line:
                # Delete from docstring start to docstring end
                # CRITICAL INDEX MATH:
                # - AST line numbers are 1-based (line 1 = first line of file)
                # - Array indices are 0-based (lines[0] = first line of file)
                # - target.lineno = 1-based line number of "def"
                # - target.body[0].lineno = 1-based line number of first statement (docstring)
                # - target.body[0].end_lineno = 1-based line number of last line of docstring
                # Example: def at line 389, docstring """ at line 394, docstring closes at line 437
                # - func_line_idx = 388 (0-based index for line 389)
                # - first_stmt.lineno = 394 (1-based)
                # - first_stmt.end_lineno = 437 (1-based)
                # To delete docstring: del lines[393:437] (0-based start, exclusive end)
                docstring_start_line = first_stmt.lineno  # 1-based
                delete_start_idx = docstring_start_line - 1  # Convert to 0-based
                delete_end_idx = docstring_end_line  # 1-based works as exclusive end for slice

                # Also check for and delete any [AGENTSPEC_CONTEXT] print after docstring
                if delete_end_idx < len(lines) and '[AGENTSPEC_CONTEXT]' in lines[delete_end_idx]:
                    delete_end_idx += 1

                # Delete the old docstring (and optional context print)
                del lines[delete_start_idx:delete_end_idx]

                # Insert point is now where the docstring was
                insert_idx = delete_start_idx
            else:
                # No existing docstring, insert before first statement
                insert_idx = (first_stmt.lineno or (func_line_idx + 1)) - 1

    except Exception as e:
        # Fallback to textual scan if AST fails
        depth = 0
        idx = func_line_idx
        while idx < len(lines):
            line_text = lines[idx]
            for ch in line_text:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth = max(0, depth - 1)
            if ':' in line_text and depth == 0:
                insert_idx = idx + 1
                break
            idx += 1

        # Fallback string-based docstring deletion
        if insert_idx < len(lines):
            line = lines[insert_idx].strip()
            if line.startswith('"""') or line.startswith("'''"):
                quote_type = '"""' if '"""' in line else "'''"
                # Skip existing docstring
                if line.count(quote_type) >= 2:
                    # Single-line docstring
                    insert_idx += 1
                else:
                    # Multi-line docstring - find end
                    insert_idx += 1
                    while insert_idx < len(lines):
                        if quote_type in lines[insert_idx]:
                            insert_idx += 1
                            break
                        insert_idx += 1

                # Also skip any existing context print
                if insert_idx < len(lines) and '[AGENTSPEC_CONTEXT]' in lines[insert_idx]:
                    insert_idx += 1

                # Delete the old docstring and print
                del lines[func_line_idx + 1:insert_idx]
                insert_idx = func_line_idx + 1

    # Determine indentation
    func_line = lines[func_line_idx]
    base_indent = len(func_line) - len(func_line.lstrip())
    indent = ' ' * (base_indent + 4)  # Function body indent

    # Choose a delimiter that won't be broken by the content.
    # Prefer triple-double; if it appears in content and triple-single does not, switch.
    # If both appear, escape occurrences inside the content.
    prefer_double = True
    contains_triple_double = '"""' in docstring
    contains_triple_single = "'''" in docstring
    if contains_triple_double and not contains_triple_single:
        delim = "'''"
    else:
        delim = '"""'

    safe_doc = docstring
    if delim == '"""' and contains_triple_double:
        safe_doc = safe_doc.replace('"""', '\\"""')
    if delim == "'''" and contains_triple_single:
        safe_doc = safe_doc.replace("'''", "\\'''")

    # Format new docstring
    new_lines = []
    new_lines.append(f'{indent}{delim}\n')
    for line in safe_doc.split('\n'):
        if line.strip():
            new_lines.append(f'{indent}{line}\n')
        else:
            new_lines.append('\n')
    new_lines.append(f'{indent}{delim}\n')

    # Add context print if requested
    if force_context:
        # Extract key bullet points
        sections: list[str] = []
        for line in docstring.split('\n'):
            line = line.strip()
            if line.startswith('-') and len(sections) < 3:
                sections.append(line[1:].strip())

        # Properly escape the content for the print statement
        print_content = ' | '.join(sections)
        # Escape quotes and backslashes
        print_content = print_content.replace('\\', '\\\\').replace('"', '\\"')

        new_lines.append(f'{indent}print(f"[AGENTSPEC_CONTEXT] {func_name}: {print_content}")\n')

    # Prepare a candidate copy with the insertion applied
    candidate = list(lines)
    for line in reversed(new_lines):
        candidate.insert(insert_idx, line)

    # If requested, also add the context print after the docstring
    # (Handled above when building new_lines)

    # Compile‑test the candidate to avoid leaving broken files
    import tempfile, py_compile, os
    tmp = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.py')
        tmp = tmp_path
        os.close(tmp_fd)
        with open(tmp_path, 'w', encoding='utf-8') as tf:
            tf.writelines(candidate)
        py_compile.compile(tmp_path, doraise=True)
    except Exception as e:
        print(f"⚠️  Syntax check failed inserting docstring for {func_name} in {filepath}: {e}. Skipping this function.")
        try:
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        return False
    finally:
        try:
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    # Write back only after successful compile test
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(candidate)
    return True


# --- Minimal JS/TS support (discovery + insertion via adapter) ---
JS_EXTS = {".js", ".mjs", ".jsx", ".ts", ".tsx"}


def _discover_js_functions(
    filepath: Path, *, require_agentspec: bool = False, update_existing: bool = False
) -> list[tuple[int, str, str]]:
    """
    ---agentspec
    what: |
      Discovers JavaScript functions in a file that require agentspec documentation.

      Scans a JavaScript file line-by-line to identify function declarations (both traditional `function name()` and arrow function assignments `const name = () =>`), including those with `export` modifiers. For each discovered function, examines up to 20 lines above to detect existing JSDoc blocks and checks for the presence of an agentspec marker (`---agentspec`).

      Returns a list of tuples containing (line_number, function_name, code_snippet) sorted in reverse line order. Each tuple represents a function candidate that either lacks documentation entirely, lacks an agentspec block when required, or is flagged for update. The code snippet captures the function declaration plus approximately 8 subsequent lines for context.

      Handles file read errors gracefully by returning an empty list. Regex patterns match standard JavaScript function naming conventions (alphanumeric, underscore, dollar sign).

      Input parameters control filtering behavior: `require_agentspec=True` identifies functions with JSDoc but missing agentspec markers; `update_existing=True` includes all discovered functions regardless of documentation state.
        deps:
          calls:
            - arrow_pat.match
            - candidates.append
            - candidates.sort
            - enumerate
            - filepath.read_text
            - func_pat.match
            - has_jsdoc
            - join
            - len
            - m1.group
            - m2.group
            - max
            - min
            - range
            - re.compile
            - s.endswith
            - strip
            - text.splitlines
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      This discovery mechanism enables automated or semi-automated generation of agentspec documentation blocks for JavaScript codebases. By identifying undocumented or partially documented functions, it supports tooling that can prompt developers or generate templates for specification. Reverse sorting by line number allows downstream processors to insert documentation without invalidating earlier line references. The configurable filtering logic accommodates different workflows: initial documentation generation, targeted agentspec addition to existing JSDoc, or bulk updates.

    guardrails:
      - DO NOT assume file encoding beyond UTF-8 with error ignoring; malformed files should fail silently and return empty results to prevent pipeline breakage.
      - DO NOT match function names in comments or strings; regex patterns are line-anchored to reduce false positives, but multi-line string literals or commented-out code may still be detected.
      - DO NOT look beyond 20 lines above for JSDoc markers; this bounds search cost and assumes JSDoc is reasonably proximate to function declarations.
      - DO NOT include functions that already have complete agentspec documentation when `update_existing=False` and `require_agentspec=False`; this prevents redundant processing.
      - DO NOT return candidates in original line order; reverse sorting is essential to prevent line number shifts when inserting documentation blocks sequentially.

        changelog:
          - "- no git history available"
        ---/agentspec
    """
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    lines = text.splitlines()
    candidates: list[tuple[int, str, str]] = []

    # Patterns: function name(, export function name(, const name = (...) =>
    func_pat = re.compile(r"^\s*(?:export\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")
    arrow_pat = re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=.*=>")

    def has_jsdoc(idx: int) -> tuple[bool, bool]:
        """
        ---agentspec
        what: |
          Scans up to 20 lines above a given line index to detect JSDoc comment blocks and identify whether they contain an agentspec marker. Returns a tuple of two booleans: (has_any_jsdoc, has_agentspec_marker). The function searches backward from the target line, looking for the closing */ of a JSDoc block, then locates the opening /** to determine if the complete block contains the "---agentspec" marker string. If no JSDoc block is found within the 20-line window, returns (False, False). If a JSDoc block is found but lacks the marker, returns (True, False). If both are present, returns (True, True).
            deps:
              calls:
                - join
                - max
                - range
                - s.endswith
                - strip
              imports:
                - agentspec.collect.collect_metadata
                - agentspec.utils.collect_python_files
                - agentspec.utils.collect_source_files
                - agentspec.utils.load_env_from_dotenv
                - ast
                - json
                - os
                - pathlib.Path
                - re
                - sys
                - typing.Any
                - typing.Dict

        why: |
          This function enables detection of pre-existing agentspec documentation blocks in JavaScript/TypeScript source files, supporting incremental documentation workflows where some functions may already be documented. The 20-line lookback window balances thoroughness against performance, capturing typical comment blocks while avoiding excessive backward scanning. The two-part return tuple allows callers to distinguish between "no JSDoc found" and "JSDoc found but no agentspec marker," enabling different handling strategies (e.g., skip vs. update).
        guardrails:
          - DO NOT assume lines are already stripped; the function explicitly calls .strip() to handle leading/trailing whitespace robustly.
          - DO NOT search beyond 20 lines backward; this prevents performance degradation on large files and focuses on proximate documentation.
          - DO NOT return True for has_any_jsdoc if only */ is found without a corresponding /**; the function requires both markers to confirm a valid JSDoc block.
          - DO NOT treat "---agentspec" as case-sensitive; the marker check uses exact string matching, so variations in casing will not be detected.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        # Look up to 20 lines above for */ and /**
        start = max(0, idx - 20)
        saw_end = False
        has_marker = False
        for i in range(idx - 1, start - 1, -1):
            s = lines[i].strip()
            if not saw_end and s.endswith("*/"):
                saw_end = True
                continue
            if saw_end:
                if "/**" in s:
                    block = "\n".join(lines[i:idx])
                    has_marker = "---agentspec" in block
                    return True, has_marker
        return False, False

    for idx, ln in enumerate(lines, start=1):
        m1 = func_pat.match(ln)
        m2 = arrow_pat.match(ln)
        name = m1.group(1) if m1 else (m2.group(1) if m2 else None)
        if not name:
            continue

        has_any, has_marker = has_jsdoc(idx)
        if update_existing:
            needs = True
        else:
            needs = (not has_any) if not require_agentspec else ((not has_any) or (has_any and not has_marker))

        if not needs:
            continue

        # Capture a small code snippet: current line + next ~8 lines
        snippet = "\n".join(lines[idx - 1 : min(len(lines), idx + 8)])
        candidates.append((idx, name, snippet))

    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates


def process_js_file(
    filepath: Path,
    dry_run: bool = False,
    force_context: bool = False,
    model: str = "claude-haiku-4-5",
    as_agentspec_yaml: bool = False,
    base_url: str | None = None,
    provider: str | None = "auto",
    update_existing: bool = False,
    terse: bool = False,
    diff_summary: bool = False,
) -> None:
    """
    ---agentspec
    what: |
      Processes a JavaScript file to discover functions and generate embedded agentspec documentation.

      Behavior additions:
      - When update_existing=True, pre-cleans existing agentspec JSDoc blocks (YAML or narrative) to prevent duplicates.
    ---/agentspec
    """
    # Pre-clean to ensure idempotency when updating
    if update_existing and not dry_run:
        try:
            removed = strip_js_agentspec_blocks(filepath)
            if removed:
                print(f"  🧹 Removed {removed} existing agentspec JSDoc block(s)")
        except Exception:
            pass

    try:
        functions = _discover_js_functions(
            filepath,
            require_agentspec=as_agentspec_yaml,
            update_existing=update_existing,
        )
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return

    if not functions:
        print(f"  Found 0 candidates in {filepath}")
        return

    print(f"  Found {len(functions)} candidate(s) in {filepath}")

    if dry_run:
        for lineno, func_name, _ in functions:
            print(f"    [DRY-RUN] Would generate doc for {func_name} @ {filepath}:{lineno}")
        return

    from agentspec.insert_metadata import apply_docstring_with_metadata

    for lineno, func_name, code in functions:
        try:
            narrative = generate_docstring(
                code=code,
                filepath=str(filepath),
                model=model,
                as_agentspec_yaml=as_agentspec_yaml,
                base_url=base_url,
                provider=provider,
                terse=terse,
                diff_summary=diff_summary,
            )

            # Collect deterministic metadata privately
            try:
                from agentspec.collect import collect_metadata
                meta = collect_metadata(filepath, func_name) or {}
            except Exception:
                meta = {}

            ok = apply_docstring_with_metadata(
                filepath,
                lineno,
                func_name,
                narrative,
                meta,
                as_agentspec_yaml=as_agentspec_yaml,
                force_context=force_context,
            )
            if ok:
                print(f"    ✅ Added verified JSDoc with deterministic metadata to {func_name}")
            else:
                print(f"    ⚠️ Skipped inserting docstring for {func_name} (validation failed)")
        except Exception as e:
            print(f"    ❌ Error processing {func_name}: {e}")

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', update_existing: bool = False, terse: bool = False, diff_summary: bool = False):
    """
    ---agentspec
    what: |
      Orchestrates end-to-end docstring generation for a single Python file by extracting all functions requiring documentation, generating AI-powered narratives via LLM, collecting deterministic metadata (deps, imports, changelog) separately, and applying both through a two-phase insertion process with compile-safety verification.

      **Inputs:**
      - filepath (Path): Target Python file to process
      - dry_run (bool): Preview mode; prints plan without writing changes
      - force_context (bool): Injects print() statements for agent observability
      - model (str): LLM model identifier (default: "claude-haiku-4-5")
      - as_agentspec_yaml (bool): Generate structured agentspec YAML instead of traditional docstrings
      - base_url (str | None): Custom LLM provider endpoint
      - provider (str | None): LLM provider selection ('auto' for automatic detection)
      - update_existing (bool): Force regeneration of existing docstrings
      - terse (bool): Generate concise documentation
      - diff_summary (bool): Include diff summaries in changelog

      **Processing Flow:**
      1. Extracts all functions lacking verbose docstrings or marked for update via extract_function_info
      2. Returns early if no functions need processing or if dry_run=True after printing the plan
      3. Sorts functions in reverse line-number order (bottom-to-top) to prevent line-shift invalidation during insertion
      4. For each function: generates LLM narrative, collects deterministic metadata independently, applies both via compile-safe insertion
      5. Handles syntax errors gracefully by catching and reporting without crashing
      6. Prints detailed progress including function names, line numbers, model selection, and success/failure status

      **Outputs:**
      - None (side effects: modified filepath with inserted docstrings, console output with progress)
      - Early returns on: syntax errors, no functions found, dry_run=True
      - Graceful degradation: metadata collection failures do not block docstring insertion

      **Edge Cases:**
      - Syntax errors in target file are caught and reported; processing halts without exception
      - Metadata collection failures (missing markers, import errors, format issues) fall back to empty dict
      - Compile-safety verification may skip insertion if docstring would break syntax; reported as warning
      - Multiple LLM providers/models with configurable endpoints; invalid model/provider combinations fail at LLM call time
      - Bottom-to-top processing ensures line numbers remain valid throughout loop without recalculation
        deps:
          calls:
            - apply_docstring_with_metadata
            - collect_metadata
            - extract_function_info
            - functions.sort
            - generate_docstring
            - len
            - print
            - str
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      **Bottom-to-top processing (reverse sort by line number)** is essential because inserting docstrings shifts all subsequent line numbers downward; processing in reverse order ensures line numbers remain valid throughout the loop without recalculation. Ascending order would cause line-number invalidation and insertion failures.

      **Two-phase generation (narrative from LLM, metadata collected separately)** maintains clean separation of concerns: the LLM generates human-readable documentation without knowledge of internal implementation details (deps, imports, changelog), while deterministic metadata is collected from the codebase independently and merged only at insertion time. This prevents LLM hallucination of technical details and keeps the LLM focused on narrative quality.

      **Metadata collection wrapped in try-except with fallback to empty dict** ensures metadata extraction failures (missing agentspec markers, import errors, file format issues) never block docstring insertion. Graceful degradation allows partial success rather than total failure.

      **Compile-safety verification via apply_docstring_with_metadata** prevents insertion of syntactically invalid docstrings that would break the file. The function returns a boolean indicating success, allowing the caller to report skips without raising exceptions.

      **Dry-run mode** allows users to preview which functions will be processed and with which model before committing any changes, reducing risk of unintended modifications.

      **Support for as_agentspec_yaml flag** enables generation of structured agent specifications instead of traditional docstrings, allowing the same pipeline to serve different documentation formats without code duplication.

      **Early return conditions** (no functions found, dry_run=True) are intentional gates that prevent unnecessary LLM calls or file writes, improving efficiency and reducing API costs.

    guardrails:
      - DO NOT modify the bottom-to-top sort order (reverse=True on line number); changing to ascending order will cause line-number invalidation and docstring insertion failures
      - DO NOT remove the try-except wrapper around collect_metadata or the fallback to empty dict; metadata collection failures must not block docstring generation
      - DO NOT pass metadata to generate_docstring; the LLM must only receive code and filepath, never implementation details like deps or changelog
      - DO NOT skip the compile-safety check via apply_docstring_with_metadata; always use this function for insertion rather than direct file manipulation
      - DO NOT attempt to process files with syntax errors; catch SyntaxError from extract_function_info and return early without attempting further processing
      - DO NOT pass string paths to extract_function_info or apply_docstring_with_metadata; filepath must be a Path object for compatibility
      - DO NOT assume model/provider combinations are valid; invalid selections will fail at LLM call time with authentication/availability errors
      - ALWAYS preserve the two-phase generation pattern: narrative first (LLM), then metadata insertion (deterministic)
      - ALWAYS call extract_function_info with require_agentspec and update_existing parameters matching the function's own flags
      - ALWAYS print progress messages at key stages (extraction, generation start, success/failure) for agent observability and user feedback

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        ---/agentspec
    """
    print(f"\n📄 Processing {filepath}")

    try:
        functions = extract_function_info(filepath, require_agentspec=as_agentspec_yaml, update_existing=update_existing)
    except SyntaxError as e:
        print(f"  ❌ Syntax error in file: {e}")
        return

    if not functions:
        if update_existing:
            print("  ℹ️  No functions found to update")
        else:
            print("  ✅ All functions already have verbose docstrings")
        return

    print(f"  Found {len(functions)} functions needing docstrings:")
    for lineno, name, _ in functions:
        print(f"    - {name} (line {lineno})")

    if force_context:
        print("  🔊 Context-forcing print() statements will be added")

    print(f"  🤖 Using model: {model}")

    if dry_run:
        return

    # Ensure bottom-to-top processing to avoid line shifts
    functions.sort(key=lambda x: x[0], reverse=True)
    # Two‑phase write: narrative first (LLM), then deterministic metadata via insert_metadata.apply_docstring_with_metadata
    for lineno, name, code in functions:
        print(f"\n  🤖 Generating {'agentspec YAML' if as_agentspec_yaml else 'docstring'} for {name}...")
        try:
            narrative = generate_docstring(code, str(filepath), model=model, as_agentspec_yaml=as_agentspec_yaml, base_url=base_url, provider=provider, terse=terse, diff_summary=diff_summary)
            # Collect metadata privately, never passed to LLM
            try:
                from agentspec.collect import collect_metadata
                meta = collect_metadata(filepath, name) or {}
            except Exception:
                meta = {}
            from agentspec.insert_metadata import apply_docstring_with_metadata
            ok = apply_docstring_with_metadata(
                filepath,
                lineno,
                name,
                narrative,
                meta,
                as_agentspec_yaml=as_agentspec_yaml,
                force_context=force_context,
            )
            if ok:
                print(f"  ✅ Added verified docstring with deterministic metadata to {name}")
            else:
                print(f"  ⚠️ Skipped inserting docstring for {name} (compile safety)")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, language: str = "auto", dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, provider: str | None = 'auto', base_url: str | None = None, update_existing: bool = False, terse: bool = False, diff_summary: bool = False) -> int:
    """
    ---agentspec
    what: |
      Orchestrates generation across Python and JS/TS with per-run metrics and proof logs.

      Behavior:
      - Loads .env and resolves provider/base_url
      - Discovers files via collect_source_files and filters by --language
      - Clears per-run token metrics before processing, prints summary afterward
      - Delegates per-file processing (process_file for Python, process_js_file for JS/TS)

    guardrails:
      - DO NOT perform file edits in dry_run
      - ALWAYS handle invalid target path
      - ALWAYS print per-run metrics summary when any functions were processed
    changelog:
      - "2025-11-01: Add per-run metrics summary"
    ---/agentspec
    """
    # Load .env and decide provider
    load_env_from_dotenv()
    prov = (provider or 'auto').lower()
    is_claude_model = (model or '').lower().startswith('claude')
    if prov == 'auto':
        prov = 'anthropic' if is_claude_model else 'openai'
    if prov == 'anthropic':
        if not os.getenv('ANTHROPIC_API_KEY') and not dry_run:
            print("❌ Error: ANTHROPIC_API_KEY environment variable not set for Claude models")
            print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
            return 1
    else:
        if base_url is None:
            base_url = os.getenv('OPENAI_BASE_URL') or os.getenv('AGENTSPEC_OPENAI_BASE_URL') or os.getenv('OLLAMA_BASE_URL')
        if not os.getenv('OPENAI_API_KEY') and not base_url:
            base_url = 'http://localhost:11434/v1'

    path = Path(target)
    if not path.exists():
        print(f"❌ Error: Path does not exist: {target}")
        return 1

    if dry_run:
        print("🔍 DRY RUN MODE - no files will be modified\n")
    if update_existing:
        print("🔄 UPDATE MODE - Regenerating existing docstrings\n")

    # Discover
    all_files = collect_source_files(path)
    js_exts = {".js", ".mjs", ".jsx", ".ts", ".tsx"}
    if language not in {"auto", "py", "js"}:
        language = "auto"
    if language == "py":
        files = [p for p in all_files if p.suffix.lower() == ".py"]
    elif language == "js":
        files = [p for p in all_files if p.suffix.lower() in js_exts]
    else:
        files = [p for p in all_files if p.suffix.lower() in {".py", *js_exts}]

    if not files:
        print("No files found to process.")
        return 0

    print(f"Found {len(files)} file(s)")

    # Clear per-run metrics
    try:
        GEN_METRICS.clear()
    except Exception:
        pass

    for fpath in files:
        try:
            print(f"Processing {fpath}")
            ext = fpath.suffix.lower()
            if ext == ".py":
                process_file(
                    fpath,
                    dry_run=dry_run,
                    force_context=force_context,
                    model=model,
                    as_agentspec_yaml=as_agentspec_yaml,
                    base_url=base_url,
                    provider=prov,
                    update_existing=update_existing,
                    terse=terse,
                    diff_summary=diff_summary,
                )
            elif ext in js_exts:
                process_js_file(
                    fpath,
                    dry_run=dry_run,
                    force_context=force_context,
                    model=model,
                    as_agentspec_yaml=as_agentspec_yaml,
                    base_url=base_url,
                    provider=prov,
                    update_existing=update_existing,
                    terse=terse,
                    diff_summary=diff_summary,
                )
            else:
                print(f"Skipping unsupported file type: {fpath}")
        except Exception as e:
            print(f"❌ Error processing {fpath}: {e}")

    # Per-run metrics summary
    try:
        if GEN_METRICS:
            pts = [m.get('prompt_tokens', 0) for m in GEN_METRICS]
            ots = [m.get('output_tokens', 0) for m in GEN_METRICS]
            cont = sum(m.get('continuations', 0) for m in GEN_METRICS)
            import statistics as _stats
            def _fmt_stats(vals):
                """
                ---agentspec
                what: |
                  Formats a sequence of numeric values into a human-readable statistics string.

                  Takes a list or iterable of numeric values and returns a formatted string containing
                  three aggregate statistics: minimum value, mean (average) value rounded to nearest integer,
                  and maximum value. The output format is "min=X avg=Y max=Z" where X and Z are the raw
                  min/max values and Y is the integer-truncated mean.

                  Inputs:
                    - vals: iterable of numeric values (list, tuple, generator, etc.)

                  Outputs:
                    - str: formatted statistics string in pattern "min={min} avg={int_mean} max={max}"

                  Edge cases:
                    - Empty sequence: will raise ValueError from min()/max() built-ins
                    - Single value: min, max, and avg will all be identical
                    - Non-numeric values: will raise TypeError during min/max/mean operations
                    - Mean truncation: uses int() which floors toward zero (not round-to-nearest)
                    deps:
                      calls:
                        - _stats.mean
                        - int
                        - max
                        - min
                      imports:
                        - agentspec.collect.collect_metadata
                        - agentspec.prompts.get_agentspec_yaml_prompt
                        - agentspec.prompts.get_terse_docstring_prompt
                        - agentspec.prompts.get_verbose_docstring_prompt
                        - agentspec.utils.collect_source_files
                        - agentspec.utils.load_env_from_dotenv
                        - ast
                        - json
                        - os
                        - pathlib.Path
                        - re
                        - sys
                        - typing.Any
                        - typing.Dict


                why: |
                  This utility function provides a compact, human-readable summary of numeric distributions
                  for logging and debugging purposes. The choice to use int() for mean truncation rather than
                  rounding reduces visual noise in logs while remaining deterministic. Delegating to built-in
                  min/max and stats.mean() ensures correctness and leverages optimized implementations rather
                  than custom aggregation logic.

                guardrails:
                  - DO NOT pass empty sequences without pre-validation, as min()/max() will raise ValueError
                  - DO NOT rely on this for statistical precision; int() truncates rather than rounds, suitable only for display
                  - DO NOT use with non-numeric iterables; type errors will propagate without graceful handling
                  - DO NOT assume vals is consumed only once; if vals is a generator, subsequent calls will be empty

                    changelog:
                      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
                      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
                      - "- 2025-10-30: docs: remove critical mode; update CLI + README/Quickref with high-accuracy guidance (avoid --terse, pick stronger model) (f5bb2a3)"
                      - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
                      - "- 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)"
                    ---/agentspec
                """
                return f"min={min(vals)} avg={int(_stats.mean(vals))} max={max(vals)}"
            print("\n[SUMMARY]")
            print(f" items={len(GEN_METRICS)}")
            print(f" prompt_tokens≈ {_fmt_stats(pts)}")
            print(f" output_tokens≈ {_fmt_stats(ots)}")
            print(f" continuations_used={cont}")
    except Exception:
        pass

    print("\n✅ Done!")
    return 0

def main():
    """
    ---agentspec
    what: |
      Entry point for the documentation generation CLI that parses command-line arguments and delegates processing to the core run() function.

      Parses the following arguments:
      - Positional argument (required): file or directory path to process
      - --dry-run flag (optional): boolean presence check; enables preview mode without file modifications
      - --force-context flag (optional): boolean presence check; injects print() statements to force LLM context loading
      - --model flag (optional): accepts a model name string; defaults to "claude-haiku-4-5" if not specified

      Validates that at least one positional argument is provided; prints usage instructions and exits with code 1 if missing. Extracts the model name by locating the --model flag in sys.argv and reading the next argument if present; silently retains default if --model is the final argument or missing.

      Delegates actual processing to run() with parameters: path, language="auto", dry_run boolean, force_context boolean, and model string. Propagates the exit code returned by run() back to the system via sys.exit(), allowing callers to detect success (0) or failure (non-zero).

      Supported model options documented in usage string: claude-haiku-4-5 (default), claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022. Requires ANTHROPIC_API_KEY environment variable to be set before execution.
        deps:
          calls:
            - argv.index
            - len
            - print
            - run
            - sys.exit
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
            - agentspec.utils.collect_source_files
            - agentspec.utils.load_env_from_dotenv
            - ast
            - json
            - os
            - pathlib.Path
            - re
            - sys
            - typing.Any
            - typing.Dict


    why: |
      Manual argument parsing (rather than argparse) minimizes dependencies and suits a small CLI with few options, allowing simple inline flag detection without external libraries.

      Default model is claude-haiku-4-5 (cost-effective) to balance performance and API costs for typical documentation generation tasks. The --model flag is positioned after the path argument to maintain intuitive CLI ordering (target first, then options).

      Dry-run and force-context flags use simple boolean presence checks (no values required) to reduce parsing complexity and improve usability. Early validation and usage printing ensures users understand environment requirements before attempting to run.

      Delegating to run() keeps main() thin and testable, separating CLI concerns from business logic. Propagating exit codes unchanged preserves the caller's ability to detect success/failure in shell scripts and automation.

    guardrails:
      - DO NOT modify the sys.exit(1) call for missing arguments; it ensures proper shell exit codes for scripting and automation
      - DO NOT change the default model without updating documentation and considering API cost implications for end users
      - DO NOT add new positional arguments without updating the usage string to remain synchronized
      - DO NOT remove or rename the --dry-run, --force-context, or --model flags; they are part of the public CLI contract
      - DO NOT alter the usage string without ensuring it accurately reflects all supported flags and options
      - DO NOT suppress or modify the exit code from run(); callers depend on it to detect success/failure
      - ALWAYS ensure the usage string remains synchronized with actual supported flags and their descriptions
      - ALWAYS preserve exact flag names as they are part of the public CLI contract
      - NOTE: sys.argv indexing assumes well-formed input; if --model is the last argument with no value following it, model silently remains at default (this is safe but may confuse users)
      - NOTE: The model parameter is passed as a string directly to run(); ensure run() validates or handles unknown model names gracefully to provide clear error messages

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors (bab4295)"
        ---/agentspec
    """
    if len(sys.argv) < 2:
        print("Usage: python generate.py <file_or_dir> [--dry-run] [--force-context] [--model MODEL]")
        print("\nRequires ANTHROPIC_API_KEY environment variable")
        print("\nOptions:")
        print("  --dry-run           Preview without modifying files")
        print("  --force-context     Add print() statements to force LLMs to load context")
        print("  --model MODEL       Claude model to use (default: claude-haiku-4-5)")
        print("                      Options: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022")
        sys.exit(1)

    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    force_context = '--force-context' in sys.argv

    # Parse model flag
    model = "claude-haiku-4-5"
    if '--model' in sys.argv:
        model_index = sys.argv.index('--model')
        if model_index + 1 < len(sys.argv):
            model = sys.argv[model_index + 1]

    exit_code = run(path, language="auto", dry_run=dry_run, force_context=force_context, model=model)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
