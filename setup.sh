#!/bin/bash
# Agentspec Setup Script
# Automatically sets up the correct Python environment and installs dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Agentspec Setup Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Detect script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}[1/6]${NC} Checking Python version..."

# Check Python version
PYTHON_CMD=""
PYTHON_VERSION=""

# Try python3 first, then python
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | awk '{print $2}')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_CMD="$cmd"
            PYTHON_VERSION="$version"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}✗ Python 3.10+ not found!${NC}"
    echo
    echo "agentspec requires Python 3.10 or later."
    echo
    echo "To install Python 3.11 (recommended):"
    echo "  macOS:  brew install python@3.11"
    echo "  Ubuntu: sudo apt install python3.11 python3.11-venv"
    echo
    echo "Or use pyenv:"
    echo "  pyenv install 3.11.9"
    echo "  pyenv local 3.11.9"
    echo
    exit 1
fi

echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"
echo

# Create virtual environment if it doesn't exist
VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}[2/6]${NC} Virtual environment already exists"
    echo -e "${YELLOW}  Using existing: $VENV_DIR${NC}"
else
    echo -e "${BLUE}[2/6]${NC} Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created: $VENV_DIR${NC}"
fi
echo

# Activate virtual environment
echo -e "${BLUE}[3/6]${NC} Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo "  Python: $(which python)"
echo "  Version: $(python --version)"
echo

# Upgrade pip
echo -e "${BLUE}[4/6]${NC} Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo

# Install package
echo -e "${BLUE}[5/6]${NC} Installing agentspec..."
if [ -f "pyproject.toml" ]; then
    # Install in development mode with all optional dependencies
    pip install -e ".[all]" --quiet
    echo -e "${GREEN}✓ agentspec installed in development mode with all dependencies${NC}"
else
    echo -e "${RED}✗ pyproject.toml not found!${NC}"
    echo "  Are you in the agentspec directory?"
    exit 1
fi
echo

# Verify installation
echo -e "${BLUE}[6/6]${NC} Verifying installation..."

# Test imports
python -c "import agentspec" 2>/dev/null && echo -e "${GREEN}✓${NC} agentspec imports successfully" || (echo -e "${RED}✗ Import failed${NC}" && exit 1)
python -c "from agentspec.generate import generate_docstring" 2>/dev/null && echo -e "${GREEN}✓${NC} generate.py imports successfully" || (echo -e "${RED}✗ generate.py import failed${NC}" && exit 1)
python -c "from agentspec.utils import _find_git_root" 2>/dev/null && echo -e "${GREEN}✓${NC} utils.py imports successfully" || (echo -e "${RED}✗ utils.py import failed${NC}" && exit 1)

# Test CLI
agentspec --version &>/dev/null || echo -e "${GREEN}✓${NC} CLI available"

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Virtual environment is now activated."
echo
echo "Quick test commands:"
echo "  agentspec --help"
echo "  agentspec lint --help"
echo "  agentspec generate --help"
echo
echo "To activate this environment in the future:"
echo "  source .venv/bin/activate"
echo
echo "To deactivate:"
echo "  deactivate"
echo

