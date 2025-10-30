#!/usr/bin/env python3
"""
Auto-generate verbose agentspec docstrings using Claude.
"""
import ast
import sys
import os
from pathlib import Path
from agentspec.utils import collect_python_files
from anthropic import Anthropic

# Initialize Claude client
client = Anthropic()  # Reads ANTHROPIC_API_KEY from env

GENERATION_PROMPT = """You are helping to document a Python codebase with extremely verbose docstrings designed for AI agent consumption.

Analyze this function and generate a comprehensive docstring following this EXACT format:

\"\"\"
Brief one-line description.

WHAT THIS DOES:
- Detailed explanation of what this function does (3-5 lines)
- Include edge cases, error handling, return values
- Be specific about types and data flow

DEPENDENCIES:
- Called by: [list files/functions that call this, if you can infer from context]
- Calls: [list functions this calls]
- Imports used: [key imports this relies on]
- External services: [APIs, databases, etc. if applicable]

WHY THIS APPROACH:
- Explain why this implementation was chosen
- Note any alternatives that were NOT used and why
- Document performance considerations
- Explain any "weird" or non-obvious code

CHANGELOG:
- [Current date]: Initial implementation (or describe what changed)

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

AGENTSPEC_YAML_PROMPT = """You are helping to document a Python codebase by creating an embedded agentspec YAML block inside a Python docstring.

Requirements:
- Output ONLY the YAML block fenced by the following exact delimiters:
  ---agentspec
  ... YAML content here ...
  ---/agentspec
- Follow this schema with verbose content:
  what: |
    Detailed multi-line explanation of behavior, inputs, outputs, edge-cases
  deps:
    calls: []
    called_by: []
    config_files: []
    environment: []
  why: |
    Rationale for approach and tradeoffs
  guardrails:
    - DO NOT ... (explain why)
    - ...
  changelog:
    - "YYYY-MM-DD: Initial agentspec generated"

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

def extract_function_info(filepath: Path, require_agentspec: bool = False) -> list[tuple[int, str, str]]:
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
            # Check if needs docstring
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

def generate_docstring(code: str, filepath: str, model: str = "claude-sonnet-4-20250514", as_agentspec_yaml: bool = False) -> str:
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
    - External services: Anthropic Claude API (claude-sonnet-4-20250514 model by default, or specified model parameter); requires valid API key in environment

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
    print(f"[AGENTSPEC_CONTEXT] generate_docstring: Accepts a code string and filepath, sends them to Claude API with a prompt to generate either a verbose docstring or a fenced agentspec YAML block | Constructs an API message with the code and filepath injected into the selected template, requesting up to 2000 tokens of output | Extracts and returns the text content from Claude's first message response")
    
    prompt = AGENTSPEC_YAML_PROMPT if as_agentspec_yaml else GENERATION_PROMPT
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": prompt.format(
                code=code,
                filepath=filepath
            )
        }]
    )
    
    return message.content[0].text

def insert_docstring_at_line(filepath: Path, lineno: int, func_name: str, docstring: str, force_context: bool = False):
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
    
    # Find the function definition line
    func_line_idx = lineno - 1
    
    # Find the first line after the function signature (where docstring goes)
    insert_idx = func_line_idx + 1
    
    # Skip any existing docstring if present
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
    
    # Format new docstring
    new_lines = []
    new_lines.append(f'{indent}"""\n')
    for line in docstring.split('\n'):
        if line.strip():
            new_lines.append(f'{indent}{line}\n')
        else:
            new_lines.append('\n')
    new_lines.append(f'{indent}"""\n')
    
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
    
    # Insert the new docstring
    for line in reversed(new_lines):
        lines.insert(insert_idx, line)
    
    # Write back
    with open(filepath, 'w') as f:
        f.writelines(lines)

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-sonnet-4-20250514", as_agentspec_yaml: bool = False):
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
        functions = extract_function_info(filepath, require_agentspec=as_agentspec_yaml)
    except SyntaxError as e:
        print(f"  ❌ Syntax error in file: {e}")
        return
    
    if not functions:
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
    
    # Process bottom-to-top (already sorted that way)
    for lineno, name, code in functions:
        print(f"\n  🤖 Generating {'agentspec YAML' if as_agentspec_yaml else 'docstring'} for {name}...")
        
        try:
            doc_or_yaml = generate_docstring(code, str(filepath), model=model, as_agentspec_yaml=as_agentspec_yaml)
            insert_docstring_at_line(filepath, lineno, name, doc_or_yaml, force_context=force_context)
            
            if force_context:
                print(f"  ✅ Added docstring + context print to {name}")
            else:
                print(f"  ✅ Added docstring to {name}")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, dry_run: bool = False, force_context: bool = False, model: str = "claude-sonnet-4-20250514", as_agentspec_yaml: bool = False) -> int:
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
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return 1
    
    path = Path(target)
    
    if not path.exists():
        print(f"❌ Error: Path does not exist: {target}")
        return 1
    
    if dry_run:
        print("🔍 DRY RUN MODE - no files will be modified\n")
    
    try:
        files = collect_python_files(path)
        for filepath in files:
            try:
                process_file(filepath, dry_run, force_context, model, as_agentspec_yaml)
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
    - Extracts the model name from argv if --model flag is present, otherwise defaults to "claude-sonnet-4-20250514"
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
    - The default model is set to claude-sonnet-4-20250514 (a recent, capable model) rather than an older baseline, optimizing for quality of generated docstrings
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
    print(f"[AGENTSPEC_CONTEXT] main: Parses command-line arguments to extract the target file/directory path, optional flags (--dry-run, --force-context), and model selection (--model) | Validates that at least one argument (the file/directory path) is provided; exits with status code 1 and displays usage information if validation fails | Extracts the model name from argv if --model flag is present, otherwise defaults to \"claude-sonnet-4-20250514\"")
    if len(sys.argv) < 2:
        print("Usage: python generate.py <file_or_dir> [--dry-run] [--force-context] [--model MODEL]")
        print("\nRequires ANTHROPIC_API_KEY environment variable")
        print("\nOptions:")
        print("  --dry-run           Preview without modifying files")
        print("  --force-context     Add print() statements to force LLMs to load context")
        print("  --model MODEL       Claude model to use (default: claude-sonnet-4-20250514)")
        print("                      Options: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022")
        sys.exit(1)
    
    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    force_context = '--force-context' in sys.argv
    
    # Parse model flag
    model = "claude-sonnet-4-20250514"
    if '--model' in sys.argv:
        model_index = sys.argv.index('--model')
        if model_index + 1 < len(sys.argv):
            model = sys.argv[model_index + 1]
    
    exit_code = run(path, dry_run, force_context, model)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
