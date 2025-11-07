#!/usr/bin/env python3
"""
Base parser abstraction for code analysis.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ParsedFunction(BaseModel):
    """
    Represents a parsed function/method with metadata.

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
