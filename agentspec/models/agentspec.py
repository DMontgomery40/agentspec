#!/usr/bin/env python3
"""
Core AgentSpec data models using Pydantic.

This module defines the structured representation of PEP 257-compliant docstrings
with agent-specific extensions (Rationale, Guardrails, Dependencies).

---agentspec
what: |
  Defines Pydantic models for representing function/class documentation in a structured,
  machine-readable format that can be converted to PEP 257-compliant docstrings.

  **Core Models:**
  - `AgentSpec`: Complete specification for a function/class/module
  - `DocstringSection`: Individual sections (Args, Returns, Rationale, etc.)
  - `DependencyInfo`: Tracks function dependencies (calls/called_by)

  **Design:**
  - Validates all fields at creation time using Pydantic
  - Supports conversion to Google, NumPy, and Sphinx docstring formats
  - Enforces minimum content requirements (configurable)
  - Compatible with Instructor library for LLM structured outputs

  **Custom Sections (Agent-Specific):**
  - Rationale: Why this implementation approach (replaces old "why")
  - Guardrails: What NOT to change and why (critical for AI safety)
  - Dependencies: What this code calls and what calls it

  **Standard Sections (PEP 257):**
  - Args/Parameters: Function arguments
  - Returns: Return value description
  - Raises: Exceptions that may be raised
  - Examples: Usage examples
  - Notes: Additional notes
  - Warnings: Important warnings

why: |
  Pydantic provides runtime validation, serialization, and JSON schema generation
  essential for LLM-based generation pipelines. Using structured models instead of
  raw dictionaries enables:
  - Type safety throughout the codebase
  - Automatic validation of LLM outputs (via Instructor)
  - Clear contracts between parser → LLM → formatter stages

  The custom sections (Rationale, Guardrails, Dependencies) encode agent-critical
  information that standard PEP 257 sections don't cover, while remaining
  100% compatible with standard Python tooling by using the Notes: convention.

guardrails:
  - DO NOT remove Pydantic validation - it's the only safeguard against malformed LLM outputs
  - DO NOT make custom sections (Rationale, Guardrails, Dependencies) optional without
    team discussion - they're core to the agent-safety value proposition
  - ALWAYS maintain PEP 257 compatibility - custom sections must render as valid docstrings
  - DO NOT change field names without updating all formatters (breaking change)

deps:
  imports:
    - pydantic
    - typing
---/agentspec
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DocstringStyle(str, Enum):
    """Supported docstring formatting styles."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    JSDOC = "jsdoc"
    TSDOC = "tsdoc"


class DependencyInfo(BaseModel):
    """
    Tracks dependencies for a function/class.

    ---agentspec
    what: |
      Represents the dependency graph for a code entity, tracking:
      - Functions/methods this entity calls
      - Functions/methods that call this entity
      - External modules/packages imported
      - Files this code depends on

      Used to populate the Dependencies: section in generated docstrings.

    why: |
      Explicit dependency tracking helps agents understand code relationships
      and avoid breaking changes. Critical for refactoring safety.

    guardrails:
      - DO NOT make lists non-optional - empty lists are valid (no dependencies)
      - ALWAYS preserve order of calls list (execution order may be significant)
    ---/agentspec
    """
    calls: List[str] = Field(
        default_factory=list,
        description="Functions/methods this entity calls (in order)"
    )
    called_by: List[str] = Field(
        default_factory=list,
        description="Functions/methods that call this entity"
    )
    imports: List[str] = Field(
        default_factory=list,
        description="External modules/packages imported"
    )
    files: List[str] = Field(
        default_factory=list,
        description="Files this code depends on (configs, data files, etc.)"
    )


