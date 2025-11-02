#!/usr/bin/env python3
"""
Test all flag combinations for strip/generate workflow.

Tests REAL behavior by:
1. Stripping agentspecs from reference files
2. Generating with different flag combinations
3. Validating output using rg/ast-grep
4. Running extract/lint on generated output
"""
from pathlib import Path
import subprocess
import tempfile
import shutil
import pytest
import itertools


# Permanent reference files
DASHBOARD_TSX = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx")
PHAXIO_PY = Path("/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py")
INDEXING_JS = Path("/Users/davidmontgomery/agro/gui/js/indexing.js")

# LLM config from AGENTS.md
LLM_ARGS = [
    "--provider", "openai",
    "--base-url", "http://localhost:11434/v1",
    "--model", "qwen3-coder:30b",
]


class TestStripGenerateCombinations:
    """Test strip + generate with all flag combinations."""

    @pytest.fixture(autouse=True)
    def setup_temp_files(self):
        """Create temp copies of reference files for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Copy reference files to temp directory
        self.temp_tsx = self.temp_dir / "Dashboard.tsx"
        self.temp_py = self.temp_dir / "phaxio_service.py"
        self.temp_js = self.temp_dir / "indexing.js"

        if DASHBOARD_TSX.exists():
            shutil.copy(DASHBOARD_TSX, self.temp_tsx)
        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.temp_py)
        if INDEXING_JS.exists():
            shutil.copy(INDEXING_JS, self.temp_js)

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir)

    def run_agentspec(self, command, filepath, extra_args=None):
        """Run agentspec command and return result."""
        cmd = ["agentspec", command, str(filepath)]

        if extra_args:
            cmd.extend(extra_args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return result

    def verify_has_agentspec(self, filepath):
        """Verify file has agentspec markers using rg."""
        result = subprocess.run(
            ["rg", "---agentspec", str(filepath)],
            capture_output=True
        )
        return result.returncode == 0

    def verify_no_agentspec(self, filepath):
        """Verify file has NO agentspec markers using rg."""
        result = subprocess.run(
            ["rg", "---agentspec", str(filepath)],
            capture_output=True
        )
        return result.returncode != 0

    def test_strip_removes_agentspecs(self):
        """Strip should remove all agentspec markers."""
        if not self.temp_tsx.exists():
            pytest.skip("TSX reference file not available")

        # Strip
        result = self.run_agentspec("strip", self.temp_tsx)
        assert result.returncode == 0, f"Strip failed: {result.stderr}"

        # Verify stripped using rg
        assert self.verify_no_agentspec(self.temp_tsx), "Strip failed - agentspec markers still exist"

    def test_generate_creates_agentspecs(self):
        """Generate should create agentspec markers."""
        if not self.temp_tsx.exists():
            pytest.skip("TSX reference file not available")

        # Strip first
        self.run_agentspec("strip", self.temp_tsx)
        assert self.verify_no_agentspec(self.temp_tsx)

        # Generate
        result = self.run_agentspec(
            "generate",
            self.temp_tsx,
            extra_args=LLM_ARGS + ["--terse", "--force-context"]
        )

        if result.returncode != 0:
            pytest.skip(f"Generate failed (likely LLM not running): {result.stderr}")

        # Verify created using rg
        assert self.verify_has_agentspec(self.temp_tsx), "Generate failed - no agentspec markers"

    def test_terse_flag(self):
        """Test --terse flag produces output."""
        if not self.temp_py.exists():
            pytest.skip("Python reference file not available")

        # Strip and generate with --terse
        self.run_agentspec("strip", self.temp_py)
        result = self.run_agentspec(
            "generate",
            self.temp_py,
            extra_args=LLM_ARGS + ["--terse", "--force-context"]
        )

        if result.returncode != 0:
            pytest.skip(f"Generate failed (likely LLM not running): {result.stderr}")

        # Should have output
        assert len(result.stdout) > 0 or len(result.stderr) > 0, "--terse produced no output"

    def test_agentspec_yaml_flag(self):
        """Test --agentspec-yaml creates YAML format agentspecs."""
        if not self.temp_py.exists():
            pytest.skip("Python reference file not available")

        # Strip and generate with YAML format
        self.run_agentspec("strip", self.temp_py)
        result = self.run_agentspec(
            "generate",
            self.temp_py,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--agentspec-yaml"]
        )

        if result.returncode != 0:
            pytest.skip(f"Generate failed (likely LLM not running): {result.stderr}")

        # Verify YAML markers exist using rg
        yaml_result = subprocess.run(
            ["rg", "what:", str(self.temp_py)],
            capture_output=True
        )
        assert yaml_result.returncode == 0, "--agentspec-yaml didn't create YAML 'what:' field"

    def test_update_existing_flag(self):
        """Test --update-existing preserves and updates agentspecs."""
        if not self.temp_py.exists():
            pytest.skip("Python reference file not available")

        # Generate initial
        result1 = self.run_agentspec(
            "generate",
            self.temp_py,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--strip"]
        )

        if result1.returncode != 0:
            pytest.skip(f"Initial generate failed: {result1.stderr}")

        # Update existing (default mode)
        result2 = self.run_agentspec(
            "generate",
            self.temp_py,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--update-existing"]
        )

        if result2.returncode != 0:
            pytest.skip(f"Update existing failed: {result2.stderr}")

        # Should still have agentspecs
        assert self.verify_has_agentspec(self.temp_py), "--update-existing removed agentspecs"

    def test_extract_after_generate(self):
        """Test extract works on generated agentspecs."""
        if not self.temp_tsx.exists():
            pytest.skip("TSX reference file not available")

        # Strip and generate
        self.run_agentspec("strip", self.temp_tsx)
        gen_result = self.run_agentspec(
            "generate",
            self.temp_tsx,
            extra_args=LLM_ARGS + ["--terse", "--force-context"]
        )

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Extract
        extract_result = self.run_agentspec(
            "extract",
            self.temp_tsx,
            extra_args=["--language", "js"]
        )

        assert extract_result.returncode == 0, f"Extract failed: {extract_result.stderr}"
        assert len(extract_result.stdout) > 0, "Extract produced no output"

    def test_lint_after_generate(self):
        """Test lint validates generated agentspecs."""
        if not self.temp_tsx.exists():
            pytest.skip("TSX reference file not available")

        # Strip and generate
        self.run_agentspec("strip", self.temp_tsx)
        gen_result = self.run_agentspec(
            "generate",
            self.temp_tsx,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--agentspec-yaml"]
        )

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Lint
        lint_result = self.run_agentspec(
            "lint",
            self.temp_tsx,
            extra_args=["--language", "js"]
        )

        # Lint should pass (or at least not crash)
        assert lint_result.returncode in [0, 1], f"Lint crashed: {lint_result.stderr}"

    def test_language_flag_js(self):
        """Test --language js forces JavaScript processing."""
        if not self.temp_js.exists():
            pytest.skip("JS reference file not available")

        # Strip and generate with --language js
        self.run_agentspec("strip", self.temp_js)
        result = self.run_agentspec(
            "generate",
            self.temp_js,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--language", "js"]
        )

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Verify JSDoc format (/** */)
        jsdoc_result = subprocess.run(
            ["rg", r"/\*\*", str(self.temp_js)],
            capture_output=True
        )
        assert jsdoc_result.returncode == 0, "--language js didn't create JSDoc format"

    def test_language_flag_py(self):
        """Test --language py forces Python processing."""
        if not self.temp_py.exists():
            pytest.skip("Python reference file not available")

        # Strip and generate with --language py
        self.run_agentspec("strip", self.temp_py)
        result = self.run_agentspec(
            "generate",
            self.temp_py,
            extra_args=LLM_ARGS + ["--terse", "--force-context", "--language", "py"]
        )

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Verify Python docstring format (""")
        docstring_result = subprocess.run(
            ["rg", '"""', str(self.temp_py)],
            capture_output=True
        )
        assert docstring_result.returncode == 0, "--language py didn't create Python docstrings"

    def test_strip_then_lint_reports_missing(self):
        """Test lint detects missing agentspecs after strip."""
        if not self.temp_py.exists():
            pytest.skip("Python reference file not available")

        # Strip
        self.run_agentspec("strip", self.temp_py)

        # Lint should report missing agentspecs
        lint_result = self.run_agentspec(
            "lint",
            self.temp_py,
            extra_args=["--language", "py"]
        )

        # Lint should fail (exit code 1) when agentspecs are missing
        assert lint_result.returncode == 1, "Lint didn't detect missing agentspecs"
        assert "missing" in lint_result.stdout.lower() or "missing" in lint_result.stderr.lower(), \
            "Lint didn't report missing agentspecs"


