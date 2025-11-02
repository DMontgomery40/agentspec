#!/usr/bin/env python3
"""
Comprehensive validation tests that actually verify functionality.

Tests REAL behavior against permanent reference files:
- Dashboard.tsx (TypeScript/TSX)
- phaxio_service.py (Python)
- indexing.js (JavaScript)

VALIDATES:
- Git changelog has actual commits (not "no git history")
- Dependencies are extracted (not empty)
- Correct parser used for TSX vs TS vs JS
- Metadata collection works for all extensions
- No duplicate JSDoc insertion
"""
from pathlib import Path
import re
import pytest

from agentspec.collect import collect_metadata
from agentspec.langs import LanguageRegistry


# Permanent reference files
DASHBOARD_TSX = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx")
PHAXIO_PY = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py")
INDEXING_JS = Path("/Users/davidmontgomery/agro/gui/js/indexing.js")


class TestGitChangelogValidation:
    """Validate git changelog actually extracts commits with dates and hashes."""

    def test_tsx_changelog_has_real_commits(self):
        """Dashboard.tsx should have REAL git history, not 'no git history'."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")
        changelog = metadata.get("changelog", [])

        # Should have actual commits
        assert len(changelog) >= 1, "Dashboard.tsx should have git history"

        # Should NOT be the fallback
        assert "no git history" not in str(changelog).lower(), "Git changelog broken - returning fallback"
        assert "none yet" not in str(changelog).lower(), "Git changelog broken - returning fallback"

        # Every entry should have date format YYYY-MM-DD
        for entry in changelog:
            assert re.search(r'\d{4}-\d{2}-\d{2}', entry), f"Missing date in: {entry}"

        # Every entry should have commit hash (7+ hex chars)
        commit_hashes = []
        for entry in changelog:
            match = re.search(r'\(([a-f0-9]{7,})\)', entry)
            assert match, f"Missing commit hash in: {entry}"
            commit_hashes.append(match.group(1))

        # CRITICAL: Verify commit hashes ACTUALLY EXIST in the repo
        import subprocess
        for commit_hash in commit_hashes:
            try:
                # Try to show the commit - will fail if hash doesn't exist
                result = subprocess.run(
                    ["git", "show", "--no-patch", "--format=%H", commit_hash],
                    cwd=DASHBOARD_TSX.parent,
                    capture_output=True,
                    check=True
                )
                # Verify it's a real commit (output should be a full hash)
                full_hash = result.stdout.decode().strip()
                assert len(full_hash) == 40, f"Invalid git hash for {commit_hash}: {full_hash}"
                assert full_hash.startswith(commit_hash), f"Hash mismatch: {commit_hash} vs {full_hash}"
            except subprocess.CalledProcessError:
                pytest.fail(f"Commit hash {commit_hash} doesn't exist in repo - metadata is FAKE")

    def test_python_changelog_has_real_commits(self):
        """phaxio_service.py should have REAL git history."""
        if not PHAXIO_PY.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(PHAXIO_PY, "get_phaxio_service")
        changelog = metadata.get("changelog", [])

        assert len(changelog) >= 1, "phaxio_service.py should have git history"
        assert "no git history" not in str(changelog).lower()

        for entry in changelog:
            assert re.search(r'\d{4}-\d{2}-\d{2}', entry), f"Missing date in: {entry}"
            assert re.search(r'\([a-f0-9]{7,}\)', entry), f"Missing commit hash in: {entry}"

    def test_js_changelog_has_real_commits(self):
        """indexing.js should have REAL git history."""
        if not INDEXING_JS.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(INDEXING_JS, "populateIndexRepoDropdown")
        changelog = metadata.get("changelog", [])

        assert len(changelog) >= 1, "indexing.js should have git history"
        assert "no git history" not in str(changelog).lower()

        for entry in changelog:
            assert re.search(r'\d{4}-\d{2}-\d{2}', entry), f"Missing date in: {entry}"
            assert re.search(r'\([a-f0-9]{7,}\)', entry), f"Missing commit hash in: {entry}"


class TestDependencyExtraction:
    """Validate dependencies are actually extracted (not empty)."""

    def test_tsx_extracts_dependencies(self):
        """Dashboard.tsx is a React component - should extract React imports and hooks."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")
        deps = metadata.get("deps", {})
        calls = deps.get("calls", [])
        imports = deps.get("imports", [])

        # React component MUST have imports
        assert len(imports) > 0, "Dashboard.tsx should have imports (it's a React component)"

        # Should extract function calls
        assert len(calls) > 0, "Dashboard.tsx should have function calls"

        # Sanity check: React component should import React stuff
        import_str = str(imports).lower()
        assert "react" in import_str or "use" in str(calls).lower(), \
            "Dashboard.tsx is a React component but no React imports/hooks found"

    def test_python_extracts_dependencies(self):
        """phaxio_service.py should extract imports and function calls."""
        if not PHAXIO_PY.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(PHAXIO_PY, "get_phaxio_service")
        deps = metadata.get("deps", {})
        calls = deps.get("calls", [])
        imports = deps.get("imports", [])

        # Production Python file MUST have imports
        assert len(imports) > 0, "phaxio_service.py should have imports"

        # Should extract calls
        assert len(calls) > 0, "get_phaxio_service should call other functions"

    def test_js_extracts_dependencies(self):
        """indexing.js should extract imports and function calls."""
        if not INDEXING_JS.exists():
            pytest.skip("Reference file not available")

        metadata = collect_metadata(INDEXING_JS, "populateIndexRepoDropdown")
        deps = metadata.get("deps", {})
        calls = deps.get("calls", [])
        imports = deps.get("imports", [])

        # JavaScript file should have some dependencies
        assert len(imports) > 0 or len(calls) > 0, \
            "indexing.js should have imports or function calls"


