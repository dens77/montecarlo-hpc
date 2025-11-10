#!/usr/bin/env bash
#
# Day 1 Verification Script
# Checks that all Day 1 deliverables are in place
#

set -euo pipefail

echo "=========================================="
echo "Day 1 Deliverable Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

echo "Checking directory structure..."
check_dir "src"
check_dir "env"
check_dir "slurm"
check_dir "data"
check_dir "results"
check_dir "results/logs"
check_dir "docs"
check_dir "tests"

echo ""
echo "Checking source files..."
check_file "src/option_pricing.py"
check_file "src/monte_carlo.py"

echo ""
echo "Checking test files..."
check_file "tests/test_black_scholes.py"

echo ""
echo "Checking data files..."
check_file "data/sample_params.csv"
check_file "data/README.md"

echo ""
echo "Checking documentation..."
check_file "README.md"
check_file "DAY1_VALIDATION.md"
check_file "run.sh"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "All Day 1 deliverables are present!"
echo ""
echo "Next steps:"
echo "1. Test Black-Scholes: python3 src/option_pricing.py"
echo "2. Test Monte Carlo:   python3 src/monte_carlo.py --n-samples 100000 --validate"
echo "3. Run test suite:     python3 tests/test_black_scholes.py"
echo "4. Or use:             ./run.sh test"
echo ""
echo "Ready for Day 2: MPI Parallelization"
echo "=========================================="

