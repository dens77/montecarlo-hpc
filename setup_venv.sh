#!/usr/bin/env bash
#
# Quick setup script for local development environment
# Creates virtual environment and installs dependencies
#

set -euo pipefail

echo "=========================================="
echo "Monte Carlo HPC - Environment Setup"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old venv..."
        rm -rf venv
    else
        echo "Keeping existing venv."
        echo "To activate: source venv/bin/activate"
        exit 0
    fi
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies from env/requirements.txt..."
pip install -r env/requirements.txt

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Installed packages:"
pip list | grep -E "numpy|scipy|mpi4py|pandas|matplotlib|pytest"

echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Test installation:    python src/option_pricing.py"
echo "  3. Run tests:            python tests/test_black_scholes.py"
echo "  4. Or use:               ./run.sh test"
echo ""
echo "Note: If mpi4py fails, install OpenMPI first:"
echo "  macOS:  brew install open-mpi"
echo "  Ubuntu: sudo apt-get install libopenmpi-dev"
echo ""
echo "To deactivate: deactivate"
echo "=========================================="

