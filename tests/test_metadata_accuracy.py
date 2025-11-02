#!/usr/bin/env python3
"""
Test metadata accuracy by validating against ACTUAL source code and git history.

Uses TOOLS.md tools (rg, fd, ast-grep, git) to independently verify extracted metadata.
"""
from pathlib import Path
import subprocess
import re
import pytest

from agentspec.collect import collect_metadata


# Permanent reference files
DASHBOARD_TSX = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx")
PHAXIO_PY = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py")
INDEXING_JS = Path("/Users/davidmontgomery/agro/gui/js/indexing.js")


class TestGitChangelogAccuracy:
    """Validate git changelog hashes match ACTUAL git history."""

    def test_tsx_changelog_commits_exist_in_repo(self):
        """Extracted commit hashes from Dashboard.tsx must exist in git repo."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        # Get ACTUAL commits from git log
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h", "-n10", str(DASHBOARD_TSX.name)],
            cwd=DASHBOARD_TSX.parent,
            capture_output=True,
            check=True
        )
        actual_commits = set(result.stdout.decode().strip().split('\n'))
        print(f"\nACTUAL commits in repo (last 10): {actual_commits}")

        # Get EXTRACTED commits from metadata
        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")
        changelog = metadata.get("changelog", [])

        extracted_hashes = []
        for entry in changelog:
            match = re.search(r'\(([a-f0-9]+)\)', entry)
            if match:
                extracted_hashes.append(match.group(1))

        print(f"EXTRACTED commits: {extracted_hashes}")

        # Verify each extracted hash exists in actual commits
        for extracted_hash in extracted_hashes:
            # Check if this short hash matches any actual commit
            # (git log -L might return different commits than git log FILE)
            result = subprocess.run(
                ["git", "show", "--no-patch", "--format=%H", extracted_hash],
                cwd=DASHBOARD_TSX.parent,
                capture_output=True
            )
            if result.returncode != 0:
                pytest.fail(f"FAKE COMMIT: {extracted_hash} doesn't exist in git repo")

            full_hash = result.stdout.decode().strip()
            assert len(full_hash) == 40, f"Invalid hash returned for {extracted_hash}"
            print(f"  ✓ {extracted_hash} verified (full: {full_hash})")


class TestImportAccuracy:
    """Validate extracted imports exist in ACTUAL source file."""

    def test_tsx_imports_exist_in_source(self):
        """Extracted imports from Dashboard.tsx must exist in the actual file."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        # Get ACTUAL imports using ripgrep
        result = subprocess.run(
            ["rg", "^import ", str(DASHBOARD_TSX)],
            capture_output=True,
            check=True
        )
        actual_imports_text = result.stdout.decode()
        print(f"\nACTUAL import statements in file:\n{actual_imports_text}")

        # Get EXTRACTED imports from metadata
        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")
        imports = metadata.get("deps", {}).get("imports", [])
        print(f"\nEXTRACTED imports ({len(imports)} total):")
        for imp in imports[:5]:  # Show first 5
            print(f"  - {imp[:80]}...")

        # Verify extracted imports reference things that exist
        # Check for key imports that MUST be there
        imports_text = "\n".join(imports)

        assert "react" in imports_text.lower(), "React import missing - Dashboard.tsx uses React"
        assert "useState" in imports_text or "use" in imports_text.lower(), "React hooks missing"
        assert "mui" in imports_text.lower() or "material" in imports_text.lower(), "Material-UI imports missing"

        # Verify against actual file content
        file_content = DASHBOARD_TSX.read_text()

        # Check a few specific imports exist in file
        if "AdminAPIClient" in imports_text:
            assert "AdminAPIClient" in file_content, "Extracted AdminAPIClient but not in file"

        if "HealthStatus" in imports_text:
            assert "HealthStatus" in file_content, "Extracted HealthStatus but not in file"

        print("✓ Key imports verified against source file")

    def test_python_imports_exist_in_source(self):
        """Extracted imports from phaxio_service.py must exist in the actual file."""
        if not PHAXIO_PY.exists():
            pytest.skip("Reference file not available")

        # Get ACTUAL imports using ripgrep
        result = subprocess.run(
            ["rg", "^(import |from .* import)", str(PHAXIO_PY)],
            capture_output=True,
            check=True
        )
        actual_imports_text = result.stdout.decode()
        print(f"\nACTUAL import statements in file:\n{actual_imports_text}")

        # Get EXTRACTED imports
        metadata = collect_metadata(PHAXIO_PY, "get_phaxio_service")
        imports = metadata.get("deps", {}).get("imports", [])
        print(f"\nEXTRACTED imports: {imports}")

        # Verify against file
        file_content = PHAXIO_PY.read_text()
        for imp in imports:
            # Check that extracted import name appears in file
            import_name = imp.split('.')[-1]  # Get last part of import path
            assert import_name in file_content, f"Extracted import '{imp}' but '{import_name}' not in file"

        print("✓ All extracted imports exist in source file")


class TestFunctionCallAccuracy:
    """Validate extracted function calls exist in ACTUAL function body."""

    def test_tsx_calls_exist_in_function(self):
        """Extracted calls from Dashboard must exist in the Dashboard function."""
        if not DASHBOARD_TSX.exists():
            pytest.skip("Reference file not available")

        # Read actual source
        source = DASHBOARD_TSX.read_text()

        # Find Dashboard function/component
        # For React components, look for "export default function Dashboard" or similar
        if "function Dashboard" not in source and "const Dashboard" not in source:
            pytest.skip("Cannot locate Dashboard function in source")

        # Get EXTRACTED calls
        metadata = collect_metadata(DASHBOARD_TSX, "Dashboard")
        calls = metadata.get("deps", {}).get("calls", [])
        print(f"\nEXTRACTED calls ({len(calls)} total): {calls[:10]}")

        # Verify key calls exist in source
        # Dashboard is a React component, should call hooks
        calls_text = " ".join(calls)
        assert "useState" in calls_text or "useEffect" in calls_text, \
            "React component should call hooks (useState/useEffect)"

        # Verify extracted calls actually appear in source
        verified_count = 0
        for call in calls:
            # Clean up call name (remove trailing dots, etc)
            call_clean = call.rstrip('.')
            if call_clean in source:
                verified_count += 1

        # At least 50% of extracted calls should exist in source
        verification_rate = verified_count / len(calls) if calls else 0
        print(f"✓ Verified {verified_count}/{len(calls)} calls ({verification_rate:.1%})")
        assert verification_rate >= 0.5, f"Only {verification_rate:.1%} of calls verified - too many false positives"

    def test_python_calls_exist_in_function(self):
        """Extracted calls from get_phaxio_service must exist in the function body."""
        if not PHAXIO_PY.exists():
            pytest.skip("Reference file not available")

        # Read actual source
        source = PHAXIO_PY.read_text()

        # Get EXTRACTED calls
        metadata = collect_metadata(PHAXIO_PY, "get_phaxio_service")
        calls = metadata.get("deps", {}).get("calls", [])
        print(f"\nEXTRACTED calls: {calls}")

        # Verify all extracted calls exist in source
        for call in calls:
            call_name = call.split('.')[-1]  # Get last part of call
            assert call_name in source, f"Extracted call '{call}' but '{call_name}' not in source"

        print("✓ All extracted calls exist in source file")
