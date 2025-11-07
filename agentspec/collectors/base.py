#!/usr/bin/env python3
"""
Base collector abstraction for deterministic metadata extraction.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class CollectedMetadata(BaseModel):
    """
    Container for all collected metadata about a function.

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
