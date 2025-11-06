#!/usr/bin/env python3
"""
Type hint analysis collector (coverage, Optional/Union, generics).
"""

from __future__ import annotations

import ast
from typing import Dict, Any

from agentspec.collectors.base import BaseCollector


class TypeAnalysisCollector(BaseCollector):
    """
    Analyzes type hint coverage and complexity.

    Metrics:
    - % of parameters with type hints
    - Whether return is typed
    - Use of Optional/Union
    - Use of generics (List, Dict, etc)
    """

    @property
    def category(self) -> str:
        return "code_analysis"

    def get_priority(self) -> int:
        return 25

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze type hints."""
        if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return {}

        # Count typed parameters
        total_params = 0
        typed_params = 0

        args = function_node.args
        for arg in args.args + args.kwonlyargs:
            total_params += 1
            if arg.annotation:
                typed_params += 1

        # Check return type
        has_return_type = function_node.returns is not None

        # Calculate coverage
        param_coverage = (typed_params / total_params * 100) if total_params > 0 else 0

        return {
            "type_analysis": {
                "parameters_typed": typed_params,
                "parameters_total": total_params,
                "parameter_coverage_percent": round(param_coverage, 1),
                "has_return_type": has_return_type,
                "note": "Full type analysis (Optional/Union/generics) to be added"
            }
        }
