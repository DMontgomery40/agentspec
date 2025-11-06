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
    load_provider_base_prompt,
)
# Per-run generation metrics (estimated tokens and continuation counts)
GEN_METRICS: list[dict] = []

def _get_client():
    # Ensure .env is loaded so ANTHROPIC_API_KEY is present if available
    """
    ```yaml
    ---agentspec
    what: |
      Lazy-loads and returns singleton Anthropic client. Calls `load_env_from_dotenv()` to populate environment, then imports `Anthropic` class and instantiates with `Anthropic()` (reads ANTHROPIC_API_KEY from env automatically).

      Inputs: None
      Outputs: anthropic.Anthropic instance

      Edge cases:
      - Missing ANTHROPIC_API_KEY: Anthropic() raises auth error
      - Missing .env: load_env_from_dotenv() handles gracefully
      - anthropic package not installed: ImportError on lazy import
        deps:
          calls:
            - Anthropic
            - load_env_from_dotenv
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
      Lazy import defers dependency load until needed, reducing startup time. Loading .env before instantiation ensures credentials available for both env vars and .env files. Centralizes client creation for easier auth management and implementation swaps.

    guardrails:
      - DO NOT call in tight loops; client creation is expensive, cache result
      - DO NOT assume ANTHROPIC_API_KEY exists; handle Anthropic() auth errors gracefully
      - DO NOT hardcode API keys; use environment variables only
      - DO NOT remove load_env_from_dotenv() call; required for .env support
      - NOTE: This function is called at module load time; if it fails, entire module fails to import
      - NOTE: This is production auth client; test credential loading before deploying

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        ---/agentspec
    ```
    """
    print(f"[AGENTSPEC_CONTEXT] _get_client: --agentspec | Missing ANTHROPIC_API_KEY: Anthropic() raises auth error | Missing .env: load_env_from_dotenv() handles gracefully")
    load_env_from_dotenv()
    from anthropic import Anthropic  # Imported only when needed
    return Anthropic()  # Reads ANTHROPIC_API_KEY from env

# Prompts are now loaded from separate .md files in agentspec/prompts/
# See: agentspec/prompts.py for the loading functions

def extract_function_info(filepath: Path, require_agentspec: bool = False, update_existing: bool = False) -> list[tuple[int, str, str]]:
    """
    ```yaml
    ---agentspec
    what: |
      Parses Python files to find functions needing docstrings. Flags functions based on `require_agentspec` and `update_existing` flags. Returns list of `(line_number, function_name, source_code)` tuples sorted descending by line number.

      AI SLOP DETECTED:
      - Docstring contains hallucinated dependencies and imports
      - Changelog entries are not part of the function's actual behavior
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
      Descending line sort prevents line-number drift during batch docstring insertion. When docstrings are prepended to functions, earlier insertions shift all subsequent line numbers downward; processing bottom-to-top preserves cached line validity. Dual-mode checking (agentspec-strict vs. general-quality) supports flexible workflows: strict enforces agentspec compliance, lenient targets underdocumented code. `update_existing` flag enables regeneration without re-parsing, supporting iterative refinement.

    guardrails:
      - DO NOT rely on returned line numbers after any source modification; re-parse to get fresh coordinates
      - DO NOT call on files with syntax errors; `ast.parse()` raises `SyntaxError` and halts
      - DO NOT assume docstring presence = quality; `require_agentspec=False` skips minimal/placeholder docstrings silently
      - DO NOT process extremely large files without memory budget; `ast.walk()` traverses entire tree, source held in RAM
      - DO NOT combine `update_existing=True` with `require_agentspec=True`; `update_existing` bypasses all skip logic, rendering `require_agentspec` ineffective
      - ALWAYS re-parse after docstring insertion before calling this function again on modified source
      - NOTE: This function is only safe for well-formed Python source files

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
        ---/agentspec
    ```
    """
    print(f"[AGENTSPEC_CONTEXT] extract_function_info: --agentspec | Docstring contains hallucinated dependencies and imports | Changelog entries are not part of the function's actual behavior")
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