class DocstringSection(BaseModel):
    """
    Represents a single section within a docstring.

    ---agentspec
    what: |
      Generic container for docstring content sections. Each section has:
      - title: Section name (e.g., "Args", "Returns", "Rationale")
      - content: The actual text content (can be multiline)
      - items: Optional list of sub-items (for Args, Raises, etc.)

      Supports both prose sections (Rationale, Notes) and structured sections
      (Args with parameter names and descriptions).

    why: |
      Flexible structure allows formatters to handle both simple prose sections
      and complex structured sections (like Args) without special-casing.

    guardrails:
      - DO NOT assume items is always populated - prose sections use content only
      - ALWAYS strip/normalize content - LLM outputs may have inconsistent whitespace
    ---/agentspec
    """
    title: str = Field(
        description="Section title (e.g., 'Args', 'Returns', 'Rationale')"
    )
    content: str = Field(
        default="",
        description="Main content text (for prose sections)"
    )
    items: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Structured items (e.g., [{'name': 'param1', 'desc': '...'}])"
    )


class AgentSpec(BaseModel):
    """
    Complete specification for a function, class, or module.

    ---agentspec
    what: |
      Primary data model for representing all documentation for a code entity.
      Designed to be:
      - Generated by LLMs (via Instructor structured outputs)
      - Validated by Pydantic
      - Converted to PEP 257 docstrings by formatters

      **Structure:**
      - summary: One-line description (required, PEP 257 first line)
      - description: Extended description (optional, detailed explanation)
      - sections: List of DocstringSection objects (Args, Returns, etc.)
      - rationale: Why this implementation (agent-specific, critical)
      - guardrails: What NOT to change (agent-specific, critical)
      - dependencies: Dependency tracking (agent-specific)
      - examples: Usage examples (standard PEP 257)

      **Validation:**
      - summary must be 10-150 characters
      - rationale must be at least 50 characters (unless terse mode)
      - guardrails must have at least 2 items (unless terse mode)

    why: |
      Centralizing all docstring data in one model enables:
      - Consistent validation across all generation pipelines
      - Easy conversion to any docstring format (Google/NumPy/Sphinx/JSDoc)
      - Structured LLM outputs with guaranteed schema compliance

      Minimum length requirements prevent LLMs from generating useless
      "placeholder" content that doesn't actually help agents.

    guardrails:
      - DO NOT reduce minimum length requirements without team discussion
      - DO NOT make rationale/guardrails optional - they're core value
      - ALWAYS validate summary is single-line (no newlines)
      - DO NOT allow empty sections list - at minimum should have Returns or description
    ---/agentspec
    """
    # Core fields (always required)
    summary: str = Field(
        min_length=10,
        max_length=150,
        description="One-line summary (PEP 257 first line, no newlines)"
    )

    # Extended description (optional but recommended)
    description: str = Field(
        default="",
        description="Extended multi-paragraph description"
    )

    # Standard PEP 257 sections (structured)
    sections: List[DocstringSection] = Field(
        default_factory=list,
        description="Standard sections: Args, Returns, Raises, Notes, etc."
    )

    # Agent-specific fields (CRITICAL for AI safety)
    rationale: str = Field(
        min_length=50,
        description="Why this implementation approach (replaces old 'why' field)"
    )

    guardrails: List[str] = Field(
        min_length=2,
        description="List of guardrails (what NOT to change and why)"
    )

    dependencies: Optional[DependencyInfo] = Field(
        default=None,
        description="Dependency tracking (calls, called_by, imports)"
    )

    # Optional standard sections
    examples: List[str] = Field(
        default_factory=list,
        description="Usage examples (code snippets)"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Important warnings for users/agents"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (language, file path, etc.)"
    )

    @field_validator("summary")
    @classmethod
    def validate_summary_single_line(cls, v: str) -> str:
        """Ensure summary is a single line (PEP 257 requirement)."""
        if "\n" in v:
            raise ValueError("summary must be a single line (no newlines)")
        return v.strip()

    @field_validator("guardrails")
    @classmethod
    def validate_guardrails_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure at least 2 guardrails are provided."""
        if len(v) < 2:
            raise ValueError("guardrails must contain at least 2 items")
        # Strip whitespace from each guardrail
        return [g.strip() for g in v if g.strip()]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentSpec:
        """Create AgentSpec from dictionary."""
        return cls.model_validate(data)
