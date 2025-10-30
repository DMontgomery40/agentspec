#!/usr/bin/env python3
"""
Ultra-accurate generation mode for critical files.
Processes functions individually with deep metadata analysis and multi-pass verification.

CRITICAL: This module ensures deps and changelog are NEVER LLM-generated.
They are programmatically inserted from collected metadata.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import ast
import re


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

ULTRATHINK and document:
1. WHAT this code does (be exhaustive, cover all edge cases)
2. WHY this approach was chosen (design decisions, tradeoffs)
3. GUARDRAILS that prevent breaking changes

Reference the provided metadata to inform your narrative, but don't copy deterministic fields.

This is CRITICAL code. Your documentation could prevent production incidents. ULTRATHINK."""

CRITICAL_SYSTEM_PROMPT_TERSE = """You are operating in CRITICAL DOCUMENTATION MODE - TERSE OUTPUT.

YOU GENERATE (narrative only):
- **what**: Core behavior, key edge cases (concise)
- **why**: Main rationale, critical tradeoffs (concise)
- **guardrails**: Essential constraints only (one line each)

YOU DO NOT GENERATE:
- **deps**: Programmatically inserted from AST
- **changelog**: Programmatically inserted from git

Document CONCISELY but include ALL sections above. This is CRITICAL code."""


