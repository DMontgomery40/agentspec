#!/usr/bin/env python3
"""
agentspec.collect
------------------
Deterministic metadata collectors for Agentspec generation.

Collects facts that can be derived from code or VCS, to reduce LLM
hallucination in docstrings:
- deps.calls: function calls within the function body (best-effort)
- deps.imports: top-level imports in the module (for context)

Notes
- Git history collection is intentionally omitted from the return value to keep
  changelog narrative model-generated as requested by users.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path
import difflib
from typing import Any, Dict, List


def _get_function_calls(node: ast.AST) -> List[str]:
    '''
    ```python
    """
    Extract all function call names from an AST node as a sorted, deduplicated list.

    WHAT:
    - Walks AST to find all ast.Call nodes and extracts callable names
    - Handles simple calls (func), method calls (obj.method), and chained attributes (attr.method)
    - Returns sorted, deduplicated list with empty strings filtered out

    WHY:
    - Enables static dependency analysis without code execution
    - Qualified names preserve semantic context (local vs method calls)
    - Sorting ensures deterministic output for reproducible analysis

    GUARDRAILS:
    - DO NOT remove isinstance() checks; they distinguish ast.Name from ast.Attribute node types
    - DO NOT modify ast.walk() traversal without understanding it visits all nested nodes
    - DO NOT alter sorting behavior; output must remain deterministic
    - ALWAYS preserve both ast.Name and ast.Attribute handling for complete call pattern coverage
    - ALWAYS filter empty strings to prevent malformed entries in results
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: ast.walk, calls.append, isinstance, sorted
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance CLI help and add rich formatting support
    - Called by: agentspec/collect.py module-level analysis functions (inferred from file context)
    - Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering)
    - Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)
    - External services: None; this is pure static analysis using Python's built-in ast module
    - Current implementation: Extracts all function call names from an AST node by walking the tree, handling simple calls, method calls, and chained attributes, then returns a sorted deduplicated list.
    - DO NOT modify the ast.walk() traversal logic without understanding that it visits all nodes in the tree
    - DO NOT remove the isinstance() type checks, as they are essential for correctly distinguishing between different call patterns
    - DO NOT change the set deduplication without considering that it removes duplicate function names across the entire AST
    - DO NOT alter the sorting behavior without ensuring output remains deterministic
    - ALWAYS preserve the handling of both ast.Name and ast.Attribute node types
    - ALWAYS maintain the qualified name construction for method calls (the "base.method" format)
    - ALWAYS filter out empty strings from the final result
    - NOTE: This function performs static analysis only and does not execute code; it cannot detect dynamically-called functions or functions called via eval/exec
    - NOTE: The base detection for chained attributes (ast.Attribute.value being another ast.Attribute) only captures the immediate parent attribute name, not the full chain; calls like `a.b.c()` will be recorded as "b.c", not "a.b.c"
    - NOTE: Edge case—if an ast.Attribute node has a base that is neither ast.Name nor ast.Attribute (e.g., a function call result), the base will be None and only the method name will be recorded
    -    print(f"[AGENTSPEC_CONTEXT] _get_function_calls: Called by: agentspec/collect.py module-level analysis functions (inferred from file context) | Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering) | Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)")
    - 2025-10-30: feat: robust docstring generation and Haiku defaults


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    **Commit 1 (2025-10-30):** Removed debug context print statement from function.

    **Commit 2 (2025-10-30):** Implement function call extraction with AST traversal.

    '''
    calls: List[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Attribute):
                base = None
                if isinstance(func.value, ast.Name):
                    base = func.value.id
                elif isinstance(func.value, ast.Attribute):
                    base = func.value.attr
                name = f"{base}.{func.attr}" if base else func.attr
                calls.append(name)
            elif isinstance(func, ast.Name):
                calls.append(func.id)
    return sorted({c for c in calls if c})


def _get_module_imports(tree: ast.AST) -> List[str]:
    '''
    ```python
    """
    Extracts and returns a sorted, deduplicated list of top-level module imports from an AST tree.

    WHAT:
    - Traverses AST body collecting `import X` and `from X import Y` statements
    - For `import`: extracts module name; for `from...import`: joins module and alias with dots
    - Handles relative imports (module=None), deduplicates via set, filters empty strings, returns sorted list

    WHY:
    - Provides coarse-grained dependency analysis sufficient for module-level context without recursive overhead
    - Sorted output ensures deterministic, reproducible results for consistent agent analysis

    GUARDRAILS:
    - DO NOT remove sorted() call; deterministic ordering required for reproducible dependency tracking
    - DO NOT change isinstance checks to single condition; Import and ImportFrom have different structures
    - DO NOT modify dot-joining logic without considering relative imports where module is None
    - ALWAYS preserve getattr fallback to [] when tree.body is missing
    - ALWAYS return List[str] as specified in type hint
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: getattr, imports.append, isinstance, join, sorted
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance CLI help and add rich formatting support
    - Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements
    - Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes)
    - For `import` statements, extracts the module name directly from the alias
    - For `from...import` statements, constructs the full import path by joining the source module with the imported name using dot notation, handling cases where the module is None (bare `from ... import`)
    - Deduplicates the collected imports by converting to a set, filters out empty strings, and returns a sorted list for consistent ordering
    - Returns an empty list if the AST has no body or contains no import statements
    - Called by: agentspec/collect.py module-level analysis functions (inferred from context of coarse dependency collection)
    - Calls: getattr (built-in), isinstance (built-in), sorted (built-in), str.join (built-in)
    - Imports used: ast (standard library for AST node types), typing.List (type hints)
    - External services: None
    - Uses getattr with a default empty list to safely access the body attribute, preventing AttributeError if the AST node lacks a body (defensive programming)
    - Checks isinstance for both ast.Import and ast.ImportFrom separately because they have different structures: Import has a flat names list, while ImportFrom has both a module and a names list
    - Constructs full import paths for ImportFrom by joining module and alias name with dots, which provides more granular dependency information than just the module name
    - Handles the edge case where ImportFrom.module is None (occurs with relative imports like `from . import foo`) by using `or ""` and filtering empty parts
    - Deduplicates using set comprehension before sorting to ensure O(n log n) performance and eliminate redundant entries that might arise from multiple import statements importing the same module
    - Returns sorted output for deterministic, reproducible results across runs, which is critical for consistent dependency tracking and agent analysis
    - Alternative approach (not used): Could have used ast.walk() to find all imports recursively, but this function intentionally restricts to top-level imports only for "coarse" dependency context as documented in the docstring
    - Current implementation: Extracts top-level imports from AST module body, deduplicates, and returns sorted list for dependency analysis.
    - DO NOT modify the deduplication logic (set conversion) without understanding its impact on downstream dependency analysis
    - DO NOT remove the sorted() call, as deterministic ordering is required for consistent agent analysis
    - DO NOT change the isinstance checks to use a single condition without testing both Import and ImportFrom node types separately
    - DO NOT modify the dot-joining logic for ImportFrom without considering relative imports (where module is None)
    - ALWAYS preserve the filtering of empty strings in the set comprehension
    - ALWAYS maintain the getattr fallback to [] for safety when tree.body is missing
    - ALWAYS return a List[str] type as specified in the type hint
    - NOTE: This function assumes the input is a valid ast.AST object; passing invalid AST structures may cause unexpected behavior
    - NOTE: The function only captures top-level imports; nested imports inside functions or classes are intentionally excluded per the "coarse dependency context" design
    - NOTE: Relative imports (from . import X) will have their module set to None, which is handled by the `or ""` pattern but results in just the alias name being returned
    -    print(f"[AGENTSPEC_CONTEXT] _get_module_imports: Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements | Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes) | For `import` statements, extracts the module name directly from the alias")
    - 2025-10-30: feat: robust docstring generation and Haiku defaults


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    # Commit Analysis

    **Commit 1 (2025-10-30):** Removed debug print statement from function.

    **Commit 2 (2025-10-30):** Implement AST traversal to extract module imports.

    '''
    imports: List[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(".".join(part for part in (mod, alias.name) if part))
    return sorted({i for i in imports if i})


def collect_changelog_diffs(filepath: Path, func_name: str) -> List[Dict[str, str]]:
    '''
    ```python
    """
    Extract function-level git history for the last 5 commits using git log -L.

    WHAT:
    - Retrieves function-specific changes across last 5 commits via `git log -L` with metadata (hash, date, message, diff)
    - Parses git output by splitting on `COMMIT_START|||` delimiter to isolate commit metadata from diffs
    - Returns list of dicts with keys: `hash`, `date` (YYYY-MM-DD), `message`, `diff`

    WHY:
    - Function-level tracking isolates relevant changes from file-wide noise for precise historical context
    - Enables LLM-based summarization of function evolution without embedding raw diffs in docstrings
    - Silent failure on git errors allows graceful degradation in non-git or offline environments

    GUARDRAILS:
    - DO NOT include returned diffs directly in docstrings; pass to LLM for summarization only
    - DO NOT raise exceptions on git failures or parsing errors; always return empty list
    - DO NOT assume function exists in git history; missing functions return empty list silently
    - ALWAYS use `errors="ignore"` when decoding subprocess output to handle non-UTF8 characters
    - ALWAYS validate delimiter split produces at least 4 parts before accessing metadata fields
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: commits.append, decode, diff_lines.append, join, len, line.split, line.startswith, out.splitlines, subprocess.check_output
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    Extract function-level git history with dates and commit messages.

    '''
    try:
        cmd = [
            "git", "log",
            "-L", f":{func_name}:{filepath}",
            "--pretty=format:COMMIT_START|||%h|||%ad|||%s|||",
            "--date=short",
            "-n5",
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        
        # Parse output into commits
        commits = []
        current_commit = None
        diff_lines = []
        
        for line in out.splitlines():
            if line.startswith("COMMIT_START|||"):
                # Save previous commit if exists
                if current_commit:
                    current_commit["diff"] = "\n".join(diff_lines)
                    commits.append(current_commit)
                    diff_lines = []
                
                # Parse new commit header (format: COMMIT_START|||hash|||date|||message|||)
                parts = line.split("|||")
                if len(parts) >= 4:
                    current_commit = {
                        "hash": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    }
            elif current_commit:
                # Accumulate diff lines
                diff_lines.append(line)
        
        # Save last commit
        if current_commit:
            current_commit["diff"] = "\n".join(diff_lines)
            commits.append(current_commit)
        
        return commits
    except Exception:
        return []


def _extract_function_source_without_docstring(src: str, func_name: str) -> str:
    '''
    ```python
    """
    Extract function source code with docstring and comment-only lines removed.

    WHAT:
    - Parses source via AST to locate function definition (sync/async), returns cleaned body
    - Removes leading docstring (handles ast.Constant and legacy ast.Str for version compatibility) and all comment-only lines
    - Returns empty string if function not found or parsing fails

    WHY:
    - Enables clean function body extraction for downstream analysis without documentation noise
    - AST-based approach ensures accurate docstring detection across Python versions
    - Defensive exception handling prevents crashes on invalid input

    GUARDRAILS:
    - DO NOT assume docstring exists; always check body presence and first statement type before removal
    - DO NOT fail on malformed source; catch all exceptions and return empty string
    - DO NOT use absolute line indices directly for slicing; always map to relative indices by subtracting start offset
    - ALWAYS call lstrip() when checking for comment-only lines to correctly identify pure comments
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: ast.parse, ast.walk, cleaned.append, getattr, hasattr, isinstance, join, ln.lstrip, max, src.split, stripped.startswith
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance CLI help and add rich formatting support


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    Extract function source code while removing docstrings and comments.

    '''
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                lines = src.split('\n')
                start = (node.lineno or 1) - 1
                end = (node.end_lineno or node.lineno)  # end is exclusive when slicing
                func_lines = lines[start:end]

                # Remove leading docstring if present using AST body[0]
                if getattr(node, 'body', None):
                    first_stmt = node.body[0]
                    is_doc = False
                    if isinstance(first_stmt, ast.Expr):
                        if isinstance(getattr(first_stmt, 'value', None), ast.Constant) and isinstance(first_stmt.value.value, str):
                            is_doc = True
                        elif hasattr(ast, 'Str') and isinstance(getattr(first_stmt, 'value', None), ast.Str):
                            is_doc = True
                    if is_doc:
                        ds_start_abs = (first_stmt.lineno or node.lineno) - 1
                        ds_end_abs = (first_stmt.end_lineno or first_stmt.lineno)
                        # Delete docstring range from func_lines using absolute indices mapped to slice
                        del_start = max(0, ds_start_abs - start)
                        del_end = max(del_start, ds_end_abs - start)
                        del func_lines[del_start:del_end]

                # Also drop pure comment-only lines
                cleaned = []
                for ln in func_lines:
                    stripped = ln.lstrip()
                    if stripped.startswith('#'):
                        continue
                    cleaned.append(ln)
                return '\n'.join(cleaned)
        return ""
    except Exception:
        return ""


def collect_function_code_diffs(filepath: Path, func_name: str, limit: int = 5) -> List[Dict[str, str]]:
    '''
    ```python
    """
    Collect per-commit code diffs for a function from git history, filtering meaningful changes only.

    WHAT:
    - Retrieves up to `limit` recent commits touching the file, extracts function body at each commit and parent, generates unified diff, filters to +/- lines only
    - Excludes file headers (+++/---), hunk markers (@@), context lines, and comment-only changes
    - Returns empty list on git failure or if function absent in both versions

    WHY:
    - Isolates functional evolution by removing noise (docstrings, comments, diff metadata) that obscures logic changes
    - Gracefully handles git failures and missing commits rather than raising exceptions, enabling partial results in varied environments

    GUARDRAILS:
    - DO NOT include file headers, hunk markers, context lines, or comment-only changes in output
    - DO NOT return results if git operations fail; return empty list instead
    - ALWAYS skip commits where function body absent in both parent and current versions
    - ALWAYS filter out malformed log entries lacking three fields (hash, date, message)
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: _extract_function_source_without_docstring, changes.append, content.lstrip, curr_func.splitlines, decode, difflib.unified_diff, dl.startswith, int, join, len, line.split, ln.strip, log_out.splitlines, prev_func.splitlines, results.append, startswith, str, subprocess.check_output
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance CLI help and add rich formatting support


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    Extract function-level code diffs across git history with limit support.

    '''
    results: List[Dict[str, str]] = []
    try:
        # Recent commits touching the file
        log_cmd = [
            "git", "log",
            f"-n{int(limit)}",
            "--pretty=format:%H|||%ad|||%s",
            "--date=short",
            "--",
            str(filepath),
        ]
        log_out = subprocess.check_output(log_cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        for line in (ln for ln in log_out.splitlines() if ln.strip()):
            parts = line.split("|||")
            if len(parts) < 3:
                continue
            commit, date, message = parts[0], parts[1], parts[2]

            # Get file content at commit and its parent
            try:
                prev_src = subprocess.check_output(["git", "show", f"{commit}^:{filepath}"], stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
            except Exception:
                prev_src = ""
            try:
                curr_src = subprocess.check_output(["git", "show", f"{commit}:{filepath}"], stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
            except Exception:
                curr_src = ""

            prev_func = _extract_function_source_without_docstring(prev_src, func_name)
            curr_func = _extract_function_source_without_docstring(curr_src, func_name)

            # If function absent in both, skip
            if not prev_func and not curr_func:
                continue

            prev_lines = prev_func.splitlines()
            curr_lines = curr_func.splitlines()

            # Compute unified diff and keep only +/- lines (exclude file/hunk headers)
            diff_iter = difflib.unified_diff(prev_lines, curr_lines, lineterm="")
            changes: List[str] = []
            for dl in diff_iter:
                if not dl:
                    continue
                if dl.startswith('+++') or dl.startswith('---') or dl.startswith('@@') or dl.startswith(' '):
                    continue
                if dl.startswith('+') or dl.startswith('-'):
                    # Exclude comment-only changes (after +/- and whitespace, a '#')
                    content = dl[1:]
                    if content.lstrip().startswith('#'):
                        continue
                    changes.append(dl)

            if not changes:
                # No code changes within the function for this commit
                continue

            # Get short hash for display
            short_hash = commit[:7] if len(commit) >= 7 else commit
            
            results.append({
                "date": date,
                "message": message,
                "hash": short_hash,
                "diff": "\n".join(changes),
            })
    except Exception:
        return []

    return results

def collect_metadata(filepath: Path, func_name: str) -> Dict[str, Any]:
    '''
    ```python
    """
    Extracts deterministic metadata (function calls, imports, git history) from a Python function via AST parsing and git log.

    WHAT:
    - Parses Python file AST to locate target function (sync or async) and extracts internal calls and module imports
    - Retrieves function-specific git history using `git log -L :func_name:filepath` (up to 5 most recent commits), filtering to commit message lines only
    - Returns `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success; empty dict `{}` on any failure (function not found, parse error, exception)
    - Edge cases: First AST match used if function name collides; git unavailable defaults changelog to `["- no git history available"]`; no commits found defaults to `["- none yet"]`

    WHY:
    - AST-based parsing provides syntactically-aware function identification, avoiding false positives from strings/comments
    - Git `-L` option provides function-specific history without manual line tracking; automatically handles boundary changes across commits
    - Fail-closed exception handling (return `{}`) ensures agent pipelines never crash; metadata collection is non-critical and degrades gracefully
    - Separate try-except for git allows partial metadata return (deps without changelog) if git fails

    GUARDRAILS:
    - DO NOT raise exceptions instead of returning `{}`; breaks fail-closed contract required by agent pipelines
    - DO NOT remove `errors="ignore"` from `.decode()` without handling git output encoding edge cases
    - DO NOT modify git command structure; `-L :func_name:filepath` syntax is required for accurate line-range filtering
    - DO NOT recursively analyze imported modules or follow call chains; keep analysis local and deterministic
    - ALWAYS preserve distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
    - ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
    - ALWAYS filter git output to only lines matching commit format (starts with `"- YYYY-MM-DD:"` and contains hash in parentheses)
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: _get_function_calls, _get_module_imports, ast.parse, ast.walk, commit_pattern.match, decode, filepath.read_text, isinstance, join, len, lines.append, ln.strip, out.splitlines, print, re.compile, str, subprocess.check_output
    Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance CLI help and add rich formatting support
    - Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions)
    - Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()`
    - Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages
    - Returns a dictionary with structure `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success, or an empty dict `{}` if the function cannot be found, parsing fails, or any exception occurs during metadata collection
    - Gracefully degrades: if git history is unavailable, changelog defaults to `["- no git history available"]`; if no commits are found, defaults to `["- none yet"]`
    - Called by: [Inferred to be called by documentation generation or agent analysis pipelines that need to understand function dependencies]
    - Calls: `_get_function_calls()` [extracts function call names from AST node], `_get_module_imports()` [extracts top-level import statements], `ast.parse()` [parses Python source into AST], `ast.walk()` [traverses AST nodes], `filepath.read_text()` [reads file content], `subprocess.check_output()` [executes git log command], `isinstance()` [type checking for FunctionDef/AsyncFunctionDef], `str.strip()` [whitespace cleanup], `str.splitlines()` [line splitting], `str.decode()` [bytes to string conversion]
    - Imports used: `__future__.annotations` [enables postponed evaluation of type hints], `ast` [abstract syntax tree parsing], `pathlib.Path` [filesystem path handling], `subprocess` [external process execution], `typing.Any` [generic type annotation], `typing.Dict` [dictionary type annotation], `typing.List` [list type annotation]
    - External services: Git command-line tool (required for changelog generation; gracefully fails if unavailable)
    - AST-based parsing was chosen over regex or string matching because it provides accurate, syntactically-aware identification of function definitions and their internal calls, avoiding false positives from comments, strings, or nested scopes
    - The `ast.walk()` approach iterates through all nodes rather than using a visitor pattern because it is simpler for one-off lookups and the performance cost is negligible for typical file sizes
    - Git's `-L` option (line-range filtering) was selected over parsing all commits because it provides function-specific history without requiring manual line number tracking or heuristic-based filtering
    - Fail-closed exception handling (returning `{}` on any error) was chosen to ensure the function never crashes the calling agent; metadata collection is non-critical and should degrade gracefully
    - The `errors="ignore"` parameter in `.decode()` prevents UnicodeDecodeError from malformed git output, prioritizing robustness over strict validation
    - Separate try-except blocks for git operations allow the function to return partial metadata (deps without changelog) if git fails, rather than losing all data
    - The function does NOT recursively analyze imported modules or follow call chains, keeping analysis local and deterministic
    - Current implementation: Parses Python AST to extract function metadata (calls and imports) and augments with git commit history using line-range filtering, with graceful degradation on parsing or git failures.
    - DO NOT modify the exception handling to raise errors instead of returning `{}`; this breaks the fail-closed contract
    - DO NOT remove the `errors="ignore"` parameter from `.decode()` without understanding git output encoding edge cases
    - DO NOT change the git command structure without verifying that `-L :func_name:filepath` syntax is preserved for accurate line-range filtering
    - DO NOT assume `_get_function_calls()` or `_get_module_imports()` are available; verify they exist in the same module
    - ALWAYS preserve the distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
    - ALWAYS return an empty dict on failure rather than raising exceptions, to maintain compatibility with agent pipelines
    - ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
    - NOTE: This function depends on external git availability; it will silently degrade if git is not installed or the filepath is not in a git repository
    - NOTE: The `-n5` limit on git log means only the 5 most recent commits are captured; older history is discarded
    - NOTE: If a function name appears multiple times in a file (e.g., in different scopes), only the first match via `ast.walk()` is used; this may not be the intended function if there are name collisions
    -    print(f"[AGENTSPEC_CONTEXT] collect_metadata: Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions) | Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()` | Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages")
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
    - Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions)
    - Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()`
    - Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages
    - Returns a dictionary with structure `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success, or an empty dict `{}` if the function cannot be found, parsing fails, or any exception occurs during metadata collection
    - Gracefully degrades: if git history is unavailable, changelog defaults to `["- no git history available"]`; if no commits are found, defaults to `["- none yet"]`
    - Called by: [Inferred to be called by documentation generation or agent analysis pipelines that need to understand function dependencies]
    - Calls: `_get_function_calls()` [extracts function call names from AST node], `_get_module_imports()` [extracts top-level import statements], `ast.parse()` [parses Python source into AST], `ast.walk()` [traverses AST nodes], `filepath.read_text()` [reads file content], `subprocess.check_output()` [executes git log command], `isinstance()` [type checking for FunctionDef/AsyncFunctionDef], `str.strip()` [whitespace cleanup], `str.splitlines()` [line splitting], `str.decode()` [bytes to string conversion]
    - Imports used: `__future__.annotations` [enables postponed evaluation of type hints], `ast` [abstract syntax tree parsing], `pathlib.Path` [filesystem path handling], `subprocess` [external process execution], `typing.Any` [generic type annotation], `typing.Dict` [dictionary type annotation], `typing.List` [list type annotation]
    - External services: Git command-line tool (required for changelog generation; gracefully fails if unavailable)
    - AST-based parsing was chosen over regex or string matching because it provides accurate, syntactically-aware identification of function definitions and their internal calls, avoiding false positives from comments, strings, or nested scopes
    - The `ast.walk()` approach iterates through all nodes rather than using a visitor pattern because it is simpler for one-off lookups and the performance cost is negligible for typical file sizes
    - Git's `-L` option (line-range filtering) was selected over parsing all commits because it provides function-specific history without requiring manual line number tracking or heuristic-based filtering
    - Fail-closed exception handling (returning `{}` on any error) was chosen to ensure the function never crashes the calling agent; metadata collection is non-critical and should degrade gracefully
    - The `errors="ignore"` parameter in `.decode()` prevents UnicodeDecodeError from malformed git output, prioritizing robustness over strict validation
    - Separate try-except blocks for git operations allow the function to return partial metadata (deps without changelog) if git fails, rather than losing all data
    - The function does NOT recursively analyze imported modules or follow call chains, keeping analysis local and deterministic
    - Current implementation: Parses Python AST to extract function metadata (calls and imports) and augments with git commit history using line-range filtering, with graceful degradation on parsing or git failures.
    - DO NOT modify the exception handling to raise errors instead of returning `{}`; this breaks the fail-closed contract
    - DO NOT remove the `errors="ignore"` parameter from `.decode()` without understanding git output encoding edge cases
    - DO NOT change the git command structure without verifying that `-L :func_name:filepath` syntax is preserved for accurate line-range filtering
    - DO NOT assume `_get_function_calls()` or `_get_module_imports()` are available; verify they exist in the same module
    - ALWAYS preserve the distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
    - ALWAYS return an empty dict on failure rather than raising exceptions, to maintain compatibility with agent pipelines
    - ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
    - NOTE: This function depends on external git availability; it will silently degrade if git is not installed or the filepath is not in a git repository
    - NOTE: The `-n5` limit on git log means only the 5 most recent commits are captured; older history is discarded
    - NOTE: If a function name appears multiple times in a file (e.g., in different scopes), only the first match via `ast.walk()` is used; this may not be the intended function if there are name collisions
    -            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    - 2025-10-30: feat: robust docstring generation and Haiku defaults


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    1. Remove verbose debug print statement from function.
    2. Filter git log output to only include formatted changelog lines.
    3. Initial implementation of metadata collection with AST parsing and git history.

    '''
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))

        target = None
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func_name:
                target = n
                break
        if not target:
            return {}

        deps_calls = _get_function_calls(target)
        imports = _get_module_imports(tree)

        # Deterministic git changelog per function using `git log -L`.
        # NOTE: git log -L includes diffs, but we only want commit messages
        changelog: List[str]
        try:
            cmd = [
                "git", "log",
                "-L", f":{func_name}:{filepath}",
                "--pretty=format:- %ad: %s (%h)",
                "--date=short",
                "-n5",
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
            # Filter: only keep lines that match our commit format (starts with "- YYYY-MM-DD:" and contains hash in parentheses)
            # This ensures we only capture actual commit message lines, not diff content or other output
            # Pattern: "- YYYY-MM-DD: commit message (hash)"
            commit_pattern = re.compile(r'^-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)$')
            lines = []
            for ln in out.splitlines():
                ln = ln.strip()
                if ln and commit_pattern.match(ln):
                    lines.append(ln)
            changelog = lines or ["- none yet"]
        except Exception:
            changelog = ["- no git history available"]

        result = {
            "deps": {
                "calls": deps_calls,
                "imports": imports,
            },
            "changelog": changelog,
        }

        # Print deterministic metadata to stdout (forces it into agent context)
        print(f"[AGENTSPEC_METADATA] {func_name} in {filepath}")
        print(f"[AGENTSPEC_METADATA] Calls: {', '.join(deps_calls) if deps_calls else 'none'}")
        print(f"[AGENTSPEC_METADATA] Imports: {len(imports)} module(s)")
        print(f"[AGENTSPEC_METADATA] Changelog: {len(changelog)} commit(s)")
        for entry in changelog[:3]:  # Show first 3 commits
            print(f"[AGENTSPEC_METADATA]   {entry}")

        return result
    except Exception:
        # Fail closed: if analysis fails, just omit metadata
        return {}
