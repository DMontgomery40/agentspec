#!/usr/bin/env python3
"""
Collector orchestrator that runs all collectors in sequence.

"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path
import time

from agentspec.collectors.base import BaseCollector, CollectedMetadata


def find_repo_root(file_path: Path) -> Optional[Path]:
    """
    Find git repository root by walking up directory tree.

    Args:
        file_path: Path to a file within the repository

    Returns:
        Path to repository root (contains .git), or None if not in a git repo

        """
    # Start with the file's directory
    current = file_path if file_path.is_dir() else file_path.parent

    # Walk up directory tree
    while True:
        git_dir = current / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return current

        # Check if we've reached the filesystem root
        parent = current.parent
        if parent == current:
            # Reached root without finding .git
            return None

        current = parent


class CollectorOrchestrator:
    """
    Orchestrates execution of all metadata collectors.

        """

    def __init__(self):
        """Initialize orchestrator with empty collector list."""
        self.collectors: List[BaseCollector] = []
        self.enable_timing = True
        self.enable_logging = True

    def register(self, collector: BaseCollector):
        """
        Register a collector.

        Args:
            collector: Collector instance to register

        Rationale:
            Explicit registration enables configuration (which collectors to run).
            Can register different collectors for different use cases.

        Guardrails:
            - DO NOT register same collector twice (check for duplicates)
            - ALWAYS validate collector implements BaseCollector
        """
        # Check for duplicates
        if any(c.name == collector.name for c in self.collectors):
            print(f"Warning: Collector {collector.name} already registered, skipping")
            return

        self.collectors.append(collector)

    def collect_all(
        self,
        function_node: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> CollectedMetadata:
        """
        Run all registered collectors and aggregate results.

        Args:
            function_node: AST node or ParsedFunction
            context: Context dict (file_path, repo_root, etc.)

        Returns:
            CollectedMetadata with all collected data

        Rationale:
            Main entry point for collection. Runs all collectors, handles
            failures gracefully, aggregates results by category.

        Guardrails:
            - ALWAYS return CollectedMetadata (even if empty)
            - DO NOT fail on collector exceptions (log and continue)
            - ALWAYS respect can_collect() results
            - DO NOT modify function_node or context
        """
        context = context or {}

        # Extract function name and file path from context or function_node
        function_name = context.get("function_name", getattr(function_node, "name", "unknown"))
        file_path = Path(context.get("file_path", "unknown"))

        # Initialize metadata container
        metadata = CollectedMetadata(
            function_name=function_name,
            file_path=file_path
        )

        # Sort collectors by priority (low number = high priority)
        sorted_collectors = sorted(self.collectors, key=lambda c: c.get_priority())

        # Run each collector
        for collector in sorted_collectors:
            collector_name = collector.name

            # Check if collector can run
            if not collector.can_collect(context):
                if self.enable_logging:
                    print(f"Skipping {collector_name} (can_collect returned False)")
                continue

            # Execute collector
            try:
                start_time = time.time() if self.enable_timing else 0

                collected_data = collector.collect(function_node, context)

                if self.enable_timing:
                    elapsed = time.time() - start_time
                    if self.enable_logging:
                        print(f"✓ {collector_name} completed in {elapsed:.3f}s")

                # Aggregate by category
                category = collector.category
                if category == "code_analysis":
                    metadata.code_analysis.update(collected_data)
                elif category == "git_analysis":
                    metadata.git_analysis.update(collected_data)
                elif category == "test_analysis":
                    metadata.test_analysis.update(collected_data)
                elif category == "runtime_analysis":
                    metadata.runtime_analysis.update(collected_data)
                elif category == "api_analysis":
                    metadata.api_analysis.update(collected_data)
                else:
                    # Unknown category - store in raw_data
                    metadata.raw_data[collector_name] = collected_data

            except Exception as e:
                if self.enable_logging:
                    print(f"✗ {collector_name} failed: {str(e)}")
                # Store error in raw_data for debugging
                metadata.raw_data[f"{collector_name}_error"] = str(e)
                # Continue to next collector (graceful degradation)

        return metadata

    def collect_for_file(
        self,
        file_path: Path,
        function_nodes: List[Any]
    ) -> Dict[str, CollectedMetadata]:
        """
        Collect metadata for all functions in a file.

        Args:
            file_path: Source file path
            function_nodes: List of AST nodes or ParsedFunction objects

        Returns:
            Dict mapping function names to CollectedMetadata

        Rationale:
            Batch processing for entire files. Some collectors (like git blame)
            can be more efficient when processing entire files.

        Guardrails:
            - DO NOT fail entire file if one function fails
            - ALWAYS return results for all functions (even failures)
        """
        results = {}

        # Find actual git repository root
        repo_root = find_repo_root(file_path)
        if repo_root is None:
            # Not in a git repo, use file's parent as fallback
            repo_root = file_path.parent

        context = {
            "file_path": file_path,
            "repo_root": repo_root,
        }

        for func_node in function_nodes:
            function_name = getattr(func_node, "name", "unknown")
            func_context = context.copy()
            func_context["function_name"] = function_name

            metadata = self.collect_all(func_node, func_context)
            results[function_name] = metadata

        return results
