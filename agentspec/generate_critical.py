#!/usr/bin/env python3
"""
Ultra-accurate generation mode for critical files.
Processes functions individually with deep metadata analysis and multi-pass verification.

CRITICAL: This module ensures deps and changelog are NEVER LLM-generated.
They are programmatically inserted from collected metadata.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Tuple
import json
import ast


CRITICAL_SYSTEM_PROMPT = """You are operating in CRITICAL DOCUMENTATION MODE.

## CRITICAL: What You Document

YOU GENERATE (narrative fields - requires reasoning):
- **what**: Detailed explanation of behavior, inputs, outputs, edge cases
- **why**: Design rationale, alternatives considered, tradeoffs
- **guardrails**: Critical warnings about what NOT to change

YOU DO NOT GENERATE (deterministic fields - code provides these):
- **deps**: Programmatically inserted from AST analysis
- **changelog**: Programmatically inserted from git history

Do NOT write deps or changelog sections. They will be discarded and replaced with real data.

## Your Mission

You are documenting code that:
- May handle sensitive data or security boundaries
- Could cause production outages if misunderstood
- Other developers will rely on for critical decisions
- AI agents will use to modify the code safely

## Requirements

1. **`ULTRATHINK` before writing** - analyze deeply, reason through edge cases
2. **Use ONLY provided metadata** - deps.calls shows actual function calls, changelog shows actual history
3. **Be exhaustively thorough** - this isn't the place for brevity
4. **Document WHY ruthlessly** - explain design decisions, rejected alternatives
5. **List ALL guardrails** - what must NEVER be changed and why
6. **Trace dependencies completely** - if it calls X which calls Y, document that chain

## Verification Promise

Your output will be verified in a second pass against the metadata. Any hallucinations or inaccuracies will be caught and corrected. This is your chance to get it right the first time.

Remember: This code is CRITICAL. Your documentation could be the difference between a safe deployment and a production incident. ULTRATHINK and be meticulous."""


CRITICAL_SYSTEM_PROMPT_TERSE = """CRITICAL DOCUMENTATION MODE (TERSE).

YOU GENERATE:
- **what**: Behavior, inputs, outputs, edge cases (concise)
- **why**: Design rationale and tradeoffs (brief)
- **guardrails**: Critical warnings (essential only)

YOU DO NOT GENERATE:
- **deps**: Programmatically inserted
- **changelog**: Programmatically inserted

Requirements:
1. ULTRATHINK but write concisely
2. Use ONLY provided metadata
3. Focus on critical information only
4. Explain WHY decisions were made
5. List essential guardrails only

This is CRITICAL code. Be accurate and concise."""


CRITICAL_VERIFICATION_PROMPT = """You are the VERIFICATION AGENT in critical documentation mode.

## Your Role

You are the second line of defense against documentation errors in critical code. The first agent generated documentation, and now you must verify it with extreme prejudice.

## Verification Checklist

1. **Metadata Accuracy**: Every claim about function calls MUST match deps.calls
2. **Git History**: Every changelog entry MUST reflect actual git commits
3. **No Hallucinations**: Remove any claims not supported by code or metadata
4. **Dependency Chains**: Verify all stated dependencies actually exist
5. **Guardrails**: Ensure guardrails are based on actual code patterns, not assumptions

## How to Verify

- ULTRATHINK about each claim in the documentation
- Cross-reference with the provided metadata
- Check if function names in "calls" actually appear in the code
- Verify changelog dates and messages match git history
- Ensure WHY explanations are grounded in visible code patterns

## Output

Return the documentation with:
- Corrections for any inaccuracies
- [VERIFIED] tags for claims you've confirmed
- [REMOVED] tags for hallucinations you've eliminated
- Additional detail where the original was vague

