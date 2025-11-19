#!/usr/bin/env bash
#
# Complete Test Suite Runner
# Runs all Phase 1-2 tests in sequence
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FAILED_TESTS=()
PASSED_TESTS=()

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: $test_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if eval "$test_cmd"; then
        echo ""
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        PASSED_TESTS+=("$test_name")
        return 0
    else
        echo ""
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        FAILED_TESTS+=("$test_name")
        return 1
    fi
}

echo "══════════════════════════════════════════════════════════════════════"
echo "Monte Carlo HPC - Complete Test Suite"
echo "══════════════════════════════════════════════════════════════════════"
echo ""
echo "Testing all Phase 1-2 functionality (Days 1-7)"
echo "This will take ~2-3 minutes to complete"
echo ""

# Check if venv is activated
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Activating venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Error: venv not found. Run ./setup_venv.sh first${NC}"
        exit 1
    fi
fi

echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Test 1: Black-Scholes Formula
run_test "Test 1: Black-Scholes Formula" \
    "python src/option_pricing.py"

# Test 2: Serial Monte Carlo
run_test "Test 2: Serial Monte Carlo (100K samples)" \
    "python src/monte_carlo.py --n-samples 100000 --validate"

# Test 3: Variance Reduction Module
run_test "Test 3: Variance Reduction Module" \
    "python src/variance_reduction.py"

# Test 4: Serial with Antithetic Variates
run_test "Test 4: Serial MC with Antithetic Variates" \
    "python src/monte_carlo.py --n-samples 100000 --antithetic --validate"

# Test 5: Unit Tests
run_test "Test 5: Unit Test Suite" \
    "python tests/test_black_scholes.py"

# Test 6: MPI (check if available first)
if command -v mpirun &> /dev/null; then
    run_test "Test 6: MPI Monte Carlo (4 ranks)" \
        "mpirun -n 4 python src/mpi_monte_carlo.py --n-samples 100000 --validate" || true
    
    run_test "Test 7: MPI with Antithetic Variates" \
        "mpirun -n 4 python src/mpi_monte_carlo.py --n-samples 100000 --antithetic --validate" || true
    
    run_test "Test 8: MPI vs Serial Comparison" \
        "python tests/test_mpi_serial_comparison.py" || true
else
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Skipping MPI tests: mpirun not found${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "MPI tests will work on the cluster (OpenMPI pre-installed)"
    echo ""
    echo "To test MPI locally, install OpenMPI:"
    echo "  macOS:  brew install open-mpi"
    echo "  Ubuntu: sudo apt-get install openmpi-bin"
    echo ""
fi

# Summary
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "══════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed: ${#PASSED_TESTS[@]}${NC}"
for test in "${PASSED_TESTS[@]}"; do
    echo -e "  ${GREEN}✅${NC} $test"
done

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed: ${#FAILED_TESTS[@]}${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}❌${NC} $test"
    done
    echo ""
    echo -e "${RED}Some tests failed. Check output above for details.${NC}"
    echo ""
    exit 1
else
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "✅ Your code is working correctly"
    echo "✅ Ready for cluster deployment"
    echo ""
    echo "Next steps:"
    echo "  1. Commit code: git add -A && git commit -m 'Phase 2 complete'"
    echo "  2. Push to GitHub: git push"
    echo "  3. Follow QUICK_START_CLUSTER.md to deploy"
    echo ""
    exit 0
fi

