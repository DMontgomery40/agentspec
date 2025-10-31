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
    ---agentspec
    what: |
      Checks if a file path contains any excluded directory names by iterating through all path components.

      Inputs:
      - path: A pathlib.Path object representing a file or directory path

      Behavior:
      - Decomposes the path into individual components using Path.parts (cross-platform safe)
      - Iterates through each component sequentially
      - Compares each component against DEFAULT_EXCLUDE_DIRS set for membership
      - Returns True immediately upon finding the first excluded directory name
      - Returns False if iteration completes without matches

      Outputs:
      - Boolean: True if any path component matches an excluded directory name, False otherwise

      Edge cases:
      - Handles nested excluded directories at any depth (e.g., .git/objects/pack)
      - Works correctly with relative and absolute paths
      - Preserves Windows and Unix path separator semantics via pathlib.Path
      - Empty paths or single-component paths are handled safely
        deps:
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      Enables efficient filtering of version control, build, and cache directories during file system traversal without recursing into excluded subtrees.

      Design rationale:
      - Early return on first match optimizes common case where excluded dirs appear near root
      - Set membership testing (DEFAULT_EXCLUDE_DIRS) provides O(1) lookup per component
      - Path.parts abstraction ensures code works identically on Windows and Unix without manual separator handling
      - Checking all components catches excluded dirs at any nesting level, preventing accidental traversal into .venv/lib or .git/objects

    guardrails:
      - DO NOT use string.split() instead of Path.parts; manual splitting breaks cross-platform compatibility and requires separator awareness
      - DO NOT assume DEFAULT_EXCLUDE_DIRS is defined; verify it exists at module scope before calling this function
      - ALWAYS use pathlib.Path for path decomposition to maintain platform independence
      - ALWAYS ensure DEFAULT_EXCLUDE_DIRS contains only universally excluded directory names (.git, .venv, __pycache__, node_modules, etc.) that should never be traversed
      - DO NOT modify the path object; this function is read-only and must remain side-effect free

        changelog:
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
        ---/agentspec
    """
    for part in path.parts:
        if part in DEFAULT_EXCLUDE_DIRS:
            return True
    return False


def _find_git_root(start: Path) -> Path | None:
    """
    ---agentspec
    what: |
      Locates the root directory of a Git repository by traversing upward from a starting path.

      Accepts a Path object representing either a file or directory and resolves it to an absolute path.
      If the input path points to a file, extracts its parent directory as the starting search point.
      Iterates through the directory hierarchy from the current location upward through all ancestor directories.
      For each directory in the traversal chain, checks whether a `.git` subdirectory exists at that location.
      Returns the first ancestor directory containing a `.git` folder (indicating a Git repository root), or None if no Git repository is found in the entire ancestry chain.

      Edge cases handled:
      - File inputs are converted to their parent directory before searching
      - Symlinks are resolved to their canonical paths via resolve()
      - Returns None gracefully when operating outside any Git repository
      - Efficiently terminates on first match without traversing entire filesystem
        deps:
          calls:
            - cur.is_file
            - exists
            - start.resolve
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      Enables repository boundary detection for operations like respecting .gitignore files and determining project scope without making external Git subprocess calls.

      Using pathlib.Path provides cross-platform compatibility (Windows, macOS, Linux) without manual path separator handling.
      The resolve() call ensures absolute paths are used, preventing issues with relative path traversal and symlink resolution.
      The file-to-parent conversion handles both file and directory inputs gracefully, allowing callers to pass either without special handling.
      Iterating through [cur, *cur.parents] is more efficient than a while loop with manual parent traversal, as it leverages pathlib's built-in parents tuple.
      Checking for .git directory existence is the standard Git convention for identifying repository roots (more reliable than checking for .gitignore alone, which may not exist in all repos).
      Early return on first match avoids unnecessary traversal of the entire filesystem hierarchy.
      Returning None (rather than raising an exception) allows graceful degradation when operating outside a Git repository, enabling callers to implement fallback behavior.

    guardrails:
      - DO NOT modify the .git directory name check; it is a Git standard and must remain hardcoded
      - DO NOT change the return type from Path | None to raise exceptions instead; callers depend on None for non-repository contexts
      - DO NOT remove the file-to-parent conversion logic; it enables flexible input handling for both files and directories
      - ALWAYS preserve the resolve() call to ensure absolute path handling and symlink resolution
      - ALWAYS maintain the iteration order from current directory upward; ancestors must be checked in order from closest to furthest
      - NOTE: This function performs filesystem I/O operations (exists() checks) for each ancestor directory; in deeply nested directory structures or slow filesystems, this could be a performance bottleneck if called repeatedly without caching

        changelog:
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support"
          - "- Accepts a Path object (file or directory) and resolves it to an absolute path"
          - "- If the path points to a file, extracts its parent directory as the starting search point"
          - "- Iterates through the directory hierarchy from the current location upward through all ancestor directories"
          - "- For each directory in the traversal chain, checks whether a `.git` subdirectory exists at that location"
          - "- Returns the first ancestor directory containing a `.git` folder (indicating a Git repository root), or None if no Git repository is found in the entire ancestry chain"
          - "- This function is used to identify repository boundaries for operations like respecting .gitignore files and determining project scope"
          - "- Called by: [Inferred to be called by repository scanning/initialization functions in agentspec that need to honor .gitignore and .venv conventions]"
          - "- Calls: start.resolve() [pathlib.Path method to convert to absolute path], cur.is_file() [pathlib.Path method to check if path is a file], (ancestor / ".git").exists() [pathlib.Path methods for path joining and existence checking]"
          - "- Imports used: __future__.annotations [for PEP 563 postponed evaluation of type hints], pathlib.Path [for cross-platform filesystem path manipulation]"
          - "- External services: None; this is a pure filesystem operation with no external dependencies"
          - "- Using pathlib.Path provides cross-platform compatibility (Windows, macOS, Linux) without manual path separator handling"
          - "- The resolve() call ensures absolute paths are used, preventing issues with relative path traversal and symlink resolution"
          - "- The file-to-parent conversion handles both file and directory inputs gracefully, allowing callers to pass either without special handling"
          - "- Iterating through [cur, *cur.parents] is more efficient than a while loop with manual parent traversal, as it leverages pathlib's built-in parents tuple"
          - "- Checking for .git directory existence is the standard Git convention for identifying repository roots (more reliable than checking for .gitignore alone, which may not exist in all repos)"
          - "- Early return on first match avoids unnecessary traversal of the entire filesystem hierarchy"
          - "- Returning None (rather than raising an exception) allows graceful degradation when operating outside a Git repository"
          - "- 2025-10-29: Initial implementation as part of feature to honor .gitignore and .venv; added agentspec YAML generation support"
          - "- DO NOT modify the .git directory name check (it is a Git standard and must remain hardcoded)"
          - "- DO NOT change the return type from Path | None to raise exceptions instead (callers depend on None for non-repository contexts)"
          - "- DO NOT remove the file-to-parent conversion logic (it enables flexible input handling)"
          - "- ALWAYS preserve the resolve() call to ensure absolute path handling"
          - "- ALWAYS maintain the iteration order from current directory upward (ancestors must be checked in order from closest to furthest)"
          - "- NOTE: This function performs filesystem I/O operations (exists() checks) for each ancestor directory; in deeply nested directory structures or slow filesystems, this could be a performance bottleneck if called repeatedly without caching"
          - "-    print(f"[AGENTSPEC_CONTEXT] _find_git_root: Accepts a Path object (file or directory) and resolves it to an absolute path | If the path points to a file, extracts its parent directory as the starting search point | Iterates through the directory hierarchy from the current location upward through all ancestor directories")"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
        ---/agentspec
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
    ---agentspec
    what: |
      Batch-checks which file paths are ignored by Git according to .gitignore rules, returning only the ignored subset as a Set[Path].

      Converts input paths to absolute form, then to relative paths anchored at repo_root to minimize stdin payload. Chunks the relative paths into groups of 1024 to prevent subprocess buffer exhaustion on large file lists. Constructs NUL-delimited input payload (each path followed by \0) and invokes `git check-ignore -z --stdin` with stderr suppressed. Parses the NUL-delimited output by splitting on \0, decodes each segment back to a path string, resolves to absolute form, and accumulates into the ignored set. Returns empty set on any exception (Git unavailable, not a Git repository, or subprocess failure), enabling graceful degradation.
        deps:
          calls:
            - encode
            - ignored.add
            - join
            - len
            - out.split
            - p.resolve
            - range
            - rel_s.decode
            - relative_to
            - resolve
            - set
            - str
            - subprocess.run
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      NUL-delimited format (via -z flag) is the only reliable mechanism to handle filenames containing embedded newlines, spaces, or other special characters without escaping ambiguity or parsing errors. Chunking balances throughput and memory efficiency against subprocess buffer limits; 1024 paths per chunk is a conservative threshold that avoids payload bloat while maintaining reasonable batch size. Converting to relative paths before passing to Git reduces stdin size and ensures Git interprets paths correctly relative to the repository root. Silent exception handling allows the function to degrade gracefully when Git is unavailable or the directory is not a Git repository, rather than propagating errors to callers.

    guardrails:
      - DO NOT modify the chunking size (1024) without benchmarking against large file lists; changing it may cause subprocess buffer exhaustion or unnecessary overhead.
      - DO NOT remove the try-except wrapper; it ensures the function returns an empty set rather than raising exceptions when Git is unavailable or the repo is invalid.
      - DO NOT change the NUL delimiter scheme (\0); any other delimiter (newline, space, etc.) will fail on filenames containing those characters.
      - ALWAYS resolve paths to absolute form before returning; relative paths would be ambiguous to callers and inconsistent with input semantics.
      - ALWAYS use relative_to(repo_root) before passing paths to Git; this ensures Git interprets them correctly within the repository context.
      - ALWAYS preserve the -z flag with git check-ignore; without it, the command cannot reliably parse filenames with special characters.

        changelog:
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "-    Batch check which paths are ignored by Git according to .gitignore."
          - "-    Returns the subset of input paths that are ignored."
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
        ---/agentspec
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
    ---agentspec
    what: |
      Recursively discovers Python files in a target path, respecting .gitignore rules and excluding common non-source directories.

      For file input: validates .py extension and checks if the file is in an excluded directory or gitignored; returns a single-element list containing the file, or an empty list if validation fails.

      For directory input: recursively globs all .py files using rglob("*.py"), filters out files in excluded directories (.venv, __pycache__, .git, build, dist, and similar), then applies .gitignore filtering if a git repository root is found.

      Returns a sorted list of absolute Path objects representing all discovered Python files that pass all filters. Returns an empty list if the target is a non-.py file, is in an excluded directory, or is gitignored.

      Gracefully degrades to unfiltered discovery (still excluding common directories) if no git repository root is found, allowing the function to work outside git repositories.

      Edge cases: symlinks are resolved before gitignore comparison to ensure correct path matching; lazy evaluation of repo_root and ignored set avoids expensive git operations when not needed; sorting by string representation ensures deterministic, human-readable output across different runs and platforms.
        deps:
          calls:
            - _find_git_root
            - _git_check_ignore
            - _is_excluded_by_dir
            - files.sort
            - p.is_file
            - p.resolve
            - str
            - target.is_file
            - target.resolve
            - target.rglob
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      .gitignore integration respects developer intent by excluding files already marked as ignored, reducing noise in analysis and respecting repository conventions.

      Excluded directory filtering prevents wasteful traversal of virtual environments, build artifacts, and cache directories, which would be incorrect to analyze and degrade performance.

      Graceful degradation when git is unavailable or target is not in a repository ensures the function remains useful in non-git contexts.

      Two-path branching (file vs. directory) allows efficient handling of both single-file and bulk discovery scenarios without redundant logic.

      Use of resolved paths in gitignore checks ensures consistent comparison even with symlinks or relative path variations.

      Sorting by string representation of paths ensures deterministic output order across different runs and platforms, critical for reproducibility.

    guardrails:
      - DO NOT remove or bypass the _is_excluded_by_dir check; it prevents analysis of virtual environments and build artifacts that should not be traversed
      - DO NOT change the sorting key from `str(p)` without ensuring output remains deterministic across platforms
      - DO NOT modify the .resolve() calls in gitignore comparisons; they are necessary for correct path matching with symlinks
      - DO NOT remove the graceful fallback when repo_root is None; this allows the function to work outside git repositories
      - ALWAYS preserve the two-branch logic (file vs. directory) to maintain efficiency and clarity
      - ALWAYS ensure that returned paths are absolute for consistency with downstream consumers
      - ALWAYS maintain the order of operations: suffix check → excluded dir check → gitignore check, to fail fast on obvious non-matches
      - NOTE: This function depends on external git availability; if git is not installed or the target is not in a git repository, gitignore filtering is silently skipped (not an error condition)
      - NOTE: Performance scales with the number of .py files in the target tree; for very large codebases, gitignore queries may be slow; consider caching results if called repeatedly on the same tree

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Accepts either a single file path or a directory path as the `target` parameter"
          - "- For file inputs: validates that the file has a .py extension, is not in an excluded directory, and is not ignored by .gitignore; returns a single-element list containing the file or an empty list if validation fails"
          - "- For directory inputs: recursively globs all .py files using `target.rglob("*.py")`, filters out files in excluded directories (e.g., .venv, __pycache__, .git, build, dist), then applies .gitignore filtering if a git repository root is found"
          - "- Returns a sorted list of absolute Path objects representing all discovered Python files that pass all filters"
          - "- Returns an empty list if the target is a non-.py file, is in an excluded directory, or is gitignored"
          - "- Gracefully degrades to unfiltered discovery if no git repository root is found (still excludes common directories)"
          - "- Called by: [inferred to be called by higher-level discovery/collection routines in agentspec, likely from a main entry point or CLI handler]"
          - "- Calls: _find_git_root (locates the root directory of a git repository), _git_check_ignore (queries git to determine which files are ignored), _is_excluded_by_dir (checks if a path is within a common exclusion directory like .venv or __pycache__)"
          - "- Imports used: pathlib.Path (for filesystem path operations), typing.List (for return type annotation), subprocess (used indirectly by _git_check_ignore), os (used indirectly by helper functions)"
          - "- External services: git command-line tool (invoked via subprocess to check .gitignore status)"
          - "- Two-path branching (file vs. directory) allows efficient handling of both single-file and bulk discovery scenarios without redundant logic"
          - "- .gitignore integration respects developer intent by excluding files already marked as ignored, reducing noise in analysis and respecting repository conventions"
          - "- Excluded directory filtering (via _is_excluded_by_dir) prevents traversal into virtual environments, build artifacts, and cache directories, which would be wasteful and incorrect to analyze"
          - "- Graceful degradation when git is unavailable or target is not in a repository ensures the function remains useful in non-git contexts"
          - "- Sorting by string representation of paths ensures deterministic, human-readable output order across different runs and platforms"
          - "- Use of resolved paths (target.resolve()) in gitignore checks ensures consistent comparison even with symlinks or relative path variations"
          - "- Lazy evaluation of repo_root and ignored set avoids expensive git operations when not needed (e.g., for single non-gitignored files)"
          - "- 2025-10-29: Initial implementation with .gitignore and excluded directory support; honors .venv, __pycache__, .git, build, dist, and similar common exclusions; added as part of agentspec YAML generation feature"
          - "- DO NOT remove or bypass the _is_excluded_by_dir check, as it prevents analysis of virtual environments and build artifacts"
          - "- DO NOT change the sorting key from `str(p)` without ensuring output remains deterministic across platforms"
          - "- DO NOT modify the .resolve() calls in gitignore comparisons, as they are necessary for correct path matching with symlinks"
          - "- DO NOT remove the graceful fallback when repo_root is None, as this allows the function to work outside git repositories"
          - "- ALWAYS preserve the two-branch logic (file vs. directory) to maintain efficiency and clarity"
          - "- ALWAYS ensure that returned paths are absolute (via Path.resolve() or rglob behavior) for consistency with downstream consumers"
          - "- ALWAYS maintain the order of operations: suffix check → excluded dir check → gitignore check, to fail fast on obvious non-matches"
          - "- NOTE: This function depends on external git availability; if git is not installed or the target is not in a git repository, gitignore filtering is silently skipped (not an error condition)"
          - "- NOTE: Performance scales with the number of .py files in the target tree; for very large codebases, gitignore queries may be slow; consider caching results if called repeatedly on the same tree"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "-    Discover Python files under target honoring .gitignore if possible and"
          - "-    excluding common environment/cache/build directories."
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
        ---/agentspec
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


