#!/usr/bin/env python3
"""
Configuration models for agentspec operations.

"""

from __future__ import annotations

from typing import Optional, Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class GenerationConfig(BaseModel):
    """
    Configuration for LLM-based docstring generation.

        """
    # Provider settings
    provider: Literal["auto", "anthropic", "openai"] = Field(
        default="auto",
        description="LLM provider: 'auto' (infer from model), 'anthropic', 'openai'"
    )

    model: str = Field(
        default="claude-haiku-4-5",
        description="Model identifier (e.g., claude-haiku-4-5, gpt-5, llama3.2)"
    )

    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for OpenAI-compatible APIs (e.g., http://localhost:11434/v1)"
    )

    # LLM parameters
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 = deterministic, 2.0 = very creative)"
    )

    max_tokens: int = Field(
        default=2000,
        ge=100,
        le=100000,
        description="Maximum tokens in LLM response"
    )

    # Generation modes
    terse: bool = Field(
        default=False,
        description="Terse mode: shorter output, max_tokens=500, temperature=0.0"
    )

    verbose: bool = Field(
        default=True,
        description="Verbose mode: full detailed docstrings (default)"
    )

    # Behavior flags
    update_existing: bool = Field(
        default=False,
        description="Regenerate docstrings even if they already exist"
    )

    dry_run: bool = Field(
        default=False,
        description="Preview output without modifying files"
    )

    force_context: bool = Field(
        default=False,
        description="Add print() statements to force LLM context loading"
    )

    diff_summary: bool = Field(
        default=False,
        description="Include git diff summaries in docstrings"
    )

    # Output format (for formatters)
    style: str = Field(
        default="google",
        description="Docstring style: google, numpy, sphinx, jsdoc, tsdoc"
    )

    @field_validator("temperature")
    @classmethod
    def adjust_temperature_for_terse(cls, v: float, info) -> float:
        """If terse mode is enabled, force temperature to 0.0."""
        # Access terse from values dict if available
        if info.data.get("terse"):
            return 0.0
        return v

    @field_validator("max_tokens")
    @classmethod
    def adjust_max_tokens_for_terse(cls, v: int, info) -> int:
        """If terse mode is enabled, cap max_tokens at 500."""
        if info.data.get("terse"):
            return min(v, 500)
        return v


class LintConfig(BaseModel):
    """
    Configuration for agentspec linting/validation.

        """
    min_lines: int = Field(
        default=10,
        ge=1,
        description="Minimum lines required in agentspec content"
    )

    strict: bool = Field(
        default=False,
        description="Treat warnings as errors (for CI/CD)"
    )

    check_pep257: bool = Field(
        default=True,
        description="Validate PEP 257 compliance"
    )

    min_guardrails: int = Field(
        default=2,
        ge=1,
        description="Minimum number of guardrails required"
    )


class ExtractConfig(BaseModel):
    """
    Configuration for extracting agentspec content.

        """
    format: Literal["markdown", "json", "agent-context"] = Field(
        default="markdown",
        description="Output format"
    )

    output_path: Optional[Path] = Field(
        default=None,
        description="Output file path (default: stdout)"
    )

    include_metadata: bool = Field(
        default=False,
        description="Include file paths, line numbers, etc."
    )
