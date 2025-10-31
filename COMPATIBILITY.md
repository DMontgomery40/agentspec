# Python Version Compatibility Guide

**agentspec requires Python 3.10 or later.**

## Quick Reference

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.9 and earlier | ❌ **Not Supported** | Code uses PEP 604 syntax (requires 3.10+) |
| 3.10.x | ✅ **Supported** | Minimum required version |
| 3.11.x | ✅ **Recommended** | ~25% faster, better error messages |
| 3.12.x | ✅ **Supported** | Latest stable, excellent performance |
| 3.13+ | ⚠️ **Untested** | Should work but not yet tested in CI |

## Why Python 3.10+?

agentspec uses **modern Python syntax** that requires Python 3.10 or later:

### PEP 604: Union Types (Python 3.10+)

```python
# Modern syntax (requires Python 3.10+)
def example(param: str | None) -> Path | None:
    ...

# Old syntax (Python 3.9 and earlier)
from typing import Optional
def example(param: Optional[str]) -> Optional[Path]:
    ...
```

**Locations in codebase:**
- `agentspec/generate.py`: 6 occurrences
- `agentspec/utils.py`: 3 occurrences

### PEP 585: Generic Types (Python 3.9+)

```python
# Modern syntax (requires Python 3.9+)
def example() -> list[tuple[int, str, str]]:
    ...

# Old syntax (Python 3.8 and earlier)
from typing import List, Tuple
def example() -> List[Tuple[int, str, str]]:
    ...
```

**Locations in codebase:**
- `agentspec/generate.py`: 1 occurrence

## Installation by Python Version

### If You Have Python 3.10+ Already

```bash
# Check your version
python --version

# If 3.10+, install directly
pip install agentspec
```

### If You Have Python 3.9 or Earlier

You need to upgrade Python. Choose one of these methods:

#### Option 1: System Python (Recommended for Beginners)

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3.11 --version

# Create venv and install
python3.11 -m venv .venv
source .venv/bin/activate
pip install agentspec
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify
python3.11 --version

# Create venv and install
python3.11 -m venv .venv
source .venv/bin/activate
pip install agentspec
```

**Windows:**
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run the installer (check "Add Python to PATH")
3. Open Command Prompt:
```cmd
python --version
python -m venv .venv
.venv\Scripts\activate
pip install agentspec
```

#### Option 2: pyenv (Recommended for Developers)

pyenv allows you to manage multiple Python versions side-by-side.

**Install pyenv:**

```bash
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash
```

**Add to your shell profile** (`~/.zshrc`, `~/.bashrc`, etc.):
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

**Install and use Python 3.11:**
```bash
# Install Python 3.11
pyenv install 3.11.9

# Set as local version for this project
cd /path/to/agentspec
pyenv local 3.11.9

# Verify
python --version  # Should show 3.11.9

# Create venv and install
python -m venv .venv
source .venv/bin/activate
pip install agentspec
```

#### Option 3: conda/miniconda

```bash
# Create environment with Python 3.11
conda create -n agentspec python=3.11

# Activate
conda activate agentspec

# Install
pip install agentspec
```

## Known Issues

### Rich Text Formatting (cli.py)

**Status:** Being investigated  
**Affected versions:** Potentially all versions  
**Symptoms:** Rich terminal formatting may not display correctly in some terminals

**Workaround:**
- Try a different terminal emulator (iTerm2, Alacritty, etc.)
- Check that `TERM` environment variable is set correctly
- Update `rich` library: `pip install --upgrade rich`

**Testing:** Run `agentspec --help` to verify Rich formatting works in your terminal.

### generate.py Functionality

**Status:** Being investigated  
**Affected versions:** Potentially all versions  
**Symptoms:** Some basic functions in generate.py may have issues

**Workaround:**
- Ensure Python 3.10+ is being used (check with `python --version`)
- Verify all dependencies are installed: `pip install -e ".[all]"`
- Check for import errors: `python -c "from agentspec.generate import generate_docstring"`

**Testing:** See `TEST_INSTRUCTIONS.md` for comprehensive test procedures.

## Testing Your Installation

### Basic Import Test

```bash
python -c "import agentspec; print('✓ agentspec imports successfully')"
python -c "from agentspec.generate import generate_docstring; print('✓ generate.py works')"
python -c "from agentspec.utils import _find_git_root; print('✓ utils.py works')"
```

### CLI Test

```bash
agentspec --help
agentspec lint --help
agentspec extract --help
agentspec generate --help
```

### Full Test Suite

```bash
# Install pytest
pip install pytest