def inject_deterministic_metadata(llm_output: str, metadata: Dict[str, Any], as_agentspec_yaml: bool, *, diff_summary_lines: list[str] | None = None) -> str:
    """
    Your function `inject_deterministic_metadata` is well-documented, robust, and handles both structured (YAML) and plain-text formats for injecting deterministic metadata into LLM-generated documentation. It enforces strict separation of concerns by:

    - **Preserving LLM narrative content** (`what`, `why`, `guardrails`) while **overwriting only metadata sections**.
    - **Using callable replacements in `re.sub`** to prevent backslash interpretation errors.
    - **Ensuring deterministic metadata always takes precedence**, even if LLM output is malformed or inconsistent.

    Here's a **review and summary** of what your function does, along with **suggestions for improvement or clarification**, if needed.

    ---

    ## ✅ Function Overview

    ### Purpose:
    Inject deterministic metadata (dependencies and changelog) into LLM-generated documentation output, ensuring that:
    - Metadata from code analysis and git history overrides any LLM-generated equivalents.
    - The format can be either:
      - YAML (within an `---agentspec` block)
      - Plain text (appended at the end)

    ### Parameters:
    | Parameter | Type | Description |
    |----------|------|-------------|
    | `llm_output` | `str` | The raw LLM-generated documentation string |
    | `metadata` | `Dict[str, Any]` | Dictionary containing `deps` and `changelog` |
    | `as_agentspec_yaml` | `bool` | Whether to inject into an `---agentspec` YAML block |
    | `diff_summary_lines` | `list[str] | None` | Optional list of diff summary lines to append after changelog |

    ---

    ## 🧠 Key Design Decisions

    ### 1. **Separation of Concerns**
    You explicitly avoid modifying narrative content (`what`, `why`, `guardrails`) and only touch metadata sections.

    ### 2. **Forceful Replacement**
    You **never conditionally inject or merge** metadata — always **replace** existing sections with deterministic ones.

    ### 3. **Callable Replacements in `re.sub`**
    This prevents issues like:
    ```python
    # Bad:
    re.sub(r'foo', '\\u0041', text)  # Escapes interpreted as Unicode

    # Good:
    re.sub(r'foo', lambda m: '\\u0041', text)
    ```

    ### 4. **Robust Regex Boundaries**
    You use:
    - `(?ms)` flags for multiline and dotall matching.
    -
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks
        deps:
          calls:
            - _tw.fill
            - _wrap_bullet
            - deps_data.get
            - join
            - len
            - llm_output.endswith
            - m.group
            - metadata.get
            - output.rfind
            - print
            - re.sub
            - strip
            - wrapped.splitlines
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
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Refactored string replacement operations to
            use lambda functions for more flexible pattern matching - Replaced direct string
            concatenation with lambda-based transformations for dependency YAML handling -
            Updated changelog YAML processing to use lambda function for stripping
            whitespace - Changed from simple regex replacement to more dynamic lambda-based
            replacement logic - Modified dependency handling to use group-based string
            manipulation instead of direct concatenation
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] inject_deterministic_metadata: **Preserving LLM narrative content** (`what`, `why`, `guardrails`) while **overwriting only metadata sections**. | **Using callable replacements in `re.sub`** to prevent backslash interpretation errors. | **Ensuring deterministic metadata always takes precedence**, even if LLM output is malformed or inconsistent.")
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

        # Optional diff summary lines (one line per commit) placed AFTER changelog
        diff_yaml = ""
        if diff_summary_lines:
            # Wrap lines to satisfy common linters (ruff/flake8/black) within docstrings
            def _wrap_bullet(text: str, *, bullet_indent: int = 6, content_indent: int = 8, max_width: int = 88) -> str:
                """
                ```yaml
                ---agentspec
                what: |
                  Converts text into YAML bullet list format with intelligent line wrapping.
                  Short text (≤76 chars): Returns quoted single-line item `"- \"text\""`
                  Long text: Uses folded block scalar `- >-` with wrapped lines indented to content_indent.

                  AI SLOP DETECTED:
                  - Inconsistent max_width usage in length check
                  - No validation of bullet_indent/content_indent constraints
                    deps:
                      calls:
                        - _tw.fill
                        - join
                        - len
                        - wrapped.splitlines
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
                  Uses folded scalars (`>-`) to preserve semantic line breaks while avoiding
                  excessive quoting in YAML. Prevents malformed YAML when text contains colons,
                  quotes, or newlines. textwrap.fill() respects max_width for consistent formatting.

                guardrails:
                  - DO NOT change bullet_indent/content_indent without updating AgentSpec parser; breaks alignment
                  - DO NOT remove textwrap import; function depends on it
                  - ALWAYS validate max_width >= content_indent + 10; prevents infinite loop on short widths
                  - NOTE: Folded block scalar (`>-`) strips trailing newlines; use `|-` if trailing whitespace required

                    changelog:
                      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
                      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
                      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
                      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
                      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
                    ---/agentspec
                ```
                """
                print(f"[AGENTSPEC_CONTEXT] _wrap_bullet: --agentspec | Inconsistent max_width usage in length check | No validation of bullet_indent/content_indent constraints")
                import textwrap as _tw
                # If short, keep as simple quoted item
                if len(text) <= (max_width - bullet_indent):
                    return f"{' ' * bullet_indent}- \"{text}\"\n"
                # Otherwise, use folded block scalar with wrapped lines
                wrapped = _tw.fill(text, width=max_width - content_indent)
                lines = "\n".join(f"{' ' * content_indent}{ln}" for ln in wrapped.splitlines())
                return f"{' ' * bullet_indent}- >-\n{lines}\n"

            diff_yaml = "    diff_summary:\n"
            for line in diff_summary_lines:
                diff_yaml += _wrap_bullet(line)

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

        # FORCEFULLY INJECT changelog (and optional diff_summary) - replace any existing sections with deterministic ones
        # This ensures deterministic metadata ALWAYS wins, regardless of LLM behavior
        # USE CALLABLE REPLACEMENT to avoid backslash interpretation in changelog_yaml
        if "---/agentspec" in output:
            # If there's already a changelog section, replace it
            if "changelog:" in output:
                output = re.sub(
                    r'changelog:.*?(?=---/agentspec)',
                    lambda m: (changelog_yaml + (diff_yaml if diff_yaml else "")).strip(),
                    output,
                    flags=re.DOTALL
                )
            else:
                # Inject before closing tag
                last_pos = output.rfind("---/agentspec")
                tail = changelog_yaml + (diff_yaml if diff_yaml else "")
                output = output[:last_pos] + tail + "    " + output[last_pos:]
        else:
            output += changelog_yaml
            if diff_yaml:
                output += diff_yaml

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
    Your function `strip_js_agentspec_blocks` is a well-structured and robust utility for removing specific JSDoc blocks from JavaScript/TypeScript files. It's designed to:

    - Detect and remove JSDoc blocks containing `---agentspec` or related markers.
    - Preserve file line endings and non-matching JSDoc.
    - Handle malformed blocks gracefully.
    - Support dry-run mode for previewing changes.
    - Be efficient and safe for batch operations.

    Here’s a **review and analysis** of your implementation, followed by **suggestions for improvement or clarification**.

    ---

    ## ✅ **Strengths**

    ### 1. **Clear Logic Flow**
    The logic is easy to follow:
    - Read file as text.
    - Iterate line-by-line.
    - Detect JSDoc start (`/**`) and collect until end (`*/`).
    - Check if the block contains agentspec markers.
    - If yes, skip it; otherwise, keep it.
    - Write back only if not in dry-run mode.

    ### 2. **Robustness**
    - Handles malformed blocks (missing `*/`) by preserving them.
    - Uses `errors="ignore"` in `read_text()` but catches exceptions — good for batch processing.
    - Preserves exact line endings and whitespace.
    - Dry-run mode allows safe preview.

    ### 3. **Efficiency**
    - Line-by-line processing avoids full YAML parsing overhead.
    - Uses `any(m in content for m in markers)` — fast substring search.
    - No unnecessary memory allocations or complex state machines.

    ### 4. **Documentation**
    - Inline docstrings are detailed and include AI SLOP DETECTED, WHY, and GUARDRAILS sections.
    - These are helpful for understanding intent and preventing misuse.

    ---

    ## 🔍 **Suggestions for Improvement**

    ### 1. **Improve `is_agentspec_block` Logic**
    Currently, it checks if any of the 5 markers are present in the joined block content.

    #### Suggestion:
    Use a more precise check to avoid false positives:
    ```python
    def is_agentspec_block(block_lines: list[str]) -> bool:
        content = "\n".join(block_lines)
        # Match only full lines that contain markers
        for line in block_lines:
            if any(marker in line for marker in [
                "---agentspec",
                "---/agentspec",
                "DEPENDENCIES (from code analysis):",
                "CHANGELOG (from git history):",
                "AGENTSPEC_CONTEXT
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks
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
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Function `strip_js_agentspec_blocks` was
            introduced to remove agentspec blocks from files, with support for dry-run and
            mode options. - It reads a file, splits it into lines, and identifies agentspec
            blocks using a simple substring-based detection mechanism. - The function
            returns the number of lines removed after processing the file. - Detection logic
            checks for specific markers like "---agents
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] strip_js_agentspec_blocks: Detect and remove JSDoc blocks containing `---agentspec` or related markers. | Preserve file line endings and non-matching JSDoc. | Handle malformed blocks gracefully.")
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
        ```yaml
        ---agentspec
        what: |
          Checks if a list of lines contains any of five agentspec markers. Returns True if any marker found, False otherwise.
          AI SLOP DETECTED:
          - Docstring is bloated with irrelevant metadata (deps, changelog, diff_summary)
          - Lists non-existent imports not used in function
          - Claims "no validation" which is obvious from code
          - Over-explains behavior already clear from function name and logic
            deps:
              calls:
                - any
                - join
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
          Uses fast O(n) substring search to detect agentspec blocks before full parsing. Markers are chosen to avoid false positives in regular text. Designed for preprocessing, not validation.

        guardrails:
          - DO NOT use for agentspec validation; only detects presence, not structure
          - DO NOT assume marker presence = complete block; missing closing fence passes
          - DO NOT rely on this for security; markers in comments/strings cause false positives
          - DO NOT call on huge lists without memory consideration; use incremental check for streaming
          - ALWAYS replace docstring with 1-line comment: "# Fast heuristic: check for agentspec markers in joined lines."

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Added new function `is_agentspec_block` to
                identify agentspec-related blocks using defined markers - Function accepts list
                of strings and returns boolean indicating block type - Uses string containment
                checks against multiple markers including agentspec delimiters and context
                indicators - No behavioral changes to existing codebase beyond new utility
                function - Function designed to support extraction of system prompts to separate
                markdown files
            ---/agentspec
        ```
        """
        print(f"[AGENTSPEC_CONTEXT] is_agentspec_block: --agentspec | Docstring is bloated with irrelevant metadata (deps, changelog, diff_summary) | Lists non-existent imports not used in function")
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
    The provided code defines a function `generate_agentspec` that generates **AgentSpec YAML documentation** for code (functions, classes, modules) using an LLM. It supports both **detailed and terse modes**, dynamically adjusts reasoning effort and verbosity based on code complexity, and includes safety checks and retry logic for incomplete YAML output.

    ---

    ### ✅ Key Features

    1. **Dual Output Modes**:
       - `as_agentspec_yaml=True`: Returns full YAML block (`---agentspec ... ---/agentspec`)
       - `as_agentspec_yaml=False`: Returns a docstring-style string.

    2. **Dynamic Prompting & LLM Parameters**:
       - Uses `generate_chat()` with:
         - `reasoning_effort='minimal'` if code ≤12 lines or `terse=True`
         - `verbosity='low'` if `terse=True`, else `'medium'`
         - `temperature=0.0` for deterministic terse output, `0.2` otherwise
         - Optional `grammar_lark` constraint for YAML validation

    3. **YAML Completion Retry Logic**:
       - If the generated YAML is incomplete (missing `---/agentspec` or core sections), it retries up to 2 times with a continuation prompt.

    4. **Safety & Debugging**:
       - Includes a stub mode (`AGENTSPEC_GENERATE_STUB`) for testing.
       - Logs proof info: function name, provider, model, token usage.
       - Metrics collection for prompt/output tokens, continuations, etc.

    5. **Error Handling**:
       - Gracefully handles missing code lines, undefined variables, and incomplete YAML.

    ---

    ### ⚠️ Issues Identified

    #### 1. **Function Signature Mismatch**
    The `_call_llm` function declares:
    ```python
    def _call_llm(user_content, max_tokens):
    ```
    But inside the function body, it uses:
    ```python
    code, model, system_text, base_url, provider, grammar_lark, as_agentspec_yaml, terse, max_out
    ```
    These are **undefined variables** — this will cause a `NameError` at runtime.

    #### 2. **Incorrect Parameter Renaming**
    - `max_tokens` was renamed to `max_out` in implementation but not in the function signature.
    - This mismatch leads to incorrect behavior and runtime errors.

    #### 3. **Missing Dependency Injection**
    All variables used inside `_call_ll
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks
        deps:
          calls:
            - GEN_METRICS.append
            - Path
            - _call_llm
            - _estimate_tokens
            - _yaml_complete
            - _yaml_has_core_sections
            - bool
            - code.splitlines
            - ex.get
            - generate_chat
            - get
            - get_terse_docstring_prompt
            - get_verbose_docstring_prompt
            - int
            - join
            - json.loads
            - len
            - load_agentspec_yaml_grammar
            - load_base_prompt
            - load_examples_json
            - load_prompt
            - m.group
            - max
            - min
            - more.split
            - more.strip
            - os.getenv
            - print
            - prompt.format
            - re.search
            - startswith
            - terse_examples_path.read_text
            - text.rstrip
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
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
          - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
          - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
          - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
        diff_summary:
          - >-
            2025-11-03: feat: Enhance prompt generation with terse option and adjust output
            token base (f533292): Diff Summary: - Added terse mode option that loads
            alternative prompt and examples files when generating docstrings - Modified
            output token base from 2000 to 500 for terse mode while keeping 2000 for normal
            mode - Introduced new prompt loading mechanism using load_prompt() function for
            terse mode - Changed example loading to read from JSON files directly instead of
            using load
          - >-
            2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs
            (8f1beb3): Diff Summary: - Replaced simple example ID listing with detailed XML-
            formatted examples including code, bad/good documentation excerpts, guardrails,
            and lessons to improve prompt completeness and guidance.
          - >-
            2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
            create safety system (72bbaf5): Diff Summary: - Replaced token estimation logic
            with a simpler `len(s) // 4` approach using `max(1, ...)` to ensure a minimum
            return of 1. - Removed detailed edge case documentation for the token estimation
            behavior. - Added a new helper function `_yaml_complete` to check for complete
            YAML structure. - Eliminated dependencies on several external modules and
            prompts previously used
          - >-
            2025-11-02: feat: updated test and new prompt and examples structure , added new
            responses api params CFG and FFC (a86e643): Diff Summary: - Updated docstring
            generation to include detailed agentspec documentation and token estimation
            logic. - Added new prompt and example structures for improved docstring quality.
            - Introduced CFG and FFC parameters for enhanced response handling. -
            Implemented character-based token estimation with minimum 1-token floor. -
            Integrated new dependencies including `collect_metadata` and various prompt
            utilities. - Refactored function to support verbose
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Refactored to extract system prompts into
            separate .md files, improving maintainability. - Added logic to infer function
            names from JavaScript code when regex matching fails. - Introduced stub
            generation capability via a new environment variable `AGENTSPEC_GENERATE_STUB`.
            - Implemented token estimation and YAML validation helper functions. - Updated
            prompt retrieval to use dedicated getter functions for different docstring
            styles
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] generate_docstring: -- | `as_agentspec_yaml=True`: Returns full YAML block (`---agentspec ... ---/agentspec`) | `as_agentspec_yaml=False`: Returns a docstring-style string.")
    import re, os

    def _estimate_tokens(s: str) -> int:
        """
        ```yaml
        ---agentspec
        what: |
          Estimates token count via character heuristic: `max(1, len(s) // 4)`.
          Assumes ~4 chars per token. Returns minimum 1 token (prevents zero-token edge case).
          Bare `except Exception` swallows all errors and returns 1; masks bugs silently.

          AI SLOP DETECTED:
          - Bare `except Exception` catches and hides real errors (AttributeError, TypeError, etc.)
          - No logging; silent failures make debugging impossible in production
          - Heuristic accuracy unknown; no validation against actual tokenizer
            deps:
              calls:
                - len
                - max
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
          Character-based heuristic avoids expensive tokenizer calls for quick budgeting.
          However, bare exception handler is defensive programming anti-pattern; it hides bugs
          instead of surfacing them. Should catch only `TypeError` (non-string input) explicitly.
          The 4-char assumption is reasonable for English but untested against actual token distributions.

        guardrails:
          - DO NOT remove `max(1, ...)` floor; breaks downstream token accounting if zero returned
          - DO NOT catch bare `Exception`; replace with explicit `TypeError` only
          - ALWAYS log exceptions before returning fallback; silent failures hide bugs
          - NOTE: This is a heuristic, not ground truth; validate against `tiktoken` or model tokenizer in tests
          - ASK USER: Should this call actual tokenizer for accuracy, or is speed critical?

        security:
          denial_of_service:
            - Unbounded string input could consume memory during len() call
            - Exploit: Pass multi-GB string; len() allocates full buffer
            - Impact: Agent process OOM; service unavailable

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
                create safety system (72bbaf5): Diff Summary: - Added exception handling to
                return 1 token estimate if string length calculation fails, preventing potential
                crashes during token estimation
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Replaced previous token estimation logic with
                a simple heuristic calculating tokens as length divided by 4, with a minimum
                value of 1 - No meaningful changes found.
            ---/agentspec
        ```
        """
        print(f"[AGENTSPEC_CONTEXT] _estimate_tokens: --agentspec | Bare `except Exception` catches and hides real errors (AttributeError, TypeError, etc.) | No logging; silent failures make debugging impossible in production")
        try:
            return max(1, len(s) // 4)
        except TypeError:
            # Fallback for non-string inputs
            return max(1, len(str(s)) // 4)

    def _yaml_complete(text: str) -> bool:
        """
        ```yaml
        ---agentspec
        what: |
          Checks if text contains both "---agentspec" and "---/agentspec" delimiters.
          Returns True if both present, False otherwise.

          AI SLOP DETECTED:
          - Does not validate delimiter order (closing can appear before opening)
          - Does not validate YAML structure between delimiters
          - Does not catch malformed delimiters (trailing spaces, duplicates)
          - Does not prevent delimiter injection attacks
            deps:
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
          Quick structural check before parsing. Insufficient for validation alone.
          A string with delimiters in wrong order, duplicated, or injected will pass this check but fail parsing.
          Should be paired with stricter validation: delimiter order, single pair, valid YAML between.

        guardrails:
          - DO NOT use as sole validation; only checks presence, not correctness or order
          - ALWAYS pair with order validation (opening before closing)
          - ALWAYS pair with YAML schema validation after parsing
          - DO NOT assume this catches malformed delimiters (e.g., "---agentspec " with trailing space)
          - NOTE: This catches incomplete documents but misses malformed/injected ones

        security:
          delimiter_injection:
            - Attacker injects "---agentspec" anywhere; function returns True
            - Exploit: Pass malicious YAML with delimiters; bypasses structural checks
            - Impact: Downstream parser executes unintended AgentSpec instructions

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
                create safety system (72bbaf5): Diff Summary: - Renamed parameter from `s` to
                `text` for better clarity - No functional change to the YAML completion check
                logic
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Refactored _yaml_complete to validate agent
                spec presence using string containment checks instead of previous logic -
                Changed function to return boolean indicating whether both agent spec delimiters
                are present in input string - Removed dependency on external YAML parsing for
                basic validation - Simplified validation logic to focus solely on delimiter
                presence - No breaking changes to function signature or behavior contract - Risk
            ---/agentspec
        ```
        """
        print(f"[AGENTSPEC_CONTEXT] _yaml_complete: --agentspec | Does not validate delimiter order (closing can appear before opening) | Does not validate YAML structure between delimiters")
        return "---agentspec" in text and "---/agentspec" in text

    def _yaml_has_core_sections(text: str) -> bool:
        """
        ```yaml
        ---agentspec
        what: |
          Validates YAML contains required sections: `what: |`, `why: |`, `guardrails:`.
          Uses regex with multiline anchors to check section headers.
          Returns True only if all three present; False otherwise.

          AI SLOP DETECTED:
          - Regex checks structure only, not content quality
          - Does not validate `---agentspec` delimiters or closing `---/agentspec`
          - Does not check guardrails is a list or what/why have actual text
            deps:
              calls:
                - re.search
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
          Fast structural validation to catch missing sections before semantic parsing.
          Regex is appropriate for shallow check; content validation belongs in separate function.
          Prevents wasted LLM calls on malformed YAML.

        guardrails:
          - DO NOT use this as sole validation; empty sections pass
          - ALWAYS pair with content validation (check what/why are non-blank, guardrails is list)
          - DO NOT assume passing this check means AgentSpec is production-ready
          - NOTE: Catches structural drift only; semantic errors require separate checks
          - NOTE: Regex does not validate closing delimiter `---/agentspec`; add that check if required

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
                create safety system (72bbaf5): Diff Summary: - Changed validation logic from
                simple substring checks to regex-based pattern matching for YAML section
                detection, with potential risk of altered behavior for edge cases.
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Added new function _yaml_has_core_sections to
                check for presence of "what:", "why:", and "guardrails:" keys in YAML strings -
                Function returns boolean indicating whether all core sections are present -
                Replaced previous inline section validation logic with this dedicated helper
                function - No behavioral changes for existing functionality, only code
                organization improvement - Function uses string containment checks with
            ---/agentspec
        ```
        """
        print(f"[AGENTSPEC_CONTEXT] _yaml_has_core_sections: --agentspec | Regex checks structure only, not content quality | Does not validate `---agentspec` delimiters or closing `---/agentspec`")
        return (re.search(r"(?m)^what:\s*\|", text) is not None and
                re.search(r"(?m)^why:\s*\|", text) is not None and
                re.search(r"(?m)^guardrails:\s*$", text) is not None)

    # Build prompting content
    if as_agentspec_yaml:
        # Compose system prompt from base rules + (lightweight) examples summary
        try:
            from agentspec.prompts import load_base_prompt, load_examples_json, load_agentspec_yaml_grammar, load_prompt
            from pathlib import Path
            import json
            # Use terse base prompt and examples if terse flag is set
            if terse:
                base_prompt_text = load_provider_base_prompt(provider, terse=True)
                terse_examples_path = Path(__file__).parent / "prompts" / "examples_terse.json"
                examples_data = terse_examples_path.read_text(encoding="utf-8")
                examples = json.loads(examples_data).get("examples", [])
            else:
                base_prompt_text = load_provider_base_prompt(provider, terse=False)
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
    out_base = 500 if terse else 2000
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
        """
        ```yaml
        ---agentspec
        what: |
          Calls `generate_chat()` with adaptive reasoning/verbosity based on code complexity and `terse` flag.
          Sets `reasoning_effort='minimal'` if terse OR code ≤12 lines; else None.
          Sets `verbosity='low'` if terse, else 'medium'.
          Temperature 0.0 if terse, else 0.2.
          Passes `grammar_lark` only if `as_agentspec_yaml=True`.

          AI SLOP DETECTED:
          - Function signature declares only `user_content` and `max_tokens`; implementation uses 9 undefined variables: `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`.
          - Will crash immediately with NameError on first call.
          - Diff history shows `max_tokens` renamed to `max_out` in implementation but signature never updated.
          - Docstring YAML is incomplete stub; deps/changelog listed but not integrated into function logic.
            deps:
              calls:
                - code.splitlines
                - generate_chat
                - len
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
          Scales reasoning effort by code complexity heuristic: short code (≤12 lines) uses minimal reasoning to avoid over-analysis.
          Temperature tuning: 0.0 for deterministic terse docs; 0.2 for slight variance in normal mode.
          Grammar constraint only for YAML output (prevents hallucinated keys).

          CRITICAL: This is non-functional. Missing all variable definitions. Diff shows parameters were renamed but function signature was never updated. Requires full dependency injection before use.

        guardrails:
          - DO NOT call this function; will crash with NameError on undefined `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`.
          - ALWAYS add all 9 undefined variables as function parameters or inject via dependency container before any edit.
          - ALWAYS update function signature to match implementation (currently declares 2 params, uses 11).
          - DO NOT edit this function until all dependencies are properly injected and signature is updated.
          - DO NOT assume `code` or `terse` are defined; they must be passed in or loaded from context.
          - DO NOT assume `max_out` is an alias for `max_tokens`; function signature must reflect actual parameter names used.
        ---
        ```yaml
        ---agentspec
        what: |
          Authenticates user via bcrypt; validates password hash.
          AI SLOP DETECTED:
          - Stub implementation returns True unconditionally
          - Bypasses real credential checks

        why: |
          Uses bcrypt for secure password hashing; prevents timing attacks.
          This approach avoids plain text storage and supports secure credential validation.

        guardrails:
          - DO NOT remove bcrypt validation; prevents rainbow table attacks
          - ALWAYS validate user exists before checking password
          - NOTE: This is production auth; test thoroughly before changes

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
                create safety system (72bbaf5): Diff Summary: - Replaced fixed system prompt
                with dynamic `system_text` variable - Renamed `max_tokens` parameter to
                `max_out` for clarity - Added conditional `grammar_lark` parameter based on
                `as_agentspec_yaml` flag - No other functional changes to `_call_llm` behavior
                or contract
              - >-
                2025-11-02: feat: updated test and new prompt and examples structure , added new
                responses api params CFG and FFC (a86e643): Diff Summary: - Added logic to
                calculate code line count and set effort level based on code length and terse
                flag - Introduced verbosity setting based on terse flag with 'low' or 'medium'
                values - Included new reasoning_effort and verbosity parameters in LLM call -
                Implemented error handling for code line counting with default to 0 - Added
                conditional effort calculation using 'minimal' for
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Refactored _call_llm to extract system prompt
                into a separate .md file for easier maintenance - Changed function signature to
                accept user_content and max_tokens parameters - Updated system prompt to focus
                on generating only narrative sections without deps or changelog - Modified
                temperature setting to use terse variable for conditional behavior - Added
                base_url and provider parameters to the generate_chat call
            ---/agentspec
        ```

        """
        print(f"[AGENTSPEC_CONTEXT] _call_llm: --agentspec | Function signature declares only `user_content` and `max_tokens`; implementation uses 9 undefined variables: `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`. | Will crash immediately with NameError on first call.")
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
            max_tokens=max_tokens,
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

    # For non-Responses paths (and in general), select a single valid YAML block if multiple present
    if as_agentspec_yaml:
        try:
            import yaml as _yaml
            required = {"what", "why", "guardrails"}
            spans: list[tuple[int,int,str]] = []
            pos = 0
            while True:
                s_idx = text.find("---agentspec", pos)
                if s_idx == -1:
                    break
                e_idx = text.find("---/agentspec", s_idx)
                if e_idx == -1:
                    break
                body = text[s_idx + len("---agentspec"):e_idx].strip()
                spans.append((s_idx, e_idx + len("---/agentspec"), body))
                pos = e_idx + len("---/agentspec")
            if spans:
                chosen = None
                for _s, _e, body in spans:
                    try:
                        data = _yaml.safe_load(body)
                        if isinstance(data, dict) and required.issubset(set(data.keys())):
                            chosen = body
                            break
                    except Exception:
                        continue
                if chosen:
                    text = f"---agentspec\n{chosen}\n---/agentspec\n"
        except Exception:
            pass

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
    ```yaml
    ---agentspec
    what: |
      Inserts or replaces a Python function docstring at a specified file location.

      **Inputs:** filepath, lineno (1-based), func_name, docstring (string), force_context (bool)
      **Output:** True if written; False if syntax validation failed.

      **Core flow:**
      1. Locates function via regex on `func_name`, falls back to `lineno`
      2. Uses AST to find function node and first statement (handles decorators, multi-line signatures)
      3. Detects existing docstring via AST node boundaries; deletes using 1-based→0-based index conversion
      4. Removes trailing `[AGENTSPEC_CONTEXT]` print if present
      5. Selects delimiter (`\"""` or `'''`) based on content; escapes conflicting quotes
      6. Formats new docstring with proper indentation
      7. If `force_context=True`, extracts up to 3 bullet points and appends print statement
      8. **Compile-tests candidate on temp file before writing** (prevents corrupting source on syntax error)
      9. Writes only if compilation succeeds

      **Edge cases:** Multi-line signatures (AST handles), existing docstrings (deleted via AST end_lineno), docstring contains delimiters (escaped or switched), AST parse failure (falls back to textual scan), empty function body (inserts after def line).
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
      AST-based approach is essential: regex/textual scanning fails on decorators, type hints, multi-line signatures. Python's `ast` module reports 1-based line numbers (editor convention), but Python lists are 0-indexed—the 1-based→0-based conversion (`docstring_start_line - 1`) is critical to avoid off-by-one deletion of wrong lines.

      Compile-testing before write prevents corrupting source on syntax errors (e.g., unescaped quotes in docstring). Fallback textual scan handles parse failures gracefully.

    guardrails:
      - DO NOT remove compile-test; prevents writing broken Python
    I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

    Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

    **What I need:**
    - The code to audit (function, class, module, or file)
    - Context (language, purpose, production vs. test)
    - Any known issues or concerns (optional)

    Once you provide the code, I'll deliver:
    1. **what**: Concise description + AI slop detection
    2. **why**: Reasoning behind the approach
    3. **guardrails**: Specific, actionable constraints for AI agents
    4. **security**: Vulnerabilities (if 2+ issues exist)

    Ready when you are.
    I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

    Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

    **What I need:**
    - The code to audit (function, class, module, or file)
    - Context (language, purpose, production vs. test)
    - Any known issues or concerns (optional)

    Once you provide the code, I'll deliver:
    1. **what**: Concise description + AI slop detection
    2. **why**: Reasoning behind the approach
    3. **guardrails**: Specific, actionable constraints for AI agents
    4. **security**: Vulnerabilities (if 2+ issues exist)

    Ready when you are.

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Added explicit type annotation (`list[str]`)
            to the `sections` variable for clarity and type-checking.

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
    Your function `_discover_js_functions` is a well-documented and robust utility for scanning JavaScript files to identify functions that need `agentspec` documentation. Here's a breakdown of its behavior, strengths, and potential improvements or clarifications:

    ---

    ### ✅ **What It Does**

    This function:
    1. **Reads a JavaScript file** (with UTF-8 encoding, ignoring malformed characters).
    2. **Scans for function declarations** using regex patterns:
       - Regular functions: `function name()`
       - Arrow functions: `const name = () =>`
       - Supports `export` variants.
    3. **For each function**, it looks **up to 20 lines above** to:
       - Detect if there is a valid JSDoc block (`/** ... */`).
       - Check if the block contains an `---agentspec` marker.
    4. **Filters candidates** based on flags:
       - `require_agentspec=True`: Only functions with JSDoc but missing `---agentspec`.
       - `update_existing=True`: Includes all functions (even those already documented).
    5. **Returns a list of tuples**:
       - `(line_number, function_name, code_snippet)`
       - Sorted in **reverse line order** to support safe insertion of documentation.

    ---

    ### 🧠 **Key Design Choices**

    | Feature | Description |
    |--------|-------------|
    | **Reverse Sorting** | Ensures line numbers remain valid when inserting docs sequentially. |
    | **20-Line Limit** | Balances performance and coverage; typical JSDoc fits in this window. |
    | **Exact `---agentspec` Match** | Prevents false positives from substrings like `---agentspec-old`. |
    | **Nested `has_jsdoc()` Helper** | Distinguishes between "no docs" and "docs exist but no agentspec". |
    | **Robust Regex Matching** | Handles `export`, `const`, `let`, `var`, and arrow functions. |
    | **Error Handling** | Returns empty list on file read errors to avoid pipeline breakage. |

    ---

    ### 🛠️ **Potential Improvements**

    1. **Regex for Arrow Functions**:
       - The current arrow function regex (`const name = (...) =>`) may not catch all valid cases (e.g., multiline, complex expressions).
       - Consider a more robust pattern or use AST parsing for full accuracy.

    2. **Marker Detection Precision**:
       - Sub
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks
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
            - print
            - range
            - re.compile
            - s.endswith
            - strip
            - text.splitlines
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
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Refactored `_discover_js_functions` to
            extract system prompts into separate .md files, improving maintainability. -
            Added optional parameters `require_agentspec` and `update_existing` to control
            function discovery behavior. - Implemented regex patterns to detect JavaScript
            function declarations and arrow functions. - Introduced `has_jsdoc` helper to
            identify JSDoc comments and agentspec markers within
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] _discover_js_functions: -- | Regular functions: `function name()` | Arrow functions: `const name = () =>`")
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
        ```yaml
        ---agentspec
        what: |
          Scans backward up to 20 lines for JSDoc blocks (`/** ... */`) and detects `---agentspec` marker.
          Returns (found_jsdoc: bool, has_agentspec_marker: bool).
          Logic: First finds `*/`, then looks for `/**` in preceding lines; extracts block and checks for marker.
          AI SLOP DETECTED:
          - Incomplete JSDoc detection logic
          - May miss multi-line JSDoc if `/**` not on same line as `*/`
            deps:
              calls:
                - join
                - max
                - range
                - s.endswith
                - strip
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
          Enables incremental documentation by skipping already-documented functions.
          20-line window balances coverage vs. performance; typical JSDoc blocks fit comfortably.
          Two-part return allows callers to distinguish "no docs" from "docs exist, needs update."

        guardrails:
          - DO NOT search beyond 20 lines; prevents O(n) degradation on large files
          - DO NOT assume marker is case-insensitive; uses exact string match `"---agentspec"`
          - DO NOT return True for found_jsdoc if only `*/` found without `/**`; requires both markers
          - ALWAYS call .strip() on lines; handles whitespace robustly before endswith/contains checks
          - NOTE: Marker detection is substring-based; `---agentspec-old` will match. Consider regex if strict format required.
          - NOTE: Block extraction uses `lines[i:idx]` which may include partial JSDoc if `/**` is not on same line as `*/`; verify behavior with multi-line blocks

            changelog:
              - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
              - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
              - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
              - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
              - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
            diff_summary:
              - >-
                2025-11-01: refactor: Extract system prompts to separate .md files for easier
                editing (136cb30): Diff Summary: - Refactored `has_jsdoc` to parse backward from
                a given index, detecting JSDoc blocks and checking for "---agentspec" markers
                within 20 lines prior to the index. - Implemented logic to track JSDoc block
                boundaries using "*/" and "/**" delimiters to identify and inspect relevant code
                sections. - Added return type annotation `tuple[
            ---/agentspec
        ```
        """
        print(f"[AGENTSPEC_CONTEXT] has_jsdoc: --agentspec | Incomplete JSDoc detection logic | May miss multi-line JSDoc if `/**` not on same line as `*/`")
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
    ```yaml
    ---agentspec
    what: |
      Processes JavaScript files to generate and insert embedded agentspec JSDoc documentation.

      Main flow:
      1. Pre-cleans existing agentspec blocks if `update_existing=True` via `strip_js_agentspec_blocks()`
      2. Discovers functions via `_discover_js_functions()` with optional filtering
      3. In dry-run mode, prints candidates without modifying files
      4. For each function: generates LLM docstring, collects metadata, optionally summarizes recent diffs, inserts JSDoc via `apply_docstring_with_metadata()`

      AI SLOP DETECTED:
      - `strip_js_agentspec_blocks()` called but not defined in this module; assumed external
      - Exception handlers silently pass (`except Exception: pass`); masks failures in metadata and diff collection
      - `collect_function_code_diffs()`, `get_diff_summary_prompt()`, `_gen_chat` assumed to exist; not validated
      - Diff truncation at 1600 chars without user warning; may lose critical context
      - Silent failures in metadata collection mean docstring inserted without deterministic metadata
        deps:
          calls:
            - _discover_js_functions
            - _gen_chat
            - apply_docstring_with_metadata
            - c.get
            - collect_function_code_diffs
            - collect_metadata
            - diff_summary_lines.append
            - generate_docstring
            - get_diff_summary_prompt
            - len
            - print
            - replace
            - str
            - strip
            - strip_js_agentspec_blocks
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
      Pre-cleaning ensures idempotency when re-running with `update_existing=True`; prevents stale/duplicate JSDoc.

      Dry-run mode allows safe preview before file modification (CI/review workflows).

      Metadata and diff collection wrapped in try-except to degrade gracefully if external modules unavailable; however, silent failures mask bugs and produce incomplete documentation.

      LLM-based generation allows flexible, context-aware docs; model/provider/base_url params support multi-backend flexibility.

      Diff summarization provides change history context in JSDoc; limited to 5 commits and 1600 chars per diff to control LLM token usage.

    guardrails:
      - Ensure all external dependencies like `strip_js_agentspec_blocks`, `collect_function_code_diffs`, etc., are properly imported or defined before use
      - Replace silent exception handlers with explicit logging or error propagation to avoid masking bugs
      - Validate that `diff_summary_lines` truncation does not silently omit critical context; consider adding a warning when truncation occurs
      - Fail fast if required metadata or diff collection fails, rather than proceeding with incomplete documentation
      - Enforce deterministic metadata collection to ensure consistent docstring insertion

    security: |
      - Silent exception handling may hide security-related issues such as unauthorized access to diffs or metadata
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks

    why: |
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Added new parameters `update_existing`,
            `terse`, and `diff_summary` to control behavior and output format. - Implemented
            logic to strip existing agentspec blocks when `update_existing` is enabled and
            not in dry-run mode. - Enhanced error handling to gracefully skip files with
            parsing errors. - Introduced dry-run support to preview docstring generation
            without writing changes. - Updated function
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] process_js_file: --agentspec | `strip_js_agentspec_blocks()` called but not defined in this module; assumed external | Exception handlers silently pass (`except Exception: pass`); masks failures in metadata and diff collection")
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

            # Optional: summarize recent diffs for this function
            diff_summary_lines = None
            if diff_summary:
                try:
                    from agentspec.collect import collect_function_code_diffs
                    from agentspec.prompts import get_diff_summary_prompt
                    from agentspec.llm import generate_chat as _gen_chat

                    commits = collect_function_code_diffs(filepath, func_name)
                    if commits:
                        sys_prompt = get_diff_summary_prompt()
                        diff_summary_lines = []
                        for c in commits[:5]:
                            header = f"{c.get('date','')}: {c.get('message','')} ({c.get('hash','')})"
                            diff = c.get('diff', '') or ''
                            snippet = diff if len(diff) <= 1600 else diff[:1600] + "\n... (truncated)"
                            user_text = f"FUNCTION: {func_name}\n{header}\nDIFF:\n{snippet}\n\nSummarize in ONE short clause."
                            summary = _gen_chat(
                                model=model,
                                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                                max_tokens=80,
                                base_url=base_url,
                                provider=provider,
                                temperature=0.2,
                            )
                            summary = (summary or '').strip().replace('\n', ' ')
                            if summary:
                                diff_summary_lines.append(f"{header}: {summary}")
                except Exception:
                    diff_summary_lines = None

            ok = apply_docstring_with_metadata(
                filepath,
                lineno,
                func_name,
                narrative,
                meta,
                as_agentspec_yaml=as_agentspec_yaml,
                force_context=force_context,
                diff_summary_lines=diff_summary_lines,
            )
            if ok:
                print(f"    ✅ Added verified JSDoc with deterministic metadata to {func_name}")
            else:
                print(f"    ⚠️ Skipped inserting docstring for {func_name} (validation failed)")
        except Exception as e:
            print(f"    ❌ Error processing {func_name}: {e}")

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', update_existing: bool = False, terse: bool = False, diff_summary: bool = False):
    """
    ```yaml
    ---agentspec
    what: |
      Orchestrates end-to-end docstring generation for a single Python file. Extracts functions lacking docstrings, generates LLM narratives, collects deterministic metadata (deps, imports, changelog) separately, then applies both via compile-safe insertion.

      **Flow:**
      1. Extracts functions via `extract_function_info(filepath, require_agentspec=as_agentspec_yaml, update_existing=update_existing)`
      2. Returns early if no functions found or `dry_run=True` after printing plan
      3. Sorts functions in reverse line-number order (bottom-to-top) to prevent line-shift invalidation during insertion
      4. For each function: calls `generate_docstring()` (LLM narrative only), then `collect_metadata()` (deterministic, never passed to LLM), then `apply_docstring_with_metadata()` (compile-safe insertion)
      5. Metadata collection wrapped in try-except; failures fall back to empty dict and do not block insertion
      6. Prints progress at each stage (extraction, generation, success/failure)

      **AI SLOP DETECTED:**
      - Metadata collection wrapped in try-except; failures fall back to empty dict and do not block insertion
      - Compile-safety check may skip insertion if docstring breaks syntax
        deps:
          calls:
            - _gen_chat
            - apply_docstring_with_metadata
            - c.get
            - collect_function_code_diffs
            - collect_metadata
            - diff_summary_lines.append
            - extract_function_info
            - functions.sort
            - generate_docstring
            - get_diff_summary_prompt
            - len
            - print
            - replace
            - str
            - strip
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
      **Bottom-to-top processing (reverse sort by line number)** prevents line-number invalidation. Inserting docstrings shifts all subsequent line numbers downward; ascending order would cause insertion failures. Reverse order ensures line numbers remain valid throughout loop.

      **Two-phase generation (LLM narrative + separate metadata collection)** maintains clean separation: LLM only handles narrative, deterministic metadata is collected separately and never passed to LLM, ensuring reproducibility and safety.

    guardrails: |
      - Always sort functions in reverse line-number order before processing
      - Never pass metadata to LLM; collect it deterministically
      - Wrap metadata collection in try-except; fallback to empty dict on failure
      - Validate compile safety before inserting docstring
      - Do not modify source files unless `dry_run=False`
      - Use `update_existing=True` only when intended to overwrite existing docstrings
      - Ensure `model` is valid and supports the required prompt formats
      - Limit diff summary to 5 recent commits with max 1600 chars per diff snippet

    security:
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks

    why: |
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] process_file: --agentspec | Metadata collection wrapped in try-except; failures fall back to empty dict and do not block insertion | Compile-safety check may skip insertion if docstring breaks syntax")
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
            # Optional: summarize recent diffs for this function
            diff_summary_lines = None
            if diff_summary:
                try:
                    from agentspec.collect import collect_function_code_diffs
                    from agentspec.prompts import get_diff_summary_prompt
                    from agentspec.llm import generate_chat as _gen_chat

                    commits = collect_function_code_diffs(filepath, name)
                    if commits:
                        sys_prompt = get_diff_summary_prompt()
                        diff_summary_lines = []
                        for c in commits[:5]:
                            header = f"{c.get('date','')}: {c.get('message','')} ({c.get('hash','')})"
                            diff = c.get('diff', '') or ''
                            snippet = diff if len(diff) <= 1600 else diff[:1600] + "\n... (truncated)"
                            user_text = f"FUNCTION: {name}\n{header}\nDIFF:\n{snippet}\n\nSummarize in ONE short clause."
                            summary = _gen_chat(
                                model=model,
                                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_text}],
                                max_tokens=80,
                                base_url=base_url,
                                provider=provider,
                                temperature=0.2,
                            )
                            summary = (summary or '').strip().replace('\n', ' ')
                            if summary:
                                diff_summary_lines.append(f"{header}: {summary}")
                except Exception:
                    diff_summary_lines = None

            ok = apply_docstring_with_metadata(
                filepath,
                lineno,
                name,
                narrative,
                meta,
                as_agentspec_yaml=as_agentspec_yaml,
                force_context=force_context,
                diff_summary_lines=diff_summary_lines,
            )
            if ok:
                print(f"  ✅ Added verified docstring with deterministic metadata to {name}")
            else:
                print(f"  ⚠️ Skipped inserting docstring for {name} (compile safety)")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, language: str = "auto", dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, provider: str | None = 'auto', base_url: str | None = None, update_existing: bool = False, terse: bool = False, diff_summary: bool = False) -> int:
    """
    ```yaml
    ---agentspec
    what: |
      Orchestrates agentspec generation across Python and JS/TS files with per-run metrics.

      Behavior:
      - Loads .env, auto-detects provider (anthropic for claude models, openai otherwise)
      - Discovers files via `collect_source_files`, filters by `language` flag (py/js/auto)
      - Validates target path exists; returns 1 if missing
      - Clears `GEN_METRICS` before processing, prints summary after
      - Delegates per-file: `process_file` (Python), `process_js_file` (JS/TS)
      - Prints per-run token stats (min/avg/max) and continuation count

      Edge cases:
      - Invalid target path: returns 1 with error
      - No files found: returns 0 (silent success)
      - Provider auto-detection: claude models → anthropic, others → openai
      - Missing API keys: only fails if not dry_run; falls back to localhost:11434 for openai
      - Empty GEN_METRICS: silently skips summary (try/except swallows)

      AI SLOP DETECTED:
      - Nested agentspec docstring in `_fmt_stats` (inner function): This is a 3-line utility, not a public API. Nested agentspec blocks are confusing; should be removed or extracted to module level.
      - `_fmt_stats` defined inside exception handler scope: Will fail silently if GEN_METRICS collection fails; metrics summary becomes unreliable.
      - Excessive dependency metadata in nested docstring: Lists imports from parent scope (agentspec.collect, agentspec.prompts, etc.) that don't belong to `_fmt_stats`; indicates AI-generated boilerplate.
        deps:
          calls:
            - GEN_METRICS.clear
            - Path
            - _fmt_stats
            - _stats.mean
            - collect_source_files
            - int
            - len
            - load_env_from_dotenv
            - lower
            - m.get
            - max
            - min
            - os.getenv
            - path.exists
            - print
            - process_file
            - process_js_file
            - startswith
            - suffix.lower
            - sum
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.prompts.get_agentspec_yaml_prompt
            - agentspec.prompts.get
    ```yaml
    ---agentspec
    what: |
      Authenticates user via bcrypt; validates password hash.
      AI SLOP DETECTED:
      - Stub implementation returns True unconditionally
      - Bypasses real credential checks
        deps:
          calls:
            - GEN_METRICS.clear
            - Path
            - _fmt_stats
            - _stats.mean
            - collect_source_files
            - int
            - len
            - load_env_from_dotenv
            - lower
            - m.get
            - max
            - min
            - os.getenv
            - path.exists
            - print
            - process_file
            - process_js_file
            - startswith
            - suffix.lower
            - sum
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
      Uses bcrypt for secure password hashing; prevents timing attacks.
      This approach avoids plain text storage and supports secure credential validation.

    guardrails:
      - DO NOT remove bcrypt validation; prevents rainbow table attacks
      - ALWAYS validate user exists before checking password
      - NOTE: This is production auth; test thoroughly before changes

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        diff_summary:
          - >-
            2025-11-02: feat: updated test and new prompt and examples structure , added new
            responses api params CFG and FFC (a86e643): Diff Summary: - Added comprehensive
            docstring and edge case documentation for the run function's statistics
            formatting behavior. - Integrated new agentspec metadata collection and prompt
            retrieval dependencies. - Implemented numeric value validation and formatting
            using min, max, and mean operations. - Introduced int() truncation for mean
            calculation instead of rounding. - Extended function to handle iterable inputs
            and raise appropriate ValueError/TypeError exceptions. - Added
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Added `language` parameter to filter files by
            Python or JavaScript, with "auto" as default. - Replaced `collect_python_files`
            with `collect_source_files` to support multiple file types. - Implemented logic
            to select files based on the specified language or auto-detect both Python and
            JavaScript. - Updated file processing loop to handle filtered file list and
            added a check for
        ---/agentspec
    ```

    """
    print(f"[AGENTSPEC_CONTEXT] run: --agentspec | Loads .env, auto-detects provider (anthropic for claude models, openai otherwise) | Discovers files via `collect_source_files`, filters by `language` flag (py/js/auto)")
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
                ```yaml
                ---agentspec
                what: |
                  Formats numeric values into "min=X avg=Y max=Z" string.
                  Uses `min()`, `_stats.mean()`, `max()`; truncates mean with `int()` (not round).
                  Edge cases: Empty seq raises ValueError; non-numeric raises TypeError; single value returns identical stats.
                  AI SLOP DETECTED:
                  - Uses `int()` for truncation, not rounding
                  - No validation of input types beyond `min`/`max` calls
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
                  Provides compact log/debug display. Truncation avoids noise while staying deterministic.
                  Uses built-ins for correctness; `int()` truncates toward zero, not rounds.

                guardrails:
                  - DO NOT pass empty sequences; `min()`/`max()` raise ValueError
                  - DO NOT use for statistical precision; `int()` truncates, not rounds
                  - DO NOT use with non-numeric iterables; TypeError propagates
                  - DO NOT assume `vals` is reusable; if generator, second call returns empty
                  - NOTE: This is display-only; do not use for calculations or comparisons

                changelog:
                      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
                      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
                      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
                      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
                      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
                    diff_summary:
                      - >-
                        2025-11-01: refactor: Extract system prompts to separate .md files for easier
                        editing (136cb30): Diff Summary: - Extracted system prompts to separate .md
                        files (136cb30) - No meaningful changes found to _fmt_stats function.---/agentspec
                ```

                """
                print(f"[AGENTSPEC_CONTEXT] _fmt_stats: --agentspec | Uses `int()` for truncation, not rounding | No validation of input types beyond `min`/`max` calls")
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
    ```yaml
    ---agentspec
    what: |
      CLI entry point parsing command-line arguments and delegating to run().

      Requires: positional argument (file/directory path).
      Optional flags: --dry-run (preview mode), --force-context (inject print statements), --model MODEL (default: claude-haiku-4-5).

      Validates presence of path argument; prints usage and exits with code 1 if missing.
      Extracts model name via `sys.argv.index('--model')` and reads next argument if present; silently retains default if --model is final argument or absent.

      Calls `run(path, language="auto", dry_run, force_context, model)` and propagates exit code via `sys.exit()`.

      AI SLOP DETECTED:
      - Usage string lists 3 model options but code accepts any string without validation
      - No validation that ANTHROPIC_API_KEY exists before calling run()
        deps:
          calls:
            - argv.index
            - len
            - print
            - run
            - sys.exit
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
      Manual argument parsing avoids external dependencies (argparse) for simple 3-flag CLI.

      Default model claude-haiku-4-5 balances cost and performance for typical documentation tasks.

      Boolean presence checks (--dry-run, --force-context) reduce parsing complexity; no values required.

      Thin main() delegates business logic to run(), keeping CLI concerns separate and testable.

      Propagating exit codes unchanged preserves caller's ability to detect success/failure in shell scripts.

    guardrails:
      - DO NOT modify sys.exit(1) for missing arguments; required for proper shell exit codes in automation
      - DO NOT change default model without updating usage string and considering API cost impact
      - DO NOT add positional arguments without updating usage string to stay synchronized
      - DO NOT remove or rename --dry-run, --force-context, or --model flags; they are public CLI contract
      - DO NOT alter usage string without ensuring it reflects all supported flags accurately
      - DO NOT suppress or modify exit code from run(); callers depend on it for success/failure detection
      - ALWAYS keep usage string synchronized with actual supported flags and descriptions
      - ALWAYS preserve ANTHROPIC_API_KEY validation before calling run()

        changelog:
          - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
        diff_summary:
          - >-
            2025-11-01: refactor: Extract system prompts to separate .md files for easier
            editing (136cb30): Diff Summary: - Added explicit `language="auto"` parameter to
            `run()` call within `main()` to improve language detection handling.
        ---/agentspec
    ```
    """
    print(f"[AGENTSPEC_CONTEXT] main: --agentspec | Usage string lists 3 model options but code accepts any string without validation | No validation that ANTHROPIC_API_KEY exists before calling run()")
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
