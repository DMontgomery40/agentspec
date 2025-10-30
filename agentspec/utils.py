#!/usr/bin/env python3
"""
Utility helpers for file discovery with .gitignore awareness.

WHAT THIS DOES:
- Collects Python source files under a target path while ignoring:
  - Entries ignored by .gitignore (when inside a Git repo and git is available)
  - Common virtualenv, VCS, cache, build, and IDE directories (fallback)

WHY THIS APPROACH:
- Prefer Git's native ignore engine when available for exact parity with gitignore.
- Fallback to a conservative denylist to avoid processing environments like .venv.

GUARDRAILS:
- DO NOT import heavy third-party libraries here; keep this zero-dep.
- DO NOT require Git; gracefully degrade when not available.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable, List, Set


DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git", ".hg", ".svn",
    ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".tox", ".eggs",
    "build", "dist", "site-packages", "node_modules",
    ".idea", ".vscode",
}


def _is_excluded_by_dir(path: Path) -> bool:
    for part in path.parts:
        if part in DEFAULT_EXCLUDE_DIRS:
            return True
    return False


def _find_git_root(start: Path) -> Path | None:
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for ancestor in [cur, *cur.parents]:
        if (ancestor / ".git").exists():
            return ancestor
    return None


def _git_check_ignore(repo_root: Path, paths: List[Path]) -> Set[Path]:
    """
    Batch check which paths are ignored by Git according to .gitignore.
    Returns the subset of input paths that are ignored.
    """
    ignored: Set[Path] = set()
    if not paths:
        return ignored
    try:
        # Use check-ignore with --stdin and NUL delim to handle arbitrary filenames
        rels = [p.resolve().relative_to(repo_root) for p in paths]
        # Chunk to avoid huge stdin payloads
        CHUNK = 1024
        for i in range(0, len(rels), CHUNK):
            chunk = rels[i : i + CHUNK]
            payload = "\0".join(str(p) for p in chunk).encode() + b"\0"
            proc = subprocess.run(
                ["git", "-C", str(repo_root), "check-ignore", "-z", "--stdin"],
                input=payload,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            out = proc.stdout
            if out:
                for rel_s in out.split(b"\0"):
                    if not rel_s:
                        continue
                    ignored.add((repo_root / rel_s.decode()).resolve())
    except Exception:
        # If git is not available or fails, just return empty set
        return set()
    return ignored


def collect_python_files(target: Path) -> List[Path]:
    """
    Discover Python files under target honoring .gitignore if possible and
    excluding common environment/cache/build directories.
    """
    if target.is_file():
        if target.suffix != ".py" or _is_excluded_by_dir(target):
            return []
        repo_root = _find_git_root(target)
        if repo_root:
            ignored = _git_check_ignore(repo_root, [target])
            return [] if target.resolve() in ignored else [target]
        return [target]

    # Directory
    all_files = [p for p in target.rglob("*.py") if p.is_file() and not _is_excluded_by_dir(p)]

    repo_root = _find_git_root(target)
    if repo_root:
        ignored = _git_check_ignore(repo_root, all_files)
        files = [p for p in all_files if p.resolve() not in ignored]
    else:
        files = all_files

    files.sort(key=lambda p: str(p))
    return files

