#!/usr/bin/env python3
"""
Google-style docstring formatter (PEP 257 compliant).

"""

from __future__ import annotations

from typing import Optional, List

from agentspec.generators.formatters.base import BaseFormatter
from agentspec.models.agentspec import AgentSpec


class GoogleDocstringFormatter(BaseFormatter):
    """
    Google-style docstring formatter.

        """

    def format(self, spec: AgentSpec) -> str:
        """
        Format AgentSpec as Google-style docstring.

        Args:
            spec: Validated AgentSpec object

        Returns:
            Complete Google-style docstring with triple quotes

        Rationale:
            Builds docstring section by section, following Google style guide.
            Each section is formatted independently, then assembled.

        Guardrails:
            - ALWAYS validate spec before formatting
            - DO NOT skip required sections
            - ALWAYS wrap text to 79 chars
        """
        lines = []

        # Opening triple quotes and summary
        lines.append('"""' + spec.summary)

        # Extended description (if present)
        if spec.description and spec.description.strip():
            lines.append("")  # Blank line after summary
            # Wrap description text
            desc_wrapped = self.wrap_text(spec.description.strip(), width=79)
            lines.append(desc_wrapped)

        # Process standard sections (if present in spec.sections)
        section_order = ["Args", "Returns", "Raises", "Examples", "Notes", "Warnings"]

        for section_name in section_order:
            # Find matching section in spec
            matching_sections = [
                s for s in spec.sections
                if s.title.lower() == section_name.lower()
            ]

            if matching_sections:
                section = matching_sections[0]
                formatted = self.format_section(section.title, section.content, section.items)
                if formatted:
                    lines.append("")  # Blank line before section
                    lines.append(formatted)

        # Rationale section (custom, always include)
        if spec.rationale and spec.rationale.strip():
            lines.append("")
            lines.append(self.format_section("Rationale", spec.rationale))

        # Guardrails section (custom, always include)
        if spec.guardrails:
            lines.append("")
            guardrails_text = "\n".join(f"- {g}" for g in spec.guardrails)
            lines.append(self.format_section("Guardrails", guardrails_text))

        # Dependencies section (custom, optional)
        if spec.dependencies:
            lines.append("")
            dep_lines = []

            if spec.dependencies.calls:
                dep_lines.append("Calls:")
                for call in spec.dependencies.calls:
                    dep_lines.append(f"    - {call}")

            if spec.dependencies.called_by:
                if dep_lines:
                    dep_lines.append("")
                dep_lines.append("Called by:")
                for caller in spec.dependencies.called_by:
                    dep_lines.append(f"    - {caller}")

            if spec.dependencies.imports:
                if dep_lines:
                    dep_lines.append("")
                dep_lines.append("Imports:")
                for imp in spec.dependencies.imports:
                    dep_lines.append(f"    - {imp}")

            if dep_lines:
                lines.append(self.format_section("Dependencies", "\n".join(dep_lines)))

        # Closing triple quotes
        lines.append('"""')

        return "\n".join(lines)

    def format_section(self, name: str, content: str, items: Optional[List[dict]] = None) -> str:
        """
        Format individual section in Google style.

        Args:
            name: Section name (e.g., "Args", "Rationale")
            content: Section content text
            items: Optional structured items (for Args, Raises)

        Returns:
            Formatted section text

        Rationale:
            Google style uses "Section Name:" followed by indented content.
            For structured sections like Args, each item is formatted as:
            "    param_name (type): Description"

        Guardrails:
            - ALWAYS indent content by 4 spaces
            - DO NOT add blank lines within section content
            - ALWAYS wrap text to 75 chars (accounting for indent)
        """
        if not content or not content.strip():
            return ""

        section_lines = [f"{name}:"]

        # Handle structured items (Args, Raises, etc.)
        if items:
            for item in items:
                param_name = item.get("name", "")
                param_type = item.get("type", "")
                param_desc = item.get("description", "")

                if param_type:
                    param_line = f"    {param_name} ({param_type}): {param_desc}"
                else:
                    param_line = f"    {param_name}: {param_desc}"

                # Wrap if too long
                if len(param_line) > 79:
                    wrapped = self.wrap_text(param_desc, width=75, indent=8)
                    param_line = f"    {param_name}" + (f" ({param_type})" if param_type else "") + ":\n" + wrapped

                section_lines.append(param_line)
        else:
            # Handle prose content
            # Indent by 4 spaces
            indented = self.indent_block(content.strip(), spaces=4)
            section_lines.append(indented)

        return "\n".join(section_lines)
