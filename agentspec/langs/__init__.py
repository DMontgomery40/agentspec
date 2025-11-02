"""
agentspec.langs
------------------
Language adapter registry and protocol for multi-language agentspec support.

Provides a pluggable architecture for adding support for new languages (Python, JavaScript, etc.)
without modifying core processing logic.

---agentspec
what: |
  Registry-based language adapter system enabling agentspec to support multiple languages.
  
  The module maintains a global registry of LanguageAdapter implementations, keyed by
  file extension. It provides two main APIs:
  - LanguageRegistry.get_by_extension(ext): Get adapter for a file extension
  - LanguageRegistry.get_by_path(path): Get adapter for a file path
  
  All adapters implement the LanguageAdapter protocol, which defines how to:
  - Discover source files of a language
  - Parse source files into AST-like structures
  - Extract and insert docstrings
  - Gather metadata (function calls, imports, etc.)
  - Validate syntax

deps:
  calls:
    - inspect, importlib
  called_by:
    - agentspec.collect
    - agentspec.extract
    - agentspec.lint
    - agentspec.generate
    - agentspec.insert_metadata
    - agentspec.cli

why: |
  A registry pattern allows core modules to dispatch language-specific behavior without
  hard-coding language logic. This enables:
  1. Adding new languages without modifying existing code
  2. Testing language adapters independently
  3. Graceful fallback if a language adapter is not installed
  4. Clear separation of concerns between language-agnostic and language-specific code
  
  Using file extensions as the registry key provides fast O(1) lookups and aligns with
  how developers naturally identify source files.

guardrails:
  - DO NOT register the same extension twice without unregistering the old adapter first
  - DO NOT modify the registry after adapters are in use; thread safety is not guaranteed
  - ALWAYS implement the LanguageAdapter protocol completely for any new language

changelog:
  - "2025-10-31: Initial implementation of language adapter architecture"
---/agentspec
"""

from __future__ import annotations
from typing import Dict, Optional, Set, Protocol
from pathlib import Path