This is CRITICAL code. Accuracy is paramount. ULTRATHINK and verify everything."""


def generate_critical_docstring(
    code: str,
    filepath: str,
    func_name: str,
    model: str = "claude-3-5-sonnet-20241022",  # Default to high-quality model
    base_url: Optional[str] = None,
    provider: str = 'auto',
    as_agentspec_yaml: bool = False,
    terse: bool = False,
    diff_summary: bool = False,
) -> str:
    '''
    ```python
    """
    Generates production-grade docstrings for critical Python functions using two-pass LLM verification with deterministic metadata injection.

    WHAT:
    - Two-pass LLM pipeline: first pass generates narrative (what/why/guardrails) at temperature 0.1 with deep reasoning; second pass verifies accuracy at temperature 0.0 against code and metadata
    - Collects deterministic metadata via static AST analysis, recursively analyzes dependency chain (distinguishing dot-notation external calls), injects deps/changelog programmatically to prevent hallucination
    - Supports AGENTSPEC_YAML or plain-text formats; optional terse mode reduces tokens ~50%; optional diff_summary analyzes function-scoped code changes with format validation

    WHY:
    - Separates concerns: LLM generates only narrative reasoning while deterministic fields (deps/changelog) sourced from static analysis and injected by code, preventing technical metadata hallucination
    - Two-pass verification catches inaccuracies before injection; recursive dependency chain provides LLM context about called functions without overwhelming token budget
    - Explicit "DO NOT generate" instructions (repeated 5x) override LLM defaults; metadata-as-reference pattern reinforces boundary between reasoning and deterministic fields

    GUARDRAILS:
    - DO NOT allow LLM to generate deps/changelog—they are sourced from static analysis only and injected by code
    - DO NOT mix YAML and plain-text formats in output—validation raises ValueError if both detected
    - DO NOT bypass inject_deterministic_metadata() call—it is the sole mechanism preventing hallucination of technical metadata
    - ALWAYS forward base_url and provider to both generate_chat() calls to ensure consistent LLM configuration
    - ALWAYS include CRITICAL_SYSTEM_PROMPT in first_pass system role to establish critical-mode reasoning tone
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: Path, ValueError, any, base_prompt.format, called_meta.get, collect_function_code_diffs, collect_metadata, d.get, diff_summaries_text.split, expected_pattern.match, generate_chat, get, inject_deterministic_metadata, json.dumps, len, line.startswith, line.strip, meta.get, print, re.compile, re.search, valid_lines.append
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple


    CHANGELOG (from git history):
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints
    -    filepath: str,s
    -    from agentspec.generate import GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT
    - 2025-10-30: updated max toxens  on criitcal flag
    -    filepath: str,
    -    model: str = "claude-3-5-sonnet-20241022",
    -    terse: bool = False,
    -    diff_summary: bool = False,
    -    """
    -    Brief one-line description.
    -    Generates exhaustively verified critical docstrings for Python functions using a two-pass LLM workflow with deterministic metadata injection.
    -    WHAT THIS DOES:
    -    - Executes a sophisticated two-pass LLM documentation pipeline: first pass generates narrative fields (what/why/guardrails) at temperature 0.1 with deep reasoning enabled, second pass verifies narrative accuracy at temperature 0.0 with deterministic metadata as reference
    -    - Collects deterministic metadata (function dependencies, calls, imports, changelog) from the target file using `collect_metadata()`, then recursively analyzes the dependency chain for each called function, distinguishing between methods/external calls (dot-notation) and internal functions
    -    - Constructs a critical prompt that explicitly instructs the LLM to generate ONLY narrative fields and NOT to generate deps/changelog sections, which will be injected programmatically afterward
    -    - Performs recursive dependency chain analysis with try-except wrapping to gracefully handle functions not found in file, marking them as "not_found_in_file" and distinguishing external/method calls via dot-notation detection
    -    - Injects deterministic metadata into the final LLM output using `inject_deterministic_metadata()`, ensuring deps and changelog fields contain accurate, non-hallucinated data sourced from actual code analysis
    -    - Returns the final docstring with verified narrative content and injected deterministic metadata, optionally formatted as AGENTSPEC_YAML if `as_agentspec_yaml=True`
    -    - Edge cases: handles missing metadata gracefully (defaults to empty dict), manages functions with no dependency chain, truncates changelog to first 2 items to prevent token bloat, wraps recursive metadata collection in try-except to prevent cascading failures, and includes debug output showing pre/post-injection state
    -    DEPENDENCIES:
    -    - Called by: [Inferred to be called by documentation generation orchestration layer or CLI tools that need critical-mode docstring generation]
    -    - Calls: `Path()` (pathlib), `collect_metadata()` (agentspec.collect), `generate_chat()` (agentspec.llm, called twice with different temperatures), `inject_deterministic_metadata()` (agentspec.generate), `json.dumps()` (stdlib), `base_prompt.format()` (string formatting), `meta.get()` and `called_meta.get()` (dict access), `print()` (debug output)
    -    - Imports used: `__future__.annotations`, `ast`, `json`, `pathlib.Path`, `re`, `typing.Any`, `typing.Dict`, `typing.List`, `typing.Optional`
    -    - External services: LLM provider (Claude or configurable via `provider` parameter), accessed through `generate_chat()` with configurable `base_url`
    -    WHY THIS APPROACH:
    -    - **Separation of concerns**: LLM generates only narrative reasoning (what/why/guardrails) while deterministic fields (deps/changelog) are sourced from static code analysis and injected programmatically, preventing hallucination of technical metadata
    -    - **Two-pass verification workflow**: First pass at temperature 0.1 enables deep reasoning ("ULTRATHINK") for narrative generation; second pass at temperature 0.0 performs deterministic verification against code and metadata, catching inaccuracies before injection
    -    - **Recursive dependency chain analysis**: Provides LLM with context about called functions' own dependencies and changelogs (truncated to 2 items), enabling more accurate "why" reasoning without overwhelming token budget; dot-notation detection distinguishes external/method calls that cannot be analyzed in-file
    -    - **Explicit "DO NOT generate" instructions**: Repeated 5 times in critical_prompt to override LLM's tendency to hallucinate technical metadata; metadata is marked "for your reference - DO NOT copy" to reinforce this boundary
    -    - **Metadata-as-reference pattern**: Deterministic metadata is provided to LLM as context for narrative reasoning but explicitly excluded from output, then injected by code as single source of truth
    -    - **Graceful error handling**: Try-except wrapping around recursive `collect_metadata()` calls prevents one missing function from cascading into complete failure; "not_found_in_file" markers allow LLM to reason about external dependencies
    -    - **Performance considerations**: O(n) dependency chain analysis where n = number of called functions; JSON serialization overhead is acceptable given the critical nature of output; changelog truncation to 2 items balances context richness against token budget
    -    - **Alternatives NOT used**: Single-pass generation would allow hallucination of deps/changelog; temperature 0.0 for both passes would reduce reasoning quality; omitting dependency chain context would weaken narrative accuracy; not injecting metadata would require manual post-processing
    -    CHANGELOG:
    -    - Current implementation: Two-pass LLM workflow with recursive dependency analysis, explicit "DO NOT generate" instructions, and programmatic deterministic metadata injection to prevent hallucination of technical fields while enabling deep reasoning for narrative documentation.
    -    AGENT INSTRUCTIONS:
    -    - DO NOT modify the two-pass structure (first_pass at temperature 0.1, final at temperature 0.0) without understanding that verification pass is actual code, not optional scaffolding
    -    - DO NOT remove or weaken the "DO NOT generate deps/changelog" instructions in critical_prompt—they appear 5 times intentionally to override LLM defaults
    -    - DO NOT bypass the `inject_deterministic_metadata()` call—it is the sole mechanism ensuring deps and changelog fields contain accurate, non-hallucinated data
    -    - DO NOT change the metadata reference format ("for your reference - DO NOT copy")—this exact phrasing is critical for LLM instruction following
    -    - DO NOT modify the recursive dependency analysis logic without accounting for: circular dependency risks, dot-notation method/external call distinction, changelog truncation to prevent token bloat, and try-except wrapping for missing functions
    -    - DO NOT alter the prompt template selection logic (`as_agentspec_yaml` parameter)—it determines which base prompt is used and must be forwarded correctly
    -    - DO NOT remove the `collect_metadata()` call—it is the source of truth for deterministic fields
    -    - ALWAYS forward `base_url` and `provider` parameters to both `generate_chat()` calls (first_pass and final) to ensure consistent LLM configuration
    -    - ALWAYS include `CRITICAL_SYSTEM_PROMPT` in the system role of the first_pass call—it sets the tone for critical-mode reasoning
    -    - ALWAYS preserve the debug output (print statements showing pre/post-injection state)—they are essential for verifying metadata injection correctness
    -    - NOTE: This function is designed for "critical code" documentation where hallucination of technical metadata is unacceptable; the two-pass workflow and explicit metadata injection are non-negotiable safeguards
    -    - NOTE: The recursive dependency chain analysis can be expensive for functions with many dependencies; consider caching `collect_metadata()` results if this function is called repeatedly on the same codebase
    -    - NOTE: LLM output quality depends heavily on the quality of `base_prompt` template and `CRITICAL_SYSTEM_PROMPT`; changes to either should be tested thoroughly
    -    """
    -    from agentspec.generate import GENERATION_PROMPT, GENERATION_PROMPT_TERSE, AGENTSPEC_YAML_PROMPT
    -    # Collect deterministic metadata
    -    # Analyze dependency chain
    -                        "changelog": called_meta.get('changelog', [])[:2]
    -    # Choose prompt template
    -    if as_agentspec_yaml:
    -        base_prompt = AGENTSPEC_YAML_PROMPT
    -    elif terse:
    -        base_prompt = GENERATION_PROMPT_TERSE
    -    else:
    -        base_prompt = GENERATION_PROMPT
    -    # Build prompt that explicitly tells LLM NOT to generate deps/changelog
    -    critical_prompt = f"""CRITICAL MODE: Document narrative fields ONLY.
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    # Code Change Analysis

    **Commit 1 (2025-10-30 - chore(lint)):**
    Allow long AGENTSPEC context prints without linting errors.

    **Commit 2 (2025-10-30 - updated max tokens):**
    Increase LLM token limits for more comprehensive critical documentation.

    **Commit 3 (2025-10-30 - feat: enhance CLI help):**
    Switch from changelog diffs to function-scoped code diffs analysis.

    **Commit 4 (2025-10-30 - feat: enhance docstring generation):**
    Add optional dependency chain analysis and diff summary generation.

    '''
    
    from agentspec.collect import collect_metadata
    from agentspec.llm import generate_chat
    from agentspec.generate import GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT, inject_deterministic_metadata

    # CRITICAL DIFFERENCE #1: Collect deep metadata
    print(f"  📊 Collecting deep metadata for {func_name}...")
    meta = collect_metadata(Path(filepath), func_name) or {}

    # CRITICAL DIFFERENCE #2: Analyze dependency chain
    deps_calls = meta.get('deps', {}).get('calls', [])
    call_chain_meta = {}

    for called_func in deps_calls:
        if '.' in called_func:
            # Method call - note it but don't try to trace
            call_chain_meta[called_func] = {"type": "method_or_external"}
        else:
            # Try to get metadata for called function in same file
            try:
                called_meta = collect_metadata(Path(filepath), called_func)
                if called_meta:
                    call_chain_meta[called_func] = {
                        "calls": called_meta.get('deps', {}).get('calls', []),
                        "changelog": called_meta.get('changelog', [])[:2]  # Just recent
                    }
            except Exception:
                call_chain_meta[called_func] = {"type": "not_found_in_file"}

    # Prepare metadata summary
    metadata_json = json.dumps(meta, indent=2)
    chain_json = json.dumps(call_chain_meta, indent=2) if call_chain_meta else "No dependency chain found"

    # CRITICAL DIFFERENCE #3: Choose appropriate prompt template
    base_prompt = AGENTSPEC_YAML_PROMPT if as_agentspec_yaml else GENERATION_PROMPT

    # CRITICAL DIFFERENCE #4: Build ultra-detailed prompt with ULTRATHINK
    critical_prompt = f"""CRITICAL MODE ACTIVE: You are documenting a critical function.

