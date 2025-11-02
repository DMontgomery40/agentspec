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
        """Initialize the JavaScript adapter with tree-sitter parsers for JavaScript, TypeScript, and TSX."""
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
        Return JavaScript/TypeScript file extensions this adapter handles.

        Supports .js, .mjs, .jsx, .ts, .tsx.
        """
        return {'.js', '.mjs', '.jsx', '.ts', '.tsx'}

    def discover_files(self, target: Path) -> List[Path]:
        """
        Discover all JavaScript files in target directory or return single file.

        Minimal pre-filtering (only .git exclusion).
        All other exclusions (.venv, node_modules, build, etc.) handled by .gitignore
        via collect_source_files post-filtering.
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
        Extract JSDoc comment from function/class at lineno in filepath.

        Returns the docstring content (without /** */ delimiters), or None.
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
        Insert or replace JSDoc block for function/class at lineno.

        Formats docstring with proper JSDoc indentation and * prefix.

        Behavior:
        - Replaces the closest JSDoc block immediately preceding the target function/class if present,
          regardless of whether we encounter the end (*/) or start (/**) first during scanning.
        - Otherwise inserts a new JSDoc block directly before the function line.
        - Validates the modified source using tree-sitter when available.
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
        Extract function calls, imports, and other metadata for a function.

        Returns dict with 'calls', 'imports', and 'called_by' keys.
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
        Check if file has valid JavaScript syntax by re-parsing.

        Returns True if valid, raises ValueError if invalid.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except (IOError, UnicodeDecodeError) as e:
            raise ValueError(f"Cannot read {filepath}: {e}")

        return self.validate_syntax_string(source)

    def validate_syntax_string(self, source: str, filepath: Path = None) -> bool:
        """
        Validate JavaScript/TypeScript/TSX syntax string using tree-sitter.

        Uses TSX parser for .tsx files, TypeScript parser for .ts files,
        JavaScript parser for .js/.mjs/.jsx files.

        Returns True if valid (no ERROR nodes), raises ValueError if invalid.
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
        Return JavaScript multi-line comment delimiters for JSDoc.
        """
        return ('/**', '*/')

    def parse(self, source_code: str) -> Any:
        """
        Parse JavaScript source code using tree-sitter.

        Returns a tree-sitter Tree object.
        """
        if not self._tree_sitter_available:
            raise RuntimeError("tree-sitter not available; cannot parse JavaScript")

        return self.parser.parse(source_code.encode('utf-8'))

    # Private helper methods

    def _find_preceding_jsdoc(self, source: str, tree: Any, lineno: int) -> Optional[str]:
        """Find JSDoc comment immediately preceding a function/class at lineno."""
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
        """Extract docstring content from JSDoc lines."""
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
        """Find function or class declaration node at specific line."""
        if not self._tree_sitter_available:
            return None

        def find_in_node(node):
            """Recursively search for function/class at target line."""
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
        """Extract function call names from a specific function."""
        calls: List[str] = []
        if not self._tree_sitter_available:
            return calls

        def collect_calls(node):
            """Recursively collect call_expression nodes."""
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
        """Extract the name of a called function from a call_expression node."""
        if not call_node or not hasattr(call_node, 'child_by_field_name'):
            return None
        func_node = call_node.child_by_field_name('function')
        if not func_node:
            return None
        start = func_node.start_byte
        end = func_node.end_byte
        if 0 <= start < end <= len(source.encode('utf-8')):
            try:
                name = source[start:end]
                return name.strip() if name else None
            except Exception:
                return None
        return None

    def _extract_imports(self, tree: Any, source: str) -> List[str]:
        """Extract import statements from the module."""
        imports: List[str] = []
        if not self._tree_sitter_available:
            return imports

        def collect_imports(node):
            if not node:
                return
            if node.type in ('import_statement', 'import_clause', 'require_clause'):
                start = node.start_byte
                end = node.end_byte
                if 0 <= start < end <= len(source.encode('utf-8')):
                    try:
                        import_text = source[start:end].strip()
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
        """Check if parse tree contains ERROR or MISSING nodes.

        ERROR nodes indicate parsing failures.
        MISSING nodes indicate incomplete/invalid syntax (e.g., unclosed JSX tags).
        """
        if not tree or not hasattr(tree, 'root_node'):
            return True

        def has_errors(node):
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