def inject_deterministic_metadata(llm_output: str, metadata: Dict[str, Any], as_agentspec_yaml: bool) -> str:
    """Injects deterministic metadata (dependencies and changelog) into LLM-generated docstrings.
    
    CRITICAL: This function ensures deps and changelog are NEVER LLM-generated.
    They are programmatically inserted from collected metadata.
    
    NOTE: This is intentionally duplicated in both generate.py and generate_critical.py
    because they are independent execution paths that must not depend on each other.
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
        if "why:" in llm_output or "why |" in llm_output:
            # Inject deps before why
            output = re.sub(
                r'(\n\s*why[:\|])',
                deps_yaml + r'\1',
                llm_output,
                count=1
            )
        else:
            # Fallback: inject after what section
            output = re.sub(
                r'(\n\s*what:.*?\n(?:\s+.*\n)*)',
                r'\1' + deps_yaml,
                llm_output,
                count=1,
                flags=re.DOTALL
            )

        # Inject changelog after guardrails or at end
        if "---/agentspec" in output:
            output = output.replace("---/agentspec", changelog_yaml + "    ---/agentspec")
        else:
            output += changelog_yaml

        return output
    else:
        # Regular format: append deps and changelog as sections
        deps_text = "\n\nDEPENDENCIES (from code analysis):\n"
        if deps_data.get('calls'):
            deps_text += "Calls: " + ", ".join(deps_data['calls']) + "\n"
        if deps_data.get('imports'):
            deps_text += "Imports: " + ", ".join(deps_data['imports']) + "\n"

        changelog_text = "\n\nCHANGELOG (from git history):\n"
        if changelog_data:
            for entry in changelog_data:
                changelog_text += f"{entry}\n"
        else:
            changelog_text += "No git history available\n"

        return llm_output + deps_text + changelog_text


def generate_critical_docstring(
    code: str,
    filepath: str,
    func_name: str,
    model: str = "claude-3-5-sonnet-20241022",
    base_url: Optional[str] = None,
    provider: str = 'auto',
    as_agentspec_yaml: bool = False,
    terse: bool = False,
    diff_summary: bool = False,
) -> str:
    """
    Brief one-line description.

    Generates exhaustively verified critical docstrings for Python functions using a two-pass LLM workflow with deterministic metadata injection.

    WHAT THIS DOES:
    - Executes a sophisticated two-pass LLM documentation pipeline: first pass generates narrative fields (what/why/guardrails) at temperature 0.1 with deep reasoning enabled, second pass verifies narrative accuracy at temperature 0.0 with deterministic metadata as reference
    - Collects deterministic metadata (function dependencies, calls, imports, changelog) from the target file using `collect_metadata()`, then recursively analyzes the dependency chain for each called function, distinguishing between methods/external calls (dot-notation) and internal functions
    - Constructs a critical prompt that explicitly instructs the LLM to generate ONLY narrative fields and NOT to generate deps/changelog sections, which will be injected programmatically afterward
    - Performs recursive dependency chain analysis with try-except wrapping to gracefully handle functions not found in file, marking them as "not_found_in_file" and distinguishing external/method calls via dot-notation detection
    - Injects deterministic metadata into the final LLM output using `inject_deterministic_metadata()`, ensuring deps and changelog fields contain accurate, non-hallucinated data sourced from actual code analysis
    - Returns the final docstring with verified narrative content and injected deterministic metadata, optionally formatted as AGENTSPEC_YAML if `as_agentspec_yaml=True`
    - Edge cases: handles missing metadata gracefully (defaults to empty dict), manages functions with no dependency chain, truncates changelog to first 2 items to prevent token bloat, wraps recursive metadata collection in try-except to prevent cascading failures, and includes debug output showing pre/post-injection state

    DEPENDENCIES:
    - Called by: [Inferred to be called by documentation generation orchestration layer or CLI tools that need critical-mode docstring generation]
    - Calls: `Path()` (pathlib), `collect_metadata()` (agentspec.collect), `generate_chat()` (agentspec.llm, called twice with different temperatures), `inject_deterministic_metadata()` (agentspec.generate), `json.dumps()` (stdlib), `base_prompt.format()` (string formatting), `meta.get()` and `called_meta.get()` (dict access), `print()` (debug output)
    - Imports used: `__future__.annotations`, `ast`, `json`, `pathlib.Path`, `re`, `typing.Any`, `typing.Dict`, `typing.List`, `typing.Optional`
    - External services: LLM provider (Claude or configurable via `provider` parameter), accessed through `generate_chat()` with configurable `base_url`

    WHY THIS APPROACH:
    - **Separation of concerns**: LLM generates only narrative reasoning (what/why/guardrails) while deterministic fields (deps/changelog) are sourced from static code analysis and injected programmatically, preventing hallucination of technical metadata
    - **Two-pass verification workflow**: First pass at temperature 0.1 enables deep reasoning ("ULTRATHINK") for narrative generation; second pass at temperature 0.0 performs deterministic verification against code and metadata, catching inaccuracies before injection
    - **Recursive dependency chain analysis**: Provides LLM with context about called functions' own dependencies and changelogs (truncated to 2 items), enabling more accurate "why" reasoning without overwhelming token budget; dot-notation detection distinguishes external/method calls that cannot be analyzed in-file
    - **Explicit "DO NOT generate" instructions**: Repeated 5 times in critical_prompt to override LLM's tendency to hallucinate technical metadata; metadata is marked "for your reference - DO NOT copy" to reinforce this boundary
    - **Metadata-as-reference pattern**: Deterministic metadata is provided to LLM as context for narrative reasoning but explicitly excluded from output, then injected by code as single source of truth
    - **Graceful error handling**: Try-except wrapping around recursive `collect_metadata()` calls prevents one missing function from cascading into complete failure; "not_found_in_file" markers allow LLM to reason about external dependencies
    - **Performance considerations**: O(n) dependency chain analysis where n = number of called functions; JSON serialization overhead is acceptable given the critical nature of output; changelog truncation to 2 items balances context richness against token budget
    - **Alternatives NOT used**: Single-pass generation would allow hallucination of deps/changelog; temperature 0.0 for both passes would reduce reasoning quality; omitting dependency chain context would weaken narrative accuracy; not injecting metadata would require manual post-processing

    CHANGELOG:
    - Current implementation: Two-pass LLM workflow with recursive dependency analysis, explicit "DO NOT generate" instructions, and programmatic deterministic metadata injection to prevent hallucination of technical fields while enabling deep reasoning for narrative documentation.

    AGENT INSTRUCTIONS:
    - DO NOT modify the two-pass structure (first_pass at temperature 0.1, final at temperature 0.0) without understanding that verification pass is actual code, not optional scaffolding
    - DO NOT remove or weaken the "DO NOT generate deps/changelog" instructions in critical_prompt—they appear 5 times intentionally to override LLM defaults
    - DO NOT bypass the `inject_deterministic_metadata()` call—it is the sole mechanism ensuring deps and changelog fields contain accurate, non-hallucinated data
    - DO NOT change the metadata reference format ("for your reference - DO NOT copy")—this exact phrasing is critical for LLM instruction following
    - DO NOT modify the recursive dependency analysis logic without accounting for: circular dependency risks, dot-notation method/external call distinction, changelog truncation to prevent token bloat, and try-except wrapping for missing functions
    - DO NOT alter the prompt template selection logic (`as_agentspec_yaml` parameter)—it determines which base prompt is used and must be forwarded correctly
    - DO NOT remove the `collect_metadata()` call—it is the source of truth for deterministic fields
    - ALWAYS forward `base_url` and `provider` parameters to both `generate_chat()` calls (first_pass and final) to ensure consistent LLM configuration
    - ALWAYS include `CRITICAL_SYSTEM_PROMPT` in the system role of the first_pass call—it sets the tone for critical-mode reasoning
    - ALWAYS preserve the debug output (print statements showing pre/post-injection state)—they are essential for verifying metadata injection correctness
    - NOTE: This function is designed for "critical code" documentation where hallucination of technical metadata is unacceptable; the two-pass workflow and explicit metadata injection are non-negotiable safeguards
    - NOTE: The recursive dependency chain analysis can be expensive for functions with many dependencies; consider caching `collect_metadata()` results if this function is called repeatedly on the same codebase
    - NOTE: LLM output quality depends heavily on the quality of `base_prompt` template and `CRITICAL_SYSTEM_PROMPT`; changes to either should be tested thoroughly
    """
    from agentspec.collect import collect_metadata
    from agentspec.llm import generate_chat
    from agentspec.generate import GENERATION_PROMPT, GENERATION_PROMPT_TERSE, AGENTSPEC_YAML_PROMPT

    # Collect deterministic metadata
    print(f"  📊 Collecting deep metadata for {func_name}...")
    meta = collect_metadata(Path(filepath), func_name) or {}

    # Analyze dependency chain
    deps_calls = meta.get('deps', {}).get('calls', [])
    call_chain_meta = {}

    for called_func in deps_calls:
        if '.' in called_func:
            call_chain_meta[called_func] = {"type": "method_or_external"}
        else:
            try:
                called_meta = collect_metadata(Path(filepath), called_func)
                if called_meta:
                    call_chain_meta[called_func] = {
                        "calls": called_meta.get('deps', {}).get('calls', []),
                        "changelog": called_meta.get('changelog', [])[:2]
                    }
            except Exception:
                call_chain_meta[called_func] = {"type": "not_found_in_file"}

    metadata_json = json.dumps(meta, indent=2)
    chain_json = json.dumps(call_chain_meta, indent=2) if call_chain_meta else "No dependency chain found"

    # Choose prompt template
    if as_agentspec_yaml:
        base_prompt = AGENTSPEC_YAML_PROMPT
    elif terse:
        base_prompt = GENERATION_PROMPT_TERSE
    else:
        base_prompt = GENERATION_PROMPT

    # Build prompt that explicitly tells LLM NOT to generate deps/changelog
    critical_prompt = f"""CRITICAL MODE: Document narrative fields ONLY.

