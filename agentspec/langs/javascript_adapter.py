"""
agentspec.langs.javascript_adapter
----------------------------------
Language adapter implementation for JavaScript/JSX source files.

Provides docstring extraction/insertion, metadata gathering, and syntax validation
for JavaScript using tree-sitter parser.

---agentspec
what: |
  Adapts JavaScript-specific functionality into the LanguageAdapter protocol.
  
  Uses tree-sitter library with precompiled JavaScript grammar to:
  - Parse .js, .mjs, .jsx, .ts, .tsx files (future)
  - Extract JSDoc comments as docstrings
  - Insert or update JSDoc blocks
  - Gather metadata (function calls, imports) via tree-sitter queries
  - Validate syntax by re-parsing
  
  Agentspec blocks in JavaScript live inside JSDoc comments:
  ```javascript
  /**
   * Brief description
   * 
   * ---agentspec
   * what: |
   *   Detailed explanation
   * deps:
   *   calls: [...]
   * ---/agentspec
   */
  function myFunction() { }
  ```

deps:
  calls:
    - tree_sitter (Parser, Language)
    - tree_sitter_languages.get_parser
    - pathlib, re, logging.getLogger
  called_by:
    - agentspec.langs.__init__ (registration)
    - agentspec.collect
    - agentspec.extract
    - agentspec.lint
    - agentspec.generate

why: |
  Tree-sitter provides a fast, incremental parser with deterministic AST output.
  Unlike regex or manual parsing, tree-sitter correctly handles:
  - Comments as first-class AST nodes
  - Complex nesting (JSX, template literals)
  - Async/await, arrow functions, modern ES syntax
  - Error recovery for partial/invalid code
  
  Precompiled grammars from tree_sitter_languages avoid per-user compilation
  and ensure portability across platforms.
  
  Maintaining parity with Python agentspec format (YAML fences) allows
  the same downstream extraction logic to work for both languages.

guardrails:
  - DO NOT parse JavaScript without tree-sitter; regex-based parsing is brittle
  - DO NOT assume comments are line-level; use tree-sitter's comment node handling
  - DO NOT insert docstrings without re-parsing for syntax validation
  - ALWAYS preserve JSDoc formatting with proper indentation and * prefix

changelog:
  - "2025-10-31: Add explicit logging and version guidance for tree-sitter initialization"
  - "2025-10-31: Initial tree-sitter based JavaScript adapter implementation"
---/agentspec
"""

from __future__ import annotations
from typing import Set, Dict, Optional, List, Any
from pathlib import Path
import logging
import re


logger = logging.getLogger(__name__)