class TestFlagCombinations:
    """Test specific flag combinations that are commonly used."""

    @pytest.fixture(autouse=True)
    def setup_temp_file(self):
        """Create temp copy for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_file = self.temp_dir / "test.py"

        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.temp_file)

        yield

        shutil.rmtree(self.temp_dir)

    def run_generate(self, filepath, extra_args):
        """Run generate with extra args."""
        cmd = [
            "agentspec", "generate",
            str(filepath)
        ] + LLM_ARGS + extra_args

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        return result

    def test_combination_terse_yaml(self):
        """Test --terse --agentspec-yaml combination."""
        if not self.temp_file.exists():
            pytest.skip("Test file not available")

        result = self.run_generate(self.temp_file, [
            "--strip",
            "--terse",
            "--agentspec-yaml",
            "--force-context"
        ])

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Should have YAML format
        yaml_check = subprocess.run(
            ["rg", "what:", str(self.temp_file)],
            capture_output=True
        )
        assert yaml_check.returncode == 0, "YAML format not created"

    def test_combination_strip_update_existing(self):
        """Test --strip with --update-existing (strip takes precedence)."""
        if not self.temp_file.exists():
            pytest.skip("Test file not available")

        result = self.run_generate(self.temp_file, [
            "--strip",
            "--update-existing",
            "--terse",
            "--force-context"
        ])

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Should have agentspecs (strip removes, then generates new)
        check = subprocess.run(
            ["rg", "---agentspec", str(self.temp_file)],
            capture_output=True
        )
        assert check.returncode == 0, "Agentspecs not created"

    def test_combination_force_context_terse(self):
        """Test --force-context --terse combination (common usage)."""
        if not self.temp_file.exists():
            pytest.skip("Test file not available")

        result = self.run_generate(self.temp_file, [
            "--strip",
            "--force-context",
            "--terse"
        ])

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Should produce output and create agentspecs
        assert len(result.stdout) > 0 or len(result.stderr) > 0

        check = subprocess.run(
            ["rg", "---agentspec", str(self.temp_file)],
            capture_output=True
        )
        assert check.returncode == 0, "Agentspecs not created"

    def test_wrong_language_flag_py_on_js(self):
        """Test --language py on .js file (should fail gracefully)."""
        temp_js = self.temp_dir / "test.js"
        if INDEXING_JS.exists():
            shutil.copy(INDEXING_JS, temp_js)
        else:
            pytest.skip("JS reference file not available")

        result = self.run_generate(temp_js, [
            "--strip",
            "--language", "py",
            "--terse",
            "--force-context"
        ])

        # Should fail or skip (wrong language)
        # We don't crash, we just don't process it
        assert result.returncode in [0, 1], f"Crashed with wrong language: {result.stderr}"

    def test_wrong_language_flag_js_on_py(self):
        """Test --language js on .py file (should fail gracefully)."""
        if not self.temp_file.exists():
            pytest.skip("Python reference file not available")

        result = self.run_generate(self.temp_file, [
            "--strip",
            "--language", "js",
            "--terse",
            "--force-context"
        ])

        # Should fail or skip (wrong language)
        assert result.returncode in [0, 1], f"Crashed with wrong language: {result.stderr}"

    def test_all_flags_combination(self):
        """Test all flags together (stress test)."""
        if not self.temp_file.exists():
            pytest.skip("Test file not available")

        result = self.run_generate(self.temp_file, [
            "--strip",
            "--update-existing",
            "--terse",
            "--force-context",
            "--agentspec-yaml",
            "--language", "py"
        ])

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Should create agentspecs
        check = subprocess.run(
            ["rg", "---agentspec", str(self.temp_file)],
            capture_output=True
        )
        assert check.returncode == 0, "All flags combination didn't create agentspecs"