class TestTypeScriptParserSelection:
    """Validate correct parser is used for TSX vs TS vs JS."""

    def test_tsx_uses_tsx_parser_not_js_parser(self):
        """Critical: TSX files MUST use tsx_parser, not js_parser."""
        adapter = LanguageRegistry.get_by_extension('.tsx')

        # Should have all three parsers initialized
        assert adapter.js_parser is not None, "JavaScript parser not initialized"
        assert adapter.ts_parser is not None, "TypeScript parser not initialized"
        assert adapter.tsx_parser is not None, "TSX parser not initialized"

        # They should be DIFFERENT objects
        assert adapter.tsx_parser != adapter.js_parser, "TSX parser same as JS parser - BUG"
        assert adapter.tsx_parser != adapter.ts_parser, "TSX parser same as TS parser - BUG"

    def test_tsx_validates_jsx_syntax(self):
        """TSX parser should handle JSX syntax that JS parser cannot."""
        adapter = LanguageRegistry.get_by_extension('.tsx')

        # JSX syntax
        tsx_code = """
function Component(props) {
  return <div>{props.children}</div>;
}
"""

        # Should validate successfully with TSX parser
        try:
            result = adapter.validate_syntax_string(tsx_code, Path("test.tsx"))
            assert result is True, "TSX parser should validate JSX syntax"
        except Exception as e:
            pytest.fail(f"TSX parser failed on JSX syntax: {e}")

    def test_ts_uses_ts_parser(self):
        """TypeScript files should use ts_parser."""
        adapter = LanguageRegistry.get_by_extension('.ts')

        ts_code = """
interface User {
  name: string;
  age: number;
}
function greet(user: User): string {
  return `Hello, ${user.name}`;
}
"""

        try:
            result = adapter.validate_syntax_string(ts_code, Path("test.ts"))
            assert result is True, "TS parser should validate TypeScript syntax"
        except Exception as e:
            pytest.fail(f"TypeScript parser failed: {e}")

    def test_js_uses_js_parser(self):
        """JavaScript files should use js_parser."""
        adapter = LanguageRegistry.get_by_extension('.js')

        js_code = """
function greet(name) {
  return `Hello, ${name}`;
}
"""

        try:
            result = adapter.validate_syntax_string(js_code, Path("test.js"))
            assert result is True, "JS parser should validate JavaScript syntax"
        except Exception as e:
            pytest.fail(f"JavaScript parser failed: {e}")


