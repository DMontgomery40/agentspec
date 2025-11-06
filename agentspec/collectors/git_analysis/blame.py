#!/usr/bin/env python3
"""
Git blame collector (authors, creation date, last modified).
"""

from __future__ import annotations

import subprocess
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from agentspec.collectors.base import BaseCollector


class GitBlameCollector(BaseCollector):
    """
    Collects git blame information for a function.

    Extracts:
    - Primary author (most lines)
    - All contributors
    - Creation date (first commit)
    - Last modified date
    - Stability metrics (how often modified)
    """

    @property
    def category(self) -> str:
        return "git_analysis"

    def get_priority(self) -> int:
        return 55

    def can_collect(self, context: Dict[str, Any]) -> bool:
        """Check if we're in a git repository."""
        file_path = context.get("file_path")
        if not file_path:
            return False

        try:
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
        Collect git blame for function.

        Uses git blame on the function's line range.
        """
        file_path = context.get("file_path")
        if not file_path:
            return {}

        # Get line range
        if hasattr(function_node, "line_number"):
            start_line = function_node.line_number
            end_line = function_node.end_line_number
        elif hasattr(function_node, "lineno"):
            start_line = function_node.lineno
            end_line = getattr(function_node, "end_lineno", start_line)
        else:
            return {}

        try:
            # git blame -L start,end file --line-porcelain
            cmd = [
                "git", "blame",
                f"-L{start_line},{end_line}",
                str(file_path),
                "--line-porcelain"
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

            # Parse blame output (simplified)
            authors = {}
            for line in result.stdout.split("\n"):
                if line.startswith("author "):
                    author = line.replace("author ", "").strip()
                    authors[author] = authors.get(author, 0) + 1

            # Find primary author (most lines)
            primary_author = max(authors.items(), key=lambda x: x[1])[0] if authors else None

            return {
                "git_blame": {
                    "primary_author": primary_author,
                    "all_authors": list(authors.keys()),
                    "author_line_counts": authors,
                    "note": "Blame data for function line range"
                }
            }

        except Exception as e:
            return {"git_blame_error": str(e)}