METADATA (DETERMINISTIC - THIS IS GROUND TRUTH):
{metadata_json}

DEPENDENCY CHAIN ANALYSIS:
{chain_json}

REQUIREMENTS:
1. ULTRATHINK - engage deep reasoning about this code
2. Generate ONLY: 'what', 'why', 'guardrails' sections
3. DO NOT generate 'deps' or 'changelog' - they will be inserted by code
4. DO NOT generate both YAML and plain text formats - generate ONLY the format specified by the prompt template
5. Base your narrative on code analysis and provided metadata
6. Be exhaustively thorough - this is critical code

{base_prompt.format(code=code, filepath=filepath, hard_data="(deterministic fields will be injected by code)")}

CRITICAL: Generate narrative fields ONLY in the format specified above. DO NOT mix YAML and plain text formats. ULTRATHINK about accuracy."""

    # First pass: Generate narrative fields
    print(f"  🤔 ULTRATHINKING documentation for {func_name}...")
    system_prompt = CRITICAL_SYSTEM_PROMPT_TERSE if terse else CRITICAL_SYSTEM_PROMPT
    first_pass = generate_chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": critical_prompt}
        ],
        temperature=0.0 if terse else 0.1,
        max_tokens=1500 if terse else 3000,
        base_url=base_url,
        provider=provider,
    )

    # Verification pass (verify narrative fields only)
    print(f"  ✓ Verifying accuracy for {func_name}...")
    verify_prompt = f"""REVIEW AND CORRECT THE DOCUMENTATION BELOW:

