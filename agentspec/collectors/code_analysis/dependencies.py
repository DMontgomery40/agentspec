#!/usr/bin/env python3
"""
Dependency collector (extracts calls, called_by, imports).

Uses existing logic from agentspec/collect.py.

"""

from __future__ import annotations

import ast
from typing import Dict, Any, List
from pathlib import Path

from agentspec.collectors.base import BaseCollector


def _get_function_calls(node: ast.AST) -> List[str]:
    """
    Extract all function call names from an AST node.

    Returns sorted, deduplicated list of callable names.
    Handles simple calls (func), method calls (obj.method), and chained attributes.

    Integrated from agentspec/collect.py.
    """
    calls: List[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Attribute):
                base = None
                if isinstance(func.value, ast.Name):
                    base = func.value.id
                elif isinstance(func.value, ast.Attribute):
                    base = func.value.attr
                name = f"{base}.{func.attr}" if base else func.attr
                calls.append(name)
            elif isinstance(func, ast.Name):
                calls.append(func.id)
    return sorted({c for c in calls if c})


def _get_module_imports(tree: ast.AST) -> List[str]:
    """
    Extract top-level module imports from an AST tree.

    Returns sorted, deduplicated list of import names.
    Handles both 'import X' and 'from X import Y' statements.

    Integrated from agentspec/collect.py.
    """
    imports: List[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                parts = [p for p in [module, alias.name] if p]
                imports.append(".".join(parts))
    return sorted({i for i in imports if i})


class DependencyCollector(BaseCollector):
    """
    Collects dependency information (imports, calls).

    Integrates proven logic from agentspec/collect.py for deterministic extraction.
    """

    @property
    def category(self) -> str:
        return "code_analysis"

    def get_priority(self) -> int:
        return 15

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract dependencies from function node and module context.

        Args:
            function_node: AST node for the function
            context: Dict containing optional 'file_path' for module imports

        Returns:
            Dict with 'dependencies' containing 'calls' and 'imports' lists
        """
        # Extract function calls from function body
        calls = _get_function_calls(function_node)

        # Extract module imports if file_path available
        imports = []
        file_path = context.get("file_path")
        if file_path and isinstance(file_path, (str, Path)):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)
                imports = _get_module_imports(tree)
            except (OSError, SyntaxError):
                # If file can't be read or parsed, return empty imports
                pass

        return {
            "dependencies": {
                "calls": calls,
                "imports": imports,
            }
        }
