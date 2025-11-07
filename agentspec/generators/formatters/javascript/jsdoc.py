#!/usr/bin/env python3
"""
JSDoc formatter for JavaScript (JSDoc 3 compliant).

"""

from __future__ import annotations

from typing import Optional, List

from agentspec.generators.formatters.base import BaseFormatter
from agentspec.models.agentspec import AgentSpec


class JSDocFormatter(BaseFormatter):
    """
    JSDoc formatter for JavaScript.

    NOTE: This is a stub implementation for architecture completeness.
    Full JSDoc support requires JavaScript parser integration (tree-sitter).
    """

    def format(self, spec: AgentSpec) -> str:
        """Format AgentSpec as JSDoc comment."""
        lines = []

        # Opening /**
        lines.append("/**")

        # Summary
        lines.append(f" * {spec.summary}")

        # Extended description
        if spec.description:
            lines.append(" *")
            for line in spec.description.strip().split("\n"):
                lines.append(f" * {line}")

        # Parameters
        for section in spec.sections:
            if section.title.lower() == "args" and section.items:
                lines.append(" *")
                for item in section.items:
                    name = item.get("name", "")
                    param_type = item.get("type", "any")
                    desc = item.get("description", "")
                    lines.append(f" * @param {{{param_type}}} {name} - {desc}")

        # Returns
        returns_sections = [s for s in spec.sections if s.title.lower() == "returns"]
        if returns_sections:
            lines.append(f" * @returns {{Object}} {returns_sections[0].content}")

        # Rationale (custom)
        if spec.rationale:
            lines.append(" *")
            lines.append(" * Rationale:")
            for line in spec.rationale.strip().split("\n"):
                lines.append(f" * {line}")

        # Guardrails (custom)
        if spec.guardrails:
            lines.append(" *")
            lines.append(" * Guardrails:")
            for g in spec.guardrails:
                lines.append(f" * - {g}")

        # Closing */
        lines.append(" */")

        return "\n".join(lines)

    def format_section(self, name: str, content: str, items: Optional[List[dict]] = None) -> str:
        """Format individual section (stub implementation)."""
        return f" * {name}:\n * {content}"
