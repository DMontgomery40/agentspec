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
    """
    ---agentspec
    what: |
      Validates whether a Python file at the given path compiles successfully without syntax errors.

      Takes a Path object pointing to a Python source file and attempts to compile it using py_compile.compile()
      with the doraise=True flag, which causes compilation errors to be raised as exceptions rather than logged.

      Returns True if compilation succeeds (file is syntactically valid Python), False if any exception occurs
      during compilation (syntax errors, file not found, permission denied, encoding issues, etc.).

      Inputs:
        - path: Path object or path-like pointing to a .py file

      Outputs:
        - bool: True if file compiles cleanly, False otherwise

      Edge cases:
        - Non-existent files: Returns False (FileNotFoundError caught)
        - Unreadable files: Returns False (PermissionError caught)
        - Invalid encoding: Returns False (UnicodeDecodeError caught)
        - Syntax errors: Returns False (SyntaxError caught)
        - All exceptions are silently suppressed and treated as compilation failure
        deps:
          calls:
            - py_compile.compile
            - str
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - py_compile
            - tempfile
            - typing.Any
            - typing.Dict
            - typing.Optional


    why: |
      This utility provides a safe, non-throwing way to validate Python syntax before processing files.
      Using a broad Exception catch ensures robustness across all failure modes without requiring
      caller to handle multiple exception types. The boolean return value is simpler for conditional
      logic than exception handling. This is useful in metadata insertion workflows where you need to
      skip or flag files with syntax issues without halting the entire process.

    guardrails:
      - DO NOT rely on this for security validation—it only checks syntax, not code safety or intent
      - DO NOT use this as a substitute for actual linting or type checking tools
      - DO NOT assume False means the file is unreadable vs. syntactically invalid; both are treated identically
      - DO NOT call this on non-Python files; behavior is undefined for non-.py content

        changelog:
          - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
        ---/agentspec
    """
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
    ---agentspec
    what: |
      Single-pass docstring insertion with metadata injection.

      Builds the complete docstring (narrative + deterministic metadata) FIRST,
      then inserts it ONCE into the file.

      Supported languages:
      - Python (.py): uses insert_docstring_at_line() and py_compile
      - JS/TS (.js, .mjs, .jsx, .ts, .tsx): uses LanguageRegistry adapter.insert_docstring() and adapter.validate_syntax_string()

    deps:
      calls:
        - insert_docstring_at_line (Python)
        - LanguageRegistry.get_by_extension (JS/TS)
        - adapter.insert_docstring (JS/TS)
        - adapter.validate_syntax_string (JS/TS)
        - inject_deterministic_metadata
        - os.replace
        - py_compile.compile (Python)
      imports:
        - agentspec.generate (inject_deterministic_metadata, insert_docstring_at_line)
        - agentspec.langs.LanguageRegistry

    why: |
      Previous implementation did a "two-phase" insert that called insert_docstring TWICE,
      creating duplicate JSDoc blocks. This version builds the complete docstring first,
      then inserts it once.

    guardrails:
      - DO NOT call insert_docstring/insert_docstring_at_line more than ONCE per function
      - ALWAYS build the complete docstring (narrative + metadata) BEFORE inserting
      - ALWAYS operate on a temp copy and perform an atomic replace on success
      - ALWAYS route by file extension; do not try to parse JS with Python tooling

    changelog:
      - "2025-11-01: Fix duplicate JSDoc insertion bug - build complete docstring first, insert once"
      - "2025-11-01: Add JS/TS support and unify two-phase flow"
    ---/agentspec
    """
    # Lazy imports to avoid circulars and optional deps at import time
    from agentspec.generate import insert_docstring_at_line, inject_deterministic_metadata

    src = Path(filepath)
    if not src.exists():
        return False

    # Build the complete docstring FIRST (narrative + deterministic metadata)
    doc_with_meta = inject_deterministic_metadata(narrative, metadata, as_agentspec_yaml)
    if diff_summary_text:
        doc_with_meta = doc_with_meta.rstrip() + "\n\n" + diff_summary_text.strip() + "\n"

    # Prepare tmp copy
    with open(src, "r", encoding="utf-8") as f:
        original = f.read()

    fd, tmp_path_str = tempfile.mkstemp(prefix=src.stem + ".", suffix=src.suffix, dir=str(src.parent))
    os.close(fd)
    tmp_path = Path(tmp_path_str)
    try:
        tmp_path.write_text(original, encoding="utf-8")

        ext = src.suffix.lower()
        is_python = ext == ".py"
        is_js = ext in {".js", ".mjs", ".jsx", ".ts", ".tsx"}

        # Insert the COMPLETE docstring ONCE
        if is_python:
            # Add force-context marker for Python
            ok = insert_docstring_at_line(tmp_path, lineno, func_name, doc_with_meta, force_context)
            if not ok or not _compile_ok(tmp_path):
                return False
        elif is_js:
            # Use JS adapter
            from agentspec.langs import LanguageRegistry
            adapter = LanguageRegistry.get_by_extension(ext)
            if adapter is None:
                return False
            
            # Add force-context marker inside JSDoc for JS/TS
            if force_context:
                doc_with_meta = doc_with_meta.rstrip() + f"\nAGENTSPEC_CONTEXT: function {func_name} documented\n"
            
            try:
                adapter.insert_docstring(tmp_path, lineno, doc_with_meta)
                # Validate via adapter on the modified content
                content = tmp_path.read_text(encoding="utf-8", errors="ignore")
                adapter.validate_syntax_string(content, tmp_path)
            except Exception:
                return False
        else:
            # Unsupported language
            return False

        # Atomically replace
        os.replace(tmp_path, src)
        return True
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

