#!/usr/bin/env python3
"""
Exception collector (scans for `raise` statements).

"""

from __future__ import annotations

import ast
from typing import Dict, Any, List

from agentspec.collectors.base import BaseCollector


class ExceptionCollector(BaseCollector):
    """
    Collects raised exceptions from function body.

        """

    @property
    def category(self) -> str:
        """This is a code analysis collector."""
        return "code_analysis"

    def get_priority(self) -> int:
        """Medium priority."""
        return 30

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract raised exceptions from function.

        Args:
            function_node: ast.FunctionDef or ParsedFunction
            context: Not used

        Returns:
            Dict with list of exceptions

        Rationale:
            Walks AST to find all Raise nodes. Extracts exception type
            and message where possible.

        Guardrails:
            - ALWAYS handle bare `raise` (exc=None)
            - DO NOT fail on complex exception expressions
        """
        # Handle ParsedFunction vs AST node
        if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(function_node, "body"):
                # ParsedFunction - parse body string
                try:
                    tree = ast.parse(function_node.body)
                    return self._extract_from_ast(tree)
                except:
                    return {}
            return {}

        return self._extract_from_ast(function_node)

    def _extract_from_ast(self, node: ast.AST) -> Dict[str, Any]:
        """Extract exceptions from AST node."""
        exceptions = []

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Raise):
                exc_info = {
                    "type": None,
                    "message": None,
                    "conditional": False  # TODO: Detect if in if/try block
                }

                # Extract exception type
                if subnode.exc:
                    # Handle `raise ExceptionType(...)`
                    if isinstance(subnode.exc, ast.Call):
                        if isinstance(subnode.exc.func, ast.Name):
                            exc_info["type"] = subnode.exc.func.id
                        elif isinstance(subnode.exc.func, ast.Attribute):
                            exc_info["type"] = ast.unparse(subnode.exc.func)

                        # Try to extract message (first arg if literal string)
                        if subnode.exc.args and isinstance(subnode.exc.args[0], ast.Constant):
                            exc_info["message"] = str(subnode.exc.args[0].value)

                    # Handle `raise ExceptionType`
                    elif isinstance(subnode.exc, ast.Name):
                        exc_info["type"] = subnode.exc.id

                    # Handle `raise module.ExceptionType`
                    elif isinstance(subnode.exc, ast.Attribute):
                        exc_info["type"] = ast.unparse(subnode.exc)

                # Bare `raise` has exc=None
                exceptions.append(exc_info)

        return {"exceptions": exceptions}
