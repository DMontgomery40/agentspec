#!/usr/bin/env python3
"""
Configuration models for agentspec operations.

---agentspec
what: |
  Pydantic models for configuring lint, extract, and generate operations.

  **Models:**
  - GenerationConfig: LLM settings (model, temperature, max_tokens, etc.)
  - LintConfig: Validation settings (strict mode, min_lines, etc.)
  - ExtractConfig: Extraction settings (format, output path, etc.)

  All configs support loading from:
  - .agentspec.yaml files (project-level)
  - Environment variables (deployment-level)
  - CLI arguments (invocation-level)

  Precedence: CLI args > env vars > config file > defaults

why: |
  Pydantic configs provide type-safe, validated configuration with clear defaults.
  Separating config from business logic enables:
  - Testing with different configs
  - Config file support without complex parsing
  - Clear documentation of all available options

guardrails:
  - DO NOT change default values without updating CLI help text
  - DO NOT make model/provider required - must have sensible defaults
  - ALWAYS validate temperature is 0.0-2.0 (LLM API constraint)

deps:
  imports:
    - pydantic
    - typing
    - pathlib
---/agentspec
"""

from __future__ import annotations

from typing import Optional, Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class GenerationConfig(BaseModel):
    """
    Configuration for LLM-based docstring generation.

    ---agentspec
    what: |
      Controls all aspects of LLM-based generation:
      - Provider selection (anthropic, openai, auto)
      - Model selection (claude-haiku-4-5, gpt-5, llama3.2, etc.)
      - LLM parameters (temperature, max_tokens)
      - Output style (verbose vs terse mode)
      - Safety flags (dry_run, update_existing)

      **Modes:**
      - Verbose (default): Full detailed docstrings with all sections
      - Terse (--terse): Shorter output, max_tokens=500, temperature=0.0

      **Providers:**
      - anthropic: Claude models (requires ANTHROPIC_API_KEY)
      - openai: OpenAI cloud or compatible APIs (requires OPENAI_API_KEY)
      - auto: Infer from model name (default)

    why: |
      Centralizing all generation settings in one config object makes it easy to:
      - Pass settings through the orchestrator → provider pipeline
      - Override settings for testing
      - Load settings from config files

      Temperature defaults (0.2 verbose, 0.0 terse) balance creativity and
      determinism. Lower temperature for terse mode ensures consistent output.

    guardrails:
      - DO NOT change default model without testing - breaks user workflows
      - DO NOT allow temperature > 2.0 (LLM API hard limit)
      - ALWAYS validate base_url is valid URL format if provided
      - DO NOT make dry_run default to True (would break normal usage)
    ---/agentspec
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

    ---agentspec
    what: |
      Controls validation behavior:
      - min_lines: Minimum lines required in agentspec content (default 10)
      - strict: Treat warnings as errors (for CI/CD)
      - check_pep257: Validate PEP 257 compliance (default True)

      Validates:
      - Presence of required sections (summary, rationale, guardrails)
      - Minimum content length (prevents placeholder text)
      - PEP 257 compliance (single-line summary, proper formatting)
      - Guardrails count (minimum 2 guardrails required)

    why: |
      Configurable linting enables teams to enforce their own standards
      while providing sensible defaults. Strict mode for CI/CD catches
      issues before merge.

    guardrails:
      - DO NOT set min_lines default below 10 (prevents useless docstrings)
      - DO NOT disable PEP 257 checks by default (breaks compatibility)
      - ALWAYS require at least 2 guardrails (core safety feature)
    ---/agentspec
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

    ---agentspec
    what: |
      Controls extraction behavior:
      - format: Output format (markdown, json, agent-context)
      - output_path: Where to write output (default stdout)
      - include_metadata: Include file paths, line numbers, etc.

      **Formats:**
      - markdown: Human-readable documentation
      - json: Machine-readable structured data
      - agent-context: Optimized for LLM context windows

    why: |
      Different formats serve different use cases:
      - Markdown for documentation sites
      - JSON for CI/CD pipelines
      - Agent-context for LLM prompts

    guardrails:
      - DO NOT change default format (breaks backward compatibility)
      - ALWAYS validate output_path is writable if provided
      - DO NOT make include_metadata True by default (breaks parsers)
    ---/agentspec
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
