#!/usr/bin/env python3
"""
Validation Tests for Black-Scholes and Monte Carlo Implementation

This module tests the correctness of our Monte Carlo implementation by comparing
it against the analytical Black-Scholes formula for various option scenarios.

Test cases:
    - ITM (In-The-Money): S0 > K for calls
    - ATM (At-The-Money): S0 = K
    - OTM (Out-of-The-Money): S0 < K for calls
"""

import sys
import os
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from option_pricing import black_scholes_call, validate_option_params
from monte_carlo import monte_carlo_european_call


def test_black_scholes_formula():
    """Test that Black-Scholes formula produces reasonable values."""
    print("\n" + "=" * 70)
    print("TEST 1: Black-Scholes Formula Sanity Check")
    print("=" * 70)
    
    # Test case: ATM call option
    S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
    price = black_scholes_call(S0, K, T, r, sigma)
    
    print(f"ATM Call (S0=K=100): ${price:.4f}")
    
    # Sanity checks
    assert price > 0, "Option price should be positive"
    assert price < S0, "Call price should be less than stock price"
    
    # For ATM option with these parameters, price should be roughly 10-11
    assert 8 < price < 15, f"ATM call price seems unreasonable: ${price:.2f}"
    
    print("✓ Black-Scholes formula sanity check PASSED")
    return True


def test_monte_carlo_vs_black_scholes_atm():
    """Test Monte Carlo vs Black-Scholes for At-The-Money option."""
    print("\n" + "=" * 70)
    print("TEST 2: Monte Carlo vs Black-Scholes (ATM)")
    print("=" * 70)
    
    # ATM parameters: S0 = K
    S0 = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma = 0.20
    n_samples = 1_000_000
    
    print(f"Parameters: S0=${S0}, K=${K}, T={T}yr, r={r}, σ={sigma}")
    print(f"Samples: {n_samples:,}")
    
    # Analytical price
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    # Monte Carlo price
    mc_price, mc_stderr, elapsed = monte_carlo_european_call(
        S0, K, T, r, sigma, n_samples, seed=42
    )
    
    # Calculate error
    abs_error = abs(mc_price - bs_price)
    rel_error_pct = (abs_error / bs_price) * 100
    
    print(f"\nResults:")
    print(f"  Black-Scholes:  ${bs_price:.6f}")
    print(f"  Monte Carlo:    ${mc_price:.6f} ± ${mc_stderr:.6f}")
    print(f"  Absolute error: ${abs_error:.6f}")
    print(f"  Relative error: {rel_error_pct:.4f}%")
    print(f"  Time elapsed:   {elapsed:.4f} sec")
    
    # Check if within 95% confidence interval (1.96 * stderr)
    within_ci = abs_error <= 1.96 * mc_stderr
    print(f"  Within 95% CI:  {within_ci}")
    
    # Assert error is less than 1%
    assert rel_error_pct < 1.0, f"ATM: Relative error {rel_error_pct:.4f}% exceeds 1%"
    print("✓ ATM test PASSED (error < 1%)")
    
    return True


def test_monte_carlo_vs_black_scholes_itm():
    """Test Monte Carlo vs Black-Scholes for In-The-Money option."""
    print("\n" + "=" * 70)
    print("TEST 3: Monte Carlo vs Black-Scholes (ITM)")
    print("=" * 70)
    
    # ITM parameters: S0 > K (call is in the money)
    S0 = 110.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma = 0.20
    n_samples = 1_000_000
    
    print(f"Parameters: S0=${S0}, K=${K}, T={T}yr, r={r}, σ={sigma}")
    print(f"Samples: {n_samples:,}")
    
    # Analytical price
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    # Monte Carlo price
    mc_price, mc_stderr, elapsed = monte_carlo_european_call(
        S0, K, T, r, sigma, n_samples, seed=43
    )
    
    # Calculate error
    abs_error = abs(mc_price - bs_price)
    rel_error_pct = (abs_error / bs_price) * 100
    
    print(f"\nResults:")
    print(f"  Black-Scholes:  ${bs_price:.6f}")
    print(f"  Monte Carlo:    ${mc_price:.6f} ± ${mc_stderr:.6f}")
    print(f"  Absolute error: ${abs_error:.6f}")
    print(f"  Relative error: {rel_error_pct:.4f}%")
    print(f"  Time elapsed:   {elapsed:.4f} sec")
    
    within_ci = abs_error <= 1.96 * mc_stderr
    print(f"  Within 95% CI:  {within_ci}")
    
    # Assert error is less than 1%
    assert rel_error_pct < 1.0, f"ITM: Relative error {rel_error_pct:.4f}% exceeds 1%"
    print("✓ ITM test PASSED (error < 1%)")
    
    return True


def test_monte_carlo_vs_black_scholes_otm():
    """Test Monte Carlo vs Black-Scholes for Out-of-The-Money option."""
    print("\n" + "=" * 70)
    print("TEST 4: Monte Carlo vs Black-Scholes (OTM)")
    print("=" * 70)
    
    # OTM parameters: S0 < K (call is out of the money)
    S0 = 90.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma = 0.20
    n_samples = 1_000_000
    
    print(f"Parameters: S0=${S0}, K=${K}, T={T}yr, r={r}, σ={sigma}")
    print(f"Samples: {n_samples:,}")
    
    # Analytical price
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    # Monte Carlo price
    mc_price, mc_stderr, elapsed = monte_carlo_european_call(
        S0, K, T, r, sigma, n_samples, seed=44
    )
    
    # Calculate error
    abs_error = abs(mc_price - bs_price)
    rel_error_pct = (abs_error / bs_price) * 100
    
    print(f"\nResults:")
    print(f"  Black-Scholes:  ${bs_price:.6f}")
    print(f"  Monte Carlo:    ${mc_price:.6f} ± ${mc_stderr:.6f}")
    print(f"  Absolute error: ${abs_error:.6f}")
    print(f"  Relative error: {rel_error_pct:.4f}%")
    print(f"  Time elapsed:   {elapsed:.4f} sec")
    
    within_ci = abs_error <= 1.96 * mc_stderr
    print(f"  Within 95% CI:  {within_ci}")
    
    # Assert error is less than 1%
    assert rel_error_pct < 1.0, f"OTM: Relative error {rel_error_pct:.4f}% exceeds 1%"
    print("✓ OTM test PASSED (error < 1%)")
    
    return True


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("MONTE CARLO VALIDATION TEST SUITE")
    print("=" * 70)
    print("Testing Monte Carlo implementation against Black-Scholes formula")
    print("Target: Relative error < 1% for N=1,000,000 samples")
    
    tests = [
        test_black_scholes_formula,
        test_monte_carlo_vs_black_scholes_atm,
        test_monte_carlo_vs_black_scholes_itm,
        test_monte_carlo_vs_black_scholes_otm,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests:  {len(tests)}")
    print(f"Passed:       {passed} ✓")
    print(f"Failed:       {failed} ✗")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