def load_env_from_dotenv(env_path: Optional[Path] = None, override: bool = False) -> Optional[Path]:
    """
    ---agentspec
    what: |
      Loads environment variables from a .env file by searching standard locations in order of precedence: explicit env_path parameter, current working directory and its parents, git repository root, and package root directory. Returns the Path to the first .env file found, or None if no file exists.

      Parsing behavior: reads file with UTF-8 encoding (ignoring decode errors), splits into lines, strips whitespace, and skips empty lines, comment lines (starting with #), and lines without an = delimiter. Extracts key-value pairs by splitting on first = only, strips surrounding whitespace from both key and value, and removes surrounding quotes (both single and double) from values.

      Environment variable assignment respects the override flag: when False (default), only sets variables that do not already exist in os.environ; when True, overwrites existing variables. All exceptions during file access or parsing are silently caught and result in None return value, enabling graceful degradation.

      Inputs: optional env_path (Path object or None) to specify explicit file location; override boolean flag (default False) to control whether existing environment variables are overwritten. Outputs: Path object pointing to the loaded .env file, or None if file not found or parsing failed.

      Edge cases: handles missing files gracefully, tolerates malformed lines by skipping them, preserves intentional environment overrides when override=False, and continues searching candidates if any candidate file access fails.
        deps:
          calls:
            - Path
            - Path.cwd
            - _find_git_root
            - c.exists
            - c.is_file
            - candidates.append
            - chosen.read_text
            - k.strip
            - line.strip
            - resolve
            - s.split
            - s.startswith
            - splitlines
            - strip
            - v.strip
          imports:
            - __future__.annotations
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      This approach enables flexible configuration management across development, repository, and package contexts without requiring code changes. The search hierarchy (CWD → parents → git root → package root) accommodates both monorepo and single-package layouts while allowing local overrides to take precedence.

      Non-destructive default behavior (override=False) prevents accidental clobbering of intentionally set environment variables, which is critical in environments where variables may be set via shell, CI/CD systems, or parent processes. Silent error handling allows .env files to be optional, supporting both configured and unconfigured deployments without initialization failures.

      Quote stripping from values accommodates common .env conventions where values may be quoted for readability or to preserve whitespace, while the flexible parsing (skipping malformed lines) tolerates real-world .env files that may contain comments or incomplete entries.

    guardrails:
      - DO NOT raise exceptions on missing files or parse errors; always return None to allow graceful degradation and optional .env configuration
      - DO NOT modify os.environ when override=False and a key already exists, to preserve intentional environment variable overrides from shell, CI/CD, or parent processes
      - DO NOT process lines that are empty, start with #, or lack an = delimiter, to avoid silent failures on malformed entries and respect comment syntax
      - DO NOT assume UTF-8 encoding will always succeed; use errors="ignore" to handle mixed or legacy encodings without crashing
      - DO NOT split on all = characters; split only on the first = to allow = characters in values (e.g., connection strings, base64 data)

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
        ---/agentspec
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