class TestMetadataRoutingByExtension:
    """Validate collect_metadata routes .tsx/.ts/.jsx to JS path (not Python path)."""

    def test_tsx_routes_to_javascript_metadata(self):
        """Bug fix: .tsx files were falling through to Python metadata collection."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        # This should NOT return empty metadata
        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")

        # Should have deps structure
        assert "deps" in metadata, ".tsx file should route to JavaScript metadata collection"
        assert "changelog" in metadata, ".tsx file should have changelog"

        # Should NOT be completely empty (the bug symptom)
        deps = metadata.get("deps", {})
        changelog = metadata.get("changelog", [])

        # At minimum, should have SOME data (not all empty)
        has_data = (
            len(deps.get("calls", [])) > 0 or
            len(deps.get("imports", [])) > 0 or
            len(changelog) > 0
        )
        assert has_data, ".tsx file returned completely empty metadata - routing broken"

    def test_ts_routes_to_javascript_metadata(self):
        """TypeScript files should also route to JS metadata path."""
        # Create a simple .ts file for testing
        ts_file = Path(__file__).parent / "fixtures" / "typescript" / "simple.ts"
        if not ts_file.exists():
            pytest.skip("TypeScript fixture not available")

        metadata = collect_metadata(ts_file, "greet")

        assert "deps" in metadata, ".ts file should route to JavaScript metadata collection"
        assert "changelog" in metadata, ".ts file should have changelog"

    def test_jsx_routes_to_javascript_metadata(self):
        """JSX files should route to JS metadata path."""
        jsx_file = Path(__file__).parent / "fixtures" / "javascript" / "simple.jsx"
        if not jsx_file.exists():
            pytest.skip("JSX fixture not available")

        metadata = collect_metadata(jsx_file, "Component")

        assert "deps" in metadata, ".jsx file should route to JavaScript metadata collection"


class TestNoJSDocDuplication:
    """Validate JSDoc insertion doesn't create duplicates."""

    def test_insert_docstring_replaces_not_appends(self):
        """Critical: insert_docstring should REPLACE existing JSDoc, not append."""
        import tempfile

        adapter = LanguageRegistry.get_by_extension('.js')

        # Create temp file with existing JSDoc
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write("""
/**
 * Old docstring
 */
function test() {
  return 42;
}
""")
            temp_path = Path(f.name)

        try:
            # Insert new docstring
            new_docstring = "New docstring with agentspec"
            adapter.insert_docstring(temp_path, 5, new_docstring)

            # Read result
            content = temp_path.read_text()

            # Should have exactly ONE JSDoc block
            jsdoc_starts = content.count('/**')
            jsdoc_ends = content.count('*/')

            assert jsdoc_starts == 1, f"Found {jsdoc_starts} JSDoc starts - should be 1 (duplicate insertion bug)"
            assert jsdoc_ends == 1, f"Found {jsdoc_ends} JSDoc ends - should be 1 (duplicate insertion bug)"

            # Should have new content, not old
            assert "New docstring" in content, "New docstring not inserted"
            assert "Old docstring" not in content, "Old docstring not replaced (append bug)"

        finally:
            temp_path.unlink()


class TestSyntaxValidation:
    """Validate syntax validation actually catches errors."""

    def test_invalid_python_raises_error(self):
        """Python adapter should reject invalid Python syntax."""
        adapter = LanguageRegistry.get_by_extension('.py')

        invalid_python = "def broken( missing colon\n  return 42"

        with pytest.raises((ValueError, SyntaxError)):
            adapter.validate_syntax_string(invalid_python, Path("test.py"))

    def test_invalid_javascript_raises_error(self):
        """JavaScript adapter should reject invalid JS syntax."""
        adapter = LanguageRegistry.get_by_extension('.js')

        invalid_js = "function broken( missing paren { return 42; }"

        with pytest.raises(ValueError, match="ERROR nodes"):
            adapter.validate_syntax_string(invalid_js, Path("test.js"))

    def test_invalid_tsx_raises_error(self):
        """TSX adapter should reject invalid TSX syntax."""
        adapter = LanguageRegistry.get_by_extension('.tsx')

        invalid_tsx = "function Component() { return <div unclosed; }"

        with pytest.raises(ValueError, match="ERROR nodes"):
            adapter.validate_syntax_string(invalid_tsx, Path("test.tsx"))
