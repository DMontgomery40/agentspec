#!/usr/bin/env python3
"""
Decorator collector (extracts all decorators applied to function).

---agentspec
what: |
  Extracts all decorators applied to a function.

  **Collected Data:**
  - Decorator names (simple and qualified)
  - Decorator arguments (if any)
  - Decorator call expressions

  **Output Format:**
  ```python
  {
      "decorators": [
          {"name": "lru_cache", "args": ["maxsize=128"], "full": "@lru_cache(maxsize=128)"},
          {"name": "property", "args": [], "full": "@property"},
          {"name": "app.route", "args": ["'/api/users'"], "full": "@app.route('/api/users')"}
      ]
  }
  ```

why: |
  Decorators affect function behavior significantly (caching, routes, etc).
  Extracting them deterministically helps LLMs understand context.

  Important patterns:
  - @lru_cache → caching behavior
  - @app.route → web endpoint
  - @deprecated → function status
  - @timing → performance monitoring

guardrails:
  - DO NOT skip complex decorators (preserve full expression)
  - ALWAYS extract decorator arguments if present
  - DO NOT modify decorator names

deps:
  imports:
    - ast
  calls:
    - ast.unparse
    - BaseCollector.collect
---/agentspec
"""

from __future__ import annotations

import ast
from typing import Dict, Any, List

from agentspec.collectors.base import BaseCollector


class DecoratorCollector(BaseCollector):
    """
    Collects decorators from function definition.

    ---agentspec
    what: |
      Extracts all decorators from function's decorator_list.

      Handles:
      - Simple decorators (@property)
      - Decorators with args (@lru_cache(maxsize=128))
      - Qualified decorators (@app.route('/'))
      - Complex decorator expressions

    why: |
      Decorators provide critical context about function behavior.
      Should be extracted deterministically, not guessed.

    guardrails:
      - DO NOT skip complex decorators
      - ALWAYS preserve full decorator expression
    ---/agentspec
    """

    @property
    def category(self) -> str:
        """This is a code analysis collector."""
        return "code_analysis"

    def get_priority(self) -> int:
        """Medium priority."""
        return 20

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract decorators from function.

        Args:
            function_node: ast.FunctionDef or ParsedFunction
            context: Not used

        Returns:
            Dict with list of decorators

        Rationale:
            Reads decorator_list from AST node. Unpars each decorator
            to get full expression.

        Guardrails:
            - ALWAYS preserve decorator arguments
            - DO NOT simplify qualified names
        """
        # Handle ParsedFunction
        if hasattr(function_node, "decorators"):
            # Already extracted
            return {
                "decorators": [
                    {"name": d, "args": [], "full": f"@{d}"}
                    for d in function_node.decorators
                ]
            }

        # Handle AST node
        if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return {}

        decorators = []

        for dec in function_node.decorator_list:
            dec_info = {
                "name": None,
                "args": [],
                "full": f"@{ast.unparse(dec)}"
            }

            # Extract decorator name
            if isinstance(dec, ast.Name):
                # Simple decorator: @property
                dec_info["name"] = dec.id

            elif isinstance(dec, ast.Attribute):
                # Qualified decorator: @app.route
                dec_info["name"] = ast.unparse(dec)

            elif isinstance(dec, ast.Call):
                # Decorator with args: @lru_cache(maxsize=128)
                if isinstance(dec.func, ast.Name):
                    dec_info["name"] = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    dec_info["name"] = ast.unparse(dec.func)

                # Extract arguments
                dec_info["args"] = [ast.unparse(arg) for arg in dec.args]
                dec_info["args"].extend(
                    f"{kw.arg}={ast.unparse(kw.value)}" for kw in dec.keywords
                )

            decorators.append(dec_info)

        return {"decorators": decorators}
