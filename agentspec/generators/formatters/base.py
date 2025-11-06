#!/usr/bin/env python3
"""
Base formatter abstraction for docstring generation.

---agentspec
what: |
  Abstract base class defining the interface all docstring formatters must implement.

  **Core Interface:**
  - format(spec) → str: Convert AgentSpec to formatted docstring
  - format_section(name, content) → str: Format individual section
  - validate_output(docstring) → bool: Check output is valid

  **What Formatters Do:**
  - Convert structured AgentSpec (Pydantic model) to text docstring
  - Apply style-specific formatting (Google vs NumPy vs Sphinx vs JSDoc)
  - Ensure output is PEP 257 compliant (Python) or JSDoc compliant (JS/TS)
  - Handle custom sections (Rationale, Guardrails, Dependencies)
  - Wrap text to appropriate line length (79 chars for Python)

  Formatters are stateless and reusable - create once, call format() many times.

why: |
  Abstracting formatting logic enables:
  - Multiple output styles from same AgentSpec
  - Consistent formatting rules across all generators
  - Easy testing (mock formatter for unit tests)
  - User choice (pick preferred style)

  Separating formatting from generation (LLM logic) improves:
  - Testability (can test formatting without LLM calls)
  - Maintainability (formatting rules in one place)
  - Extensibility (new styles just implement this interface)

guardrails:
  - DO NOT add style-specific logic to base class
  - ALWAYS ensure output is PEP 257/JSDoc compliant
  - DO NOT modify AgentSpec in formatters (read-only)
  - ALWAYS handle missing optional fields gracefully

deps:
  imports:
    - abc
    - typing
  calls:
    - AgentSpec (from models)
---/agentspec
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from agentspec.models.agentspec import AgentSpec


class BaseFormatter(ABC):
    """
    Abstract base class for docstring formatters.

    ---agentspec
    what: |
      Defines the contract all docstring formatters must implement.

      **Required Methods:**
      - format(spec) → str: Main formatting method
      - format_section(name, content) → str: Format individual section
      - validate_output(docstring) → bool: Validate output

      **Optional Overrides:**
      - wrap_text(text, width) → str: Text wrapping logic
      - indent(text, spaces) → str: Indentation logic

      Formatters should:
      - Be stateless (no instance state between format() calls)
      - Handle missing optional fields gracefully
      - Produce PEP 257 or JSDoc compliant output
      - Wrap text to appropriate line length

    why: |
      ABC ensures all formatters implement consistent interface.
      Polymorphic usage enables swapping formatters without code changes.

    guardrails:
      - DO NOT maintain state between format() calls
      - ALWAYS validate AgentSpec before formatting
      - DO NOT modify input AgentSpec (read-only)
      - ALWAYS produce spec-compliant output
    ---/agentspec
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
