#!/usr/bin/env python3
"""
Complexity metrics collector (cyclomatic complexity, LOC, etc).
"""

from __future__ import annotations

import ast
from typing import Dict, Any

from agentspec.collectors.base import BaseCollector


class ComplexityCollector(BaseCollector):
    """
    Collects code complexity metrics.

    Metrics:
    - Lines of code (LOC)
    - Cyclomatic complexity
    - Nesting depth
    - Number of branches
    """

    @property
    def category(self) -> str:
        return "code_analysis"

    def get_priority(self) -> int:
        return 40

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate complexity metrics."""
        if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return {}

        # Count lines of code
        start_line = function_node.lineno
        end_line = getattr(function_node, "end_lineno", start_line)
        loc = end_line - start_line + 1

        # Simple cyclomatic complexity (count decision points)
        complexity = 1  # Base complexity
        for node in ast.walk(function_node):
            # Each branch adds to complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return {
            "complexity": {
                "lines_of_code": loc,
                "cyclomatic_complexity": complexity,
                "note": "Full complexity analysis (nesting, branches) to be added"
            }
        }
