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
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def _get_function_calls(node: ast.AST) -> List[str]:
    """
    Brief one-line description.
    Extracts and returns a sorted, deduplicated list of all function names called within an AST node.

    WHAT THIS DOES:
    This function performs a complete traversal of an Abstract Syntax Tree (AST) node using ast.walk() to identify all function call expressions (ast.Call nodes) and extract their callable names. It handles three distinct call patterns: (1) simple function calls like `func()` where the callable is an ast.Name node, (2) method calls like `obj.method()` where the callable is an ast.Attribute node with a Name base, and (3) chained attribute calls like `obj.attr.method()` where the callable is an ast.Attribute node with another Attribute as its base. For method calls, it constructs qualified names in the format "base.method" when a base object is identifiable, or returns just the method name if the base cannot be determined. The function returns a sorted list with duplicates removed (via set deduplication), filtering out any empty strings that may result from edge cases. This is useful for static analysis, dependency tracking, and code introspection tasks.

    DEPENDENCIES:
    - Called by: agentspec/collect.py module-level analysis functions (inferred from file context)
    - Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering)
    - Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)
    - External services: None; this is pure static analysis using Python's built-in ast module

    WHY THIS APPROACH:
    This implementation uses ast.walk() for complete tree traversal rather than recursive descent because walk() is simpler, more maintainable, and guaranteed to visit all nodes. The isinstance() checks distinguish between different call patterns (Name vs. Attribute) because the AST structure differs fundamentally depending on whether a call is a simple function reference or a method/attribute access. Qualified names (e.g., "obj.method") are constructed for Attribute calls to preserve semantic information about which object the method belongs to, improving the usefulness of the extracted call list for dependency analysis. The deduplication via set comprehension reduces noise when the same function is called multiple times. Sorting ensures deterministic, reproducible output regardless of AST traversal order. The approach does NOT use a recursive visitor pattern (ast.NodeVisitor) because walk() is more concise for this simple extraction task. Performance is O(n log n) where n is the number of Call nodes, dominated by the final sort operation; the ast.walk() traversal is O(n) in total AST nodes.

    CHANGELOG:
    - Current implementation: Extracts all function call names from an AST node by walking the tree, handling simple calls, method calls, and chained attributes, then returns a sorted deduplicated list.

    AGENT INSTRUCTIONS:
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
    """
    print(f"[AGENTSPEC_CONTEXT] _get_function_calls: Called by: agentspec/collect.py module-level analysis functions (inferred from file context) | Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering) | Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)")
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
    """
    Brief one-line description.
    Extracts and returns a sorted list of all top-level module imports from an AST tree, deduplicating entries for coarse dependency analysis.

    WHAT THIS DOES:
    - Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements
    - Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes)
    - For `import` statements, extracts the module name directly from the alias
    - For `from...import` statements, constructs the full import path by joining the source module with the imported name using dot notation, handling cases where the module is None (bare `from ... import`)
    - Deduplicates the collected imports by converting to a set, filters out empty strings, and returns a sorted list for consistent ordering
    - Returns an empty list if the AST has no body or contains no import statements

    DEPENDENCIES:
    - Called by: agentspec/collect.py module-level analysis functions (inferred from context of coarse dependency collection)
    - Calls: getattr (built-in), isinstance (built-in), sorted (built-in), str.join (built-in)
    - Imports used: ast (standard library for AST node types), typing.List (type hints)
    - External services: None

    WHY THIS APPROACH:
    - Uses getattr with a default empty list to safely access the body attribute, preventing AttributeError if the AST node lacks a body (defensive programming)
    - Checks isinstance for both ast.Import and ast.ImportFrom separately because they have different structures: Import has a flat names list, while ImportFrom has both a module and a names list
    - Constructs full import paths for ImportFrom by joining module and alias name with dots, which provides more granular dependency information than just the module name
    - Handles the edge case where ImportFrom.module is None (occurs with relative imports like `from . import foo`) by using `or ""` and filtering empty parts
    - Deduplicates using set comprehension before sorting to ensure O(n log n) performance and eliminate redundant entries that might arise from multiple import statements importing the same module
    - Returns sorted output for deterministic, reproducible results across runs, which is critical for consistent dependency tracking and agent analysis
    - Alternative approach (not used): Could have used ast.walk() to find all imports recursively, but this function intentionally restricts to top-level imports only for "coarse" dependency context as documented in the docstring

    CHANGELOG:
    - Current implementation: Extracts top-level imports from AST module body, deduplicates, and returns sorted list for dependency analysis.

    AGENT INSTRUCTIONS:
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
    """
    print(f"[AGENTSPEC_CONTEXT] _get_module_imports: Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements | Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes) | For `import` statements, extracts the module name directly from the alias")
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
    """
    Collects git diffs for a function's last 5 commits for LLM summarization.
    
    Returns a list of dicts with structure:
    [
        {"date": "2025-10-29", "message": "Add feature X", "diff": "diff content..."},
        ...
    ]
    
    Used only when --diff-summary flag is set. These diffs are NOT included in
    docstrings directly - they're sent to LLM for concise summarization.
    """
    try:
        cmd = [
            "git", "log",
            "-L", f":{func_name}:{filepath}",
            "--pretty=format:COMMIT_START|||%ad|||%s|||",
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
                
                # Parse new commit header
                parts = line.split("|||")
                if len(parts) >= 3:
                    current_commit = {
                        "date": parts[1],
                        "message": parts[2],
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


def collect_metadata(filepath: Path, func_name: str) -> Dict[str, Any]:
    """
    Brief one-line description.

    Collects deterministic metadata (function dependencies and git changelog) for a specified function within a Python source file.

    WHAT THIS DOES:
    - Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions)
    - Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()`
    - Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages
    - Returns a dictionary with structure `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success, or an empty dict `{}` if the function cannot be found, parsing fails, or any exception occurs during metadata collection
    - Gracefully degrades: if git history is unavailable, changelog defaults to `["- no git history available"]`; if no commits are found, defaults to `["- none yet"]`

    DEPENDENCIES:
    - Called by: [Inferred to be called by documentation generation or agent analysis pipelines that need to understand function dependencies]
    - Calls: `_get_function_calls()` [extracts function call names from AST node], `_get_module_imports()` [extracts top-level import statements], `ast.parse()` [parses Python source into AST], `ast.walk()` [traverses AST nodes], `filepath.read_text()` [reads file content], `subprocess.check_output()` [executes git log command], `isinstance()` [type checking for FunctionDef/AsyncFunctionDef], `str.strip()` [whitespace cleanup], `str.splitlines()` [line splitting], `str.decode()` [bytes to string conversion]
    - Imports used: `__future__.annotations` [enables postponed evaluation of type hints], `ast` [abstract syntax tree parsing], `pathlib.Path` [filesystem path handling], `subprocess` [external process execution], `typing.Any` [generic type annotation], `typing.Dict` [dictionary type annotation], `typing.List` [list type annotation]
    - External services: Git command-line tool (required for changelog generation; gracefully fails if unavailable)

    WHY THIS APPROACH:
    - AST-based parsing was chosen over regex or string matching because it provides accurate, syntactically-aware identification of function definitions and their internal calls, avoiding false positives from comments, strings, or nested scopes
    - The `ast.walk()` approach iterates through all nodes rather than using a visitor pattern because it is simpler for one-off lookups and the performance cost is negligible for typical file sizes
    - Git's `-L` option (line-range filtering) was selected over parsing all commits because it provides function-specific history without requiring manual line number tracking or heuristic-based filtering
    - Fail-closed exception handling (returning `{}` on any error) was chosen to ensure the function never crashes the calling agent; metadata collection is non-critical and should degrade gracefully
    - The `errors="ignore"` parameter in `.decode()` prevents UnicodeDecodeError from malformed git output, prioritizing robustness over strict validation
    - Separate try-except blocks for git operations allow the function to return partial metadata (deps without changelog) if git fails, rather than losing all data
    - The function does NOT recursively analyze imported modules or follow call chains, keeping analysis local and deterministic

    CHANGELOG:
    - Current implementation: Parses Python AST to extract function metadata (calls and imports) and augments with git commit history using line-range filtering, with graceful degradation on parsing or git failures.

    AGENT INSTRUCTIONS:
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
    """
    print(f"[AGENTSPEC_CONTEXT] collect_metadata: Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions) | Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()` | Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages")
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
                "--pretty=format:- %ad: %s",
                "--date=short",
                "-n5",
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
            # Filter: only keep lines starting with "- " (commit messages), skip diff lines
            lines = [ln.strip() for ln in out.splitlines() if ln.strip() and ln.strip().startswith("- ")]
            changelog = lines or ["- none yet"]
        except Exception:
            changelog = ["- no git history available"]

        return {
            "deps": {
                "calls": deps_calls,
                "imports": imports,
            },
            "changelog": changelog,
        }
    except Exception:
        # Fail closed: if analysis fails, just omit metadata
        return {}