# Run tests
pytest tests/ -v
```

### Multi-Version Testing

If you have `tox` and multiple Python versions installed:

```bash
pip install tox
tox  # Tests Python 3.9 (expected to fail), 3.10, 3.11, 3.12
```

See `TEST_INSTRUCTIONS.md` for detailed testing procedures.

## Troubleshooting

### "SyntaxError: invalid syntax" on Import

**Problem:** Python version is too old  
**Solution:** Upgrade to Python 3.10+

```bash
# Check your version
python --version

# If < 3.10, follow installation instructions above
```

### "ModuleNotFoundError: No module named 'agentspec'"

**Problem:** agentspec not installed in current environment  
**Solution:** Install agentspec

```bash
# Make sure you're in the right venv
which python

# Install
pip install agentspec
```

### "ImportError: cannot import name 'X' from 'agentspec'"

**Problem:** Outdated installation  
**Solution:** Reinstall

```bash
pip uninstall agentspec
pip install agentspec
```

### Rich Formatting Not Working

**Problem:** Terminal doesn't support rich formatting  
**Solution:** Try these steps

1. Update rich library:
   ```bash
   pip install --upgrade rich rich-argparse
   ```

2. Check terminal compatibility:
   ```bash
   python -c "from rich.console import Console; c = Console(); c.print('[bold green]Test[/bold green]')"
   ```

3. Try a different terminal (iTerm2, Alacritty, Windows Terminal)

### Version Check Failed on Startup

**Problem:** Python version check is too strict  
**Solution:** This is intentional - upgrade Python

If you believe you have the correct version:
```bash
# Verify Python version
python --version

# Check if it's actually being used
which python

# Make sure venv is activated
source .venv/bin/activate
```

## Dependency Requirements

| Dependency | Version | Min Python |
|-----------|---------|------------|
| pyyaml | ≥6.0.3 | 3.6+ |
| rich | ≥13.7.0 | 3.7+ |
| rich-argparse | ≥1.4.0 | 3.7+ |
| anthropic | (optional) | 3.7+ |
| openai | (optional) | 3.7.1+ |

**All dependencies support Python 3.7+**, so they're not the limiting factor. The codebase syntax requires Python 3.10+.

## CI/CD Integration

agentspec's CI tests against multiple Python versions. Your CI should do the same:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install agentspec
      - run: agentspec lint src/ --strict
```

## Migration from Python 3.9

If you were using Python 3.9 (even though it never actually worked with agentspec):

1. **Upgrade Python** to 3.10, 3.11, or 3.12
2. **Recreate virtual environment** with new Python version
3. **Reinstall dependencies** in new environment
4. **Test thoroughly** with your codebase

Example migration:

```bash
# Remove old venv
rm -rf .venv

# Create new venv with Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate

# Reinstall everything
pip install --upgrade pip
pip install agentspec

# Verify
python --version  # Should be 3.10+
agentspec --version
```

## Performance Notes

### Python 3.11 vs 3.10

Python 3.11 is approximately **10-25% faster** than Python 3.10 for agentspec workflows:

- Faster startup time
- Faster parsing (AST operations)
- Faster string operations
- Better error messages with exact locations

**Recommendation:** Use Python 3.11+ for production.

### Python 3.12

Python 3.12 offers additional performance improvements but is newer. agentspec is tested and works with 3.12, but enterprise users may prefer 3.11 for stability.

## Future Plans

- **Python 3.13:** Will add support when stable (expected early 2025)
- **Python 3.9 EOL:** October 2025 - no plans to support
- **Python 3.10 EOL:** October 2026 - will maintain support until then

## Getting Help

If you're having Python version issues:

1. Check this compatibility guide first
2. Verify your Python version: `python --version`
3. Try the troubleshooting steps above
4. See `TEST_INSTRUCTIONS.md` for testing procedures
5. File an issue: https://github.com/DMontgomery40/agentspec/issues

Include in your issue:
- Python version (`python --version`)
- Operating system
- Installation method (pip, from source, etc.)
- Full error message

## See Also

- `PYTHON_VERSION_ANALYSIS.md` - Technical analysis of version requirements
- `PYTHON_VERSION_DECISION.md` - Why we chose Python 3.10+ minimum
- `TEST_INSTRUCTIONS.md` - Detailed testing procedures
- `tox.ini` - Automated multi-version testing configuration

