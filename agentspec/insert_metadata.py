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
    # Lazy import to avoid circulars
    from agentspec.generate import insert_docstring_at_line, inject_deterministic_metadata

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

