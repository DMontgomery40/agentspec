"""
agentspec.langs.python_adapter
------------------------------
Language adapter implementation for Python source files.

Provides docstring extraction/insertion, metadata gathering, and syntax validation
for Python using the ast module.

---agentspec
what: |
  Adapts Python-specific functionality into the LanguageAdapter protocol.
  
  Relocates existing Python AST analysis from core modules into a cohesive adapter
  that handles:
  - File discovery using collect_python_files() logic
  - Docstring extraction from ast nodes
  - Docstring insertion into Python source
  - Metadata gathering (function calls, imports) via ast traversal
  - Syntax validation via compile()
  - Python-specific comment delimiters (triple quotes, #)

deps:
  calls:
    - ast, pathlib, agentspec.utils, agentspec.collect
  called_by:
    - agentspec.langs.__init__
    - agentspec.collect
    - agentspec.extract
    - agentspec.lint
    - agentspec.generate
  imports:
    - ast
    - pathlib.Path
    - agentspec.utils.collect_python_files
    - agentspec.collect module functions

why: |
  Extracting Python-specific code into an adapter allows core processing logic
  to remain language-agnostic. This enables adding JavaScript and other languages
  without modifying collect.py, extract.py, lint.py, etc.
  
  The adapter preserves all guardrails and behavior from the original Python
  implementation while wrapping it behind a common interface.

guardrails:
  - DO NOT remove or significantly alter Python AST analysis behavior; existing guardrails still apply
  - DO NOT merge this with JavaScript adapter logic; keep language-specific concerns isolated
  - ALWAYS delegate to existing Python utilities rather than reimplementing AST traversal

changelog:
  - "2025-10-31: Extract Python implementation from core modules into adapter"
---/agentspec
"""

from __future__ import annotations
from typing import Set, Dict, Optional, List
from pathlib import Path
import ast
import inspect


