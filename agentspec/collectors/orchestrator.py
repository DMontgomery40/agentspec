#!/usr/bin/env python3
"""
Collector orchestrator that runs all collectors in sequence.

---agentspec
what: |
  Coordinates execution of all metadata collectors and aggregates results.

  **Responsibilities:**
  - Register collectors
  - Determine execution order (by priority)
  - Run collectors in sequence
  - Aggregate results into CollectedMetadata
  - Handle collector failures gracefully
  - Provide timing/logging information

  **Flow:**
  1. Register collectors (code analysis, git analysis, etc.)
  2. Sort by priority (low number = high priority)
  3. Run each collector's can_collect() check
  4. Execute collect() for enabled collectors
  5. Aggregate results by category
  6. Return CollectedMetadata object

why: |
  Orchestrator pattern separates coordination from collection logic.
  Each collector focuses on one task, orchestrator handles workflow.

  Benefits:
  - Easy to add/remove collectors
  - Clear execution order
  - Graceful degradation (one collector failure doesn't break all)
  - Easy testing (mock individual collectors)

guardrails:
  - DO NOT run collectors in parallel without dependency analysis
  - ALWAYS catch and log collector exceptions (don't fail entire pipeline)
  - DO NOT enforce strict schemas (collectors return flexible dicts)
  - ALWAYS respect can_collect() results (skip disabled collectors)

deps:
  imports:
    - typing
    - pathlib
  calls:
    - BaseCollector.can_collect
    - BaseCollector.collect
    - CollectedMetadata
---/agentspec
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path
import time

from agentspec.collectors.base import BaseCollector, CollectedMetadata


class CollectorOrchestrator:
    """
    Orchestrates execution of all metadata collectors.

    ---agentspec
    what: |
      Main coordinator for running collectors and aggregating results.

      **Usage:**
      ```python
      orchestrator = CollectorOrchestrator()
      orchestrator.register(SignatureCollector())
      orchestrator.register(GitBlameCollector())

      metadata = orchestrator.collect_all(
          function_node=func_ast_node,
          context={"file_path": Path("foo.py"), "repo_root": Path(".")}
      )

      print(metadata.code_analysis)  # Signature data
      print(metadata.git_analysis)    # Blame data
      ```

      **Execution Order:**
      1. Sort collectors by priority
      2. Run can_collect() for each
      3. Execute collect() for enabled collectors
      4. Aggregate by category
      5. Return CollectedMetadata

    why: |
      Centralized orchestration makes it easy to:
      - Configure which collectors run
      - Control execution order
      - Handle failures gracefully
      - Add timing/logging
      - Test end-to-end collection

    guardrails:
      - DO NOT fail entire pipeline if one collector fails
      - ALWAYS log collector errors (for debugging)
      - DO NOT modify collector results (pass through as-is)
      - ALWAYS return CollectedMetadata (even if all collectors fail)
    ---/agentspec
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

        context = {
            "file_path": file_path,
            "repo_root": file_path.parent,  # TODO: Find actual repo root
        }

        for func_node in function_nodes:
            function_name = getattr(func_node, "name", "unknown")
            func_context = context.copy()
            func_context["function_name"] = function_name

            metadata = self.collect_all(func_node, func_context)
            results[function_name] = metadata

        return results