ORIGINAL CODE:
```python
{code}
```

GENERATED DOCUMENTATION:
{first_pass}

METADATA FOR REFERENCE:
{metadata_json}

YOUR TASK:
1. ULTRATHINK: Review the generated documentation for accuracy
2. Check that 'what' explains actual behavior from the code
3. Check that 'why' is grounded in code patterns
4. Check that 'guardrails' are based on real risks
5. DO NOT add deps or changelog - those will be injected by code

CRITICAL: Return the CORRECTED VERSION of the documentation in the EXACT SAME FORMAT as the generated documentation above.
DO NOT return a verification report or meta-commentary.
DO NOT wrap the output in markdown code fences.
DO NOT generate both YAML and plain text formats - use ONLY the format from the generated documentation above.
Return ONLY the docstring content that will be inserted into the file.

If the documentation is already accurate, return it unchanged.
If corrections are needed, return the corrected version in the same format (YAML OR plain text, not both)."""

    final = generate_chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a documentation accuracy reviewer. Return the corrected documentation in the same format as the input, not a verification report. Do not generate deps or changelog."},
            {"role": "user", "content": verify_prompt}
        ],
        temperature=0.0,
        max_tokens=1500 if terse else 3000,
        base_url=base_url,
        provider=provider,
    )

    # FORMAT VALIDATION: Ensure LLM output follows expected structure
    # This is about format compliance, not content control
    import re
    if as_agentspec_yaml:
        # YAML mode: should NOT contain plain text sections like "WHAT:" "WHY:"
        # (Note: CHANGELOG sections are OK - they'll be overwritten by deterministic metadata)
        plain_text_patterns = [
            r'(?m)^[ \t]*WHAT:', r'(?m)^[ \t]*WHY:'
        ]
        if any(re.search(pattern, final) for pattern in plain_text_patterns):
            raise ValueError("LLM generated invalid YAML format - contains plain text sections. Rejecting and requiring regeneration.")
    else:
        # Plain text mode: should NOT contain YAML sections
        yaml_patterns = [
            r'^---agentspec',  # YAML block start at beginning of line
            r'(?m)^[ \t]+what:',  # Indented YAML what: (not plain WHAT:)
            r'(?m)^[ \t]+why:',   # Indented YAML why:
            r'---/agentspec'  # YAML block end
        ]
        if any(re.search(pattern, final, re.MULTILINE) for pattern in yaml_patterns):
            raise ValueError("LLM generated invalid plain text format - contains YAML sections. Rejecting and requiring regeneration.")

    # CRITICAL: Inject deterministic metadata programmatically
    print("\n  🔧 DEBUG: About to inject metadata")
    print("  📊 Collected metadata:")
    print(json.dumps(meta, indent=2))
    print("\n  📝 LLM output BEFORE injection:")
    print("="*80)
    print(final)
    print("="*80)
    print(f"  🔍 LLM output has 'changelog:': {'changelog:' in final}")
    print(f"  🔍 LLM output has 'deps:': {'deps:' in final}")

    final_with_metadata = inject_deterministic_metadata(final, meta, as_agentspec_yaml)

    # DEBUG: verify that deterministic changelog entries survived injection
    try:
        if meta.get('changelog'):
            for entry in meta['changelog']:
                if entry not in final_with_metadata:
                    print(f"  ⚠️  WARNING: Changelog entry not found in output: {entry[:80]}")
    except Exception:
        # Debug only; never fail generation on debug check
        pass

    print("\n  ✅ AFTER injection:")
    print("="*80)
    print(final_with_metadata)
    print("="*80)

    # If diff_summary requested, make separate LLM call to summarize function-scoped code diffs (excluding docstrings/comments)
    if diff_summary:
        from agentspec.collect import collect_function_code_diffs
        diffs = collect_function_code_diffs(Path(filepath), func_name)

        if diffs:
            print(f"  📊 Collecting function-scoped diff summaries for {func_name}...")
            # Build prompt for LLM to summarize WHY based on code-only changes
            diff_prompt = (
                "CRITICAL: Output format is EXACTLY one line per commit in format:\n"
                "- YYYY-MM-DD: summary (hash)\n\n"
                "Summarize the intent (WHY) behind these code-only changes to the function.\n"
                "Only consider the added/removed lines shown (docstrings/comments removed).\n"
                "Use the exact date and commit hash provided. Provide a concise WHY summary in <=15 words.\n\n"
            )
            for d in diffs:
                commit_hash = d.get('hash', 'unknown')
                diff_prompt += f"Commit: {d['date']} - {d['message']} ({commit_hash})\n"
                diff_prompt += f"Function: {func_name}\n"
                diff_prompt += f"Changed lines:\n{d['diff']}\n\n"

            # Separate API call for diff summaries
            summary_system_prompt = (
                "CRITICAL: You are a precise code-change analyst. Output EXACTLY one line per commit in format:\n"
                "- YYYY-MM-DD: concise summary (hash)\n\n"
                "Infer WHY the function changed in <=10 words. Use exact date and hash provided."
                if terse else
                "CRITICAL: You are a precise code-change analyst. Output EXACTLY one line per commit in format:\n"
                "- YYYY-MM-DD: concise summary (hash)\n\n"
                "Explain WHY the function changed in <=15 words. Use exact date and hash provided."
            )
            diff_summaries_text = generate_chat(
                model=model,
                messages=[
                    {"role": "system", "content": summary_system_prompt},
                    {"role": "user", "content": diff_prompt}
                ],
                temperature=0.0,
                max_tokens=500 if terse else 1000,
                base_url=base_url,
                provider=provider,
            )

            # Validate diff summary format
            import re
            expected_pattern = re.compile(r'^\s*-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)\s*$', re.MULTILINE)
            lines = [line.strip() for line in diff_summaries_text.split('\n') if line.strip()]

            # Check if response follows the required format
            valid_lines = []
            for line in lines:
                if expected_pattern.match(line):
                    valid_lines.append(line)
                elif line and not line.startswith('#') and not line.startswith('```'):
                    # If line has content but doesn't match format, LLM ignored instructions
                    print(f"  ⚠️  Warning: Diff summary line doesn't match required format: {line[:50]}...")
                    break
            else:
                # All lines are valid or empty
                if not valid_lines:
                    print("  ⚠️  Warning: Diff summary is empty")
                else:
                    print(f"  ✅ Diff summary format validated ({len(valid_lines)} entries)")

            # Inject function-scoped diff summary section
            diff_summary_section = f"\n\nFUNCTION CODE DIFF SUMMARY (LLM-generated):\n{diff_summaries_text}\n"
            final_with_metadata += diff_summary_section

    return final_with_metadata


def process_file_critical(
    filepath: Path,
    dry_run: bool = False,
    force_context: bool = False,
    model: str = "claude-3-5-sonnet-20241022",
    as_agentspec_yaml: bool = False,
    provider: str = "auto",
    base_url: Optional[str] = None,
    update_existing: bool = False,
    terse: bool = False,
    diff_summary: bool = False
) -> None:
    '''
    ```python
    """
    Orchestrate three-phase pipeline: AST extraction → LLM generation with deterministic metadata → safe insertion with syntax validation.

    WHAT:
    - Extracts undocumented functions via AST, generates verified docstrings with LLM, injects code-derived metadata (deps/changelog), inserts safely with syntax validation.
    - Processes functions in descending line order to preserve line number validity during sequential insertions; per-function error isolation allows batch processing to continue despite individual failures.
    - Supports dry-run preview, context-forcing debug injection, flexible LLM provider selection, and update-existing flag for refreshing stale docs.

    WHY:
    - LLM verification with deterministic metadata injection prevents AI hallucination of facts derivable from code analysis.
    - Descending line-number processing ensures earlier insertions don't invalidate later line references; per-function try-except isolates failures for granular error reporting.
    - Lazy imports and early SyntaxError abort prevent cascade failures; structured emoji-prefixed output enables CI/CD parsing and human readability.

    GUARDRAILS:
    - DO NOT process files with syntax errors; abort early to prevent cascade failures.
    - DO NOT skip dry-run checks; they prevent unintended file modifications.
    - DO NOT process functions in ascending line order; descending order is required to preserve line number validity.
    - DO NOT inline insert_docstring_at_line import; lazy import avoids circular dependencies and import-time side effects.
    - DO NOT narrow exception handling to specific types; broad Exception catch prevents missing error categories.
    - ALWAYS process functions in descending line number order before insertion.
    - ALWAYS verify syntax before insertion to prevent corrupting source files.
    - ALWAYS inject deterministic metadata after LLM generation, never before.
    - ALWAYS pass model, base_url, provider through to generate_critical_docstring for flexible LLM selection.
    - ALWAYS distinguish three empty-result scenarios with specific console messages (no functions found, all documented, syntax error).
    - ALWAYS preserve emoji-prefixed console output structure for CI/CD regex parsing.
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: extract_function_info_critical, generate_critical_docstring, insert_docstring_at_line, len, print, str
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple


    CHANGELOG (from git history):
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints
    - Executes a three-phase pipeline: (1) AST-based extraction of functions needing documentation via `extract_function_info_critical()`, (2) per-function LLM generation with deterministic metadata injection via `generate_critical_docstring()` followed by safe insertion via `insert_docstring_at_line()`, and (3) dry-run safety check that returns early without file modification if `dry_run=True`
    - Parses the target file for syntax errors and returns immediately if parsing fails, preventing cascade failures on malformed Python
    - Distinguishes three empty-result scenarios with specific console messaging: (a) no functions found even with `--update-existing` flag, (b) all functions already have verbose docstrings (normal completion), (c) file syntax error (early abort)
    - Processes functions in bottom-to-top line order (confirmed by code comment) to preserve line number validity during sequential insertions, ensuring later insertions do not invalidate earlier line references
    - Wraps each function's generation and insertion in individual try-except blocks to isolate per-function failures and allow batch processing to continue despite individual errors
    - Conditionally injects context-forcing print() statements into generated docstrings when `force_context=True`, enabling AI agents to trace execution flow
    - Passes model, base_url, and provider parameters through to downstream generation functions, enabling flexible LLM provider selection (auto-detection or explicit specification)
    - Returns `None` after completion (or early return on error/dry-run); all side effects are console output and conditional file modification
    - Produces structured console output with emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖) for machine-parseable CI/CD integration and human readability
    - Called by: [Inferred from context: likely CLI entry point or orchestration layer in agentspec/main.py or similar]
    - Calls: `extract_function_info_critical()` (AST extraction with update_existing flag), `generate_critical_docstring()` (LLM generation with deterministic metadata), `insert_docstring_at_line()` (safe docstring insertion with syntax validation), `len()` (function count), `print()` (console output), `str()` (type conversion)
    - Imports used: `__future__.annotations` (PEP 563 deferred evaluation), `ast` (syntax parsing, implicit via extract_function_info_critical), `json` (metadata serialization, implicit via generate_critical_docstring), `pathlib.Path` (file path abstraction), `re` (regex, implicit via extraction/insertion), `typing.Any`, `typing.Dict`, `typing.List`, `typing.Optional` (type hints)
    - External services: LLM provider (Claude 3.5 Sonnet by default, or configurable via `provider` and `base_url` parameters); provider selection is delegated to `generate_critical_docstring()`
    - **Bottom-to-Top Processing**: Functions are sorted by descending line number before insertion. This is critical because inserting a docstring at line N shifts all subsequent line numbers downward; processing from bottom-to-top ensures earlier insertions do not invalidate later line references. Alternative (top-to-bottom) would require recalculating line numbers after each insertion, introducing complexity and error risk.
    - **Per-Function Error Isolation**: Each function is wrapped in its own try-except block rather than wrapping the entire loop. This allows the batch to continue processing remaining functions even if one fails (e.g., due to LLM timeout or insertion syntax error). Alternative (single outer try-except) would abort the entire file on first error, reducing utility for large files with mixed success rates.
    - **Lazy Import of insert_docstring_at_line**: The import statement is placed inside the function body rather than at module level. This avoids import-time side effects and circular dependency risks, and allows the function to be called without triggering downstream module initialization. Alternative (top-level import) would couple this module tightly to the insertion logic at import time.
    - **Dry-Run Early Return**: The dry-run check occurs after printing the processing plan but before any file modification. This allows users to preview what will happen without risk. Alternative (no dry-run) would require file backups or version control recovery; alternative (dry-run after processing) would waste computation.
    - **Deterministic Metadata Injection**: The function delegates metadata collection (deps, changelog) to `extract_function_info_critical()` and `generate_critical_docstring()`, rather than computing it inline. This separation ensures metadata is deterministic (derived from code analysis, not LLM hallucination) and reusable across multiple generation attempts. Alternative (inline metadata) would couple metadata logic to this orchestration function.
    - **Model/Provider Flexibility**: Parameters `model`, `base_url`, and `provider` are passed through to `generate_critical_docstring()`, enabling runtime selection of LLM backend without code modification. Alternative (hardcoded model) would reduce flexibility for users with custom LLM deployments or provider preferences.
    - **Force-Context Flag**: The `force_context` parameter conditionally injects print() statements into docstrings. This enables AI agents to trace execution flow during docstring-guided code analysis. Alternative (always inject) would clutter docstrings; alternative (never inject) would reduce agent observability.
    - **Update-Existing Flag**: Passed to `extract_function_info_critical()` to control whether functions with existing docstrings are re-processed. This allows users to refresh stale documentation or skip already-documented functions. Alternative (always update) would waste computation; alternative (never update) would prevent corrections.
    - **Console Output Structure**: Emoji prefixes and indentation are consistent throughout, enabling CI/CD systems to parse output via regex and extract function names, line numbers, and success/failure status. Alternative (unstructured output) would require fragile line-by-line parsing.
    - **Broad Exception Handling**: The per-function try-except uses `except Exception as e` (not specific exception types). This catches all failures (LLM errors, file I/O errors, syntax errors during insertion) and logs them without crashing. Alternative (specific exception types) would miss unexpected error categories; alternative (no exception handling) would abort on first error.
    - Current implementation: Orchestrates three-phase pipeline (extraction, generation, insertion) with bottom-to-top processing, per-function error isolation, dry-run safety, and deterministic metadata injection for AI-agent-consumable docstrings.
    - DO NOT remove or reorder the bottom-to-top sorting of functions; line number validity depends on this ordering
    - DO NOT skip or modify the SyntaxError handler that returns early; malformed Python must abort immediately to prevent cascade failures
    - DO NOT modify the dry-run early return; it is the only safeguard against unintended file modifications
    - DO NOT change the per-function try-except wrapper; it isolates failures and allows batch processing to continue
    - DO NOT remove the `force_context` parameter or its conditional output; AI agents depend on context-forcing print() statements for execution tracing
    - DO NOT inline the `insert_docstring_at_line` import into module scope; lazy import avoids circular dependencies and import-time side effects
    - DO NOT modify the return type from `None`; callers expect no return value, only side effects
    - ALWAYS preserve the console output structure with emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖); CI/CD systems parse this format
    - ALWAYS pass through `model`, `base_url`, and `provider` parameters to `generate_critical_docstring()`; these enable flexible LLM provider selection
    - ALWAYS check the return value of `insert_docstring_at_line()` and distinguish success (ok=True) from syntax-safety failures (ok=False)
    - ALWAYS distinguish between the three empty-result scenarios (no functions found with update_existing, all functions already documented, syntax error) with specific console messages
    - ALWAYS print the list of functions found before processing; this provides user feedback and enables progress tracking
    - NOTE: The bottom-to-top assumption is critical for line number validity; any deviation will cause subsequent insertions to target wrong line numbers
    - NOTE: Broad exception handling (`except Exception as e`) catches all failure categories; do not narrow to specific exception types without understanding downstream error propagation
    - NOTE: Deterministic metadata
    -    print(f"  🔬 CRITICAL MODE: Processing one function at a time with verification")
    - 2025-10-30: updated max toxens  on criitcal flag
    - Executes a three-phase pipeline: (1) AST-based extraction of functions needing documentation via `extract_function_info_critical()`, (2) per-function LLM generation with deterministic metadata injection via `generate_critical_docstring()` followed by safe insertion via `insert_docstring_at_line()`, and (3) dry-run safety check that returns early without file modification if `dry_run=True`
    - Parses the target file for syntax errors and returns immediately if parsing fails, preventing cascade failures on malformed Python
    - Distinguishes three empty-result scenarios with specific console messaging: (a) no functions found even with `--update-existing` flag, (b) all functions already have verbose docstrings (normal completion), (c) file syntax error (early abort)
    - Processes functions in bottom-to-top line order (confirmed by code comment) to preserve line number validity during sequential insertions, ensuring later insertions do not invalidate earlier line references
    - Wraps each function's generation and insertion in individual try-except blocks to isolate per-function failures and allow batch processing to continue despite individual errors
    - Conditionally injects context-forcing print() statements into generated docstrings when `force_context=True`, enabling AI agents to trace execution flow
    - Passes model, base_url, and provider parameters through to downstream generation functions, enabling flexible LLM provider selection (auto-detection or explicit specification)
    - Returns `None` after completion (or early return on error/dry-run); all side effects are console output and conditional file modification
    - Produces structured console output with emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖) for machine-parseable CI/CD integration and human readability
    - Called by: [Inferred from context: likely CLI entry point or orchestration layer in agentspec/main.py or similar]
    - Calls: `extract_function_info_critical()` (AST extraction with update_existing flag), `generate_critical_docstring()` (LLM generation with deterministic metadata), `insert_docstring_at_line()` (safe docstring insertion with syntax validation), `len()` (function count), `print()` (console output), `str()` (type conversion)
    - Imports used: `__future__.annotations` (PEP 563 deferred evaluation), `ast` (syntax parsing, implicit via extract_function_info_critical), `json` (metadata serialization, implicit via generate_critical_docstring), `pathlib.Path` (file path abstraction), `re` (regex, implicit via extraction/insertion), `typing.Any`, `typing.Dict`, `typing.List`, `typing.Optional` (type hints)
    - External services: LLM provider (Claude 3.5 Sonnet by default, or configurable via `provider` and `base_url` parameters); provider selection is delegated to `generate_critical_docstring()`
    - **Bottom-to-Top Processing**: Functions are sorted by descending line number before insertion. This is critical because inserting a docstring at line N shifts all subsequent line numbers downward; processing from bottom-to-top ensures earlier insertions do not invalidate later line references. Alternative (top-to-bottom) would require recalculating line numbers after each insertion, introducing complexity and error risk.
    - **Per-Function Error Isolation**: Each function is wrapped in its own try-except block rather than wrapping the entire loop. This allows the batch to continue processing remaining functions even if one fails (e.g., due to LLM timeout or insertion syntax error). Alternative (single outer try-except) would abort the entire file on first error, reducing utility for large files with mixed success rates.
    - **Lazy Import of insert_docstring_at_line**: The import statement is placed inside the function body rather than at module level. This avoids import-time side effects and circular dependency risks, and allows the function to be called without triggering downstream module initialization. Alternative (top-level import) would couple this module tightly to the insertion logic at import time.
    - **Dry-Run Early Return**: The dry-run check occurs after printing the processing plan but before any file modification. This allows users to preview what will happen without risk. Alternative (no dry-run) would require file backups or version control recovery; alternative (dry-run after processing) would waste computation.
    - **Deterministic Metadata Injection**: The function delegates metadata collection (deps, changelog) to `extract_function_info_critical()` and `generate_critical_docstring()`, rather than computing it inline. This separation ensures metadata is deterministic (derived from code analysis, not LLM hallucination) and reusable across multiple generation attempts. Alternative (inline metadata) would couple metadata logic to this orchestration function.
    - **Model/Provider Flexibility**: Parameters `model`, `base_url`, and `provider` are passed through to `generate_critical_docstring()`, enabling runtime selection of LLM backend without code modification. Alternative (hardcoded model) would reduce flexibility for users with custom LLM deployments or provider preferences.
    - **Force-Context Flag**: The `force_context` parameter conditionally injects print() statements into docstrings. This enables AI agents to trace execution flow during docstring-guided code analysis. Alternative (always inject) would clutter docstrings; alternative (never inject) would reduce agent observability.
    - **Update-Existing Flag**: Passed to `extract_function_info_critical()` to control whether functions with existing docstrings are re-processed. This allows users to refresh stale documentation or skip already-documented functions. Alternative (always update) would waste computation; alternative (never update) would prevent corrections.
    - **Console Output Structure**: Emoji prefixes and indentation are consistent throughout, enabling CI/CD systems to parse output via regex and extract function names, line numbers, and success/failure status. Alternative (unstructured output) would require fragile line-by-line parsing.
    - **Broad Exception Handling**: The per-function try-except uses `except Exception as e` (not specific exception types). This catches all failures (LLM errors, file I/O errors, syntax errors during insertion) and logs them without crashing. Alternative (specific exception types) would miss unexpected error categories; alternative (no exception handling) would abort on first error.
    - Current implementation: Orchestrates three-phase pipeline (extraction, generation, insertion) with bottom-to-top processing, per-function error isolation, dry-run safety, and deterministic metadata injection for AI-agent-consumable docstrings.
    - DO NOT remove or reorder the bottom-to-top sorting of functions; line number validity depends on this ordering
    - DO NOT skip or modify the SyntaxError handler that returns early; malformed Python must abort immediately to prevent cascade failures
    - DO NOT modify the dry-run early return; it is the only safeguard against unintended file modifications
    - DO NOT change the per-function try-except wrapper; it isolates failures and allows batch processing to continue
    - DO NOT remove the `force_context` parameter or its conditional output; AI agents depend on context-forcing print() statements for execution tracing
    - DO NOT inline the `insert_docstring_at_line` import into module scope; lazy import avoids circular dependencies and import-time side effects
    - DO NOT modify the return type from `None`; callers expect no return value, only side effects
    - ALWAYS preserve the console output structure with emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖); CI/CD systems parse this format
    - ALWAYS pass through `model`, `base_url`, and `provider` parameters to `generate_critical_docstring()`; these enable flexible LLM provider selection
    - ALWAYS check the return value of `insert_docstring_at_line()` and distinguish success (ok=True) from syntax-safety failures (ok=False)
    - ALWAYS distinguish between the three empty-result scenarios (no functions found with update_existing, all functions already documented, syntax error) with specific console messages
    - ALWAYS print the list of functions found before processing; this provides user feedback and enables progress tracking
    - NOTE: The bottom-to-top assumption is critical for line number validity; any deviation will cause subsequent insertions to target wrong line numbers
    - NOTE: Broad exception handling (`except Exception as e`) catches all failure categories; do not narrow to specific exception types without understanding downstream error propagation
    - NOTE: Deterministic metadata
    -    print("  🛡️  Deps and changelog will be programmatically injected (no LLM hallucination)")
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    # Commit Analysis

    **Commit 1 (2025-10-30 - chore(lint)):**
    Suppress line-length linting to permit verbose AGENTSPEC context output.

    **Commit 2 (2025-10-30 - updated max tokens):**
    Remove function implementation (appears to be revert/deletion).

    **Commit 3 (2025-10-30 - feat: enhance docstring generation):**
    Add programmatic dependency and changelog injection to critical mode.

    '''
    print(f"\n📄 Processing {filepath} in CRITICAL MODE")
    print("  🔬 Using ultra-accurate generation with verification")
    print("  🛡️  Deps and changelog will be programmatically injected (no LLM hallucination)")

    try:
        functions = extract_function_info_critical(filepath, update_existing, as_agentspec_yaml)
    except SyntaxError as e:
        print(f"  ❌ Syntax error in file: {e}")
        return

    if not functions:
        if update_existing:
            print("  ℹ️  No functions found (even with --update-existing)")
        else:
            print("  ✅ All functions already have verbose docstrings")
        return

    print(f"  Found {len(functions)} functions for critical documentation:")
    for lineno, name, _ in functions:
        print(f"    - {name} (line {lineno})")

    if force_context:
        print("  🔊 Context-forcing print() statements will be added")

    print(f"  🤖 Using model: {model}")
    print("  🔬 CRITICAL MODE: Processing one function at a time with verification")

    if dry_run:
        print("  🏃 DRY RUN - No files will be modified")
        return

    # Process each function individually for critical accuracy
    for lineno, func_name, code in functions:
        print(f"  🔬 Deep analysis of {func_name}...")
        print(f"  🤔 ULTRATHINKING documentation for {func_name}...")
        print(f"  ✓ Verifying accuracy for {func_name}...")
        # Collect deterministic metadata early for visibility and potential reuse
        try:
            from agentspec.collect import collect_metadata
            _meta_preview = collect_metadata(filepath, func_name)
            if _meta_preview and _meta_preview.get('changelog'):
                # Show top changelog entry as a quick sanity check
                print(f"  🧾 Changelog head: {_meta_preview['changelog'][0]}")
        except Exception as e:
            print(f"  ⚠️  Metadata pre-collection failed for {func_name}: {e}")
        
        # Generate with critical verification
        final = generate_critical_docstring(
            code=code,
            filepath=str(filepath),
            func_name=func_name,
            model=model,
            base_url=base_url,
            provider=provider,
            as_agentspec_yaml=as_agentspec_yaml,
            terse=terse,
            diff_summary=diff_summary
        )

        # Metadata already injected by generate_critical_docstring()
        final_with_metadata = final

        # Safe insertion
        from agentspec.generate import insert_docstring_at_line
        ok = insert_docstring_at_line(filepath, lineno, func_name, final_with_metadata, force_context)
        if ok:
            print(f"  ✅ {func_name}: Added verified docstring with deterministic metadata")
        else:
            print(f"  ❌ {func_name}: Failed syntax validation - docstring not inserted")


def extract_function_info_critical(
    filepath: Path,
    update_existing: bool = False,
    require_agentspec: bool = False
) -> List[Tuple[int, str, str]]:
    '''
    ```python
    """
    Extract function definitions from Python source via AST, returning (line_number, name, source) tuples sorted descending for safe batch modifications.

    WHAT:
    - Parses file into AST, identifies FunctionDef and AsyncFunctionDef nodes, extracts source via line boundaries (node.lineno to node.end_lineno).
    - Filters by priority cascade: update_existing=True processes all functions; else checks agentspec marker presence or docstring length (<5 lines triggers extraction).
    - Returns tuples sorted descending by line number to enable safe bottom-to-top batch insertions without line offset drift.

    WHY:
    - AST parsing guarantees accurate function boundaries across decorators, nested functions, and multiline signatures; regex fails on all three.
    - Descending sort prevents line number invalidation during sequential modifications—modifying bottom-to-top preserves line references for remaining functions.
    - Dual-mode filtering (full regeneration via update_existing vs. selective marker-based targeting) supports both aggressive and conservative docstring workflows.

    GUARDRAILS:
    - DO NOT alter descending sort; breaks line number validity for batch insertions.
    - DO NOT replace AST parsing with regex; fails on decorators, nested functions, multiline signatures.
    - ALWAYS handle both FunctionDef and AsyncFunctionDef node types.
    - ALWAYS extract source using AST line boundaries (node.lineno, node.end_lineno), never pattern matching.
    - ALWAYS return (lineno, name, code) tuple format for downstream compatibility.
    - DO NOT use ast.walk() for ordered traversal; use ast.iter_child_nodes() or manual recursion if order matters.
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: ast.get_docstring, ast.parse, ast.walk, existing.split, f.read, functions.append, functions.sort, isinstance, join, len, open, source.split
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    # Code-Change Analysis

    **Commit 1 (2025-10-30 - chore(lint)):**
    Suppress line-length linting to permit verbose AGENTSPEC output.

    **Commit 2 (2025-10-30 - updated max tokens):**
    Remove function; token limit adjustment (context unclear from diff).

    **Commit 3 (2025-10-30 - feat: enhance docstring generation):**
    Restore function; support optional dependencies and CLI enhancements.

    '''
    with open(filepath, "r") as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if update_existing:
                # CRITICAL: When update_existing=True, process ALL functions
                needs = True
            else:
                # Normal logic: check if needs docstring
                existing = ast.get_docstring(node)
                if require_agentspec:
                    needs = (not existing) or ("---agentspec" not in existing)
                else:
                    needs = (not existing) or (len(existing.split("\n")) < 5)

            if needs:
                # Get source code
                lines = source.split("\n")
                func_lines = lines[node.lineno - 1:node.end_lineno]
                code = "\n".join(func_lines)
                functions.append((node.lineno, node.name, code))

    # Sort by line number DESCENDING (bottom to top)
    functions.sort(key=lambda x: x[0], reverse=True)

    return functions
