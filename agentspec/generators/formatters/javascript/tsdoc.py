#!/usr/bin/env python3
"""
TSDoc formatter for TypeScript (Microsoft TSDoc standard).

---agentspec
what: |
  Formats AgentSpec objects as TSDoc comments for TypeScript.

  TSDoc extends JSDoc with additional TypeScript-specific features.
  Standardized by Microsoft, used in TypeScript compiler and VS Code.

  **Example:**
  ```typescript
  /**
   * Process user input and return validated data.
   *
   * @param inputData - Raw input from form
   * @param strict - If true, raise on errors
   * @returns Validated data object
   *
   * @remarks
   * Using plain objects instead of interfaces here because we need
   * to preserve unknown fields for audit logging.
   */
  ```

why: |
  TSDoc is the preferred format for TypeScript projects.
  Better type integration than JSDoc for TypeScript code.

guardrails:
  - DO NOT use JSDoc-only tags (@typedef, @callback, etc.)
  - ALWAYS use @remarks for extended descriptions (TSDoc convention)
  - DO NOT duplicate type info (TypeScript has static types)

deps:
  imports:
    - typing
  calls:
    - BaseFormatter.format
---/agentspec
"""

from __future__ import annotations

from typing import Optional, List

from agentspec.generators.formatters.base import BaseFormatter
from agentspec.models.agentspec import AgentSpec


class TSDocFormatter(BaseFormatter):
    """
    TSDoc formatter for TypeScript.

    NOTE: This is a stub implementation for architecture completeness.
    Full TSDoc support requires TypeScript parser integration (tree-sitter).
    """

    def format(self, spec: AgentSpec) -> str:
        """Format AgentSpec as TSDoc comment."""
        lines = []

        lines.append("/**")
        lines.append(f" * {spec.summary}")

        if spec.description:
            lines.append(" *")
            lines.append(" * @remarks")
            for line in spec.description.strip().split("\n"):
                lines.append(f" * {line}")

        # Parameters (TypeScript has types, so no type annotations needed)
        for section in spec.sections:
            if section.title.lower() == "args" and section.items:
                lines.append(" *")
                for item in section.items:
                    name = item.get("name", "")
                    desc = item.get("description", "")
                    lines.append(f" * @param {name} - {desc}")

        # Returns
        returns_sections = [s for s in spec.sections if s.title.lower() == "returns"]
        if returns_sections:
            lines.append(f" * @returns {returns_sections[0].content}")

        # Custom sections
        if spec.rationale:
            lines.append(" *")
            lines.append(" * @remarks Rationale")
            for line in spec.rationale.strip().split("\n"):
                lines.append(f" * {line}")

        if spec.guardrails:
            lines.append(" *")
            lines.append(" * @remarks Guardrails")
            for g in spec.guardrails:
                lines.append(f" * - {g}")

        lines.append(" */")
        return "\n".join(lines)

    def format_section(self, name: str, content: str, items: Optional[List[dict]] = None) -> str:
        """Format individual section (stub implementation)."""
        return f" * {name}:\n * {content}"
