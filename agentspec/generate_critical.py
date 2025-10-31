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
    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    # Commit Analysis

    **Commit 1 (2025-10-30 - fix(critical)):**
    Enforce strict format validation for commit hashes in diff summaries.

    **Commit 2 (2025-10-30 - chore(lint)):**
    Add comprehensive metadata injection and format validation for YAML/plain text.

    **Commit 3 (2025-10-30 - updated max tokens):**
    Increase LLM token limits for richer critical documentation generation.

    **Commit 4 (2025-10-30 - feat: enhance CLI):**
    Switch from changelog diffs to function-scoped code diffs with WHY analysis.

    DEPENDENCIES (from code analysis):
    Calls: Path, ValueError, any, base_prompt.format, called_meta.get, collect_function_code_diffs, collect_metadata, d.get, diff_summaries_text.split, expected_pattern.match, generate_chat, get, inject_deterministic_metadata, json.dumps, len, line.startswith, line.strip, meta.get, print, re.compile, re.search, valid_lines.append
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints (3eb8b6b)
    - 2025-10-30: updated max toxens  on criitcal flag (496c4e3)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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
      - ALWAYS process functions in descending line number order before insertion.
      - ALWAYS verify syntax before insertion to prevent corrupting source files.
      - ALWAYS inject deterministic metadata after LLM generation, never before.
      - ALWAYS pass model, base_url, provider through to generate_critical_docstring for flexible LLM selection.
      - ALWAYS distinguish three empty-result scenarios with specific console messages (no functions found, all documented, syntax error).
      - ALWAYS preserve emoji-prefixed console output structure for CI/CD regex parsing.
      """
      ```

    DEPENDENCIES (from code analysis):
    Calls: _meta_preview.get, collect_metadata, extract_function_info_critical, generate_critical_docstring, insert_docstring_at_line, len, print, str
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints (3eb8b6b)
    - 2025-10-30: updated max toxens  on criitcal flag (496c4e3)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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
        """
        ```

    DEPENDENCIES (from code analysis):
    Calls: ast.get_docstring, ast.parse, ast.walk, existing.split, f.read, functions.append, functions.sort, isinstance, join, len, open, source.split
    Imports: __future__.annotations, ast, json, pathlib.Path, typing.List, typing.Optional, typing.Tuple

    CHANGELOG (from git history):
    - 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)
    - 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)

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
