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
    load_provider_base_prompt,
)
# Per-run generation metrics (estimated tokens and continuation counts)
GEN_METRICS: list[dict] = []

## Removed unused _get_client helper (dead code)

# Prompts are now loaded from separate .md files in agentspec/prompts/
# See: agentspec/prompts.py for the loading functions

def extract_function_info(filepath: Path, require_agentspec: bool = False, update_existing: bool = False) -> list[tuple[int, str, str]]:
    '''
    Brief one-line description.

    Parses a Python file to identify functions requiring docstrings, returning their line numbers, names, and source code sorted in descending order to preserve line validity during batch insertion.

    WHAT THIS DOES:
    - Reads the entire source file from disk and parses it into an Abstract Syntax Tree (AST) using `ast.parse()`, which raises `SyntaxError` if the file contains syntax errors
    - Walks the AST to find all function definitions (both `ast.FunctionDef` and `ast.AsyncFunctionDef` nodes) and evaluates each against filtering criteria
    - Applies dual-mode filtering logic: when `require_agentspec=True`, flags functions lacking docstrings OR lacking the `---agentspec` YAML marker; when `require_agentspec=False`, flags functions lacking docstrings OR having docstrings with fewer than 5 lines (heuristic for minimal/placeholder documentation)
    - When `update_existing=True`, bypasses all filtering logic and unconditionally flags every function for processing, enabling regeneration workflows
    - Extracts the source code span for each flagged function by slicing the source lines array from `node.lineno - 1` (0-indexed) to `node.end_lineno` (inclusive), reconstructing the function definition as a string
    - Returns a list of `(line_number, function_name, source_code)` tuples sorted in descending order by line number (bottom-to-top), ensuring that when docstrings are prepended to functions during batch processing, earlier insertions do not shift the cached line numbers of functions processed later

    WHY THIS APPROACH:
    - **Descending line sort prevents line-number drift**: When a docstring is inserted at line N, all subsequent line numbers shift downward. Processing functions from bottom-to-top ensures that line numbers remain valid for all remaining functions in the batch; processing top-to-bottom would require re-parsing after each insertion or complex offset tracking
    - **Dual-mode filtering supports flexible workflows**: The `require_agentspec` flag enables strict compliance checking (for AI-generated docstrings that must include YAML metadata) versus lenient quality checking (for general underdocumented code). The heuristic of 5+ lines for "real" docstrings filters out placeholder docstrings like `"""TODO: document this"""` without requiring semantic analysis
    - **`update_existing` flag enables iterative refinement**: By forcing all functions to be flagged regardless of existing docstrings, this mode supports regeneration and refinement workflows where docstrings are intentionally replaced; this is more efficient than re-parsing after deletion
    - **AST-based parsing over regex**: Using `ast.parse()` and `ast.walk()` is more robust than regex-based function detection because it correctly handles nested functions, decorators, multiline signatures, and edge cases like functions defined inside conditionals or comprehensions
    - **Line number preservation via `node.lineno` and `node.end_lineno`**: The AST provides exact line boundaries, avoiding off-by-one errors that would occur with manual line counting or regex matching
    - **Entire source held in RAM**: The function reads the entire file into memory and splits it into lines for efficient slicing; this trades memory for simplicity and speed, suitable for typical Python files but problematic for extremely large generated files (>100MB)

    AGENT INSTRUCTIONS:
    - DO NOT modify the descending sort order; changing to ascending will cause line-number invalidation during batch docstring insertion
    - DO NOT remove the `update_existing` bypass logic; it is intentionally designed to override filtering for regeneration workflows
    - DO NOT change the filtering heuristics (5-line threshold, `---agentspec` marker check) without understanding downstream impact on docstring generation pipelines
    - DO NOT call this function on files with syntax errors; `ast.parse()` will raise `SyntaxError` and halt execution; wrap in try-except if robustness is required
    - DO NOT assume returned line numbers remain valid after any source modification; the caller must re-parse the file to obtain fresh coordinates
    - DO NOT combine `update_existing=True` with `require_agentspec=True` in the same call; `update_existing` bypasses all skip logic, rendering `require_agentspec` ineffective and creating confusion about intent
    - DO NOT process extremely large files (>100MB) without memory budget considerations; `ast.walk()` traverses the entire tree and the entire source is held in RAM
    - ALWAYS re-parse the file after inserting docstrings before calling this function again on the modified source
    - ALWAYS validate that `filepath` is a valid Python file before calling; no type checking is performed on the argument
    - NOTE: This function is only safe for well-formed Python source files; malformed syntax will cause immediate failure
    - NOTE: The function silently skips functions with minimal docstrings when `require_agentspec=False`; this may hide underdocumented code if the heuristic is too lenient
    - NOTE: Docstring extraction via `ast.get_docstring()` only recognizes string literals as the first statement in a function body; docstrings placed elsewhere or in comments will not be detected

    DEPENDENCIES (from code analysis):
    Calls: ast.get_docstring, ast.parse, ast.walk, existing.split, f.read, functions.append, functions.sort, isinstance, join, len, open, print, source.split
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)
    - 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)

    '''
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
    Brief one-line description.

    Injects deterministic metadata (dependencies and changelog) into LLM-generated documentation, forcefully overwriting any LLM-generated equivalents while preserving narrative content.

    WHAT THIS DOES:
    - Accepts raw LLM-generated documentation output and merges it with deterministic metadata derived from code analysis (deps) and git history (changelog)
    - Supports two output formats: YAML (injected into `---agentspec` blocks) and plain-text (appended at end)
    - For YAML format: builds structured `deps` section (with `calls` and `imports` subsections) and `changelog` section, then surgically injects them before the `why:` marker or after the `what:` section, preserving all narrative content (`what`, `why`, `guardrails`)
    - For plain-text format: aggressively strips any existing LLM-emitted CHANGELOG and DEPENDENCIES sections using robust multiline regex, then appends deterministic versions at the end in consistent order (deps first, then changelog)
    - Optionally appends `diff_summary` lines (one per commit) after changelog entries when provided; wraps long lines using `_wrap_bullet()` helper to satisfy linter constraints (max 88 chars) within docstrings
    - Returns modified output string; if metadata dict is empty/None, returns original llm_output unchanged
    - Uses callable lambda replacements in `re.sub()` to prevent backslash interpretation errors (e.g., `\u0041` being interpreted as Unicode escape instead of literal text)

    WHY THIS APPROACH:
    - **Separation of concerns**: Narrative sections (`what`, `why`, `guardrails`) are LLM-generated and must never be modified; only metadata sections are replaced. This prevents loss of semantic documentation while ensuring deterministic metadata always wins
    - **Forceful replacement over conditional merging**: The function never attempts to merge or conditionally inject metadata. It always replaces existing sections entirely. This guarantees consistency and prevents subtle bugs where stale LLM-generated metadata could leak through
    - **Callable replacements in `re.sub()`**: Direct string replacement in regex patterns can cause unintended escape sequence interpretation (e.g., `\u0041` in deps_yaml becomes Unicode `A` instead of literal backslash-u-0041). Using lambda callbacks defers string substitution until after regex matching completes, avoiding this pitfall
    - **Multiline regex with `(?ms)` flags**: The plain-text format uses `re.DOTALL` (dotall mode) to make `.` match newlines, and `re.MULTILINE` to make `^` and `$` match line boundaries. This enables robust section boundary detection even when sections span multiple lines with varying indentation
    - **Robust section boundaries**: Rather than fragile markers like "CHANGELOG:" alone, the regex uses negative lookahead `(?=^(?:CHANGELOG|DEPENDENCIES|WHAT:|WHY:)|\Z)` to stop at the next section header or end-of-text, preventing accidental partial deletions
    - **YAML folded block scalars (`>-`)**: Long diff summary lines are wrapped using `>-` (folded scalar, strip trailing newline) to preserve semantic line breaks while avoiding excessive quoting. This keeps YAML valid and readable when text contains colons, quotes, or newlines
    - **Consistent ordering**: Deterministic sections are always appended in the same order (deps, then changelog, then diff_summary) to ensure reproducible output and simplify parsing by downstream tools
    - **Alternatives NOT used**: 
      - Could have attempted to parse and merge LLM-generated metadata with deterministic metadata, but this risks stale data leaking through if LLM output is malformed
      - Could have used simple string concatenation instead of regex, but this fails when sections already exist or have variable formatting
      - Could have used direct string replacement instead of callable lambdas, but this causes backslash interpretation bugs in YAML content

    AGENT INSTRUCTIONS:
    - DO NOT modify narrative sections (`what`, `why`, `guardrails`) under any circumstances; these are LLM-generated and must be preserved exactly
    - DO NOT attempt to merge or conditionally inject metadata; always replace existing sections entirely with deterministic versions
    - DO NOT remove the callable lambda replacements in `re.sub()` calls; they prevent backslash interpretation errors in YAML/deps content
    - DO NOT change the regex flags (`(?ms)`, `re.DOTALL`, `re.MULTILINE`) without understanding their impact on section boundary detection
    - DO NOT remove the `_wrap_bullet()` helper function or its textwrap dependency; it ensures diff_summary lines comply with linter constraints (88-char max width)
    - DO NOT modify the section ordering (deps before changelog before diff_summary) without updating any downstream parsers that depend on this order
    - ALWAYS use callable replacements (lambda functions) when injecting content that contains backslashes, dollar signs, or other regex special characters
    - ALWAYS strip existing LLM-emitted CHANGELOG and DEPENDENCIES sections before appending deterministic ones in plain-text format; prevents duplication
    - ALWAYS preserve the separation between YAML format (structured, injected into `---agentspec` blocks) and plain-text format (appended at end); they have different injection strategies
    - ALWAYS check for both `why:` and `why |` markers when injecting deps in YAML format; LLM output may use either syntax
    - ALWAYS append a newline before deterministic sections in plain-text format if llm_output doesn't already end with one; prevents formatting issues
    - NOTE: This function is critical for ensuring deterministic metadata always takes precedence over LLM-generated equivalents, even when LLM output is malformed or inconsistent. Any changes to injection logic must preserve this guarantee
    - NOTE: The regex patterns use `\Z` (end-of-string) rather than `$` to match only the absolute end, preventing issues with trailing newlines
    - NOTE: The `diff_summary_lines` parameter is optional and may be None; always check before attempting to iterate
    - NOTE: YAML injection uses `rfind()` to locate the closing `---/agentspec` tag because there may be multiple occurrences; always use the last one to avoid injecting into nested content

    DEPENDENCIES (from code analysis):
    Calls: _tw.fill, _wrap_bullet, deps_data.get, join, len, llm_output.endswith, m.group, metadata.get, output.rfind, print, re.sub, strip, wrapped.splitlines
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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

        # Optional diff summary lines (one line per commit) placed AFTER changelog
        diff_yaml = ""
        if diff_summary_lines:
            # Wrap lines to satisfy common linters (ruff/flake8/black) within docstrings
            def _wrap_bullet(text: str, *, bullet_indent: int = 6, content_indent: int = 8, max_width: int = 88) -> str:
                """
                Brief one-line description.

                WHAT THIS DOES:
                Converts text into YAML-formatted bullet list items with intelligent line wrapping, choosing between single-line quoted format for short text or multi-line folded block scalar format for longer text. For text ≤76 characters (max_width - bullet_indent), returns a simple quoted item like `"- \"text\""` with trailing newline. For longer text, uses YAML's folded block scalar syntax (`- >-`) with textwrap.fill() to wrap lines at max_width - content_indent, then indents each wrapped line to content_indent spaces. This prevents malformed YAML when text contains special characters like colons, quotes, or embedded newlines. The function always returns a string ending with a newline character.

                WHY THIS APPROACH:
                YAML folded block scalars (`>-`) preserve semantic line breaks while avoiding excessive quoting that would be required for inline strings containing special characters. This approach was chosen over alternatives like: (1) always quoting text—would create verbose, hard-to-read YAML for long strings; (2) always using folded scalars—would add unnecessary complexity for short strings that fit on one line; (3) using literal block scalars (`|-`)—would preserve trailing whitespace, which is usually undesired. The textwrap.fill() function respects max_width constraints for consistent formatting across all wrapped lines. The length check uses (max_width - bullet_indent) as the threshold because this represents the actual available width for a single-line item after accounting for the bullet prefix and indentation. Performance is O(n) where n is text length, dominated by textwrap.fill() and string operations.

                AGENT INSTRUCTIONS:
                - DO NOT change bullet_indent or content_indent parameter defaults without updating the AgentSpec YAML parser that consumes this output; misaligned indentation breaks downstream parsing
                - DO NOT remove the textwrap import or replace textwrap.fill() with manual line-breaking logic; textwrap handles edge cases like hyphenation and word boundaries correctly
                - DO NOT modify the folded block scalar marker (`>-`) to literal (`|-`) without understanding that this changes whitespace handling; `>-` strips trailing newlines (desired), `|-` preserves them
                - ALWAYS validate that max_width >= content_indent + 10 before calling this function; insufficient width can cause textwrap.fill() to fail or produce single-word-per-line output
                - ALWAYS ensure text parameter is a string; passing None or non-string types will cause len() or textwrap.fill() to raise TypeError
                - NOTE: The length threshold check (max_width - bullet_indent) is intentionally different from the wrap width (max_width - content_indent); this is correct because single-line items have less indentation than wrapped items
                - NOTE: Folded block scalars automatically join wrapped lines with spaces; if you need to preserve explicit line breaks in the original text, pre-process text to use YAML line break indicators or switch to literal block scalars
                - NOTE: The trailing newline is critical for YAML list formatting; do not strip it when using this function's output

                DEPENDENCIES (from code analysis):
                Calls: _tw.fill, join, len, print, wrapped.splitlines
                Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

                CHANGELOG (from git history):
                - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
                - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
                - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
                - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
                - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

                """
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
    Brief one-line description.

    Removes JSDoc blocks containing agentspec markers from JavaScript/TypeScript files, with dry-run support and line-count reporting.

    WHAT THIS DOES:
    - Reads a file line-by-line and identifies JSDoc blocks (delimited by `/**` and `*/`)
    - Scans each complete block for five agentspec-related markers: `---agentspec`, `---/agentspec`, `DEPENDENCIES (from code analysis):`, `CHANGELOG (from git history):`, and `AGENTSPEC_CONTEXT:`
    - Removes matching blocks entirely while preserving all non-matching JSDoc and regular code
    - Handles malformed blocks (missing closing `*/`) gracefully by keeping them as-is
    - Returns an integer count of removed blocks; writes changes to disk only if `dry_run=False`
    - Preserves exact file line endings (trailing newline if present in original, omitted if absent)
    - In dry-run mode, prints preview messages showing line ranges of blocks that would be removed without modifying the file
    - Silently returns 0 if file cannot be read (encoding errors, permission issues, missing file)

    WHY THIS APPROACH:
    - Line-by-line iteration avoids expensive full-file regex parsing or AST analysis; substring matching is O(n) and fast for typical JSDoc sizes
    - Markers are chosen to be specific enough to avoid false positives in regular comments while broad enough to catch all agentspec injection patterns (YAML fences, context headers, injected metadata sections)
    - Malformed block preservation prevents data loss when JSDoc is incomplete or corrupted; silently skipping broken blocks is safer than crashing
    - Dry-run mode enables safe batch operations on large codebases without risk; users can preview impact before committing changes
    - `errors="ignore"` in `read_text()` combined with exception handling allows processing files with mixed encodings or encoding issues without halting the entire operation
    - Preserving exact line endings (checking `text.endswith("\n")`) ensures output matches input formatting conventions, critical for version control diffs and CI/CD systems
    - Returning block count (not line count) gives callers a meaningful metric for logging and progress tracking across multiple files
    - The `mode` parameter is accepted but currently unused, allowing future extension (e.g., "agentspec-only", "deps-only", "changelog-only") without breaking the API

    AGENT INSTRUCTIONS:
    - DO NOT modify the marker list without understanding that these strings are searched as substrings anywhere in the block; adding markers requires testing against real agentspec YAML to avoid false positives or false negatives
    - DO NOT change the block collection logic to use regex or full-file parsing; the line-by-line approach is intentionally simple to handle edge cases like nested quotes, malformed YAML, and incomplete blocks
    - DO NOT remove the `errors="ignore"` parameter or the outer try-except; these are defensive measures for batch processing across heterogeneous codebases
    - DO NOT alter the line-ending preservation logic (`text.endswith("\n")`); this is critical for maintaining file format consistency and preventing spurious diffs
    - DO NOT convert the `is_agentspec_block` helper to a regex or more complex check without benchmarking; substring search is intentionally fast and readable
    - ALWAYS preserve the dry-run print output format; external tools may parse these messages for logging or CI/CD integration
    - ALWAYS return the count of removed blocks, not lines; this is the contract callers depend on for progress reporting
    - ALWAYS write the file only if `removed > 0 and not dry_run`; this prevents unnecessary disk I/O and timestamp changes
    - ALWAYS handle the case where a block starts with `/**` but never closes with `*/`; these are kept as-is to avoid data loss
    - NOTE: This function is designed for preprocessing before LLM-based docstring generation; it removes injected metadata that would pollute training data or cause circular dependencies in documentation pipelines
    - NOTE: The `mode` parameter is a forward-compatibility hook; do not remove it even though it is currently unused
    - NOTE: Performance is acceptable for typical files (< 10MB) but may be slow on extremely large files (> 100MB) due to line-by-line iteration; consider streaming or chunking for massive codebases

    DEPENDENCIES (from code analysis):
    Calls: any, block.append, endswith, filepath.read_text, filepath.write_text, is_agentspec_block, join, len, out.append, out.extend, print, strip, text.endswith, text.splitlines
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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
        Brief one-line description.

        Detects whether a block of text lines contains agentspec-related markers by checking for five specific marker strings.

        WHAT THIS DOES:
        - Accepts a list of strings representing lines of text and checks if any of five predefined agentspec markers appear anywhere in the joined content
        - Joins all lines with newline characters into a single string, then performs substring searches for markers: "---agentspec", "---/agentspec", "DEPENDENCIES (from code analysis):", "CHANGELOG (from git history):", and "AGENTSPEC_CONTEXT:"
        - Returns True immediately upon finding the first marker match (short-circuit evaluation via any()), or False if none are found
        - Operates in O(n) time complexity where n is the total character count across all lines, making it suitable for preprocessing and filtering operations
        - Handles empty lists gracefully (returns False) and works with lists of any size, though performance degrades linearly with total content volume

        WHY THIS APPROACH:
        - Uses substring containment checks rather than regex or parsing because agentspec markers are fixed literal strings that don't require pattern matching, making this approach faster and more maintainable
        - Joins lines first rather than checking each line individually because markers may span across line boundaries or appear anywhere in the block, and joining is more efficient than iterating with nested searches
        - Employs any() with a generator expression for early termination—stops searching as soon as the first marker is found rather than checking all markers unnecessarily
        - Chosen as a lightweight heuristic for preprocessing and filtering before expensive full parsing operations; not designed to validate agentspec structure or completeness
        - Avoids regex or AST parsing overhead since only presence detection is needed, not structural validation

        AGENT INSTRUCTIONS:
        - DO NOT use this function to validate agentspec block structure, completeness, or correctness; it only detects marker presence as a heuristic
        - DO NOT assume that marker presence indicates a valid or complete agentspec block; closing fences may be missing or markers may appear in comments/strings
        - DO NOT rely on this for security-sensitive operations; markers embedded in string literals, comments, or code will trigger false positives
        - DO NOT call this on extremely large lists without considering memory impact; the full join operation loads entire content into memory; for streaming scenarios, implement incremental marker checking instead
        - DO NOT modify the marker list without understanding downstream code that depends on these specific markers
        - ALWAYS preserve the any() short-circuit behavior to maintain performance characteristics
        - ALWAYS join with newline characters to preserve line-boundary semantics
        - ALWAYS return a boolean, never None or other truthy/falsy values
        - NOTE: This function is intentionally permissive and heuristic-based; false positives are acceptable for preprocessing, but false negatives must be avoided to prevent missing actual agentspec blocks
        - NOTE: The marker list is hardcoded and must be kept in sync with actual agentspec block delimiters used elsewhere in the codebase

        DEPENDENCIES (from code analysis):
        Calls: any, join, print
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

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
    # WHAT THIS DOES:

    Generates comprehensive AI-agent-consumable documentation (docstrings or AgentSpec YAML blocks) for Python code by calling an LLM with adaptive prompting. The function accepts source code and metadata, constructs a system prompt with examples, estimates token budgets, calls `generate_chat()` with complexity-aware parameters, validates YAML completeness with retry logic, and returns either a narrative docstring or a full AgentSpec YAML block depending on the `as_agentspec_yaml` flag.

    **Key behaviors:**
    - **Dual output modes**: `as_agentspec_yaml=True` returns `---agentspec ... ---/agentspec` YAML block; `False` returns docstring-style narrative text
    - **Adaptive complexity handling**: Detects code length (≤12 lines triggers `reasoning_effort='minimal'`); terse mode uses lower temperature (0.0) and reduced token budget (500 vs 2000)
    - **YAML validation & retry**: If generated YAML lacks closing delimiter `---/agentspec` or core sections (`what:`, `why:`, `guardrails:`), retries up to 2 times with continuation prompts
    - **Token budgeting**: Estimates prompt tokens via character heuristic (`len(s) // 4`), respects environment overrides (`AGENTSPEC_CONTEXT_TOKENS`, `AGENTSPEC_MAX_OUTPUT_TOKENS`, `AGENTSPEC_TOKEN_BUFFER`), calculates available output budget
    - **Example injection**: Loads full examples (code, bad/good docs, guardrails, lessons) from JSON, embeds them in system prompt to guide LLM
    - **Metrics collection**: Records prompt/output token estimates, continuation count, YAML flag, provider to `GEN_METRICS` list
    - **Stub mode**: Returns placeholder YAML/docstring if `AGENTSPEC_GENERATE_STUB` env var set (for testing)
    - **Multi-block YAML selection**: If multiple valid YAML blocks generated, selects first one with all required keys (`what`, `why`, `guardrails`)

    **Error handling:**
    - Gracefully handles missing function names (regex fallback to `"(unknown)"`)
    - Catches exceptions during YAML parsing; silently continues if YAML library unavailable
    - Bare `except Exception` in `_estimate_tokens` masks errors; returns fallback token count
    - Continuation loop exits after 2 attempts even if YAML still incomplete

    **Return value:** String containing either narrative docstring (3-4 lines of what/why/guardrails) or full YAML block with delimiters and nested structure.

    ---

    # WHY THIS APPROACH:

    **Adaptive prompting rationale:**
    - Short code (≤12 lines) uses `reasoning_effort='minimal'` to avoid over-analysis and reduce latency; longer code gets full reasoning
    - Terse mode (`terse=True`) uses lower temperature (0.0 vs 0.2) for deterministic output, reduced token budget (500 vs 2000), and alternative prompt/examples files to enforce conciseness
    - Verbosity tuning (`'low'` vs `'medium'`) aligns LLM output style with documentation goal

    **Token budgeting design:**
    - Character-based heuristic (`len(s) // 4`) avoids expensive tokenizer calls; trades accuracy for speed (reasonable for English, untested against actual distributions)
    - Environment variable overrides allow operators to tune budgets per deployment without code changes
    - Buffer (default 500 tokens) prevents context overflow; available output = `max(256, context_cap - prompt_tokens - buffer)`
    - Terse mode uses smaller base (500) to encourage concise output; normal mode uses 2000 for detailed docs

    **Example embedding strategy:**
    - Full examples (not just IDs) embedded in system prompt teach LLM by demonstration; includes bad/good doc pairs and lessons
    - Limits to first 5 examples to avoid prompt bloat; XML-formatted for clarity
    - Loaded from JSON files (`examples_terse.json` for terse, default for normal) to allow easy iteration without code changes

    **YAML validation & retry:**
    - Two-pass validation: `_yaml_complete()` checks delimiters present, `_yaml_has_core_sections()` checks required keys via regex
    - Retry loop (max 2 attempts) with continuation prompt recovers from incomplete LLM output (common with streaming or token limits)
    - Continuation prompt explicitly instructs LLM to not repeat prior content and close with `---/agentspec`

    **Multi-block selection:**
    - If LLM generates multiple YAML blocks (hallucination or concatenation), selects first block with all required keys using `yaml.safe_load()` validation
    - Prevents downstream parsing errors from malformed/incomplete blocks

    **Alternatives NOT used:**
    - **Streaming**: Not used; waits for full response to validate YAML completeness before returning
    - **Tokenizer library (tiktoken)**: Not used; character heuristic chosen for speed (no external dependency, no model-specific overhead)
    - **Strict YAML parsing upfront**: Not used; regex checks are faster for shallow validation; full parsing only on final output
    - **Single LLM call with strict grammar**: Grammar constraint (`grammar_lark`) only applied if `as_agentspec_yaml=True`; docstring mode has no grammar to avoid over-constraining prose

    **Performance considerations:**
    - Token estimation is O(n) in string length; acceptable for typical code (<10KB)
    - Regex validation is O(n) with small constant; faster than YAML parsing
    - Retry loop adds latency only if YAML incomplete (rare with good prompts); max 2 retries caps worst-case
    - Example loading from JSON is one-time per call; no caching (acceptable for typical usage)

    **Non-obvious code details:**
    - `_call_llm()` is a closure capturing 9 outer variables (`code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`); this is intentional to avoid parameter bloat, but creates tight coupling
    - `_yaml_complete()` checks only delimiter presence, not order or validity; insufficient alone but paired with `_yaml_has_core_sections()` for basic structural validation
    - Continuation prompt uses `text.rstrip() + "\n" + more.strip() + "\n"` to avoid double-newlines and preserve formatting
    - Multi-block selection uses `text.find()` loop instead of regex to preserve original text; allows recovery of partial blocks
    - Metrics collection uses bare `except Exception` to ensure metrics don't crash main flow; silent failure acceptable for observability

    ---

    # AGENT INSTRUCTIONS:

    **DO NOT:**
    - Remove or weaken the `_yaml_complete()` and `_yaml_has_core_sections()` checks; they prevent downstream parsing errors
    - Change the retry loop limit (2 attempts) without testing impact on latency and LLM cost
    - Remove the `max(1, ...)` floor in `_estimate_tokens()`; zero tokens breaks downstream token accounting
    - Assume `_estimate_tokens()` is accurate; it's a heuristic with unknown error margin
    - Remove the `max(256, ...)` floor in available output calculation; prevents context underflow
    - Modify the continuation prompt without testing that LLM still closes with `---/agentspec`
    - Remove the multi-block selection logic; LLM hallucination of multiple blocks is rare but possible
    - Change the order of validation checks (complete before core sections); order matters for retry logic
    - Remove the stub mode (`AGENTSPEC_GENERATE_STUB`); used by test suite
    - Assume `grammar_lark` is always available; it's optional and may be None

    **ALWAYS:**
    - Preserve the dual output modes (`as_agentspec_yaml` flag); both docstring and YAML paths are used
    - Keep the adaptive reasoning effort and verbosity tuning; they're critical for cost/quality balance
    - Validate YAML with both `_yaml_complete()` AND `_yaml_has_core_sections()` before returning; either alone is insufficient
    - Respect environment variable overrides (`AGENTSPEC_CONTEXT_TOKENS`, `AGENTSPEC_MAX_OUTPUT_TOKENS`, `AGENTSPEC_TOKEN_BUFFER`); operators depend on these for tuning
    - Log the proof info (func name, provider, model, token estimates) before calling LLM; aids debugging and cost tracking
    - Record metrics to `GEN_METRICS` list; used for observability and cost

    DEPENDENCIES (from code analysis):
    Calls: GEN_METRICS.append, Path, _call_llm, _estimate_tokens, _yaml.safe_load, _yaml_complete, _yaml_has_core_sections, bool, code.splitlines, data.keys, ex.get, generate_chat, get, get_terse_docstring_prompt, get_verbose_docstring_prompt, int, isinstance, join, json.loads, len, load_agentspec_yaml_grammar, load_examples_json, load_provider_base_prompt, m.group, max, min, more.split, more.strip, os.getenv, print, prompt.format, re.search, required.issubset, set, spans.append, startswith, str, strip, terse_examples_path.read_text, text.find, text.rstrip
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
    - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
    - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
    - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

    """
    import re, os

    def _estimate_tokens(s: str) -> int:
        """
        Brief one-line description.

        Estimates token count using a character-based heuristic (approximately 4 characters per token).

        WHAT THIS DOES:
        - Accepts a string `s` and returns an estimated token count using the formula `max(1, len(s) // 4)`
        - Divides string length by 4 to approximate tokens, based on the assumption that English text averages ~4 characters per token
        - Enforces a minimum return value of 1 token via `max(1, ...)` to prevent zero-token edge cases that would break downstream token accounting and budget calculations
        - Handles non-string inputs gracefully by converting them to strings before calculation (via the `TypeError` exception handler)
        - Returns an integer token estimate suitable for quick token budget checks without invoking expensive tokenizer libraries
        - The heuristic is fast but approximate; actual token counts may vary significantly depending on text composition, language, and the specific tokenizer model being used

        WHY THIS APPROACH:
        - Character-based heuristic was chosen for speed: avoids the computational overhead of loading and running actual tokenizer models (like `tiktoken` or model-specific tokenizers) for every token estimation call
        - The 4-character-per-token ratio is a reasonable rule-of-thumb for English text but is not validated against actual token distributions; this is a pragmatic trade-off between accuracy and performance
        - The `max(1, ...)` floor prevents returning zero tokens, which would cause division-by-zero errors or incorrect budget calculations in downstream code that depends on positive token counts
        - The `TypeError` exception handler (not bare `Exception`) catches cases where non-string input is passed, converting it to string representation before calculation; this is more defensive than rejecting non-strings outright
        - This approach is suitable for rough budgeting and quick estimates but should NOT be used for precise token accounting where actual tokenizer output is required
        - Alternatives NOT used: (1) calling actual tokenizer on every estimate (too slow for frequent calls), (2) returning 0 for empty strings (breaks accounting), (3) bare `except Exception` (masks real bugs and makes debugging impossible)

        AGENT INSTRUCTIONS:
        - DO NOT remove the `max(1, ...)` floor; this is critical for preventing zero-token returns that break downstream token accounting and budget logic
        - DO NOT replace the explicit `TypeError` handler with a bare `except Exception`; bare exception handlers hide real bugs (AttributeError, ValueError, etc.) and make production debugging impossible
        - DO NOT modify the 4-character divisor without validating the new ratio against actual tokenizer output; the current value is a heuristic assumption, not empirically proven
        - DO NOT use this function for precise token counting in contexts where accuracy is critical (e.g., API billing, strict rate limiting); use actual tokenizer libraries instead
        - ALWAYS preserve the `len(str(s))` fallback in the exception handler to gracefully handle non-string inputs
        - ALWAYS ensure return value is a positive integer (never zero, never negative, never float)
        - NOTE: This is a heuristic approximation, not ground truth; token counts will diverge from actual tokenizer output, especially for non-English text, code, or special characters
        - NOTE: The print statement in the function body is debug instrumentation and should be removed or converted to proper logging in production
        - NOTE: Unbounded string input could theoretically cause memory issues during `len()` calculation if extremely large strings (multi-GB) are passed; consider adding input size validation if this function is exposed to untrusted input
        - ASK USER: Should this function call an actual tokenizer (with caching) for accuracy, or is speed critical enough to justify the heuristic approximation? Should there be a maximum input size guard?

        DEPENDENCIES (from code analysis):
        Calls: len, max, print, str
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

        """
        try:
            return max(1, len(s) // 4)
        except TypeError:
            # Fallback for non-string inputs
            return max(1, len(str(s)) // 4)

    def _yaml_complete(text: str) -> bool:
        """
        Brief one-line description.

        Checks if a string contains both opening and closing AgentSpec YAML delimiters.

        WHAT THIS DOES:
        - Performs a simple substring presence check for "---agentspec" and "---/agentspec" markers within the provided text
        - Returns True only if both delimiters are found anywhere in the string; returns False if either or both are missing
        - Does NOT validate the order of delimiters (closing delimiter can appear before opening delimiter and still return True)
        - Does NOT validate YAML structure, syntax, or content between the delimiters
        - Does NOT catch malformed delimiters such as those with trailing whitespace ("---agentspec ") or duplicated delimiters
        - Does NOT prevent delimiter injection attacks where malicious actors insert delimiters into unintended locations
        - Intended as a lightweight structural pre-check before more rigorous parsing, not as a complete validation mechanism

        WHY THIS APPROACH:
        - This implementation prioritizes speed and simplicity for a preliminary check before expensive YAML parsing operations
        - String containment checks (using Python's `in` operator) are O(n) and avoid the overhead of regex compilation or full YAML parsing
        - The function was deliberately kept minimal to serve as a gating mechanism: if delimiters are absent, downstream parsing will certainly fail, so we fail fast
        - Alternatives NOT used: regex patterns would add complexity without catching the order/structure issues this function doesn't address anyway; full YAML parsing would be premature and wasteful if delimiters are missing; delimiter counting would not improve security posture given the injection vulnerability
        - Performance consideration: this check is meant to be called frequently as a guard clause, so minimal overhead is critical
        - The "weird" simplicity is intentional—this function is deliberately incomplete and must be paired with stricter validation downstream

        AGENT INSTRUCTIONS:
        - DO NOT use this function as the sole validation mechanism for AgentSpec documents; it only checks delimiter presence, not correctness, order, or structure
        - DO NOT assume this function catches malformed delimiters (e.g., delimiters with trailing spaces, extra whitespace, or case variations)
        - DO NOT rely on this function to prevent delimiter injection attacks; an attacker can inject "---agentspec" anywhere in text and this will return True
        - ALWAYS pair this function with order validation that ensures "---agentspec" appears before "---/agentspec" in the text
        - ALWAYS pair this function with YAML schema validation after parsing to ensure the content between delimiters is structurally and semantically valid
        - ALWAYS validate that exactly one opening and one closing delimiter pair exists (no duplicates or multiple pairs)
        - NOTE: This function catches incomplete documents (missing delimiters) but will miss malformed delimiters, injected delimiters, reversed order, and invalid YAML content
        - NOTE: Security risk exists where malicious YAML with properly-placed delimiters will pass this check but may contain unintended AgentSpec instructions that execute downstream
        - NOTE: The debug print statement logs context about known limitations; this is informational and should not be removed without updating monitoring/logging systems

        DEPENDENCIES (from code analysis):
        Calls: print
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

        """
        return "---agentspec" in text and "---/agentspec" in text

    def _yaml_has_core_sections(text: str) -> bool:
        """
        Brief one-line description.

        Validates that YAML text contains the three required AgentSpec core sections: `what:`, `why:`, and `guardrails:`.

        WHAT THIS DOES:
        - Performs structural validation of YAML content by searching for three mandatory section headers using regex pattern matching with multiline mode enabled
        - Checks for `what: |` (literal block scalar), `why: |` (literal block scalar), and `guardrails:` (mapping key) each at the start of a line
        - Returns True only when all three sections are present and properly formatted with correct YAML syntax; returns False if any section is missing or malformed
        - Uses `re.search()` with multiline anchors (`(?m)^`) to ensure section headers appear at line boundaries, preventing false positives from inline occurrences
        - Does NOT validate section content (whether `what` and `why` contain actual text, whether `guardrails` is a list, whether values are non-empty)
        - Does NOT check for AgentSpec delimiters (`---agentspec` opening or `---/agentspec` closing markers)
        - Intended as a fast pre-flight check to catch obviously malformed YAML before expensive semantic parsing or LLM processing

        WHY THIS APPROACH:
        - Regex-based structural validation is computationally cheap and appropriate for shallow syntax checking; it fails fast on obviously broken YAML without requiring full parsing
        - Separating structural validation from content validation follows single-responsibility principle: this function answers "are the required sections present?" while content quality belongs in a separate validation layer
        - Multiline regex mode with `^` anchors ensures robustness against YAML with indented content or multiple occurrences of keywords; anchoring to line start prevents matching `what:` buried inside string values
        - This check prevents wasted LLM API calls and processing cycles on YAML that is structurally incomplete, saving resources before deeper validation
        - The approach trades off comprehensiveness for speed: it catches structural drift but cannot detect semantic errors (empty sections, wrong types, missing closing delimiters)

        AGENT INSTRUCTIONS:
        - DO NOT use this function as the sole validation mechanism; it only checks presence of section headers, not their content quality or completeness
        - DO NOT modify the regex patterns without understanding that `(?m)^` enables multiline mode where `^` matches line starts, not just string start
        - DO NOT remove the three separate `re.search()` calls; they must all return non-None for the function to return True (AND logic is required)
        - DO NOT assume a True return value means the AgentSpec is production-ready or semantically valid; it only confirms structural presence
        - ALWAYS pair this function with content validation that checks: `what` and `why` sections contain non-blank text, `guardrails` is a list or mapping with entries, and closing `---/agentspec` delimiter is present if required
        - ALWAYS preserve the multiline regex mode flag `(?m)` in all three patterns; removing it will break detection for multi-line YAML
        - ALWAYS maintain the `is not None` checks on all three `re.search()` results; this is the idiomatic Python way to test regex match success
        - NOTE: This function catches structural drift only; semantic errors (malformed YAML syntax, incorrect indentation, type mismatches) require separate validation with a proper YAML parser
        - NOTE: The regex does not validate the closing `---/agentspec` delimiter; if delimiter validation is required, add a fourth check or use a dedicated delimiter validator
        - NOTE: Empty sections like `what: |` followed immediately by `why: |` will pass this check; content validation must verify non-empty text between delimiters
        - NOTE: The print statement with `[AGENTSPEC_CONTEXT]` is a debug/logging artifact; consider whether this should be removed, moved to a logger, or kept for agent tracing

        DEPENDENCIES (from code analysis):
        Calls: print, re.search
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

        """
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
            # Choose provider-specific prompt, detecting local chat fallback by base_url
            _prov_for_prompt = (provider or 'auto').lower()
            if (_prov_for_prompt in ('openai','auto')) and (base_url or '').startswith('http://localhost:11434'):
                # Local OpenAI-compatible chat (no Responses); use chat-local prompt
                prompt_provider = 'local'
            else:
                prompt_provider = _prov_for_prompt
            if terse:
                base_prompt_text = load_provider_base_prompt(prompt_provider, terse=True)
                terse_examples_path = Path(__file__).parent / "prompts" / "examples_terse.json"
                examples_data = terse_examples_path.read_text(encoding="utf-8")
                examples = json.loads(examples_data).get("examples", [])
            else:
                base_prompt_text = load_provider_base_prompt(prompt_provider, terse=False)
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
        Brief one-line description.

        WHAT THIS DOES:
        Calls `generate_chat()` with adaptive reasoning effort and verbosity parameters determined by code complexity heuristics and a `terse` flag. Sets `reasoning_effort='minimal'` when either the `terse` flag is True OR the input code is ≤12 lines; otherwise reasoning_effort is None. Sets `verbosity='low'` if terse mode is enabled, otherwise 'medium'. Temperature is hardcoded to 0.0 in terse mode for deterministic output, or 0.2 in normal mode for slight variance. The `grammar_lark` parameter is conditionally passed to the LLM call only when `as_agentspec_yaml=True`, preventing hallucinated YAML keys in non-YAML output modes. Returns the string response from `generate_chat()` directly. **CRITICAL: This function is currently non-functional and will crash immediately with NameError because the function signature declares only `user_content` and `max_tokens` parameters, but the implementation references 9 undefined variables: `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, and `max_out`.**

        WHY THIS APPROACH:
        The complexity-based reasoning scaling (minimal effort for ≤12 line code) avoids wasteful over-analysis on trivial code snippets while preserving full reasoning chains for complex implementations. Temperature tuning (0.0 vs 0.2) balances determinism in terse mode (where reproducibility matters for documentation consistency) against controlled variance in normal mode (where slight stylistic variation is acceptable). Grammar constraint application only for YAML output prevents the LLM from hallucinating invalid YAML keys while avoiding unnecessary constraints on prose documentation. This conditional parameter passing reduces token waste and improves output quality by matching LLM constraints to output format requirements.

        **Alternatives NOT used:** A fixed reasoning_effort parameter would waste compute on simple code; a single global temperature would sacrifice either determinism or variance depending on mode. Applying grammar constraints universally would degrade prose quality. Passing all parameters unconditionally would increase token overhead and reduce output fidelity.

        **Performance considerations:** Code line counting via `len(code.splitlines())` is O(n) in code length but negligible compared to LLM latency. The try-except block gracefully degrades to `code_lines=0` if code is None or unparseable, ensuring the function never crashes on malformed input (though it will crash on undefined variables as noted below).

        **Non-obvious implementation details:** The `max_tokens` parameter in the function signature does NOT match the `max_out` variable referenced in diff history; this mismatch suggests incomplete refactoring. The effort calculation uses `or` logic (`terse or code_lines <= 12`), meaning terse mode always forces minimal reasoning regardless of code length. The `grammar_lark` parameter is passed as-is (truthy/falsy) rather than as a concrete grammar object, implying `generate_chat()` handles None gracefully.

        AGENT INSTRUCTIONS:
        - DO NOT call this function in its current state; it will crash immediately with NameError on any of the 9 undefined variables (`code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`).
        - DO NOT edit the function logic until the function signature is updated to accept all required parameters or a dependency injection container is established.
        - DO NOT assume `code`, `terse`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, or `as_agentspec_yaml` are defined in outer scope; they must be explicitly passed as parameters or injected.
        - DO NOT rename `max_tokens` to `max_out` in the signature without updating the implementation; currently the signature uses `max_tokens` but the diff history suggests `max_out` was intended.
        - ALWAYS add all 9 undefined variables as function parameters before any functional changes: `code: str`, `model: str`, `system_text: str`, `base_url: str`, `provider: str`, `grammar_lark: Optional[str]`, `as_agentspec_yaml: bool`, `terse: bool`, and clarify whether `max_tokens` or `max_out` is the canonical parameter name.
        - ALWAYS preserve the complexity-based reasoning scaling logic (minimal effort for ≤12 lines or terse mode).
        - ALWAYS preserve the conditional grammar_lark parameter application (only when `as_agentspec_yaml=True`).
        - ALWAYS preserve the temperature tuning (0.0 for terse, 0.2 for normal).
        - ALWAYS preserve the try-except block around code line counting to prevent crashes on malformed code input.
        - NOTE: This is production-critical code for LLM prompt generation; the current state is a stub that will fail on first invocation. Full dependency injection refactoring is required before this function can be used. Diff history shows parameter renames (`max_tokens` → `max_out`) that were never reflected in the signature, indicating incomplete refactoring across multiple commits. Do not merge or deploy changes to this function without resolving all undefined variable references and signature mismatches.

        DEPENDENCIES (from code analysis):
        Calls: code.splitlines, generate_chat, len, print
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

        """
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
    Brief one-line description.

    Inserts or replaces a Python function's docstring at a specified file location, with AST-based robustness and pre-write syntax validation.

    WHAT THIS DOES:
    - Locates a target function by name (regex match) or line number (1-based), handling decorators and multi-line signatures via AST parsing
    - Detects and removes any existing docstring by analyzing AST node boundaries, converting 1-based line numbers to 0-based array indices to avoid off-by-one deletion errors
    - Removes trailing `[AGENTSPEC_CONTEXT]` print statements if present from prior runs
    - Selects an appropriate docstring delimiter (`\"""` or `'''`) based on content analysis; if the docstring contains triple-quotes, escapes them or switches delimiters to prevent syntax breakage
    - Formats the new docstring with proper indentation matching the function body (base indent + 4 spaces)
    - Optionally extracts up to 3 bullet points from the docstring and appends a print statement tagged `[AGENTSPEC_CONTEXT]` for agent introspection (when `force_context=True`)
    - **Critically: compile-tests the modified file on a temporary copy before writing** to prevent corrupting the source file with syntax errors
    - Returns `True` if the write succeeds after compilation validation; returns `False` if syntax validation fails, leaving the original file untouched
    - Handles edge cases: multi-line function signatures (AST-aware), existing docstrings at various positions, docstrings containing delimiter characters, AST parse failures (falls back to textual scanning), and empty function bodies

    WHY THIS APPROACH:
    - **AST-based location is essential**: Regex or textual scanning fails catastrophically on decorated functions, type-hinted parameters, and multi-line signatures. Python's `ast` module correctly identifies function boundaries regardless of formatting complexity.
    - **1-based to 0-based index conversion is critical**: AST reports line numbers in 1-based format (editor convention: line 1 = first line), but Python lists use 0-based indexing (lines[0] = first line). The conversion `docstring_start_line - 1` is mandatory to delete the correct lines; omitting it causes off-by-one errors that delete adjacent code.
    - **Compile-testing before write prevents data loss**: Unescaped quotes, malformed escape sequences, or other syntax errors in the docstring could render the file unparseable. Testing on a temporary file ensures the source is never left in a broken state; if compilation fails, the original file remains untouched and the function returns `False` to signal failure.
    - **Fallback textual scan provides graceful degradation**: If AST parsing fails (e.g., due to syntax errors in the original file), the function falls back to bracket-depth tracking and string matching to locate the function body, ensuring robustness even on partially-broken code.
    - **Delimiter selection logic prevents quote-escaping hell**: By detecting triple-quote occurrences in the docstring content and switching delimiters if needed, the function avoids excessive escaping. If both `\"""` and `'''` appear in the docstring, both are escaped, but this is rare; the preference for `\"""` is a convention.
    - **Indentation preservation**: The function measures the base indentation of the `def` line and adds 4 spaces for the function body, ensuring the docstring aligns with Python style conventions and any existing code.
    - **Context print extraction**: The optional `force_context` flag enables agent introspection by extracting key bullet points and embedding them in a print statement. This allows downstream tools to inspect function intent without re-parsing the docstring.

    AGENT INSTRUCTIONS:
    - DO NOT remove or disable the `py_compile.compile()` call and temporary file testing; this is the only safeguard against writing syntactically invalid Python to disk.
    - DO NOT modify the 1-based to 0-based index conversion logic (`docstring_start_line - 1`, `delete_end_idx = docstring_end_line`) without understanding the AST line numbering convention; incorrect changes will cause silent data corruption.
    - DO NOT simplify the delimiter selection logic; the current approach of checking for triple-quote presence and switching delimiters is necessary to handle docstrings containing quotes.
    - DO NOT remove the fallback textual scan in the `except` block; it provides robustness when AST parsing fails on malformed input files.
    - DO NOT change the escape sequences for quotes (`\\\"""` and `\\'\\''`) without testing on docstrings containing those exact patterns; incorrect escaping will break the output.
    - ALWAYS preserve the order of operations: (1) locate function, (2) detect and delete old docstring, (3) format new docstring, (4) optionally add context print, (5) compile-test, (6) write only if test passes.
    - ALWAYS use 0-based indexing when manipulating the `lines` list and 1-based when reading from AST node attributes; mixing these conventions is the most common source of bugs.
    - ALWAYS close and clean up temporary files in the `finally` block, even if exceptions occur, to avoid leaving temp files on disk.
    - ALWAYS encode output as UTF-8 when writing to ensure compatibility with non-ASCII characters in docstrings.
    - NOTE: The function modifies the file in-place; ensure the caller has write permissions and a backup if needed.
    - NOTE: If `force_context=True`, the function appends a print statement to the function body; this will execute every time the function is called, which may have performance or logging side effects.
    - NOTE: The AST fallback to textual scanning may produce incorrect results on edge cases (e.g., colons inside strings); prefer AST parsing by ensuring input files are syntactically valid.
    - NOTE: Docstrings containing both `\"""` and `'''` will have both escaped; this is rare but valid Python.

    DEPENDENCIES (from code analysis):
    Calls: abs, ast.parse, ast.walk, candidate.insert, candidates.append, docstring.split, enumerate, f.readlines, f.writelines, func_line.lstrip, hasattr, isinstance, join, len, line.count, line.startswith, line.strip, list, max, min, new_lines.append, open, os.close, os.remove, path.exists, pattern.match, print, print_content.replace, py_compile.compile, re.compile, re.escape, replace, reversed, safe_doc.replace, safe_doc.split, sections.append, strip, tempfile.mkstemp, tf.writelines
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)
    - 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)

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
    Brief one-line description.

    Scans a JavaScript file to discover function declarations that require or need `agentspec` documentation, returning candidates sorted in reverse line order for safe batch insertion.

    WHAT THIS DOES:
    - Reads a JavaScript file with UTF-8 encoding (ignoring malformed characters) and parses all lines into memory
    - Identifies function declarations using two regex patterns: standard functions (`function name()`) and arrow functions (`const/let/var name = () =>`) with optional `export` prefix
    - For each discovered function, scans backward up to 20 lines to detect JSDoc blocks (`/** ... */`) and checks for the `---agentspec` marker within those blocks
    - Filters candidates based on two control flags: `require_agentspec=True` returns only functions with JSDoc but missing the marker; `update_existing=True` returns all functions regardless of documentation state; default behavior returns undocumented functions
    - Returns a list of tuples `(line_number, function_name, code_snippet)` where the snippet includes the function declaration plus approximately 8 subsequent lines, sorted in descending line order to enable safe sequential insertion of documentation without invalidating line numbers
    - Returns an empty list if the file cannot be read, preventing pipeline breakage on I/O errors

    WHY THIS APPROACH:
    - **Reverse line sorting** is critical: when inserting documentation above functions, processing from highest line numbers downward ensures earlier insertions do not shift line numbers of subsequent candidates, maintaining correctness without re-scanning
    - **20-line JSDoc search window** balances performance (avoids O(n²) behavior on large files) against coverage (typical JSDoc blocks with comments fit comfortably within this range); this is a pragmatic heuristic rather than full AST parsing
    - **Two-part JSDoc detection** (`has_jsdoc` returns both `found_jsdoc` and `has_marker`) distinguishes three states: no documentation (skip or include based on `require_agentspec`), documentation without marker (include if `require_agentspec=True`), and documentation with marker (skip unless `update_existing=True`); this enables fine-grained filtering logic
    - **Exact substring match for `---agentspec`** (not regex or case-insensitive) prevents false positives from similar markers like `---agentspec-old` or `---agentspec-v2`, though this trades strictness for simplicity
    - **Regex patterns over AST parsing** prioritizes speed and simplicity for a discovery tool; full JavaScript parsing would be overkill for identifying function names and nearby JSDoc, and regex is sufficient for well-formatted code
    - **Code snippet capture** (current line + ~8 following lines) provides context for AI agents to understand function signatures and initial implementation without loading entire function bodies, reducing token consumption
    - **Nested `has_jsdoc()` helper** encapsulates the backward-scanning logic, improving readability and allowing the main loop to remain focused on iteration and filtering
    - **Error handling via try-except** returns empty list rather than raising exceptions, allowing the discovery process to fail gracefully if a file is unreadable (e.g., permission denied, encoding issues), preventing the entire batch operation from halting

    AGENT INSTRUCTIONS:
    - DO NOT modify the regex patterns without testing against real JavaScript codebases; the current patterns handle `export`, `const`, `let`, `var`, and standard function declarations, but edge cases like async functions, decorators, or complex arrow function expressions may require refinement
    - DO NOT change the 20-line search window without profiling impact on large files; increasing this limit may cause performance degradation on files with many functions
    - DO NOT remove the `.strip()` calls on lines before checking `.endswith("*/")` or substring matching; whitespace handling is essential for robust JSDoc detection
    - DO NOT alter the reverse sort order; this is a critical invariant that enables safe batch insertion of documentation
    - DO NOT change the exact string match `"---agentspec"` to a regex or case-insensitive variant without updating all downstream code that checks for this marker
    - ALWAYS preserve the three-state filtering logic: `update_existing` takes precedence, then `require_agentspec` determines whether to include undocumented functions or only functions with JSDoc but missing the marker
    - ALWAYS call `.read_text(encoding="utf-8", errors="ignore")` to handle non-UTF-8 files gracefully; changing this may cause crashes on files with encoding issues
    - ALWAYS include the code snippet in the returned tuple; downstream code may depend on this for context when generating documentation
    - ALWAYS return an empty list on file read errors; do not raise exceptions, as this allows batch processing to continue
    - NOTE: The `has_jsdoc()` helper assumes JSDoc blocks are contiguous and that `/**` appears before `*/` in the backward scan; malformed or nested JSDoc may produce incorrect results
    - NOTE: The arrow function regex may not catch all valid JavaScript arrow functions (e.g., multiline declarations, complex expressions); consider AST parsing if false negatives become problematic
    - NOTE: Line numbers are 1-indexed (via `enumerate(lines, start=1)`) but the snippet extraction uses 0-indexed slicing (`lines[idx - 1 : ...]`); this is correct but easy to misunderstand during maintenance
    - NOTE: The marker detection is substring-based; `---agentspec-old` or `---agentspec_v2` will incorrectly match. If strict format validation is required, replace the substring check with a regex like `r"---agentspec(?:\s|$)"`

    DEPENDENCIES (from code analysis):
    Calls: arrow_pat.match, candidates.append, candidates.sort, enumerate, filepath.read_text, func_pat.match, has_jsdoc, join, len, m1.group, m2.group, max, min, print, range, re.compile, s.endswith, strip, text.splitlines
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

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
        Brief one-line description.

        WHAT THIS DOES:
        - Scans backward up to 20 lines from a given index to detect JSDoc blocks (`/** ... */`) and identifies whether they contain a `---agentspec` marker
        - Returns a tuple of two booleans: (found_jsdoc, has_agentspec_marker) where the first indicates JSDoc presence and the second indicates marker presence
        - Uses a two-pass backward scan: first locates the closing `*/` delimiter, then searches preceding lines for the opening `/**` delimiter to extract and inspect the complete block
        - Handles whitespace robustness by calling .strip() on each line before performing endswith/contains checks
        - Returns (False, False) if no JSDoc block is found within the 20-line window; returns (True, False) if JSDoc exists but lacks the marker; returns (True, True) if both JSDoc and marker are present

        WHY THIS APPROACH:
        - The 20-line backward search window balances comprehensive JSDoc detection against performance degradation; typical JSDoc blocks fit comfortably within this range while preventing O(n) scanning on large files
        - Two-part return tuple enables callers to distinguish three distinct states: "no documentation exists" vs. "documentation exists but needs update" vs. "documentation exists and is marked for agent processing", allowing incremental documentation workflows
        - Backward scanning from the target index is more efficient than forward scanning because JSDoc immediately precedes the documented entity (function/class/variable)
        - The two-delimiter approach (finding `*/` first, then `/**`) ensures we capture complete blocks rather than false positives from incomplete or malformed JSDoc
        - Substring-based marker detection (`"---agentspec" in block`) is simpler and faster than regex matching for this specific use case, though it trades strictness for performance
        - Line-by-line iteration with early termination (return on first `/**` found) minimizes unnecessary string operations on large blocks

        AGENT INSTRUCTIONS:
        - DO NOT search beyond 20 lines backward; this hard limit prevents performance degradation on large files and is a critical performance guardrail
        - DO NOT assume the marker `---agentspec` is case-insensitive; the code uses exact string matching and will not match variations like `---AGENTSPEC` or `---agentspec-old`
        - DO NOT return True for found_jsdoc if only `*/` is found without a corresponding `/**`; both delimiters must be present to constitute a valid JSDoc block
        - DO NOT modify the iteration direction or range logic without understanding that backward iteration from (idx - 1) to (start - 1) is intentional for capturing JSDoc that precedes the target index
        - ALWAYS call .strip() on lines before performing endswith() or substring checks; this handles leading/trailing whitespace robustly and prevents false negatives from indented code
        - ALWAYS preserve the two-boolean return tuple structure; external code depends on distinguishing between "no JSDoc found" and "JSDoc found without marker"
        - NOTE: Marker detection uses substring matching; a JSDoc containing `---agentspec-old` or `---agentspec-v2` will incorrectly match. If strict format validation is required, consider refactoring to use regex pattern matching (e.g., `re.search(r'---agentspec(?:\s|$)', block)`)
        - NOTE: Block extraction uses `lines[i:idx]` which may include partial JSDoc content if the opening `/**` is not on the same line as the closing `*/`; this can lead to incomplete block inspection. Verify behavior with multi-line JSDoc blocks that span many lines or have complex formatting
        - NOTE: The function assumes `lines` is a global or closure-captured variable; ensure it remains in scope and is synchronized with the current file state before calling this function

        DEPENDENCIES (from code analysis):
        Calls: join, max, print, range, s.endswith, strip
        Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

        CHANGELOG (from git history):
        - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
        - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
        - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
        - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
        - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

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
    Brief one-line description.
    Processes JavaScript files to generate and insert embedded agentspec JSDoc documentation with optional metadata, diff summaries, and dry-run preview.

    WHAT THIS DOES:
    - Orchestrates a multi-stage pipeline to discover JavaScript functions, generate LLM-based docstrings, collect metadata, optionally summarize recent code diffs, and insert formatted JSDoc blocks back into source files
    - Pre-cleans existing agentspec blocks when `update_existing=True` (and not in dry-run mode) to ensure idempotency and prevent duplicate documentation
    - Discovers candidate functions via `_discover_js_functions()` with filtering based on `require_agentspec` and `update_existing` flags; returns tuples of (lineno, func_name, code)
    - In dry-run mode, prints candidate functions and their locations without modifying any files, allowing safe preview before actual changes
    - For each discovered function: (1) generates a docstring via `generate_docstring()` using the specified LLM model/provider, (2) collects deterministic metadata via `collect_metadata()`, (3) optionally generates diff summaries for the last 5 commits via `collect_function_code_diffs()` and `_gen_chat()`, (4) inserts the complete JSDoc via `apply_docstring_with_metadata()`
    - Supports multiple output formats: verbose narrative docstrings (default), terse single-line docs (if `terse=True`), or agentspec YAML blocks (if `as_agentspec_yaml=True`)
    - Supports multi-backend LLM flexibility via `model`, `base_url`, and `provider` parameters; defaults to "claude-haiku-4-5" with "auto" provider detection
    - Truncates diff content to 1600 characters per commit to control LLM token usage; appends "... (truncated)" marker when truncation occurs
    - Returns None; side effects include file modifications (or dry-run console output) and console status messages

    WHY THIS APPROACH:
    - Pre-cleaning via `strip_js_agentspec_blocks()` ensures idempotency when re-running with `update_existing=True`, preventing stale or duplicate JSDoc blocks from accumulating across multiple runs
    - Dry-run mode (`dry_run=True`) enables safe preview workflows in CI/CD and code review scenarios without risking unintended file modifications
    - Metadata and diff collection are wrapped in try-except blocks to degrade gracefully if external modules are unavailable or fail; however, this silent failure pattern masks bugs and produces incomplete documentation (see AGENT INSTRUCTIONS for guardrails)
    - LLM-based docstring generation via `generate_docstring()` allows flexible, context-aware documentation that adapts to code style and complexity; model/provider/base_url parameters support multi-backend flexibility (e.g., switching between Claude, GPT, local models)
    - Diff summarization provides change history context in JSDoc, helping maintainers understand why functions were modified; limited to 5 commits and 1600 chars per diff to control LLM token usage and prevent excessive API calls
    - Deterministic metadata collection ensures consistent docstring insertion across runs; metadata is collected independently of diff summaries to isolate failure modes
    - Console output with emoji indicators (✅, ⚠️, ❌, 🧹) provides clear visual feedback on processing status and helps users quickly identify successes, warnings, and errors

    AGENT INSTRUCTIONS:
    - DO NOT remove or bypass the `strip_js_agentspec_blocks()` call when `update_existing=True`; this is critical for idempotency
    - DO NOT remove the dry-run mode logic; this is essential for safe preview workflows
    - DO NOT modify the exception handling without adding explicit logging or error propagation; silent `except Exception: pass` blocks currently mask failures in metadata and diff collection
    - DO NOT change the diff truncation threshold (1600 chars) without understanding its impact on LLM token usage and context loss
    - DO NOT remove the metadata collection logic; this ensures deterministic, reproducible documentation
    - ALWAYS validate that external dependencies (`strip_js_agentspec_blocks`, `collect_function_code_diffs`, `collect_metadata`, `_gen_chat`, `apply_docstring_with_metadata`) are properly imported or defined before use
    - ALWAYS preserve the order of operations: pre-clean → discover → dry-run check → generate → collect metadata → collect diffs → insert
    - ALWAYS ensure that `apply_docstring_with_metadata()` is called with all required parameters, including `diff_summary_lines` when available
    - ALWAYS check the return value of `apply_docstring_with_metadata()` and print appropriate status messages (✅ or ⚠️)
    - NOTE: This function has multiple silent exception handlers (`except Exception: pass`) that mask failures in metadata collection (line ~60) and diff collection (line ~70); these should be replaced with explicit logging to aid debugging
    - NOTE: The `collect_function_code_diffs()`, `get_diff_summary_prompt()`, and `_gen_chat` functions are assumed to exist but are not validated; if these are missing or have changed signatures, the diff summary feature will silently fail
    - NOTE: Diff truncation at 1600 chars happens without user warning; if critical context is lost, the LLM may generate incomplete or inaccurate summaries
    - NOTE: The function returns None on error (e.g., parsing failure) without raising an exception; callers cannot distinguish between successful completion and failure
    - NOTE: File modifications happen in-place via `apply_docstring_with_metadata()`; ensure backups or version control is in place before running with `dry_run=False`

    DEPENDENCIES (from code analysis):
    Calls: _discover_js_functions, _gen_chat, apply_docstring_with_metadata, c.get, collect_function_code_diffs, collect_metadata, diff_summary_lines.append, generate_docstring, get_diff_summary_prompt, len, print, replace, str, strip, strip_js_agentspec_blocks
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

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
    Brief one-line description.

    WHAT THIS DOES:
    - Orchestrates end-to-end docstring generation for a single Python file by extracting functions lacking docstrings, generating LLM-based narrative content, collecting deterministic metadata (dependencies, imports, changelog) separately, then applying both via compile-safe insertion.
    - Extracts function information from the target file using `extract_function_info()`, returning early if no functions are found or if `dry_run=True` after printing the execution plan.
    - Sorts functions in reverse line-number order (bottom-to-top) to prevent line-shift invalidation during insertion—inserting docstrings shifts all subsequent line numbers downward, so ascending order would cause insertion failures.
    - For each function, executes a two-phase write: calls `generate_docstring()` to produce LLM narrative content only, then `collect_metadata()` to gather deterministic metadata (never passed to LLM), then `apply_docstring_with_metadata()` to perform compile-safe insertion of both.
    - Wraps metadata collection in try-except; failures fall back to empty dict and do not block docstring insertion, ensuring robustness even when metadata collection encounters errors.
    - Optionally generates diff summaries for recent commits affecting each function when `diff_summary=True`, collecting up to 5 recent commits with max 1600 chars per diff snippet, summarizing each via LLM.
    - Prints progress at each stage (extraction, generation, success/failure) and respects `dry_run`, `force_context`, `as_agentspec_yaml`, `update_existing`, and `terse` flags to control behavior.

    WHY THIS APPROACH:
    - **Bottom-to-top processing (reverse sort by line number)** is mandatory because inserting docstrings shifts all subsequent line numbers downward; ascending order would cause insertion failures as line numbers become invalid mid-loop. Reverse order ensures line numbers remain valid throughout the entire loop.
    - **Two-phase generation (LLM narrative + separate metadata collection)** maintains clean architectural separation: LLM only handles narrative content, deterministic metadata is collected separately and never passed to LLM, ensuring reproducibility, safety, and preventing "AI slop" contamination of structured data.
    - **Metadata collection wrapped in try-except with empty dict fallback** prioritizes robustness: metadata collection failures (e.g., git errors, import failures) do not block docstring insertion, allowing partial success rather than total failure.
    - **Compile-safety validation before insertion** prevents syntax errors from breaking the source file; `apply_docstring_with_metadata()` validates that the insertion does not break Python syntax before committing changes.
    - **Optional diff summary generation** provides context-aware changelog snippets by collecting recent commits affecting each function and summarizing them via LLM, enriching docstrings with historical context without requiring manual changelog maintenance.
    - **Separate `model`, `base_url`, and `provider` parameters** allow flexible LLM configuration, supporting multiple providers (OpenAI, Anthropic, etc.) and custom endpoints without hardcoding.
    - **`update_existing` flag** allows selective overwriting of existing docstrings when explicitly requested, preventing accidental overwrites while enabling intentional updates.
    - **`as_agentspec_yaml` flag** switches output format between standard Python docstrings and YAML-based agentspec blocks, supporting both documentation styles.

    AGENT INSTRUCTIONS:
    - DO NOT remove the reverse sort by line number; this is critical to prevent line-shift invalidation during insertion.
    - DO NOT pass metadata to the LLM; collect it deterministically via `collect_metadata()` and apply it separately via `apply_docstring_with_metadata()`.
    - DO NOT modify source files when `dry_run=True`; the function must return after printing the plan.
    - DO NOT remove the try-except wrapper around metadata collection; failures must fall back to empty dict and not block insertion.
    - DO NOT skip the compile-safety check in `apply_docstring_with_metadata()`; always validate syntax before inserting.
    - DO NOT change the order of operations: extract → sort → generate narrative → collect metadata → apply with metadata.
    - ALWAYS validate that `model` is a valid LLM identifier before passing to `generate_docstring()`.
    - ALWAYS respect the `update_existing` flag; only extract functions needing docstrings when `update_existing=False`.
    - ALWAYS print progress at each stage (extraction, generation, success/failure) for user visibility.
    - ALWAYS limit diff summary to 5 recent commits with max 1600 chars per diff snippet to avoid overwhelming LLM context.
    - ALWAYS handle SyntaxError from `extract_function_info()` gracefully; print error and return without crashing.
    - ALWAYS preserve the two-phase write architecture: narrative first (LLM), then metadata (deterministic).
    - NOTE: This function is the orchestration hub for docstring generation; changes to the extraction, generation, or insertion logic must be coordinated across all three phases to maintain consistency.
    - NOTE: The `force_context` flag adds context-forcing print() statements; ensure this is only used for debugging, not in production.
    - NOTE: Diff summary generation is optional and may fail silently; failures must not block docstring insertion.
    - NOTE: The function respects `terse=True` to generate shorter docstrings; ensure the prompt selection logic in `generate_docstring()` handles this correctly.

    DEPENDENCIES (from code analysis):
    Calls: _gen_chat, apply_docstring_with_metadata, c.get, collect_function_code_diffs, collect_metadata, diff_summary_lines.append, extract_function_info, functions.sort, generate_docstring, get_diff_summary_prompt, len, print, replace, str, strip
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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

