#!/usr/bin/env python3
"""
Sphinx-style docstring formatter (reStructuredText).

---agentspec
what: |
  Formats AgentSpec objects as Sphinx-style reStructuredText docstrings.

  **Sphinx Style Features:**
  - Uses reStructuredText directives (:param:, :returns:, etc.)
  - Integrates seamlessly with Sphinx documentation generator
  - Supports cross-references and rich formatting
  - Popular in larger Python projects (Django, Flask, Requests)

  **Example Output:**
  ```python
  \"\"\"Process user input and return validated data.

  Takes raw user input, validates format, sanitizes content,
  and returns structured data ready for database insertion.

  :param input_data: Raw input dictionary from form
  :type input_data: dict
  :param strict: If True, raise on validation errors
  :type strict: bool
  :returns: Validated and sanitized data dictionary
  :rtype: dict
  :raises ValueError: If input_data is malformed and strict=True

  .. rubric:: Rationale

  Using dict instead of Pydantic model here because we need
  to preserve unknown fields for audit logging.

  .. rubric:: Guardrails

  - DO NOT remove sanitization step (XSS vulnerability)
  - DO NOT make strict=True the default (breaks existing callers)
  \"\"\"
  ```

why: |
  Sphinx style integrates best with Sphinx documentation tools.
  Preferred for projects that generate extensive API documentation.
  Supports advanced features like cross-references.

guardrails:
  - DO NOT change directive names (:param:, :returns:, etc.)
  - ALWAYS use .. rubric:: for custom sections
  - ALWAYS include :type: after :param: (Sphinx convention)

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


class SphinxDocstringFormatter(BaseFormatter):
    """Sphinx-style docstring formatter."""

    def format(self, spec: AgentSpec) -> str:
        """Format AgentSpec as Sphinx-style docstring."""
        lines = []

        # Opening and summary
        lines.append('"""' + spec.summary)

        # Extended description
        if spec.description and spec.description.strip():
            lines.append("")
            lines.append(self.wrap_text(spec.description.strip(), width=79))

        # Process sections using Sphinx directives
        for section in spec.sections:
            title_lower = section.title.lower()

            if title_lower == "args" and section.items:
                # Parameters as :param: directives
                lines.append("")
                for item in section.items:
                    name = item.get("name", "")
                    param_type = item.get("type", "")
                    desc = item.get("description", "")

                    lines.append(f":param {name}: {desc}")
                    if param_type:
                        lines.append(f":type {name}: {param_type}")

            elif title_lower == "returns":
                lines.append("")
                lines.append(f":returns: {section.content}")
                # TODO: Extract return type if present

            elif title_lower == "raises" and section.items:
                lines.append("")
                for item in section.items:
                    exc_type = item.get("name", "")
                    desc = item.get("description", "")
                    lines.append(f":raises {exc_type}: {desc}")

        # Custom sections with .. rubric::
        if spec.rationale:
            lines.append("")
            lines.append(".. rubric:: Rationale")
            lines.append("")
            lines.append(spec.rationale.strip())

        if spec.guardrails:
            lines.append("")
            lines.append(".. rubric:: Guardrails")
            lines.append("")
            for g in spec.guardrails:
                lines.append(f"- {g}")

        if spec.dependencies:
            lines.append("")
            lines.append(".. rubric:: Dependencies")
            lines.append("")
            if spec.dependencies.calls:
                lines.append("Calls:")
                for c in spec.dependencies.calls:
                    lines.append(f"    - {c}")
            if spec.dependencies.called_by:
                lines.append("")
                lines.append("Called by:")
                for c in spec.dependencies.called_by:
                    lines.append(f"    - {c}")

        lines.append('"""')
        return "\n".join(lines)

    def format_section(self, name: str, content: str, items: Optional[List[dict]] = None) -> str:
        """Format section with Sphinx directives (not used in main flow, but required by ABC)."""
        if not content:
            return ""
        return f".. rubric:: {name}\n\n{content}"
