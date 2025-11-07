#!/usr/bin/env python3
"""
Result models for agentspec operations.

"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """
    Result of validating an AgentSpec.

        """
    valid: bool = Field(
        description="True if spec passes all validation checks"
    )

    errors: List[str] = Field(
        default_factory=list,
        description="Validation error messages"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Validation warning messages"
    )

    spec: Optional[Any] = Field(
        default=None,
        description="The validated AgentSpec (if valid)"
    )


class GenerationResult(BaseModel):
    """
    Result of generating docstrings for a code entity.

        """
    success: bool = Field(
        description="True if generation completed without errors"
    )

    function_name: str = Field(
        description="Name of the function/class processed"
    )

    file_path: Path = Field(
        description="Path to the file containing the entity"
    )

    original_code: str = Field(
        default="",
        description="Original code before modification"
    )

    generated_docstring: str = Field(
        default="",
        description="The generated docstring text"
    )

    modified_code: str = Field(
        default="",
        description="Code after docstring insertion"
    )

    messages: List[str] = Field(
        default_factory=list,
        description="Informational messages"
    )

    errors: List[str] = Field(
        default_factory=list,
        description="Error messages"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Warning messages"
    )

    dry_run: bool = Field(
        default=False,
        description="True if this was a dry run"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (timing, LLM calls, etc.)"
    )


class LintResult(BaseModel):
    """
    Result of linting a file for agentspec compliance.

        """
    success: bool = Field(
        description="True if no errors (warnings OK unless strict mode)"
    )

    file_path: Path = Field(
        description="Path to the linted file"
    )

    total_functions: int = Field(
        default=0,
        ge=0,
        description="Number of functions/classes checked"
    )

    functions_with_specs: int = Field(
        default=0,
        ge=0,
        description="Number with agentspec docstrings"
    )

    functions_without_specs: int = Field(
        default=0,
        ge=0,
        description="Number missing docstrings"
    )

    errors: List[str] = Field(
        default_factory=list,
        description="Error messages"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Warning messages"
    )

    strict: bool = Field(
        default=False,
        description="True if strict mode enabled"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