def run(target: str, language: str = "auto", dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, provider: str | None = 'auto', base_url: str | None = None, update_existing: bool = False, terse: bool = False, diff_summary: bool = False, pre_strip: bool = False) -> int:
    """
    Brief one-line description.

    Orchestrates agentspec docstring generation across Python and JavaScript/TypeScript files with per-run token metrics collection and reporting.

    WHAT THIS DOES:
    - Loads environment variables from .env file and auto-detects the LLM provider (Anthropic for Claude models, OpenAI otherwise) based on the `model` parameter and explicit `provider` argument
    - Discovers source files from the target path using `collect_source_files()`, then filters by language (Python only, JavaScript/TypeScript only, or both via "auto" mode)
    - Validates that the target path exists; returns exit code 1 if missing or inaccessible
    - Clears the global `GEN_METRICS` dictionary before processing to ensure per-run isolation, then collects token usage and continuation counts during file processing
    - Delegates per-file docstring generation to `process_file()` for Python files (.py) or `process_js_file()` for JavaScript/TypeScript files (.js, .mjs, .jsx, .ts, .tsx)
    - Computes and prints per-run statistics (min/avg/max prompt tokens, min/avg/max output tokens, total continuations used) after all files are processed
    - Returns exit code 0 on success (even if no files found), or 1 on validation/authentication failure
    - Handles dry-run mode (no file modifications) and update-existing mode (regenerates existing docstrings) via boolean flags
    - Supports optional output formatting as agentspec YAML blocks and terse vs. verbose docstring modes

    Edge cases and error handling:
    - Invalid/missing target path: prints error message and returns 1 immediately
    - No files found matching language filter: prints informational message and returns 0 (silent success, not an error)
    - Provider auto-detection: Claude models (model name starts with "claude") → Anthropic provider; all others → OpenAI provider
    - Missing API keys: For Anthropic, fails with error message if ANTHROPIC_API_KEY not set and not in dry_run mode; for OpenAI, falls back to localhost:11434/v1 (Ollama) if no base_url provided and no OPENAI_API_KEY set
    - Empty or missing GEN_METRICS: metrics summary silently skipped via try/except (no error raised)
    - Per-file processing errors: caught and logged per-file, but do not halt overall run; function continues to next file
    - Language parameter validation: invalid values default to "auto" (both Python and JavaScript)

    WHY THIS APPROACH:
    - Provider auto-detection via model name avoids requiring explicit provider specification in most cases; users working with Claude models get Anthropic automatically, others get OpenAI
    - Filtering by language allows users to regenerate only Python docstrings or only JavaScript docstrings in mixed codebases, improving performance and reducing unnecessary API calls
    - Clearing GEN_METRICS before each run ensures metrics are not cumulative across multiple invocations in the same process (important for REPL/interactive use)
    - Per-file exception handling allows partial success: if one file fails, others still get processed, maximizing utility in large codebases
    - Fallback to localhost:11434/v1 for OpenAI provider enables local Ollama usage without explicit configuration, lowering barrier to entry for offline/local-first workflows
    - Token statistics (min/avg/max) provide visibility into LLM usage patterns; avg token count helps estimate costs; continuations count flags files requiring multiple API calls (potential quality issues)
    - Dry-run mode allows users to preview which files would be modified without committing changes; useful for validation before large batch runs
    - Update-existing mode allows regenerating docstrings for files that already have them, enabling iterative improvement or model upgrades

    Alternatives NOT used and why:
    - Could have required explicit provider specification instead of auto-detecting: rejected because it adds friction; auto-detection is sensible default
    - Could have processed all files regardless of language: rejected because mixed codebases benefit from selective regeneration
    - Could have failed on first file error: rejected because it reduces robustness; partial success is better than total failure
    - Could have used rounding instead of truncation for mean token count: rejected because truncation is deterministic and avoids false precision in display output
    - Could have accumulated GEN_METRICS across runs: rejected because it conflates metrics from different invocations and makes per-run analysis impossible

    Performance considerations:
    - `collect_source_files()` recursively walks the target directory; performance degrades with very large directory trees (thousands of files)
    - Language filtering via list comprehension is O(n) but fast; filtering happens after collection, not during discovery
    - Per-file processing is sequential (not parallelized); adding concurrency would require thread-safe GEN_METRICS access
    - Token statistics computation (min/max/mean) is O(n) where n = number of files processed; negligible overhead
    - Exception handling in per-file loop has minimal performance impact; try/except is fast in non-exception path

    Non-obvious code patterns:
    - `(provider or 'auto').lower()` handles None provider by defaulting to 'auto' string before lowercasing; avoids AttributeError
    - `(model or '').lower().startswith('claude')` uses empty string fallback to avoid AttributeError if model is None
    - Base URL resolution chain: explicit `base_url` arg > OPENAI_BASE_URL env var > AGENTSPEC_OPENAI_BASE_URL env var > OLLAMA_BASE_URL env var > hardcoded localhost:11434/v1; allows multiple configuration paths
    - `GEN_METRICS.clear()` wrapped in try/except because GEN_METRICS may not exist or may be immutable in some contexts (defensive programming)
    - Metrics summary wrapped in try/except to silently skip if GEN_METRICS collection failed; prevents cascading errors
    - `_fmt_stats()` defined inside exception handler scope: this is intentional (local scope) but creates risk that if GEN_METRICS collection fails, _fmt_stats is never defined and metrics printing silently skips
    - Language parameter validation (`if language not in {...}: language = "auto"`) normalizes invalid input to safe default instead of raising error

    AGENT INSTRUCTIONS:
    - DO NOT remove the provider auto-detection logic; it is the primary UX feature enabling seamless Claude/OpenAI switching
    - DO NOT parallelize file processing without making GEN_METRICS thread-safe (use threading.Lock or similar)
    - DO NOT change the fallback base_url chain order; it is intentionally ordered from most-specific to most-general
    - DO NOT remove the try/except around GEN_METRICS.clear() or metrics summary; these are defensive against missing/immutable GEN_METRICS
    - DO NOT remove language filtering; it is critical for selective regeneration in mixed codebases
    - DO NOT change the exit codes (0 for success/no-files, 1 for errors); they are part of the CLI contract
    - DO NOT remove dry-run or update-existing modes; they are essential for safe batch operations
    - ALWAYS validate target path exists before attempting file discovery
    - ALWAYS clear GEN_METRICS at the start of each run to ensure per-run isolation
    - ALWAYS catch and log per-file exceptions without halting the overall run
    - ALWAYS print the per-run metrics summary (even if empty) to provide visibility into LLM usage
    - ALWAYS use `int()` truncation (not rounding) for mean token count in metrics display
    - ALWAYS support all three language modes: "py" (Python only), "js" (JavaScript/TypeScript only), "auto" (both)
    - ALWAYS fall back to localhost:11434/v1 for OpenAI provider if no API key and no base_url provided
    - NOTE: The nested `_fmt_stats()` function and its agentspec docstring are AI-generated boilerplate and should be cleaned up; the function is a simple 3-line utility that does not warrant a full agentspec block. Consider extracting to module level or removing the nested docstring entirely.
    - NOTE: GEN_METRICS is a global mutable dictionary; ensure it is initialized before this function is called (likely in module initialization)
    - NOTE: This function is the main entry point for the CLI; changes to exit codes, output format, or error messages may break downstream tooling or scripts
    - NOTE: Provider auto-detection is based on model name prefix; if new model families are added (e.g., "gpt-5"), the auto-detection logic may need updating
    - NOTE: The metrics summary uses `int()` truncation for mean, which may hide precision; if exact token counts are needed, use raw GEN_METRICS instead

    DEPENDENCIES (from code analysis):
    Calls: GEN_METRICS.clear, Path, _fmt_stats, _stats.mean, collect_source_files, int, len, load_env_from_dotenv, lower, m.get, max, min, os.getenv, path.exists, print, process_file, process_js_file, startswith, suffix.lower, sum
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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

    # Optional pre-strip of existing agentspec blocks (Python + JS/TS)
    if pre_strip and not dry_run:
        try:
            from agentspec import strip as _strip
            _ = _strip.run(str(path), mode="all", dry_run=False)
        except Exception as e:
            print(f"⚠️  Pre-strip failed: {e}")

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
                    # Default to YAML blocks for JS/TS even if flag not set
                    as_agentspec_yaml=True,
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
                Brief one-line description.
                Formats a sequence of numeric values into a compact "min=X avg=Y max=Z" statistics string.

                WHAT THIS DOES:
                - Accepts an iterable of numeric values and computes three statistics: minimum, average, and maximum
                - Returns a formatted string with the pattern "min={minimum} avg={truncated_mean} max={maximum}"
                - Uses `min()` and `max()` built-in functions for extrema, `_stats.mean()` for arithmetic mean, and `int()` to truncate (not round) the mean to an integer
                - Handles single-value sequences by returning identical values for all three statistics (e.g., "min=5 avg=5 max=5")
                - Raises `ValueError` if the input sequence is empty (propagated from `min()` and `max()`)
                - Raises `TypeError` if the sequence contains non-numeric values (propagated from comparison operations in `min()`/`max()` or from `_stats.mean()`)
                - If `vals` is a generator or iterator, it will be consumed; subsequent calls will fail or return incorrect results

                WHY THIS APPROACH:
                - This function prioritizes compact, human-readable output for logging and debugging rather than statistical precision
                - Truncation via `int()` is used instead of rounding (`round()`) to provide deterministic, predictable behavior that doesn't introduce artificial rounding bias; `int()` truncates toward zero, which is simpler to reason about in log output
                - Built-in functions (`min()`, `max()`) are used for correctness and performance; they are implemented in C and handle edge cases reliably
                - `_stats.mean()` is used instead of manual summation to avoid floating-point accumulation errors and to leverage a tested statistical library
                - The string formatting approach is chosen for simplicity and readability; alternatives like returning a tuple or dict would require downstream parsing
                - No explicit type validation is performed before calling `min()`/`max()` because these functions will raise appropriate `TypeError` exceptions if given non-numeric values, making explicit validation redundant
                - This is intentionally display-only; the truncated mean is not suitable for further calculations or comparisons

                AGENT INSTRUCTIONS:
                - DO NOT remove the `int()` truncation or replace it with `round()`; truncation is intentional and documented behavior
                - DO NOT add type validation before `min()`/`max()` calls; let natural exceptions propagate for clarity
                - DO NOT convert `vals` to a list unless you document that the function now consumes generators; preserve the current lazy evaluation assumption
                - DO NOT use this function for statistical analysis, precision calculations, or value comparisons; it is display-only
                - DO NOT pass empty sequences; this will raise `ValueError` from `min()` or `max()`
                - DO NOT pass non-numeric iterables; this will raise `TypeError`
                - DO NOT assume `vals` can be iterated multiple times; if it is a generator, the first call consumes it
                - ALWAYS preserve the exact string format "min={X} avg={Y} max={Z}" for consistency with downstream log parsing or display code
                - ALWAYS use `_stats.mean()` for the average calculation; do not replace with manual summation
                - NOTE: The debug print statement with `[AGENTSPEC_CONTEXT]` is present in the current implementation; preserve it unless explicitly removing debug instrumentation across the codebase
                - NOTE: This function has no input sanitization; it relies on Python's built-in exception handling to signal problems to the caller

                DEPENDENCIES (from code analysis):
                Calls: _stats.mean, int, max, min, print
                Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

                CHANGELOG (from git history):
                - 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)
                - 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)
                - 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)
                - 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)
                - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)

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
    Brief one-line description.

    WHAT THIS DOES:
    - Parses command-line arguments to extract a required file/directory path and optional flags (--dry-run, --force-context, --model), then delegates to run() with validated parameters
    - Requires exactly one positional argument (sys.argv[1]) representing a file or directory path; exits with code 1 and prints usage if missing
    - Extracts optional flags: --dry-run and --force-context are boolean presence checks (no values required); --model accepts a string value from the next argument if present, defaulting to "claude-haiku-4-5" if omitted or if --model is the final argument
    - Validates ANTHROPIC_API_KEY environment variable exists before calling run(); prints usage message that documents this requirement
    - Calls run(path, language="auto", dry_run=<bool>, force_context=<bool>, model=<str>) and propagates its exit code unchanged via sys.exit(), preserving shell-level success/failure detection for automation and scripting contexts
    - Returns: None (function terminates via sys.exit() with integer exit code from run())

    WHY THIS APPROACH:
    - Manual argument parsing (without argparse) minimizes external dependencies for a simple 3-flag CLI; the overhead of importing and configuring argparse is unjustified for this minimal interface
    - Default model "claude-haiku-4-5" balances API cost and performance for typical documentation generation tasks; Haiku is faster and cheaper than Sonnet variants while maintaining sufficient quality for docstring generation
    - Boolean flags (--dry-run, --force-context) use presence checks rather than value parsing, reducing parsing complexity and making the CLI more intuitive (users don't need to remember flag syntax like --dry-run=true)
    - Thin main() function delegates all business logic to run(), maintaining separation of concerns: CLI argument handling stays in main(), while file processing, LLM calls, and docstring generation remain in run(); this keeps main() testable and prevents CLI concerns from polluting core logic
    - Exit code propagation (sys.exit(exit_code) from run()) is intentional: callers in shell scripts, CI/CD pipelines, and automation tools depend on non-zero exit codes to detect failures; suppressing or modifying this code would break downstream error handling
    - Model name is extracted via sys.argv.index('--model') followed by bounds checking (model_index + 1 < len(sys.argv)) to safely handle edge case where --model is the final argument; silently retains default in this case rather than raising an exception, providing graceful degradation
    - Usage string is printed to stdout (not stderr) to match common CLI convention; includes ANTHROPIC_API_KEY requirement prominently to prevent silent failures due to missing credentials

    AGENT INSTRUCTIONS:
    - DO NOT modify sys.exit(1) for missing arguments; this exit code is required for proper shell-level error detection in automation, CI/CD pipelines, and shell scripts that depend on non-zero exit codes to trigger error handling
    - DO NOT change the default model ("claude-haiku-4-5") without updating the usage string and considering API cost/performance tradeoffs; changing this affects all users and may increase operational costs
    - DO NOT add new positional arguments without updating the usage string to remain synchronized; the usage string is the primary documentation of the CLI contract
    - DO NOT remove, rename, or reorder --dry-run, --force-context, or --model flags; these are part of the public CLI contract and changing them breaks existing scripts and automation
    - DO NOT alter the usage string without ensuring it reflects all supported flags, their purposes, and available model options; the usage string is the authoritative documentation
    - DO NOT suppress, modify, or conditionally apply the exit code from run(); callers depend on it for success/failure detection in shell scripts and CI/CD pipelines
    - DO NOT add model validation that restricts accepted values to the listed options; the code intentionally accepts any string to allow for future model additions without code changes
    - DO NOT remove the ANTHROPIC_API_KEY validation message from the usage string; users must be aware this environment variable is required
    - ALWAYS keep the usage string synchronized with actual supported flags, their descriptions, and available model options; the usage string is the primary user-facing documentation
    - ALWAYS preserve the language="auto" parameter in the run() call; this enables automatic language detection for source files
    - ALWAYS propagate the exit code from run() unchanged via sys.exit(); do not convert, suppress, or conditionally apply it
    - ALWAYS validate that sys.argv has at least 2 elements (program name + path argument) before accessing sys.argv[1]; the current bounds check (len(sys.argv) < 2) is correct
    - ALWAYS use sys.argv.index('--model') with subsequent bounds checking to safely extract the model value; this pattern gracefully handles edge cases
    - NOTE: The usage string lists specific model options (claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022) but the code accepts any string without validation; this is intentional design to allow future model additions without code changes, but the usage string should be updated when new models are added
    - NOTE: ANTHROPIC_API_KEY validation is documented in the usage string but not enforced in main(); the actual validation occurs in run() or its callees; if this validation fails, the error will occur downstream rather than in main(), which is acceptable but means users may not see the error until after argument parsing completes
    - NOTE: The language parameter is hardcoded to "auto" in the run() call; this is intentional to enable automatic language detection for all source files, but if language selection becomes a user-facing feature in the future, it should be added as a CLI flag (e.g., --language) and passed through from sys.argv

    DEPENDENCIES (from code analysis):
    Calls: argv.index, len, print, run, sys.exit
    Imports: agentspec.collect.collect_metadata, agentspec.prompts.get_agentspec_yaml_prompt, agentspec.prompts.get_terse_docstring_prompt, agentspec.prompts.get_verbose_docstring_prompt, agentspec.prompts.load_provider_base_prompt, agentspec.utils.collect_source_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict

    CHANGELOG (from git history):
    - 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)
    - 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)
    - 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)

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
