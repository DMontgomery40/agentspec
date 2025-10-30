#!/usr/bin/env python3
"""
agentspec.lint
--------------------------------
Lints Python files for presence and completeness of structured agent spec blocks.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


REQUIRED_KEYS = ["what", "deps", "why", "guardrails"]


class AgentSpecLinter(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors: List[Tuple[int, str]] = []

    def visit_FunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)

    def _check_docstring(self, node):
        doc = ast.get_docstring(node)
        if not doc:
            self.errors.append((node.lineno, f"❌ {node.name}() missing docstring"))
            return

        if "---agentspec" not in doc or "---/agentspec" not in doc:
            self.errors.append((node.lineno, f"⚠️ {node.name}() missing agentspec fenced block"))
            return

        # Extract fenced section
        start = doc.find("---agentspec") + len("---agentspec")
        end = doc.find("---/agentspec")
        fenced = doc[start:end].strip()

        # Check required keys
        missing = [k for k in REQUIRED_KEYS if f"{k}:" not in fenced]
        if missing:
            self.errors.append(
                (node.lineno, f"⚠️ {node.name}() missing keys: {', '.join(missing)}")
            )

    def check(self) -> List[Tuple[int, str]]:
        return self.errors


def check_file(filepath: Path) -> List[Tuple[int, str]]:
    """Check a single Python file for compliance."""
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))
        checker = AgentSpecLinter(str(filepath))
        checker.visit(tree)
        return checker.check()
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e}")]
    except Exception as e:
        return [(0, f"Error parsing {filepath}: {e}")]


def run(target: str) -> int:
    """Main lint runner for CLI."""
    path = Path(target)
    files = [path] if path.is_file() else list(path.rglob("*.py"))

    total_errors = 0
    for file in files:
        results = check_file(file)
        if results:
            print(f"\n{file}:")
            for line, msg in results:
                print(f"  Line {line}: {msg}")
            total_errors += len(results)

    if total_errors == 0:
        print("✅ All files have valid agent specs.")
        return 0
    else:
        print(f"\n❌ Found {total_errors} lint issues.")
        return 1
