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
        Return Python file extensions this adapter handles.
        """
        return {'.py', '.pyi'}

    def discover_files(self, target: Path) -> List[Path]:
        """
        Discover all Python files in target directory or return single file.
        
        Delegates to agentspec.utils.collect_python_files() which respects
        .gitignore and excludes common directories (.venv, __pycache__, etc).
        """
        # Import here to avoid circular dependencies
        from agentspec.utils import collect_python_files
        return collect_python_files(target)

    def extract_docstring(self, filepath: Path, lineno: int) -> Optional[str]:
        """
        Extract docstring from function/class at lineno in filepath.
        
        Returns the raw docstring including any agentspec blocks, or None.
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
        Insert or replace docstring for function/class at lineno in filepath.
        
        Handles proper indentation and preservation of function body.
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
        Extract function calls, imports, and other metadata for a function.
        
        Returns dict with 'calls', 'imports', and 'called_by' keys.
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
        Check if file has valid Python syntax.

        Returns True if valid, raises SyntaxError if invalid.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), str(filepath), 'exec')
            return True
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {filepath}: {e}")

    def validate_syntax_string(self, source: str, filepath: Path = None) -> bool:
        """
        Validate Python syntax string.

        Returns True if valid, raises ValueError if invalid.
        """
        try:
            compile(source, str(filepath) if filepath else '<string>', 'exec')
            return True
        except SyntaxError as e:
            raise ValueError(f"Syntax error: {e}")

    def get_comment_delimiters(self) -> tuple[str, str]:
        """
        Return Python multi-line string delimiters.
        """
        triple_quote = chr(34) * 3
        return (triple_quote, triple_quote)

    def parse(self, source_code: str) -> ast.Module:
        """
        Parse Python source code into an AST.
        """
        return ast.parse(source_code)


def _get_indent(node: ast.AST) -> str:
    """
    Get indentation string for an AST node.
    
    Returns the indentation level as a string of spaces.
    """
    # For a function/class definition, we need to determine its indent level
    # This is a simplified version; the real implementation would calculate
    # based on the source file content
    col_offset = getattr(node, 'col_offset', 0)
    return ' ' * col_offset
