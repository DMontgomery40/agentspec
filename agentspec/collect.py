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
from typing import Any, Dict, List, Optional, Tuple

from agentspec.langs import LanguageRegistry


def _get_function_calls(node: ast.AST) -> List[str]:
    """
    ---agentspec
    what: |
      Extracts all function call names from an AST node and returns them as a sorted, deduplicated list of strings.

      Traverses the entire AST subtree using ast.walk() to find all Call nodes. For each Call node, inspects the func attribute to determine the call type:
      - If func is an ast.Attribute (method call like obj.method()), constructs a qualified name by extracting the base object identifier (either from ast.Name.id or nested ast.Attribute.attr) and appending the method name with dot notation (e.g., "obj.method").
      - If func is an ast.Name (simple function call like func()), appends just the function identifier.
      - Ignores calls where the base cannot be determined (base is None for Attribute nodes with non-Name/non-Attribute values).

      Returns a sorted list with duplicates removed. Empty strings are filtered out before deduplication.

      Inputs: node (ast.AST) - any AST node to analyze
      Outputs: List[str] - sorted, unique function call names found in the node and all descendants

      Edge cases:
      - Nested method chains (e.g., obj.method1().method2()) extract only the outermost call names
      - Attribute access on non-Name/non-Attribute values (e.g., function returns) are skipped silently
      - Lambda calls and dynamic calls via variables are captured by their variable name, not their runtime target
      - Empty input nodes produce empty output list
        deps:
          calls:
            - ast.walk
            - calls.append
            - isinstance
            - sorted
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function enables static analysis of code to identify which functions and methods are invoked within a given code block. The approach uses ast.walk() for simplicity and completeness rather than manual recursion, ensuring all nested calls are discovered. Deduplication and sorting provide a canonical, readable output suitable for dependency tracking, call graph construction, or code impact analysis. The qualified name format (base.method) preserves semantic meaning for method calls while remaining simple to parse and compare.

    guardrails:
      - DO NOT rely on this function to determine runtime behavior or actual call targets, as it performs static analysis only and cannot resolve dynamic dispatch, monkey-patching, or indirect calls through variables.
      - DO NOT assume the extracted names are valid or callable; they are syntactic identifiers that may reference undefined symbols, built-ins, or non-existent attributes.
      - DO NOT use this for security analysis without additional validation, as it does not distinguish between safe library calls and potentially dangerous operations.
      - DO NOT expect this to handle all call patterns; it misses calls via getattr(), operator overloading, or calls stored in data structures.

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        ---/agentspec
    """
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
    ---agentspec
    what: |
      Extracts all module import names from an AST (Abstract Syntax Tree) by traversing the tree's body and collecting both direct imports (ast.Import) and from-imports (ast.ImportFrom).

      For ast.Import nodes, appends the full module name (e.g., "os", "numpy.random").
      For ast.ImportFrom nodes, constructs qualified names by joining the source module with the imported name (e.g., "os.path" from "from os import path").

      Returns a sorted, deduplicated list of import strings. Filters out empty strings that may result from malformed or relative imports where module is None.

      Inputs:
      - tree: ast.AST object (typically ast.Module from ast.parse())

      Outputs:
      - List[str]: sorted unique import identifiers

      Edge cases:
      - Handles relative imports where node.module is None by treating as empty string
      - Deduplicates imports using set comprehension before sorting
      - Gracefully handles trees without a body attribute via getattr with empty list default
      - Filters out empty strings to avoid polluting results from edge cases
        deps:
          calls:
            - getattr
            - imports.append
            - isinstance
            - join
            - sorted
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function enables static analysis of Python source code to identify external dependencies without executing the code. Sorting and deduplication ensure consistent, clean output for downstream processing (e.g., dependency tracking, import validation).

      Using ast module avoids regex fragility and handles Python syntax edge cases correctly. The approach trades off some complexity for robustness—parsing the full AST is more reliable than string matching.

    guardrails:
      - DO NOT execute the code or import modules—ast parsing is static analysis only, preventing side effects and security risks
      - DO NOT assume all imports are absolute—relative imports (from . import x) have module=None and must be handled gracefully
      - DO NOT skip deduplication—multiple import statements for the same module would pollute results without set filtering
      - DO NOT return unsorted results—consumers expect deterministic, comparable output for testing and caching

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
        ---/agentspec
    """
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


def _normalize_metadata_list(values: Any) -> List[str]:
    """
    ---agentspec
    what: |
      Normalizes arbitrary metadata values into a canonical sorted list of unique strings.

      Accepts multiple input types:
      - None/empty values: returns empty list []
      - Iterables (list, tuple, set): converts each element to string, strips whitespace, deduplicates via set, returns sorted list
      - Scalar values: converts to string, strips whitespace, returns single-element list if non-empty, else empty list

      All string conversions use str() to handle non-string types. Whitespace stripping occurs before deduplication to treat "value" and " value " as identical. Empty strings after stripping are filtered out. Final output is always sorted alphabetically for deterministic ordering.

      Edge cases handled:
      - Falsy iterables (empty list/tuple/set) return []
      - Whitespace-only strings become [] after strip
      - Mixed-type iterables (e.g., [1, "two", None]) are all converted to strings
      - Duplicate values across different types (e.g., 1 and "1") deduplicate to single "1"
        deps:
          calls:
            - isinstance
            - sorted
            - str
            - strip
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      Metadata often arrives from heterogeneous sources in inconsistent formats (user input, config files, API responses). Normalization ensures:
      1. Consistent representation for comparison and storage
      2. Deduplication prevents redundant metadata entries
      3. Sorted output enables deterministic behavior and easier testing
      4. Whitespace tolerance handles common formatting variations
      5. Type coercion via str() provides robustness without strict validation

      This permissive approach prioritizes usability over strictness, accepting any input and producing valid output rather than raising errors.

    guardrails:
      - DO NOT assume input is already a string or list—handle all types via str() conversion to prevent TypeErrors
      - DO NOT skip whitespace stripping—leading/trailing spaces cause false duplicates and inconsistent comparisons
      - DO NOT preserve input order—sorting is required for deterministic output and cache-friendly behavior
      - DO NOT return None or non-list types—callers expect a list always, even if empty
      - DO NOT mutate input—use set comprehension and sorted() to create new collections
      - DO NOT allow None elements in output—filter after strip() to prevent ["", None] artifacts

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    """
    if not values:
        return []

    if isinstance(values, (list, tuple, set)):
        cleaned = {str(v).strip() for v in values if str(v).strip()}
        return sorted(cleaned)

    value = str(values).strip()
    return [value] if value else []


def _collect_python_deps(filepath: Path, func_name: str) -> Optional[Tuple[List[str], List[str]]]:
    """
    ---agentspec
    what: |
      Extracts call and import metadata from a Python source file for a specific function using Abstract Syntax Tree (AST) parsing.

      **Inputs:**
      - filepath: Path object pointing to a Python source file
      - func_name: String name of the target function to analyze

      **Outputs:**
      - Returns a tuple of (deps_calls, imports) where:
        - deps_calls: List of function/method calls made within the target function
        - imports: List of module imports present in the file
      - Returns None if the file cannot be parsed, the function is not found, or any exception occurs during processing

      **Behavior:**
      1. Reads the source file as UTF-8 text
      2. Parses the source into an AST using ast.parse()
      3. Walks the AST to locate a FunctionDef or AsyncFunctionDef node matching func_name
      4. If found, extracts function calls via _get_function_calls() and module imports via _get_module_imports()
      5. Returns both lists as a tuple

      **Edge Cases:**
      - File encoding issues: Assumes UTF-8; non-UTF-8 files will raise an exception and return None
      - Syntax errors: Malformed Python files will fail ast.parse() and return None
      - Function not found: Returns None if func_name does not exist in the file
      - Duplicate function names: Returns the first matching FunctionDef or AsyncFunctionDef encountered during tree walk
      - Empty files or files with no imports/calls: Returns empty lists, not None
        deps:
          calls:
            - _get_function_calls
            - _get_module_imports
            - ast.parse
            - ast.walk
            - filepath.read_text
            - isinstance
            - str
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      AST-based static analysis provides accurate, syntax-aware extraction of dependencies without executing code, avoiding side effects and security risks. Using ast.walk() ensures all nested scopes are examined. The broad exception handling allows graceful degradation when files are unparseable or inaccessible, preventing the collection pipeline from crashing on malformed inputs. Returning None on failure signals to the caller that metadata could not be obtained, enabling fallback strategies. This approach scales to large codebases and integrates with automated tooling for dependency graph construction.

    guardrails:
      - DO NOT execute the source code; AST parsing is static analysis only to prevent arbitrary code execution and maintain security
      - DO NOT assume UTF-8 encoding without validation; explicitly specify encoding to handle files with different encodings gracefully
      - DO NOT raise exceptions to the caller; catch all exceptions and return None to allow batch processing of multiple files without pipeline interruption
      - DO NOT modify the source file or filesystem; this function is read-only and must have no side effects
      - DO NOT assume func_name is unique; document that the first match is returned and callers should handle potential ambiguity
      - DO NOT parse files larger than available memory; very large files may cause memory exhaustion; consider adding file size checks upstream

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    """
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))

        target = None
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func_name:
                target = n
                break

        if not target:
            return None

        deps_calls = _get_function_calls(target)
        imports = _get_module_imports(tree)
        return deps_calls, imports
    except Exception:
        return None


def _collect_git_changelog(filepath: Path, func_name: str) -> List[str]:
    """
    ---agentspec
    what: |
      Collects deterministic git changelog entries for a specified function within a file.

      **Inputs:**
      - filepath: Path object pointing to a source file (Python, JavaScript, etc.)
      - func_name: String name of the function to track

      **Outputs:**
      - List of strings formatted as "- YYYY-MM-DD: commit message (short hash)"
      - Returns up to 5 most recent commits
      - Falls back to ["- no git history available"] on any unrecoverable error

      **Behavior:**
      1. Resolves filepath to absolute path and locates the git repository root by walking up parent directories until .git is found
      2. Computes relative path from git root to target file
      3. Attempts function-level history using `git log -L :func_name:rel_path` to track changes to the specific function
      4. If function-level tracking fails (common for nested functions in IIFEs or JavaScript closures), falls back to file-level history using `git log` on the entire file
      5. Validates all output lines against regex pattern `^-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)$` to ensure deterministic, well-formed entries
      6. Returns empty list as ["- none yet"] if no valid commits found after fallback

      **Edge cases:**
      - File not in any git repository: returns ["- no git history available"]
      - Function name not found in file: silently falls back to file-level history
      - Subprocess errors (git not installed, permission denied): caught and returns ["- no git history available"]
      - Malformed git output: filtered out by regex validation, only well-formed lines included
      - Unicode decode errors: handled with errors="ignore" to prevent crashes
        deps:
          calls:
            - commit_pattern.match
            - decode
            - exists
            - filepath.is_file
            - filepath.relative_to
            - filepath.resolve
            - lines.append
            - list
            - ln.strip
            - out.splitlines
            - re.compile
            - str
            - subprocess.check_output
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      Function-level git tracking provides fine-grained change history for documentation purposes, enabling readers to understand when and why specific functions were modified. The fallback to file-level history is necessary because git's `-L` option (line-range tracking) does not work reliably for nested functions in JavaScript IIFEs or other dynamically-scoped constructs where function boundaries are not statically determinable by git.

      The regex validation ensures output is deterministic and parseable by downstream consumers, preventing malformed or partial git output from corrupting documentation. Running git commands in the correct repository root (not current working directory) ensures correctness when the codebase spans multiple git repositories or when the tool is invoked from arbitrary directories.

      Limiting to 5 commits balances completeness with readability in generated documentation. The short hash (4+ chars) provides sufficient uniqueness for most repositories while keeping output compact.

    guardrails:
      - DO NOT run git commands in the current working directory without first locating the file's actual git root; this causes failures when the file is in a different repository than the CWD
      - DO NOT assume function-level history will succeed; always provide a file-level fallback for languages/patterns where function boundaries are ambiguous
      - DO NOT include malformed or partial git output in results; validate all lines against the expected format regex to maintain determinism
      - DO NOT raise exceptions on git failures; always return a sensible fallback message so that missing history does not break documentation generation
      - DO NOT decode git output as UTF-8 without error handling; use errors="ignore" to gracefully handle non-UTF-8 bytes in commit messages

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    """
    try:
        # CRITICAL: Git command must run in the file's git repo, not current working directory
        # Find git root for this file
        filepath = filepath.resolve()
        file_dir = filepath.parent if filepath.is_file() else filepath

        # Find git root by walking up directories
        git_root = file_dir
        for parent in [file_dir] + list(file_dir.parents):
            if (parent / ".git").exists():
                git_root = parent
                break

        # Get relative path from git root
        try:
            rel_path = filepath.relative_to(git_root)
        except ValueError:
            # File not in a git repo
            return ["- no git history available"]

        # Try function-level history first
        cmd = [
            "git",
            "log",
            "-L",
            f":{func_name}:{rel_path}",
            "--pretty=format:- %ad: %s (%h)",
            "--date=short",
            "-n5",
        ]
        try:
            out = subprocess.check_output(cmd, cwd=git_root, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
            commit_pattern = re.compile(r"^-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)$")
            lines = []
            for ln in out.splitlines():
                ln = ln.strip()
                if ln and commit_pattern.match(ln):
                    lines.append(ln)
            if lines:
                return lines
        except subprocess.CalledProcessError:
            pass  # Fall through to file-level history

        # Fallback to file-level history (e.g., for nested functions in IIFEs)
        file_cmd = [
            "git",
            "log",
            "--pretty=format:- %ad: %s (%h)",
            "--date=short",
            "-n5",
            str(rel_path),
        ]
        out = subprocess.check_output(file_cmd, cwd=git_root, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        commit_pattern = re.compile(r"^-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)$")
        lines = []
        for ln in out.splitlines():
            ln = ln.strip()
            if ln and commit_pattern.match(ln):
                lines.append(ln)
        return lines or ["- none yet"]
    except Exception:
        return ["- no git history available"]


def _collect_javascript_metadata(filepath: Path, func_name: str) -> Optional[Dict[str, Any]]:
    """
    ---agentspec
    what: |
      Collects call and import metadata for JavaScript files by delegating to a language-specific adapter.

      **Inputs:**
      - filepath: Path object pointing to a JavaScript file
      - func_name: Name of the function or entity to analyze within the file

      **Outputs:**
      - Returns a dictionary with "deps" (containing "calls" and "imports" lists) and "changelog" metadata, or None if no adapter is available
      - "calls": sorted list of detected function/method calls (e.g., ["foo.bar", "baz"])
      - "imports": sorted list of detected import statements or require() calls
      - "changelog": git history metadata for the file and function

      **Behavior:**
      1. Retrieves the appropriate language adapter from LanguageRegistry based on file path
      2. Attempts to gather metadata via adapter.gather_metadata(); silently catches exceptions and defaults to empty dict
      3. Validates that returned metadata is a dict; coerces to empty dict if not
      4. Normalizes both "calls" and "imports" lists via _normalize_metadata_list()
      5. If adapter extraction yields no calls or imports, performs lightweight fallback regex scanning on raw source:
         - Regex pattern `([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*\(` captures function/method names followed by `(`
         - Scans for lines starting with "import " or containing "require(" to collect import statements
      6. Collects git changelog metadata via _collect_git_changelog()
      7. Returns structured dict or None if no adapter found

      **Edge cases:**
      - File read failures (encoding errors, permissions) are caught and treated as empty source
      - Adapter exceptions are silently swallowed; metadata defaults to {}
      - Non-dict adapter returns are coerced to {}
      - Regex fallback is naive and may over-capture or under-capture in complex JavaScript
        deps:
          calls:
            - LanguageRegistry.get_by_path
            - _collect_git_changelog
            - _normalize_metadata_list
            - _re.findall
            - adapter.gather_metadata
            - filepath.read_text
            - import_lines.append
            - isinstance
            - line.strip
            - metadata.get
            - set
            - sorted
            - src.splitlines
            - startswith
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function provides a resilient, multi-layered approach to extracting JavaScript dependencies:
      - **Adapter delegation** allows language-specific parsing (e.g., tree-sitter) for accuracy
      - **Exception handling** prevents crashes from missing dependencies or malformed files
      - **Regex fallback** ensures partial metadata extraction even when advanced parsing is unavailable, improving coverage
      - **Normalization** guarantees consistent list types and prevents downstream type errors
      - **Git changelog integration** provides historical context for dependency changes

      The tradeoff is that regex fallback is imprecise (may capture false positives or miss dynamic calls), but it gracefully degrades when the primary adapter fails rather than returning nothing.

    guardrails:
      - DO NOT assume adapter.gather_metadata() always returns a valid dict—always validate and coerce to {} to prevent KeyError or AttributeError downstream
      - DO NOT skip the regex fallback if adapter extraction is incomplete; missing deps metadata reduces traceability and may cause incomplete dependency graphs
      - DO NOT use raw regex patterns without bounds checking on source file size; extremely large files could cause performance degradation (consider adding file size limits if needed)
      - DO NOT expose raw regex matches without deduplication and sorting; inconsistent ordering breaks reproducibility and complicates testing
      - DO NOT fail silently on file read errors without logging; silent failures make debugging difficult when source files are inaccessible

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    """
    adapter = LanguageRegistry.get_by_path(filepath)
    if not adapter:
        return None

    try:
        metadata = adapter.gather_metadata(filepath, func_name)  # type: ignore[arg-type]
    except Exception:
        metadata = {}

    if not isinstance(metadata, dict):
        metadata = {}

    calls = _normalize_metadata_list(metadata.get("calls"))
    imports = _normalize_metadata_list(metadata.get("imports"))

    # Fallback: lightweight regex scan if adapter couldn't extract anything (e.g., missing tree-sitter)
    if not calls or not imports:
        try:
            src = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            src = ""
        # naive call detection: foo.bar(  -> capture foo.bar
        import re as _re
        if not calls:
            call_matches = _re.findall(r"([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*\(", src)
            calls = sorted({m for m in call_matches})
        if not imports:
            # collect ES module imports
            import_lines = []
            for line in src.splitlines():
                if line.strip().startswith("import ") or "require(" in line:
                    import_lines.append(line.strip())
            imports = sorted(set(import_lines))

    changelog = _collect_git_changelog(filepath, func_name)

    return {
        "deps": {
            "calls": calls,
            "imports": imports,
        },
        "changelog": changelog,
    }


def collect_changelog_diffs(filepath: Path, func_name: str) -> List[Dict[str, str]]:
    """
    ---agentspec
    what: |
      Retrieves the git history of a specific function within a file using `git log -L` (line-based history).

      **Inputs:**
      - filepath: Path object pointing to the target Python file
      - func_name: String name of the function to trace (e.g., "my_function")

      **Outputs:**
      - List of dictionaries, each containing:
        - "hash": commit SHA (short form)
        - "date": commit date in YYYY-MM-DD format
        - "message": commit message subject line
        - "diff": accumulated diff/patch content for that commit
      - Empty list [] if git command fails or no history found

      **Behavior:**
      - Executes `git log -L :func_name:filepath` to extract function-specific history (last 5 commits)
      - Parses output using custom delimiter "COMMIT_START|||" to separate commit metadata from diff content
      - Accumulates multi-line diff output per commit and associates it with commit metadata
      - Handles UTF-8 decoding with error suppression to tolerate non-UTF8 bytes in diffs
      - Gracefully returns empty list on any exception (git not available, file not in repo, invalid path, etc.)

      **Edge cases:**
      - Function name not found in file: git returns empty output, function returns []
      - File not tracked by git: git command fails, exception caught, returns []
      - Malformed commit header (fewer than 4 pipe-delimited parts): header skipped, diff lines discarded
      - Non-UTF8 characters in diff: decoded with errors="ignore", lossy but non-fatal
      - No commits in history: returns []
      - Uncommitted changes: not included (git log only shows committed history)
        deps:
          calls:
            - commits.append
            - decode
            - diff_lines.append
            - join
            - len
            - line.split
            - line.startswith
            - out.splitlines
            - subprocess.check_output
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function enables automated documentation generation by extracting the evolution of a specific function.
      Using `git log -L` is the most precise method to track function-level changes rather than file-level history,
      avoiding noise from unrelated modifications in the same file. The custom delimiter parsing allows robust
      separation of structured metadata (hash/date/message) from unstructured diff content. Silent exception handling
      ensures the documentation pipeline continues even in non-git environments or edge cases, with graceful degradation
      to an empty changelog rather than pipeline failure.

    guardrails:
      - DO NOT assume git is installed or the file is in a git repository; always catch exceptions and return [] to prevent pipeline crashes
      - DO NOT parse commit metadata by line count or position; use the explicit "COMMIT_START|||" delimiter to handle variable-length messages and diffs
      - DO NOT strip or normalize diff content; preserve raw output to maintain patch fidelity for downstream consumers
      - DO NOT increase the commit limit (-n5) without considering performance impact on large histories; current limit balances recency with query speed
      - DO NOT assume func_name exactly matches the git function signature; git's -L heuristic may fail on complex nested functions or lambdas

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
        ---/agentspec
    """
    try:
        cmd = [
            "git",
            "log",
            "-L",
            f":{func_name}:{filepath}",
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
    """
    ---agentspec
    what: |
      Extracts the source code of a named function while removing its docstring and comment-only lines.

      Takes a source code string and function name, parses it into an AST, locates the matching function definition (sync or async), and returns the function source with:
      - Leading docstring removed (if present as first statement)
      - All pure comment-only lines stripped
      - Indentation preserved for remaining code lines

      Inputs:
        - src: Complete Python source code as string
        - func_name: Name of function to extract

      Outputs:
        - String containing function definition and body without docstring/comments
        - Empty string if function not found or parsing fails

      Edge cases:
        - Handles both ast.Constant (Python 3.8+) and legacy ast.Str docstring representations
        - Gracefully returns empty string on any parse/extraction exception
        - Correctly maps absolute line numbers to relative slice indices when removing docstring
        - Preserves original indentation of remaining lines
        - Handles functions with no docstring (no-op removal)
        - Handles async function definitions identically to sync functions
        deps:
          calls:
            - ast.parse
            - ast.walk
            - cleaned.append
            - getattr
            - hasattr
            - isinstance
            - join
            - ln.lstrip
            - max
            - src.split
            - stripped.startswith
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function supports code introspection workflows where docstrings and comments need to be excluded from analysis or serialization. The dual AST node type handling (ast.Constant and ast.Str) ensures compatibility across Python versions. Exception suppression with empty string fallback prevents crashes during exploratory code analysis. Line-by-line comment filtering is simpler and more reliable than regex-based approaches for preserving code structure.

    guardrails:
      - DO NOT assume docstring is always present—check body existence and first statement type before removal to avoid index errors
      - DO NOT use only ast.Constant for docstring detection—legacy Python versions use ast.Str, requiring dual-path checking
      - DO NOT rely on relative line numbers without mapping to absolute indices—off-by-one errors occur when slicing extracted function lines
      - DO NOT strip lines that contain code followed by comments—only remove lines that are pure comments (after lstrip, start with #)
      - DO NOT raise exceptions on malformed source—catch all exceptions and return empty string to allow graceful degradation in batch processing

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
        ---/agentspec
    """
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                lines = src.split("\n")
                start = (node.lineno or 1) - 1
                end = node.end_lineno or node.lineno  # end is exclusive when slicing
                func_lines = lines[start:end]

                # Remove leading docstring if present using AST body[0]
                if getattr(node, "body", None):
                    first_stmt = node.body[0]
                    is_doc = False
                    if isinstance(first_stmt, ast.Expr):
                        if isinstance(getattr(first_stmt, "value", None), ast.Constant) and isinstance(
                            first_stmt.value.value, str
                        ):
                            is_doc = True
                        elif hasattr(ast, "Str") and isinstance(getattr(first_stmt, "value", None), ast.Str):
                            is_doc = True
                    if is_doc:
                        ds_start_abs = (first_stmt.lineno or node.lineno) - 1
                        ds_end_abs = first_stmt.end_lineno or first_stmt.lineno
                        # Delete docstring range from func_lines using absolute indices mapped to slice
                        del_start = max(0, ds_start_abs - start)
                        del_end = max(del_start, ds_end_abs - start)
                        del func_lines[del_start:del_end]

                # Also drop pure comment-only lines
                cleaned = []
                for ln in func_lines:
                    stripped = ln.lstrip()
                    if stripped.startswith("#"):
                        continue
                    cleaned.append(ln)
                return "\n".join(cleaned)
        return ""
    except Exception:
        return ""


def collect_function_code_diffs(filepath: Path, func_name: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    ---agentspec
    what: |
      Collects git commit history for a specific file and extracts code-level diffs for a named function across recent commits.

      Inputs:
        - filepath: Path object pointing to a Python source file
        - func_name: String name of the function to track
        - limit: Maximum number of recent commits to inspect (default 5)

      Outputs:
        - List of dictionaries, each containing:
          - date: Commit date in YYYY-MM-DD format
          - message: Commit message
          - hash: 7-character short commit hash
          - diff: Unified diff showing only added/removed code lines (excluding headers and context)

      Behavior:
        1. Queries git log for the N most recent commits touching the file
        2. For each commit, retrieves the function source at that commit and its parent
        3. Extracts function bodies (excluding docstrings) using _extract_function_source_without_docstring
        4. Computes unified diff between parent and current versions
        5. Filters diff output to include only +/- lines, excluding:
           - File/hunk headers (+++, ---, @@)
           - Context lines (leading space)
           - Comment-only changes (lines containing only whitespace and # after the +/-)
        6. Skips commits where the function did not exist in either version or had no code changes
        7. Returns empty list on any top-level exception (git command failure, subprocess errors, etc.)

      Edge cases:
        - Function does not exist in current or parent commit: gracefully skipped
        - Commit has no parent (initial commit): prev_src set to empty string
        - File encoding issues: handled via errors="ignore" in decode
        - Malformed git log output: lines with fewer than 3 pipe-separated parts are skipped
        - No code changes detected (only comments changed): commit excluded from results
        deps:
          calls:
            - _extract_function_source_without_docstring
            - changes.append
            - content.lstrip
            - curr_func.splitlines
            - decode
            - difflib.unified_diff
            - dl.startswith
            - int
            - join
            - len
            - line.split
            - ln.strip
            - log_out.splitlines
            - prev_func.splitlines
            - results.append
            - startswith
            - str
            - subprocess.check_output
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      This function enables historical analysis of function-level changes without requiring full file diffs, reducing noise and focusing on semantic code modifications. By filtering comment-only changes, it avoids cluttering results with documentation updates. The git-based approach leverages existing repository history rather than external APIs or databases. Graceful error handling ensures robustness in environments with incomplete git history or encoding anomalies. The limit parameter allows tuning between comprehensiveness and performance.

    guardrails:
      - DO NOT include comment-only changes in diffs; they obscure actual code evolution and inflate result size
      - DO NOT fail the entire operation on individual commit retrieval errors; use try-except per commit to maximize partial results
      - DO NOT assume function exists in all commits; absence in both versions is a valid skip condition
      - DO NOT parse git output without validating field count; malformed lines can cause index errors
      - DO NOT expose raw subprocess exceptions to caller; wrap in empty list return to maintain consistent interface
      - DO NOT include file/hunk headers or context lines in diff output; they add no semantic value for function-level tracking

        changelog:
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
        ---/agentspec
    """
    results: List[Dict[str, str]] = []
    try:
        # Recent commits touching the file
        log_cmd = [
            "git",
            "log",
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
                prev_src = subprocess.check_output(
                    ["git", "show", f"{commit}^:{filepath}"], stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="ignore")
            except Exception:
                prev_src = ""
            try:
                curr_src = subprocess.check_output(
                    ["git", "show", f"{commit}:{filepath}"], stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="ignore")
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
                if dl.startswith("+++") or dl.startswith("---") or dl.startswith("@@") or dl.startswith(" "):
                    continue
                if dl.startswith("+") or dl.startswith("-"):
                    # Exclude comment-only changes (after +/- and whitespace, a '#')
                    content = dl[1:]
                    if content.lstrip().startswith("#"):
                        continue
                    changes.append(dl)

            if not changes:
                # No code changes within the function for this commit
                continue

            # Get short hash for display
            short_hash = commit[:7] if len(commit) >= 7 else commit

            results.append(
                {
                    "date": date,
                    "message": message,
                    "hash": short_hash,
                    "diff": "\n".join(changes),
                }
            )
    except Exception:
        return []

    return results


def collect_metadata(filepath: Path, func_name: str) -> Dict[str, Any]:
    """
    ---agentspec
    what: |
      Collects metadata about a function across multiple dimensions: dependency calls, module imports, and git changelog history.

      Accepts a filepath (string or Path object) and function name, then routes to language-specific collectors based on file extension.

      For JavaScript/TypeScript files (.js, .mjs, .jsx, .ts, .tsx): delegates to _collect_javascript_metadata(), extracting calls, imports, and changelog from the result structure.

      For Python files: calls _collect_python_deps() to extract function calls and imports, then _collect_git_changelog() to retrieve commit history for that function.

      Returns a dictionary with structure: {"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}.

      Prints diagnostic output with [AGENTSPEC_METADATA] prefix showing function name, file path, call count, import count, and first 3 changelog entries.

      Returns empty dict {} if language-specific collection returns falsy value (None, empty dict, etc.).

      Edge cases: handles mixed case file extensions via .lower(), gracefully degrades when no metadata found, normalizes Path objects.
        deps:
          calls:
            - Path
            - _collect_git_changelog
            - _collect_javascript_metadata
            - _collect_python_deps
            - get
            - join
            - js_result.get
            - len
            - print
            - suffix.lower
          imports:
            - __future__.annotations
            - agentspec.langs.LanguageRegistry
            - ast
            - difflib
            - pathlib.Path
            - re
            - subprocess
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - typing.Tuple


    why: |
      Centralizes metadata collection across heterogeneous codebases (Python + JavaScript/TypeScript) under a single interface, enabling unified dependency analysis and change tracking.

      Language-specific routing avoids forcing incompatible parsing logic; each language collector handles its own AST/syntax requirements.

      Structured output (deps + changelog) supports both static analysis (what does this function call?) and temporal analysis (how has it changed?), useful for impact analysis and documentation generation.

      Diagnostic printing aids debugging and provides visibility into collection success/failure without requiring external logging infrastructure.

      Early return on empty results prevents downstream processing of incomplete metadata.

    guardrails:
      - DO NOT assume file extension case consistency; always normalize via .lower() before comparison to handle .JS, .Js, etc.
      - DO NOT mix language-specific result structures; ensure JavaScript and Python paths both normalize to identical output schema before returning.
      - DO NOT print sensitive information in diagnostic output; changelog entries may contain commit messages with credentials or internal details.
      - DO NOT silently fail on malformed paths; Path() constructor should validate but caller should handle non-existent files explicitly.
      - DO NOT assume function exists in file; language collectors must handle missing function gracefully and return empty/falsy rather than raising.
      - DO NOT return partial results; if any collection step fails, return {} rather than incomplete deps or missing changelog to prevent downstream assumptions.

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
          - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
        ---/agentspec
    """
    filepath = Path(filepath)

    if filepath.suffix.lower() in {".js", ".mjs", ".jsx", ".ts", ".tsx"}:
        js_result = _collect_javascript_metadata(filepath, func_name)
        if not js_result:
            return {}

        deps_calls = js_result["deps"].get("calls", [])
        imports = js_result["deps"].get("imports", [])
        changelog = js_result.get("changelog", [])

        print(f"[AGENTSPEC_METADATA] {func_name} in {filepath}")
        print(f"[AGENTSPEC_METADATA] Calls: {', '.join(deps_calls) if deps_calls else 'none'}")
        print(f"[AGENTSPEC_METADATA] Imports: {len(imports)} module(s)")
        print(f"[AGENTSPEC_METADATA] Changelog: {len(changelog)} commit(s)")
        for entry in changelog[:3]:
            print(f"[AGENTSPEC_METADATA]   {entry}")

        return js_result

    python_deps = _collect_python_deps(filepath, func_name)
    if not python_deps:
        return {}

    deps_calls, imports = python_deps

    changelog = _collect_git_changelog(filepath, func_name)

    result = {
        "deps": {
            "calls": deps_calls,
            "imports": imports,
        },
        "changelog": changelog,
    }

    print(f"[AGENTSPEC_METADATA] {func_name} in {filepath}")
    print(f"[AGENTSPEC_METADATA] Calls: {', '.join(deps_calls) if deps_calls else 'none'}")
    print(f"[AGENTSPEC_METADATA] Imports: {len(imports)} module(s)")
    print(f"[AGENTSPEC_METADATA] Changelog: {len(changelog)} commit(s)")
    for entry in changelog[:3]:
        print(f"[AGENTSPEC_METADATA]   {entry}")

    return result
