# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-31

### 🎉 Major Features

#### Multi-Language Support via Tree-Sitter
- **Language Adapter Architecture**: Introduced pluggable `LanguageAdapter` protocol and `LanguageRegistry` enabling support for new languages without modifying core modules
- **JavaScript/JSX Support**: Full tree-sitter based parser for `.js` and `.mjs` files
  - JSDoc comment extraction and insertion with proper formatting
  - Function call and import statement analysis via tree-sitter queries
  - Syntax validation using error node detection
  - Comprehensive metadata gathering (calls, imports, called_by)
- **Python 3.10+ Support**: Extracted Python-specific AST logic into `PythonAdapter` preserving all existing functionality

### ✨ Enhancements

#### CLI Updates
- Added `--language {py,js,auto}` flag to `lint`, `extract`, and `generate` commands
- Auto-detection based on file extensions (default behavior)
- Updated help text to advertise JavaScript support

#### Documentation
- New `docs/javascript-style-guide.md` with comprehensive examples for JavaScript agentspec blocks
- Updated README with JavaScript support announcement
- Example agentspec blocks for arrow functions, classes, async functions, and higher-order functions

#### Testing
- 18 new tests for JavaScript adapter covering:
  - File discovery
  - JSDoc extraction
  - Tree-sitter parsing (functions, classes, imports)
  - Syntax validation
  - Metadata extraction
- 4 JavaScript fixture files demonstrating real-world patterns
- All tests passing (20 total: 2 existing Python tests + 18 new JavaScript tests)

### 📦 Dependencies

#### Added
- `tree-sitter==0.20.1` - Fast incremental parser runtime
- `tree-sitter-languages==1.10.2` - Precompiled language grammars (JavaScript, Python, etc.)

#### Updated
- `pyproject.toml`: Added `javascript` optional dependency group
- `requirements.txt`: Added tree-sitter packages

### 🔄 Migration Guide for Existing Projects

**Existing Python projects** continue to work without any changes. The default `--language auto` automatically detects Python files.

**To add JavaScript support:**
```bash
# Install optional dependencies
pip install agentspec[javascript]

# Lint mixed Python/JavaScript project
agentspec lint src/ --language auto

# Extract from JavaScript files
agentspec extract src/ --language js --format markdown

# Generate docstrings for JavaScript
agentspec generate src/my-module.js --model claude-haiku-4-5
```

### 🏗️ Architecture Changes

#### Language Adapter Protocol
New `agentspec/langs/` module provides:
- `LanguageAdapter`: Protocol defining interface for language-specific adapters
- `LanguageRegistry`: Global registry for discovering adapters by file extension
- `PythonAdapter`: Wraps existing Python AST analysis
- `JavaScriptAdapter`: Tree-sitter based parsing for JavaScript

#### Core Module Compatibility
All existing functions in `collect.py`, `extract.py`, `lint.py`, `generate.py`, and `insert_metadata.py` remain unchanged and continue to work with Python files. Future refactoring will make these modules language-agnostic via adapter lookups.

### 🐛 Bug Fixes

- Fixed YAML indentation in agentspec blocks (previous build artifacts)
- Improved docstring extraction robustness
- Resolved tree-sitter version mismatch causing silent JavaScript adapter failures and added logging guidance when optional dependencies are missing

### ⚠️ Known Limitations

- JavaScript adapter focuses on `.js` and `.mjs` files; `.jsx`, `.ts`, `.tsx` support deferred to v0.2.1
- Decorators and other advanced ECMAScript features deferred pending test coverage
- Cross-file analysis (called_by) not implemented; marked as `[]` in metadata

### 🙏 Acknowledgments

Tree-sitter implementation based on [official tree-sitter documentation](https://tree-sitter.github.io/tree-sitter/) and the maintained [py-tree-sitter-languages](https://github.com/grantjenks/py-tree-sitter-languages) project.

---

## [0.1.0] - 2025-10-20

### Initial Release

- Core agentspec YAML format for Python
- `lint` command for validating agentspec compliance
- `extract` command for exporting specs to Markdown/JSON
- `generate` command for auto-generating docstrings via Claude
- Python 3.10+ support
- Rich CLI formatting and error messages