class JavaScriptAdapter:
    """
    Language adapter for JavaScript (.js, .mjs, .jsx, .ts, .tsx) files.

    Uses tree-sitter parser for reliable syntax analysis and comment extraction.
    Supports ES6+ syntax including async/await, arrow functions, classes, etc.
    """

    def __init__(self):
        """
        ---agentspec
        what: |
          Initializes a JavaScript language adapter with tree-sitter parsers for three JavaScript-family languages: JavaScript, TypeScript, and TSX. The initializer attempts to import the optional tree-sitter-languages dependency and instantiate language-specific parsers for each supported file type. On successful initialization, the default parser is set to the JavaScript parser and an internal flag (_tree_sitter_available) is set to True, enabling downstream parsing operations. If the tree-sitter-languages package is not installed, an ImportError is caught, logged at error level with installation instructions, and the method returns early without raising an exception, leaving all parser attributes as None. If parser instantiation fails after successful import, an exception is raised after logging diagnostic information. Special handling detects version mismatches between tree-sitter and tree-sitter-languages by inspecting exception messages for "takes exactly" and "argument" keywords, providing targeted remediation guidance to users.
            deps:
              calls:
                - logger.debug
                - logger.error
                - logger.exception
                - str
                - tree_sitter_languages.get_parser
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter is an optional dependency because not all users require JavaScript/TypeScript parsing support, keeping the base installation lightweight. Graceful degradation on missing dependencies allows the broader agentspec package to function for other languages while clearly communicating to users what is needed for JavaScript support. The three separate parser instances (js_parser, ts_parser, tsx_parser) enable language-specific parsing strategies and future extensibility for language-variant-specific logic. Defaulting to the JavaScript parser provides a sensible fallback for ambiguous cases. Version mismatch detection with specific error messaging reduces user friction during dependency installation and configuration, as tree-sitter has strict version coupling requirements.

        guardrails:
          - DO NOT silently fail if tree-sitter-languages is installed but parser instantiation fails; raise the exception after logging to ensure users are aware of configuration problems rather than experiencing silent degradation downstream.
          - DO NOT assume tree-sitter-languages is available globally; always attempt import and handle ImportError gracefully to support optional dependency patterns.
          - DO NOT initialize self.parser to a non-None value if any parser instantiation fails; leave it as None to signal to calling code that parsing is unavailable rather than risking use of a partially-initialized adapter.
          - DO NOT catch and suppress the exception from parser instantiation without re-raising; defensive logging is appropriate but the error must propagate so installation/configuration issues are surfaced to the user.

            changelog:
              - "- 2025-11-04: fix: slice UTF-8 bytes then decode to avoid multibyte misalignment"
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        self.js_parser = None
        self.ts_parser = None
        self.tsx_parser = None
        self.parser = None  # Will be set based on file extension
        self._tree_sitter_available = False

        try:
            import tree_sitter_languages  # type: ignore
        except ImportError as exc:
            logger.error(
                "JavaScript support requires the optional 'tree-sitter-languages' dependency. "
                "Install with `pip install agentspec[javascript]`."
            )
            logger.debug("Missing tree-sitter dependency", exc_info=True)
            return

        try:
            self.js_parser = tree_sitter_languages.get_parser('javascript')
            self.ts_parser = tree_sitter_languages.get_parser('typescript')
            self.tsx_parser = tree_sitter_languages.get_parser('tsx')
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.exception("Failed to initialize tree-sitter parser for JavaScript/TypeScript/TSX")
            if "takes exactly" in str(exc) and "argument" in str(exc):
                logger.error(
                    "Detected a tree-sitter version mismatch. "
                    "Agentspec pins tree-sitter==0.20.1; run `pip install 'tree-sitter==0.20.1'`."
                )
            raise
        else:
            # Default to JavaScript parser
            self.parser = self.js_parser
            self._tree_sitter_available = True

    @property
    def file_extensions(self) -> Set[str]:
        """
        ---agentspec
        what: |
          Returns a set of file extensions that the JavaScript/TypeScript adapter is responsible for handling.

          The method returns exactly five extensions as strings: '.js' (standard JavaScript), '.mjs' (ES modules),
          '.jsx' (React/JSX syntax), '.ts' (TypeScript), and '.tsx' (TypeScript with JSX). Each extension is
          prefixed with a dot and stored in a set data structure for O(1) lookup performance.

          This is a stateless accessor method with no parameters. It always returns the same immutable set
          of extensions regardless of adapter state or configuration. The returned set can be used by the
          adapter registry or file routing logic to determine which files should be processed by this adapter.
            deps:
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Using a set provides efficient membership testing when routing files to appropriate language adapters.
          Returning a set (rather than a list or tuple) makes the intent clear that order is irrelevant and
          duplicates are impossible. This method centralizes the definition of supported extensions in one place,
          making it easy to audit which file types are handled and reducing the risk of inconsistencies across
          the codebase. The method is simple and pure, with no side effects, making it safe to call repeatedly.

        guardrails:
          - DO NOT modify the returned set in-place; callers should treat it as immutable to prevent unexpected
            behavior in other parts of the adapter system that may rely on the same set reference.
          - DO NOT add or remove extensions without updating documentation and considering downstream impact on
            file routing logic and language detection heuristics.
          - DO NOT return None or an empty set; this method must always return the complete set of supported
            extensions to avoid silent failures in file routing.

            changelog:
              - "- 2025-11-04: fix: use byte-slice+decode for import text extraction"
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return {'.js', '.mjs', '.jsx', '.ts', '.tsx'}

    def discover_files(self, target: Path) -> List[Path]:
        """
        ---agentspec
        what: |
          Discovers all JavaScript/TypeScript files within a target directory or validates a single file.

          Accepts either a string path or Path object as input. If target is a file with a supported extension (.js, .mjs, .jsx, .ts, .tsx), returns a list containing that single resolved file path. If target is a directory, recursively globs for all files matching supported extensions, filtering out paths containing '.git' directory component, and returns a sorted list of resolved absolute paths. If target is neither file nor directory, returns empty list.

          Supported extensions: .js, .mjs, .jsx, .ts, .tsx

          Edge cases:
          - String paths are converted to Path objects for consistent handling
          - Single files are validated against extension whitelist before inclusion
          - Only .git directories are excluded at discovery time; all other exclusions (.venv, node_modules, build, dist, etc.) are deferred to downstream .gitignore-based filtering in collect_source_files
          - Non-existent paths return empty list rather than raising exceptions
          - Results are sorted for deterministic output across runs
          - All returned paths are resolved to absolute paths
            deps:
              calls:
                - Path
                - add_glob
                - files.append
                - files.sort
                - isinstance
                - p.is_file
                - p.resolve
                - target.is_dir
                - target.is_file
                - target.resolve
                - target.rglob
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Minimal pre-filtering at discovery stage keeps this function focused and fast. Deferring comprehensive exclusion logic to .gitignore-based post-filtering (in collect_source_files) provides several benefits: respects project-specific ignore patterns, avoids hardcoding exclusion lists that may become stale, and centralizes exclusion logic in one place. Only .git is excluded here because it is a universal concern that should never contain source files and its presence in path.parts is a reliable indicator. This two-stage approach (minimal discovery + comprehensive filtering) balances performance with flexibility.

        guardrails:
          - DO NOT apply comprehensive exclusion patterns here (node_modules, .venv, build, etc.) because these should be driven by .gitignore configuration, allowing projects to customize what is ignored
          - DO NOT raise exceptions for missing or invalid paths; return empty list instead to allow graceful handling by callers
          - DO NOT skip the .resolve() call; absolute paths prevent ambiguity and path traversal issues in downstream processing
          - DO NOT omit the sort() call; deterministic ordering is essential for reproducible results and testing
          - DO NOT accept file extensions beyond the defined whitelist without explicit code change; this prevents accidental inclusion of non-source files

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if isinstance(target, str):
            target = Path(target)

        files: List[Path] = []

        if target.is_file():
            if target.suffix in self.file_extensions:
                files.append(target.resolve())
            return files

        if not target.is_dir():
            return []

        def add_glob(ext: str):
            """
            ---agentspec
            what: |
              Recursively globs for files matching a given extension pattern within a target directory.

              Inputs:
                - ext (str): File extension pattern to match (e.g., '.js', '.ts'). Pattern is passed directly to rglob().
                - target (Path): Root directory to search from (implicit, from enclosing scope).
                - files (list): Accumulator list to append resolved file paths to (implicit, from enclosing scope).

              Behavior:
                - Uses Path.rglob() to recursively search all subdirectories for files matching the pattern '*{ext}'.
                - Filters out any paths containing '.git' in their path components to exclude version control metadata.
                - Only appends entries that are actual files (not directories) via is_file() check.
                - Resolves each matched file to its absolute path before appending.

              Outputs:
                - Mutates the files list by appending Path objects (absolute, resolved paths).
                - Returns None (side-effect function).

              Edge cases:
                - Symlinks are followed by rglob() by default; resolved paths will point to their targets.
                - Empty extension strings or malformed patterns may yield no matches without error.
                - .git exclusion is path-component based, so directories named '.git' anywhere in the hierarchy are skipped.
                - If target is not readable or does not exist, rglob() will raise an exception.
                deps:
                  calls:
                    - files.append
                    - p.is_file
                    - p.resolve
                    - target.rglob
                  imports:
                    - __future__.annotations
                    - logging
                    - pathlib.Path
                    - re
                    - typing.Any
                    - typing.Dict
                    - typing.List
                    - typing.Optional
                    - typing.Set


            why: |
              This approach balances simplicity with practical filtering needs for JavaScript/TypeScript file collection.

              Rationale:
                - rglob() provides concise recursive traversal without manual stack management.
                - Explicit .git filtering is necessary because .gitignore rules are not automatically applied by Path methods; this ensures build artifacts and dependencies in node_modules (often under .git-adjacent structures) are excluded.
                - is_file() check prevents directories from being added, which would cause downstream processing errors.
                - resolve() ensures consistent absolute paths regardless of relative symlinks or working directory state.

              Tradeoffs:
                - Does not parse .gitignore files, so other ignored patterns (e.g., node_modules, dist/) must be handled elsewhere or require additional filtering logic.
                - .git filtering is coarse-grained (any path component named '.git'); more granular control would require regex or explicit path matching.
                - No caching of glob results; repeated calls with the same ext will re-traverse the filesystem.

            guardrails:
              - DO NOT rely on .gitignore rules being respected; this function only excludes .git directories. Callers must implement additional filtering for build artifacts, dependencies, and other ignored patterns.
              - DO NOT assume the extension pattern is validated; malformed patterns (e.g., missing dot, regex syntax) will be passed to rglob() as-is and may produce unexpected results.
              - DO NOT use this function on very large directory trees without considering performance; rglob() traverses all subdirectories and may be slow on deep hierarchies with many files.
              - DO NOT modify the files list concurrently from other threads; this function mutates a shared accumulator without synchronization.

                changelog:
                  - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
                  - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
                  - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
                  - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
                ---/agentspec
            """
            for p in target.rglob(f'*{ext}'):
                # Only exclude .git (everything else via .gitignore)
                if '.git' in p.parts:
                    continue
                if p.is_file():
                    files.append(p.resolve())

        for ext in ('.js', '.mjs', '.jsx', '.ts', '.tsx'):
            add_glob(ext)

        files.sort()
        return files

    def extract_docstring(self, filepath: Path, lineno: int) -> Optional[str]:
        """
        ---agentspec
        what: |
          Extracts JSDoc comment blocks preceding a function or class declaration at a specified line number in a JavaScript/TypeScript file.

          **Inputs:**
          - filepath: Path object pointing to a JavaScript/TypeScript source file
          - lineno: Integer line number where the target function/class is declared

          **Outputs:**
          - Returns the docstring content as a string (JSDoc text without /** */ delimiters), or None if extraction fails

          **Behavior:**
          1. Returns None immediately if tree-sitter parser is unavailable (graceful degradation)
          2. Attempts to read the source file with UTF-8 encoding
          3. Parses the source code into an abstract syntax tree (AST) using tree-sitter
          4. Delegates to _find_preceding_jsdoc() to locate and extract the JSDoc block that precedes the declaration at lineno
          5. Returns extracted docstring or None on any parsing/IO failure

          **Edge cases:**
          - File not found or unreadable (IOError) → returns None
          - File contains invalid UTF-8 sequences → returns None
          - Parser fails on malformed JavaScript/TypeScript → returns None
          - No JSDoc comment precedes the target declaration → returns None (delegated to _find_preceding_jsdoc)
          - Line number out of bounds or not a function/class → returns None (delegated to _find_preceding_jsdoc)
            deps:
              calls:
                - f.read
                - open
                - parser.parse
                - self._find_preceding_jsdoc
                - source.encode
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This method provides a robust, fault-tolerant interface for extracting documentation from JavaScript source files. By returning None on any error rather than raising exceptions, it allows calling code to gracefully handle missing or unparseable files without try-catch overhead. The tree-sitter dependency check prevents runtime errors in environments where the parser is unavailable. Delegating AST traversal to _find_preceding_jsdoc separates concerns: this method handles I/O and parsing setup, while the helper handles AST navigation logic. This design supports incremental documentation extraction across large codebases where some files may be malformed or inaccessible.

        guardrails:
          - DO NOT assume the file encoding is UTF-8 without attempting to decode; some legacy JavaScript files may use other encodings, but UTF-8 is the modern standard and failures should be caught gracefully
          - DO NOT raise exceptions for file I/O or parse errors; return None to allow batch processing of multiple files without interruption
          - DO NOT modify the source file or tree-sitter parser state; this method must be read-only to avoid side effects
          - DO NOT assume lineno is 1-indexed vs 0-indexed without verifying against the caller's convention; document this contract in the calling code
          - DO NOT attempt to extract docstrings if tree-sitter is unavailable; the early return prevents cascading failures in environments without native parser bindings

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except (IOError, UnicodeDecodeError):
            return None

        try:
            tree = self.parser.parse(source.encode('utf-8'))
        except Exception:
            return None

        # Find function/class at lineno and extract preceding JSDoc
        docstring = self._find_preceding_jsdoc(source, tree, lineno)
        return docstring

    def insert_docstring(self, filepath: Path, lineno: int, docstring: str) -> None:
        """
        ---agentspec
        what: |
          Inserts or replaces a JSDoc documentation block for a JavaScript function or class at a specified line number.

          Inputs:
          - filepath: Path object pointing to the JavaScript source file
          - lineno: 1-indexed line number where the target function/class is declared
          - docstring: Raw documentation text (without JSDoc formatting)

          Outputs:
          - Modifies the file in-place with formatted JSDoc block
          - JSDoc block is properly indented to match the target function/class indentation
          - Each line is prefixed with " * " and wrapped with /** and */ delimiters

          Behavior:
          - Reads source file with UTF-8 encoding; raises ValueError if file cannot be read or line is out of range
          - Extracts indentation from the target function line and applies it to all JSDoc lines
          - Searches backward up to 200 lines from the target to find an existing JSDoc block (/** ... */)
          - If an existing JSDoc block is found immediately preceding the function, replaces it entirely
          - If no existing JSDoc block is found, inserts the new block directly before the function line
          - Validates the modified source syntax using tree-sitter parser if available
          - Writes modified source back to file with UTF-8 encoding

          Edge cases:
          - Handles empty docstring lines by outputting " *" without trailing content
          - Stops backward search if non-comment code is encountered before finding JSDoc start
          - Gracefully handles missing tree-sitter parser (validation is optional)
          - Normalizes line indices to handle 1-indexed input against 0-indexed internal arrays
            deps:
              calls:
                - ValueError
                - candidate.insert
                - docstring.split
                - endswith
                - filepath.read_text
                - filepath.write_text
                - getattr
                - join
                - jsdoc_lines.append
                - len
                - list
                - lstrip
                - max
                - range
                - s.endswith
                - s.startswith
                - self.validate_syntax_string
                - source.split
                - strip
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          JSDoc blocks must be precisely positioned and formatted to be recognized by documentation generators and IDE tooling.
          The backward search with a 200-line limit balances finding legitimate preceding comments while avoiding false matches
          with unrelated documentation far above the target. Indentation preservation ensures the generated documentation
          visually aligns with the code structure. Optional tree-sitter validation catches syntax errors early without requiring
          external tooling to be mandatory. In-place file modification allows integration into automated documentation workflows.

        guardrails:
          - DO NOT assume the file encoding is anything other than UTF-8; explicitly handle encoding errors to prevent silent data corruption
          - DO NOT search backward indefinitely; the 200-line limit prevents pathological performance on large files with many comments
          - DO NOT replace JSDoc blocks that are not immediately preceding the function; verify start_replace <= end_replace < func_line_idx to avoid replacing unrelated documentation
          - DO NOT fail silently if tree-sitter validation is unavailable; use getattr with defaults to gracefully degrade
          - DO NOT modify the file if syntax validation fails; call validate_syntax_string before write_text to prevent introducing broken code
          - DO NOT assume the target line exists; validate func_line_idx is within bounds before accessing lines array

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            source = filepath.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            raise ValueError(f"Cannot read {filepath}: {e}")

        lines = source.split('\n')
        func_line_idx = max(0, lineno - 1)
        if func_line_idx >= len(lines):
            raise ValueError(f"Line {lineno} out of range for {filepath}")

        indent = len(lines[func_line_idx]) - len(lines[func_line_idx].lstrip())
        indent_str = ' ' * max(0, indent)

        # Format new JSDoc content
        jsdoc_lines = ['/**']
        for line in docstring.split('\n'):
            jsdoc_lines.append(f" * {line}" if line else " *")
        jsdoc_lines.append(' */')
        jsdoc_str = '\n'.join(f'{indent_str}{line}' for line in jsdoc_lines)

        # Robust replacement: search for nearest '/**' above and its matching '*/' before the function line
        start_replace = None
        end_replace = None

        # Find nearest start '/**' above the function
        for i in range(func_line_idx - 1, max(-1, func_line_idx - 200), -1):
            s = lines[i].strip()
            if '/**' in s:
                start_replace = i
                # Find the end '*/' from start downwards to function line
                for j in range(i, func_line_idx):
                    if lines[j].strip().endswith('*/'):
                        end_replace = j
                        break
                break
            # Stop if we see non-comment code before finding any start
            if s and not s.startswith('*') and not s.startswith('/*') and not s.startswith('//') and not s.endswith('*/'):
                break

        candidate = list(lines)
        if start_replace is not None and end_replace is not None and start_replace <= end_replace < func_line_idx:
            candidate[start_replace:end_replace + 1] = [jsdoc_str]
        else:
            candidate.insert(func_line_idx, jsdoc_str)

        modified_source = '\n'.join(candidate)

        if getattr(self, '_tree_sitter_available', False) and getattr(self, 'parser', None) is not None:
            self.validate_syntax_string(modified_source, filepath)

        filepath.write_text(modified_source, encoding='utf-8')

    def gather_metadata(self, filepath: Path, function_name: str) -> Dict:
        """
        ---agentspec
        what: |
          Extracts structural metadata from a Python source file for a specified function using tree-sitter parsing.

          Inputs:
            - filepath: Path object pointing to a Python source file
            - function_name: string identifier of the target function to analyze

          Outputs:
            - Dictionary with three keys:
              - 'calls': list of function names called within the target function
              - 'imports': list of import statements present in the file
              - 'called_by': empty list (cross-file analysis not yet implemented)

          Behavior:
            - Returns early with empty metadata dict if tree-sitter parser is unavailable
            - Attempts to read file with UTF-8 encoding; returns empty dict on IOError or UnicodeDecodeError
            - Parses source code into AST using tree-sitter; returns empty dict on parse failure
            - Delegates extraction logic to helper methods (_extract_function_calls, _extract_imports)
            - Gracefully degrades to empty results rather than raising exceptions

          Edge cases:
            - Missing or inaccessible files: returns empty metadata
            - Files with encoding issues: returns empty metadata
            - Malformed Python syntax: returns empty metadata
            - tree-sitter unavailable: returns empty metadata immediately
            - 'called_by' field is placeholder; cross-file call graph analysis not implemented
            deps:
              calls:
                - f.read
                - open
                - parser.parse
                - self._extract_function_calls
                - self._extract_imports
                - source.encode
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Defensive error handling ensures the metadata extraction pipeline remains robust when encountering file system issues, encoding problems, or syntactically invalid code. Early return for unavailable tree-sitter prevents unnecessary file I/O. Delegating extraction to helper methods maintains separation of concerns and allows independent testing of parsing logic. Returning empty dicts instead of raising exceptions allows callers to handle missing metadata gracefully without try-catch overhead.

        guardrails:
          - DO NOT assume tree-sitter is available; check _tree_sitter_available flag first to avoid runtime errors on systems without native bindings
          - DO NOT raise exceptions for file I/O or parse failures; return empty metadata dict to maintain caller stability
          - DO NOT implement cross-file 'called_by' analysis in this method; it requires separate indexing infrastructure and should be deferred to a dedicated call-graph builder
          - DO NOT modify the source file or cache results; this method must be side-effect-free for safe repeated invocation
          - DO NOT assume function_name exists in the file; extraction helpers must handle missing targets gracefully

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            return {'calls': [], 'imports': [], 'called_by': []}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except (IOError, UnicodeDecodeError):
            return {'calls': [], 'imports': [], 'called_by': []}

        try:
            tree = self.parser.parse(source.encode('utf-8'))
        except Exception:
            return {'calls': [], 'imports': [], 'called_by': []}

        result = {
            'calls': self._extract_function_calls(tree, source, function_name),
            'imports': self._extract_imports(tree, source),
            'called_by': [],  # TODO: implement cross-file analysis
        }

        return result

    def validate_syntax(self, filepath: Path) -> bool:
        """
        ---agentspec
        what: |
          Validates JavaScript syntax by reading a file from disk and re-parsing its contents.

          **Inputs:**
          - filepath: Path object pointing to a JavaScript source file

          **Outputs:**
          - Returns True if the file contains valid JavaScript syntax
          - Raises ValueError if the file cannot be read or contains invalid syntax

          **Behavior:**
          1. Opens the file at the given filepath with UTF-8 encoding
          2. Reads the entire file contents into memory as a string
          3. Delegates syntax validation to validate_syntax_string() method
          4. Propagates any ValueError raised by the validation method

          **Edge Cases:**
          - File does not exist: IOError caught and wrapped in ValueError
          - File is not readable (permissions): IOError caught and wrapped in ValueError
          - File contains invalid UTF-8 sequences: UnicodeDecodeError caught and wrapped in ValueError
          - Empty files: Passed to validate_syntax_string() for handling
          - Very large files: Entire contents loaded into memory (potential memory concern)
          - Symbolic links and special files: Handled by standard open() behavior
            deps:
              calls:
                - ValueError
                - f.read
                - open
                - self.validate_syntax_string
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This method provides a file-based entry point to syntax validation, abstracting away I/O concerns from the core validation logic. By delegating to validate_syntax_string(), it maintains separation of concerns: file handling is isolated from parsing logic, making both easier to test and reuse independently. The explicit exception wrapping (IOError/UnicodeDecodeError → ValueError) provides a consistent error contract to callers, who need not handle multiple exception types. Re-parsing the source (rather than using cached AST or metadata) ensures validation reflects the actual current file state on disk.

        guardrails:
          - DO NOT assume the file encoding is anything other than UTF-8; explicitly specify encoding to avoid platform-dependent defaults
          - DO NOT silently ignore read errors; wrap and re-raise as ValueError to maintain consistent error semantics with validate_syntax_string()
          - DO NOT load extremely large files without considering memory implications; callers should validate file size if needed
          - DO NOT modify the file or its permissions during validation; this is a read-only operation
          - DO NOT cache file contents across calls; always re-read to detect external modifications

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except (IOError, UnicodeDecodeError) as e:
            raise ValueError(f"Cannot read {filepath}: {e}")

        return self.validate_syntax_string(source)

    def validate_syntax_string(self, source: str, filepath: Path = None) -> bool:
        """
        ---agentspec
        what: |
          Validates JavaScript, TypeScript, and TSX source code syntax using tree-sitter parsing.

          Accepts a source code string and optional filepath. Selects the appropriate parser based on file extension:
          - .tsx files use tsx_parser
          - .ts files use ts_parser
          - .js, .mjs, .jsx files use js_parser (or default js_parser if no filepath provided)

          Encodes the source string to UTF-8 bytes and parses it into an abstract syntax tree (AST).
          Inspects the resulting tree for ERROR nodes, which indicate parse failures or syntax violations.

          Returns True if parsing succeeds with no ERROR nodes present.
          Raises ValueError with descriptive message if ERROR nodes are detected in the tree.
          Raises RuntimeError if tree-sitter is not available in the runtime environment.

          Edge cases:
          - Empty source strings parse successfully (valid empty program)
          - Filepath parameter is optional; omission defaults to JavaScript parser
          - File extension matching is case-insensitive
          - UTF-8 encoding handles Unicode characters in source code
          - Malformed syntax produces ERROR nodes rather than exceptions during parsing
            deps:
              calls:
                - RuntimeError
                - ValueError
                - parser.parse
                - self._has_error_nodes
                - source.encode
                - suffix.lower
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter provides robust, incremental parsing for multiple language variants without requiring external processes or language runtimes.
          Parser selection by file extension ensures language-specific syntax rules are applied (e.g., TypeScript type annotations, JSX elements).
          ERROR node detection is the standard tree-sitter pattern for identifying parse failures without exception handling overhead.
          UTF-8 encoding is required by tree-sitter's C API and handles modern JavaScript source files universally.
          Returning boolean on success and raising exceptions on failure provides clear success/failure semantics for validation workflows.

        guardrails:
          - DO NOT assume tree-sitter is installed; always check _tree_sitter_available flag first to avoid ImportError at runtime
          - DO NOT parse untrusted source without resource limits; tree-sitter can consume significant memory on pathologically nested code
          - DO NOT rely on ERROR node detection alone for security validation; syntax validity does not imply semantic safety
          - DO NOT modify the source string before encoding; preserve original whitespace and line endings for accurate error reporting
          - DO NOT use this for runtime code execution validation; syntax validation does not guarantee the code is safe to execute

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            raise RuntimeError("tree-sitter not available; cannot validate syntax")

        # Select parser based on file extension
        parser = self.parser  # Default to JavaScript
        if filepath:
            ext = filepath.suffix.lower()
            if ext == '.tsx':
                parser = self.tsx_parser
            elif ext == '.ts':
                parser = self.ts_parser
            elif ext in {'.jsx', '.mjs', '.js'}:
                parser = self.js_parser

        tree = parser.parse(source.encode('utf-8'))
        # Check for ERROR nodes indicating parse failures
        if self._has_error_nodes(tree):
            raise ValueError("Syntax error: parser encountered ERROR nodes")
        return True

    def get_comment_delimiters(self) -> tuple[str, str]:
        """
        ---agentspec
        what: |
          Returns a tuple of two strings representing the standard JSDoc multi-line comment delimiters used in JavaScript.

          Output: A tuple containing exactly two elements:
          - First element: '/**' (opening delimiter for JSDoc blocks)
          - Second element: '*/' (closing delimiter for JSDoc blocks)

          This method provides the canonical comment syntax for JavaScript documentation generation tools. JSDoc is the de facto standard for documenting JavaScript code and is recognized by IDEs, linters, and documentation generators.

          The delimiters are hardcoded and language-specific, reflecting JavaScript's fixed syntax for multi-line comments. No parameters are required as the delimiters are invariant for the JavaScript language.

          Edge cases: None applicable—the return value is constant and deterministic.
            deps:
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          This method abstracts language-specific comment syntax into a consistent interface. By centralizing delimiter definitions, the codebase can programmatically generate or parse documentation blocks without hardcoding language details throughout the adapter layer.

          The tuple return type (rather than separate methods or a dict) provides a lightweight, ordered pair that maps directly to opening and closing delimiters, making it intuitive for callers to unpack and use immediately.

          JSDoc delimiters are standardized and non-configurable in JavaScript, so a static return is appropriate and efficient.

        guardrails:
          - DO NOT modify the returned delimiters at runtime—they are language-defined constants and changing them would break JSDoc compliance and IDE recognition.
          - DO NOT assume these delimiters work for single-line comments—JSDoc requires multi-line comment syntax; use '//' only for non-documentation comments.
          - DO NOT return delimiters in reverse order—callers expect (opening, closing) tuple order for correct block construction.

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        return ('/**', '*/')

    def parse(self, source_code: str) -> Any:
        """
        ---agentspec
        what: |
          Parses JavaScript source code into a tree-sitter Tree object for syntactic analysis.

          **Inputs:**
          - source_code (str): Raw JavaScript source code to be parsed

          **Outputs:**
          - tree-sitter Tree object: Abstract syntax tree representation of the input code, enabling traversal and node inspection

          **Behavior:**
          - Encodes the input string to UTF-8 bytes before passing to the underlying tree-sitter parser
          - Returns the complete parse tree, including all nodes and their relationships
          - Raises RuntimeError if tree-sitter is not available (checked via _tree_sitter_available flag)

          **Edge Cases:**
          - Empty strings: Will parse successfully, returning a minimal tree with root node
          - Malformed JavaScript: tree-sitter will still produce a tree with error nodes; does not raise an exception
          - Non-UTF-8 compatible strings: Encoding step may fail if source_code contains invalid UTF-8 sequences
          - Very large files: No built-in size limits, but memory usage scales with code size
            deps:
              calls:
                - RuntimeError
                - parser.parse
                - source_code.encode
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          tree-sitter provides incremental, robust parsing that handles incomplete or malformed code gracefully, making it suitable for IDE-like use cases and incremental analysis. UTF-8 encoding is the standard for tree-sitter's byte-based API. The availability check prevents cryptic downstream errors when the native tree-sitter library is not installed. Returning the raw Tree object preserves flexibility for callers to traverse and analyze the AST according to their needs.

        guardrails:
          - DO NOT assume the returned tree is always valid or error-free; tree-sitter produces partial trees for malformed code, so callers must inspect error nodes
          - DO NOT pass non-string types to source_code; the encode() call will fail on non-string inputs
          - DO NOT rely on this method to validate JavaScript syntax; use the tree's error nodes to detect parse failures
          - DO NOT cache or reuse Tree objects across multiple parse calls without understanding tree-sitter's memory model; trees may reference shared parser state

            changelog:
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            raise RuntimeError("tree-sitter not available; cannot parse JavaScript")

        return self.parser.parse(source_code.encode('utf-8'))

    # Private helper methods

    def _find_preceding_jsdoc(self, source: str, tree: Any, lineno: int) -> Optional[str]:
        """
        ---agentspec
        what: |
          Searches backward from a given line number to locate a JSDoc comment block (/** ... */) that immediately precedes a function or class declaration. Returns the extracted JSDoc content as a string, or None if no valid JSDoc is found or tree-sitter is unavailable.

          Inputs:
            - source: Full source code as a single string
            - tree: AST tree object (currently unused but available for future enhancement)
            - lineno: Line number of the function/class declaration (1-indexed)

          Outputs:
            - String containing extracted JSDoc content if found
            - None if tree-sitter is disabled, no JSDoc found, or extraction fails

          Behavior:
            1. Returns None immediately if tree-sitter is not available (graceful degradation)
            2. Splits source into lines and searches backward from lineno-2 up to 50 lines prior
            3. Identifies JSDoc end marker (*/) and then searches backward for start marker (**)
            4. Extracts comment lines between markers and processes via _extract_jsdoc_content()
            5. Returns processed content if non-empty, otherwise continues searching or returns None
            6. Stops searching after finding first complete JSDoc block or reaching 50-line boundary

          Edge cases:
            - lineno beyond source length: safely skipped via bounds check
            - Malformed JSDoc (missing /** or **): ignored, search continues
            - Multiple JSDoc blocks in 50-line window: returns first (closest) one found
            - Empty JSDoc content after extraction: treated as invalid, search continues
            - tree-sitter unavailable: returns None without attempting parse
            deps:
              calls:
                - len
                - line.endswith
                - max
                - range
                - self._extract_jsdoc_content
                - source.split
                - strip
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          JSDoc comments are critical metadata for JavaScript/TypeScript documentation extraction. Searching backward from declaration line is efficient because JSDoc conventionally appears immediately above the declaration. The 50-line limit prevents excessive backward scanning in large files while accommodating reasonable comment spacing. Graceful fallback to None when tree-sitter is unavailable allows the adapter to function in degraded mode. Delegating content extraction to _extract_jsdoc_content() maintains separation of concerns and allows flexible comment normalization.

        guardrails:
          - DO NOT assume lineno is always valid or within source bounds; always check array indices to prevent IndexError
          - DO NOT search beyond 50 lines backward; this prevents performance degradation on large files and catches only reasonably-positioned JSDoc
          - DO NOT return partial or malformed JSDoc; validate via _extract_jsdoc_content() to ensure content quality
          - DO NOT proceed if tree-sitter is unavailable; the early return prevents cascading failures in downstream parsing
          - DO NOT assume JSDoc markers are on separate lines; handle cases where /** and */ may share lines with code

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            return None

        lines = source.split('\n')

        # Look backward for preceding JSDoc
        for i in range(lineno - 2, max(-1, lineno - 50), -1):
            if i >= len(lines):
                continue
            line = lines[i].strip()
            if line.endswith('*/'):
                # Found potential JSDoc end, now find start
                for j in range(i, max(-1, i - 50), -1):
                    if j >= len(lines):
                        continue
                    if '/**' in lines[j]:
                        # Extract JSDoc content
                        comment_lines = lines[j:i+1]
                        content = self._extract_jsdoc_content(comment_lines)
                        if content:
                            return content
                        break
                break
        return None

    def _extract_jsdoc_content(self, comment_lines: List[str]) -> str:
        """
        ---agentspec
        what: |
          Extracts the textual content from JSDoc comment lines by removing JSDoc syntax markers and normalizing whitespace.

          Input: A list of strings representing lines from a JSDoc comment block (e.g., ['/**', ' * @param foo description', ' */'])

          Processing:
          - Skips lines that are pure JSDoc delimiters (lines starting with '/**' or ending with '*/')
          - Removes leading asterisk ('*') from each line and strips surrounding whitespace
          - Filters out empty lines after normalization
          - Joins remaining content lines with newline characters

          Output: A single string containing the cleaned docstring content without JSDoc markup

          Edge cases:
          - Handles mixed indentation and spacing around asterisks
          - Preserves internal content structure and line breaks
          - Returns empty string if input contains only JSDoc delimiters or whitespace
          - Does not parse or validate JSDoc tags (@param, @returns, etc.) — only removes syntax markers
            deps:
              calls:
                - content.append
                - join
                - line.strip
                - lstrip
                - stripped.endswith
                - stripped.startswith
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          JSDoc comments use a specific syntax (/** ... */) that must be stripped to extract human-readable documentation.
          This function normalizes the raw comment lines into clean text suitable for downstream processing or display.
          By separating syntax removal from semantic parsing, the function maintains a single responsibility and allows
          tag parsing to operate on clean content. The line-by-line approach handles variable indentation gracefully
          without requiring regex or complex state machines.

        guardrails:
          - DO NOT assume consistent indentation — JSDoc lines may have varying leading whitespace before the asterisk
          - DO NOT strip internal whitespace or collapse multiple spaces within content — preserve formatting intent
          - DO NOT attempt to parse JSDoc tags in this function — that is a separate concern for tag extraction
          - DO NOT return lines that are only whitespace — empty lines should be filtered to avoid spurious newlines
          - DO NOT modify the order or structure of content lines — maintain document flow for downstream consumers

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        content: List[str] = []
        for line in comment_lines:
            stripped = line.strip()
            if stripped.startswith('/**') or stripped.endswith('*/'):
                continue
            if stripped.startswith('*'):
                stripped = stripped[1:].lstrip()
            if stripped:
                content.append(stripped)
        return '\n'.join(content)

    def _find_node_at_line(self, tree: Any, lineno: int) -> Optional[Any]:
        """
        ---agentspec
        what: |
          Locates a function or class declaration node at a specific line number within a tree-sitter AST.

          **Inputs:**
          - tree: A tree-sitter Tree object containing the parsed AST
          - lineno: Target line number (1-based indexing) to search for

          **Outputs:**
          - Returns the AST node if a matching function/class declaration is found at the exact line
          - Returns None if tree-sitter is unavailable, no match exists, or tree is malformed

          **Behavior:**
          - Performs depth-first recursive traversal of the AST starting from tree.root_node
          - Converts tree-sitter's 0-based line numbering to 1-based for comparison
          - Matches against five node types: function_declaration, arrow_function, function_expression, method_definition, class_declaration
          - Returns immediately upon first match (does not continue searching siblings after finding a result)
          - Handles missing or None nodes gracefully without raising exceptions

          **Edge cases:**
          - Returns None if _tree_sitter_available flag is False (graceful degradation)
          - Handles sparse ASTs where target line has no declaration
          - Correctly processes nested declarations (inner functions/classes)
          - Works with arrow functions and method definitions in addition to standard declarations
            deps:
              calls:
                - find_in_node
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter provides fast, incremental parsing with precise line/column information needed for accurate source mapping.
          The recursive approach is natural for AST traversal and avoids maintaining explicit stack state.
          Early return on match optimizes for common case where declarations are not deeply nested.
          The availability check prevents runtime errors when tree-sitter is not installed or initialized.
          1-based line numbering conversion aligns with editor conventions and user expectations.

        guardrails:
          - DO NOT assume tree.root_node exists without checking—malformed or uninitialized trees may cause AttributeError
          - DO NOT modify node state during traversal; this is a read-only inspection operation
          - DO NOT search beyond the first matching node at the target line—multiple declarations on same line are ambiguous and first match is sufficient
          - DO NOT rely on this function for line ranges; it only matches exact line numbers where declaration starts
          - DO NOT skip the _tree_sitter_available check—calling without it may fail if tree-sitter dependency is missing

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not self._tree_sitter_available:
            return None

        def find_in_node(node):
            """
            ---agentspec
            what: |
              Recursively traverses a tree-sitter AST to locate a function or class declaration at a specific target line number. Accepts a node parameter (typically the root of an AST subtree) and searches depth-first through all children until finding a node whose type matches one of the supported declaration types (function_declaration, arrow_function, function_expression, method_definition, class_declaration) AND whose start line equals the target lineno.

              Inputs: node (tree-sitter Node object or None), lineno (integer, 1-based line number from caller context)
              Outputs: Returns the matching tree-sitter Node object if found, otherwise None

              Edge cases handled:
              - Null/None node input returns None immediately (base case)
              - Line number conversion: tree-sitter uses 0-based indexing; function adds 1 to node.start_point[0] to match 1-based line numbers expected by callers
              - Multiple nested declarations at same line: returns first match found via depth-first traversal
              - No matching declaration at target line: returns None after exhausting all children
                deps:
                  calls:
                    - find_in_node
                  imports:
                    - __future__.annotations
                    - logging
                    - pathlib.Path
                    - re
                    - typing.Any
                    - typing.Dict
                    - typing.List
                    - typing.Optional
                    - typing.Set


            why: |
              Tree-sitter provides efficient incremental parsing and precise AST node location data. Recursive depth-first search is the natural traversal pattern for AST structures and avoids maintaining explicit stack state. Converting to 1-based line numbers at the node level (rather than at call sites) centralizes the indexing logic and reduces caller burden. Early return on match optimizes for the common case where target is found in a shallow subtree.

            guardrails:
              - DO NOT assume node.start_point exists without checking node is not None first; tree-sitter nodes may have incomplete metadata in edge cases
              - DO NOT modify the node object or its children during traversal; this function must be read-only to preserve AST integrity for subsequent operations
              - DO NOT rely on this function to disambiguate between multiple declarations at the same line; if multiple functions/classes start at lineno, only the first discovered is returned (depth-first order)
              - DO NOT use this on unparsed or malformed AST trees; caller must ensure tree-sitter parsing succeeded before invoking

                changelog:
                  - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
                  - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
                  - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
                  - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
                ---/agentspec
            """
            if not node:
                return None

            node_type = node.type
            node_start_line = node.start_point[0] + 1  # tree-sitter uses 0-based line numbers

            # Check if this node matches
            if node_type in (
                'function_declaration', 'arrow_function', 'function_expression',
                'method_definition', 'class_declaration'
            ) and node_start_line == lineno:
                return node

            # Recursively search children
            for child in node.children:
                result = find_in_node(child)
                if result:
                    return result
            return None

        return find_in_node(tree.root_node)

    def _extract_function_calls(self, tree: Any, source: str, function_name: str) -> List[str]:
        """
        ---agentspec
        what: |
          Extracts all unique function call names from within a specific function's AST subtree.

          **Inputs:**
          - tree: A tree-sitter Tree object (or object with root_node attribute) representing parsed source code
          - source: The original source code string, used to extract call names from AST nodes
          - function_name: The name of the target function (currently unused in extraction logic; caller responsible for tree scoping)

          **Outputs:**
          - Returns a sorted list of unique function call names (strings) found within the function body
          - Returns empty list if tree-sitter is unavailable

          **Behavior:**
          - Performs depth-first recursive traversal of the AST starting from tree.root_node
          - Identifies all nodes with type 'call_expression'
          - Extracts the call name from each call_expression node via _extract_call_name helper
          - Deduplicates results using set conversion before sorting
          - Gracefully degrades to empty list if tree-sitter dependency is not available

          **Edge Cases:**
          - Handles missing or None nodes without crashing (early return in recursion)
          - Filters out None/empty call names returned by _extract_call_name
          - Works with any tree-sitter compatible language parser (not JavaScript-specific despite file location)
            deps:
              calls:
                - calls.append
                - collect_calls
                - hasattr
                - list
                - self._extract_call_name
                - set
                - sorted
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Recursive tree traversal is necessary because call_expression nodes can appear at arbitrary depths within nested scopes (blocks, conditionals, loops). Deduplication and sorting provide a canonical, deterministic output suitable for dependency analysis and comparison. The tree-sitter availability check prevents runtime errors in environments where the native binding is not installed. Delegating call name extraction to _extract_call_name allows language-specific parsing logic to be isolated and reused.

        guardrails:
          - DO NOT assume tree.root_node exists without checking hasattr; some tree-sitter versions or mock objects may not expose this attribute
          - DO NOT skip the tree-sitter availability check; calling tree-sitter methods when unavailable will raise AttributeError
          - DO NOT rely on function_name parameter for filtering; the caller must pass a pre-scoped tree containing only the target function's AST
          - DO NOT return unsorted or non-deduplicated results; callers depend on canonical ordering for caching and comparison
          - DO NOT assume _extract_call_name always returns a non-empty string; filter out falsy values to avoid polluting the call list

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        calls: List[str] = []
        if not self._tree_sitter_available:
            return calls

        def collect_calls(node):
            """
            ---agentspec
            what: |
              Recursively traverses an Abstract Syntax Tree (AST) node and its descendants to identify and collect all function/method call expressions. For each node of type 'call_expression' encountered, extracts the call name using the _extract_call_name helper method and appends it to a calls list if extraction succeeds. The recursion terminates when a None node is encountered or when all children have been processed. Handles edge cases where call_name extraction returns None or falsy values by skipping those entries. Returns implicitly via side-effect mutation of the outer scope's calls list.

              Inputs: node (AST node object with .type and .children attributes, or None)
              Outputs: None (side-effect: populates calls list in enclosing scope)
              Edge cases: None nodes, nodes without children attribute, failed call name extraction, deeply nested AST structures
                deps:
                  calls:
                    - calls.append
                    - collect_calls
                    - self._extract_call_name
                  imports:
                    - __future__.annotations
                    - logging
                    - pathlib.Path
                    - re
                    - typing.Any
                    - typing.Dict
                    - typing.List
                    - typing.Optional
                    - typing.Set

            why: |
              Recursive tree traversal is the natural approach for AST analysis since call expressions can appear at arbitrary nesting depths. Using a nested function allows access to the outer scope's calls list and source context without parameter threading. Early None-check prevents AttributeError on null nodes. Conditional append only on successful extraction avoids polluting results with None or empty strings, maintaining data quality.
            guardrails:
              - DO NOT assume node.children exists without type checking—some AST implementations may have sparse or missing children attributes, causing AttributeError
              - DO NOT skip the None guard at function entry—recursive calls may pass None and cause crashes if not handled
              - DO NOT append call_name without truthiness validation—failed extractions (None, empty string) corrupt the calls collection
              - DO NOT use this function on extremely deep AST trees without stack depth monitoring—Python's default recursion limit (~1000) may be exceeded on pathological inputs

                changelog:
                  - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
                  - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
                  - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
                  - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
                ---/agentspec
            """
            if not node:
                return
            if node.type == 'call_expression':
                call_name = self._extract_call_name(node, source)
                if call_name:
                    calls.append(call_name)
            for child in node.children:
                collect_calls(child)

        if hasattr(tree, 'root_node'):
            collect_calls(tree.root_node)
        return sorted(list(set(calls)))

    def _extract_call_name(self, call_node: Any, source: str) -> Optional[str]:
        """
        ---agentspec
        what: |
          Extracts the name of a called function from a tree-sitter call_expression AST node.

          Takes a call_node (tree-sitter Node object) and the original source code string as inputs.
          Returns the extracted function name as a string, or None if extraction fails.

          Process:
          1. Validates call_node exists and has tree-sitter Node interface (child_by_field_name method)
          2. Retrieves the 'function' child field from the call_node using tree-sitter's field API
          3. Extracts byte offsets (start_byte, end_byte) from the function node
          4. Validates byte range is within source bounds (0 <= start < end <= source length in UTF-8 bytes)
          5. Slices source string using byte offsets and strips whitespace
          6. Returns cleaned name or None if name is empty string

          Edge cases handled:
          - Missing or malformed call_node (returns None)
          - Missing 'function' field in call_node (returns None)
          - Invalid byte ranges or out-of-bounds offsets (returns None)
          - UTF-8 encoding edge cases (byte length validation before slicing)
          - Exception during extraction (caught and returns None)
          - Whitespace-only function names (stripped to None)
            deps:
              calls:
                - call_node.child_by_field_name
                - hasattr
                - len
                - name.strip
                - source.encode
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter provides byte-offset-based source extraction rather than direct text in AST nodes.
          This approach:
          - Avoids reliance on tree-sitter's potentially incomplete node.text property
          - Enables precise extraction by directly indexing the source with validated byte offsets
          - Handles UTF-8 multi-byte characters correctly by validating encoded byte length
          - Provides defensive null-checking at each step to prevent crashes on malformed AST
          - Strips whitespace to normalize function names that may include formatting

          Tradeoff: Requires passing original source string (memory overhead) but ensures accuracy
          for JavaScript call expressions across different syntax variations.

        guardrails:
          - DO NOT assume call_node has tree-sitter Node interface without hasattr check; external callers may pass invalid types
          - DO NOT slice source using byte offsets without validating against UTF-8 encoded length; multi-byte characters can cause index misalignment
          - DO NOT skip the bounds check (0 <= start < end <= len); malformed AST nodes can produce out-of-range offsets
          - DO NOT return whitespace-only strings; strip and convert empty results to None for consistent null semantics
          - DO NOT let exceptions propagate; catch all exceptions during extraction to maintain robustness in AST traversal loops

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not call_node or not hasattr(call_node, 'child_by_field_name'):
            return None
        func_node = call_node.child_by_field_name('function')
        if not func_node:
            return None
        start = func_node.start_byte
        end = func_node.end_byte
        # Slice using byte offsets on the UTF-8 encoded buffer, then decode.
        source_bytes = source.encode('utf-8')
        if 0 <= start < end <= len(source_bytes):
            try:
                name = source_bytes[start:end].decode('utf-8', errors='replace')
                return name.strip() if name else None
            except Exception:
                return None
        return None

    def _extract_imports(self, tree: Any, source: str) -> List[str]:
        """
        ---agentspec
        what: |
          Recursively traverses a tree-sitter parse tree to extract import statements from JavaScript/TypeScript source code.

          Inputs:
            - tree: A tree-sitter Tree object (or None if tree-sitter unavailable)
            - source: The original source code string as UTF-8 encoded text

          Outputs:
            - List[str]: Deduplicated list of import statement text strings extracted from the source

          Behavior:
            - Returns empty list immediately if tree-sitter is not available (graceful degradation)
            - Recursively traverses all nodes in the parse tree via depth-first traversal
            - Identifies import nodes by type: 'import_statement', 'import_clause', or 'require_clause'
            - Extracts raw source text using byte offsets (start_byte, end_byte) from the tree node
            - Validates byte offsets are within bounds of UTF-8 encoded source before extraction
            - Strips whitespace from extracted import text and filters empty strings
            - Silently catches and ignores any extraction exceptions (malformed nodes, encoding issues)
            - Deduplicates results using set() before returning

          Edge cases:
            - Tree-sitter unavailable: returns empty list without error
            - Malformed parse tree or invalid byte offsets: silently skipped via exception handling
            - Empty or whitespace-only import nodes: filtered out
            - UTF-8 encoding edge cases: bounds checking prevents index errors
            - Duplicate imports in source: automatically deduplicated in output
            deps:
              calls:
                - collect_imports
                - hasattr
                - imports.append
                - len
                - list
                - set
                - source.encode
                - strip
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter provides precise AST parsing for multiple languages including JavaScript. Using byte offsets directly from the parse tree is more reliable than regex-based extraction because it respects actual syntax boundaries and handles complex nested structures.

          Deduplication via set() is applied at the end rather than during collection to avoid repeated set operations during recursion, improving performance for large trees.

          Silent exception handling is intentional: malformed nodes or encoding issues should not crash the entire import extraction process. This allows partial extraction to succeed even if some nodes are problematic.

          The bounds check (0 <= start < end <= len(source.encode('utf-8'))) prevents index errors and handles edge cases where tree-sitter offsets might be slightly out of sync with the actual source encoding.

        guardrails:
          - DO NOT assume tree-sitter is always available; always check _tree_sitter_available flag first to prevent AttributeError
          - DO NOT use string slicing directly on byte offsets without validating bounds; UTF-8 encoding can have variable-width characters that cause index misalignment
          - DO NOT re-encode source on every bounds check; cache the encoded length or validate offsets against the original string length to avoid performance degradation
          - DO NOT raise exceptions on malformed nodes; silently skip them to allow partial extraction and maintain robustness
          - DO NOT skip deduplication; imports may appear multiple times in source and duplicates should be removed before returning

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        imports: List[str] = []
        if not self._tree_sitter_available:
            return imports

        # Pre-encode once; tree-sitter offsets are byte-based
        source_bytes = source.encode('utf-8')
        source_bytes_len = len(source_bytes)

        def collect_imports(node):
            """
            ---agentspec
            what: |
              Recursively traverses a tree-sitter AST node to extract and collect import statements from source code.

              Behavior:
              - Accepts a tree-sitter node object (or None)
              - Returns early if node is falsy to prevent recursion errors
              - Identifies import-related nodes by type: 'import_statement', 'import_clause', 'require_clause'
              - For matching nodes, extracts byte range (start_byte to end_byte) and validates bounds against UTF-8 encoded source length
              - Slices source code using byte indices, strips whitespace, and appends non-empty import text to shared imports list
              - Silently catches and ignores any extraction exceptions to prevent parse failures from blocking traversal
              - Recursively processes all child nodes depth-first

              Inputs:
              - node: tree-sitter Node object or None
              - Implicit dependency on outer scope: source (string), imports (list accumulator)

              Outputs:
              - Mutates imports list by appending extracted import statement strings
              - Returns None

              Edge cases:
              - Handles None/falsy nodes gracefully
              - Validates byte indices are within valid range before slicing
              - Tolerates UTF-8 encoding edge cases and extraction errors
              - Processes nodes with no children without error
                deps:
                  calls:
                    - collect_imports
                    - imports.append
                    - len
                    - source.encode
                    - strip
                  imports:
                    - __future__.annotations
                    - logging
                    - pathlib.Path
                    - re
                    - typing.Any
                    - typing.Dict
                    - typing.List
                    - typing.Optional
                    - typing.Set


            why: |
              Tree-sitter provides byte-indexed AST nodes that require careful boundary validation when slicing source text, especially with multi-byte UTF-8 characters. Recursive traversal is necessary because import statements can appear at various nesting levels in the AST. Silent exception handling prevents a single malformed node from halting the entire import collection process, prioritizing robustness over strict error reporting. The byte-range validation guards against off-by-one errors and corrupted AST metadata that could cause index out-of-bounds exceptions.

            guardrails:
              - DO NOT assume node.start_byte and node.end_byte are always valid—always validate against encoded source length to prevent IndexError on corrupted or edge-case AST nodes
              - DO NOT use string indices directly on source without converting byte indices, as Python string indexing is character-based and will misalign with multi-byte UTF-8 sequences
              - DO NOT re-raise exceptions during import extraction—silent failure ensures one malformed import statement does not block collection of valid imports from sibling/parent nodes
              - DO NOT modify the source string or node structure during traversal—only append to the imports accumulator to maintain functional purity and prevent side effects
              - DO NOT assume all nodes have a children attribute—always iterate safely or check hasattr to avoid AttributeError on leaf nodes

                changelog:
                  - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
                  - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
                  - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
                  - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
                ---/agentspec
            """
            if not node:
                return
            if node.type in ('import_statement', 'import_clause', 'require_clause'):
                start = node.start_byte
                end = node.end_byte
                if 0 <= start < end <= source_bytes_len:
                    try:
                        import_text = source_bytes[start:end].decode('utf-8', errors='replace').strip()
                        if import_text:
                            imports.append(import_text)
                    except Exception:
                        pass
            for child in node.children:
                collect_imports(child)

        if hasattr(tree, 'root_node'):
            collect_imports(tree.root_node)
        return list(set(imports))

    def _has_error_nodes(self, tree: Any) -> bool:
        """
        ---agentspec
        what: |
          Recursively inspects a tree-sitter parse tree to detect parsing failures and syntax errors.

          Returns True if the tree contains ERROR nodes (indicating malformed syntax that tree-sitter could not parse) or MISSING nodes (indicating incomplete or invalid syntax such as unclosed JSX tags).

          Returns True immediately if the input tree is None, falsy, or lacks a root_node attribute, treating these as error conditions.

          The function performs depth-first traversal of the tree starting from root_node. For each node:
          - Checks if node.type equals 'ERROR' (direct parse failure indicator)
          - Checks if 'MISSING' string appears in node.sexp() output (incomplete syntax indicator that doesn't surface as node.type)
          - Recursively checks all child nodes

          Returns False only if tree is valid, has a root_node, and no ERROR or MISSING nodes exist anywhere in the tree hierarchy.
            deps:
              calls:
                - has_errors
                - hasattr
                - node.sexp
              imports:
                - __future__.annotations
                - logging
                - pathlib.Path
                - re
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - typing.Set


        why: |
          Tree-sitter represents parse failures in two distinct ways: ERROR nodes for syntax it cannot parse, and MISSING nodes for incomplete constructs (e.g., unclosed JSX tags). Checking only node.type misses MISSING nodes since they appear in the s-expression representation but not as a distinct type. This dual-check approach ensures comprehensive error detection across both failure modes.

          Early return on invalid tree input (None, no root_node) treats malformed input as an error condition rather than silently returning False, which is safer for downstream consumers expecting a valid parse tree.

          Recursive traversal ensures errors deep in the tree are not missed, which is critical for validating complete parse trees before further processing.

        guardrails:
          - DO NOT rely solely on node.type == 'ERROR' without checking sexp() for MISSING nodes, as incomplete syntax (unclosed tags) will be missed
          - DO NOT assume tree.root_node exists without hasattr check, as malformed or None trees will cause AttributeError
          - DO NOT skip the initial tree validity check (if not tree or not hasattr), as None or invalid trees should signal error state
          - DO NOT assume all nodes have a sexp() method; use hasattr guard to prevent AttributeError on nodes that lack this method
          - DO NOT modify the tree during traversal; this is a read-only inspection function

            changelog:
              - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
              - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
              - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
              - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
            ---/agentspec
        """
        if not tree or not hasattr(tree, 'root_node'):
            return True

        def has_errors(node):
            """
            ---agentspec
            what: |
              Recursively traverses a tree-sitter parse tree node to detect syntax errors and incomplete syntax.

              Returns True if any error condition is found, False otherwise.

              Detection logic:
              - Returns False immediately if node is None or falsy (base case for recursion)
              - Checks node.type == 'ERROR': tree-sitter marks malformed syntax with ERROR node type
              - Checks for 'MISSING' string in node.sexp() output: tree-sitter represents incomplete syntax (e.g., unclosed tags, missing tokens) as MISSING in s-expression form, even though MISSING does not appear as a direct node.type value
              - Recursively checks all child nodes via node.children, returning True on first error found in any subtree
              - Returns False only if node exists and no errors detected in node or any descendants

              Inputs: node (tree-sitter Node object or None)
              Outputs: boolean indicating presence of syntax errors or incomplete syntax anywhere in subtree

              Edge cases:
              - Handles None/falsy nodes gracefully (returns False)
              - Handles nodes without sexp() method via hasattr check (defaults to empty string)
              - Short-circuits recursion on first error found for efficiency
                deps:
                  calls:
                    - has_errors
                    - hasattr
                    - node.sexp
                  imports:
                    - __future__.annotations
                    - logging
                    - pathlib.Path
                    - re
                    - typing.Any
                    - typing.Dict
                    - typing.List
                    - typing.Optional
                    - typing.Set


            why: |
              Tree-sitter represents syntax problems in two distinct ways that must both be checked:
              1. ERROR node type for malformed/unparseable syntax
              2. MISSING token in s-expression for incomplete syntax (unclosed delimiters, missing required tokens)

              Checking only node.type would miss incomplete syntax. Checking only sexp() would be inefficient and miss some error types. Recursive traversal ensures errors anywhere in the parse tree are caught, not just at the root level.

              This approach prioritizes correctness (catching all error types) over performance, which is appropriate for syntax validation where missing an error is worse than slight overhead.

            guardrails:
              - DO NOT rely solely on node.type == 'ERROR' without checking sexp() for MISSING, as incomplete syntax is not marked with ERROR type
              - DO NOT assume all nodes have sexp() method; use hasattr guard to prevent AttributeError on unexpected node types
              - DO NOT skip recursive checks on child nodes; errors can be nested deep in the tree and must be detected
              - DO NOT return True prematurely without checking all children if an error is found at current level, as the function should detect any error in the entire subtree

                changelog:
                  - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
                  - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
                  - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
                  - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
                ---/agentspec
            """
            if not node:
                return False
            # Check for ERROR nodes (malformed syntax)
            if node.type == 'ERROR':
                return True
            # Check for MISSING nodes in sexp (incomplete syntax like unclosed tags)
            # Note: MISSING appears in sexp() but not as node.type
            node_sexp = node.sexp() if hasattr(node, 'sexp') else ''
            if 'MISSING' in node_sexp:
                return True
            for child in node.children:
                if has_errors(child):
                    return True
            return False

        return has_errors(tree.root_node)
