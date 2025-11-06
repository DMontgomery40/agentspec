#!/usr/bin/env python3
"""
Base parser abstraction for code analysis.

---agentspec
what: |
  Abstract base class and data models for language-agnostic code parsing.

  **Core Models:**
  - ParsedFunction: Represents a parsed function/method with metadata
  - ParsedModule: Represents a parsed file/module with all its functions
  - BaseParser: Abstract interface all language parsers must implement

  **What Parsers Extract:**
  - Function/class names and signatures
  - Existing docstrings (if any)
  - Function bodies (for dependency analysis)
  - Imports/dependencies
  - Line numbers (for error reporting)
  - Decorators (Python) / Annotations (TS)

  Parsers are stateless and reusable - create once, call parse() many times.

why: |
  Abstracting parsing logic enables:
  - Multi-language support (Python, JavaScript, TypeScript)
  - Swappable parsing backends (ast vs tree-sitter)
  - Consistent data model across all languages
  - Easy testing (mock parser for unit tests)

  Data classes (ParsedFunction, ParsedModule) provide type-safe intermediate
  representation that decouples parsing from generation/formatting.

guardrails:
  - DO NOT add language-specific logic to base classes
  - ALWAYS preserve original code in ParsedFunction (needed for diffs)
  - DO NOT make existing_docstring required (many functions lack docstrings)
  - ALWAYS include line numbers (critical for error reporting)

deps:
  imports:
    - abc
    - typing
    - pydantic
    - pathlib
---/agentspec
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ParsedFunction(BaseModel):
    """
    Represents a parsed function/method with metadata.

    ---agentspec
    what: |
      Intermediate representation of a function extracted from source code.

      **Core Fields:**
      - name: Function name (e.g., "process_data")
      - signature: Full signature (e.g., "def process_data(x: int) -> str:")
      - body: Function body code (for dependency analysis)
      - existing_docstring: Current docstring if present (None if missing)
      - line_number: Starting line number in source file
      - end_line_number: Ending line number in source file

      **Metadata:**
      - decorators: List of decorator names (Python) or annotations (TS)
      - is_async: True if async function
      - is_method: True if class method
      - is_private: True if private (starts with _)
      - parent_class: Class name if this is a method

      **Dependencies:**
      - calls: Functions this function calls
      - imports: Modules this function imports/requires

      Used by generators to understand function context and by formatters to
      reconstruct code with new docstrings.

    why: |
      Structured representation enables:
      - Language-agnostic processing (same model for Python/JS/TS)
      - Easy metadata access (no re-parsing)
      - Clear contracts between parser → generator → formatter

      Including both original body and line numbers supports:
      - Dependency analysis (parse calls from body)
      - Error reporting (show line numbers in errors)
      - Code reconstruction (insert docstring at correct line)

    guardrails:
      - DO NOT make existing_docstring required (many functions lack docstrings)
      - ALWAYS preserve original body text (needed for diffs)
      - DO NOT modify body during parsing (keep it exactly as source)
      - ALWAYS include line_number and end_line_number (critical for updates)
    ---/agentspec
    """
    # Core identification
    name: str = Field(
        description="Function/method name"
    )

    signature: str = Field(
        description="Full function signature with types"
    )

    body: str = Field(
        description="Function body code (for dependency analysis)"
    )

    existing_docstring: Optional[str] = Field(
        default=None,
        description="Existing docstring if present"
    )

    # Location information
    line_number: int = Field(
        ge=1,
        description="Starting line number in source file"
    )

    end_line_number: int = Field(
        ge=1,
        description="Ending line number in source file"
    )

    # Metadata
    decorators: List[str] = Field(
        default_factory=list,
        description="Decorator names (Python) or annotations (TS)"
    )

    is_async: bool = Field(
        default=False,
        description="True if async function"
    )

    is_method: bool = Field(
        default=False,
        description="True if class method"
    )

    is_private: bool = Field(
        default=False,
        description="True if private (starts with _)"
    )

    parent_class: Optional[str] = Field(
        default=None,
        description="Class name if this is a method"
    )

    # Dependencies (populated by parser or collector)
    calls: List[str] = Field(
        default_factory=list,
        description="Functions this function calls"
    )

    imports: List[str] = Field(
        default_factory=list,
        description="Modules imported in this function"
    )

    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional language-specific metadata"
    )


class ParsedModule(BaseModel):
    """
    Represents a parsed module/file with all its functions.

    ---agentspec
    what: |
      Intermediate representation of an entire source file.

      **Contents:**
      - file_path: Path to source file
      - language: Programming language (python, javascript, typescript)
      - functions: List of ParsedFunction objects
      - classes: List of class names defined in module
      - module_docstring: Module-level docstring if present
      - imports: Top-level imports

      Used by generators to process all functions in a file and by
      extractors to export documentation for entire modules.

    why: |
      Module-level representation enables:
      - Batch processing (generate docstrings for all functions)
      - Dependency tracking (see all imports and calls)
      - Complete file reconstruction (preserve structure)

    guardrails:
      - ALWAYS include file_path (needed for error reporting)
      - DO NOT filter out private functions (user decides what to document)
      - ALWAYS preserve import order (semantic in some cases)
    ---/agentspec
    """
    file_path: Path = Field(
        description="Path to source file"
    )

    language: str = Field(
        description="Programming language (python, javascript, typescript)"
    )

    functions: List[ParsedFunction] = Field(
        default_factory=list,
        description="All functions/methods in module"
    )

    classes: List[str] = Field(
        default_factory=list,
        description="Class names defined in module"
    )

    module_docstring: Optional[str] = Field(
        default=None,
        description="Module-level docstring if present"
    )

    imports: List[str] = Field(
        default_factory=list,
        description="Top-level imports"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class BaseParser(ABC):
    """
    Abstract base class for language parsers.

    ---agentspec
    what: |
      Defines the interface all language parsers must implement.

      **Required Methods:**
      - parse_file(file_path) → ParsedModule: Parse entire file
      - parse_function(code) → ParsedFunction: Parse single function
      - can_parse(file_path) → bool: Check if parser supports this file

      **Lifecycle:**
      1. Create parser instance (stateless, reusable)
      2. Call can_parse() to check compatibility
      3. Call parse_file() to extract all functions
      4. Access ParsedModule.functions for processing

      Parsers should be stateless and thread-safe where possible.

    why: |
      ABC ensures consistent interface across all language parsers,
      enabling polymorphic usage (same code works with Python/JS/TS parsers).

      Stateless design allows reuse and parallel processing.

    guardrails:
      - DO NOT maintain state between parse calls (parsers should be stateless)
      - ALWAYS raise descriptive exceptions on parse failures
      - DO NOT swallow syntax errors (let them propagate)
    ---/agentspec
    """

    @abstractmethod
    def parse_file(self, file_path: Path) -> ParsedModule:
        """
        Parse entire source file into ParsedModule.

        Args:
            file_path: Path to source file

        Returns:
            ParsedModule with all functions extracted

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
            Exception: Other parsing failures

        Rationale:
            Primary interface for file-level parsing. Returns complete
            structured representation for downstream processing.

        Guardrails:
            - ALWAYS validate file exists before parsing
            - DO NOT suppress syntax errors (they indicate broken code)
            - ALWAYS populate line numbers for error reporting
        """
        pass

    @abstractmethod
    def parse_function(self, code: str, context: Optional[Dict[str, Any]] = None) -> ParsedFunction:
        """
        Parse single function from code string.

        Args:
            code: Function source code
            context: Optional context (file path, parent class, etc.)

        Returns:
            ParsedFunction object

        Raises:
            SyntaxError: If code has syntax errors
            ValueError: If code doesn't contain a function
            Exception: Other parsing failures

        Rationale:
            Useful for parsing code snippets in tests or interactive workflows.
            Context parameter provides file/class information when available.

        Guardrails:
            - ALWAYS validate code contains a function definition
            - DO NOT assume code is a complete module (may be snippet)
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if parser can handle this file.

        Args:
            file_path: Path to check

        Returns:
            True if parser supports this file type

        Rationale:
            Enables automatic parser selection based on file extension.
            Cleaner than try/except around parse_file().

        Guardrails:
            - DO NOT check file contents (just extension/metadata)
            - ALWAYS return bool (don't raise exceptions)
        """
        pass

    @property
    def supported_extensions(self) -> List[str]:
        """
        List of file extensions this parser supports.

        Returns:
            List of extensions (e.g., ['.py', '.pyw'])
        """
        return []
