#!/usr/bin/env python3
"""
Python code parser using AST.

"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional, Dict, Any

from agentspec.parsers.base import BaseParser, ParsedFunction, ParsedModule


class PythonParser(BaseParser):
    """
    Python AST-based parser.

        """

    @property
    def supported_extensions(self) -> List[str]:
        """Python file extensions."""
        return [".py", ".pyw"]

    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a Python source file."""
        return file_path.suffix in self.supported_extensions

    def parse_file(self, file_path: Path) -> ParsedModule:
        """
        Parse entire Python file.

        Args:
            file_path: Path to Python source file

        Returns:
            ParsedModule with all functions and classes extracted

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If Python syntax is invalid
            Exception: Other parsing errors

        Rationale:
            Reads file, parses with ast.parse(), walks AST to extract all
            functions and classes. Returns structured representation.

        Guardrails:
            - ALWAYS validate file exists
            - DO NOT suppress SyntaxError (indicates broken code)
            - ALWAYS extract module-level docstring
            - ALWAYS extract top-level imports
        """
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read source code
        source_code = file_path.read_text(encoding="utf-8")

        # Parse with AST
        try:
            tree = ast.parse(source_code, filename=str(file_path))
        except SyntaxError as e:
            raise SyntaxError(
                f"Syntax error in {file_path}:{e.lineno}: {e.msg}"
            ) from e

        # Extract module docstring
        module_docstring = ast.get_docstring(tree)

        # Extract top-level imports
        imports = self._extract_imports(tree)

        # Extract all functions and classes
        functions: List[ParsedFunction] = []
        classes: List[str] = []

        for node in tree.body:
            # Handle function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._parse_function_node(
                    node,
                    source_code=source_code,
                    parent_class=None
                )
                functions.append(func)

            # Handle class definitions
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

                # Extract methods from class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method = self._parse_function_node(
                            item,
                            source_code=source_code,
                            parent_class=node.name
                        )
                        functions.append(method)

        return ParsedModule(
            file_path=file_path,
            language="python",
            functions=functions,
            classes=classes,
            module_docstring=module_docstring,
            imports=imports,
        )

    def parse_function(self, code: str, context: Optional[Dict[str, Any]] = None) -> ParsedFunction:
        """
        Parse single function from code string.

        Args:
            code: Python function source code
            context: Optional context dict (parent_class, etc.)

        Returns:
            ParsedFunction object

        Raises:
            SyntaxError: If code has syntax errors
            ValueError: If code doesn't contain a function

        Rationale:
            Useful for testing and interactive workflows. Wraps code in
            a module, parses, extracts first function.

        Guardrails:
            - ALWAYS validate code contains function definition
            - DO NOT assume code is complete module
        """
        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error: {e.msg}") from e

        # Find first function definition
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent_class = context.get("parent_class") if context else None
                return self._parse_function_node(
                    node,
                    source_code=code,
                    parent_class=parent_class
                )

        raise ValueError("No function definition found in code")

    def _parse_function_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source_code: str,
        parent_class: Optional[str] = None
    ) -> ParsedFunction:
        """
        Convert ast.FunctionDef to ParsedFunction.

        Args:
            node: AST function definition node
            source_code: Full source code (for extracting body)
            parent_class: Parent class name if this is a method

        Returns:
            ParsedFunction object

        Rationale:
            Central conversion logic. Extracts all metadata from AST node
            and constructs ParsedFunction model.

        Guardrails:
            - ALWAYS use ast.get_docstring() (handles triple-quote extraction)
            - ALWAYS use ast.unparse() for signature (preserves types)
            - DO NOT reconstruct signature manually (breaks on complex types)
        """
        # Extract name
        name = node.name

        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Check if private
        is_private = name.startswith("_")

        # Check if method
        is_method = parent_class is not None

        # Extract docstring
        existing_docstring = ast.get_docstring(node)

        # Extract decorators
        decorators = [
            ast.unparse(dec) for dec in node.decorator_list
        ]

        # Reconstruct signature using ast.unparse
        # This preserves type hints correctly
        signature = ast.unparse(node).split("\n")[0]  # First line is signature

        # Extract body (exclude docstring)
        body_nodes = node.body
        # Skip docstring node if present
        if body_nodes and isinstance(body_nodes[0], ast.Expr) and isinstance(body_nodes[0].value, ast.Constant):
            body_nodes = body_nodes[1:]

        # Unparse body
        body = "\n".join(ast.unparse(n) for n in body_nodes) if body_nodes else ""

        # Extract function calls
        calls = self._extract_function_calls(node)

        # Line numbers
        line_number = node.lineno
        end_line_number = node.end_lineno or line_number

        return ParsedFunction(
            name=name,
            signature=signature,
            body=body,
            existing_docstring=existing_docstring,
            line_number=line_number,
            end_line_number=end_line_number,
            decorators=decorators,
            is_async=is_async,
            is_method=is_method,
            is_private=is_private,
            parent_class=parent_class,
            calls=calls,
        )

    def _extract_function_calls(self, node: ast.AST) -> List[str]:
        """
        Extract all function call names from AST node.

        Args:
            node: AST node to analyze

        Returns:
            Sorted, deduplicated list of function call names

        Rationale:
            Walks AST to find all ast.Call nodes. Handles:
            - Simple calls: foo()
            - Method calls: obj.method()
            - Chained calls: obj.attr.method()

            Returns sorted list for deterministic output.

        Guardrails:
            - DO NOT remove isinstance checks (distinguish node types)
            - DO NOT modify ast.walk traversal (visits all nested nodes)
            - ALWAYS filter empty strings
            - ALWAYS deduplicate (use set)

        Implementation:
            This is extracted from the existing collect.py _get_function_calls()
            logic, with minimal changes for integration.
        """
        calls: List[str] = []

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                func = sub.func

                # Handle method calls (obj.method)
                if isinstance(func, ast.Attribute):
                    base = None
                    if isinstance(func.value, ast.Name):
                        base = func.value.id
                    elif isinstance(func.value, ast.Attribute):
                        base = func.value.attr

                    name = f"{base}.{func.attr}" if base else func.attr
                    calls.append(name)

                # Handle simple calls (foo)
                elif isinstance(func, ast.Name):
                    calls.append(func.id)

        # Return sorted, deduplicated list
        return sorted({c for c in calls if c})

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """
        Extract all top-level imports from module.

        Args:
            tree: AST module tree

        Returns:
            List of import statements as strings

        Rationale:
            Walks AST to find Import and ImportFrom nodes. Reconstructs
            import statements for dependency tracking.

        Guardrails:
            - DO NOT extract imports from function bodies (only top-level)
            - ALWAYS preserve "from X import Y" format
            - ALWAYS preserve "import X as Y" format
        """
        imports: List[str] = []

        # Only walk top-level nodes (not nested functions)
        for node in tree.body:
            # import X, Y, Z
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        imports.append(f"{alias.name} as {alias.asname}")
                    else:
                        imports.append(alias.name)

            # from X import Y, Z
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if alias.asname:
                        imports.append(f"{module}.{alias.name} as {alias.asname}")
                    else:
                        imports.append(f"{module}.{alias.name}")

        return imports
