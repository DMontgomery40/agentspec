#!/usr/bin/env python3
"""
Python Version Checker for agentspec

Verifies that the Python version meets the minimum requirements.
Can be used as a standalone script or imported for runtime validation.

Usage:
    python scripts/check_python_version.py
    
Or in code:
    from scripts.check_python_version import check_version_or_exit
    check_version_or_exit()
"""

import sys

# Minimum required version
REQUIRED_MAJOR = 3
REQUIRED_MINOR = 10

# Recommended version for best experience
RECOMMENDED_MAJOR = 3
RECOMMENDED_MINOR = 11


def get_python_version():
    """Get the current Python version as a tuple."""
    return sys.version_info[:2]


def format_version(major, minor):
    """Format version tuple as string."""
    return f"{major}.{minor}"


def check_version(show_warnings=True):
    """
    Check if the current Python version meets requirements.
    
    Returns:
        tuple: (is_valid, message)
            - is_valid (bool): True if version meets minimum requirements
            - message (str): Human-readable status message
    """
    current_major, current_minor = get_python_version()
    current_version = format_version(current_major, current_minor)
    required_version = format_version(REQUIRED_MAJOR, REQUIRED_MINOR)
    recommended_version = format_version(RECOMMENDED_MAJOR, RECOMMENDED_MINOR)
    
    # Check if version is too old
    if (current_major < REQUIRED_MAJOR or 
        (current_major == REQUIRED_MAJOR and current_minor < REQUIRED_MINOR)):
        
        message = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     ❌ PYTHON VERSION TOO OLD                            ║
╚══════════════════════════════════════════════════════════════════════════╝

Current Python version: {current_version}
Required minimum: {required_version}+

agentspec requires Python {required_version} or later because it uses modern
Python syntax features:
  • PEP 604 union types (str | None)
  • PEP 585 generic types (list[...])

┌──────────────────────────────────────────────────────────────────────────┐
│ How to upgrade:                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ macOS (using Homebrew):                                                  │
│   brew install python@{RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} │
│                                                                           │
│ Ubuntu/Debian:                                                           │
│   sudo apt update                                                        │
│   sudo apt install python{RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} python{RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR}-venv │
│                                                                           │
│ Using pyenv (recommended for managing multiple Python versions):        │
│   pyenv install {RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} │
│   pyenv local {RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} │
│                                                                           │
│ Create a new virtual environment with Python {recommended_version}: │
│   python{RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} -m venv .venv │
│   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate    │
│   pip install agentspec                                                  │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

For more information, see:
  https://github.com/DMontgomery40/agentspec/blob/main/COMPATIBILITY.md
"""
        return False, message
    
    # Check if version is below recommended
    if show_warnings and (current_major < RECOMMENDED_MAJOR or 
        (current_major == RECOMMENDED_MAJOR and current_minor < RECOMMENDED_MINOR)):
        
        message = f"""
┌──────────────────────────────────────────────────────────────────────────┐
│ ⚠️  Python {current_version} detected                                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ While Python {current_version} is supported, Python {recommended_version}+ is recommended for:    │
│   • Better performance (Python 3.11 is ~25% faster)                      │
│   • Improved error messages                                              │
│   • Latest security updates                                              │
│                                                                           │
│ To upgrade: brew install python@{RECOMMENDED_MAJOR}.{RECOMMENDED_MINOR} (or see COMPATIBILITY.md)    │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
"""
        return True, message
    
    # Version is good!
    message = f"✓ Python {current_version} meets requirements (minimum: {required_version}+)"
    return True, message


def check_version_or_exit(show_warnings=True):
    """
    Check Python version and exit with error code 1 if requirements not met.
    Prints warning if version is below recommended but still supported.
    
    Args:
        show_warnings (bool): Whether to show warnings for sub-optimal versions
    """
    is_valid, message = check_version(show_warnings=show_warnings)
    
    if not is_valid:
        print(message, file=sys.stderr)
        sys.exit(1)
    
    if show_warnings and "⚠️" in message:
        print(message)


def main():
    """Main entry point when run as a script."""
    is_valid, message = check_version(show_warnings=True)
    
    print(message)
    
    if not is_valid:
        sys.exit(1)
    
    # Print detailed version info
    print("\nPython version details:")
    print(f"  Version: {sys.version}")
    print(f"  Executable: {sys.executable}")
    print(f"  Platform: {sys.platform}")


if __name__ == "__main__":
    main()

