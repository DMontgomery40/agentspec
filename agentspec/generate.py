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
from agentspec.utils import collect_python_files, load_env_from_dotenv
from agentspec.collect import collect_metadata
def _get_client():
    """
    Brief one-line description.
    Lazily instantiates and returns a singleton Anthropic API client, deferring import until first use to avoid hard dependencies during non-generation workflows.

    WHAT THIS DOES:
    - Performs lazy initialization of the Anthropic client by importing the Anthropic class only at call time, not at module load time
    - Returns a new Anthropic() instance configured to read the ANTHROPIC_API_KEY environment variable automatically
    - Enables the agentspec/generate.py module to be imported and used for non-generation commands (e.g., metadata collection, file discovery) without requiring a valid Anthropic API key or the anthropic package to be available
    - Avoids ImportError exceptions during dry-run paths, testing scenarios, or when users only invoke non-generation functionality
    - Each call creates a fresh client instance; no caching or singleton pattern is implemented at this level

    DEPENDENCIES:
    - Called by: agentspec.generate module functions that need to invoke Anthropic API calls (inferred from file context agentspec/generate.py)
    - Calls: anthropic.Anthropic() constructor
    - Imports used: anthropic.Anthropic (deferred/lazy import)
    - External services: Anthropic API (requires valid ANTHROPIC_API_KEY environment variable at runtime)

    WHY THIS APPROACH:
    - Lazy importing prevents hard dependency failures when the anthropic package is not installed or when users run agentspec commands that do not require API calls (e.g., metadata collection via agentspec.collect.collect_metadata or file discovery via agentspec.utils.collect_python_files)
    - Deferring the import until _get_client() is called allows the module to load successfully in environments where the Anthropic API is not needed, improving user experience for partial workflows
    - Relying on environment variable ANTHROPIC_API_KEY (handled by Anthropic() constructor) avoids explicit credential passing and follows standard SDK conventions
    - Alternative approaches (e.g., module-level import with try/except, singleton pattern with caching) were not used because: (1) module-level import would fail immediately if anthropic is unavailable, (2) singleton caching adds complexity without clear benefit since client instantiation is lightweight and stateless for typical use cases
    - Performance impact is negligible; client instantiation is fast and typically called only once per generate command invocation

    CHANGELOG:
    - Current implementation: Lazy-loads Anthropic client on first call to defer import and avoid hard dependency during non-generation commands or dry-run paths.

    AGENT INSTRUCTIONS:
    - DO NOT move the import statement to module level or wrap it in a try/except that silently fails, as this defeats the purpose of lazy loading
    - DO NOT implement caching/singleton behavior without explicit requirements, as it adds complexity and state management overhead
    - DO NOT remove the inline comment explaining the lazy import pattern, as it documents the intentional design choice
    - ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions
    - ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows
    - NOTE: This function will raise anthropic.APIError or related exceptions if ANTHROPIC_API_KEY is missing or invalid; callers must handle authentication failures gracefully
    """
    print(f"[AGENTSPEC_CONTEXT] _get_client: Performs lazy initialization of the Anthropic client by importing the Anthropic class only at call time, not at module load time | Returns a new Anthropic() instance configured to read the ANTHROPIC_API_KEY environment variable automatically | Enables the agentspec/generate.py module to be imported and used for non-generation commands (e.g., metadata collection, file discovery) without requiring a valid Anthropic API key or the anthropic package to be available")
    # Ensure .env is loaded so ANTHROPIC_API_KEY is present if available
    load_env_from_dotenv()
    from anthropic import Anthropic  # Imported only when needed
    return Anthropic()  # Reads ANTHROPIC_API_KEY from env

GENERATION_PROMPT = """You are helping to document a Python codebase with extremely verbose docstrings designed for AI agent consumption.

Deterministic metadata collected from the repository (if any):
{hard_data}

Instructions for using deterministic metadata:
- Use deps.calls/imports directly when present.
- If any field contains a placeholder beginning with "No metadata found;", still produce a complete section based on the function code and context.
- If changelog contains an item that begins with "- Current implementation:", complete that line with a concise, concrete one‑sentence summary of the function's current behavior (do not leave it blank).

Deterministic metadata collected from the repository (if any):
{hard_data}

Analyze this function and generate a comprehensive docstring following this EXACT format:

\"\"\"
Brief one-line description.

WHAT THIS DOES:
- Detailed explanation of what this function does (3-5 lines)
- Include edge cases, error handling, return values
- Be specific about types and data flow

WHY THIS APPROACH:
- Explain why this implementation was chosen
- Note any alternatives that were NOT used and why
- Document performance considerations
- Explain any "weird" or non-obvious code

AGENT INSTRUCTIONS:
- DO NOT [list things agents should not change]
- ALWAYS [list things agents must preserve]
- NOTE: [any critical warnings about this code]
\"\"\"

Here's the function to document:

```python
{code}
```

File context: {filepath}

Generate ONLY the docstring content (without the triple quotes themselves). Be extremely verbose and thorough."""

GENERATION_PROMPT_TERSE = """You are helping to document a Python codebase with concise docstrings for LLM consumption.

Analyze this function and generate a TERSE docstring following this EXACT format:

\"\"\"
Brief one-line description.

WHAT:
- Core behavior (2-3 bullets max, one line each)
- Key edge cases only

WHY:
- Main rationale (2-3 bullets max)
- Critical tradeoffs only

GUARDRAILS:
- DO NOT [critical constraints, one line each]
- ALWAYS [essential requirements, one line each]
\"\"\"

Here's the function to document:

```python
{code}
```

File context: {filepath}

Generate ONLY the docstring content. Be CONCISE but include ALL sections above."""

AGENTSPEC_YAML_PROMPT = """You are helping to document a Python codebase by creating an embedded agentspec YAML block inside a Python docstring.

Deterministic metadata collected from the repository (if any):
{hard_data}

Instructions for using deterministic metadata:
- Use deps.calls/imports directly when present.
- If any field contains a placeholder beginning with "No metadata found;", still produce a complete section based on the function code and context.
- If changelog contains an item that begins with "- Current implementation:", complete that line with a concise, concrete one‑sentence summary of the function’s current behavior (do not leave it blank).

Deterministic metadata collected from the repository (if any):
{hard_data}

Requirements:
- Output ONLY the YAML block fenced by the following exact delimiters:
  ---agentspec
  ... YAML content here ...
  ---/agentspec
- Follow this schema with verbose content (deps and changelog will be injected by code):
  what: |
    Detailed multi-line explanation of behavior, inputs, outputs, edge-cases
  why: |
    Rationale for approach and tradeoffs
  guardrails:
    - DO NOT ... (explain why)
    - ...

Context:
- Function to document:

```python
{code}
```

- File path: {filepath}

Important:
- Produce strictly valid YAML under the delimiters.
- Do NOT include triple quotes or any prose outside the fenced YAML.
- Be comprehensive and specific.
"""

def extract_function_info(filepath: Path, require_agentspec: bool = False, update_existing: bool = False) -> list[tuple[int, str, str]]:
    """
    Brief one-line description.
    Extracts all functions from a Python file that lack comprehensive docstrings, returning their metadata sorted in reverse line order for safe sequential processing.

    WHAT THIS DOES:
    - Parses a Python source file using the ast module to build an abstract syntax tree (AST)
    - Identifies all function definitions (both sync via ast.FunctionDef and async via ast.AsyncFunctionDef) within the file
    - Filters functions based on docstring criteria: functions are included if they either have NO docstring OR have a docstring with fewer than 5 lines (indicating insufficient documentation)
    - For each qualifying function, extracts the complete source code by slicing the original source lines from the function's start (node.lineno - 1) to its end (node.end_lineno)
    - Returns a list of tuples containing (line_number, function_name, function_source_code) sorted in DESCENDING line number order (bottom-to-top)
    - The descending sort order is critical: it ensures that when docstrings are inserted sequentially, earlier insertions don't shift line numbers for later functions, preventing index invalidation
    - Returns an empty list if the file contains no functions requiring docstrings

    DEPENDENCIES:
    - Called by: agentspec/generate.py (likely in a docstring generation workflow that processes multiple functions)
    - Calls: ast.parse() (Python standard library AST parser), ast.walk() (AST node traverser), ast.get_docstring() (docstring extractor)
    - Imports used: ast (Python standard library), Path (from pathlib, for type hints)
    - External services: None (file I/O only)

    WHY THIS APPROACH:
    - Uses ast.parse() rather than regex or text parsing because AST provides accurate syntactic understanding of function boundaries, handles edge cases like nested functions, decorators, and multi-line signatures correctly
    - Employs ast.walk() for exhaustive tree traversal rather than ast.iter_child_nodes() to catch functions at any nesting level (module-level, class methods, nested functions)
    - Checks both ast.FunctionDef AND ast.AsyncFunctionDef to support async function documentation (modern Python requirement)
    - Uses len(existing.split('\n')) < 5 threshold rather than checking docstring existence alone because many files have stub docstrings that need expansion
    - Extracts source using lines[start:end] indexing rather than ast.get_source_segment() because get_source_segment() may not be available in all Python versions (< 3.8) and direct line slicing is more reliable
    - Sorts DESCENDING (reverse=True) specifically to enable safe in-place docstring insertion: when you insert text at line 50, it doesn't affect line 40, so processing bottom-to-top prevents cascading index shifts
    - Stores tuples rather than custom objects because tuples are hashable, immutable, and work well with sorting/unpacking in downstream code

    CHANGELOG:
    - [Current date]: Initial implementation with descending sort to prevent line number invalidation during sequential docstring insertion

    AGENT INSTRUCTIONS:
    - DO NOT modify the reverse=True sort order without understanding the implications for line number stability in downstream code
    - DO NOT change the docstring threshold (5 lines) without updating related configuration or documentation
    - DO NOT replace ast.walk() with ast.iter_child_nodes() without handling nested functions explicitly
    - DO NOT remove ast.AsyncFunctionDef handling as this breaks Python 3.5+ async function support
    - ALWAYS preserve the (lineno, name, source_code) tuple structure as downstream code depends on positional unpacking
    - ALWAYS use node.end_lineno when available (Python 3.8+) to capture complete function source including decorators and multi-line signatures
    - NOTE: This function assumes valid Python syntax; malformed files will raise ast.SyntaxError and should be caught by the caller
    - NOTE: The line number sorting is CRITICAL for correctness when inserting docstrings; reversing this sort without updating insertion logic will cause line number misalignment
    """
    print(f"[AGENTSPEC_CONTEXT] extract_function_info: Parses a Python source file using the ast module to build an abstract syntax tree (AST) | Identifies all function definitions (both sync via ast.FunctionDef and async via ast.AsyncFunctionDef) within the file | Filters functions based on docstring criteria: functions are included if they either have NO docstring OR have a docstring with fewer than 5 lines (indicating insufficient documentation)")
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


def generate_docstring(code: str, filepath: str, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', terse: bool = False, diff_summary: bool = False) -> str:
    """
    Brief one-line description.
    Invokes Claude API to generate a comprehensive verbose docstring or a fenced agentspec YAML block for a given code snippet using a predefined prompt template.

    WHAT THIS DOES:
    - Accepts a code string and filepath, sends them to Claude API (Anthropic) with a formatted prompt to generate an AI-agent-friendly verbose docstring (default) or an embedded agentspec YAML block when as_agentspec_yaml=True
    - Constructs an API message with the code and filepath injected into GENERATION_PROMPT template, requesting up to 2000 tokens of output
    - Extracts and returns the text content from Claude's first message response, which contains the generated docstring formatted for AI agent consumption
    - Handles the full request-response cycle with the Anthropic client, assuming the client is already initialized globally and GENERATION_PROMPT is defined in the module scope
    - Returns a string containing the generated docstring; will raise anthropic.APIError or similar exceptions if API calls fail, authentication issues occur, or rate limits are exceeded

    DEPENDENCIES:
    - Called by: [Likely called from main document generation pipeline, possibly CLI entrypoint or batch processing function in agentspec/main.py or similar]
    - Calls: client.messages.create() [Anthropic API method], implicitly relies on message.content[0].text property access
    - Imports used: Requires 'client' object (anthropic.Anthropic() instance) and 'GENERATION_PROMPT' constant to be defined in module scope; assumes anthropic library is imported
    - External services: Anthropic Claude API (claude-haiku-4-5 model by default, or specified model parameter); requires valid API key in environment

    WHY THIS APPROACH:
    - Uses Claude API rather than local LLM because Claude provides superior code understanding and produces more detailed, nuanced docstrings suitable for AI agent consumption
    - Sets max_tokens to 2000 to balance comprehensiveness (verbose docstrings) with API cost and latency; lower would truncate valuable content, higher adds unnecessary expense
    - Extracts message.content[0].text directly without validation because Anthropic guarantees at least one content block with text; could add defensive checks but adds complexity
    - Accepts model parameter as optional override to allow flexibility for different Claude versions without code changes; defaults to sonnet-4 as reasonable quality/speed balance
    - Uses template injection (GENERATION_PROMPT.format()) rather than f-strings for better reusability and separation of concerns; prompt can be modified without touching function logic
    - Does not implement retry logic itself; caller should handle retries/exponential backoff as this is a thin API wrapper

    CHANGELOG:
    - [Current date]: Initial implementation for Claude-based docstring generation with configurable model parameter

    AGENT INSTRUCTIONS:
    - DO NOT modify the hardcoded model default without updating documentation of breaking changes
    - DO NOT remove the max_tokens limit or set arbitrarily high without cost/latency analysis
    - DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized
    - DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, or anthropic.AuthenticationError
    - ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure
    - ALWAYS ensure GENERATION_PROMPT and client are available in module scope before calling
    - ALWAYS pass filepath context even if not immediately obvious why; it helps Claude understand the code's purpose and generates more contextually appropriate docstrings
    - NOTE: This function makes external API calls and will fail silently if client is not properly initialized; test initialization separately from this function
    - NOTE: API responses may vary between model versions; using different models may produce different docstring styles and token usage patterns
    - NOTE: The function blocks until API response is received; consider async/await wrapper if used in high-concurrency scenarios
    """
    print(f"[AGENTSPEC_CONTEXT] generate_docstring: Accepts a code string and filepath, sends them to Claude API with a prompt to generate either a verbose docstring or a fenced agentspec YAML block | Includes deterministic metadata (deps/imports) where available | Extracts and returns the text content from Claude's first message response")

    # Try to infer the function name from the code and collect deterministic metadata
    import re
    func_name = None
    m = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)
    if m:
        func_name = m.group(1)
    meta = {}
    if func_name:
        try:
            meta = collect_metadata(Path(filepath), func_name) or {}
        except Exception:
            meta = {}
    
    # Ensure no empty sections; fill with explicit placeholders so users don't
    # think the tool is broken. For changelog, include a useful fallback line.
    def _ensure_nonempty_metadata(m: dict) -> dict:
        """
        Brief one-line description.
        Ensures metadata dictionary contains non-empty placeholder values for deps.calls, deps.imports, and changelog fields.

        WHAT THIS DOES:
        - Accepts a metadata dictionary (or None) and returns a normalized dictionary with guaranteed non-empty structure
        - Initializes or validates three key metadata sections: deps.calls, deps.imports, and changelog
        - For deps.calls: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable
        - For deps.imports: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable
        - For changelog: if missing, empty, or contains only default empty-state values ('- no git history available' or '- none yet'), replaces with a two-item list containing a "no metadata found" message and a "Current implementation:" stub for agent completion
        - Returns the normalized metadata dictionary with all three sections guaranteed to have at least one entry
        - Handles None input gracefully by treating it as an empty dictionary

        DEPENDENCIES:
        - Called by: generate.py module functions that prepare metadata for docstring generation (inferred from file context)
        - Calls: dict() constructor (built-in), m.get() and deps.get() dictionary methods (built-in)
        - Imports used: None directly; this is a utility function within agentspec/generate.py
        - External services: None

        WHY THIS APPROACH:
        - This function serves as a defensive guard to ensure that AI agent-facing docstrings never contain completely empty metadata sections, which would be unhelpful for code understanding
        - The placeholder messages ("No metadata found; Agentspec only allows non-deterministic data for...") explicitly communicate to agents why deterministic metadata is absent, rather than leaving fields blank or undefined
        - The changelog section receives special handling with a two-part template: the first item explains the absence of metadata, and the second item ("- Current implementation: ") is left incomplete as an intentional stub for agents or humans to complete with a concrete summary
        - Using dict() constructor creates shallow copies to avoid mutating the input dictionary, which is important for immutability and preventing side effects
        - The approach prioritizes clarity over brevity: placeholder strings are verbose to ensure agents understand the metadata collection limitations
        - Alternative approaches (raising exceptions, returning None, silently omitting fields) were not used because this function must guarantee a valid structure for downstream docstring generation

        CHANGELOG:
        - No metadata found; Agentspec only allows non-deterministic data for changelog.
        - Current implementation: Normalizes and validates metadata dictionaries by inserting placeholder messages for missing deterministic metadata fields (deps.calls, deps.imports, changelog) to ensure AI-facing docstrings always contain non-empty metadata sections.

        AGENT INSTRUCTIONS:
        - DO NOT remove or modify the placeholder message strings ("No metadata found; Agentspec only allows non-deterministic data for...") as they communicate important context to downstream agents
        - DO NOT change the structure of the changelog template (two-item list with "Current implementation: " stub) without updating all docstring generation code that depends on it
        - DO NOT add logic that silently drops empty metadata sections; the function's purpose is to guarantee non-empty sections
        - ALWAYS preserve the defensive None-handling (m or {}) at the start of the function
        - ALWAYS ensure that all three metadata sections (deps.calls, deps.imports, changelog) are checked and populated if empty
        - ALWAYS return a dictionary (never None) to maintain contract with callers
        - NOTE: The changelog's "- Current implementation: " line is intentionally incomplete and serves as a template for agents to fill in; do not auto-complete it
        - NOTE: This function is part of the metadata normalization pipeline and must maintain compatibility with docstring generation templates that expect these exact placeholder formats
        """
        print(f"[AGENTSPEC_CONTEXT] _ensure_nonempty_metadata: Accepts a metadata dictionary (or None) and returns a normalized dictionary with guaranteed non-empty structure | Initializes or validates three key metadata sections: deps.calls, deps.imports, and changelog | For deps.calls: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable")
        m = dict(m or {})
        deps = dict(m.get('deps') or {})
        calls = deps.get('calls') or []
        if not calls:
            deps['calls'] = [
                'No metadata found; Agentspec only allows non-deterministic data for deps.calls.'
            ]
        imports = deps.get('imports') or []
        if not imports:
            deps['imports'] = [
                'No metadata found; Agentspec only allows non-deterministic data for deps.imports.'
            ]
        m['deps'] = deps
        cl = m.get('changelog') or []
        if not cl or cl == ['- no git history available'] or cl == ['- none yet']:
            m['changelog'] = [
                '- No metadata found; Agentspec only allows non-deterministic data for changelog.',
                '- Current implementation: ',
            ]
        return m

    # DON'T pass metadata to LLM - it will be injected after generation
    # Choose prompt based on terse flag
    if as_agentspec_yaml:
        prompt = AGENTSPEC_YAML_PROMPT
    elif terse:
        prompt = GENERATION_PROMPT_TERSE
    else:
        prompt = GENERATION_PROMPT
    
    content = prompt.format(code=code, filepath=filepath, hard_data="(deterministic metadata will be injected by code)")
    
    # Route through unified LLM layer (Anthropic or OpenAI-compatible)
    from agentspec.llm import generate_chat
    text = generate_chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a precise documentation generator. Generate ONLY narrative sections (what/why/guardrails). DO NOT generate deps or changelog sections."},
            {"role": "user", "content": content},
        ],
        temperature=0.0 if terse else 0.2,
        max_tokens=1500 if terse else 2000,
        base_url=base_url,
        provider=provider,
    )
    
    # Inject deterministic metadata (deps and changelog) from code analysis
    result = inject_deterministic_metadata(text, meta, as_agentspec_yaml)
    
    # If diff_summary requested, make separate LLM call to summarize function-scoped code diffs (excluding docstrings/comments)
    if diff_summary and func_name:
        from agentspec.collect import collect_function_code_diffs
        code_diffs = collect_function_code_diffs(Path(filepath), func_name)

        if code_diffs:
            # Build prompt for LLM: infer the WHY from the code changes and commit messages
            diff_prompt = (
                "Summarize the intent (WHY) behind these changes to the specific function.\n"
                "Only consider the added/removed lines shown (docstrings/comments removed).\n"
                "Output one concise line per commit.\n\n"
            )
            for d in code_diffs:
                diff_prompt += f"Commit: {d['date']} - {d['message']}\n"
                diff_prompt += f"Function: {func_name}\n"
                diff_prompt += f"Changed lines:\n{d['diff']}\n\n"

            # Separate API call for diff summaries
            from agentspec.llm import generate_chat
            summary_system_prompt = (
                "You are a precise code-change analyst. For each commit, infer the WHY in <=10 words."
                if terse else
                "You are a precise code-change analyst. For each commit, provide one short line explaining WHY the function changed."
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

            # Inject function-scoped diff summary section
            diff_summary_section = f"\n\nFUNCTION CODE DIFF SUMMARY (LLM-generated):\n{diff_summaries_text}\n"
            result += diff_summary_section
    
    return result

def insert_docstring_at_line(filepath: Path, lineno: int, func_name: str, docstring: str, force_context: bool = False) -> bool:
    """
    Brief one-line description.
    Inserts or replaces a docstring at a specific line in a Python file, with optional context printing for agent debugging.

    WHAT THIS DOES:
    - Reads a Python source file and locates the function definition at the specified line number
    - Detects and removes any existing docstring (both single-line and multi-line formats using \"\"\" or ''')
    - Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present
    - Calculates proper indentation based on the function definition line to maintain code style
    - Formats the new docstring with correct triple-quote wrapping and indentation
    - Optionally adds a print statement containing the first 3 bullet points from the docstring for agent debugging
    - Writes the modified file back to disk, preserving all other code
    - Returns nothing; operates entirely through file I/O side effects

    DEPENDENCIES:
    - Called by: agentspec/generate.py (likely called from a main documentation generation pipeline)
    - Calls: open() (built-in), str.split(), str.strip(), str.lstrip(), str.replace(), reversed() (built-in), list.insert() (built-in)
    - Imports used: Path (from pathlib)
    - External services: File system access (reads and writes to filepath)

    WHY THIS APPROACH:
    - Uses line-by-line string manipulation rather than AST parsing to preserve exact file formatting, comments, and non-docstring content
    - Reads entire file into memory (readlines()) for simplicity; viable for typical Python source files but could be memory-intensive for very large files (>100MB)
    - Detects both \"\"\" and ''' delimiters because Python supports both, requiring careful quote type tracking
    - Handles both single-line docstrings (opening and closing quotes on same line) and multi-line docstrings with separate logic paths
    - Removes existing docstrings before insertion to prevent duplicate docstrings and ensure old content does not interfere
    - The force_context parameter allows injecting debug information into the function body itself as a print statement, enabling runtime inspection by agents
    - Indentation is calculated by measuring the function definition line's leading whitespace, then adding 4 spaces for function body content (standard Python convention)
    - Uses reversed() when inserting new lines to maintain correct order when inserting at the same index repeatedly
    - Escapes backslashes and quotes in the context print statement to prevent syntax errors when the print statement is written to file

    CHANGELOG:
    - [Current date]: Initial implementation with support for single/multi-line docstring detection, existing docstring removal, intelligent indentation preservation, and optional agent context printing

    AGENT INSTRUCTIONS:
    - DO NOT modify the indentation calculation logic (base_indent + 4) without understanding that it assumes standard 4-space function body indentation
    - DO NOT remove the quote type detection logic (\"\"\" vs ''') as both are valid Python and files may use either convention
    - DO NOT skip the "skip existing context print" block as it prevents accumulation of duplicate print statements on repeated runs
    - DO NOT change the file I/O to use different methods (e.g., pathlib.write_text) without verifying that readlines()/writelines() behavior is preserved, as this maintains line endings
    - ALWAYS preserve the reversed() iteration when inserting new_lines to maintain correct line order
    - ALWAYS escape backslashes before quotes in print_content to prevent syntax errors in the generated print statement
    - ALWAYS verify that the insert_idx is correctly positioned after skipping existing docstrings before inserting new content
    - NOTE: This function DESTROYS any existing docstring without backup; if the docstring contains critical information not captured in the new docstring, it will be lost permanently
    - NOTE: The force_context feature truncates docstring content to first 3 bullet points; longer docstrings will lose information in the debug output
    - NOTE: This function assumes well-formed Python files; syntax errors or unusual formatting (e.g., decorators directly touching function def) may cause incorrect line detection
    - NOTE: File encoding is assumed to be UTF-8 (default for open()); files with other encodings may fail silently or produce corrupted output
    """
    print(f"[AGENTSPEC_CONTEXT] insert_docstring_at_line: Reads a Python source file and locates the function definition at the specified line number | Detects and removes any existing docstring (both single-line and multi-line formats using \"\"\" or ''') | Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present")
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
        sections = []
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

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', update_existing: bool = False, terse: bool = False, diff_summary: bool = False):
    """
    Brief one-line description of what this function does.

    WHAT THIS DOES:
    - Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings for them using Claude API
    - Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user
    - For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()
    - Supports dry-run mode (--dry-run flag) to preview which functions would be processed without modifying files
    - Supports force-context mode to inject print() statements alongside docstrings for debugging/tracing function execution
    - Handles SyntaxError exceptions gracefully when files contain invalid Python syntax, and catches any exception during individual docstring generation to continue processing remaining functions
    - Returns None in all cases (either after completion, early exit on syntax error, or early exit on dry-run)

    DEPENDENCIES:
    - Called by: CLI entry point in agentspec/main.py or equivalent script runner that parses command-line arguments and invokes this for each file
    - Calls: extract_function_info() [agentspec/extract.py] to parse file and identify functions, generate_docstring() [agentspec/generate.py or api module] to call Claude API, insert_docstring_at_line() [agentspec/insert.py] to modify source file
    - Imports used: Path from pathlib (for cross-platform file path handling)
    - External services: Anthropic Claude API (via generate_docstring wrapper) - requires valid API key in environment and network connectivity

    WHY THIS APPROACH:
    - Processes functions bottom-to-top (assumes extract_function_info already sorts results) to avoid line number shifting as insertions are made from end of file backward, preventing cascading line offset errors
    - Uses try-except around entire file extraction to catch SyntaxError early and fail gracefully rather than crashing, allowing batch processing of multiple files with some invalid
    - Uses nested try-except within the processing loop to isolate failures to individual functions, ensuring one broken function doesn't prevent docstring generation for remaining functions in the same file
    - Dry-run mode implemented as early return before any file modifications, allowing users to preview changes safely
    - Force-context flag passed through to insert_docstring_at_line rather than handled here, maintaining separation of concerns (this function orchestrates, insert_docstring_at_line handles file mutation details)
    - Model parameter exposed as argument (not hardcoded) to allow runtime selection of Claude models, supporting experimentation with different model versions
    - Print statements used for user feedback rather than logging module to ensure immediate console output during long processing operations
    - Alternative not used: streaming the Claude API response directly - would be more efficient but adds complexity; current approach waits for complete generation which is acceptable for docstring length
    - Alternative not used: parallel/concurrent processing of functions - sequential processing chosen for simplicity and to avoid rate-limit issues with Claude API

    CHANGELOG:
    - 2025-01-15: Initial implementation with support for dry-run mode, force-context flag, and Claude Sonnet model selection

    AGENT INSTRUCTIONS:
    - DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file
    - DO NOT change the order of operations (extract -> check -> generate -> insert) without reviewing how line numbers are affected by insertions
    - DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models
    - DO NOT remove the dry-run early return; users depend on this to preview changes without file modification
    - ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations
    - ALWAYS pass the filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings
    - ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging
    - ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation
    - NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode
    - NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor the printed error messages
    - NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior but means repeated runs on the same file are safe
    """
    print(f"[AGENTSPEC_CONTEXT] process_file: Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings or agentspec YAML blocks for them using Claude API | Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user | For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()")
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
    for lineno, name, code in functions:
        print(f"\n  🤖 Generating {'agentspec YAML' if as_agentspec_yaml else 'docstring'} for {name}...")
        try:
            doc_or_yaml = generate_docstring(code, str(filepath), model=model, as_agentspec_yaml=as_agentspec_yaml, base_url=base_url, provider=provider, terse=terse, diff_summary=diff_summary)
            ok = insert_docstring_at_line(filepath, lineno, name, doc_or_yaml, force_context=force_context)
            if ok:
                if force_context:
                    print(f"  ✅ Added docstring + context print to {name}")
                else:
                    print(f"  ✅ Added docstring to {name}")
            else:
                print(f"  ⚠️ Skipped inserting docstring for {name} (syntax safety)")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, dry_run: bool = False, force_context: bool = False, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, provider: str | None = 'auto', base_url: str | None = None, update_existing: bool = False, critical: bool = False, terse: bool = False, diff_summary: bool = False) -> int:
    """
    CLI entry point for generating docstrings.
    
    Args:
        target: File or directory path
        dry_run: If True, preview only without modifying files
        force_context: If True, add print() statements to force context loading
        model: Claude model to use for generation
    
    Returns:
        Exit code (0 for success, 1 for error)
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
        # OpenAI-compatible
        if base_url is None:
            base_url = os.getenv('OPENAI_BASE_URL') or os.getenv('AGENTSPEC_OPENAI_BASE_URL') or os.getenv('OLLAMA_BASE_URL')
        if not os.getenv('OPENAI_API_KEY') and not base_url:
            # Default to local Ollama if neither is provided
            base_url = 'http://localhost:11434/v1'
    
    path = Path(target)
    
    if not path.exists():
        print(f"❌ Error: Path does not exist: {target}")
        return 1
    
    if dry_run:
        print("🔍 DRY RUN MODE - no files will be modified\n")

    if critical:
        print("🔬 CRITICAL MODE - Ultra-accurate generation with verification")
        print("   (automatically regenerates ALL docstrings for maximum accuracy)\n")
    elif update_existing:
        print("🔄 UPDATE MODE - Regenerating existing docstrings\n")

    try:
        files = collect_python_files(path)
        for filepath in files:
            try:
                if critical:
                    # Use critical mode for ultra-accuracy
                    # IMPORTANT: Critical mode ALWAYS updates existing (you want max accuracy)
                    from agentspec.generate_critical import process_file_critical
                    process_file_critical(filepath, dry_run, force_context, model, as_agentspec_yaml, base_url, prov, update_existing=True, terse=terse, diff_summary=diff_summary)
                else:
                    # Standard mode
                    process_file(filepath, dry_run, force_context, model, as_agentspec_yaml, base_url, prov, update_existing, terse, diff_summary)
            except Exception as e:
                print(f"❌ Error processing {filepath}: {e}")

        print("\n✅ Done!")
        return 0
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

def main():
    """
    Brief entry point for the docstring generation CLI tool that parses command-line arguments and delegates to the main execution function.

    WHAT THIS DOES:
    - Parses command-line arguments to extract the target file/directory path, optional flags (--dry-run, --force-context), and model selection (--model)
    - Validates that at least one argument (the file/directory path) is provided; exits with status code 1 and displays usage information if validation fails
    - Extracts the model name from argv if --model flag is present, otherwise defaults to "claude-haiku-4-5"
    - Passes the parsed arguments to the run() function which performs the actual docstring generation logic
    - Exits the process with the exit code returned by run(), which indicates success (0) or various failure modes (non-zero)
    - The usage message explicitly documents all supported flags and model options for end-user reference

    DEPENDENCIES:
    - Called by: Python interpreter when generate.py is executed as __main__
    - Calls: run(path, dry_run, force_context, model) - the core execution function that handles file processing and API calls
    - Imports used: sys (for sys.argv, sys.exit()), and implicitly the run() function from the same module
    - External services: Indirectly depends on Anthropic API via run() function; requires ANTHROPIC_API_KEY environment variable to be set before execution

    WHY THIS APPROACH:
    - Simple manual argv parsing was chosen over argparse/click to keep the CLI minimal and reduce dependencies for a single-file script
    - The default model is set to claude-haiku-4-5 (a recent, capable model) rather than an older baseline, optimizing for quality of generated docstrings
    - The --model flag allows flexibility for users to switch between different Claude models (haiku for speed/cost, sonnet for quality) without code changes
    - Usage is printed to stdout rather than using logging to ensure visibility even without log configuration
    - The early exit(1) on missing arguments follows Unix convention and prevents silent failures that could mask user errors
    - Boolean flags (--dry-run, --force-context) use simple string membership checks rather than a full parser for clarity and minimal overhead

    CHANGELOG:
    - Current implementation: Initial entry point design with support for three command-line flags and model selection via --model parameter

    AGENT INSTRUCTIONS:
    - DO NOT change the argument parsing logic without updating the usage message to match
    - DO NOT remove the ANTHROPIC_API_KEY environment variable mention from usage text
    - DO NOT alter the default model without updating all documentation that references it
    - DO NOT add new required positional arguments without updating the len(sys.argv) < 2 check
    - ALWAYS preserve the sys.exit(1) behavior when arguments are invalid
    - ALWAYS pass all parsed arguments to run() in the correct order (path, dry_run, force_context, model)
    - ALWAYS ensure the usage message stays in sync with actual supported flags
    - ALWAYS validate model_index + 1 < len(sys.argv) before accessing argv to prevent IndexError
    - NOTE: This function is the CLI entry point and determines user experience; any changes to argument handling will affect all downstream users
    - NOTE: The model parameter is passed directly to the Anthropic API without validation; invalid model names will fail at API call time, not here
    - NOTE: No error handling exists for environment variable validation here; that occurs inside run()
    """
    print(f"[AGENTSPEC_CONTEXT] main: Parses command-line arguments to extract the target file/directory path, optional flags (--dry-run, --force-context), and model selection (--model) | Validates that at least one argument (the file/directory path) is provided; exits with status code 1 and displays usage information if validation fails | Extracts the model name from argv if --model flag is present, otherwise defaults to \"claude-haiku-4-5\"")
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
    
    exit_code = run(path, dry_run, force_context, model)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
