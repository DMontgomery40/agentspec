#!/usr/bin/env python3
"""
Git commit history collector (last N commits affecting a function).

Reuses and improves existing logic from agentspec/collect.py.
"""

from __future__ import annotations

import subprocess
from typing import Dict, Any, List
from pathlib import Path

from agentspec.collectors.base import BaseCollector


class CommitHistoryCollector(BaseCollector):
    """
    Collects git commit history for a function.

    Uses git log with -L option to get function-specific history.
    """

    @property
    def category(self) -> str:
        return "git_analysis"

    def get_priority(self) -> int:
        return 50

    def can_collect(self, context: Dict[str, Any]) -> bool:
        """Check if we're in a git repository."""
        file_path = context.get("file_path")
        if not file_path:
            return False

        try:
            # Check if file is in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=Path(file_path).parent,
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def collect(self, function_node: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect git history for function.

        Uses git log -L:<funcname>:<file> to get function-specific commits.
        """
        file_path = context.get("file_path")
        function_name = context.get("function_name", getattr(function_node, "name", None))

        if not file_path or not function_name:
            return {}

        try:
            # Get last 5 commits affecting this function
            # git log -L :function_name:file_path --pretty=format:"%h|%an|%ae|%ad|%s" -5
            cmd = [
                "git", "log",
                f"-L:{function_name}:{file_path}",
                "--pretty=format:%h|%an|%ae|%ad|%s",
                "-5"  # Last 5 commits
            ]

            result = subprocess.run(
                cmd,
                cwd=Path(file_path).parent,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {}

            # Parse output
            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" not in line:
                    continue

                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

            return {
                "commit_history": {
                    "commits": commits,
                    "total_commits": len(commits),
                    "note": "Last 5 commits affecting this function"
                }
            }

        except Exception as e:
            return {"commit_history_error": str(e)}
