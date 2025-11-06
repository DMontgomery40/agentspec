#!/usr/bin/env python3
"""
Base collector abstraction for deterministic metadata extraction.

---agentspec
what: |
  Abstract base class defining the interface for all metadata collectors.

  **Collectors vs LLMs:**
  - Collectors extract DETERMINISTIC facts (git history, AST analysis, type hints)
  - LLMs generate SUBJECTIVE content (what/why/guardrails/rationale)
  - Together they produce complete, accurate docstrings

  **Design Principles:**
  - Each collector is independent and stateless
  - Collectors never call LLMs (pure deterministic logic)
  - Collectors return structured data (dicts/Pydantic models)
  - Collectors can fail gracefully (return partial data)
  - Collectors run in parallel where possible

  **Collected Data Goes To:**
  - LLM context (helps LLM generate better what/why/guardrails)
  - Direct docstring inclusion (Args, Returns, Raises from AST)
  - Metadata sections (git history, complexity metrics)

why: |
  Separating deterministic collection from LLM generation:
  - Reduces hallucination (LLM doesn't guess args/types/exceptions)
  - Improves accuracy (git history, complexity are facts)
  - Enables caching (deterministic data doesn't change between runs)
  - Simplifies testing (collectors are pure functions)
  - Reduces cost (LLM only generates subjective content)

guardrails:
  - DO NOT call LLMs in collectors (defeats purpose)
  - DO NOT make collectors stateful (must be reusable)
  - ALWAYS handle failures gracefully (partial data > no data)
  - DO NOT block on slow collectors (use timeouts)

deps:
  imports:
    - abc
    - typing
    - pydantic
---/agentspec
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class CollectedMetadata(BaseModel):
    """
    Container for all collected metadata about a function.

    ---agentspec
    what: |
      Structured container holding all deterministic facts collected about a function.

      **Categories:**
      - code_analysis: From AST (signature, exceptions, decorators, complexity)
      - git_analysis: From git history (commits, blame, churn)
      - test_analysis: From test files (coverage, test discovery)
      - runtime_analysis: From code patterns (logging, caching, async)
      - api_analysis: From framework detection (CLI, web endpoints)

      Used as input to LLM prompts and direct docstring formatting.

    why: |
      Centralizing all metadata in one model enables:
      - Type-safe access to collected data
      - Easy serialization (for caching)
      - Clear schema for what collectors produce
      - Validation of collected data

    guardrails:
      - DO NOT make fields required (collectors may fail)
      - ALWAYS use default_factory=dict for nested data
      - DO NOT include LLM-generated content here (only deterministic facts)
    ---/agentspec
    """
    # Function identification
    function_name: str = Field(description="Function name")
    file_path: Path = Field(description="Source file path")

    # Code analysis (from AST/tree-sitter)
    code_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Signature, exceptions, decorators, complexity, types"
    )

    # Git analysis (from git history)
    git_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Commits, blame, churn, diff summaries"
    )

    # Test analysis (from test files)
    test_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Coverage, test discovery, fixtures"
    )

    # Runtime analysis (from code patterns)
    runtime_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Logging, caching, async, performance patterns"
    )

    # API analysis (from framework detection)
    api_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="CLI commands, web endpoints, visibility"
    )

    # Raw data (for debugging)
    raw_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original data from collectors (for debugging)"
    )


class BaseCollector(ABC):
    """
    Abstract base class for metadata collectors.

    ---agentspec
    what: |
      Defines the interface all collectors must implement.

      **Required Methods:**
      - collect(function_node, context) → Dict[str, Any]: Extract metadata
      - can_collect(context) → bool: Check if collector can run
      - get_name() → str: Collector name (for logging)

      **Lifecycle:**
      1. Check can_collect(context) to see if collector should run
      2. Call collect(function_node, context) to extract metadata
      3. Return dict of collected facts (no LLM calls!)
      4. Handle failures gracefully (return partial data)

      Collectors should be stateless and reusable.

    why: |
      ABC ensures consistent interface across all collectors.
      Polymorphic usage enables CollectorOrchestrator to run
      all collectors without knowing implementation details.

    guardrails:
      - DO NOT call LLMs in collect() (deterministic only)
      - DO NOT maintain state between collect() calls
      - ALWAYS handle exceptions gracefully (return partial data)
      - DO NOT block indefinitely (use timeouts for slow operations)
    ---/agentspec
    """

    @abstractmethod
    def collect(
        self,
        function_node: Any,  # ast.FunctionDef or ParsedFunction
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect metadata for a function.

        Args:
            function_node: AST node or ParsedFunction object
            context: Additional context (file_path, repo_root, etc.)

        Returns:
            Dict of collected metadata (structure varies by collector)

        Raises:
            Exception: Only for fatal errors (prefer returning partial data)

        Rationale:
            Main entry point for collection. Returns raw dict instead of
            Pydantic model to allow flexible schemas per collector.

        Guardrails:
            - DO NOT call LLMs (deterministic only)
            - ALWAYS handle missing data gracefully
            - DO NOT modify input parameters
            - ALWAYS return dict (even if empty)
        """
        pass

    def can_collect(self, context: Dict[str, Any]) -> bool:
        """
        Check if this collector can run given the context.

        Args:
            context: Context dict with file_path, repo_root, etc.

        Returns:
            True if collector should run

        Rationale:
            Some collectors require specific context (e.g., git collectors
            need a git repo). Checking up front avoids wasteful work.

        Guardrails:
            - DO NOT perform expensive operations here (just checks)
            - ALWAYS return bool (don't raise exceptions)
            - DO NOT modify context
        """
        return True  # Default: always run

    @property
    def name(self) -> str:
        """Collector name (for logging/debugging)."""
        return self.__class__.__name__

    @property
    def category(self) -> str:
        """
        Collector category (code_analysis, git_analysis, etc.).

        Used by orchestrator to organize collected data.
        """
        return "other"

    def get_priority(self) -> int:
        """
        Collector priority (lower = runs first).

        Returns:
            Priority value (0 = highest)

        Rationale:
            Some collectors depend on others. Priority ensures correct
            execution order. Default is 50 (medium priority).

        Guardrails:
            - DO NOT use negative priorities (reserved for critical collectors)
            - DO NOT use priorities > 100 (reserved for optional collectors)
        """
        return 50  # Medium priority
