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
    """Normalize metadata values to a sorted list of unique strings."""
    if not values:
        return []

    if isinstance(values, (list, tuple, set)):
        cleaned = {str(v).strip() for v in values if str(v).strip()}
        return sorted(cleaned)

    value = str(values).strip()
    return [value] if value else []


def _collect_python_deps(filepath: Path, func_name: str) -> Optional[Tuple[List[str], List[str]]]:
    """Collect call/import metadata for Python files using AST helpers."""
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
    """Collect deterministic git changelog entries for a function.

    Falls back to file-level history if function-level tracking fails
    (common for JavaScript files using IIFEs where functions are nested).
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
    """Collect call/import metadata for JavaScript files via language adapter."""
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
