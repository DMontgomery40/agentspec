#!/usr/bin/env python3
"""
agentspec.lint
--------------------------------
Lints Python files for presence and completeness of structured agent spec blocks.
Now with YAML validation and verbose comment requirements.
"""

import ast
import sys
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any


REQUIRED_KEYS = ["what", "deps", "why", "guardrails"]
RECOMMENDED_KEYS = ["changelog", "testing", "performance"]


class AgentSpecLinter(ast.NodeVisitor):
    def __init__(self, filepath: str, min_lines: int = 10):
        self.filepath = filepath
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
        self.min_lines = min_lines

    def visit_FunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self._check_docstring(node)
        self.generic_visit(node)

    def _check_docstring(self, node):
        doc = ast.get_docstring(node)
        if not doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing docstring"))
            return

        # Check for agentspec block
        if "---agentspec" not in doc or "---/agentspec" not in doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing agentspec fenced block"))
            return

        # Extract fenced section
        start = doc.find("---agentspec") + len("---agentspec")
        end = doc.find("---/agentspec")
        fenced = doc[start:end].strip()

        # Check minimum verbosity (line count)
        fenced_lines = [l for l in fenced.split('\n') if l.strip()]
        if len(fenced_lines) < self.min_lines:
            self.warnings.append(
                (node.lineno, f"⚠️  {node.name} agentspec too short "
                 f"({len(fenced_lines)} lines, recommend {self.min_lines}+)")
            )

        # Try to parse as YAML
        try:
            spec_data = yaml.safe_load(fenced)
            if not isinstance(spec_data, dict):
                self.errors.append(
                    (node.lineno, f"❌ {node.name} agentspec is not valid YAML dict")
                )
                return
        except yaml.YAMLError as e:
            self.errors.append(
                (node.lineno, f"❌ {node.name} agentspec has invalid YAML: {e}")
            )
            return

        # Check required keys
        missing = [k for k in REQUIRED_KEYS if k not in spec_data]
        if missing:
            self.errors.append(
                (node.lineno, f"❌ {node.name} missing required keys: {', '.join(missing)}")
            )

        # Check recommended keys (warnings only)
        missing_recommended = [k for k in RECOMMENDED_KEYS if k not in spec_data]
        if missing_recommended:
            self.warnings.append(
                (node.lineno, f"⚠️  {node.name} missing recommended keys: "
                 f"{', '.join(missing_recommended)}")
            )

        # Validate 'what' field verbosity
        if 'what' in spec_data:
            what_text = str(spec_data['what']).strip()
            if len(what_text) < 50:
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} 'what' field too brief "
                     f"({len(what_text)} chars, recommend 50+)")
                )

        # Validate deps structure
        if 'deps' in spec_data:
            if not isinstance(spec_data['deps'], dict):
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} 'deps' should be a dict with "
                     "'calls', 'called_by', etc.")
                )

        # Validate guardrails is a list
        if 'guardrails' in spec_data:
            if not isinstance(spec_data['guardrails'], list):
                self.errors.append(
                    (node.lineno, f"❌ {node.name} 'guardrails' must be a list")
                )
            elif len(spec_data['guardrails']) == 0:
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} has empty 'guardrails' list")
                )

    def check(self) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
        return self.errors, self.warnings


def check_file(filepath: Path, min_lines: int = 10) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """Check a single Python file for compliance."""
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))
        checker = AgentSpecLinter(str(filepath), min_lines=min_lines)
        checker.visit(tree)
        return checker.check()
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e}")], []
    except Exception as e:
        return [(0, f"Error parsing {filepath}: {e}")], []


def run(target: str, min_lines: int = 10, strict: bool = False) -> int:
    """
    Main lint runner for CLI.
    
    Args:
        target: File or directory to lint
        min_lines: Minimum lines required in agentspec block
        strict: Treat warnings as errors
    """
    path = Path(target)
    files = [path] if path.is_file() else list(path.rglob("*.py"))

    total_errors = 0
    total_warnings = 0
    
    for file in files:
        errors, warnings = check_file(file, min_lines=min_lines)
        
        if errors or warnings:
            print(f"\n{file}:")
            for line, msg in errors:
                print(f"  Line {line}: {msg}")
                total_errors += 1
            for line, msg in warnings:
                print(f"  Line {line}: {msg}")
                total_warnings += 1

    print(f"\n{'='*60}")
    if total_errors == 0 and (total_warnings == 0 or not strict):
        print("✅ All files have valid agent specs.")
        print(f"   {len(files)} files checked, {total_warnings} warnings")
        return 0
    else:
        if strict and total_warnings > 0:
            print(f"❌ Found {total_errors} errors and {total_warnings} warnings (strict mode)")
            return 1
        elif total_errors > 0:
            print(f"❌ Found {total_errors} errors and {total_warnings} warnings")
            return 1
        else:
            print(f"⚠️  Found {total_warnings} warnings")
            return 0
