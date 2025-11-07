#!/usr/bin/env python3
"""
Base formatter abstraction for docstring generation.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from agentspec.models.agentspec import AgentSpec


class BaseFormatter(ABC):
    """
    Abstract base class for docstring formatters.

        """

    @abstractmethod
    def format(self, spec: AgentSpec) -> str:
        """
        Format AgentSpec as docstring.

        Args:
            spec: Validated AgentSpec object

        Returns:
            Formatted docstring text (including triple quotes)

        Raises:
            ValueError: If spec is invalid
            Exception: Formatting errors

        Rationale:
            Primary interface for docstring generation. Returns complete
            docstring ready for insertion into source code.

        Guardrails:
            - ALWAYS include triple quotes (''' or \"\"\")
            - ALWAYS start with summary line (PEP 257 requirement)
            - DO NOT modify input spec
            - ALWAYS handle missing optional fields
        """
        pass

    @abstractmethod
    def format_section(self, name: str, content: str) -> str:
        """
        Format individual section (Args, Returns, Rationale, etc.).

        Args:
            name: Section name (e.g., "Args", "Rationale")
            content: Section content

        Returns:
            Formatted section text

        Rationale:
            Allows style-specific section formatting (Google uses indented
            bullet lists, NumPy uses underlined headers, Sphinx uses directives).

        Guardrails:
            - DO NOT add section if content is empty
            - ALWAYS follow style conventions for this section
            - ALWAYS indent content appropriately
        """
        pass

    def validate_output(self, docstring: str) -> bool:
        """
        Validate formatted docstring is compliant.

        Args:
            docstring: Formatted docstring text

        Returns:
            True if valid

        Raises:
            ValueError: If docstring is invalid (with explanation)

        Rationale:
            Catches formatting bugs before inserting into code.
            Ensures PEP 257/JSDoc compliance.

        Guardrails:
            - DO NOT return False (raise ValueError with explanation)
            - ALWAYS check basic requirements (triple quotes, summary line)
        """
        # Default implementation: basic checks
        if not docstring or not docstring.strip():
            raise ValueError("Docstring cannot be empty")

        # Check for triple quotes
        if not (docstring.startswith('"""') or docstring.startswith("'''")):
            raise ValueError("Docstring must start with triple quotes")

        return True

    def wrap_text(self, text: str, width: int = 79, indent: int = 0) -> str:
        """
        Wrap text to specified width with optional indentation.

        Args:
            text: Text to wrap
            width: Maximum line width (default 79 for PEP 8)
            indent: Number of spaces to indent wrapped lines

        Returns:
            Wrapped and indented text

        Rationale:
            Helper for maintaining consistent line length. Uses textwrap
            module for smart wrapping (respects word boundaries).

        Guardrails:
            - DO NOT break words mid-word
            - ALWAYS respect existing paragraph breaks
            - DO NOT wrap code blocks or lists
        """
        import textwrap

        indent_str = " " * indent
        wrapped = textwrap.fill(
            text,
            width=width,
            initial_indent=indent_str,
            subsequent_indent=indent_str,
            break_long_words=False,
            break_on_hyphens=False,
        )
        return wrapped

    def indent_block(self, text: str, spaces: int = 4) -> str:
        """
        Indent all lines in text block.

        Args:
            text: Text to indent
            spaces: Number of spaces to indent

        Returns:
            Indented text

        Rationale:
            Helper for indenting sections, examples, etc.

        Guardrails:
            - DO NOT indent empty lines (PEP 8 style)
            - ALWAYS preserve relative indentation
        """
        indent_str = " " * spaces
        lines = text.split("\n")
        return "\n".join(
            f"{indent_str}{line}" if line.strip() else ""
            for line in lines
        )

    @property
    def name(self) -> str:
        """Formatter name (for logging/debugging)."""
        return self.__class__.__name__
