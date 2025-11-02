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
from agentspec.langs import LanguageRegistry


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
      Fast pre-filter to skip obviously excluded directories before calling git check-ignore.
      
      ONLY checks for .git directory to avoid recursing into repository metadata.
      All other exclusions (.venv, node_modules, etc.) are handled by .gitignore.

      Inputs:
      - path: A pathlib.Path object

      Behavior:
      - Checks if '.git' is in any path component
      - Returns True only for .git, False otherwise
      - All other filtering delegated to git check-ignore

    deps:
          imports:
            - pathlib.Path

    why: |
      Previous versions tried to maintain a hardcoded exclusion list that would never
      cover all cases (.venv311, venv38, etc.). Instead, rely on .gitignore which the
      user has already configured correctly. Only exclude .git since it's universal
      and we never want to process repository metadata.

    guardrails:
      - DO NOT add more directories to this check; use .gitignore instead
      - ONLY check for .git directory
      - Let git check-ignore handle all other exclusions

    changelog:
          - "2025-11-01: Simplify to only check .git; delegate all other exclusions to .gitignore"
          - "2025-11-01: Add pattern matching for versioned virtualenvs (.venv*, venv*, .env*)"
          - "2025-10-30: feat: robust docstring generation and Haiku defaults"
        ---/agentspec
    """
    # Only exclude .git - everything else is handled by .gitignore
    return '.git' in path.parts


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

      - "2025-10-31: Clean up docstring formatting"
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

      - "2025-10-31: Clean up docstring formatting"
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
    """
    ---agentspec
    what: |
      Locates the .agentspecignore configuration file used to exclude paths from agent processing.

      Search strategy (in order):
      1. Attempts to import the agentspec package and locate its built-in .agentspecignore file from the package installation directory (parent of agentspec module root)
      2. Falls back to checking repo_root parameter for a project-specific .agentspecignore file
      3. Returns None if neither location contains the file

      Inputs:
      - repo_root: Path object representing the repository root directory (may be None)

      Outputs:
      - Path object pointing to the .agentspecignore file if found
      - None if no .agentspecignore file exists in either location

      Edge cases:
      - Import of agentspec package fails silently (catches all exceptions during import/path resolution)
      - repo_root is None or invalid: skips fallback check
      - Built-in .agentspecignore exists but is inaccessible: falls back to repo_root check
      - Both locations lack .agentspecignore: returns None (no default behavior)
        deps:
          calls:
            - Path
            - builtin_ignore.exists
            - exists
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - fnmatch
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      Dual-source approach balances framework defaults with user customization. Built-in .agentspecignore provides sensible exclusions for common patterns (node_modules, .git, etc.) across all projects. Project-specific .agentspecignore allows teams to override or extend defaults for their repository. Silent exception handling during package import prevents initialization failures when agentspec is in an unusual installation state. Fallback to repo_root ensures functionality even if package metadata is unavailable.

    guardrails:
      - DO NOT assume repo_root is always valid—it may be None or point to a non-existent directory, so existence checks are required before use
      - DO NOT raise exceptions during package import—silent fallback is intentional to prevent cascading failures in agent initialization
      - DO NOT modify or create .agentspecignore files—this function is read-only discovery only
      - DO NOT cache the result indefinitely—.agentspecignore files may be created/modified during runtime, so callers should re-invoke as needed

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
        ---/agentspec
    """
    # Use agentspec's built-in .agentspecignore from package installation
    try:
        import agentspec
        package_root = Path(agentspec.__file__).parent.parent
        builtin_ignore = package_root / '.agentspecignore'
        if builtin_ignore.exists():
            return builtin_ignore
    except Exception:
        pass
    
    # Fallback: check repo root
    if repo_root and (repo_root / ".agentspecignore").exists():
        return repo_root / ".agentspecignore"
    
    return None


def _parse_agentspecignore(ignore_path: Path, repo_root: Path) -> List[str]:
    """
    ---agentspec
    what: |
      Parses a .agentspecignore file and extracts a list of ignore patterns.

      Inputs:
        - ignore_path (Path): File system path to the .agentspecignore file
        - repo_root (Path): Root directory of the repository (currently unused but available for context)

      Outputs:
        - List[str]: Ordered list of non-empty, non-comment pattern strings

      Behavior:
        - Reads the file with UTF-8 encoding, ignoring decode errors via errors="ignore"
        - Splits content by lines and strips whitespace from each line
        - Filters out empty lines and lines starting with '#' (comments)
        - Returns remaining lines as patterns
        - Returns empty list [] on any exception (file not found, permission denied, etc.)

      Edge cases:
        - Missing or inaccessible file: silently returns []
        - Malformed UTF-8 bytes: ignored via errors="ignore" parameter
        - Blank lines and whitespace-only lines: filtered out
        - Comment-only files: returns []
        - Mixed comment and pattern content: correctly separates them
        deps:
          calls:
            - ignore_path.read_text
            - line.startswith
            - line.strip
            - patterns.append
            - splitlines
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - fnmatch
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      This utility enables flexible ignore pattern configuration without raising exceptions that would halt processing.
      The lenient error handling (returning [] on failure) allows graceful degradation when .agentspecignore is absent or unreadable.
      Stripping whitespace normalizes patterns and prevents leading/trailing space issues.
      Comment filtering via '#' prefix follows standard convention (matching .gitignore behavior) for user-friendly configuration files.
      The repo_root parameter is included for potential future use (e.g., relative path resolution or validation).

    guardrails:
      - DO NOT raise exceptions on file read failures; return [] instead to allow processing to continue without .agentspecignore
      - DO NOT preserve leading/trailing whitespace in patterns; strip() ensures consistent pattern matching
      - DO NOT include comment lines in output; '#' prefix filtering prevents malformed patterns from being used
      - DO NOT assume UTF-8 validity; use errors="ignore" to handle binary corruption or mixed encodings gracefully
      - DO NOT modify or validate pattern syntax; this function only extracts raw strings; validation belongs in the consumer

        changelog:
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
        ---/agentspec
    """
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
    ---agentspec
    what: |
      Determines whether a filesystem path matches a gitignore-style pattern string.

      Inputs:
        - path: Path object to test against the pattern
        - pattern: gitignore-style pattern string (e.g., "*.log", "/build/", "**/node_modules/")
        - repo_root: Path object representing the repository root for relative path calculation

      Outputs:
        - Boolean: True if path matches pattern, False otherwise

      Behavior:
        1. Converts the input path to a relative path from repo_root and normalizes path separators to forward slashes for consistent matching
        2. Strips whitespace from pattern and processes special gitignore syntax:
           - Leading /: anchors pattern to repo root (must match from beginning)
           - Trailing /: restricts match to directories only (verifies with is_dir())
           - **/: matches any directory depth; converted to * for fnmatch compatibility
        3. Attempts two matching strategies:
           a) Component-wise matching: splits relative path into parts and tests each component name against the pattern
           b) Full-path matching: tests the entire relative path string against the pattern
        4. For directory-only patterns (trailing /), reconstructs the full path and validates it is actually a directory before returning True
        5. Returns False on any exception (invalid paths, permission errors, etc.)

      Edge cases:
        - Paths with backslashes on Windows are normalized to forward slashes
        - Patterns with **/ in the middle are converted to * (partial support for gitignore semantics)
        - Leading / patterns also match subdirectories via "pattern/*" fallback
        - Directory-only patterns require filesystem verification; non-existent paths return False
        - Exceptions during path resolution or directory checks are silently caught and return False
        deps:
          calls:
            - Path
            - component_path.is_dir
            - enumerate
            - fnmatch.fnmatch
            - path.resolve
            - pattern.endswith
            - pattern.replace
            - pattern.startswith
            - pattern.strip
            - rel_str.split
            - relative_to
            - replace
            - repo_root.resolve
            - str
            - test_full.is_dir
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - fnmatch
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set


    why: |
      This function provides gitignore-compatible pattern matching for filtering repository contents. The approach uses fnmatch for glob-style wildcard support while layering gitignore-specific semantics (anchoring, directory-only flags, recursive wildcards). Component-wise matching enables patterns like "*.log" to match "dir/file.log" without explicit path separators. The dual matching strategy (component + full-path) accommodates both simple filename patterns and explicit path patterns like "foo/bar/baz". Exception handling ensures robustness when paths don't exist or are inaccessible, defaulting to non-match rather than crashing. Path normalization ensures cross-platform consistency.

    guardrails:
      - DO NOT rely on this function for security filtering; it performs pattern matching only and does not validate path traversal attacks or symlink loops
      - DO NOT assume ** semantics are fully gitignore-compliant; the implementation converts **/ to * which is a simplification and may not match complex nested patterns correctly
      - DO NOT use this for real-time filesystem monitoring without caching; repeated is_dir() calls on non-existent paths incur filesystem overhead
      - DO NOT pass non-absolute or non-resolvable paths without ensuring repo_root is also resolvable; relative path calculation will fail silently and return False
      - DO NOT assume exception suppression is safe for all use cases; silent failures on permission errors or invalid paths may mask configuration issues

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
        ---/agentspec
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

        # Check if any path component (directory or file name) matches
        parts = rel_str.split('/')
        for i, part in enumerate(parts):
            # Test just this component name against the pattern
            if fnmatch.fnmatch(part, pattern):
                if dir_only:
                    # For directory patterns, verify this component is actually a directory
                    # Reconstruct the path up to this component
                    component_path = repo_root / Path(*parts[:i+1])
                    if component_path.is_dir():
                        return True
                else:
                    return True

        # Also check full path for patterns like "foo/bar"
        if fnmatch.fnmatch(rel_str, pattern):
            if dir_only:
                test_full = repo_root / rel_str
                return test_full.is_dir()
            return True

        return False
    except Exception:
        return False


def _check_agentspecignore(path: Path, repo_root: Path | None) -> bool:
    """
    ---agentspec
    what: |
      Determines whether a given file path should be ignored based on .agentspecignore patterns.

      Returns True if the path matches any ignore pattern, False otherwise.

      Pattern loading strategy (two-tier):
      1. Built-in patterns: Loads agentspec's stock .agentspecignore from the package root directory. These patterns are always applied and provide sensible defaults (e.g., __pycache__, .git, node_modules, etc.).
      2. User patterns: Loads project-specific .agentspecignore from repo_root if it exists. User patterns are merged with built-in patterns, allowing projects to extend or override defaults.

      Matching behavior:
      - Patterns are checked sequentially against the input path
      - First match returns True (path is ignored)
      - If no patterns exist or no matches found, returns False (path is not ignored)
      - Pattern matching is delegated to _matches_pattern() helper

      Edge cases:
      - If repo_root is None, returns False immediately (no context to check patterns)
      - If built-in .agentspecignore cannot be located or loaded, silently continues (exception caught)
      - If user .agentspecignore does not exist, only built-in patterns are used
      - If both ignore files are missing, returns False (nothing to ignore)
      - Empty pattern lists result in False (no matches possible)

      Inputs: path (Path object to check), repo_root (Path to repository root or None)
      Outputs: bool indicating ignore status
        deps:
          calls:
            - Path
            - _matches_pattern
            - _parse_agentspecignore
            - builtin_ignore.exists
            - patterns.extend
            - user_ignore.exists
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - fnmatch
            - os
            - pathlib.Path
            - subprocess
            - typing.Iterable
            - typing.List
            - typing.Optional
            - typing.Set

    why: |
      Two-tier pattern loading provides both sensible defaults and project customization. Built-in patterns protect against common unintended inclusions (compiled artifacts, dependencies, VCS metadata) without requiring every project to maintain identical ignore rules. User patterns enable project-specific filtering (e.g., build directories, generated code, vendor folders) without modifying the package itself.

      Silent exception handling on built-in pattern loading ensures robustness: if the package structure is unusual or agentspec cannot be imported, the function degrades gracefully rather than failing the entire ignore check.

      Early return when repo_root is None prevents unnecessary processing and clarifies intent: ignore checking is meaningless without repository context.

      Sequential pattern matching with early exit (first match wins) is efficient and predictable for users reasoning about which rule caused a path to be ignored.
    guardrails:
      - DO NOT apply only user patterns and skip built-in patterns; built-in patterns are mandatory defaults that protect against common mistakes
      - DO NOT raise exceptions if built-in .agentspecignore is missing or unreadable; this would break the function for non-standard installations or edge cases
      - DO NOT return True when repo_root is None; without repository context, ignore status cannot be reliably determined
      - DO NOT modify or cache patterns across multiple calls without invalidation; patterns may change between calls if files are edited
      - DO NOT assume pattern file encoding; delegate encoding handling to _parse_agentspecignore() to ensure consistent UTF-8 or fallback behavior

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
        ---/agentspec
    """
    if not repo_root:
        return False

    patterns = []
    
    # Load agentspec's built-in patterns (ALWAYS)
    try:
        import agentspec
        package_root = Path(agentspec.__file__).parent.parent
        builtin_ignore = package_root / '.agentspecignore'
        if builtin_ignore.exists():
            patterns.extend(_parse_agentspecignore(builtin_ignore, repo_root))
    except Exception:
        pass
    
    # ALSO load user's project patterns (if they exist)
    user_ignore = repo_root / ".agentspecignore"
    if user_ignore.exists():
        patterns.extend(_parse_agentspecignore(user_ignore, repo_root))
    
    # If no patterns found, not ignored
    if not patterns:
        return False
    
    # Check if path matches any pattern
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

      - "2025-10-31: Clean up docstring formatting"
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


def collect_source_files(target: Path) -> List[Path]:
    """
    ---agentspec
    what: |
      Discover source files across all registered language adapters (Python, JavaScript, TypeScript) while
      honoring repository ignore patterns and adapter-specific exclusions.

      Behavior:
      - Accepts a file or directory `target`
      - If `target` is a file, returns `[target]` only if its extension is supported by any registered adapter
      - If `target` is a directory, unions results of per-adapter discovery:
        * Python files are discovered via `collect_python_files` (preserves .gitignore and .agentspecignore handling)
        * Other languages use their adapter's `discover_files` method (expected to exclude build/third-party dirs)
        * ALL files (Python and non-Python) are post-filtered through .gitignore and .agentspecignore for consistency
      - Deduplicates and returns a sorted list of absolute Paths

      Edge cases:
      - Nonexistent `target`: returns an empty list (graceful degradation consistent with other collectors)
      - Repositories without git: Python discovery still works without .gitignore filtering; adapters may still exclude common directories

    deps:
      calls:
        - LanguageRegistry.list_adapters
        - LanguageRegistry.supported_extensions
        - collect_python_files
        - adapter.discover_files
        - target.is_file
        - target.is_dir
        - target.suffix
        - files.sort
        - _find_git_root
        - _git_check_ignore
        - _check_agentspecignore
      imports:
        - agentspec.langs.LanguageRegistry
        - pathlib.Path
        - typing.List

    why: |
      Agentspec aims to be language-agnostic. Centralizing file discovery avoids duplicating multi-language logic
      in each CLI entry point (extract, lint, strip). It preserves robust Python discovery semantics while enabling
      pluggable discovery for other languages via their adapters.
      
      The post-filtering through .gitignore and .agentspecignore ensures that ALL languages respect the same
      ignore patterns, preventing vendor/minified/build files from being processed regardless of language.

    guardrails:
      - DO NOT hard-code extensions here; rely on registered adapters for non-Python languages
      - DO NOT raise on missing paths; always return an empty list for graceful CLI behavior
      - ALWAYS delegate Python discovery to `collect_python_files` to preserve .gitignore and .agentspecignore handling
      - ALWAYS post-filter adapter results through .gitignore and .agentspecignore to maintain parity with Python
      - ALWAYS return absolute, sorted paths for deterministic downstream processing

    changelog:
      - "2025-11-01: Add multi-language collect_source_files (JS/TS support)"
      - "2025-11-01: Fix .gitignore/.agentspecignore filtering for non-Python languages (adapter results now post-filtered)"
    ---/agentspec
    """
    # Gracefully handle missing/nonexistent paths
    try:
        exists = target.exists()
    except Exception:
        exists = False
    if not exists:
        return []

    if target.is_file():
        ext = target.suffix.lower()
        if ext == ".py":
            return [target]
        if ext in LanguageRegistry.supported_extensions():
            # For single files, apply ignore filters directly
            repo_root = _find_git_root(target)
            if repo_root:
                ignored = _git_check_ignore(repo_root, [target])
                if target.resolve() in ignored:
                    return []
                if _check_agentspecignore(target, repo_root):
                    return []
            return [target]
        return []

    if not target.is_dir():
        return []

    files: List[Path] = []
    # Python via dedicated collector (already has ignore semantics built-in)
    files.extend(collect_python_files(target))

    # Other languages via their adapters
    non_python_files: List[Path] = []
    for ext, adapter in LanguageRegistry.list_adapters().items():
        if ext == ".py":
            continue
        try:
            non_python_files.extend(adapter.discover_files(target))
        except Exception:
            # Ignore adapter-specific discovery failures to avoid breaking cross-language processing
            continue

    # POST-FILTER non-Python files through .gitignore and .agentspecignore
    # This ensures parity with Python discovery and prevents vendor/minified files from being processed
    if non_python_files:
        repo_root = _find_git_root(target)
        if repo_root:
            # Filter through .gitignore
            ignored = _git_check_ignore(repo_root, non_python_files)
            filtered = [p for p in non_python_files if p.resolve() not in ignored]
            # Filter through .agentspecignore
            filtered = [p for p in filtered if not _check_agentspecignore(p, repo_root)]
            files.extend(filtered)
        else:
            # No git repo, just add them all
            files.extend(non_python_files)

    # Deduplicate and sort
    uniq = sorted({p.resolve() for p in files}, key=lambda p: str(p))
    return uniq


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
