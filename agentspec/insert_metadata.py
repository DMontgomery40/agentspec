#!/usr/bin/env python3
"""
apply deterministic metadata after LLM generation using a safe, two‑phase file update.

This module NEVER calls an LLM. It only takes narrative docstrings and appends
deterministic metadata (deps/changelog) programmatically, verifying syntax after
each phase using py_compile before replacing the target file atomically.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import os
import tempfile
import py_compile
import re


def inject_deterministic_metadata(llm_output: str, metadata: Dict[str, Any], as_agentspec_yaml: bool) -> str:
    """
    Inject deterministic metadata (dependencies and changelog) into docstrings.

    This is the MODULAR version extracted from generate.py.
    Does NOT call any LLM - pure string manipulation.

    Args:
        llm_output: Formatted docstring from LLM
        metadata: Dict with 'deps' and 'changelog' keys
        as_agentspec_yaml: True for YAML format, False for plain text

    Returns:
        Docstring with injected metadata sections
    """
    if not metadata:
        return llm_output

    deps_data = metadata.get('deps', {})
    changelog_data = metadata.get('changelog', [])

    if as_agentspec_yaml:
        # YAML format: inject deps and changelog sections
        deps_yaml = "\n    deps:\n"
        if deps_data.get('calls'):
            deps_yaml += "      calls:\n"
            for call in deps_data['calls']:
                deps_yaml += f"        - {call}\n"
        if deps_data.get('imports'):
            deps_yaml += "      imports:\n"
            for imp in deps_data['imports']:
                deps_yaml += f"        - {imp}\n"

        changelog_yaml = "\n    changelog:\n"
        if changelog_data:
            for entry in changelog_data:
                changelog_yaml += f"      - \"{entry}\"\n"
        else:
            changelog_yaml += "      - \"No git history available\"\n"

        # Inject deps before "why:" section
        if "why:" in llm_output or "why |" in llm_output:
            output = re.sub(
                r'(\n\s*why[:\|])',
                deps_yaml + r'\1',
                llm_output,
                count=1
            )
        else:
            output = re.sub(
                r'(\n\s*what:.*?\n(?:\s+.*\n)*)',
                r'\1' + deps_yaml,
                llm_output,
                count=1,
                flags=re.DOTALL
            )

        # Inject changelog before closing tag
        if "---/agentspec" in output:
            if "changelog:" in output:
                output = re.sub(
                    r'changelog:.*?(?=---/agentspec)',
                    changelog_yaml.strip(),
                    output,
                    flags=re.DOTALL
                )
            else:
                last_pos = output.rfind("---/agentspec")
                output = output[:last_pos] + changelog_yaml + "    " + output[last_pos:]
        else:
            output += changelog_yaml

        return output
    else:
        # Plain text format: append deterministic sections
        changelog_content = "CHANGELOG (from git history):\n"
        if changelog_data:
            for entry in changelog_data:
                changelog_content += f"{entry}\n"
        else:
            changelog_content += "No git history available\n"

        # Strip any LLM-emitted CHANGELOG/DEPENDENCIES sections
        llm_output = re.sub(
            r'(?ms)^\s*CHANGELOG \(from git history\):\s*\n.*?(?=^(?:FUNCTION CODE DIFF SUMMARY|DEPENDENCIES \(from code analysis\):|WHAT:|WHY:)|\Z)',
            '',
            llm_output,
        )
        llm_output = re.sub(
            r'(?ms)^\s*DEPENDENCIES \(from code analysis\):\s*\n.*?(?=^(?:CHANGELOG \(from git history\):|FUNCTION CODE DIFF SUMMARY|WHAT:|WHY:)|\Z)',
            '',
            llm_output,
        )

        # Build deterministic deps section
        deps_text = "DEPENDENCIES (from code analysis):\n"
        if deps_data.get('calls'):
            deps_text += "Calls: " + ", ".join(deps_data['calls']) + "\n"
        if deps_data.get('imports'):
            deps_text += "Imports: " + ", ".join(deps_data['imports']) + "\n"

        # Append deterministic sections
        if not llm_output.endswith("\n"):
            llm_output += "\n"
        llm_output += "\n" + deps_text + "\n" + changelog_content

        return llm_output


def _compile_ok(path: Path) -> bool:
    try:
        py_compile.compile(str(path), doraise=True)
        return True
    except Exception:
        return False


def apply_docstring_with_metadata(
    filepath: Path,
    lineno: int,
    func_name: str,
    narrative: str,
    metadata: Dict[str, Any],
    *,
    as_agentspec_yaml: bool = False,
    force_context: bool = False,
    diff_summary_text: Optional[str] = None,
) -> bool:
    """
    Insert narrative-only docstring first, verify syntax, then inject deterministic
    metadata (deps/changelog) and verify syntax again. If both passes succeed,
    replace the target file atomically.

    Notes
    - This function deliberately avoids exposing metadata to any LLM.
    - Works by writing to a temporary copy, then replacing the original file.
    """
    # Import insert_docstring_at_line from monolithic generate.py
    # TODO: Move insert_docstring_at_line to its own modular location
    # For now, this is the ONLY acceptable import from generate.py because
    # insert_docstring_at_line handles complex AST manipulation that
    # hasn't been modularized yet
    from agentspec.generate import insert_docstring_at_line

    src = Path(filepath)
    if not src.exists():
        return False

    # Create temp copy in same directory for atomic replace semantics
    with open(src, "r", encoding="utf-8") as f:
        original = f.read()

    fd, tmp_path_str = tempfile.mkstemp(prefix=src.stem + ".", suffix=src.suffix, dir=str(src.parent))
    os.close(fd)
    tmp_path = Path(tmp_path_str)
    try:
        tmp_path.write_text(original, encoding="utf-8")

        # Phase 1: narrative only
        ok = insert_docstring_at_line(tmp_path, lineno, func_name, narrative, force_context)
        if not ok or not _compile_ok(tmp_path):
            return False

        # Phase 2: deterministic metadata (never shown to LLM)
        # Use LOCAL inject_deterministic_metadata (not from generate.py)
        doc_with_meta = inject_deterministic_metadata(narrative, metadata, as_agentspec_yaml)
        if diff_summary_text:
            # Append diff summary as a separate section after metadata
            doc_with_meta += "\n\n" + diff_summary_text.strip() + "\n"

        ok2 = insert_docstring_at_line(tmp_path, lineno, func_name, doc_with_meta, force_context)
        if not ok2 or not _compile_ok(tmp_path):
            return False

        # Replace original atomically
        os.replace(tmp_path, src)
        return True
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

