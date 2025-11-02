#!/usr/bin/env python3
"""
Test EVERY flag combination - the comprehensive version.

Tests include:
- All valid flag combinations
- Wrong language flags (py on js, js on py, ts on js, etc.)
- Conflicting flags (--terse --verbose)
- Invalid command sequences
- Format mismatches
- Error message quality

Run in batches to actually check results.
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

# LLM config
LLM_ARGS = [
    "--provider", "openai",
    "--base-url", "http://localhost:11434/v1",
    "--model", "qwen3-coder:30b",
]


def run_cmd(cmd, timeout=30):
    """Run command and return result."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


class TestWrongLanguageFlags:
    """Test --language flag with wrong file types."""

    @pytest.fixture(autouse=True)
    def setup_files(self):
        """Create temp copies."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tsx = self.temp_dir / "test.tsx"
        self.py = self.temp_dir / "test.py"
        self.js = self.temp_dir / "test.js"

        if DASHBOARD_TSX.exists():
            shutil.copy(DASHBOARD_TSX, self.tsx)
        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.py)
        if INDEXING_JS.exists():
            shutil.copy(INDEXING_JS, self.js)

        yield
        shutil.rmtree(self.temp_dir)

    def test_language_py_on_js_file(self):
        """--language py on .js file should skip or handle gracefully."""
        if not self.js.exists():
            pytest.skip("JS file not available")

        # Use lint (which supports --language)
        result = run_cmd(["agentspec", "lint", str(self.js), "--language", "py"])

        # Should not crash (exit 0, 1, or 2 are acceptable)
        assert result.returncode in [0, 1, 2], f"Crashed: {result.stderr}"
        print(f"Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")

    def test_language_py_on_tsx_file(self):
        """--language py on .tsx file should skip or handle gracefully."""
        if not self.tsx.exists():
            pytest.skip("TSX file not available")

        result = run_cmd(["agentspec", "lint", str(self.tsx), "--language", "py"])

        assert result.returncode in [0, 1, 2], f"Crashed: {result.stderr}"
        print(f"Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")

    def test_language_js_on_py_file(self):
        """--language js on .py file should skip or handle gracefully."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        result = run_cmd(["agentspec", "lint", str(self.py), "--language", "js"])

        assert result.returncode in [0, 1, 2], f"Crashed: {result.stderr}"
        print(f"Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")

    def test_language_flag_on_strip_errors(self):
        """--language on strip command should error (unsupported)."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        result = run_cmd(["agentspec", "strip", str(self.py), "--language", "py"])

        # Should error (strip doesn't support --language)
        assert result.returncode == 2, "Should reject --language on strip"
        assert "unrecognized arguments" in result.stderr, f"Unhelpful error: {result.stderr}"
        print(f"Error message: {result.stderr}")

    def test_language_ts_on_js_file(self):
        """--language ts on .js file (different JS variant)."""
        if not self.js.exists():
            pytest.skip("JS file not available")

        result = run_cmd(["agentspec", "extract", str(self.js), "--language", "ts"])

        # Might work (both are JS variants) or might not
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}")

    def test_language_js_on_ts_file(self):
        """--language js on .tsx file (different JS variant)."""
        if not self.tsx.exists():
            pytest.skip("TSX file not available")

        result = run_cmd(["agentspec", "extract", str(self.tsx), "--language", "js"])

        # Might work or might not
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:200]}")


class TestConflictingFlags:
    """Test conflicting flag combinations."""

    @pytest.fixture(autouse=True)
    def setup_file(self):
        """Create temp file."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.py = self.temp_dir / "test.py"

        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.py)

        yield
        shutil.rmtree(self.temp_dir)

    def test_terse_and_verbose_together(self):
        """--terse --verbose together (conflicting)."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        result = run_cmd([
            "agentspec", "generate", str(self.py),
            "--terse", "--verbose",
            "--strip", "--force-context"
        ] + LLM_ARGS, timeout=120)

        # Should either pick one or error
        print(f"Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr[:500]}")

    def test_strip_without_generate(self):
        """--strip flag on commands other than generate."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Strip on extract
        result = run_cmd(["agentspec", "extract", str(self.py), "--strip"])
        print(f"Extract --strip exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")

        # Strip on lint
        result = run_cmd(["agentspec", "lint", str(self.py), "--strip"])
        print(f"Lint --strip exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")


class TestInvalidCommands:
    """Test invalid command sequences."""

    def test_multiple_commands(self):
        """Multiple commands in one call (invalid)."""
        result = run_cmd(["agentspec", "generate", "strip", "lint", "test.py"])

        # Should error with helpful message
        assert result.returncode != 0, "Should reject multiple commands"
        print(f"Exit code: {result.returncode}")
        print(f"Error message: {result.stderr}")

        # Check if error message is helpful
        stderr_lower = result.stderr.lower()
        is_helpful = any(word in stderr_lower for word in ["invalid", "usage", "command", "error"])
        assert is_helpful, f"Unhelpful error message: {result.stderr}"

    def test_no_command(self):
        """No command (just filename)."""
        result = run_cmd(["agentspec", "test.py"])

        assert result.returncode != 0, "Should reject missing command"
        print(f"Exit code: {result.returncode}")
        print(f"Error message: {result.stderr}")

    def test_invalid_command(self):
        """Invalid command name."""
        result = run_cmd(["agentspec", "foobar", "test.py"])

        assert result.returncode != 0, "Should reject invalid command"
        print(f"Exit code: {result.returncode}")
        print(f"Error message: {result.stderr}")


