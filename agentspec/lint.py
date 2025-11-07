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
from agentspec.utils import collect_source_files
from typing import List, Tuple, Dict, Any


REQUIRED_KEYS = ["what", "deps", "why", "guardrails"]
RECOMMENDED_KEYS = ["changelog", "testing", "performance"]


class AgentSpecLinter(ast.NodeVisitor):
    def __init__(self, filepath: str, min_lines: int = 10):
        """
                """
        self.filepath = filepath
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
        self.min_lines = min_lines

    def visit_FunctionDef(self, node):
        """
                """
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
                """
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
                """
        self._check_docstring(node)
        self.generic_visit(node)

    def _check_docstring(self, node):
        """
        " fenced block, parses its YAML content, and enforces structural constraints: REQUIRED_KEYS presence, RECOMMENDED_KEYS presence (warnings), 'what' field minimum character length (50+), 'deps' as dict structure, and 'guardrails' as non-empty list. Returns early on critical failures (missing docstring, missing fenced block, invalid YAML, non-dict YAML root) to prevent cascading validation errors. Appends validation results as (lineno, message) tuples to self.errors (critical issues prefixed with ❌) or self.warnings (advisory issues prefixed with ⚠️).
            deps:
              calls:
                - ast.get_docstring
                - doc.find
                - errors.append
                - fenced.split
                - isinstance
                - join
                - l.strip
                - len
                - str
                - strip
                - warnings.append
                - yaml.safe_load
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          Fenced YAML blocks balance human-readable docstring formatting with machine-parseable structured metadata for AI agent consumption. Using yaml.safe_load() prevents code injection vulnerabilities and handles YAML edge cases more robustly than manual string parsing. Early returns on critical failures prevent AttributeErrors when accessing dict keys and eliminate nonsensical cascading error messages that confuse developers. Separating errors from warnings enables configurable strictness policies across different CI/CD environments (e.g., fail on errors, warn on missing recommendations). Numeric thresholds (character counts, line counts) provide objective, configurable validation criteria rather than subjective heuristics.

        guardrails:
          - DO NOT modify the "" fenced block delimiters without coordinating updates across all code that generates or parses agentspec docstrings, as this will break round-trip consistency.
          - DO NOT remove early returns on critical failures (missing docstring, missing block, invalid YAML, non-dict root); they prevent AttributeErrors and cascading error messages that obscure root causes.
          - DO NOT use yaml.load() instead of yaml.safe_load(); arbitrary code execution vulnerability when parsing untrusted docstrings.
          - DO NOT access spec_data dict attributes without isinstance() type checks first; YAML parsing may produce unexpected types (None, list, scalar) if input is malformed.
          - ALWAYS preserve the (lineno, message) tuple format when appending to self.errors and self.warnings; downstream code depends on this structure for sorting and reporting.
          - ALWAYS include the emoji prefix (❌ for errors, ⚠️ for warnings) in error/warning messages for visual distinction in linter output.
          - DO NOT treat missing recommended keys as errors; they should only generate warnings to allow gradual adoption of new metadata fields.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        doc = ast.get_docstring(node)
        if not doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing docstring"))
            return

        # Check for agentspec block
        if "" not in doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing agentspec fenced block"))
            return

        # Extract fenced section
        start = doc.find("")
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
        '''
                '''
        return self.errors, self.warnings


def check_file(filepath: Path, min_lines: int = 10) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    '''
        '''
    # For non-Python files, skip AST linting for now
    if filepath.suffix not in [".py", ".pyw"]:
        # JS/TS files: skip for now (could add text-based linting later)
        return [], []

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
    '''
        '''
    path = Path(target)
    files = collect_source_files(path)  # Supports .py, .js, .jsx, .ts, .tsx

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
