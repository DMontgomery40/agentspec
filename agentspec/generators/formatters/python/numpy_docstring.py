#!/usr/bin/env python3
"""
NumPy-style docstring formatter (PEP 257 compliant).

"""

from __future__ import annotations

from typing import Optional, List

from agentspec.generators.formatters.base import BaseFormatter
from agentspec.models.agentspec import AgentSpec


class NumpyDocstringFormatter(BaseFormatter):
    """NumPy-style docstring formatter."""

    def format(self, spec: AgentSpec) -> str:
        """Format AgentSpec as NumPy-style docstring."""
        lines = []

        # Opening and summary
        lines.append('"""' + spec.summary)

        # Extended description
        if spec.description and spec.description.strip():
            lines.append("")
            lines.append(self.wrap_text(spec.description.strip(), width=79))

        # Process sections
        section_mapping = {
            "Args": "Parameters",  # NumPy uses Parameters
            "Returns": "Returns",
            "Raises": "Raises",
            "Examples": "Examples",
            "Notes": "Notes",
            "Warnings": "Warnings",
        }

        for old_name, new_name in section_mapping.items():
            matching = [s for s in spec.sections if s.title.lower() == old_name.lower()]
            if matching:
                section = matching[0]
                formatted = self.format_section(new_name, section.content, section.items)
                if formatted:
                    lines.append("")
                    lines.append(formatted)

        # Custom sections
        if spec.rationale:
            lines.append("")
            lines.append(self.format_section("Rationale", spec.rationale))

        if spec.guardrails:
            lines.append("")
            guardrails_text = "\n".join(f"- {g}" for g in spec.guardrails)
            lines.append(self.format_section("Guardrails", guardrails_text))

        if spec.dependencies:
            lines.append("")
            dep_lines = []
            if spec.dependencies.calls:
                dep_lines.append("Calls:")
                dep_lines.extend(f"    - {c}" for c in spec.dependencies.calls)
            if spec.dependencies.called_by:
                if dep_lines:
                    dep_lines.append("")
                dep_lines.append("Called by:")
                dep_lines.extend(f"    - {c}" for c in spec.dependencies.called_by)
            if dep_lines:
                lines.append(self.format_section("Dependencies", "\n".join(dep_lines)))

        lines.append('"""')
        return "\n".join(lines)

    def format_section(self, name: str, content: str, items: Optional[List[dict]] = None) -> str:
        """
        Format section with NumPy-style underlined header.

        NumPy style uses:
        Section Name
        ------------
        Content here
        """
        if not content or not content.strip():
            return ""

        section_lines = [name]
        section_lines.append("-" * len(name))  # Underline with dashes

        if items:
            # Structured items (Parameters, Raises)
            for item in items:
                param_name = item.get("name", "")
                param_type = item.get("type", "")
                param_desc = item.get("description", "")

                # NumPy format: "name : type\n    Description"
                if param_type:
                    section_lines.append(f"{param_name} : {param_type}")
                else:
                    section_lines.append(param_name)

                # Indent description
                desc_indented = self.indent_block(param_desc, spaces=4)
                section_lines.append(desc_indented)
        else:
            # Prose content
            section_lines.append(content.strip())

        return "\n".join(section_lines)