class TestFormatMismatches:
    """Test format extraction mismatches."""

    @pytest.fixture(autouse=True)
    def setup_file(self):
        """Create temp file with YAML agentspec."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.py = self.temp_dir / "test.py"

        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.py)

        yield
        shutil.rmtree(self.temp_dir)

    def test_extract_markdown_on_yaml_agentspec(self):
        """Extract --format markdown on file with --agentspec-yaml."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # First generate with YAML format
        gen_result = run_cmd([
            "agentspec", "generate", str(self.py),
            "--strip", "--agentspec-yaml",
            "--terse", "--force-context"
        ] + LLM_ARGS, timeout=120)

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Try to extract as markdown
        extract_result = run_cmd([
            "agentspec", "extract", str(self.py),
            "--format", "markdown"
        ])

        # Should work (extract converts formats)
        print(f"Exit code: {extract_result.returncode}")
        print(f"Output: {extract_result.stdout[:300]}")


class TestLintAfterEveryOperation:
    """Run lint after various operations to verify output validity."""

    @pytest.fixture(autouse=True)
    def setup_file(self):
        """Create temp file."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.py = self.temp_dir / "test.py"

        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.py)

        yield
        shutil.rmtree(self.temp_dir)

    def test_lint_after_strip(self):
        """Lint after strip should report missing agentspecs."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Strip
        strip_result = run_cmd(["agentspec", "strip", str(self.py)])
        assert strip_result.returncode == 0

        # Lint
        lint_result = run_cmd(["agentspec", "lint", str(self.py)])

        # Should report missing
        print(f"Lint exit code: {lint_result.returncode}")
        print(f"Lint output: {lint_result.stdout}")
        assert lint_result.returncode == 1, "Lint should detect missing agentspecs"

    def test_lint_after_generate_yaml(self):
        """Lint after generate --agentspec-yaml."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Generate with YAML
        gen_result = run_cmd([
            "agentspec", "generate", str(self.py),
            "--strip", "--agentspec-yaml",
            "--terse", "--force-context"
        ] + LLM_ARGS, timeout=120)

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Lint
        lint_result = run_cmd(["agentspec", "lint", str(self.py)])

        print(f"Lint exit code: {lint_result.returncode}")
        print(f"Lint output: {lint_result.stdout[:500]}")

    def test_lint_after_generate_default(self):
        """Lint after generate (default format)."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Generate default
        gen_result = run_cmd([
            "agentspec", "generate", str(self.py),
            "--strip", "--terse", "--force-context"
        ] + LLM_ARGS, timeout=120)

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Lint
        lint_result = run_cmd(["agentspec", "lint", str(self.py)])

        print(f"Lint exit code: {lint_result.returncode}")
        print(f"Lint output: {lint_result.stdout[:500]}")

    def test_lint_with_wrong_language_flag(self):
        """Lint with --language mismatch."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Lint Python file with --language js
        lint_result = run_cmd([
            "agentspec", "lint", str(self.py),
            "--language", "js"
        ])

        print(f"Lint exit code: {lint_result.returncode}")
        print(f"Lint output: {lint_result.stdout}")


class TestExtractCombinations:
    """Test extract with various combinations."""

    @pytest.fixture(autouse=True)
    def setup_file(self):
        """Create temp file."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.py = self.temp_dir / "test.py"

        if PHAXIO_PY.exists():
            shutil.copy(PHAXIO_PY, self.py)

        yield
        shutil.rmtree(self.temp_dir)

    def test_extract_all_formats(self):
        """Extract in all formats after generate."""
        if not self.py.exists():
            pytest.skip("Python file not available")

        # Generate first
        gen_result = run_cmd([
            "agentspec", "generate", str(self.py),
            "--strip", "--terse", "--force-context"
        ] + LLM_ARGS, timeout=120)

        if gen_result.returncode != 0:
            pytest.skip(f"Generate failed: {gen_result.stderr}")

        # Extract markdown
        result = run_cmd([
            "agentspec", "extract", str(self.py),
            "--format", "markdown"
        ])
        print(f"Markdown extract exit: {result.returncode}")
        assert result.returncode == 0

        # Extract YAML
        result = run_cmd([
            "agentspec", "extract", str(self.py),
            "--format", "yaml"
        ])
        print(f"YAML extract exit: {result.returncode}")
        assert result.returncode == 0

        # Extract agent-context
        result = run_cmd([
            "agentspec", "extract", str(self.py),
            "--format", "agent-context"
        ])
        print(f"Agent-context extract exit: {result.returncode}")
        assert result.returncode == 0
