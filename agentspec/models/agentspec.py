#!/usr/bin/env python3
"""
Core AgentSpec data models using Pydantic.

This module defines the structured representation of PEP 257-compliant docstrings
with agent-specific extensions (Rationale, Guardrails, Dependencies).

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