CODE TO DOCUMENT:
```python
{code}
```

DETERMINISTIC METADATA (for your reference - DO NOT copy into output):
{metadata_json}

DEPENDENCY CHAIN:
{chain_json}

REQUIREMENTS:
1. ULTRATHINK - engage deep reasoning about this code
2. Generate ONLY: 'what', 'why', 'guardrails' sections
3. DO NOT generate 'deps' or 'changelog' - they will be inserted by code
4. Base your narrative on code analysis and provided metadata
5. Be exhaustively thorough - this is critical code

{base_prompt.format(code=code, filepath=filepath, hard_data="(deterministic fields will be injected by code)")}

ULTRATHINK about accuracy. Generate narrative fields only."""

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
Return ONLY the docstring content that will be inserted into the file.

If the documentation is already accurate, return it unchanged.
If corrections are needed, return the corrected version in the same format."""

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

    # CRITICAL: Inject deterministic metadata programmatically
    print(f"\n  🔧 DEBUG: About to inject metadata")
    print(f"  📊 Collected metadata:")
    print(json.dumps(meta, indent=2))
    print(f"\n  📝 LLM output BEFORE injection:")
    print("="*80)
    print(final)
    print("="*80)
    print(f"  🔍 LLM output has 'changelog:': {'changelog:' in final}")
    print(f"  🔍 LLM output has 'deps:': {'deps:' in final}")

    final_with_metadata = inject_deterministic_metadata(final, meta, as_agentspec_yaml)

    print(f"\n  ✅ AFTER injection:")
    print("="*80)
    print(final_with_metadata)
    print("="*80)

    # If diff_summary requested, make separate LLM call to summarize git diffs
    if diff_summary:
        from agentspec.collect import collect_changelog_diffs
        diffs = collect_changelog_diffs(Path(filepath), func_name)
        
        if diffs:
            print(f"  📊 Collecting diff summaries for {func_name}...")
            # Build prompt for LLM to summarize diffs
            diff_prompt = "Summarize these git diffs concisely (one line per commit):\n\n"
            for d in diffs:
                diff_prompt += f"Commit: {d['date']} - {d['message']}\n"
                diff_prompt += f"Diff:\n{d['diff']}\n\n"
            
            # Separate API call for diff summaries
            summary_system_prompt = (
                "You are a code change summarizer. For each commit, provide a SHORT one-line summary (max 10 words)."
                if terse else
                "You are a code change summarizer. For each commit, provide a one-line summary of what changed."
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
            
            # Inject diff summary section
            diff_summary_section = f"\n\nCHANGELOG DIFF SUMMARY (LLM-generated):\n{diff_summaries_text}\n"
            final_with_metadata += diff_summary_section

    return final_with_metadata


def process_file_critical(
    filepath: Path,
    dry_run: bool = False,
    force_context: bool = False,
    model: str = "claude-3-5-sonnet-20241022",
    as_agentspec_yaml: bool = False,
    base_url: Optional[str] = None,
    provider: str = 'auto',
    update_existing: bool = False,
    terse: bool = False,
    diff_summary: bool = False,
) -> None:
    """
    Brief one-line description: Processes a Python source file to inject ultra-accurate, AI-agent-consumable docstrings with deterministic metadata into functions lacking verbose documentation.

    WHAT THIS DOES:
    - Executes a three-phase pipeline: (1) AST-based extraction of functions needing documentation via `extract_function_info_critical()`, (2) per-function LLM generation with deterministic metadata injection via `generate_critical_docstring()` followed by safe insertion via `insert_docstring_at_line()`, and (3) dry-run safety check that returns early without file modification if `dry_run=True`
    - Parses the target file for syntax errors and returns immediately if parsing fails, preventing cascade failures on malformed Python
    - Distinguishes three empty-result scenarios with specific console messaging: (a) no functions found even with `--update-existing` flag, (b) all functions already have verbose docstrings (normal completion), (c) file syntax error (early abort)
    - Processes functions in bottom-to-top line order (confirmed by code comment) to preserve line number validity during sequential insertions, ensuring later insertions do not invalidate earlier line references
    - Wraps each function's generation and insertion in individual try-except blocks to isolate per-function failures and allow batch processing to continue despite individual errors
    - Conditionally injects context-forcing print() statements into generated docstrings when `force_context=True`, enabling AI agents to trace execution flow
    - Passes model, base_url, and provider parameters through to downstream generation functions, enabling flexible LLM provider selection (auto-detection or explicit specification)
    - Returns `None` after completion (or early return on error/dry-run); all side effects are console output and conditional file modification
    - Produces structured console output with emoji prefixes (📄, 🔬, 🛡️, ✅, ❌, ⚠️, 🤖) for machine-parseable CI/CD integration and human readability

    DEPENDENCIES:
    - Called by: [Inferred from context: likely CLI entry point or orchestration layer in agentspec/main.py or similar]
    - Calls: `extract_function_info_critical()` (AST extraction with update_existing flag), `generate_critical_docstring()` (LLM generation with deterministic metadata), `insert_docstring_at_line()` (safe docstring insertion with syntax validation), `len()` (function count), `print()` (console output), `str()` (type conversion)
    - Imports used: `__future__.annotations` (PEP 563 deferred evaluation), `ast` (syntax parsing, implicit via extract_function_info_critical), `json` (metadata serialization, implicit via generate_critical_docstring), `pathlib.Path` (file path abstraction), `re` (regex, implicit via extraction/insertion), `typing.Any`, `typing.Dict`, `typing.List`, `typing.Optional` (type hints)
    - External services: LLM provider (Claude 3.5 Sonnet by default, or configurable via `provider` and `base_url` parameters); provider selection is delegated to `generate_critical_docstring()`

    WHY THIS APPROACH:
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

    CHANGELOG:
    - Current implementation: Orchestrates three-phase pipeline (extraction, generation, insertion) with bottom-to-top processing, per-function error isolation, dry-run safety, and deterministic metadata injection for AI-agent-consumable docstrings.

    AGENT INSTRUCTIONS:
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
    """
    from agentspec.generate import insert_docstring_at_line

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
    print(f"  🔬 CRITICAL MODE: Processing one function at a time with verification")

    if dry_run:
        print("\n  DRY RUN - No files will be modified")
        return

    # Process functions one at a time (already sorted bottom-to-top)
    for lineno, name, code in functions:
        print(f"\n  🔬 Deep analysis of {name}...")
        try:
            # Generate with critical accuracy and deterministic metadata injection
            docstring = generate_critical_docstring(
                code=code,
                filepath=str(filepath),
                func_name=name,
                model=model,
                base_url=base_url,
                provider=provider,
                as_agentspec_yaml=as_agentspec_yaml,
                terse=terse,
                diff_summary=diff_summary,
            )

            # Insert with same safety mechanisms
            ok = insert_docstring_at_line(filepath, lineno, name, docstring, force_context)

            if ok:
                if force_context:
                    print(f"  ✅ {name}: Added verified docstring with deterministic metadata + context print")
                else:
                    print(f"  ✅ {name}: Added verified docstring with deterministic metadata")
            else:
                print(f"  ⚠️ {name}: Skipped (syntax safety check failed)")

        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")


def extract_function_info_critical(
    filepath: Path,
    update_existing: bool = False,
    require_agentspec: bool = False
) -> List[tuple[int, str, str]]:
    """
    Brief one-line description.

    Parses a Python source file into an Abstract Syntax Tree (AST), identifies all function definitions (sync and async), applies priority-based filtering logic to determine which functions require documentation, extracts complete source code for each selected function with line number metadata, and returns results sorted in descending line order to enable safe batch file modifications.

    WHAT THIS DOES:
    - Parses a Python source file into an Abstract Syntax Tree (AST) and identifies all function definitions, including both synchronous (ast.FunctionDef) and asynchronous (ast.AsyncFunctionDef) functions using ast.walk() for complete tree traversal
    - Applies priority-based filtering logic to determine which functions require documentation:
      1. **update_existing=True**: Selects ALL functions in the file regardless of existing docstrings or other flag values; used for bulk re-documentation workflows where every function must be processed
      2. **update_existing=False + require_agentspec=True**: Selects functions that either lack docstrings entirely OR have docstrings that do not contain the "---agentspec" marker; used for agent-spec compliance validation and enforcement
      3. **update_existing=False + require_agentspec=False** (default mode): Selects functions that either lack docstrings entirely OR have docstrings with fewer than 5 lines when split by newline; used for initial documentation of underdocumented code
    - Extracts the complete source code for each selected function by slicing the original source lines using AST line number metadata (node.lineno for start, node.end_lineno for end), preserving all formatting, decorators, and implementation details
    - Returns a list of tuples in the format (line_number, function_name, source_code) sorted in DESCENDING line order (bottom-to-top), which is critical for enabling safe in-place file modifications without invalidating line numbers of unprocessed functions
    - Handles nested functions correctly; ast.walk() traverses the entire tree depth-first, so nested functions are extracted independently with their own accurate line numbers and complete source text
    - Edge case: When update_existing=True, both require_agentspec and the 5-line threshold are completely ignored; this is intentional for bulk workflows but may be unexpected if flags are combined without understanding the priority ordering
    - Edge case: Docstring detection relies on ast.get_docstring() which returns None for functions without docstrings; the falsy check (not existing) correctly triggers selection
    - Edge case: Line number accuracy depends on AST end_lineno attribute (available in Python 3.8+); if end_lineno is None in malformed AST, the slice will fail silently or produce incomplete code
    - Edge case: Empty files or files with no functions return an empty list without error
    - Edge case: Multiline docstrings are evaluated by splitting on '\n', so a triple-quoted docstring spanning 4 lines will be considered underdocumented in default mode
    - Edge case: File encoding defaults to system encoding; non-UTF-8 files will raise UnicodeDecodeError
    - Returns empty list if no functions match the filtering criteria

    DEPENDENCIES:
    - Called by: [Inferred from filename "generate_critical.py": likely called by documentation generation orchestration code that processes multiple files and aggregates results]
    - Calls: ast.parse, ast.walk, isinstance, ast.get_docstring, str.split, str.join, list.append, list.sort
    - Imports used: __future__.annotations, ast, pathlib.Path, typing.List, typing.Optional (inferred from type hints)
    - External services: None; operates entirely on local file I/O and in-memory AST processing

    WHY THIS APPROACH:
    - **AST-based extraction over regex or string parsing**: AST parsing is semantically correct and handles arbitrarily complex Python syntax including decorators, type hints, nested scopes, string literals containing "def", and complex formatting that would break regex-based approaches. Regex cannot reliably distinguish between function definitions and string content, making AST the only robust solution for production-grade code analysis.
    - **Priority-based filtering with update_existing as master override**: The update_existing flag acts as a master override rather than an independent mode, enabling two distinct workflows: (1) bulk re-documentation of ALL functions when update_existing=True, and (2) selective documentation based on agentspec compliance or documentation quality when update_existing=False. This design prevents accidental flag conflicts (e.g., setting both update_existing=True and require_agentspec=True and expecting agentspec filtering) and ensures predictable, unambiguous behavior across different documentation scenarios.
    - **Descending sort order (bottom-to-top)**: Critical for safe batch modifications. When documentation is inserted or replaced in-place, modifying from bottom to top preserves line numbers of unprocessed functions above. Ascending order would invalidate line numbers after the first modification, causing subsequent modifications to target wrong locations or fail entirely. This is a non-negotiable requirement for any downstream code that performs in-place file edits.
    - **Full source code extraction instead of just signatures**: Returning the complete function source (not just name and signature) enables AI agents to analyze implementation details, context, and complexity when generating documentation, resulting in higher-quality and more accurate docstrings that reflect actual behavior rather than just interface contracts.
    - **Line number tuple format (lineno, name, code)**: Provides both human-readable identification (function name) and machine-processable positioning (line number) for downstream modification logic, enabling callers to locate and replace functions in the original file with precision while maintaining code structure integrity.
    - **Handling both sync and async functions identically**: Using isinstance() check for both ast.FunctionDef and ast.AsyncFunctionDef ensures that async functions are processed with the same filtering and extraction logic as synchronous functions, preventing accidental omission of async code from documentation pipelines and ensuring comprehensive coverage of modern Python codebases.

    CHANGELOG:
    - Current implementation: Parses Python files using AST to identify and filter functions based on documentation status (update_existing, require_agentspec, or 5-line threshold), extracts complete source code with line numbers, and returns results sorted in descending order for safe batch modifications.

    AGENT INSTRUCTIONS:
    - DO NOT modify the descending sort order (reverse=True) without updating all downstream code that depends on bottom-to-top processing; ascending order will cause line number invalidation during batch modifications and break file editing workflows
    - DO NOT change the filtering logic without understanding the priority ordering: update_existing=True overrides all other flags and filtering criteria unconditionally
    - DO NOT combine update_existing=True with require_agentspec=True expecting agentspec filtering; update_existing=True will unconditionally select all functions regardless of agentspec status or documentation quality
    - DO NOT remove the isinstance() check for both ast.FunctionDef and ast.AsyncFunctionDef; async functions must be processed identically to synchronous functions to ensure complete coverage
    - DO NOT modify the line slicing logic (node.lineno - 1:node.end_lineno) without extensive testing on nested functions, decorated functions, multiline signatures, and edge cases; off-by-one errors will produce incomplete or incorrect source extraction
    - DO NOT change the return type from List[tuple[int, str, str]] without updating all callers that unpack (lineno, name, code); changing tuple structure will break downstream code that depends on positional unpacking
    - DO NOT remove the ast.get_docstring() call; it correctly handles edge cases like docstrings that are not the first statement in a function and distinguishes between actual docstrings and regular string literals
    - ALWAYS preserve the priority-based filtering logic even if refactoring for performance or clarity; the update_existing flag is critical for supporting different documentation workflows and must remain the master override
    - ALWAYS test with files containing nested functions, async functions, functions with complex decorators, functions with multiline signatures, and functions with various docstring formats (single-line, multiline, missing, malformed)
    - ALWAYS verify that line numbers remain valid after sorting and that descending order is preserved in all test cases
    - ALWAYS handle the case where end_lineno is None (rare but possible in malformed AST); consider adding defensive checks if robustness is critical for production use
    - NOTE: This function is marked "critical" in the filename; changes may affect production documentation generation pipelines and should be reviewed carefully before deployment
    - NOTE: The 5-line threshold in default mode is arbitrary and may need tuning based on actual documentation quality metrics and user feedback; consider making this configurable if threshold adjustments become frequent
    - NOTE: ast.get_docstring() returns None for functions without docstrings; the falsy check (not existing) is intentional and correct, and it properly handles the distinction between missing docstrings and empty docstrings
    - NOTE
    """
    with open(filepath, 'r') as f:
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
                    needs = (not existing) or (len(existing.split('\n')) < 5)

            if needs:
                # Get source code
                lines = source.split('\n')
                func_lines = lines[node.lineno - 1:node.end_lineno]
                code = '\n'.join(func_lines)
                functions.append((node.lineno, node.name, code))

    # Sort by line number DESCENDING (bottom to top)
    functions.sort(key=lambda x: x[0], reverse=True)

    return functions
