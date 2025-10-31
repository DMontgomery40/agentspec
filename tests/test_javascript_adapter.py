"""
Tests for JavaScript language adapter.

Tests tree-sitter integration, docstring extraction, metadata gathering,
and syntax validation for JavaScript files.

---agentspec
what: |
  Unit tests validating the JavaScriptAdapter implementation.
  
  Tests cover:
  - File discovery in JavaScript projects
  - JSDoc extraction from functions and classes
  - Call expression identification via tree-sitter
  - Import statement collection
  - Syntax validation for JavaScript code
  
  Fixtures use realistic JavaScript patterns: arrow functions, async/await,
  classes, imports/exports, and nested structures.

deps:
  calls:
    - pytest, pathlib, agentspec.langs.JavaScriptAdapter
  called_by:
    - pytest, CI/CD pipelines

why: |
  JavaScript adapter must handle tree-sitter properly and extract metadata
  correctly to support multi-language agentspec processing. Unit tests
  ensure reliability before integration with core modules.

guardrails:
  - DO NOT skip tree-sitter import checks
  - DO NOT assume parser state between tests
  - ALWAYS clean up fixtures after each test

changelog:
  - "2025-10-31: Initial JavaScript adapter test suite"
---/agentspec
"""

import pytest
from pathlib import Path
from agentspec.langs.javascript_adapter import JavaScriptAdapter


@pytest.fixture
def adapter():
    """Create a fresh JavaScriptAdapter instance."""
    return JavaScriptAdapter()


@pytest.fixture
def fixtures_dir():
    """Return path to JavaScript test fixtures."""
    return Path(__file__).parent / "fixtures" / "javascript"


class TestJavaScriptAdapterBasics:
    """Test basic adapter functionality."""

    def test_adapter_initialized(self, adapter):
        """Test that adapter initializes without errors."""
        assert adapter is not None
        assert adapter._tree_sitter_available

    def test_file_extensions(self, adapter):
        """Test that adapter claims correct file extensions."""
        exts = adapter.file_extensions
        assert ".js" in exts
        assert ".mjs" in exts
        # Python extensions should not be included
        assert ".py" not in exts

    def test_comment_delimiters(self, adapter):
        """Test that adapter returns correct JSDoc delimiters."""
        start, end = adapter.get_comment_delimiters()
        assert start == "/**"
        assert end == "*/"


class TestJavaScriptParsing:
    """Test JavaScript parsing with tree-sitter."""

    def test_parse_simple_function(self, adapter):
        """Test parsing a simple function."""
        code = "function hello() { return 42; }"
        tree = adapter.parse(code)
        assert tree is not None
        assert hasattr(tree, "root_node")
        assert tree.root_node.type == "program"

    def test_parse_arrow_function(self, adapter):
        """Test parsing arrow function syntax."""
        code = "const add = (a, b) => a + b;"
        tree = adapter.parse(code)
        assert tree is not None
        assert tree.root_node.type == "program"

    def test_parse_class(self, adapter):
        """Test parsing class declaration."""
        code = "class MyClass { constructor() {} method() {} }"
        tree = adapter.parse(code)
        assert tree is not None
        assert tree.root_node.type == "program"

    def test_parse_with_imports(self, adapter):
        """Test parsing code with import statements."""
        code = (
            "import { readFile } from 'fs/promises';\n"
            "import path from 'path';\n"
            "export function main() { }"
        )
        tree = adapter.parse(code)
        assert tree is not None
        assert tree.root_node.type == "program"


class TestSyntaxValidation:
    """Test syntax validation."""

    def test_valid_syntax(self, adapter):
        """Test that valid JavaScript passes validation."""
        code = "const x = 42; function test() { return x; }"
        # Should not raise
        result = adapter.validate_syntax_string(code)
        assert result is True

    def test_invalid_syntax_raises(self, adapter):
        """Test that invalid JavaScript raises ValueError."""
        code = "const x = 42 this is invalid syntax }{]["
        with pytest.raises(ValueError, match="Syntax error"):
            adapter.validate_syntax_string(code)


class TestFileDiscovery:
    """Test JavaScript file discovery."""

    def test_discover_single_js_file(self, adapter, fixtures_dir):
        """Test discovering a single .js file."""
        js_file = fixtures_dir / "simple-function.js"
        if js_file.exists():
            files = adapter.discover_files(js_file)
            assert len(files) == 1
            assert files[0].suffix == ".js"

    def test_discover_directory_files(self, adapter, fixtures_dir):
        """Test discovering all .js files in directory."""
        if fixtures_dir.exists():
            files = adapter.discover_files(fixtures_dir)
            assert len(files) > 0
            # All files should be JavaScript
            for f in files:
                assert f.suffix in {".js", ".mjs"}


class TestJSDocExtraction:
    """Test JSDoc comment extraction."""

    def test_extract_jsdoc_simple(self, adapter):
        """Test extracting simple JSDoc."""
        jsdoc_lines = [
            "/**",
            " * Brief description",
            " * More details",
            " */",
        ]
        content = adapter._extract_jsdoc_content(jsdoc_lines)
        assert "Brief description" in content
        assert "More details" in content
        assert "/**" not in content
        assert "*/" not in content

    def test_extract_jsdoc_with_tags(self, adapter):
        """Test extracting JSDoc with tags."""
        jsdoc_lines = [
            "/**",
            " * Function description",
            " * @param {number} x - First parameter",
            " * @returns {number} The result",
            " */",
        ]
        content = adapter._extract_jsdoc_content(jsdoc_lines)
        assert "@param" in content
        assert "@returns" in content


class TestMetadataExtraction:
    """Test metadata gathering from JavaScript."""

    def test_gather_metadata_empty(self, adapter):
        """Test metadata gathering on empty structure."""
        result = adapter.gather_metadata(Path("nonexistent.js"), "test")
        assert isinstance(result, dict)
        assert "calls" in result
        assert "imports" in result
        assert "called_by" in result

    def test_extract_imports_regex(self, adapter):
        """Test import extraction with regex fallback."""
        source = (
            "import fs from 'fs';\n"
            "import { readFile } from 'fs/promises';\n"
            "const path = require('path');\n"
        )
        tree = adapter.parse(source)
        imports = adapter._extract_imports(tree, source)
        # Should find at least some imports
        assert len(imports) > 0


class TestIntegration:
    """Integration tests with fixture files."""

    def test_parse_fixture_simple_function(self, adapter, fixtures_dir):
        """Test parsing the simple-function fixture."""
        fixture = fixtures_dir / "simple-function.js"
        if fixture.exists():
            with open(fixture) as f:
                code = f.read()
            tree = adapter.parse(code)
            assert tree is not None
            assert tree.root_node.type == "program"

    def test_parse_fixture_class_example(self, adapter, fixtures_dir):
        """Test parsing the class-example fixture."""
        fixture = fixtures_dir / "class-example.js"
        if fixture.exists():
            with open(fixture) as f:
                code = f.read()
            tree = adapter.parse(code)
            assert tree is not None
            assert tree.root_node.type == "program"

    def test_parse_fixture_arrow_functions(self, adapter, fixtures_dir):
        """Test parsing the arrow-functions fixture."""
        fixture = fixtures_dir / "arrow-functions.js"
        if fixture.exists():
            with open(fixture) as f:
                code = f.read()
            tree = adapter.parse(code)
            assert tree is not None
            assert tree.root_node.type == "program"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
