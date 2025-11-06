#!/usr/bin/env python3
"""
Google-style docstring formatter (PEP 257 compliant).

---agentspec
what: |
  Formats AgentSpec objects as Google-style Python docstrings.

  **Google Style Features:**
  - One-line summary followed by blank line
  - Extended description (optional)
  - Sections with labels followed by colon
  - Indented content under each section
  - Blank lines between sections

  **Standard Sections:**
  - Args: Function arguments with types and descriptions
  - Returns: Return value description
  - Raises: Exceptions that may be raised
  - Examples: Usage examples
  - Notes: Additional notes

  **Custom Agent Sections:**
  - Rationale: Why this implementation (replaces old "why")
  - Guardrails: What NOT to change (critical for AI safety)
  - Dependencies: What this code calls and what calls it

  **Example Output:**
  ```python
  \"\"\"Process user input and return validated data.

  Takes raw user input, validates format, sanitizes content,
  and returns structured data ready for database insertion.

  Args:
      input_data: Raw input dictionary from form
      strict: If True, raise on validation errors instead of warnings

  Returns:
      Validated and sanitized data dictionary

  Raises:
      ValueError: If input_data is malformed and strict=True

  Rationale:
      Using dict instead of Pydantic model here because we need
      to preserve unknown fields for audit logging. Pydantic
      would silently drop them.

  Guardrails:
      - DO NOT remove sanitization step (XSS vulnerability)
      - DO NOT make strict=True the default (breaks existing callers)
  \"\"\"
  ```

why: |
  Google style is the most popular Python docstring format:
  - Best IDE support (VSCode, PyCharm recognize it)
  - Most readable (clear section labels, simple formatting)
  - Widely adopted (Google, Uber, many open source projects)
  - Works well with Sphinx (using napoleon extension)

  Adding custom sections (Rationale, Guardrails) as regular sections
  maintains 100% PEP 257 compliance while encoding agent-critical info.

guardrails:
  - DO NOT change section names without updating LLM prompts
  - ALWAYS start with one-line summary (PEP 257 requirement)
  - ALWAYS include blank line after summary (PEP 257 requirement)
  - DO NOT skip Rationale or Guardrails sections (core value)

deps:
  imports:
    - typing
  calls:
    - BaseFormatter.__init__
    - AgentSpec (model validation)
---/agentspec
"""

from __future__ import annotations

from typing import Optional, List

from agentspec.generators.formatters.base import BaseFormatter
from agentspec.models.agentspec import AgentSpec


class GoogleDocstringFormatter(BaseFormatter):
    """
    Google-style docstring formatter.

    ---agentspec
    what: |
      Implements BaseFormatter for Google-style Python docstrings.

      **Formatting Rules:**
      1. Start with triple quotes (\"\"\")
      2. One-line summary (no period at end)
      3. Blank line
      4. Extended description (if present)
      5. Blank line before first section
      6. Sections in order: Args, Returns, Raises, Examples, Rationale, Guardrails, Dependencies
      7. Each section: "Name:" followed by indented content
      8. Close with triple quotes

      **Text Wrapping:**
      - Summary: max 79 chars
      - Description: wrapped at 79 chars
      - Section content: wrapped at 75 chars (4-space indent)

    why: |
      Google style provides clear visual hierarchy and good readability.
      Section-based format makes it easy for both humans and tools to parse.

    guardrails:
      - DO NOT reorder sections without team discussion (standardization)
      - ALWAYS include Rationale and Guardrails (even if short)
      - DO NOT wrap code examples (breaks syntax)
    ---/agentspec
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