class LanguageAdapter(Protocol):
    """
    Protocol defining the interface for language-specific adapters.
    
    Any language adapter must implement all methods and properties defined here.
    """

    @property
    def file_extensions(self) -> Set[str]:
        """
        ---agentspec
        what: |
          Returns a set of file extensions that this language adapter is responsible for processing and analyzing. Each extension is a string prefixed with a dot (e.g., '.py', '.pyi', '.js'). The method enables the adapter registry to route files to the correct language-specific handler based on their file extension. The returned set is immutable after retrieval and represents all extensions this adapter claims ownership over. Extensions are lowercase and include the leading dot character. An adapter may handle multiple related extensions (e.g., a Python adapter handling both '.py' and '.pyi' files).
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          File extension-based routing is the primary mechanism for dispatching source files to language-specific adapters. By centralizing extension declarations in this method, the adapter registry can build a comprehensive mapping without requiring adapters to register themselves imperatively. This approach decouples adapter discovery from adapter instantiation and allows the system to validate extension conflicts or overlaps at initialization time. Returning a set (rather than a list or tuple) emphasizes that order is irrelevant and that extensions are unique within an adapter.

        guardrails:
          - DO NOT return extensions without the leading dot character, as this breaks downstream file matching logic that expects normalized '.ext' format
          - DO NOT return uppercase extensions; maintain lowercase convention for case-insensitive file system compatibility
          - DO NOT return an empty set unless the adapter genuinely handles no files; this indicates a misconfigured or incomplete adapter
          - DO NOT mutate or return a mutable reference that callers could modify; return a defensive copy or immutable collection to prevent registry corruption
          - DO NOT include extensions for file types this adapter cannot actually parse or analyze; only declare extensions for which language-specific logic exists

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...

    def discover_files(self, target: Path) -> list[Path]:
        """
        ---agentspec
        what: |
          Discovers all source files within a target directory or returns a single file if the target is a file path.

          Behavior:
          - If target is a file: returns a list containing only that file path
          - If target is a directory: recursively traverses and collects all source files matching language-specific patterns
          - Respects language-specific ignore patterns (e.g., __pycache__, node_modules, .git, build artifacts)
          - Respects common exclusion directories across all languages (e.g., .venv, venv, dist, build)
          - Returns results as a list of Path objects for consistent downstream processing

          Inputs:
          - target: Path object pointing to either a file or directory

          Outputs:
          - list[Path]: ordered collection of discovered source files

          Edge cases:
          - Empty directories return empty list
          - Symlinks are followed based on Path.rglob behavior
          - Non-existent paths may raise FileNotFoundError or return empty list depending on implementation
          - Deeply nested directories are fully traversed
          - Files with no extension or unknown extensions are excluded
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method provides a unified entry point for file discovery across multiple language contexts. By centralizing discovery logic, we ensure consistent filtering behavior and avoid duplicating ignore patterns across language-specific implementations. The method abstracts away filesystem traversal complexity from callers, allowing them to focus on processing discovered files rather than path manipulation.

          Returning Path objects (rather than strings) provides type safety and enables callers to use Path methods for further manipulation. Supporting both file and directory inputs increases flexibility for different usage patterns (single file analysis vs. batch directory processing).

        guardrails:
          - DO NOT include hidden files (dotfiles) unless explicitly part of language source conventions, as they typically represent configuration or metadata rather than source code
          - DO NOT follow symlinks that create cycles, as this could cause infinite traversal or performance degradation
          - DO NOT return duplicate paths if the same file is reachable through multiple symlink paths
          - DO NOT raise exceptions for permission-denied directories; instead skip them and continue discovery to maximize coverage
          - DO NOT include generated or compiled artifacts (*.pyc, *.class, *.o, etc.) as these are not source files
          - DO NOT traverse into version control directories (.git, .hg, .svn) as they contain metadata, not source code

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...

    def extract_docstring(self, filepath: Path, lineno: int) -> Optional[str]:
        """
        ---agentspec
        what: |
          Extracts the raw docstring from a function or class definition at a specified line number in a given file.

          Inputs:
            - filepath: Path object pointing to a Python source file
            - lineno: Integer line number (1-indexed) where the function/class definition begins

          Outputs:
            - Returns the complete docstring as a string if present, including any embedded agentspec YAML blocks
            - Returns None if no docstring exists at the specified location

          Behavior:
            - Parses the Python file at filepath to locate the AST node at lineno
            - Retrieves the docstring from that node using ast.get_docstring() or equivalent introspection
            - Preserves all formatting, indentation, and special blocks (including agentspec YAML) in raw form
            - Handles edge cases: missing files, invalid line numbers, non-function/class definitions, nodes without docstrings

          Edge cases:
            - lineno points to a line that is not a function or class definition → returns None
            - lineno is out of bounds for the file → returns None or raises appropriate error
            - File cannot be parsed as valid Python → propagates parse error
            - Docstring uses different quote styles (single, double, triple) → all preserved as-is
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method serves as the core extraction point for the agentspec documentation pipeline. By returning raw docstrings with embedded YAML blocks intact, it allows downstream processors to parse and validate agentspec blocks without losing formatting context. This design decouples extraction from interpretation, enabling flexible post-processing and validation workflows. Returning None for missing docstrings provides a clear signal for filtering and error handling rather than raising exceptions, improving robustness in batch processing scenarios.

        guardrails:
          - DO NOT modify or normalize the docstring content; preserve exact formatting and whitespace to maintain agentspec block integrity
          - DO NOT attempt to parse or validate YAML within this method; that responsibility belongs to downstream processors
          - DO NOT assume lineno is 0-indexed; clarify and document the indexing convention to prevent off-by-one errors
          - DO NOT silently ignore parse errors on malformed Python files; propagate them to allow callers to handle invalid source gracefully
          - DO NOT cache results without invalidating on file modification; ensure freshness for development workflows

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...

    def insert_docstring(self, filepath: Path, lineno: int, docstring: str) -> None:
        """
        ---agentspec
        what: |
          Inserts or replaces a docstring for a function or class at a specified line number in a given file.

          Inputs:
            - filepath: Path object pointing to the target source file
            - lineno: Integer line number where the function/class definition begins (1-indexed)
            - docstring: String containing the complete docstring to insert (should include quotes and formatting)

          Outputs:
            - None (modifies file in-place)

          Behavior:
            - Locates the function or class definition at the specified line number
            - Determines the appropriate indentation level based on the definition's context
            - Inserts the docstring immediately after the function/class signature, or replaces an existing docstring
            - Preserves surrounding code structure and indentation
            - Handles language-specific docstring conventions (e.g., Python triple quotes, proper placement after def/class keyword)

          Edge cases:
            - Function/class already has a docstring: replaces the existing one while maintaining indentation
            - Nested functions/classes: correctly determines indentation relative to parent scope
            - Multi-line function signatures: correctly identifies where docstring should be inserted
            - Files with mixed indentation or non-standard formatting: adapts to existing style
            - Invalid line numbers: behavior depends on implementation (may raise error or handle gracefully)
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method abstracts the language-specific complexity of docstring insertion, allowing callers to work with a uniform interface regardless of the target language. By accepting a line number, it enables precise targeting of specific definitions without requiring the caller to parse the file. The method handles indentation automatically, reducing boilerplate and ensuring consistency with the file's existing style. This is essential for automated documentation generation tools that need to inject docstrings into source files while preserving code integrity.

        guardrails:
          - DO NOT assume the docstring parameter is already properly formatted with language-specific quotes or delimiters; validate or document whether the caller is responsible for this
          - DO NOT modify file permissions or ownership; preserve the original file metadata
          - DO NOT insert docstrings at incorrect indentation levels, as this will break syntax and code structure
          - DO NOT overwrite or corrupt existing code beyond the target docstring; use precise line-based insertion
          - DO NOT assume line numbers are 0-indexed; clarify and enforce 1-indexed convention to match editor conventions
          - DO NOT handle files that cannot be read or written without raising appropriate exceptions; do not silently fail

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...

    def gather_metadata(self, filepath: Path, function_name: str) -> Dict:
        """
        ---agentspec
        what: |
          Extracts and aggregates metadata from a Python source file for a specified function.

          Takes a filepath and function name as inputs and returns a dictionary containing:
          - 'calls': List of functions/methods invoked within the target function
          - 'imports': All import statements present in the file (both absolute and relative)
          - 'called_by': Functions or methods that call the target function
          - 'signature': Function signature including parameters and return type annotation if present
          - 'docstring': Extracted docstring content if available
          - 'decorators': Any decorators applied to the function
          - 'line_range': Start and end line numbers of the function definition

          Handles edge cases including:
          - Functions with no docstrings (returns None or empty string)
          - Nested function definitions (captures scope appropriately)
          - Dynamic imports and conditional imports (includes all discovered imports)
          - Methods within classes (distinguishes between instance, class, and static methods)
          - Functions with no callers or callees (returns empty lists)
          - Malformed or incomplete function definitions (graceful degradation)
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method serves as a central extraction point for static analysis of Python code.
          It enables downstream analysis tools to understand function dependencies, call graphs,
          and documentation without requiring full AST traversal at call sites. By consolidating
          metadata extraction into a single method, we reduce code duplication and provide a
          consistent interface for analysis operations. The dictionary return format allows
          flexible consumption by different analysis stages without tight coupling.

        guardrails:
          - DO NOT attempt to execute the code or resolve runtime imports; this is static analysis only
          - DO NOT modify the source file during metadata extraction; this must be read-only
          - DO NOT assume function names are globally unique; include class context in results when applicable
          - DO NOT include transitive call chains; only direct calls should be listed in 'calls' and 'called_by'
          - DO NOT resolve relative imports to absolute paths; preserve import statements as written in source
          - DO NOT fail silently on parse errors; raise or log exceptions for malformed Python syntax

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...

    def validate_syntax(self, filepath: Path) -> bool:
        """
        ---agentspec
        what: |
          Validates whether a file has syntactically correct code after modifications.

          Accepts a Path object pointing to a file on disk. Returns True if the file's syntax is valid and parseable by the target language's parser. Returns False or raises an exception if syntax is invalid.

          The method should perform language-specific syntax checking appropriate to the file type (determined by extension or other metadata). It validates the complete file contents, not partial snippets. Edge cases include: empty files (typically valid), files with encoding declarations, files with syntax errors at various positions (start, middle, end), and files with mixed line endings.

          Output is a boolean True for valid syntax. Invalid syntax should either return False or raise a descriptive exception indicating the nature of the syntax error and its location.
        what: |
          Rationale for this validation step is to catch errors introduced during code generation or modification before the file is used or committed. This prevents downstream failures and provides immediate feedback. The boolean return type allows for graceful degradation in some contexts, while exception raising allows strict validation in others. Language-specific implementation is necessary because syntax rules vary significantly across Python, JavaScript, Go, etc.
        guardrails:
          - DO NOT assume file encoding; respect encoding declarations or use safe fallbacks to avoid UnicodeDecodeError
          - DO NOT modify the file during validation; this is a read-only check operation
          - DO NOT catch all exceptions silently; distinguish between syntax errors and I/O errors (file not found, permission denied)
          - DO NOT validate only partial syntax; ensure the entire file is checked for consistency
          - DO NOT skip validation for empty files without explicit language-specific rules; some languages treat empty files as valid, others do not
        ---/agentspec
        I don't have context of a previous YAML agentspec block you were generating. To continue accurately, I would need you to provide:

        1. The existing YAML agentspec content you've already created
        2. Which sections remain incomplete
        3. Any specific requirements or constraints for the remaining sections

        Please share the partial agentspec block, and I'll complete it with narrative sections (what/why/guardrails) while avoiding deps and changelog sections, then close with `
            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec`.
        I don't have context of a previous YAML agentspec block you were generating. To continue accurately, I would need you to provide:

        1. The existing YAML agentspec content you've already created
        2. Which sections remain incomplete
        3. Any specific requirements or constraints for the remaining sections

        Please share the partial agentspec block, and I'll complete it with the narrative sections (what/why/guardrails) while avoiding deps and changelog sections.

            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set

        """
        ...

    def get_comment_delimiters(self) -> tuple[str, str]:
        '''
        ---agentspec
        what: |
          Returns a tuple of two strings representing the opening and closing delimiters for multi-line comments in the target programming language.

          The function retrieves language-specific comment syntax by returning a (start_delimiter, end_delimiter) pair. For example:
          - JavaScript/C-style: ('/*', '*/')
          - Python docstrings: ('"""', '"""')
          - HTML/XML: ('<!--', '-->')
          - Lua: ('--[[', ']]')

          This is used by the language abstraction layer to identify and parse multi-line comment blocks during code analysis and transformation. The delimiters are language-specific and must match the exact syntax recognized by the target language's parser.

          Edge cases:
          - Languages without multi-line comments may return empty strings or raise NotImplementedError
          - Some languages use identical start/end delimiters (Python), others use distinct pairs (JavaScript)
          - Delimiters are case-sensitive and must include any required whitespace or special characters
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method abstracts language-specific comment syntax behind a uniform interface, allowing the agentspec system to work with multiple programming languages without hardcoding syntax rules throughout the codebase. By centralizing delimiter definitions in the language module, changes to language support only require updates in one location. The tuple return type provides a simple, immutable contract that is easy to unpack and use in string operations.

        guardrails:
          - DO NOT return delimiters that don't match the actual language syntax, as this will cause comment parsing to fail silently or produce incorrect results
          - DO NOT assume delimiters are symmetric; some languages use different start/end markers and both must be returned in the correct order
          - DO NOT include escape characters or regex patterns; return literal delimiter strings only
          - DO NOT return None or single-element tuples; always return exactly a 2-tuple of strings

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        '''
        ...

    def parse(self, source_code: str) -> object:
        """
        ---agentspec
        what: |
          Parses source code strings into language-specific Abstract Syntax Tree (AST) or tree structures.

          Input: A string containing source code in the target language (e.g., Python, JavaScript, Go).
          Output: A language-agnostic tree object representing the hierarchical structure of the code, with nodes for statements, expressions, declarations, and other syntactic elements.

          The method serves as the entry point for code analysis workflows. It delegates to language-specific parsers (e.g., ast module for Python, tree-sitter for compiled languages) and normalizes their output into a common traversable format.

          Edge cases:
          - Malformed or syntactically invalid source code raises ParseError with line/column information
          - Empty strings return an empty tree or minimal valid AST
          - Unicode and multi-byte characters are preserved and correctly positioned in error reporting
          - Very large source files (>10MB) may trigger memory or timeout constraints depending on parser implementation
          - Mixed line endings (CRLF/LF) are normalized before parsing
            deps:
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          Abstracting parse logic into a single method enables consistent AST access across multiple languages without caller code duplication. By returning a normalized tree structure, downstream adapter methods (traversal, transformation, analysis) can operate uniformly regardless of the underlying parser library.

          This design supports incremental language support: new languages can be added by implementing language-specific parse logic without modifying consumer code. The tree abstraction also enables caching and memoization of parse results for repeated analysis on the same source.

        guardrails:
          - DO NOT assume the returned tree is mutable; some parser backends return immutable structures. Callers should not modify tree nodes in place.
          - DO NOT rely on parser-specific node types leaking through the interface; always use the adapter's tree traversal methods to access node properties.
          - DO NOT pass untrusted source code without resource limits; parsing can be computationally expensive and may be exploited for denial-of-service attacks.
          - DO NOT assume parse errors include full source context; truncate or summarize large files in error messages to avoid memory bloat.
          - DO NOT parse binary or non-text data; validate input is valid UTF-8 or declared encoding before calling parse.

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        ...


class LanguageRegistry:
    """
    Global registry mapping file extensions to language adapters.
    """

    _adapters: Dict[str, LanguageAdapter] = {}

    @classmethod
    def register(cls, adapter: LanguageAdapter) -> None:
        """
        ---agentspec
        what: |
          Registers a LanguageAdapter instance for all file extensions it declares support for.

          Takes a LanguageAdapter object and iterates through its `file_extensions` attribute,
          storing a reference to the adapter in the class-level `_adapters` dictionary keyed by
          each extension (normalized to lowercase). This enables the registry to map file extensions
          to their corresponding language adapters for later lookup and instantiation.

          Inputs:
            - adapter: LanguageAdapter instance with a `file_extensions` iterable of strings

          Outputs:
            - None (mutates class-level `_adapters` dict as side effect)

          Edge cases:
            - Empty file_extensions: adapter registered but unreachable via extension lookup
            - Duplicate extensions across adapters: later registration overwrites earlier one
            - Mixed case extensions: normalized to lowercase for case-insensitive matching
            - None or invalid adapter: will raise AttributeError when accessing file_extensions
            deps:
              calls:
                - ext.lower
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          Centralizes adapter registration logic into a single class method to maintain a
          consistent registry pattern. Normalizing extensions to lowercase ensures predictable
          lookups regardless of how extensions are specified. Using a dictionary keyed by
          extension provides O(1) lookup performance for the common case of "find adapter for
          this file extension." Class-level storage allows all instances to share the same
          registry without duplication.

        guardrails:
          - DO NOT assume adapter.file_extensions is non-empty; validate before registration if
            empty adapters should be rejected
          - DO NOT allow unvalidated adapter objects; verify adapter implements LanguageAdapter
            protocol before storing to prevent runtime errors during adapter usage
          - DO NOT silently overwrite existing adapters for an extension; log or raise on
            collision to catch configuration errors early
          - DO NOT mutate the adapter object itself; only store references in the registry

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        for ext in adapter.file_extensions:
            cls._adapters[ext.lower()] = adapter

    @classmethod
    def unregister(cls, extension: str) -> None:
        """
        ---agentspec
        what: |
          Unregisters a language adapter from the internal adapter registry by its file extension.

          Takes a single extension string parameter (e.g., "py", "js", "ts") and removes the corresponding
          adapter from the class-level _adapters dictionary. The extension lookup is case-insensitive
          (converted to lowercase before removal). If the extension does not exist in the registry,
          the operation silently succeeds (no exception raised) due to the dict.pop() default None behavior.

          Returns None. This is a class method that modifies shared state across all instances.

          Typical use case: removing support for a language adapter at runtime, cleaning up after
          dynamic registration, or disabling specific language handlers without restarting the application.

          Edge cases:
          - Extension not found: silently ignored (pop with default None)
          - Empty string extension: will be lowercased to empty string and removed if it exists
          - None passed as extension: will raise AttributeError (str method .lower() called on None)
          - Whitespace in extension: preserved as-is before lowercasing (e.g., " py " becomes " py ")
            deps:
              calls:
                - _adapters.pop
                - extension.lower
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          The silent failure approach (pop with default) prevents exceptions when unregistering
          non-existent adapters, making the API forgiving and idempotent. Case-insensitive lookup
          ensures consistency with typical file extension handling across operating systems.

          Using a class method allows centralized adapter lifecycle management without requiring
          instance creation. The _adapters dictionary is the single source of truth for registered
          adapters, so direct mutation is the appropriate mechanism.

          Tradeoff: silent failure means caller cannot distinguish between successful removal and
          attempted removal of non-existent adapter. This is acceptable for cleanup operations but
          may hide bugs if strict validation is needed elsewhere.

        guardrails:
          - DO NOT pass None as extension—will raise AttributeError; validate input is string before calling
          - DO NOT rely on return value for confirmation of removal—always returns None; check registry state separately if verification needed
          - DO NOT assume case sensitivity—extension is always lowercased, so "PY" and "py" target the same adapter
          - DO NOT use this to remove adapters during active adapter lookups in other threads without synchronization—_adapters is not thread-safe

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        cls._adapters.pop(extension.lower(), None)

    @classmethod
    def get_by_extension(cls, extension: str) -> Optional[LanguageAdapter]:
        """
        ---agentspec
        what: |
          Retrieves a LanguageAdapter instance for a given file extension by performing a case-insensitive lookup in the internal adapter registry. Accepts a file extension string (e.g., '.py', '.js', '.ts') and returns the corresponding LanguageAdapter if registered, or None if no adapter exists for that extension. The lookup normalizes the input extension to lowercase before querying the _adapters dictionary to ensure consistent matching regardless of input case variation (e.g., '.PY', '.Py', '.py' all resolve identically). This is a class method that accesses the shared _adapters registry maintained across all instances.
            deps:
              calls:
                - _adapters.get
                - extension.lower
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          File extensions are conventionally case-insensitive in most filesystems and development workflows, but Python string comparisons are case-sensitive by default. Normalizing to lowercase ensures robust matching across different naming conventions users might employ. Using a class method with a shared registry provides efficient O(1) lookup performance and centralizes adapter management. Returning Optional[LanguageAdapter] allows graceful handling of unsupported file types without raising exceptions, enabling caller code to implement fallback logic or user-friendly error messages.

        guardrails:
          - DO NOT assume the extension parameter includes a leading dot—validate or document whether callers must provide '.py' vs 'py' format
          - DO NOT modify the _adapters registry during lookup; this method must be read-only to maintain thread-safety and prevent accidental state corruption
          - DO NOT return a default adapter if the extension is not found; returning None forces explicit handling and prevents silent mismatches
          - DO NOT perform expensive operations (file I/O, network calls) during lookup; this must remain a simple dictionary access for performance

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return cls._adapters.get(extension.lower())

    @classmethod
    def get_by_path(cls, filepath: Path | str) -> Optional[LanguageAdapter]:
        """
        ---agentspec
        what: |
          Retrieves a LanguageAdapter instance for a given file path by extracting and normalizing its file extension.

          **Inputs:**
          - filepath: Path | str - A file path as either a pathlib.Path object or string (e.g., "/path/to/file.py", "script.js")

          **Outputs:**
          - Optional[LanguageAdapter] - Returns a LanguageAdapter matching the file extension, or None if no adapter exists for that extension

          **Behavior:**
          1. Normalizes string input to Path object if needed
          2. Extracts file extension using Path.suffix (includes leading dot, e.g., ".py")
          3. Converts extension to lowercase for case-insensitive matching
          4. Delegates to get_by_extension() for adapter lookup

          **Edge cases:**
          - Files with no extension (suffix is empty string) - returns None via get_by_extension
          - Mixed-case extensions (e.g., ".PY", ".Js") - normalized to lowercase before lookup
          - Compound extensions (e.g., ".tar.gz") - only rightmost extension is used (Path.suffix behavior)
          - Non-existent file paths - Path object creation succeeds; adapter lookup determines result
            deps:
              calls:
                - Path
                - cls.get_by_extension
                - isinstance
                - suffix.lower
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          This method provides a convenient file-path-based entry point to the adapter registry, abstracting away extension extraction logic. By normalizing to lowercase, it ensures consistent matching regardless of filesystem or user input casing conventions. Delegating to get_by_extension() maintains single responsibility and reuses existing lookup logic. The Optional return type allows graceful handling of unsupported file types without raising exceptions.

        guardrails:
          - DO NOT assume the file exists on disk - Path objects are created without validation, only the extension string matters
          - DO NOT use Path.name or other path components for adapter selection - only the file extension suffix is relevant
          - DO NOT perform case-sensitive extension matching - always normalize to lowercase to handle cross-platform and user input variations
          - DO NOT handle compound extensions specially (e.g., treating ".tar.gz" as a unit) - rely on Path.suffix which returns only the final component

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)
        ext = filepath.suffix.lower()
        return cls.get_by_extension(ext)

    @classmethod
    def supported_extensions(cls) -> Set[str]:
        """
        ---agentspec
        what: |
          Returns a set of all file extensions currently registered in the language adapter registry.

          This is a class method that provides read-only access to the keys of the internal `_adapters` dictionary,
          which maps file extensions (strings like ".py", ".js", ".ts") to their corresponding language adapter instances.

          The method converts the dictionary keys to a set to provide a clean, deduplicated collection of supported extensions.
          Extensions are stored without normalization, so the exact format depends on how adapters were registered.

          Returns an empty set if no adapters have been registered yet. The returned set is a shallow copy,
          so modifications to it do not affect the internal registry.

          Typical use cases: checking capability before processing a file, displaying supported formats to users,
          or validating file extensions against the registry.
            deps:
              calls:
                - _adapters.keys
                - set
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          Exposing the adapter keys as a set provides a simple, immutable view of supported extensions without
          revealing the internal adapter implementation details or allowing callers to modify the registry.

          Using a set (rather than returning keys() directly) provides a standard collection type that is
          hashable, iterable, and supports set operations (union, intersection, etc.) that callers may need.

          This class method pattern allows querying capabilities without instantiating the class, following
          the registry pattern where the class itself acts as a factory and capability provider.

        guardrails:
          - DO NOT modify the returned set expecting changes to persist in the registry—the set is a copy
          - DO NOT assume extension format is normalized (e.g., ".py" vs "py")—use exact values from the registry
          - DO NOT call this method in tight loops without caching if performance is critical, as it reconstructs the set each call
          - DO NOT rely on extension ordering—sets are unordered; sort if deterministic output is needed

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return set(cls._adapters.keys())

    @classmethod
    def list_adapters(cls) -> Dict[str, LanguageAdapter]:
        """
        ---agentspec
        what: |
          Returns a shallow copy of all currently registered language adapters as a dictionary.

          The method accesses the class-level `_adapters` dictionary (a private registry mapping language identifiers to LanguageAdapter instances) and returns a new dictionary containing all registered adapters. This ensures callers receive a snapshot of the adapter registry at call time without holding a reference to the internal mutable state.

          Inputs: None (class method, no instance parameters required)

          Outputs: Dict[str, LanguageAdapter] where keys are language identifiers (strings) and values are LanguageAdapter instances

          Edge cases:
          - If no adapters have been registered, returns an empty dictionary
          - Modifications to the returned dictionary do not affect the internal `_adapters` registry (shallow copy isolation)
          - Adapter instances themselves remain mutable references; modifications to adapter state will be reflected across all copies
            deps:
              calls:
                - dict
              imports:
                - __future__.annotations
                - agentspec.langs.javascript_adapter.JavaScriptAdapter
                - agentspec.langs.python_adapter.PythonAdapter
                - pathlib.Path
                - typing.Dict
                - typing.Optional
                - typing.Protocol
                - typing.Set


        why: |
          Returning a copy rather than the internal registry directly prevents external code from accidentally mutating the adapter registry through direct dictionary manipulation (e.g., adding, removing, or replacing adapters). This provides a controlled public interface for introspection while maintaining encapsulation of the internal registration mechanism.

          Using a class method allows access to the shared adapter registry without requiring an instance, supporting a singleton-like pattern for language adapter management across the application.

        guardrails:
          - DO NOT return the internal `_adapters` dictionary directly; always return a copy to prevent external mutation of the registry
          - DO NOT assume the registry is non-empty; callers must handle empty dictionary responses gracefully
          - DO NOT modify adapter state through this method; it is read-only introspection only

            changelog:
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return dict(cls._adapters)


# Import and register the Python adapter
from agentspec.langs.python_adapter import PythonAdapter

_python_adapter = PythonAdapter()
LanguageRegistry.register(_python_adapter)

# Import and register the JavaScript adapter
from agentspec.langs.javascript_adapter import JavaScriptAdapter

_javascript_adapter = JavaScriptAdapter()
LanguageRegistry.register(_javascript_adapter)

__all__ = [
    'LanguageAdapter',
    'LanguageRegistry',
    'PythonAdapter',
    'JavaScriptAdapter',
]