class PythonAdapter:
    """
    Language adapter for Python (.py, .pyi) files.
    
    Implements the LanguageAdapter protocol using ast module for parsing
    and analysis.
    """

    @property
    def file_extensions(self) -> Set[str]:
        """
        ---agentspec
        what: |
          Returns a set containing the file extensions that the Python adapter is responsible for handling. Specifically returns {'.py', '.pyi'}, representing Python source files and Python stub files respectively.

          The method takes no parameters beyond self and returns a Set[str] containing exactly two string elements: '.py' for standard Python source code files and '.pyi' for Python type stub files used by type checkers and IDEs.

          This is a read-only accessor that provides a consistent interface for querying which file types this adapter processes. The returned set is immutable in intent (though technically mutable as a set object) and should be treated as a constant definition of the adapter's scope.

          Edge cases: The method always returns the same set regardless of adapter state or configuration. There are no conditional branches or dynamic behavior—it is purely declarative.
            deps:
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This method exists to provide a standardized way for the adapter framework to determine file type compatibility without hardcoding extension lists throughout the codebase. By centralizing extension definitions in the adapter itself, the system can dynamically discover which file types each language adapter supports.

          The choice to include both '.py' and '.pyi' reflects that Python type stubs are semantically part of the Python ecosystem and should be processed with the same logic as source files. This design allows a single adapter to handle both file types rather than requiring separate adapters.

          Returning a set (rather than a list or tuple) emphasizes that order is irrelevant and membership testing is the primary use case, which is semantically clearer and potentially more efficient for lookups.

        guardrails:
          - DO NOT modify the returned set in-place, as it may be cached or reused by the framework; treat the return value as read-only
          - DO NOT add or remove extensions dynamically based on runtime state; this method should always return the same set to maintain predictable adapter behavior
          - DO NOT return extensions without the leading dot (e.g., 'py' instead of '.py'), as the framework expects normalized extension format with dots

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return {'.py', '.pyi'}

    def discover_files(self, target: Path) -> List[Path]:
        """
        ---agentspec
        what: |
          Discovers all Python files within a target directory or returns a single file if target is a file path.

          Accepts a Path object pointing to either a directory or a file. When given a directory, recursively collects all Python source files (.py extension) from that directory tree. When given a file path, returns that file wrapped in a list.

          Delegates to agentspec.utils.collect_python_files() for the actual discovery logic, which applies intelligent filtering:
          - Respects .gitignore rules to exclude version-controlled ignored paths
          - Excludes common non-source directories: .venv, venv, __pycache__, .git, .tox, node_modules, dist, build, *.egg-info
          - Skips hidden directories (prefixed with .)
          - Returns results as a list of Path objects in consistent order

          Handles edge cases:
          - Empty directories return empty list
          - Symlinks are followed during traversal
          - Permission errors on subdirectories are silently skipped
          - Non-existent paths raise FileNotFoundError from underlying pathlib operations

          Returns: List[Path] - ordered collection of discovered Python file paths, may be empty if no Python files found
            deps:
              calls:
                - collect_python_files
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Centralizes file discovery logic to ensure consistent behavior across the codebase. Delegating to a shared utility function (collect_python_files) prevents duplication and ensures all adapters respect the same filtering rules.

          Importing collect_python_files locally within the method avoids circular dependency issues that would occur if imported at module level, since utils may import from other adapter modules.

          Respecting .gitignore is important for development workflows where developers intentionally exclude directories from version control (e.g., virtual environments, build artifacts). Including these would pollute analysis results and slow discovery.

          Excluding __pycache__ and build artifacts prevents analyzing stale bytecode or generated files that don't represent actual source intent.

        guardrails:
          - DO NOT modify .gitignore during discovery - treat it as read-only configuration that reflects developer intent
          - DO NOT follow symlinks that create cycles - this would cause infinite recursion; rely on os.walk's cycle detection
          - DO NOT raise exceptions for permission-denied on individual files/subdirectories - silently skip them to allow partial discovery of accessible portions
          - DO NOT cache results across calls - each invocation should reflect current filesystem state in case files were added/removed
          - DO NOT assume target path exists before calling - let pathlib raise appropriate FileNotFoundError for missing paths

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        # Import here to avoid circular dependencies
        from agentspec.utils import collect_python_files
        return collect_python_files(target)

    def extract_docstring(self, filepath: Path, lineno: int) -> Optional[str]:
        """
        ---agentspec
        what: |
          Extracts the docstring from a Python function, async function, or class definition located at a specific line number in a given file.

          **Inputs:**
          - filepath: Path object pointing to a Python source file
          - lineno: Integer line number where the target function/class is defined

          **Outputs:**
          - Returns the raw docstring as a string if found (including any embedded agentspec YAML blocks)
          - Returns None if the file cannot be parsed, the line number doesn't match any definition, or no docstring exists

          **Behavior:**
          - Opens and reads the file with UTF-8 encoding
          - Parses the entire file into an AST (Abstract Syntax Tree)
          - Walks the AST to find function, async function, or class nodes matching the exact line number
          - Uses ast.get_docstring() to extract the docstring, which handles both raw strings and formatted docstrings
          - Silently returns None on parse failures (SyntaxError, UnicodeDecodeError) rather than raising

          **Edge cases:**
          - File encoding issues: caught and returns None
          - Invalid Python syntax: caught and returns None
          - Line number mismatch: no matching node found, returns None
          - Docstring absence: ast.get_docstring() returns None for definitions without docstrings
          - Multiple definitions on same line: returns docstring of first match found during walk
            deps:
              calls:
                - ast.get_docstring
                - ast.parse
                - ast.walk
                - f.read
                - isinstance
                - open
                - str
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This approach uses Python's built-in ast module for reliable, syntax-aware parsing rather than regex or line-based text matching. AST parsing correctly handles complex syntax (decorators, nested definitions, multi-line signatures) and provides precise node location matching via lineno. The silent failure mode (returning None) allows callers to gracefully handle unparseable files without exception handling overhead. Using ast.get_docstring() ensures compatibility with PEP 257 docstring conventions and automatically strips leading indentation.

        guardrails:
          - DO NOT assume the file is valid Python syntax; always catch SyntaxError and return None rather than propagating exceptions that could crash the extraction pipeline
          - DO NOT use regex-based docstring extraction; it will fail on edge cases like docstrings containing triple quotes or complex string escaping
          - DO NOT modify or validate the docstring content; return it raw to preserve embedded agentspec blocks and allow downstream processors to parse them
          - DO NOT assume lineno uniquely identifies a definition; use exact equality matching and return on first match to handle edge cases consistently
          - DO NOT attempt to handle file I/O errors (PermissionError, FileNotFoundError) separately; let them propagate as they indicate configuration or environment issues, not parsing failures

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError):
            return None

        # Find the function or class at lineno
        for node in ast.walk(tree):
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and 
                node.lineno == lineno):
                return ast.get_docstring(node)

        return None

    def insert_docstring(self, filepath: Path, lineno: int, docstring: str) -> None:
        """
        ---agentspec
        what: |
          Inserts or replaces a docstring for a function, async function, or class at a specified line number in a Python source file.

          **Inputs:**
          - filepath: Path object pointing to a Python source file
          - lineno: Integer line number where target function/class definition begins
          - docstring: String content to insert as the docstring (without quotes)

          **Outputs:**
          - Modifies the file in-place; no return value
          - Writes updated source back to filepath with docstring inserted/replaced

          **Behavior:**
          1. Reads entire source file and parses it into an AST
          2. Walks AST to find FunctionDef, AsyncFunctionDef, or ClassDef node at exact lineno
          3. Detects if a docstring already exists (first statement is string Expr)
          4. If docstring exists: replaces lines from docstring start to end
          5. If no docstring: inserts after function/class definition line
          6. Preserves indentation by extracting indent from target node and applying to all docstring lines
          7. Formats docstring with triple double-quotes and writes file back

          **Edge cases:**
          - File with syntax errors raises ValueError
          - No matching function/class at lineno raises ValueError
          - Empty docstring string is valid and produces empty triple-quoted string
          - Multi-line docstrings preserve internal line structure with consistent indentation
          - Handles both old-style ast.Str and new-style ast.Constant string nodes
            deps:
              calls:
                - ValueError
                - _get_indent
                - ast.parse
                - ast.walk
                - chr
                - f.read
                - f.write
                - isinstance
                - join
                - open
                - quoted_docstring.split
                - source.split
                - str
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          AST-based approach ensures precise targeting of the correct definition by line number rather than fragile text pattern matching. Parsing validates file syntax upfront. Walking the tree finds the exact node, avoiding ambiguity with nested functions or classes. Detecting existing docstrings allows safe replacement without duplicating or orphaning old content. Preserving indentation maintains code style consistency. Reading entire file and writing back is simpler than seeking/truncating and avoids partial-write corruption risks.

        guardrails:
          - DO NOT assume lineno matches the first line of a multi-line function signature; use AST node.lineno which points to the def/class keyword line
          - DO NOT modify the file if AST parsing fails; raise ValueError to prevent corrupting unparseable source
          - DO NOT attempt to preserve comments or formatting beyond indentation; AST round-trip loses non-semantic whitespace
          - DO NOT insert docstring if target node body is empty; this would create invalid syntax (class/function with only docstring and no pass)
          - DO NOT use string slicing to find old docstring boundaries; rely on AST node.lineno and node.end_lineno for accuracy across quote styles and escape sequences

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            raise ValueError(f"Cannot parse {filepath}: syntax error")

        # Find the function or class at lineno
        target_node = None
        for node in ast.walk(tree):
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and 
                node.lineno == lineno):
                target_node = node
                break

        if not target_node:
            raise ValueError(f"No function or class found at line {lineno} in {filepath}")

        lines = source.split('\n')
        indent = _get_indent(target_node)

        # Check if docstring exists
        if (target_node.body and 
            isinstance(target_node.body[0], ast.Expr) and 
            isinstance(target_node.body[0].value, (ast.Str, ast.Constant))):
            # Replace existing docstring
            old_docstring_node = target_node.body[0]
            old_end_line = old_docstring_node.end_lineno
            old_start_line = old_docstring_node.lineno - 1
        else:
            # Insert new docstring after function/class definition line
            old_start_line = target_node.lineno
            old_end_line = target_node.lineno

        # Format new docstring with proper indentation
        quote = chr(34) * 3  # Triple double-quote
        quoted_docstring = f'{quote}{docstring}{quote}'
        indented_docstring = '\n'.join(
            f'{indent}{line}' if line else ''
            for line in quoted_docstring.split('\n')
        )

        # Replace lines
        lines[old_start_line:old_end_line] = [indented_docstring]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def gather_metadata(self, filepath: Path, function_name: str) -> Dict:
        """
        ---agentspec
        what: |
          Extracts static metadata from a Python source file for a specified function using Abstract Syntax Tree (AST) parsing.

          **Inputs:**
          - filepath (Path): File system path to a Python source file
          - function_name (str): Name of the target function to analyze

          **Outputs:**
          - Dict with three keys:
            - 'calls': List of function calls made within the target function
            - 'imports': List of module-level imports in the file
            - 'called_by': List of callers of the target function (currently empty, reserved for future use)

          **Behavior:**
          1. Opens and reads the file with UTF-8 encoding
          2. Parses file contents into an AST
          3. Walks the AST to locate a FunctionDef or AsyncFunctionDef node matching function_name
          4. Extracts function calls from the matched function body using agentspec.collect._get_function_calls()
          5. Extracts all module-level imports using agentspec.collect._get_module_imports()
          6. Returns empty lists for all keys if file cannot be parsed or function not found

          **Edge Cases:**
          - SyntaxError or UnicodeDecodeError during file read returns empty metadata dict
          - Function name not found in AST results in empty 'calls' list but imports still populated
          - Async functions handled identically to sync functions
          - Multiple functions with same name: only first match processed (ast.walk order)
            deps:
              calls:
                - ast.parse
                - ast.walk
                - collect._get_function_calls
                - collect._get_module_imports
                - f.read
                - isinstance
                - open
                - str
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          AST-based static analysis provides accurate, dependency-free extraction of code structure without executing code. This approach:
          - Avoids runtime side effects and security risks of dynamic execution
          - Handles both sync and async functions uniformly
          - Gracefully degrades on malformed Python files rather than crashing
          - Integrates with agentspec.collect utilities for consistent metadata extraction across the codebase
          - Enables dependency graph construction and call chain analysis for documentation and tooling

        guardrails:
          - DO NOT execute the parsed code or use eval/exec—AST parsing is intentionally static to prevent arbitrary code execution
          - DO NOT assume function_name is unique—only the first matching function is analyzed; document this limitation if multiple definitions exist
          - DO NOT rely on 'called_by' field—it is currently unpopulated and reserved; do not assume it contains meaningful data
          - DO NOT skip error handling for file I/O—encoding errors and syntax errors are common in large codebases and must return safe defaults
          - DO NOT parse files without UTF-8 encoding declaration without explicit user confirmation—non-UTF-8 files may silently fail or corrupt metadata

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError):
            return {'calls': [], 'imports': [], 'called_by': []}

        # Import from agentspec.collect for analysis
        from agentspec import collect
        
        result = {
            'calls': [],
            'imports': [],
            'called_by': [],
        }

        # Find the target function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    result['calls'] = collect._get_function_calls(node)
                    break

        # Get module-level imports
        result['imports'] = collect._get_module_imports(tree)

        return result

    def validate_syntax(self, filepath: Path) -> bool:
        """
        ---agentspec
        what: |
          Validates Python source file syntax by attempting to compile the file contents.

          **Inputs:**
          - filepath: Path object pointing to a Python source file

          **Outputs:**
          - Returns True if file contains valid Python syntax
          - Raises ValueError (wrapping SyntaxError) if syntax is invalid, with message containing filepath and original error details

          **Behavior:**
          - Opens file with UTF-8 encoding
          - Reads entire file contents into memory
          - Attempts compilation using Python's built-in compile() function with 'exec' mode
          - Catches SyntaxError exceptions and re-raises as ValueError with contextual information

          **Edge cases:**
          - File not found: FileNotFoundError propagates uncaught
          - Encoding errors: UnicodeDecodeError propagates uncaught
          - Empty files: Valid (compile succeeds on empty string)
          - Large files: Entire contents loaded into memory (potential memory concern for very large files)
          - Permission denied: PermissionError propagates uncaught
            deps:
              calls:
                - ValueError
                - compile
                - f.read
                - open
                - str
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Using compile() with 'exec' mode provides accurate syntax validation matching Python's actual parser behavior, avoiding regex-based or AST-based approximations that could miss edge cases. Re-raising as ValueError provides a consistent exception interface for the adapter layer rather than exposing language-specific SyntaxError. UTF-8 encoding is standard for Python source files per PEP 263. The try-except pattern is minimal and explicit about which error condition is handled, allowing other I/O errors to surface naturally for debugging.

        guardrails:
          - DO NOT silently return False on syntax errors—raising an exception forces callers to handle validation failures explicitly rather than accidentally proceeding with invalid code
          - DO NOT catch FileNotFoundError or PermissionError—these indicate environmental issues that should propagate to the caller for proper handling, not be masked as syntax problems
          - DO NOT use ast.parse() as the sole validation method without compile()—compile() catches additional syntax issues that AST parsing might defer
          - DO NOT load entire file into memory without considering file size limits—very large files could cause memory exhaustion; consider streaming or size checks for production use
          - DO NOT modify the exception message format without updating dependent error handling code that may parse the filepath from the ValueError message

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), str(filepath), 'exec')
            return True
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {filepath}: {e}")

    def validate_syntax_string(self, source: str, filepath: Path = None) -> bool:
        """
        ---agentspec
        what: |
          Validates Python source code syntax by attempting to compile it without execution.

          **Inputs:**
          - source (str): Python source code to validate
          - filepath (Path, optional): File path for error reporting context; defaults to '<string>' if not provided

          **Outputs:**
          - Returns True if syntax is valid
          - Raises ValueError wrapping the original SyntaxError if syntax is invalid

          **Behavior:**
          - Uses Python's built-in compile() function with 'exec' mode to parse the entire source
          - Catches SyntaxError exceptions and re-raises them as ValueError with formatted error message
          - Filepath parameter is converted to string for compile() compatibility; None values are replaced with '<string>' placeholder

          **Edge Cases:**
          - Empty strings compile successfully (valid Python)
          - Incomplete code (e.g., unclosed parentheses) raises SyntaxError → ValueError
          - Unicode and encoding issues in source may raise SyntaxError → ValueError
          - Very large source strings are processed without truncation
          - Filepath=None produces generic '<string>' in error messages, reducing debugging context
            deps:
              calls:
                - ValueError
                - compile
                - str
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Using compile() with 'exec' mode provides the most accurate syntax validation without executing code, matching Python's own parser behavior. Re-raising as ValueError (rather than SyntaxError) provides a consistent exception interface for the adapter layer, allowing callers to handle validation errors uniformly without importing language-specific exceptions. The optional filepath parameter enables better error diagnostics when validating files, while gracefully degrading to a placeholder for in-memory strings. This approach is lightweight and leverages the standard library rather than external parsing tools.

        guardrails:
          - DO NOT execute the compiled code; compile() with 'exec' mode only parses without running, preventing arbitrary code execution during validation
          - DO NOT suppress or silently ignore SyntaxError; re-raising as ValueError ensures validation failures are visible to callers
          - DO NOT assume filepath is always provided; the None check prevents TypeError when passing None to str()
          - DO NOT modify the source string; validation must be read-only to avoid side effects
          - DO NOT validate semantics (e.g., undefined variables, type mismatches); this function only checks syntax, not runtime correctness

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            compile(source, str(filepath) if filepath else '<string>', 'exec')
            return True
        except SyntaxError as e:
            raise ValueError(f"Syntax error: {e}")

    def get_comment_delimiters(self) -> tuple[str, str]:
        '''
        ---agentspec
        what: |
          Returns a tuple containing the opening and closing delimiters for Python multi-line string comments.

          The function constructs the delimiter by repeating the double-quote character (ASCII 34) three times,
          producing the standard Python triple-quote string delimiter (""").

          Inputs: None (instance method, no parameters)

          Outputs: A tuple of two strings, each containing three double-quote characters.
          The tuple format is (opening_delimiter, closing_delimiter), both identical for Python's symmetric
          triple-quote syntax.

          Edge cases:
          - The function uses chr(34) to obtain the double-quote character, ensuring proper character encoding
            regardless of string literal representation in the source code.
          - Both elements of the returned tuple are identical since Python uses the same delimiter for opening
            and closing multi-line strings.
          - This method is deterministic and stateless; it always returns the same value.
            deps:
              calls:
                - chr
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This method abstracts the language-specific comment delimiter syntax into a reusable interface.
          By using chr(34) instead of hardcoding a string literal, the code avoids potential issues with
          quote escaping and makes the intent explicit: we are constructing delimiters programmatically.

          The tuple return type (rather than separate methods) allows callers to unpack delimiters in a
          single operation and supports polymorphic implementations across different language adapters.

          Returning identical opening and closing delimiters reflects Python's symmetric triple-quote syntax,
          simplifying downstream logic that wraps content with these delimiters.

        guardrails:
          - DO NOT modify the delimiter strings after retrieval; they represent immutable language syntax rules.
          - DO NOT assume the delimiters are unique across different language adapters; other languages may
            use different or asymmetric delimiters (e.g., /* */ in C-style languages).
          - DO NOT use this method for single-line comment detection; Python single-line comments use # and
            require a separate method.

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        '''
        triple_quote = chr(34) * 3
        return (triple_quote, triple_quote)

    def parse(self, source_code: str) -> ast.Module:
        """
        ---agentspec
        what: |
          Parses Python source code string into an Abstract Syntax Tree (AST) module object.

          Input: A string containing valid Python source code (single or multi-line).
          Output: An ast.Module object representing the parsed code structure, containing nodes for all top-level statements, expressions, and definitions.

          The function delegates directly to Python's built-in ast.parse() with default parameters. This produces a complete AST suitable for traversal, analysis, or transformation. The resulting Module node contains a body list of statement nodes and type_ignores metadata.

          Edge cases:
          - Syntax errors in source_code raise SyntaxError with line/column information
          - Empty strings parse successfully to an empty Module with body=[]
          - Incomplete or malformed code raises SyntaxError before AST construction
          - Unicode and multi-byte characters are handled transparently by ast.parse()
          - The function does not validate semantic correctness, only syntactic structure
            deps:
              calls:
                - ast.parse
              imports:
                - __future__.annotations
                - ast
                - inspect
                - pathlib.Path
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Using ast.parse() directly provides a standard, well-tested entry point to Python's compiler infrastructure. This approach:
          - Leverages the official Python parser, ensuring compatibility across Python versions
          - Avoids reimplementing parsing logic, reducing maintenance burden and bugs
          - Produces canonical AST nodes that integrate seamlessly with ast module utilities (NodeVisitor, NodeTransformer, etc.)
          - Maintains consistency with Python tooling ecosystem expectations
          - Delegates error handling to the standard library, providing clear SyntaxError messages with location data

        guardrails:
          - DO NOT attempt to catch and suppress SyntaxError silently; callers must handle parse failures explicitly to avoid masking malformed input
          - DO NOT modify or normalize source_code before parsing; pass it as-is to preserve original line/column information in error messages
          - DO NOT assume the AST is semantically valid; ast.parse() only validates syntax, not name resolution, type correctness, or runtime behavior
          - DO NOT use mode parameter variations without explicit caller intent; default 'exec' mode is appropriate for module-level code analysis

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return ast.parse(source_code)


def _get_indent(node: ast.AST) -> str:
    """
    ---agentspec
    what: |
      Extracts the indentation level of an AST node and returns it as a string of spaces.

      Takes an ast.AST node as input and retrieves its col_offset attribute, which represents
      the column position (0-indexed) where the node begins in its source line. This column
      offset is converted directly to a string of spaces matching that width.

      Returns a string containing only space characters, with length equal to the node's
      col_offset. For nodes at the start of a line (col_offset=0), returns an empty string.
      For nodes indented 4 spaces, returns '    ' (4 spaces).

      Edge cases:
      - Nodes without col_offset attribute default to 0, returning empty string
      - Does not validate that col_offset is non-negative
      - Does not account for tabs or mixed whitespace in original source
      - Assumes col_offset directly maps to space-based indentation (may not reflect actual source if tabs were used)
        deps:
          calls:
            - getattr
          imports:
            - __future__.annotations
            - ast
            - inspect
            - pathlib.Path
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      This utility function normalizes AST node positioning into a consistent indentation
      representation for code generation or formatting tasks. Using col_offset directly
      provides a simple, deterministic way to preserve relative indentation when reconstructing
      or modifying code from AST nodes.

      The approach trades accuracy for simplicity: it assumes space-based indentation and
      doesn't reconstruct the exact original whitespace. This is acceptable for most code
      generation scenarios where consistent spacing is more important than byte-for-byte
      fidelity to the source.

    guardrails:
      - DO NOT assume col_offset reflects the actual whitespace in the source file; it is a character position count, not a whitespace type indicator. Original source may use tabs.
      - DO NOT use this for round-trip source preservation where exact whitespace must be maintained; use the tokenize module or source lines directly instead.
      - DO NOT rely on this for indentation validation; col_offset can be any non-negative integer and doesn't guarantee valid Python indentation.
      - DO NOT call this on nodes that may not have col_offset defined without explicit error handling, as the getattr fallback silently masks missing position information.

        changelog:
          - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
        ---/agentspec
    """
    # For a function/class definition, we need to determine its indent level
    # This is a simplified version; the real implementation would calculate
    # based on the source file content
    col_offset = getattr(node, 'col_offset', 0)
    return ' ' * col_offset
