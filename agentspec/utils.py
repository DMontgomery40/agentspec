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
    Brief one-line description.
    Determines whether a file path should be excluded from processing based on directory name components.

    WHAT THIS DOES:
    - Iterates through all directory components (parts) of a given Path object
    - Checks each component against a predefined set of directory names stored in DEFAULT_EXCLUDE_DIRS
    - Returns True immediately upon finding the first matching excluded directory name, short-circuiting further iteration
    - Returns False if no excluded directory names are found in any part of the path
    - This function enables efficient filtering of paths that contain version control directories (.git, .venv, etc.) or other directories that should be ignored during file traversal operations
    - The matching is performed on individual path components, so a directory named ".venv" anywhere in the path hierarchy will cause the entire path to be excluded

    DEPENDENCIES:
    - Called by: File traversal and filtering logic in agentspec codebase (likely called during repository scanning operations)
    - Calls: No function calls; uses only built-in Path.parts property and set membership testing
    - Imports used: pathlib.Path (for path manipulation and component extraction)
    - External services: None; this is a pure utility function with no external dependencies
    - Related module-level constant: DEFAULT_EXCLUDE_DIRS (must be defined in the same module as a set or iterable of directory names to exclude)

    WHY THIS APPROACH:
    - This implementation uses a simple linear scan through path components rather than regex matching or more complex path analysis, prioritizing readability and maintainability over micro-optimizations
    - The early return (True on first match) provides performance benefits for paths with excluded directories near the root, avoiding unnecessary iteration through remaining components
    - Path.parts is used instead of string splitting to ensure cross-platform compatibility (handles both forward and backward slashes correctly on Windows, macOS, and Linux)
    - Set membership testing (if part in DEFAULT_EXCLUDE_DIRS) is O(1) average case, making this function efficient even for deeply nested paths
    - Alternative approaches considered but not used: regex pattern matching (overly complex for simple string matching), os.path.walk with filtering (would require different function signature), or checking only the immediate parent directory (insufficient for excluding nested .venv or .git directories at any depth)

    CHANGELOG:
    - 2025-10-29: Initial implementation; added to honor .gitignore and .venv exclusion patterns during repository scanning

    AGENT INSTRUCTIONS:
    - DO NOT modify the function signature or return type (must accept Path and return bool)
    - DO NOT change the early-return logic that short-circuits on first match
    - DO NOT assume DEFAULT_EXCLUDE_DIRS is defined locally; verify it exists at module scope before modifying
    - DO NOT use string-based path manipulation instead of Path.parts
    - ALWAYS preserve the cross-platform path handling provided by pathlib.Path
    - ALWAYS maintain the O(1) set membership check for performance
    - ALWAYS ensure DEFAULT_EXCLUDE_DIRS is properly initialized before this function is called
    - NOTE: This function will exclude ANY path containing an excluded directory name at ANY level of nesting; ensure DEFAULT_EXCLUDE_DIRS contains only directory names that should be universally excluded (e.g., ".git", ".venv", "__pycache__")
    - NOTE: The function operates on path components only and does not perform filesystem checks; a path can be excluded even if the directory does not actually exist on disk
    """
    print(f"[AGENTSPEC_CONTEXT] _is_excluded_by_dir: Iterates through all directory components (parts) of a given Path object | Checks each component against a predefined set of directory names stored in DEFAULT_EXCLUDE_DIRS | Returns True immediately upon finding the first matching excluded directory name, short-circuiting further iteration")
    for part in path.parts:
        if part in DEFAULT_EXCLUDE_DIRS:
            return True
    return False


def _find_git_root(start: Path) -> Path | None:
    """
    Brief one-line description.
    Locates the root directory of a Git repository by traversing upward from a given starting path.

    WHAT THIS DOES:
    - Accepts a Path object (file or directory) and resolves it to an absolute path
    - If the path points to a file, extracts its parent directory as the starting search point
    - Iterates through the directory hierarchy from the current location upward through all ancestor directories
    - For each directory in the traversal chain, checks whether a `.git` subdirectory exists at that location
    - Returns the first ancestor directory containing a `.git` folder (indicating a Git repository root), or None if no Git repository is found in the entire ancestry chain
    - This function is used to identify repository boundaries for operations like respecting .gitignore files and determining project scope

    DEPENDENCIES:
    - Called by: [Inferred to be called by repository scanning/initialization functions in agentspec that need to honor .gitignore and .venv conventions]
    - Calls: start.resolve() [pathlib.Path method to convert to absolute path], cur.is_file() [pathlib.Path method to check if path is a file], (ancestor / ".git").exists() [pathlib.Path methods for path joining and existence checking]
    - Imports used: __future__.annotations [for PEP 563 postponed evaluation of type hints], pathlib.Path [for cross-platform filesystem path manipulation]
    - External services: None; this is a pure filesystem operation with no external dependencies

    WHY THIS APPROACH:
    - Using pathlib.Path provides cross-platform compatibility (Windows, macOS, Linux) without manual path separator handling
    - The resolve() call ensures absolute paths are used, preventing issues with relative path traversal and symlink resolution
    - The file-to-parent conversion handles both file and directory inputs gracefully, allowing callers to pass either without special handling
    - Iterating through [cur, *cur.parents] is more efficient than a while loop with manual parent traversal, as it leverages pathlib's built-in parents tuple
    - Checking for .git directory existence is the standard Git convention for identifying repository roots (more reliable than checking for .gitignore alone, which may not exist in all repos)
    - Early return on first match avoids unnecessary traversal of the entire filesystem hierarchy
    - Returning None (rather than raising an exception) allows graceful degradation when operating outside a Git repository

    CHANGELOG:
    - 2025-10-29: Initial implementation as part of feature to honor .gitignore and .venv; added agentspec YAML generation support

    AGENT INSTRUCTIONS:
    - DO NOT modify the .git directory name check (it is a Git standard and must remain hardcoded)
    - DO NOT change the return type from Path | None to raise exceptions instead (callers depend on None for non-repository contexts)
    - DO NOT remove the file-to-parent conversion logic (it enables flexible input handling)
    - ALWAYS preserve the resolve() call to ensure absolute path handling
    - ALWAYS maintain the iteration order from current directory upward (ancestors must be checked in order from closest to furthest)
    - NOTE: This function performs filesystem I/O operations (exists() checks) for each ancestor directory; in deeply nested directory structures or slow filesystems, this could be a performance bottleneck if called repeatedly without caching
    """
    print(f"[AGENTSPEC_CONTEXT] _find_git_root: Accepts a Path object (file or directory) and resolves it to an absolute path | If the path points to a file, extracts its parent directory as the starting search point | Iterates through the directory hierarchy from the current location upward through all ancestor directories")
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for ancestor in [cur, *cur.parents]:
        if (ancestor / ".git").exists():
            return ancestor
    return None


def _git_check_ignore(repo_root: Path, paths: List[Path]) -> Set[Path]:
    """
    Brief one-line description.
    Batch-check which file paths are ignored by Git according to .gitignore rules, returning only the ignored subset.

    WHAT THIS DOES:
    - Accepts a repository root directory and a list of file paths, then queries Git's .gitignore rules to determine which paths should be ignored
    - Converts all input paths to absolute paths, then to relative paths from the repo root for efficient batch processing
    - Chunks the relative paths into groups of 1024 to avoid overwhelming subprocess stdin with massive payloads
    - For each chunk, invokes `git check-ignore -z --stdin` with NUL-delimited input to handle arbitrary filenames (including those with spaces, newlines, or special characters)
    - Parses the NUL-delimited output from Git, decodes each ignored path back to absolute form, and accumulates them in a Set[Path]
    - Returns an empty set if Git is unavailable, fails, or if the input paths list is empty; gracefully degrades rather than raising exceptions
    - Ensures all returned paths are resolved to their canonical absolute form for consistency with caller expectations

    DEPENDENCIES:
    - Called by: [Inferred to be called by file-discovery or filtering logic in agentspec that needs to exclude .gitignore'd files from processing]
    - Calls: subprocess.run (to invoke git check-ignore), Path.resolve(), Path.relative_to(), str.encode(), bytes.split(), str.decode()
    - Imports used: pathlib.Path, subprocess, typing.List, typing.Set, __future__.annotations
    - External services: Git executable (must be available in PATH or discoverable via -C flag); relies on .gitignore files in the repository

    WHY THIS APPROACH:
    - Batch processing with chunking avoids subprocess stdin buffer limits and keeps memory usage bounded; 1024-path chunks balance throughput against payload size
    - NUL-delimited format (--stdin with -z flag) is the only reliable way to handle filenames with embedded newlines, spaces, or other special characters without escaping ambiguity
    - Relative-path conversion before passing to Git reduces payload size and ensures Git interprets paths relative to repo_root correctly
    - Absolute path resolution on output ensures caller receives consistent, canonical paths regardless of current working directory
    - Silent exception handling (return empty set on any error) allows graceful degradation when Git is not installed or repository is not a Git repo, rather than crashing the entire agent
    - Resolving paths twice (input and output) ensures idempotency and consistency with Path semantics

    CHANGELOG:
    - 2025-10-29: Initial implementation to honor .gitignore rules during file discovery; supports arbitrary filenames via NUL-delimited Git protocol; chunks large path lists to avoid subprocess buffer exhaustion

    AGENT INSTRUCTIONS:
    - DO NOT modify the chunking size (1024) without benchmarking against large repositories; DO NOT remove the try-except wrapper as it enables graceful degradation; DO NOT change the NUL delimiter scheme as it is the only reliable approach for arbitrary filenames; DO NOT assume Git is always available
    - ALWAYS resolve paths to absolute form before returning; ALWAYS use relative_to(repo_root) before passing to Git; ALWAYS handle empty input lists early; ALWAYS preserve the NUL-delimited protocol (-z flag) when invoking git check-ignore; ALWAYS decode bytes output back to strings before constructing Path objects
    - NOTE: This function silently returns an empty set on any exception, which means callers cannot distinguish between "no files ignored" and "Git check failed"; this is intentional for robustness but may mask configuration issues. The function assumes repo_root is a valid Git repository; behavior is undefined if called on a non-Git directory (Git will simply report no matches). Performance scales linearly with the number of paths; very large path lists (>100k) may benefit from further optimization or caching.
    """
    print(f"[AGENTSPEC_CONTEXT] _git_check_ignore: Accepts a repository root directory and a list of file paths, then queries Git's .gitignore rules to determine which paths should be ignored | Converts all input paths to absolute paths, then to relative paths from the repo root for efficient batch processing | Chunks the relative paths into groups of 1024 to avoid overwhelming subprocess stdin with massive payloads")
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
    Brief one-line description.

    Recursively discovers Python files within a target path, respecting .gitignore rules and excluding common non-source directories.

    WHAT THIS DOES:
    - Accepts either a single file path or a directory path as the `target` parameter
    - For file inputs: validates that the file has a .py extension, is not in an excluded directory, and is not ignored by .gitignore; returns a single-element list containing the file or an empty list if validation fails
    - For directory inputs: recursively globs all .py files using `target.rglob("*.py")`, filters out files in excluded directories (e.g., .venv, __pycache__, .git, build, dist), then applies .gitignore filtering if a git repository root is found
    - Returns a sorted list of absolute Path objects representing all discovered Python files that pass all filters
    - Returns an empty list if the target is a non-.py file, is in an excluded directory, or is gitignored
    - Gracefully degrades to unfiltered discovery if no git repository root is found (still excludes common directories)

    DEPENDENCIES:
    - Called by: [inferred to be called by higher-level discovery/collection routines in agentspec, likely from a main entry point or CLI handler]
    - Calls: _find_git_root (locates the root directory of a git repository), _git_check_ignore (queries git to determine which files are ignored), _is_excluded_by_dir (checks if a path is within a common exclusion directory like .venv or __pycache__)
    - Imports used: pathlib.Path (for filesystem path operations), typing.List (for return type annotation), subprocess (used indirectly by _git_check_ignore), os (used indirectly by helper functions)
    - External services: git command-line tool (invoked via subprocess to check .gitignore status)

    WHY THIS APPROACH:
    - Two-path branching (file vs. directory) allows efficient handling of both single-file and bulk discovery scenarios without redundant logic
    - .gitignore integration respects developer intent by excluding files already marked as ignored, reducing noise in analysis and respecting repository conventions
    - Excluded directory filtering (via _is_excluded_by_dir) prevents traversal into virtual environments, build artifacts, and cache directories, which would be wasteful and incorrect to analyze
    - Graceful degradation when git is unavailable or target is not in a repository ensures the function remains useful in non-git contexts
    - Sorting by string representation of paths ensures deterministic, human-readable output order across different runs and platforms
    - Use of resolved paths (target.resolve()) in gitignore checks ensures consistent comparison even with symlinks or relative path variations
    - Lazy evaluation of repo_root and ignored set avoids expensive git operations when not needed (e.g., for single non-gitignored files)

    CHANGELOG:
    - 2025-10-29: Initial implementation with .gitignore and excluded directory support; honors .venv, __pycache__, .git, build, dist, and similar common exclusions; added as part of agentspec YAML generation feature

    AGENT INSTRUCTIONS:
    - DO NOT remove or bypass the _is_excluded_by_dir check, as it prevents analysis of virtual environments and build artifacts
    - DO NOT change the sorting key from `str(p)` without ensuring output remains deterministic across platforms
    - DO NOT modify the .resolve() calls in gitignore comparisons, as they are necessary for correct path matching with symlinks
    - DO NOT remove the graceful fallback when repo_root is None, as this allows the function to work outside git repositories
    - ALWAYS preserve the two-branch logic (file vs. directory) to maintain efficiency and clarity
    - ALWAYS ensure that returned paths are absolute (via Path.resolve() or rglob behavior) for consistency with downstream consumers
    - ALWAYS maintain the order of operations: suffix check → excluded dir check → gitignore check, to fail fast on obvious non-matches
    - NOTE: This function depends on external git availability; if git is not installed or the target is not in a git repository, gitignore filtering is silently skipped (not an error condition)
    - NOTE: Performance scales with the number of .py files in the target tree; for very large codebases, gitignore queries may be slow; consider caching results if called repeatedly on the same tree
    """
    print(f"[AGENTSPEC_CONTEXT] collect_python_files: Accepts either a single file path or a directory path as the `target` parameter | For file inputs: validates that the file has a .py extension, is not in an excluded directory, and is not ignored by .gitignore; returns a single-element list containing the file or an empty list if validation fails | For directory inputs: recursively globs all .py files using `target.rglob(\"*.py\")`, filters out files in excluded directories (e.g., .venv, __pycache__, .git, build, dist), then applies .gitignore filtering if a git repository root is found")
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


def load_env_from_dotenv(env_path: Optional[Path] = None, override: bool = False) -> Optional[Path]:
    """
    Load environment variables from a .env file if present.

    Search order when env_path is None:
    1) Current working directory and its parents
    2) Git repository root (if discovered) and its .env
    3) The agentspec package directory root

    Only sets variables that are not already present in os.environ, unless
    override=True.

    Returns the Path of the loaded .env file or None if not found.
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
