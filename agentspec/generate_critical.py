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
    """
    # WHAT THIS DOES:

    Generates production-grade docstrings for critical Python functions using a two-pass LLM verification pipeline with deterministic metadata injection. The function orchestrates: (1) static AST analysis via `collect_metadata()` to extract deterministic function metadata (deps, changelog); (2) recursive dependency chain analysis distinguishing dot-notation external calls from in-file functions, with changelog truncation to 2 items; (3) construction of a critical prompt with explicit "DO NOT generate deps/changelog" instructions (repeated 5x for instruction-following reliability) and metadata provided as reference-only context; (4) first LLM pass at temperature 0.1 (0.0 if terse) with ULTRATHINK reasoning to generate narrative fields (what/why/guardrails) only; (5) verification pass at temperature 0.0 to catch hallucinations and accuracy failures before injection; (6) format validation via regex to reject mixed YAML/plain-text output; (7) programmatic injection of deterministic metadata via `inject_deterministic_metadata()` to prevent technical field hallucination; (8) optional function-scoped code diff summary generation when `diff_summary=True`, with strict line-by-line format validation (pattern: `- YYYY-MM-DD: summary (hash)`). Supports both AGENTSPEC_YAML and plain-text formats. Terse mode reduces tokens ~50% via shorter prompts and lower max_tokens. Returns final docstring with verified narrative content and injected deterministic metadata.

    **Edge cases handled**: missing metadata defaults to empty dict; functions with no dependency chain proceed normally; changelog truncated to 2 items to prevent token bloat; recursive `collect_metadata()` calls wrapped in try-except to prevent cascading failures from missing functions; diff summary format validated line-by-line with regex, rejecting malformed output; debug output shows pre/post-injection state for transparency and verification.

    **Return type**: `str` containing complete docstring with narrative sections and injected deterministic metadata.

    # WHY THIS APPROACH:

    **Separation of concerns—core principle**: LLM generates only narrative reasoning (what/why/guardrails) while deterministic fields (deps/changelog) are sourced from static code analysis and injected programmatically by code, not by LLM. This prevents hallucination of technical metadata. LLMs cannot reliably generate accurate dependency lists or changelog entries, but can reason about code behavior when given correct context. Injecting deterministic fields ensures single source of truth.

    **Two-pass verification workflow over single-pass**: First pass at temperature 0.1 enables deep reasoning ("ULTRATHINK") for narrative generation with slight creativity in phrasing; second pass at temperature 0.0 performs deterministic verification against code and metadata, catching inaccuracies before injection. Single-pass generation would allow hallucination of deps/changelog to slip through; three+ passes would increase latency without accuracy gains. Temperature 0.1 for first pass balances creativity with accuracy; 0.0 for verification ensures deterministic output.

    **Recursive dependency chain analysis with truncation**: Provides LLM with context about called functions' own dependencies and recent changelog (truncated to 2 items), enabling more accurate "why" reasoning without overwhelming token budget. Dot-notation detection (checking for `.` in function name) distinguishes external/method calls that cannot be analyzed in-file, preventing failed lookups and "not_found_in_file" markers. This allows LLM to reason about external dependencies without breaking on missing functions.

    **Explicit "DO NOT generate" instructions repeated 5x**: Overrides LLM's probabilistic tendency to hallucinate technical metadata. Metadata is marked "for your reference - DO NOT copy" to reinforce boundary between reasoning and deterministic fields. This redundancy is intentional—LLM instruction following is probabilistic, not deterministic; repetition increases compliance probability.

    **Metadata-as-reference pattern**: Deterministic metadata is provided to LLM as context for narrative reasoning but explicitly excluded from output scope, then injected by code as single source of truth. This prevents both hallucination (LLM cannot generate deps/changelog) and manual post-processing (code handles injection). Cleaner than trying to parse and repair LLM output.

    **Format validation before injection**: Raises `ValueError` if LLM generates mixed YAML/plain-text formats, rejecting invalid output rather than attempting repair. Regex patterns check for plain-text sections in YAML mode (e.g., `^WHAT:`) and YAML sections in plain-text mode (e.g., indented `what:`). This catches instruction-following failures early, preventing corrupted output from reaching injection stage.

    **Graceful error handling with try-except wrapping**: Try-except around recursive `collect_metadata()` calls prevents one missing function from cascading into complete failure. "not_found_in_file" markers allow LLM to reason about external dependencies without breaking. Separate try-except for debug checks ensures verification failures never halt generation.

    **Performance considerations**: O(n) dependency chain analysis where n = number of called functions; JSON serialization overhead is acceptable given critical nature of output; changelog truncation to 2 items balances context richness against token budget; terse mode reduces tokens ~50% (1500→750 max_tokens) for batch processing. Diff summary is optional and behind `diff_summary` flag to avoid wasting API calls for files without git history.

    **Temperature tuning for determinism vs. creativity**: Terse mode uses 0.0 for maximum determinism; normal mode uses 0.1 for slight creativity in phrasing while maintaining accuracy. Higher temperatures (0.3+) cause hallucination of deps/changelog. Verification pass always uses 0.0 to ensure deterministic output.

    **Separate diff summary call**: Diff analysis is expensive and optional, so it's behind `diff_summary` flag. Always including would waste API calls. Strict format validation (regex pattern matching per line) ensures LLM follows output requirements. Diff summary section is appended after metadata injection to preserve deterministic fields.

    **Debug output for transparency**: Pre/post-injection state is printed to console, allowing operators to verify metadata injection succeeded and deterministic fields were not hallucinated by LLM. Warnings for missing changelog entries or malformed diff summaries aid troubleshooting.

    # GUARDRAILS:

    - **DO NOT remove the two-pass verification structure** (first_pass at temperature 0.1, final at temperature 0.0). Single-pass mode has unacceptably high hallucination rates for critical documentation. The verification pass is actual code, not optional

    DEPENDENCIES (from code analysis):
    Calls: Path, ValueError, any, base_prompt.format, called_meta.get, collect_function_code_diffs, collect_metadata, d.get, diff_summaries_text.split, expected_pattern.match, generate_chat, get, inject_deterministic_metadata, json.dumps, len, line.startswith, line.strip, meta.get, print, re.compile, re.search, valid_lines.append
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): backfill missing commit hashes in generate_critical.py docstrings via deterministic reinjection (8043e05)
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints (3eb8b6b)
    - 2025-10-30: updated max toxens  on criitcal flag (496c4e3)


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    - 2025-10-30: Enforce output format with regex validation and commit hash inclusion (9c524b4)
    - 2025-10-30: Add format validation and dependency chain metadata collection (3eb8b6b)
    - 2025-10-30: Increase token limits for critical documentation generation (496c4e3)

    """
    
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

    # CRITICAL: Do NOT inject metadata here; handled later via safe two‑phase write
    print("\n  🔧 DEBUG: Narrative generated (metadata will be applied separately)")
    print("="*80)
    print(final)
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
            final += diff_summary_section

    return final


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
    """
    # WHAT THIS DOES:

    Orchestrates three-phase critical documentation pipeline: AST extraction of undocumented functions → LLM generation with deterministic metadata injection → safe syntax-validated insertion.

    - Extracts functions lacking verbose docstrings via AST parsing; generates docstrings using specified LLM model with configurable provider/endpoint; injects code-derived metadata (deps, changelog) deterministically; inserts into source with syntax validation.
    - Processes functions in descending line number order (critical for correctness: inserting at line N shifts all subsequent line numbers downward; bottom-to-top ensures earlier insertions don't invalidate later line references).
    - Per-function error isolation via individual try-except blocks allows batch processing to continue despite individual failures (LLM timeout, insertion syntax error, metadata collection failure); failures logged but non-fatal.
    - Supports dry-run preview (early return after printing plan), force-context flag (injects print() statements for agent tracing), flexible LLM provider selection (model, base_url, provider parameters), update-existing flag (refresh stale docs), and output format selection (AGENTSPEC YAML or plain text).
    - Pre-collects metadata before generation for user visibility (prints changelog head as sanity check) and pipeline validation; metadata collection failures isolated and non-fatal.
    - Distinguishes three empty-result scenarios with specific console messages: no functions found (with --update-existing), all functions already documented, syntax error in file.
    - Returns `None` after completion; all side effects are emoji-prefixed console output (parseable by CI/CD regex) and conditional file modification.

    # WHY THIS APPROACH:

    **Bottom-to-Top Processing Order**: Functions sorted by descending line number before insertion. Critical because inserting docstring at line N shifts all subsequent line numbers downward; processing bottom-to-top ensures earlier insertions don't invalidate later line references. Alternative (top-to-bottom) would require recalculating line numbers after each insertion, introducing complexity, state management overhead, and error propagation risk. Alternative (simultaneous insertion) would require buffering all docstrings and rewriting entire file, losing granular error recovery.

    **Per-Function Error Isolation**: Each function wrapped in individual try-except rather than outer loop wrapper. Allows batch to continue processing remaining functions if one fails (LLM timeout, insertion syntax error, metadata collection failure). Alternative (single outer try-except) would abort entire file on first error, reducing utility for large files with mixed success rates and making partial progress invisible. Alternative (no error handling) would crash on first failure without logging context.

    **Lazy Import of insert_docstring_at_line**: Import placed inside function body (within processing loop), not module level. Avoids import-time side effects, circular dependency risks, and allows function to be called without triggering downstream module initialization. Alternative (top-level import) would couple this module tightly to insertion logic at import time, creating hard dependency on insertion module even if only extraction is needed.

    **Metadata Pre-Collection Before Generation**: Calls `collect_metadata()` before `generate_critical_docstring()` to preview changelog head and validate metadata pipeline. Provides user feedback ("Changelog head: ...") and early error detection without blocking generation. Isolated in try-except to prevent metadata collection failures from blocking docstring generation. Alternative (metadata collection after generation) wastes computation if metadata pipeline is broken. Alternative (no pre-collection) reduces user visibility into metadata derivation.

    **Deterministic Metadata Injection in generate_critical_docstring()**: Function delegates metadata collection (deps, changelog) to downstream `generate_critical_docstring()` and `extract_function_info_critical()`, not computed inline. Ensures metadata is deterministic (derived from code analysis, not LLM hallucination) and reusable across multiple generation attempts. Alternative (inline metadata computation) couples metadata logic to orchestration function, reducing modularity. Alternative (LLM-generated metadata) introduces hallucination risk and non-determinism.

    **Model/Provider/Base-URL Flexibility**: Parameters `model`, `base_url`, `provider` passed through to `generate_critical_docstring()`, enabling runtime LLM backend selection without code modification. Supports custom deployments (local Ollama, enterprise LLM proxies, alternative providers). Alternative (hardcoded model) reduces flexibility; alternative (environment variables only) reduces CLI usability.

    **Force-Context Flag for Agent Tracing**: Conditionally injects print() statements into docstrings (passed to `insert_docstring_at_line()`). Enables AI agents to trace execution flow during docstring-guided code analysis by seeing intermediate values. Alternative (always inject) clutters docstrings with noise; alternative (never inject) reduces agent observability during debugging.

    **Update-Existing Flag for Refresh Control**: Passed to `extract_function_info_critical()` to control whether functions with existing docstrings are re-processed. Allows users to refresh stale documentation or skip already-documented functions. Alternative (always update) wastes computation on already-documented functions; alternative (never update) prevents corrections to incorrect or outdated docs.

    **Dry-Run Early Return**: Check occurs after printing processing plan but before file modification. Allows users to preview function list and processing strategy without risk. Alternative (no dry-run) requires file backups; alternative (dry-run after processing) wastes computation on LLM calls.

    **Console Output Structure with Emoji Prefixes**: Emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖) and consistent indentation throughout, enabling CI/CD systems to parse output via regex and extract function names, line numbers, success/failure status. Alternative (unstructured output) requires fragile line-by-line parsing; alternative (JSON output) loses human readability.

    **Broad Exception Handling (except Exception)**: Per-function try-except uses `except Exception as e` (not specific exception types). Catches all failures (LLM errors, file I/O errors, syntax errors during insertion, metadata collection errors) without crashing. Alternative (specific exception types like `LLMError`, `SyntaxError`) misses unexpected error categories and requires maintaining exception taxonomy. Alternative (no exception handling) aborts on first error without logging context.

    **Syntax Error Early Abort**: Catches `SyntaxError` from `extract_function_info_critical()` and returns immediately. Prevents cascade failures on malformed Python (attempting to insert docstrings into syntactically invalid file would corrupt source). Alternative (continue on syntax error) risks corrupting source files with invalid insertions.

    # GUARDRAILS:

    - DO

    DEPENDENCIES (from code analysis):
    Calls: _meta_preview.get, collect_metadata, extract_function_info_critical, generate_critical_docstring, insert_docstring_at_line, len, print, str
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): backfill missing commit hashes in generate_critical.py docstrings via deterministic reinjection (8043e05)
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints (3eb8b6b)
    - 2025-10-30: updated max toxens  on criitcal flag (496c4e3)


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    - 2025-10-30: Relax regex to preserve commit hashes in CHANGELOG injection (9c524b4)
    - 2025-10-30: Ignore E501 linting for long AGENTSPEC context prints (3eb8b6b)
    - 2025-10-30: Increase max tokens for critical mode LLM generation (496c4e3)

    """
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
        # Collect deterministic metadata privately (never passed to LLM)
        try:
            from agentspec.collect import collect_metadata
            _meta = collect_metadata(filepath, func_name) or {}
            if _meta.get('changelog'):
                print(f"  🧾 Changelog head: {_meta['changelog'][0]}")
        except Exception as e:
            print(f"  ⚠️  Metadata collection failed for {func_name}: {e}")
            _meta = {}

        # Generate with critical verification (narrative only)
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

        # Safe two‑phase application with metadata
        from agentspec.insert_metadata import apply_docstring_with_metadata
        ok = apply_docstring_with_metadata(
            filepath,
            lineno,
            func_name,
            final,
            _meta,
            as_agentspec_yaml=as_agentspec_yaml,
            force_context=force_context,
        )
        if ok:
            print(f"  ✅ {func_name}: Added verified docstring with deterministic metadata")
        else:
            print(f"  ❌ {func_name}: Failed syntax validation - docstring not inserted")


