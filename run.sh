#!/usr/bin/env bash
#
# Main entry point for Monte Carlo European Option Pricing
#
# Usage:
#   ./run.sh test              # Run validation tests
#   ./run.sh example           # Run example pricing
#   ./run.sh help              # Show help message

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_usage() {
    echo "Monte Carlo European Option Pricing - Main Runner"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  test       - Run validation tests (compare MC vs Black-Scholes)"
    echo "  example    - Run example option pricing"
    echo "  bs         - Test Black-Scholes formula only"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test"
    echo "  $0 example"
}

function run_tests() {
    echo -e "${GREEN}Running validation tests...${NC}"
    python3 tests/test_black_scholes.py
}

function run_example() {
    echo -e "${GREEN}Running example option pricing...${NC}"
    echo ""
    
    # Example 1: ATM option with validation
    echo "Example 1: At-The-Money Call Option"
    python3 src/monte_carlo.py \
        --n-samples 100000 \
        --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
        --validate
    
    echo ""
    echo "Example 2: In-The-Money Call Option"
    python3 src/monte_carlo.py \
        --n-samples 100000 \
        --S0 110 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
        --validate
}

function test_black_scholes() {
    echo -e "${GREEN}Testing Black-Scholes formula...${NC}"
    python3 src/option_pricing.py
}

# Main command dispatcher
case "${1:-help}" in
    test)
        run_tests
        ;;
    example)
        run_example
        ;;
    bs)
        test_black_scholes
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac

