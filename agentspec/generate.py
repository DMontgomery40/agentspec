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
    ---agentspec
    what: |
      Lazily instantiates and returns an Anthropic API client, deferring the import of the Anthropic class until the function is first called rather than at module load time.

      Inputs: None

      Outputs: An Anthropic() instance configured to automatically read the ANTHROPIC_API_KEY environment variable.

      Behavior:
      - Calls load_env_from_dotenv() to ensure environment variables from .env files are loaded
      - Performs a deferred import of the Anthropic class from the anthropic package only at call time
      - Instantiates and returns a new Anthropic() client, which internally reads ANTHROPIC_API_KEY from the environment
      - Each invocation creates a fresh client instance; no caching or singleton pattern is implemented

      Edge cases:
      - If ANTHROPIC_API_KEY is missing or invalid, the Anthropic() constructor will raise anthropic.APIError or related authentication exceptions; callers must handle these gracefully
      - If the anthropic package is not installed, ImportError is raised only when _get_client() is called, not during module import
      - Enables agentspec/generate.py to be imported successfully in environments where the Anthropic API is not needed (e.g., dry-run paths, metadata collection, file discovery)
        deps:
          calls:
            - Anthropic
            - load_env_from_dotenv
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
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
      Lazy loading defers the hard dependency on the anthropic package until it is actually needed, allowing the module to load successfully in non-generation workflows. This approach prevents ImportError exceptions during dry-run scenarios, testing, or when users invoke only non-generation commands such as metadata collection or file discovery.

      The Anthropic() constructor automatically reads ANTHROPIC_API_KEY from the environment, following standard SDK conventions and avoiding the need for explicit credential passing.

      Lightweight client instantiation means performance impact is negligible; the client is typically created only once per generate command invocation.

      Alternative approaches (module-level import with try/except, singleton caching) were rejected because: (1) module-level import would fail immediately if anthropic is unavailable, defeating the purpose of supporting non-generation workflows, and (2) singleton caching adds unnecessary complexity and state management overhead without clear benefit for stateless, lightweight client instantiation.

    guardrails:
      - DO NOT move the import statement to module level or wrap it in a try/except that silently fails; this defeats the lazy-loading purpose and reintroduces hard dependencies during module import
      - DO NOT implement caching or singleton behavior without explicit requirements; it adds complexity and state management overhead without clear benefit
      - DO NOT remove the inline comment explaining the lazy import pattern; it documents the intentional design choice for future maintainers
      - ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions so users understand the credential requirement
      - ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows and partial command invocations
      - ALWAYS handle anthropic.APIError and related authentication exceptions in calling code, as missing or invalid credentials will raise exceptions at runtime

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Performs lazy initialization of the Anthropic client by importing the Anthropic class only at call time, not at module load time"
          - "- Returns a new Anthropic() instance configured to read the ANTHROPIC_API_KEY environment variable automatically"
          - "- Enables the agentspec/generate.py module to be imported and used for non-generation commands (e.g., metadata collection, file discovery) without requiring a valid Anthropic API key or the anthropic package to be available"
          - "- Avoids ImportError exceptions during dry-run paths, testing scenarios, or when users only invoke non-generation functionality"
          - "- Each call creates a fresh client instance; no caching or singleton pattern is implemented at this level"
          - "- Called by: agentspec.generate module functions that need to invoke Anthropic API calls (inferred from file context agentspec/generate.py)"
          - "- Calls: anthropic.Anthropic() constructor"
          - "- Imports used: anthropic.Anthropic (deferred/lazy import)"
          - "- External services: Anthropic API (requires valid ANTHROPIC_API_KEY environment variable at runtime)"
          - "- Lazy importing prevents hard dependency failures when the anthropic package is not installed or when users run agentspec commands that do not require API calls (e.g., metadata collection via agentspec.collect.collect_metadata or file discovery via agentspec.utils.collect_python_files)"
          - "- Deferring the import until _get_client() is called allows the module to load successfully in environments where the Anthropic API is not needed, improving user experience for partial workflows"
          - "- Relying on environment variable ANTHROPIC_API_KEY (handled by Anthropic() constructor) avoids explicit credential passing and follows standard SDK conventions"
          - "- Alternative approaches (e.g., module-level import with try/except, singleton pattern with caching) were not used because: (1) module-level import would fail immediately if anthropic is unavailable, (2) singleton caching adds complexity without clear benefit since client instantiation is lightweight and stateless for typical use cases"
          - "- Performance impact is negligible; client instantiation is fast and typically called only once per generate command invocation"
          - "- Current implementation: Lazy-loads Anthropic client on first call to defer import and avoid hard dependency during non-generation commands or dry-run paths."
          - "- DO NOT move the import statement to module level or wrap it in a try/except that silently fails, as this defeats the purpose of lazy loading"
          - "- DO NOT implement caching/singleton behavior without explicit requirements, as it adds complexity and state management overhead"
          - "- DO NOT remove the inline comment explaining the lazy import pattern, as it documents the intentional design choice"
          - "- ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions"
          - "- ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows"
          - "- NOTE: This function will raise anthropic.APIError or related exceptions if ANTHROPIC_API_KEY is missing or invalid; callers must handle authentication failures gracefully"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API"
        ---/agentspec
    """
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
    '''
    ---agentspec
    what: |
      Parses a Python source file into an abstract syntax tree (AST) and identifies all function definitions requiring documentation. Filters functions based on docstring presence, length, and agentspec marker requirements. Returns a list of (line_number, function_name, source_code) tuples sorted in descending line number order to enable safe sequential docstring insertion without line number invalidation.

      Inputs:
      - filepath: Path object pointing to a valid Python source file
      - require_agentspec: Boolean flag; when True, only functions lacking docstrings or missing the "---agentspec" marker are included
      - update_existing: Boolean flag; when True, forces inclusion of ALL functions regardless of docstring status, bypassing normal filtering logic

      Outputs:
      - List of tuples: (line_number: int, function_name: str, source_code: str)
      - Sorted descending by line_number (bottom-to-top processing order)
      - Empty list if no functions match filtering criteria

      Behavior:
      - Handles both synchronous (ast.FunctionDef) and asynchronous (ast.AsyncFunctionDef) function definitions
      - Traverses entire AST tree to capture module-level, class methods, and nested functions
      - Docstring filtering: includes functions with no docstring OR docstrings shorter than 5 lines (unless require_agentspec=True, which checks for "---agentspec" marker instead)
      - Extracts complete function source including decorators and multi-line signatures using node.lineno and node.end_lineno
      - Descending sort order is critical: prevents line number shifts when inserting docstrings sequentially from bottom to top

      Edge cases:
      - Malformed Python syntax raises ast.SyntaxError (caller responsibility to handle)
      - Functions with stub docstrings (< 5 lines) are treated as underdocumented
      - Nested functions are included in results
      - Async functions receive equal treatment to sync functions
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
            - agentspec.utils.collect_python_files
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
      AST parsing provides accurate syntactic understanding of function boundaries, correctly handling nested functions, decorators, and multi-line signatures where regex or text-based approaches would fail. The descending sort order is essential for correctness: when docstrings are inserted sequentially at specific line numbers, processing bottom-to-top ensures earlier insertions do not shift line numbers for functions processed later, preventing cascading index invalidation. Tuple-based return structure enables efficient positional unpacking and sorting in downstream code. Supporting both FunctionDef and AsyncFunctionDef ensures compatibility with modern Python async patterns. The 5-line threshold balances between detecting stub docstrings and respecting intentionally brief documentation. The update_existing flag provides programmatic control for regeneration workflows without requiring external filtering logic.

    guardrails:
      - DO NOT reverse the sort order without updating all downstream insertion logic, as this will cause line number misalignment and syntax errors during docstring insertion
      - DO NOT change the 5-line docstring threshold without updating related configuration and documentation, as this affects which functions are considered underdocumented
      - DO NOT replace ast.walk() with ast.iter_child_nodes() without explicit handling for nested functions, as iter_child_nodes() only traverses immediate children
      - DO NOT remove ast.AsyncFunctionDef handling, as this breaks support for Python 3.5+ async function documentation
      - DO NOT use ast.get_source_segment() instead of manual line slicing without verifying Python 3.8+ availability across target environments
      - ALWAYS preserve the (lineno, name, source_code) tuple structure, as downstream code depends on positional unpacking
      - ALWAYS use node.end_lineno to capture complete function source including decorators and multi-line signatures
      - ALWAYS validate that the input file contains syntactically valid Python before calling this function
      - NOTE: Line number sorting is CRITICAL for correctness; reversing sort order without updating insertion logic will cause line number misalignment and potential syntax corruption

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Parses a Python source file using the ast module to build an abstract syntax tree (AST)"
          - "- Identifies all function definitions (both sync via ast.FunctionDef and async via ast.AsyncFunctionDef) within the file"
          - "- Filters functions based on docstring criteria: functions are included if they either have NO docstring OR have a docstring with fewer than 5 lines (indicating insufficient documentation)"
          - "- For each qualifying function, extracts the complete source code by slicing the original source lines from the function's start (node.lineno - 1) to its end (node.end_lineno)"
          - "- Returns a list of tuples containing (line_number, function_name, function_source_code) sorted in DESCENDING line number order (bottom-to-top)"
          - "- The descending sort order is critical: it ensures that when docstrings are inserted sequentially, earlier insertions don't shift line numbers for later functions, preventing index invalidation"
          - "- Returns an empty list if the file contains no functions requiring docstrings"
          - "- Called by: agentspec/generate.py (likely in a docstring generation workflow that processes multiple functions)"
          - "- Calls: ast.parse() (Python standard library AST parser), ast.walk() (AST node traverser), ast.get_docstring() (docstring extractor)"
          - "- Imports used: ast (Python standard library), Path (from pathlib, for type hints)"
          - "- External services: None (file I/O only)"
          - "- Uses ast.parse() rather than regex or text parsing because AST provides accurate syntactic understanding of function boundaries, handles edge cases like nested functions, decorators, and multi-line signatures correctly"
          - "- Employs ast.walk() for exhaustive tree traversal rather than ast.iter_child_nodes() to catch functions at any nesting level (module-level, class methods, nested functions)"
          - "- Checks both ast.FunctionDef AND ast.AsyncFunctionDef to support async function documentation (modern Python requirement)"
          - "- Uses len(existing.split('\n')) < 5 threshold rather than checking docstring existence alone because many files have stub docstrings that need expansion"
          - "- Extracts source using lines[start:end] indexing rather than ast.get_source_segment() because get_source_segment() may not be available in all Python versions (< 3.8) and direct line slicing is more reliable"
          - "- Sorts DESCENDING (reverse=True) specifically to enable safe in-place docstring insertion: when you insert text at line 50, it doesn't affect line 40, so processing bottom-to-top prevents cascading index shifts"
          - "- Stores tuples rather than custom objects because tuples are hashable, immutable, and work well with sorting/unpacking in downstream code"
          - "- [Current date]: Initial implementation with descending sort to prevent line number invalidation during sequential docstring insertion"
          - "- DO NOT modify the reverse=True sort order without understanding the implications for line number stability in downstream code"
          - "- DO NOT change the docstring threshold (5 lines) without updating related configuration or documentation"
          - "- DO NOT replace ast.walk() with ast.iter_child_nodes() without handling nested functions explicitly"
          - "- DO NOT remove ast.AsyncFunctionDef handling as this breaks Python 3.5+ async function support"
          - "- ALWAYS preserve the (lineno, name, source_code) tuple structure as downstream code depends on positional unpacking"
          - "- ALWAYS use node.end_lineno when available (Python 3.8+) to capture complete function source including decorators and multi-line signatures"
          - "- NOTE: This function assumes valid Python syntax; malformed files will raise ast.SyntaxError and should be caught by the caller"
          - "- NOTE: The line number sorting is CRITICAL for correctness when inserting docstrings; reversing this sort without updating insertion logic will cause line number misalignment"
          - "-            # Check if needs docstring"
          - "-            existing = ast.get_docstring(node)"
          - "-            if require_agentspec:"
          - "-                needs = (not existing) or ("---agentspec" not in existing)"
          - "-                needs = (not existing) or (len(existing.split('\n')) < 5)"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    Extract information about all functions in a file that need docstrings."
          - "-    Returns list of (lineno, name, source_code) tuples, sorted bottom-to-top."
          - "-            if not existing or len(existing.split('\n')) < 5:"
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors"
          - "-    """Extract the source code for a specific function.""""
          - "-            if node.lineno == lineno:"
          - "-                # Get the function's source code"
          - "-                return '\n'.join(func_lines), node"
          - "-    raise ValueError(f"No function found at line {lineno}")"
          - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API"
        ---/agentspec
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

def inject_deterministic_metadata(llm_output: str, metadata: Dict[str, Any], as_agentspec_yaml: bool) -> str:
    '''
    ---agentspec
    what: |
      Injects deterministic metadata (dependencies and changelog) into LLM-generated docstrings in either YAML or plain text format.

      For YAML format (as_agentspec_yaml=True):
      - Parses deps_data (calls, imports) and changelog_data from metadata dictionary
      - Locates injection point by searching for "why:" or "why |" markers; injects deps section before the first occurrence
      - Falls back to injecting after "what:" section if no "why:" marker found
      - Strips any LLM-generated changelog sections using regex to prevent duplication
      - Injects changelog section before the closing "---/agentspec" tag (or appends if tag absent)
      - Includes "No git history available" placeholder when changelog_data is empty

      For plain text format (as_agentspec_yaml=False):
      - Appends "DEPENDENCIES (from code analysis):" section with Calls and Imports lists
      - Appends "CHANGELOG (from git history):" section with timestamped entries
      - Strips any pre-existing LLM-generated CHANGELOG sections before appending
      - Returns unmodified output if metadata dictionary is empty or falsy

      Edge cases:
      - Handles missing "why:" section by falling back to "what:" injection point
      - Handles missing closing "---/agentspec" tag by appending changelog to end
      - Handles empty deps_data by omitting empty subsections
      - Handles empty changelog_data by inserting placeholder text
        deps:
          calls:
            - deps_data.get
            - join
            - metadata.get
            - output.rfind
            - re.sub
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
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
      Separates deterministic facts (code calls, imports, git history) from LLM-generated reasoning to ensure reproducibility and auditability.
      LLMs frequently hallucinate or ignore instructions about structured metadata, so programmatic injection after generation prevents contamination.
      Two format options support both YAML-embedded agentspec blocks and traditional docstring conventions.
      Regex-based stripping of LLM-generated changelog sections provides defense-in-depth against LLM non-compliance with generation instructions.

    guardrails:
      - DO NOT allow LLM to generate deps or changelog content; always use provided metadata dictionary to ensure facts are never hallucinated
      - ALWAYS strip LLM-generated changelog sections before injecting to prevent duplication and conflicting information
      - ALWAYS inject deps before "why:" section when present; only fall back to "what:" injection if "why:" is absent
      - ALWAYS include "No git history available" placeholder if changelog_data is empty to maintain consistent structure
      - DO NOT modify metadata dictionary in-place; only transform the output string
      - ALWAYS preserve exact YAML formatting (indentation, quotes, markers) to maintain valid agentspec block syntax

        changelog:
          - "- 2025-10-31: fix: relax CHANGELOG replacement regex to handle single-newline boundaries and preserve commit hashes during injection"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Use Claude to generate a verbose docstring.""""
          - "- 2025-10-29: Add --model flag to choose between Claude models (Sonnet/Haiku)"
          - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API"
        ---/agentspec
    '''
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

        # NEVER TRY TO STRIP LLM CONTENT - this violates separation of concerns
        # The injection process must ALWAYS overwrite with deterministic metadata
        # regardless of what the LLM generates. No stripping, no conditional logic.
        
        # FORCEFULLY INJECT changelog - replace any existing changelog sections with deterministic ones
        # This ensures deterministic metadata ALWAYS wins, regardless of LLM behavior
        if "---/agentspec" in output:
            # If there's already a changelog section, replace it
            if "changelog:" in output:
                output = re.sub(
                    r'changelog:.*?(?=---/agentspec)',
                    changelog_yaml.strip(),
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

        if "CHANGELOG (from git history):" in llm_output:
            # Replace existing CHANGELOG section with deterministic content
            llm_output = re.sub(
                r'CHANGELOG \(from git history\):.*?(?=\n+[A-Z]|\Z)',
                changelog_content.rstrip(),
                llm_output,
                flags=re.DOTALL
            )
        else:
            # Append deterministic sections if not already present
            llm_output += "\n\n" + changelog_content

        # Inject deps section (this should come before changelog)
        deps_text = "\n\nDEPENDENCIES (from code analysis):\n"
        if deps_data.get('calls'):
            deps_text += "Calls: " + ", ".join(deps_data['calls']) + "\n"
        if deps_data.get('imports'):
            deps_text += "Imports: " + ", ".join(deps_data['imports']) + "\n"

        if "DEPENDENCIES (from code analysis):" in llm_output:
            llm_output = re.sub(
                r'DEPENDENCIES \(from code analysis\):.*?(?=\n\n(?:CHANGELOG|$)|\Z)',
                deps_text.strip(),
                llm_output,
                flags=re.DOTALL
            )
        else:
            # Insert deps before changelog
            llm_output = llm_output.replace("\n\n" + changelog_content, deps_text + "\n\n" + changelog_content)

        return llm_output


def generate_docstring(code: str, filepath: str, model: str = "claude-haiku-4-5", as_agentspec_yaml: bool = False, base_url: str | None = None, provider: str | None = 'auto', terse: bool = False, diff_summary: bool = False) -> str:
    '''
    ---agentspec
    what: |
      Generates AI-agent-friendly docstrings or embedded agentspec YAML blocks by invoking Claude API with code context and deterministic metadata injection.

      **Inputs:**
      - `code` (str): Source code snippet to document
      - `filepath` (str): Path to the file containing the code (used for context and metadata collection)
      - `model` (str): Claude model identifier; defaults to "claude-haiku-4-5"
      - `as_agentspec_yaml` (bool): If True, generates fenced YAML block; if False, generates verbose narrative docstring
      - `base_url` (str | None): Optional custom LLM endpoint URL for provider routing
      - `provider` (str | None): LLM provider identifier ('auto', 'anthropic', 'openai', etc.); defaults to 'auto'
      - `terse` (bool): If True, uses compact prompt template and lower token limits (1500 vs 2000)
      - `diff_summary` (bool): If True, makes secondary LLM call to infer WHY from function-scoped git diffs

      **Processing flow:**
      1. Extracts function name from code using regex pattern matching
      2. Collects deterministic metadata (deps.calls, deps.imports, changelog) via `collect_metadata()` from code analysis
      3. Normalizes metadata via `_ensure_nonempty_metadata()` to guarantee non-empty sections with placeholder messages
      4. Selects prompt template based on `as_agentspec_yaml` and `terse` flags
      5. Routes through unified LLM layer (`generate_chat()`) with configurable provider and base_url
      6. Injects deterministic metadata into generated text via `inject_deterministic_metadata()`
      7. If `diff_summary=True` and function name found, collects function-scoped code diffs and makes secondary LLM call to summarize WHY changes were made
      8. Appends diff summary section to result if generated

      **Outputs:**
      - Returns complete docstring string (narrative sections only; metadata injected deterministically)
      - Raises `anthropic.APIError`, `anthropic.RateLimitError`, `anthropic.AuthenticationError`, or provider-specific exceptions on API failures
      - Raises `ValueError` or `KeyError` if required module-scope prompts (GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT, GENERATION_PROMPT_TERSE) are undefined

      **Edge cases:**
      - If function name cannot be extracted from code, metadata collection is skipped (meta remains empty dict)
      - If metadata collection fails, exception is caught and meta defaults to empty dict
      - If diff_summary requested but no code diffs found, diff summary section is omitted
      - If provider is 'auto', LLM layer auto-detects based on model name or environment configuration
      - Empty or None metadata sections are replaced with explicit placeholder messages to prevent downstream docstring generation failures
        deps:
          calls:
            - Path
            - collect_function_code_diffs
            - collect_metadata
            - deps.get
            - dict
            - generate_chat
            - inject_deterministic_metadata
            - m.get
            - m.group
            - prompt.format
            - re.search
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
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
      **Rationale for approach:**
      - Claude provides superior code understanding for nuanced, AI-consumable docstrings compared to local LLMs or rule-based approaches
      - Separates LLM generation (narrative only) from deterministic metadata injection to avoid hallucination and ensure accuracy of deps/changelog
      - Unified LLM layer (`generate_chat()`) abstracts provider differences, enabling flexible routing to Anthropic, OpenAI, or other compatible endpoints without code changes
      - Optional `diff_summary` flag enables WHY inference from git history without bloating main generation call or requiring git parsing in primary prompt
      - Terse mode reduces token usage and latency for resource-constrained scenarios while maintaining quality via lower temperature (0.0)
      - Function-scoped diff collection (via `collect_function_code_diffs()`) excludes docstrings/comments to focus on actual logic changes

      **Tradeoffs:**
      - Max tokens set to 2000 (1500 for terse) balances comprehensiveness with API cost and latency; lower values truncate valuable content, higher values add unnecessary expense
      - Temperature set to 0.2 (0.0 for terse) prioritizes consistency over creativity; higher values increase variance in docstring style
      - Metadata normalization uses defensive placeholder messages rather than raising exceptions, ensuring downstream code never encounters empty sections but potentially obscuring collection failures
      - Secondary diff_summary call adds latency and cost but provides richer WHY context without requiring complex multi-turn prompting
      - Regex-based function name extraction is simple but fragile for complex signatures; more robust parsing would require AST analysis

    guardrails:
      - DO NOT pass metadata to LLM during generation; inject only after generation to prevent hallucination of false deps or changelog entries
      - DO NOT remove max_tokens limits without cost/latency analysis; unbounded tokens significantly increase API costs and response time
      - DO NOT modify hardcoded model defaults without updating documentation of breaking changes; users may depend on specific model behavior
      - DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized; prompt templates are module-scoped and may be overridden
      - DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, anthropic.AuthenticationError, or provider-specific exceptions at call site
      - DO NOT remove or modify placeholder message strings ("No metadata found; Agentspec only allows non-deterministic data for...") as they communicate important context to downstream agents
      - DO NOT change the changelog template structure (two-item list with "- Current implementation: " stub) without updating all docstring generation code that depends on it
      - DO NOT add logic that silently drops empty metadata sections; the function's purpose is to guarantee non-empty sections for AI consumption
      - ALWAYS ensure GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT, and GENERATION_PROMPT_TERSE are defined in module scope before calling
      - ALWAYS pass filepath context even if not immediately obvious why; it improves Claude's understanding of code purpose and generates more contextually appropriate docstrings
      - ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure
      - ALWAYS preserve defensive None-handling in `_ensure_nonempty_metadata()` (m or {}) to accept None input gracefully
      - ALWAYS return a dictionary (never None) from metadata normalization to maintain contract with callers
        changelog:
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support"
          - "- Accepts a code string and filepath, sends them to Claude API (Anthropic) with a formatted prompt to generate an AI-agent-friendly verbose docstring (default) or an embedded agentspec YAML block when as_agentspec_yaml=True"
          - "- Constructs an API message with the code and filepath injected into GENERATION_PROMPT template, requesting up to 2000 tokens of output"
          - "- Extracts and returns the text content from Claude's first message response, which contains the generated docstring formatted for AI agent consumption"
          - "- Handles the full request-response cycle with the Anthropic client, assuming the client is already initialized globally and GENERATION_PROMPT is defined in the module scope"
          - "- Returns a string containing the generated docstring; will raise anthropic.APIError or similar exceptions if API calls fail, authentication issues occur, or rate limits are exceeded"
          - "- Called by: [Likely called from main document generation pipeline, possibly CLI entrypoint or batch processing function in agentspec/main.py or similar]"
          - "- Calls: client.messages.create() [Anthropic API method], implicitly relies on message.content[0].text property access"
          - "- Imports used: Requires 'client' object (anthropic.Anthropic() instance) and 'GENERATION_PROMPT' constant to be defined in module scope; assumes anthropic library is imported"
          - "- External services: Anthropic Claude API (claude-haiku-4-5 model by default, or specified model parameter); requires valid API key in environment"
          - "- Uses Claude API rather than local LLM because Claude provides superior code understanding and produces more detailed, nuanced docstrings suitable for AI agent consumption"
          - "- Sets max_tokens to 2000 to balance comprehensiveness (verbose docstrings) with API cost and latency; lower would truncate valuable content, higher adds unnecessary expense"
          - "- Extracts message.content[0].text directly without validation because Anthropic guarantees at least one content block with text; could add defensive checks but adds complexity"
          - "- Accepts model parameter as optional override to allow flexibility for different Claude versions without code changes; defaults to sonnet-4 as reasonable quality/speed balance"
          - "- Uses template injection (GENERATION_PROMPT.format()) rather than f-strings for better reusability and separation of concerns; prompt can be modified without touching function logic"
          - "- Does not implement retry logic itself; caller should handle retries/exponential backoff as this is a thin API wrapper"
          - "- [Current date]: Initial implementation for Claude-based docstring generation with configurable model parameter"
          - "- DO NOT modify the hardcoded model default without updating documentation of breaking changes"
          - "- DO NOT remove the max_tokens limit or set arbitrarily high without cost/latency analysis"
          - "- DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized"
          - "- DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, or anthropic.AuthenticationError"
          - "- ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure"
          - "- ALWAYS ensure GENERATION_PROMPT and client are available in module scope before calling"
          - "- ALWAYS pass filepath context even if not immediately obvious why; it helps Claude understand the code's purpose and generates more contextually appropriate docstrings"
          - "- NOTE: This function makes external API calls and will fail silently if client is not properly initialized; test initialization separately from this function"
          - "- NOTE: API responses may vary between model versions; using different models may produce different docstring styles and token usage patterns"
          - "- NOTE: The function blocks until API response is received; consider async/await wrapper if used in high-concurrency scenarios"
          - "- Accepts a metadata dictionary (or None) and returns a normalized dictionary with guaranteed non-empty structure"
          - "- Initializes or validates three key metadata sections: deps.calls, deps.imports, and changelog"
          - "- For deps.calls: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable"
          - "- For deps.imports: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable"
          - "- For changelog: if missing, empty, or contains only default empty-state values ('- no git history available' or '- none yet'), replaces with a two-item list containing a "no metadata found" message and a "Current implementation:" stub for agent completion"
          - "- Returns the normalized metadata dictionary with all three sections guaranteed to have at least one entry"
          - "- Handles None input gracefully by treating it as an empty dictionary"
          - "- Called by: generate.py module functions that prepare metadata for docstring generation (inferred from file context)"
          - "- Calls: dict() constructor (built-in), m.get() and deps.get() dictionary methods (built-in)"
          - "- Imports used: None directly; this is a utility function within agentspec/generate.py"
          - "- External services: None"
          - "- This function serves as a defensive guard to ensure that AI agent-facing docstrings never contain completely empty metadata sections, which would be unhelpful for code understanding"
          - "- The placeholder messages ("No metadata found; Agentspec only allows non-deterministic data for...") explicitly communicate to agents why deterministic metadata is absent, rather than leaving fields blank or undefined"
          - "- The changelog section receives special handling with a two-part template: the first item explains the absence of metadata, and the second item ("- Current implementation: ") is left incomplete as an intentional stub for agents or humans to complete with a concrete summary"
          - "- Using dict() constructor creates shallow copies to avoid mutating the input dictionary, which is important for immutability and preventing side effects"
          - "- The approach prioritizes clarity over brevity: placeholder strings are verbose to ensure agents understand the metadata collection limitations"
          - "- Alternative approaches (raising exceptions, returning None, silently omitting fields) were not used because this function must guarantee a valid structure for downstream docstring generation"
          - "- No metadata found; Agentspec only allows non-deterministic data for changelog."
          - "- Current implementation: Normalizes and validates metadata dictionaries by inserting placeholder messages for missing deterministic metadata fields (deps.calls, deps.imports, changelog) to ensure AI-facing docstrings always contain non-empty metadata sections."
          - "- DO NOT remove or modify the placeholder message strings ("No metadata found; Agentspec only allows non-deterministic data for...") as they communicate important context to downstream agents"
          - "- DO NOT change the structure of the changelog template (two-item list with "Current implementation: " stub) without updating all docstring generation code that depends on it"
          - "- DO NOT add logic that silently drops empty metadata sections; the function's purpose is to guarantee non-empty sections"
          - "- ALWAYS preserve the defensive None-handling (m or {}) at the start of the function"
          - "- ALWAYS ensure that all three metadata sections (deps.calls, deps.imports, changelog) are checked and populated if empty"
          - "- ALWAYS return a dictionary (never None) to maintain contract with callers"
          - "- NOTE: The changelog's "- Current implementation: " line is intentionally incomplete and serves as a template for agents to fill in; do not auto-complete it"
          - "- NOTE: This function is part of the metadata normalization pipeline and must maintain compatibility with docstring generation templates that expect these exact placeholder formats"
          - "-    # If diff_summary requested, make separate LLM call to summarize git diffs"
          - "-        from agentspec.collect import collect_changelog_diffs"
          - "-        diffs = collect_changelog_diffs(Path(filepath), func_name)"
          - "-        if diffs:"
          - "-            # Build prompt for LLM to summarize diffs"
          - "-            diff_prompt = "Summarize these git diffs concisely (one line per commit):\n\n""
          - "-            for d in diffs:"
          - "-                diff_prompt += f"Diff:\n{d['diff']}\n\n""
          - "-                "You are a code change summarizer. For each commit, provide a SHORT one-line summary (max 10 words).""
          - "-                "You are a code change summarizer. For each commit, provide a one-line summary of what changed.""
          - "-            # Inject diff summary section"
          - "-            diff_summary_section = f"\n\nCHANGELOG DIFF SUMMARY (LLM-generated):\n{diff_summaries_text}\n""
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Accepts a code string and filepath, sends them to Claude API (Anthropic) with a formatted prompt to generate an AI-agent-friendly verbose docstring (default) or an embedded agentspec YAML block when as_agentspec_yaml=True"
          - "- Constructs an API message with the code and filepath injected into GENERATION_PROMPT template, requesting up to 2000 tokens of output"
          - "- Extracts and returns the text content from Claude's first message response, which contains the generated docstring formatted for AI agent consumption"
          - "- Handles the full request-response cycle with the Anthropic client, assuming the client is already initialized globally and GENERATION_PROMPT is defined in the module scope"
          - "- Returns a string containing the generated docstring; will raise anthropic.APIError or similar exceptions if API calls fail, authentication issues occur, or rate limits are exceeded"
          - "- Called by: [Likely called from main document generation pipeline, possibly CLI entrypoint or batch processing function in agentspec/main.py or similar]"
          - "- Calls: client.messages.create() [Anthropic API method], implicitly relies on message.content[0].text property access"
          - "- Imports used: Requires 'client' object (anthropic.Anthropic() instance) and 'GENERATION_PROMPT' constant to be defined in module scope; assumes anthropic library is imported"
          - "- External services: Anthropic Claude API (claude-haiku-4-5 model by default, or specified model parameter); requires valid API key in environment"
          - "- Uses Claude API rather than local LLM because Claude provides superior code understanding and produces more detailed, nuanced docstrings suitable for AI agent consumption"
          - "- Sets max_tokens to 2000 to balance comprehensiveness (verbose docstrings) with API cost and latency; lower would truncate valuable content, higher adds unnecessary expense"
          - "- Extracts message.content[0].text directly without validation because Anthropic guarantees at least one content block with text; could add defensive checks but adds complexity"
          - "- Accepts model parameter as optional override to allow flexibility for different Claude versions without code changes; defaults to sonnet-4 as reasonable quality/speed balance"
          - "- Uses template injection (GENERATION_PROMPT.format()) rather than f-strings for better reusability and separation of concerns; prompt can be modified without touching function logic"
          - "- Does not implement retry logic itself; caller should handle retries/exponential backoff as this is a thin API wrapper"
          - "- [Current date]: Initial implementation for Claude-based docstring generation with configurable model parameter"
          - "- DO NOT modify the hardcoded model default without updating documentation of breaking changes"
          - "- DO NOT remove the max_tokens limit or set arbitrarily high without cost/latency analysis"
          - "- DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized"
          - "- DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, or anthropic.AuthenticationError"
          - "- ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure"
          - "- ALWAYS ensure GENERATION_PROMPT and client are available in module scope before calling"
          - "- ALWAYS pass filepath context even if not immediately obvious why; it helps Claude understand the code's purpose and generates more contextually appropriate docstrings"
          - "- NOTE: This function makes external API calls and will fail silently if client is not properly initialized; test initialization separately from this function"
          - "- NOTE: API responses may vary between model versions; using different models may produce different docstring styles and token usage patterns"
          - "- NOTE: The function blocks until API response is received; consider async/await wrapper if used in high-concurrency scenarios"
          - "- Accepts a metadata dictionary (or None) and returns a normalized dictionary with guaranteed non-empty structure"
          - "- Initializes or validates three key metadata sections: deps.calls, deps.imports, and changelog"
          - "- For deps.calls: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable"
          - "- For deps.imports: if missing or empty, inserts a placeholder message indicating deterministic metadata was unavailable"
          - "- For changelog: if missing, empty, or contains only default empty-state values ('- no git history available' or '- none yet'), replaces with a two-item list containing a "no metadata found" message and a "Current implementation:" stub for agent completion"
          - "- Returns the normalized metadata dictionary with all three sections guaranteed to have at least one entry"
          - "- Handles None input gracefully by treating it as an empty dictionary"
          - "- Called by: generate.py module functions that prepare metadata for docstring generation (inferred from file context)"
          - "- Calls: dict() constructor (built-in), m.get() and deps.get() dictionary methods (built-in)"
          - "- Imports used: None directly; this is a utility function within agentspec/generate.py"
          - "- External services: None"
          - "- This function serves as a defensive guard to ensure that AI agent-facing docstrings never contain completely empty metadata sections, which would be unhelpful for code understanding"
          - "- The placeholder messages ("No metadata found; Agentspec only allows non-deterministic data for...") explicitly communicate to agents why deterministic metadata is absent, rather than leaving fields blank or undefined"
          - "- The changelog section receives special handling with a two-part template: the first item explains the absence of metadata, and the second item ("- Current implementation: ") is left incomplete as an intentional stub for agents or humans to complete with a concrete summary"
          - "- Using dict() constructor creates shallow copies to avoid mutating the input dictionary, which is important for immutability and preventing side effects"
          - "- The approach prioritizes clarity over brevity: placeholder strings are verbose to ensure agents understand the metadata collection limitations"
          - "- Alternative approaches (raising exceptions, returning None, silently omitting fields) were not used because this function must guarantee a valid structure for downstream docstring generation"
          - "- No metadata found; Agentspec only allows non-deterministic data for changelog."
          - "- Current implementation: Normalizes and validates metadata dictionaries by inserting placeholder messages for missing deterministic metadata fields (deps.calls, deps.imports, changelog) to ensure AI-facing docstrings always contain non-empty metadata sections."
          - "- DO NOT remove or modify the placeholder message strings ("No metadata found; Agentspec only allows non-deterministic data for...") as they communicate important context to downstream agents"
          - "- DO NOT change the structure of the changelog template (two-item list with "Current implementation: " stub) without updating all docstring generation code that depends on it"
          - "- DO NOT add logic that silently drops empty metadata sections; the function's purpose is to guarantee non-empty sections"
          - "- ALWAYS preserve the defensive None-handling (m or {}) at the start of the function"
          - "- ALWAYS ensure that all three metadata sections (deps.calls, deps.imports, changelog) are checked and populated if empty"
          - "- ALWAYS return a dictionary (never None) to maintain contract with callers"
          - "- NOTE: The changelog's "- Current implementation: " line is intentionally incomplete and serves as a template for agents to fill in; do not auto-complete it"
          - "- NOTE: This function is part of the metadata normalization pipeline and must maintain compatibility with docstring generation templates that expect these exact placeholder formats"
          - "-    meta = _ensure_nonempty_metadata(meta)"
          - "-    hard_data = json.dumps(meta, indent=2)"
          - "-    prompt = AGENTSPEC_YAML_PROMPT if as_agentspec_yaml else GENERATION_PROMPT"
          - "-    client = _get_client()"
          - "-    message = client.messages.create("
          - "-        max_tokens=2000,"
          - "-        temperature=0.2,"
          - "-        messages=[{"
          - "-            "role": "user","
          - "-            "content": prompt.format("
          - "-                code=code,"
          - "-                filepath=filepath,"
          - "-                hard_data=hard_data"
          - "-            )"
          - "-        }]"
          - "-    return message.content[0].text"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- Accepts a code string and filepath, sends them to Claude API (Anthropic) with a formatted prompt to generate an AI-agent-friendly verbose docstring (default) or an embedded agentspec YAML block when as_agentspec_yaml=True"
          - "- Constructs an API message with the code and filepath injected into GENERATION_PROMPT template, requesting up to 2000 tokens of output"
          - "- Extracts and returns the text content from Claude's first message response, which contains the generated docstring formatted for AI agent consumption"
          - "- Handles the full request-response cycle with the Anthropic client, assuming the client is already initialized globally and GENERATION_PROMPT is defined in the module scope"
          - "- Returns a string containing the generated docstring; will raise anthropic.APIError or similar exceptions if API calls fail, authentication issues occur, or rate limits are exceeded"
          - "- Called by: [Likely called from main document generation pipeline, possibly CLI entrypoint or batch processing function in agentspec/main.py or similar]"
          - "- Calls: client.messages.create() [Anthropic API method], implicitly relies on message.content[0].text property access"
          - "- Imports used: Requires 'client' object (anthropic.Anthropic() instance) and 'GENERATION_PROMPT' constant to be defined in module scope; assumes anthropic library is imported"
          - "-    - External services: Anthropic Claude API (claude-sonnet-4-20250514 model by default, or specified model parameter); requires valid API key in environment"
          - "- Uses Claude API rather than local LLM because Claude provides superior code understanding and produces more detailed, nuanced docstrings suitable for AI agent consumption"
          - "- Sets max_tokens to 2000 to balance comprehensiveness (verbose docstrings) with API cost and latency; lower would truncate valuable content, higher adds unnecessary expense"
          - "- Extracts message.content[0].text directly without validation because Anthropic guarantees at least one content block with text; could add defensive checks but adds complexity"
          - "- Accepts model parameter as optional override to allow flexibility for different Claude versions without code changes; defaults to sonnet-4 as reasonable quality/speed balance"
          - "- Uses template injection (GENERATION_PROMPT.format()) rather than f-strings for better reusability and separation of concerns; prompt can be modified without touching function logic"
          - "- Does not implement retry logic itself; caller should handle retries/exponential backoff as this is a thin API wrapper"
          - "- [Current date]: Initial implementation for Claude-based docstring generation with configurable model parameter"
          - "- DO NOT modify the hardcoded model default without updating documentation of breaking changes"
          - "- DO NOT remove the max_tokens limit or set arbitrarily high without cost/latency analysis"
          - "- DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized"
          - "- DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, or anthropic.AuthenticationError"
          - "- ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure"
          - "- ALWAYS ensure GENERATION_PROMPT and client are available in module scope before calling"
          - "- ALWAYS pass filepath context even if not immediately obvious why; it helps Claude understand the code's purpose and generates more contextually appropriate docstrings"
          - "- NOTE: This function makes external API calls and will fail silently if client is not properly initialized; test initialization separately from this function"
          - "- NOTE: API responses may vary between model versions; using different models may produce different docstring styles and token usage patterns"
          - "- NOTE: The function blocks until API response is received; consider async/await wrapper if used in high-concurrency scenarios"
          - "-    print(f"[AGENTSPEC_CONTEXT] generate_docstring: Accepts a code string and filepath, sends them to Claude API with a prompt to generate either a verbose docstring or a fenced agentspec YAML block | Constructs an API message with the code and filepath injected into the selected template, requesting up to 2000 tokens of output | Extracts and returns the text content from Claude's first message response")"
          - "-                filepath=filepath"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Use Claude to generate a verbose docstring.""""
          - "-            "content": GENERATION_PROMPT.format("
          - "- 2025-10-29: Add --model flag to choose between Claude models (Sonnet/Haiku)"
          - "-        model="claude-sonnet-4-20250514","

    '''

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
        ---agentspec
        what: |
          Normalizes a metadata dictionary by ensuring all required sections (deps.calls, deps.imports, changelog) contain non-empty values. Accepts a metadata dict or None as input and returns a guaranteed non-empty normalized dict. When deterministic metadata fields are missing or empty, inserts placeholder strings that explicitly communicate why the data is absent. The changelog section receives a two-item template: an absence explanation followed by a "Current implementation: " stub for later completion. Handles gracefully the case where input is None by treating it as an empty dict.
            deps:
              calls:
                - deps.get
                - dict
                - m.get
              imports:
                - agentspec.collect.collect_metadata
                - agentspec.utils.collect_python_files
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
          Ensures that AI-facing docstrings never contain completely empty metadata sections, which could confuse agents or cause downstream processing failures. Placeholder strings serve as explicit communication to agents about metadata collection limitations and the distinction between deterministic and non-deterministic data. This defensive normalization prevents callers from needing to check for missing fields and maintains a consistent contract: the function always returns a fully populated dictionary suitable for docstring generation.

        guardrails:
          - DO NOT remove or modify placeholder message strings; they communicate to agents why deterministic metadata is absent and distinguish between data collection limitations and intentional non-deterministic allowances.
          - DO NOT change the changelog template structure (two-item list with absence explanation + "Current implementation: " stub) without updating all dependent docstring generation code that relies on this format.
          - ALWAYS preserve the None-handling pattern (m or {}) to accept None input gracefully and avoid AttributeError on dict operations.
          - ALWAYS return a dictionary (never None) to maintain the caller's contract and prevent downstream code from needing null checks.
          - ALWAYS populate all three metadata sections (deps.calls, deps.imports, changelog) even when input is empty, to guarantee consistent structure for template rendering.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
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
    # CRITICAL VALIDATION: Check for format consistency before metadata injection
    import re
    if as_agentspec_yaml:
        # YAML mode: should NOT contain plain text sections like "WHAT:" "WHY:" "CHANGELOG:"
        # Check for plain text section headers (typically at start of line with optional leading space)
        plain_text_patterns = [
            r'(?m)^[ \t]*WHAT:', r'(?m)^[ \t]*WHY:', r'(?m)^CHANGELOG \(from git history\):'
        ]
        if any(re.search(pattern, text) for pattern in plain_text_patterns):
            raise ValueError("LLM generated invalid YAML format - contains plain text sections. Rejecting and requiring regeneration.")
    else:
        # Plain text mode: should NOT contain YAML sections
        # Check for YAML block markers and indented YAML section headers (not plain text headers)
        yaml_patterns = [
            r'^---agentspec',  # YAML block start at beginning of line
            r'(?m)^[ \t]+what:',  # Indented YAML what: (not plain WHAT:)
            r'(?m)^[ \t]+why:',   # Indented YAML why:
            r'(?m)^[ \t]+changelog:',  # Indented YAML changelog:
            r'---/agentspec'  # YAML block end
        ]
        if any(re.search(pattern, text, re.MULTILINE) for pattern in yaml_patterns):
            raise ValueError("LLM generated invalid plain text format - contains YAML sections. Rejecting and requiring regeneration.")

    result = inject_deterministic_metadata(text, meta, as_agentspec_yaml)

    # If diff_summary requested, make separate LLM call to summarize function-scoped code diffs (excluding docstrings/comments)
    if diff_summary and func_name:
        from agentspec.collect import collect_function_code_diffs
        code_diffs = collect_function_code_diffs(Path(filepath), func_name)

        if code_diffs:
            # Build prompt for LLM: infer the WHY from the code changes and commit messages
            diff_prompt = (
                "CRITICAL: Output format is EXACTLY one line per commit in format:\n"
                "- YYYY-MM-DD: summary (hash)\n\n"
                "Summarize the intent (WHY) behind these changes to the specific function.\n"
                "Only consider the added/removed lines shown (docstrings/comments removed).\n"
                "Use the exact date and commit hash provided. Provide a concise WHY summary in <=15 words.\n\n"
            )
            for d in code_diffs:
                commit_hash = d.get('hash', 'unknown')
                diff_prompt += f"Commit: {d['date']} - {d['message']} ({commit_hash})\n"
                diff_prompt += f"Function: {func_name}\n"
                diff_prompt += f"Changed lines:\n{d['diff']}\n\n"

            # Separate API call for diff summaries
            from agentspec.llm import generate_chat
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
            result += diff_summary_section
    
    return result

def insert_docstring_at_line(filepath: Path, lineno: int, func_name: str, docstring: str, force_context: bool = False) -> bool:
    """
    ```python
    \"""
    Insert or replace a docstring at a specific function, with optional debug context printing.

    WHAT:
    - Locates function by name/line using AST (with regex fallback), detects and removes existing docstring, inserts new docstring with correct indentation
    - Optionally adds print statement with first 3 docstring bullets for agent debugging
    - Validates syntax via compile before writing; returns False if compilation fails

    WHY:
    - AST-first approach handles multi-line signatures and decorators robustly; textual fallback preserves formatting better than full rewrite
    - Compile validation prevents leaving broken Python files on insertion errors
    - Bottom-to-top processing (via reversed insertion) prevents line number invalidation on repeated runs

    GUARDRAILS:
    - DO NOT modify indentation calculation (base_indent + 4) without verifying 4-space function body assumption
    - DO NOT remove quote-type detection (\""" vs '''); both are valid and files may use either
    - DO NOT skip existing docstring/context-print removal; prevents duplicate accumulation on repeated runs
    - ALWAYS use reversed() when inserting new_lines to maintain correct line order
    - ALWAYS escape backslashes before quotes in print_content to prevent syntax errors in generated code
    \"""
    ```

    DEPENDENCIES (from code analysis):
    Calls: abs, ast.parse, ast.walk, candidate.insert, candidates.append, docstring.split, enumerate, f.readlines, f.writelines, func_line.lstrip, hasattr, isinstance, join, len, line.count, line.startswith, line.strip, list, max, min, new_lines.append, open, os.close, os.remove, path.exists, pattern.match, print, print_content.replace, py_compile.compile, re.compile, re.escape, replace, reversed, safe_doc.replace, safe_doc.split, sections.append, strip, tempfile.mkstemp, tf.writelines
    Imports: agentspec.collect.collect_metadata, agentspec.utils.collect_python_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
    - Reads a Python source file and locates the function definition at the specified line number
    - Detects and removes any existing docstring (both single-line and multi-line formats using \"\"\" or ''')
    - Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present
    - Calculates proper indentation based on the function definition line to maintain code style
    - Formats the new docstring with correct triple-quote wrapping and indentation
    - Optionally adds a print statement containing the first 3 bullet points from the docstring for agent debugging
    - Writes the modified file back to disk, preserving all other code
    - Returns nothing; operates entirely through file I/O side effects
    - Called by: agentspec/generate.py (likely called from a main documentation generation pipeline)
    - Calls: open() (built-in), str.split(), str.strip(), str.lstrip(), str.replace(), reversed() (built-in), list.insert() (built-in)
    - Imports used: Path (from pathlib)
    - External services: File system access (reads and writes to filepath)
    - Uses line-by-line string manipulation rather than AST parsing to preserve exact file formatting, comments, and non-docstring content
    - Reads entire file into memory (readlines()) for simplicity; viable for typical Python source files but could be memory-intensive for very large files (>100MB)
    - Detects both \"\"\" and ''' delimiters because Python supports both, requiring careful quote type tracking
    - Handles both single-line docstrings (opening and closing quotes on same line) and multi-line docstrings with separate logic paths
    - Removes existing docstrings before insertion to prevent duplicate docstrings and ensure old content does not interfere
    - The force_context parameter allows injecting debug information into the function body itself as a print statement, enabling runtime inspection by agents
    - Indentation is calculated by measuring the function definition line's leading whitespace, then adding 4 spaces for function body content (standard Python convention)
    - Uses reversed() when inserting new lines to maintain correct order when inserting at the same index repeatedly
    - Escapes backslashes and quotes in the context print statement to prevent syntax errors when the print statement is written to file
    - [Current date]: Initial implementation with support for single/multi-line docstring detection, existing docstring removal, intelligent indentation preservation, and optional agent context printing
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
    -        target = None
    -            # Insert before the first statement in the body
    -            insert_idx = (target.body[0].lineno or (func_line_idx + 1)) - 1
    -    except Exception:
    -    # Skip any existing docstring if present
    -    if insert_idx < len(lines):
    -        line = lines[insert_idx].strip()
    -        if line.startswith('\"""') or line.startswith("'''"):
    -            quote_type = '\"""' if '\"""' in line else "'''"
    -            # Skip existing docstring
    -            if line.count(quote_type) >= 2:
    -                # Single-line docstring
    -                insert_idx += 1
    -            else:
    -                # Multi-line docstring - find end
    -                insert_idx += 1
    -                while insert_idx < len(lines):
    -                    if quote_type in lines[insert_idx]:
    -                        break
    -            # Also skip any existing context print
    -            if insert_idx < len(lines) and '[AGENTSPEC_CONTEXT]' in lines[insert_idx]:
    -                insert_idx += 1
    -            # Delete the old docstring and print
    -            del lines[func_line_idx + 1:insert_idx]
    -            insert_idx = func_line_idx + 1
    - 2025-10-30: feat: robust docstring generation and Haiku defaults
    - Reads a Python source file and locates the function definition at the specified line number
    - Detects and removes any existing docstring (both single-line and multi-line formats using \"\"\" or ''')
    - Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present
    - Calculates proper indentation based on the function definition line to maintain code style
    - Formats the new docstring with correct triple-quote wrapping and indentation
    - Optionally adds a print statement containing the first 3 bullet points from the docstring for agent debugging
    - Writes the modified file back to disk, preserving all other code
    - Returns nothing; operates entirely through file I/O side effects
    - Called by: agentspec/generate.py (likely called from a main documentation generation pipeline)
    - Calls: open() (built-in), str.split(), str.strip(), str.lstrip(), str.replace(), reversed() (built-in), list.insert() (built-in)
    - Imports used: Path (from pathlib)
    - External services: File system access (reads and writes to filepath)
    - Uses line-by-line string manipulation rather than AST parsing to preserve exact file formatting, comments, and non-docstring content
    - Reads entire file into memory (readlines()) for simplicity; viable for typical Python source files but could be memory-intensive for very large files (>100MB)
    - Detects both \"\"\" and ''' delimiters because Python supports both, requiring careful quote type tracking
    - Handles both single-line docstrings (opening and closing quotes on same line) and multi-line docstrings with separate logic paths
    - Removes existing docstrings before insertion to prevent duplicate docstrings and ensure old content does not interfere
    - The force_context parameter allows injecting debug information into the function body itself as a print statement, enabling runtime inspection by agents
    - Indentation is calculated by measuring the function definition line's leading whitespace, then adding 4 spaces for function body content (standard Python convention)
    - Uses reversed() when inserting new lines to maintain correct order when inserting at the same index repeatedly
    - Escapes backslashes and quotes in the context print statement to prevent syntax errors when the print statement is written to file
    - [Current date]: Initial implementation with support for single/multi-line docstring detection, existing docstring removal, intelligent indentation preservation, and optional agent context printing
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
    -    # Find the function definition line
    -    func_line_idx = lineno - 1
    -    # Find the first line after the function signature (where docstring goes)
    -    new_lines.append(f'{indent}\"""\n')
    -    for line in docstring.split('\n'):
    -    new_lines.append(f'{indent}\"""\n')
    -    # Insert the new docstring
    -        lines.insert(insert_idx, line)
    -    # Write back
    -    with open(filepath, 'w') as f:
    -        f.writelines(lines)
    - 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate
    -    Insert docstring at a specific line number in a file.
    -    This handles the actual file modification.
    -    \"""Process a single file and generate docstrings.\"""
    - 2025-10-29: CRITICAL FIX: Escape quotes in context print statements to prevent syntax errors
    - 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors
    -    \"""Insert or replace docstring in function, optionally adding context print.\"""
    -    # Find where to insert docstring (right after function definition)
    -    func_line = node.lineno - 1
    -    # Check if there's already a docstring
    -    existing_docstring = ast.get_docstring(node)
    -    if existing_docstring:
    -        # Find and replace existing docstring
    -        start_line = func_line + 1
    -        # Skip decorators and find the actual def line
    -        for i in range(func_line, len(lines)):
    -            if 'def ' in lines[i]:
    -                start_line = i + 1
    -                break
    -        # Find end of existing docstring
    -        in_docstring = False
    -        quote_type = None
    -        end_line = start_line
    -        for i in range(start_line, len(lines)):
    -            line = lines[i].strip()
    -            if not in_docstring:
    -                if line.startswith('\"""') or line.startswith("'''"):
    -                    in_docstring = True
    -                    quote_type = '\"""' if '\"""' in line else "'''"
    -                    if line.count(quote_type) >= 2:
    -                        # Single line docstring
    -                        end_line = i + 1
    -                        break
    -                if quote_type in line:
    -                    end_line = i + 1
    -                    break
    -        # Check if there's already a context print statement after docstring
    -        has_context_print = False
    -        if end_line < len(lines):
    -            next_line = lines[end_line].strip()
    -            if 'print(f"[AGENTSPEC_CONTEXT]' in next_line or 'print("[AGENTSPEC_CONTEXT]' in next_line:
    -                has_context_print = True
    -                end_line += 1  # Include the print line in deletion
    -        # Remove old docstring (and old print if exists)
    -        del lines[start_line:end_line]
    -        insert_line = start_line
    -    else:
    -        # Find insertion point (after function definition line)
    -        for i in range(func_line, len(lines)):
    -            if 'def ' in lines[i] or 'async def' in lines[i]:
    -                insert_line = i + 1
    -                break
    -    indent = '    '  # Assuming 4-space indent
    -    formatted = f'{indent}\"""\n'
    -        formatted += f'{indent}{line}\n'
    -    formatted += f'{indent}\"""\n'
    -    # Add context-forcing print if requested
    -        # Extract key sections for print
    -        sections_to_print = []
    -        current_section = None
    -            if line.startswith('WHAT THIS DOES:'):
    -                current_section = 'WHAT_THIS_DOES'
    -            elif line.startswith('DEPENDENCIES:'):
    -                current_section = 'DEPENDENCIES'
    -            elif line.startswith('WHY THIS APPROACH:'):
    -                current_section = 'WHY_APPROACH'
    -            elif line.startswith('AGENT INSTRUCTIONS:'):
    -                current_section = 'AGENT_INSTRUCTIONS'
    -            elif line.startswith('CHANGELOG:'):
    -                current_section = None  # Skip changelog in prints
    -            elif current_section and line.startswith('-'):
    -                sections_to_print.append(line)
    -        # Add print statement that forces context
    -        func_name = node.name
    -        print_content = ' | '.join(sections_to_print[:3])  # First 3 bullet points
    -        formatted += f'{indent}print(f"[AGENTSPEC_CONTEXT] {func_name}: {print_content}")\n'
    -    # Insert new docstring (and print if applicable)
    -    lines.insert(insert_line, formatted)
    -    \"""Find all functions that need docstrings.\"""
    -    def __init__(self):
    -        self.functions = []
    -    def visit_FunctionDef(self, node):
    -        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('\n')) < 5:
    -            self.functions.append((node.lineno, node.name))
    -        self.generic_visit(node)
    -    def visit_AsyncFunctionDef(self, node):
    -        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('\n')) < 5:
    -            self.functions.append((node.lineno, node.name))
    -        self.generic_visit(node)

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
    '''
    ---agentspec
    what: |
      Processes a single Python file to identify functions lacking verbose docstrings and generates AI-consumable documentation for them using the Claude API.

      Behavior:
      - Extracts all function definitions from the target file using AST parsing via extract_function_info()
      - Filters to functions without existing verbose docstrings (or all functions if update_existing=True)
      - Displays a summary of findings to the user with function names and line numbers
      - For each function needing documentation, calls generate_docstring() to create AI-generated docstrings via Claude API
      - Inserts generated docstrings into the source file at correct line numbers using insert_docstring_at_line()
      - Processes functions in descending line order (bottom-to-top) to prevent line number shifting during multi-insertion
      - Supports dry-run mode to preview changes without file modification
      - Supports force-context mode to inject print() statements alongside docstrings for debugging
      - Optionally generates agentspec YAML blocks instead of traditional docstrings when as_agentspec_yaml=True
      - Handles SyntaxError gracefully with early return and batch-safe failure isolation

      Inputs:
      - filepath: Path object pointing to Python file to process
      - dry_run: bool (default False) - preview mode without file modifications
      - force_context: bool (default False) - inject debug print() statements
      - model: str (default "claude-haiku-4-5") - Claude model identifier
      - as_agentspec_yaml: bool (default False) - generate YAML agentspec blocks instead of docstrings
      - base_url: str | None (default None) - custom API endpoint URL
      - provider: str | None (default 'auto') - API provider selection
      - update_existing: bool (default False) - regenerate docstrings for all functions
      - terse: bool (default False) - generate concise documentation
      - diff_summary: bool (default False) - include diff summary in output

      Outputs:
      - Returns None in all cases (completion, early exit on syntax error, or dry-run)
      - Side effects: modifies source file in-place (unless dry_run=True) by inserting docstrings
      - Console output: progress messages, function list, success/error feedback

      Edge cases:
      - File with no functions: exits early with informational message
      - File with all functions already documented: exits early (unless update_existing=True)
      - SyntaxError in target file: caught and reported, allows batch processing to continue
      - Individual function generation failure: caught and isolated, remaining functions still processed
      - Dry-run mode: returns before any file modifications occur
      - insert_docstring_at_line returns False: skips insertion with warning (syntax safety check)
        deps:
          calls:
            - extract_function_info
            - functions.sort
            - generate_docstring
            - insert_docstring_at_line
            - len
            - print
            - str
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
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
      Bottom-to-top processing prevents cascading line offset errors: insertions from end of file backward ensure previously-calculated line numbers remain valid as the file grows.

      Nested exception handling (outer for SyntaxError, inner for per-function failures) allows graceful degradation: one malformed function or API error does not block remaining functions in the same file or other files in batch operations.

      Dry-run mode implemented as early return before any file modifications enables safe preview and user confidence before committing changes.

      Force-context flag is propagated to insert_docstring_at_line rather than handled here, maintaining separation of concerns: this function orchestrates the workflow while insert_docstring_at_line handles file mutation details.

      Model parameter exposed as configurable argument (not hardcoded) allows runtime selection of Claude models, supporting experimentation with different versions and cost/quality tradeoffs.

      Print statements used for user feedback rather than logging module ensures immediate console output during long-running batch operations without buffering delays.

      Sequential processing chosen over parallel/concurrent to avoid Claude API rate-limit issues and maintain simplicity; docstring generation is I/O-bound but rate-limited, not CPU-bound.

      Complete API response collection (not streaming) is acceptable for docstring length and simplifies error handling and insertion logic.

    guardrails:
      - DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file
      - DO NOT change the order of operations (extract → check → generate → insert) without reviewing how line numbers are affected by insertions
      - DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models
      - DO NOT remove the dry-run early return; users depend on this to preview changes without file modification
      - DO NOT skip the bottom-to-top sort; processing top-to-bottom will invalidate line numbers as insertions shift subsequent lines
      - ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations
      - ALWAYS pass filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings
      - ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging
      - ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation
      - ALWAYS check the return value of insert_docstring_at_line; False indicates syntax safety rejection and should be reported to user
      - NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode
      - NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor printed error messages
      - NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior and means repeated runs on the same file are safe

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings for them using Claude API"
          - "- Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user"
          - "- For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()"
          - "- Supports dry-run mode (--dry-run flag) to preview which functions would be processed without modifying files"
          - "- Supports force-context mode to inject print() statements alongside docstrings for debugging/tracing function execution"
          - "- Handles SyntaxError exceptions gracefully when files contain invalid Python syntax, and catches any exception during individual docstring generation to continue processing remaining functions"
          - "- Returns None in all cases (either after completion, early exit on syntax error, or early exit on dry-run)"
          - "- Called by: CLI entry point in agentspec/main.py or equivalent script runner that parses command-line arguments and invokes this for each file"
          - "- Calls: extract_function_info() [agentspec/extract.py] to parse file and identify functions, generate_docstring() [agentspec/generate.py or api module] to call Claude API, insert_docstring_at_line() [agentspec/insert.py] to modify source file"
          - "- Imports used: Path from pathlib (for cross-platform file path handling)"
          - "- External services: Anthropic Claude API (via generate_docstring wrapper) - requires valid API key in environment and network connectivity"
          - "- Processes functions bottom-to-top (assumes extract_function_info already sorts results) to avoid line number shifting as insertions are made from end of file backward, preventing cascading line offset errors"
          - "- Uses try-except around entire file extraction to catch SyntaxError early and fail gracefully rather than crashing, allowing batch processing of multiple files with some invalid"
          - "- Uses nested try-except within the processing loop to isolate failures to individual functions, ensuring one broken function doesn't prevent docstring generation for remaining functions in the same file"
          - "- Dry-run mode implemented as early return before any file modifications, allowing users to preview changes safely"
          - "- Force-context flag passed through to insert_docstring_at_line rather than handled here, maintaining separation of concerns (this function orchestrates, insert_docstring_at_line handles file mutation details)"
          - "- Model parameter exposed as argument (not hardcoded) to allow runtime selection of Claude models, supporting experimentation with different model versions"
          - "- Print statements used for user feedback rather than logging module to ensure immediate console output during long processing operations"
          - "- Alternative not used: streaming the Claude API response directly - would be more efficient but adds complexity; current approach waits for complete generation which is acceptable for docstring length"
          - "- Alternative not used: parallel/concurrent processing of functions - sequential processing chosen for simplicity and to avoid rate-limit issues with Claude API"
          - "- 2025-01-15: Initial implementation with support for dry-run mode, force-context flag, and Claude Sonnet model selection"
          - "- DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file"
          - "- DO NOT change the order of operations (extract -> check -> generate -> insert) without reviewing how line numbers are affected by insertions"
          - "- DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models"
          - "- DO NOT remove the dry-run early return; users depend on this to preview changes without file modification"
          - "- ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations"
          - "- ALWAYS pass the filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings"
          - "- ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging"
          - "- ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation"
          - "- NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode"
          - "- NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor the printed error messages"
          - "- NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior but means repeated runs on the same file are safe"
          - "-        functions = extract_function_info(filepath, require_agentspec=as_agentspec_yaml)"
          - "-        print("  ✅ All functions already have verbose docstrings")"
          - "-            doc_or_yaml = generate_docstring(code, str(filepath), model=model, as_agentspec_yaml=as_agentspec_yaml)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings for them using Claude API"
          - "- Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user"
          - "- For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()"
          - "- Supports dry-run mode (--dry-run flag) to preview which functions would be processed without modifying files"
          - "- Supports force-context mode to inject print() statements alongside docstrings for debugging/tracing function execution"
          - "- Handles SyntaxError exceptions gracefully when files contain invalid Python syntax, and catches any exception during individual docstring generation to continue processing remaining functions"
          - "- Returns None in all cases (either after completion, early exit on syntax error, or early exit on dry-run)"
          - "- Called by: CLI entry point in agentspec/main.py or equivalent script runner that parses command-line arguments and invokes this for each file"
          - "- Calls: extract_function_info() [agentspec/extract.py] to parse file and identify functions, generate_docstring() [agentspec/generate.py or api module] to call Claude API, insert_docstring_at_line() [agentspec/insert.py] to modify source file"
          - "- Imports used: Path from pathlib (for cross-platform file path handling)"
          - "- External services: Anthropic Claude API (via generate_docstring wrapper) - requires valid API key in environment and network connectivity"
          - "- Processes functions bottom-to-top (assumes extract_function_info already sorts results) to avoid line number shifting as insertions are made from end of file backward, preventing cascading line offset errors"
          - "- Uses try-except around entire file extraction to catch SyntaxError early and fail gracefully rather than crashing, allowing batch processing of multiple files with some invalid"
          - "- Uses nested try-except within the processing loop to isolate failures to individual functions, ensuring one broken function doesn't prevent docstring generation for remaining functions in the same file"
          - "- Dry-run mode implemented as early return before any file modifications, allowing users to preview changes safely"
          - "- Force-context flag passed through to insert_docstring_at_line rather than handled here, maintaining separation of concerns (this function orchestrates, insert_docstring_at_line handles file mutation details)"
          - "- Model parameter exposed as argument (not hardcoded) to allow runtime selection of Claude models, supporting experimentation with different model versions"
          - "- Print statements used for user feedback rather than logging module to ensure immediate console output during long processing operations"
          - "- Alternative not used: streaming the Claude API response directly - would be more efficient but adds complexity; current approach waits for complete generation which is acceptable for docstring length"
          - "- Alternative not used: parallel/concurrent processing of functions - sequential processing chosen for simplicity and to avoid rate-limit issues with Claude API"
          - "- 2025-01-15: Initial implementation with support for dry-run mode, force-context flag, and Claude Sonnet model selection"
          - "- DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file"
          - "- DO NOT change the order of operations (extract -> check -> generate -> insert) without reviewing how line numbers are affected by insertions"
          - "- DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models"
          - "- DO NOT remove the dry-run early return; users depend on this to preview changes without file modification"
          - "- ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations"
          - "- ALWAYS pass the filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings"
          - "- ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging"
          - "- ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation"
          - "- NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode"
          - "- NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor the printed error messages"
          - "- NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior but means repeated runs on the same file are safe"
          - "-    # Process bottom-to-top (already sorted that way)"
          - "-            insert_docstring_at_line(filepath, lineno, name, doc_or_yaml, force_context=force_context)"
          - "-            if force_context:"
          - "-                print(f"  ✅ Added docstring + context print to {name}")"
          - "-                print(f"  ✅ Added docstring to {name}")"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Process a single file and generate docstrings.""""
          - "-        functions = extract_function_info(filepath)"
          - "-        print(f"\n  🤖 Generating docstring for {name}...")"
          - "-            docstring = generate_docstring(code, str(filepath), model=model)"
          - "-            insert_docstring_at_line(filepath, lineno, name, docstring, force_context=force_context)"
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors"
          - "-    with open(filepath, 'r') as f:"
          - "-        tree = ast.parse(f.read())"
          - "-    finder = FunctionFinder()"
          - "-    finder.visit(tree)"
          - "-    if not finder.functions:"
          - "-    print(f"  Found {len(finder.functions)} functions needing docstrings:")"
          - "-    for lineno, name in finder.functions:"
          - "-    for lineno, name in finder.functions:"
          - "-            code, node = extract_function_code(filepath, lineno)"
          - "-            insert_docstring(filepath, node, docstring, force_context=force_context)"
          - "- 2025-10-29: Add --model flag to choose between Claude models (Sonnet/Haiku)"
          - "-            docstring = generate_docstring(code, str(filepath))"
        ---/agentspec
    '''
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
    '''
    ---agentspec
    what: |
      CLI entry point for batch docstring generation across Python files with multi-provider LLM support.

      Accepts a target path (file or directory) and routes Python files through either critical or standard processing modes. Performs provider auto-detection (Anthropic/OpenAI-compatible), validates API credentials before processing, and defaults to local Ollama (http://localhost:11434/v1) if OpenAI provider is selected without credentials.

      Critical mode forces full regeneration of all docstrings for maximum accuracy by internally setting update_existing=True and delegating to process_file_critical(). Standard mode respects the update_existing flag to selectively regenerate or skip existing docstrings.

      Collects all Python files from target path using collect_python_files(), then iterates through each file, catching per-file exceptions to allow batch processing to continue despite individual failures. Dry-run mode prevents all file modifications and displays what would be processed. Returns 0 on success, 1 on credential validation failure or fatal errors.

      Inputs: target (str path), dry_run (bool), force_context (bool), model (str, defaults to "claude-haiku-4-5"), as_agentspec_yaml (bool), provider (str or None, defaults to 'auto'), base_url (str or None), update_existing (bool), critical (bool), terse (bool), diff_summary (bool).

      Outputs: int exit code (0 for success, 1 for failure).

      Edge cases: target path does not exist (returns 1 after validation), missing API credentials in non-dry-run mode (returns 1 with error message), per-file processing exceptions (caught and logged, batch continues), provider auto-detection when model name contains "claude" (forces Anthropic provider).
        deps:
          calls:
            - Path
            - collect_python_files
            - load_env_from_dotenv
            - lower
            - os.getenv
            - path.exists
            - print
            - process_file
            - process_file_critical
            - startswith
          imports:
            - agentspec.collect.collect_metadata
            - agentspec.utils.collect_python_files
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
      Centralizes provider detection and credential validation at batch entry point to prevent runtime failures across multiple files. Auto-detection logic (checking model name for "claude" prefix, falling back to Ollama for OpenAI provider) enables offline-first workflows without credential setup while maintaining explicit control via provider parameter.

      Critical mode ensures precision when accuracy is paramount by forcing regeneration; standard mode respects user intent via update_existing flag to avoid unnecessary API calls. Dry-run mode provides safe preview capability before committing changes.

      Per-file exception handling allows batch operations to be resilient—one malformed file or API failure does not block processing of remaining files. Early path validation prevents wasted API calls on non-existent targets.

      Lazy import of process_file_critical (only when critical=True) reduces module load overhead for standard mode operations.

    guardrails:
      - DO NOT proceed without valid API credentials (ANTHROPIC_API_KEY for Anthropic, OPENAI_API_KEY or base_url for OpenAI-compatible) unless dry_run=True, as this prevents silent failures mid-batch
      - DO NOT allow critical mode to skip regeneration; critical mode must always set update_existing=True internally to guarantee maximum accuracy
      - DO NOT hardcode model names or remove the model parameter; model selection must remain configurable for testing different Claude versions
      - DO NOT remove the dry-run early return; users depend on this to preview changes without file modification
      - ALWAYS validate target path exists before file collection to fail fast with clear error message
      - ALWAYS default to http://localhost:11434/v1 (local Ollama) if OpenAI provider is selected with no credentials, enabling offline-first workflows
      - ALWAYS preserve per-file exception handling to allow batch processing to continue despite individual file failures
      - ALWAYS load .env via load_env_from_dotenv() before credential checks to respect environment configuration
      - ALWAYS pass base_url through to process_file/process_file_critical to maintain provider configuration across batch operations
      - NOTE: This function modifies source files in-place during non-dry-run execution; ensure files are version-controlled or backed up
      - NOTE: Provider auto-detection checks model name for "claude" prefix (case-insensitive) to route to Anthropic; explicit provider parameter overrides this logic
      - NOTE: Batch processing catches exceptions per-file but does not retry; users should monitor printed error messages for failures

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings for them using Claude API"
          - "- Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user"
          - "- For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()"
          - "- Supports dry-run mode (--dry-run flag) to preview which functions would be processed without modifying files"
          - "- Supports force-context mode to inject print() statements alongside docstrings for debugging/tracing function execution"
          - "- Handles SyntaxError exceptions gracefully when files contain invalid Python syntax, and catches any exception during individual docstring generation to continue processing remaining functions"
          - "- Returns None in all cases (either after completion, early exit on syntax error, or early exit on dry-run)"
          - "- Called by: CLI entry point in agentspec/main.py or equivalent script runner that parses command-line arguments and invokes this for each file"
          - "- Calls: extract_function_info() [agentspec/extract.py] to parse file and identify functions, generate_docstring() [agentspec/generate.py or api module] to call Claude API, insert_docstring_at_line() [agentspec/insert.py] to modify source file"
          - "- Imports used: Path from pathlib (for cross-platform file path handling)"
          - "- External services: Anthropic Claude API (via generate_docstring wrapper) - requires valid API key in environment and network connectivity"
          - "- Processes functions bottom-to-top (assumes extract_function_info already sorts results) to avoid line number shifting as insertions are made from end of file backward, preventing cascading line offset errors"
          - "- Uses try-except around entire file extraction to catch SyntaxError early and fail gracefully rather than crashing, allowing batch processing of multiple files with some invalid"
          - "- Uses nested try-except within the processing loop to isolate failures to individual functions, ensuring one broken function doesn't prevent docstring generation for remaining functions in the same file"
          - "- Dry-run mode implemented as early return before any file modifications, allowing users to preview changes safely"
          - "- Force-context flag passed through to insert_docstring_at_line rather than handled here, maintaining separation of concerns (this function orchestrates, insert_docstring_at_line handles file mutation details)"
          - "- Model parameter exposed as argument (not hardcoded) to allow runtime selection of Claude models, supporting experimentation with different model versions"
          - "- Print statements used for user feedback rather than logging module to ensure immediate console output during long processing operations"
          - "- Alternative not used: streaming the Claude API response directly - would be more efficient but adds complexity; current approach waits for complete generation which is acceptable for docstring length"
          - "- Alternative not used: parallel/concurrent processing of functions - sequential processing chosen for simplicity and to avoid rate-limit issues with Claude API"
          - "- 2025-01-15: Initial implementation with support for dry-run mode, force-context flag, and Claude Sonnet model selection"
          - "- DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file"
          - "- DO NOT change the order of operations (extract -> check -> generate -> insert) without reviewing how line numbers are affected by insertions"
          - "- DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models"
          - "- DO NOT remove the dry-run early return; users depend on this to preview changes without file modification"
          - "- ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations"
          - "- ALWAYS pass the filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings"
          - "- ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging"
          - "- ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation"
          - "- NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode"
          - "- NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor the printed error messages"
          - "- NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior but means repeated runs on the same file are safe"
          - "-        functions = extract_function_info(filepath, require_agentspec=as_agentspec_yaml)"
          - "-        print("  ✅ All functions already have verbose docstrings")"
          - "-            doc_or_yaml = generate_docstring(code, str(filepath), model=model, as_agentspec_yaml=as_agentspec_yaml)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- Processes a single Python file to identify functions lacking verbose docstrings and generates comprehensive AI-consumable docstrings for them using Claude API"
          - "- Extracts all function definitions from the target file using AST parsing, filters to those without existing verbose docstrings, and displays a summary of findings to the user"
          - "- For each function needing a docstring, calls the Claude API via generate_docstring() to create AI-generated documentation, then inserts it into the source file at the correct line number using insert_docstring_at_line()"
          - "- Supports dry-run mode (--dry-run flag) to preview which functions would be processed without modifying files"
          - "- Supports force-context mode to inject print() statements alongside docstrings for debugging/tracing function execution"
          - "- Handles SyntaxError exceptions gracefully when files contain invalid Python syntax, and catches any exception during individual docstring generation to continue processing remaining functions"
          - "- Returns None in all cases (either after completion, early exit on syntax error, or early exit on dry-run)"
          - "- Called by: CLI entry point in agentspec/main.py or equivalent script runner that parses command-line arguments and invokes this for each file"
          - "- Calls: extract_function_info() [agentspec/extract.py] to parse file and identify functions, generate_docstring() [agentspec/generate.py or api module] to call Claude API, insert_docstring_at_line() [agentspec/insert.py] to modify source file"
          - "- Imports used: Path from pathlib (for cross-platform file path handling)"
          - "- External services: Anthropic Claude API (via generate_docstring wrapper) - requires valid API key in environment and network connectivity"
          - "- Processes functions bottom-to-top (assumes extract_function_info already sorts results) to avoid line number shifting as insertions are made from end of file backward, preventing cascading line offset errors"
          - "- Uses try-except around entire file extraction to catch SyntaxError early and fail gracefully rather than crashing, allowing batch processing of multiple files with some invalid"
          - "- Uses nested try-except within the processing loop to isolate failures to individual functions, ensuring one broken function doesn't prevent docstring generation for remaining functions in the same file"
          - "- Dry-run mode implemented as early return before any file modifications, allowing users to preview changes safely"
          - "- Force-context flag passed through to insert_docstring_at_line rather than handled here, maintaining separation of concerns (this function orchestrates, insert_docstring_at_line handles file mutation details)"
          - "- Model parameter exposed as argument (not hardcoded) to allow runtime selection of Claude models, supporting experimentation with different model versions"
          - "- Print statements used for user feedback rather than logging module to ensure immediate console output during long processing operations"
          - "- Alternative not used: streaming the Claude API response directly - would be more efficient but adds complexity; current approach waits for complete generation which is acceptable for docstring length"
          - "- Alternative not used: parallel/concurrent processing of functions - sequential processing chosen for simplicity and to avoid rate-limit issues with Claude API"
          - "- 2025-01-15: Initial implementation with support for dry-run mode, force-context flag, and Claude Sonnet model selection"
          - "- DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file"
          - "- DO NOT change the order of operations (extract -> check -> generate -> insert) without reviewing how line numbers are affected by insertions"
          - "- DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models"
          - "- DO NOT remove the dry-run early return; users depend on this to preview changes without file modification"
          - "- ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations"
          - "- ALWAYS pass the filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings"
          - "- ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging"
          - "- ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation"
          - "- NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode"
          - "- NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor the printed error messages"
          - "- NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior but means repeated runs on the same file are safe"
          - "-    # Process bottom-to-top (already sorted that way)"
          - "-            insert_docstring_at_line(filepath, lineno, name, doc_or_yaml, force_context=force_context)"
          - "-            if force_context:"
          - "-                print(f"  ✅ Added docstring + context print to {name}")"
          - "-                print(f"  ✅ Added docstring to {name}")"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Process a single file and generate docstrings.""""
          - "-        functions = extract_function_info(filepath)"
          - "-        print(f"\n  🤖 Generating docstring for {name}...")"
          - "-            docstring = generate_docstring(code, str(filepath), model=model)"
          - "-            insert_docstring_at_line(filepath, lineno, name, docstring, force_context=force_context)"
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors"
          - "-    with open(filepath, 'r') as f:"
          - "-        tree = ast.parse(f.read())"
          - "-    finder = FunctionFinder()"
          - "-    finder.visit(tree)"
          - "-    if not finder.functions:"
          - "-    print(f"  Found {len(finder.functions)} functions needing docstrings:")"
          - "-    for lineno, name in finder.functions:"
          - "-    for lineno, name in finder.functions:"
          - "-            code, node = extract_function_code(filepath, lineno)"
          - "-            insert_docstring(filepath, node, docstring, force_context=force_context)"
          - "- 2025-10-29: Add --model flag to choose between Claude models (Sonnet/Haiku)"
          - "-            docstring = generate_docstring(code, str(filepath))"
        ---/agentspec
    '''
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
    '''
    ---agentspec
    what: |
      CLI entry point that parses command-line arguments and delegates to docstring generation.

      Accepts a positional path argument (file or directory) and optional flags:
      - `--dry-run`: Preview changes without modifying files
      - `--force-context`: Insert print() statements to force LLMs to load docstrings into context
      - `--model MODEL`: Specify Claude model variant (defaults to claude-haiku-4-5)

      Validates that at least one argument is provided; exits with code 1 and displays usage if missing.
      Extracts model name from `--model` flag if present, otherwise uses default.
      Passes all parsed arguments (path, dry_run, force_context, model) to run() function.
      Exits process with the exit code returned by run(), indicating success (0) or failure (non-zero).

      Supported models: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022.
      Requires ANTHROPIC_API_KEY environment variable to be set before execution.
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
      Manual argv parsing without argparse dependency keeps the single-file script minimal and self-contained.
      Early validation of required path argument prevents silent failures and follows Unix convention (exit 1 on invalid input).
      Model flag enables runtime switching between Claude variants without code modifications, allowing users to trade off speed/cost (Haiku) versus quality (Sonnet).
      Default to claude-haiku-4-5 optimizes for speed and cost efficiency while maintaining reasonable output quality.
      Boolean flags use simple string membership checks for clarity and minimal overhead in a lightweight CLI.
      Usage message printed to stdout ensures visibility without requiring log configuration.

    guardrails:
      - DO NOT parse arguments without updating the usage message to match all supported flags
      - DO NOT remove ANTHROPIC_API_KEY environment variable mention from usage text
      - DO NOT add required positional arguments without updating the len(sys.argv) < 2 validation check
      - DO NOT alter the default model without updating all documentation and usage text that references it
      - ALWAYS validate model_index + 1 < len(sys.argv) before accessing sys.argv[model_index + 1] to prevent IndexError
      - ALWAYS pass all parsed arguments to run() in correct order: path, dry_run, force_context, model
      - ALWAYS preserve sys.exit(1) behavior when arguments are invalid to follow Unix conventions
      - ALWAYS ensure usage message stays in sync with actual supported flags and model options
      - DO NOT validate model names here; invalid models will fail at API call time inside run()
      - DO NOT perform environment variable validation here; that occurs inside run()

        changelog:
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- Parses command-line arguments to extract the target file/directory path, optional flags (--dry-run, --force-context), and model selection (--model)"
          - "- Validates that at least one argument (the file/directory path) is provided; exits with status code 1 and displays usage information if validation fails"
          - "-    - Extracts the model name from argv if --model flag is present, otherwise defaults to "claude-sonnet-4-20250514""
          - "- Passes the parsed arguments to the run() function which performs the actual docstring generation logic"
          - "- Exits the process with the exit code returned by run(), which indicates success (0) or various failure modes (non-zero)"
          - "- The usage message explicitly documents all supported flags and model options for end-user reference"
          - "- Called by: Python interpreter when generate.py is executed as __main__"
          - "- Calls: run(path, dry_run, force_context, model) - the core execution function that handles file processing and API calls"
          - "- Imports used: sys (for sys.argv, sys.exit()), and implicitly the run() function from the same module"
          - "- External services: Indirectly depends on Anthropic API via run() function; requires ANTHROPIC_API_KEY environment variable to be set before execution"
          - "- Simple manual argv parsing was chosen over argparse/click to keep the CLI minimal and reduce dependencies for a single-file script"
          - "-    - The default model is set to claude-sonnet-4-20250514 (a recent, capable model) rather than an older baseline, optimizing for quality of generated docstrings"
          - "- The --model flag allows flexibility for users to switch between different Claude models (haiku for speed/cost, sonnet for quality) without code changes"
          - "- Usage is printed to stdout rather than using logging to ensure visibility even without log configuration"
          - "- The early exit(1) on missing arguments follows Unix convention and prevents silent failures that could mask user errors"
          - "- Boolean flags (--dry-run, --force-context) use simple string membership checks rather than a full parser for clarity and minimal overhead"
          - "- Current implementation: Initial entry point design with support for three command-line flags and model selection via --model parameter"
          - "- DO NOT change the argument parsing logic without updating the usage message to match"
          - "- DO NOT remove the ANTHROPIC_API_KEY environment variable mention from usage text"
          - "- DO NOT alter the default model without updating all documentation that references it"
          - "- DO NOT add new required positional arguments without updating the len(sys.argv) < 2 check"
          - "- ALWAYS preserve the sys.exit(1) behavior when arguments are invalid"
          - "- ALWAYS pass all parsed arguments to run() in the correct order (path, dry_run, force_context, model)"
          - "- ALWAYS ensure the usage message stays in sync with actual supported flags"
          - "- ALWAYS validate model_index + 1 < len(sys.argv) before accessing argv to prevent IndexError"
          - "- NOTE: This function is the CLI entry point and determines user experience; any changes to argument handling will affect all downstream users"
          - "- NOTE: The model parameter is passed directly to the Anthropic API without validation; invalid model names will fail at API call time, not here"
          - "- NOTE: No error handling exists for environment variable validation here; that occurs inside run()"
          - "-    print(f"[AGENTSPEC_CONTEXT] main: Parses command-line arguments to extract the target file/directory path, optional flags (--dry-run, --force-context), and model selection (--model) | Validates that at least one argument (the file/directory path) is provided; exits with status code 1 and displays usage information if validation fails | Extracts the model name from argv if --model flag is present, otherwise defaults to \"claude-sonnet-4-20250514\"")"
          - "-        print("  --model MODEL       Claude model to use (default: claude-sonnet-4-20250514)")"
          - "-    model = "claude-sonnet-4-20250514""
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Standalone script entry point.""""
          - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors"
          - "-        print("                      Options: claude-haiku-4-5-20250929, claude-sonnet-4-5-20250929")"
          - "- 2025-10-29: Add --model flag to choose between Claude models (Sonnet/Haiku)"
          - "-        print("Usage: python generate.py <file_or_dir> [--dry-run] [--force-context]")"
          - "-        print("  --dry-run        Preview without modifying files")"
          - "-        print("  --force-context  Add print() statements to force LLMs to load context")"
          - "-    exit_code = run(path, dry_run, force_context)"
          - "- 2025-10-29: Add --force-context flag to insert print() statements that force LLMs to load docstrings into context"
          - "-        print("Usage: python generate.py <file_or_dir> [--dry-run]")"
          - "-    exit_code = run(path, dry_run)"
        ---/agentspec
    '''
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
