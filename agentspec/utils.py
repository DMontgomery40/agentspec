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

import fnmatch
import os
import subprocess
from pathlib import Path
from typing import Iterable, List, Set, Optional


DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git", ".hg", ".svn",
    ".venv", "venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".tox", ".eggs",
    "build", "dist", "site-packages", "node_modules",
    ".idea", ".vscode",
}


def _is_excluded_by_dir(path: Path) -> bool:
    """
        """
    for part in path.parts:
        if part in DEFAULT_EXCLUDE_DIRS:
            return True
    return False


def _find_git_root(start: Path) -> Path | None:
    """
        """
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for ancestor in [cur, *cur.parents]:
        if (ancestor / ".git").exists():
            return ancestor
    return None


def _git_check_ignore(repo_root: Path, paths: List[Path]) -> Set[Path]:
    """
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


def _find_agentspecignore(repo_root: Path) -> Path | None:
    """Find .agentspecignore file in repo root."""
    if repo_root and (repo_root / ".agentspecignore").exists():
        return repo_root / ".agentspecignore"
    return None


def _parse_agentspecignore(ignore_path: Path, repo_root: Path) -> List[str]:
    """Parse .agentspecignore file and return list of patterns (filtered for comments and empty lines)."""
    try:
        patterns = []
        for line in ignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            patterns.append(line)
        return patterns
    except Exception:
        return []


def _matches_pattern(path: Path, pattern: str, repo_root: Path) -> bool:
    """
    Check if a path matches a gitignore-style pattern.
    
    Supports:
    - * wildcards (via fnmatch)
    - **/ for any directory depth
    - Leading / for absolute match from repo root
    - Trailing / for directories only
    """
    try:
        # Convert path to relative path from repo root
        rel_path = path.resolve().relative_to(repo_root.resolve())
        rel_str = str(rel_path).replace('\\', '/')  # Normalize separators
        
        # Handle leading / (match from root)
        pattern = pattern.strip()
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Must match from beginning
            return fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(rel_str, pattern + '/*')
        
        # Handle trailing / (directory only)
        dir_only = pattern.endswith('/')
        if dir_only:
            pattern = pattern[:-1]
        
        # Handle **/ (any directory depth)
        if pattern.startswith('**/'):
            pattern = pattern[3:]
        elif '**/' in pattern:
            # Replace **/ with * for fnmatch
            pattern = pattern.replace('**/', '*')
        
        # Check if any component matches
        parts = rel_str.split('/')
        for i in range(len(parts)):
            test_path = '/'.join(parts[i:])
            if fnmatch.fnmatch(test_path, pattern):
                if dir_only:
                    # For directory patterns, check if it's actually a directory
                    test_full = repo_root / test_path
                    return test_full.is_dir()
                return True
        
        # Also check full path
        if fnmatch.fnmatch(rel_str, pattern):
            if dir_only:
                test_full = repo_root / rel_str
                return test_full.is_dir()
            return True
        
        return False
    except Exception:
        return False


def _check_agentspecignore(path: Path, repo_root: Path | None) -> bool:
    """Check if a path is ignored by .agentspecignore. Returns True if ignored."""
    if not repo_root:
        return False
    
    ignore_file = _find_agentspecignore(repo_root)
    if not ignore_file:
        return False
    
    patterns = _parse_agentspecignore(ignore_file, repo_root)
    for pattern in patterns:
        if _matches_pattern(path, pattern, repo_root):
            return True
    
    return False


def collect_python_files(target: Path) -> List[Path]:
    """
        """
    if target.is_file():
        if target.suffix != ".py" or _is_excluded_by_dir(target):
            return []
        repo_root = _find_git_root(target)
        if repo_root:
            # Check .gitignore
            ignored = _git_check_ignore(repo_root, [target])
            if target.resolve() in ignored:
                return []
            # Check .agentspecignore
            if _check_agentspecignore(target, repo_root):
                return []
        return [target]

    # Directory
    all_files = [p for p in target.rglob("*.py") if p.is_file() and not _is_excluded_by_dir(p)]

    repo_root = _find_git_root(target)
    if repo_root:
        # Check .gitignore
        ignored = _git_check_ignore(repo_root, all_files)
        files = [p for p in all_files if p.resolve() not in ignored]
        # Check .agentspecignore
        files = [p for p in files if not _check_agentspecignore(p, repo_root)]
    else:
        files = all_files

    files.sort(key=lambda p: str(p))
    return files


def collect_source_files(target: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """
    Recursively discover source files with specified extensions, respecting .gitignore/.agentspecignore.

    Args:
        target: File or directory path to search
        extensions: List of file extensions to collect (e.g., [".py", ".js", ".ts"])
                   Defaults to [".py", ".js", ".jsx", ".ts", ".tsx"] if None

    Returns:
        Sorted list of absolute Path objects for matching source files

        """
    if extensions is None:
        extensions = [".py", ".js", ".jsx", ".ts", ".tsx"]

    # Normalize extensions (ensure leading dot)
    extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    if target.is_file():
        # Check extension matches
        if target.suffix not in extensions or _is_excluded_by_dir(target):
            return []

        repo_root = _find_git_root(target)
        if repo_root:
            # Check .gitignore
            ignored = _git_check_ignore(repo_root, [target])
            if target.resolve() in ignored:
                return []
            # Check .agentspecignore
            if _check_agentspecignore(target, repo_root):
                return []
        return [target]

    # Directory - collect all matching extensions
    all_files = []
    for ext in extensions:
        pattern = f"*{ext}"
        all_files.extend([p for p in target.rglob(pattern) if p.is_file() and not _is_excluded_by_dir(p)])

    repo_root = _find_git_root(target)
    if repo_root:
        # Check .gitignore
        ignored = _git_check_ignore(repo_root, all_files)
        files = [p for p in all_files if p.resolve() not in ignored]
        # Check .agentspecignore
        files = [p for p in files if not _check_agentspecignore(p, repo_root)]
    else:
        files = all_files

    files.sort(key=lambda p: str(p))
    return files


def load_env_from_dotenv(env_path: Optional[Path] = None, override: bool = False) -> Optional[Path]:
    """
        """
    # If a path is provided, use it directly
    candidates: List[Path] = []
    if env_path:
        candidates = [env_path]
    else:
        cwd = Path.cwd()
        # Walk up from CWD
        for p in [cwd, *cwd.parents]:
            candidates.append(p / ".env")
        # Git root
        git_root = _find_git_root(cwd)
        if git_root:
            candidates.append(git_root / ".env")
        # Package directory
        pkg_root = Path(__file__).resolve().parents[1]
        candidates.append(pkg_root / ".env")

    chosen: Optional[Path] = None
    for c in candidates:
        try:
            if c.exists() and c.is_file():
                chosen = c
                break
        except Exception:
            continue

    if not chosen:
        return None

    try:
        for line in chosen.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith('#') or '=' not in s:
                continue
            k, v = s.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if override or k not in os.environ:
                os.environ[k] = v
        return chosen
    except Exception:
        return None