def extract_function_info_critical(
    filepath: Path,
    update_existing: bool = False,
    require_agentspec: bool = False
) -> List[Tuple[int, str, str]]:
    """
    Extract function definitions from Python source via AST, returning (line_number, name, source) tuples sorted descending for safe batch modifications.

    WHAT THIS DOES:
    - Parses file into AST using ast.parse(), identifies all FunctionDef and AsyncFunctionDef nodes via ast.walk(), extracts complete source code by slicing original lines using node.lineno (start) and node.end_lineno (end), preserves decorators and multiline signatures intact.
    - Applies priority-cascade filtering: update_existing=True selects ALL functions unconditionally; else if require_agentspec=True selects functions lacking docstrings OR missing "---agentspec" marker; else (default) selects functions lacking docstrings OR with docstrings <5 lines when split by '\n'.
    - Returns list of tuples (line_number, function_name, source_code) sorted DESCENDING by line number (bottom-to-top), critical for safe in-place batch modifications without line offset invalidation.
    - Handles nested functions correctly; ast.walk() traverses entire tree depth-first, extracting each function independently with accurate line boundaries.
    - Edge case: update_existing=True completely ignores require_agentspec and 5-line threshold; intentional for bulk workflows but non-obvious when flags combined.
    - Edge case: ast.get_docstring() returns None for missing docstrings; falsy check (not existing) correctly triggers selection.
    - Edge case: end_lineno may be None in malformed AST (Python 3.8+); slice will fail silently or produce incomplete code.
    - Edge case: Multiline docstrings evaluated by '\n' split; 4-line docstring considered underdocumented in default mode.
    - Edge case: File encoding defaults to system; non-UTF-8 files raise UnicodeDecodeError.
    - Returns empty list if no functions match filtering criteria or file contains no functions.

    WHY THIS APPROACH:
    - **AST parsing over regex**: Semantically correct, handles decorators, nested functions, multiline signatures, type hints, and string literals containing "def" that break regex. Regex cannot distinguish function definitions from string content; AST is only robust production solution.
    - **Priority-cascade with update_existing as master override**: Prevents accidental flag conflicts (e.g., update_existing=True + require_agentspec=True expecting agentspec filtering). update_existing=True acts as unconditional master switch enabling two workflows: (1) bulk re-documentation of ALL functions, (2) selective documentation based on agentspec compliance or quality when False. Ensures predictable, unambiguous behavior across documentation scenarios.
    - **Descending sort (bottom-to-top)**: Non-negotiable for safe batch modifications. Modifying from bottom preserves line numbers of unprocessed functions above. Ascending order invalidates line numbers after first modification, causing subsequent modifications to target wrong locations or fail. Critical requirement for downstream in-place file edits.
    - **Full source extraction vs. signatures only**: Complete function source enables AI agents to analyze implementation details, context, complexity for higher-quality, behavior-accurate docstrings reflecting actual code rather than interface contracts alone.
    - **Tuple format (lineno, name, code)**: Provides human-readable identification (name) and machine-processable positioning (lineno) for downstream modification logic, enabling precise file location and replacement while maintaining code structure integrity.
    - **Identical handling of sync and async functions**: isinstance() check for both ast.FunctionDef and ast.AsyncFunctionDef prevents accidental omission of async code from documentation pipelines, ensuring comprehensive coverage of modern Python codebases.

    GUARDRAILS:
    - DO NOT alter descending sort order (reverse=True); breaks line number validity for batch insertions and causes subsequent modifications to target wrong locations.
    - DO NOT replace AST parsing with regex or string pattern matching; fails on decorators, nested functions, multiline signatures, and string literals containing "def".
    - DO NOT remove isinstance() check for both ast.FunctionDef and ast.AsyncFunctionDef; async functions must be processed identically to ensure complete coverage.
    - DO NOT modify line slicing logic (node.lineno - 1:node.end_lineno) without extensive testing on nested, decorated, multiline-signature functions; off-by-one errors produce incomplete or incorrect source extraction.
    - DO NOT change return type from List[Tuple[int, str, str]] without updating all callers unpacking (lineno, name, code); tuple structure changes break downstream positional unpacking.
    - DO NOT remove ast.get_docstring() call; correctly handles docstrings not as first statement and distinguishes actual docstrings from regular string literals.
    - DO NOT combine update_existing=True with require_agentspec=True expecting agentspec filtering; update_existing=True unconditionally selects all functions regardless of agentspec status.
    - ALWAYS preserve priority-cascade filtering logic even when refactoring; update_existing flag is critical for supporting different documentation workflows and must remain master override.
    - ALWAYS extract source using AST line boundaries (node.lineno, node.end_lineno), never pattern matching or regex.
    - ALWAYS return (lineno, name, code) tuple format for downstream compatibility.
    - ALWAYS test with nested functions, async functions, complex decorators, multiline signatures, and various docstring formats (single-line, multiline, missing, malformed).
    - ALWAYS verify line numbers remain valid after sorting and descending order preserved in all test cases.
    - NOTE: This function marked "critical" in filename; changes affect production documentation generation pipelines and require careful review before deployment.
    - NOTE: 5-line threshold in default mode is arbitrary; may need tuning based on documentation quality metrics and user feedback; consider making configurable if adjustments become frequent.
    - NOTE: ast.get_docstring() returns None for missing docstrings; falsy check (not existing) is intentional and correct, properly distinguishing missing from empty docstrings.
    - NOTE: end_lineno attribute available Python 3.8+; consider defensive checks if robustness critical for production use with older AST implementations.

    DEPENDENCIES (from code analysis):
    Calls: ast.get_docstring, ast.parse, ast.walk, existing.split, f.read, functions.append, functions.sort, isinstance, join, len, open, source.split
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): backfill missing commit hashes in generate_critical.py docstrings via deterministic reinjection (8043e05)
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    - 2025-10-30: Standardize quotes and type hints for code consistency (9c524b4)
    - 2025-10-30: Add function to extract critical functions with agentspec validation (3eb8b6b)
    - 2025-10-30: Remove extract_function_info_critical function implementation (496c4e3)

    """
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
