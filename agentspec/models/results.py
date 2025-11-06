#!/usr/bin/env python3
"""
Result models for agentspec operations.

---agentspec
what: |
  Pydantic models for representing operation results (success/failure/warnings).

  **Models:**
  - GenerationResult: Result of generating docstrings for a file/function
  - LintResult: Result of linting a file (errors, warnings, status)
  - ValidationResult: Result of validating an AgentSpec against schema

  All results include:
  - success: Boolean indicating overall success
  - messages: List of informational messages
  - errors: List of error messages (if any)
  - warnings: List of warning messages (if any)

why: |
  Structured result objects enable:
  - Consistent error handling across all operations
  - Easy aggregation of results (e.g., multiple files)
  - Clear separation of success/warning/error states
  - Programmatic access to results (for testing, CI/CD)

guardrails:
  - DO NOT change success logic without updating all result consumers
  - ALWAYS populate messages for debugging (even on success)
  - DO NOT make errors/warnings optional (empty list is valid)

deps:
  imports:
    - pydantic
    - typing
    - pathlib
---/agentspec
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """
    Result of validating an AgentSpec.

    ---agentspec
    what: |
      Returned by validators after checking an AgentSpec against schema.

      Fields:
      - valid: True if spec passes all validation checks
      - errors: List of error messages (validation failures)
      - warnings: List of warning messages (style issues, recommendations)
      - spec: The validated AgentSpec (if valid)

      Used by linters to determine if generated content meets requirements.

    why: |
      Separating validation results from the AgentSpec itself allows
      validators to return rich error context without polluting the model.

    guardrails:
      - DO NOT set valid=True if errors list is non-empty
      - ALWAYS include spec in result if valid=True
      - DO NOT raise exceptions on validation failure (return result instead)
    ---/agentspec
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

    ---agentspec
    what: |
      Returned after attempting to generate docstrings for a function/class.

      Fields:
      - success: True if generation completed without errors
      - function_name: Name of the function/class processed
      - file_path: Path to the file containing the entity
      - original_code: Original code before modification
      - generated_docstring: The generated docstring text
      - modified_code: Code after docstring insertion
      - messages: Informational messages (LLM calls, timing, etc.)
      - errors: Error messages (LLM failures, parsing errors, etc.)
      - warnings: Warning messages (existing docstring overwritten, etc.)
      - dry_run: True if this was a dry run (no files modified)

      Used by the orchestrator to track generation progress and report results.

    why: |
      Detailed result tracking enables:
      - Rollback on failure (using original_code)
      - Dry-run previews (show generated_docstring without modifying files)
      - Debugging (messages list shows all LLM interactions)
      - CI/CD integration (errors list for failure reporting)

    guardrails:
      - DO NOT set success=True if errors list is non-empty
      - ALWAYS preserve original_code for rollback capability
      - DO NOT modify files if dry_run=True (enforced by orchestrator)
      - ALWAYS include function_name and file_path for traceability
    ---/agentspec
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

    ---agentspec
    what: |
      Returned after linting one or more files.

      Fields:
      - success: True if no errors (warnings OK unless strict mode)
      - file_path: Path to the linted file
      - total_functions: Number of functions/classes checked
      - functions_with_specs: Number with agentspec docstrings
      - functions_without_specs: Number missing docstrings
      - errors: List of error messages (validation failures)
      - warnings: List of warning messages (style issues)
      - strict: True if strict mode enabled (warnings treated as errors)

      Used by the lint command to report validation status.

    why: |
      Structured lint results enable:
      - CI/CD integration (non-zero exit code on errors)
      - Coverage reporting (functions_with_specs / total_functions)
      - Detailed error reporting (per-function error messages)
      - Strict mode enforcement (warnings → errors)

    guardrails:
      - DO NOT set success=True if errors exist
      - DO NOT set success=True if warnings exist AND strict=True
      - ALWAYS count all functions (even if some have specs)
      - DO NOT skip validation just because a spec exists (could be invalid)
    ---/agentspec
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
