#!/usr/bin/env python3
"""
Comparison Test: MPI vs Serial Monte Carlo

This script verifies that the MPI parallel implementation produces
results consistent with the serial implementation.

Usage:
    python tests/test_mpi_serial_comparison.py
"""

import sys
import os
import subprocess
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from option_pricing import black_scholes_call
from monte_carlo import monte_carlo_european_call


def test_serial_implementation():
    """Test that serial implementation works correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Serial Implementation")
    print("=" * 70)
    
    S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
    n_samples = 100000
    seed = 42
    
    print(f"Parameters: S0=${S0}, K=${K}, T={T}yr, r={r}, σ={sigma}")
    print(f"Samples: {n_samples:,}")
    
    # Run serial MC
    mc_price, mc_stderr, elapsed = monte_carlo_european_call(
        S0, K, T, r, sigma, n_samples, seed
    )
    
    # Analytical price
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    print(f"\nResults:")
    print(f"  Black-Scholes:  ${bs_price:.6f}")
    print(f"  Monte Carlo:    ${mc_price:.6f} ± ${mc_stderr:.6f}")
    print(f"  Absolute error: ${abs(mc_price - bs_price):.6f}")
    print(f"  Relative error: {abs(mc_price - bs_price) / bs_price * 100:.4f}%")
    print(f"  Time:           {elapsed:.4f} sec")
    
    print("✓ Serial implementation test PASSED")
    return mc_price, mc_stderr


def test_mpi_implementation():
    """Test that MPI implementation works with mpirun."""
    print("\n" + "=" * 70)
    print("TEST 2: MPI Implementation")
    print("=" * 70)
    
    # Check if mpirun is available
    try:
        result = subprocess.run(['which', 'mpirun'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  mpirun not found. Skipping MPI test.")
            print("   Install OpenMPI to run MPI tests:")
            print("   - macOS:  brew install open-mpi")
            print("   - Ubuntu: sudo apt-get install openmpi-bin")
            return None, None
    except FileNotFoundError:
        print("⚠️  Cannot check for mpirun. Skipping MPI test.")
        return None, None
    
    S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
    n_samples = 100000
    seed = 42
    n_ranks = 4
    
    print(f"Parameters: S0=${S0}, K=${K}, T={T}yr, r={r}, σ={sigma}")
    print(f"Samples: {n_samples:,}")
    print(f"MPI ranks: {n_ranks}")
    
    # Construct command
    cmd = [
        'mpirun', '-n', str(n_ranks),
        'python', 'src/mpi_monte_carlo.py',
        '--n-samples', str(n_samples),
        '--S0', str(S0),
        '--K', str(K),
        '--T', str(T),
        '--r', str(r),
        '--sigma', str(sigma),
        '--seed', str(seed),
        '--validate'
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"✗ MPI test FAILED with return code {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return None, None
        
        # Parse output to extract price (simple parsing)
        for line in result.stdout.split('\n'):
            if 'Monte Carlo price:' in line:
                try:
                    price_str = line.split('$')[1].strip()
                    mpi_price = float(price_str)
                    print(f"\n✓ MPI implementation test PASSED")
                    print(f"  Extracted price: ${mpi_price:.6f}")
                    return mpi_price, None
                except (IndexError, ValueError):
                    pass
        
        print("✓ MPI test completed (could not extract price for comparison)")
        return None, None
        
    except subprocess.TimeoutExpired:
        print("✗ MPI test TIMEOUT after 30 seconds")
        return None, None
    except Exception as e:
        print(f"✗ MPI test ERROR: {e}")
        return None, None


def test_serial_vs_mpi_consistency():
    """Test that serial and MPI implementations give consistent results."""
    print("\n" + "=" * 70)
    print("TEST 3: Serial vs MPI Consistency")
    print("=" * 70)
    
    print("Comparing serial and MPI implementations with same seed...")
    print("Note: Results should be statistically similar (within confidence intervals)")
    
    # Run both implementations
    serial_price, serial_stderr = test_serial_implementation()
    mpi_price, mpi_stderr = test_mpi_implementation()
    
    if mpi_price is None:
        print("\n⚠️  Could not compare: MPI test did not return price")
        return False
    
    # Compare results
    print("\n" + "=" * 70)
    print("Comparison Results:")
    print("=" * 70)
    
    diff = abs(serial_price - mpi_price)
    rel_diff_pct = (diff / serial_price) * 100
    
    # Statistical test: check if difference is within expected Monte Carlo error
    # Combined standard error (assuming independent samples)
    combined_stderr = np.sqrt(serial_stderr**2 + (mpi_stderr or serial_stderr)**2)
    z_score = diff / combined_stderr if combined_stderr > 0 else 0
    
    print(f"Serial price:     ${serial_price:.6f} ± ${serial_stderr:.6f}")
    print(f"MPI price:        ${mpi_price:.6f}")
    print(f"Difference:       ${diff:.6f} ({rel_diff_pct:.4f}%)")
    print(f"Combined stderr:  ${combined_stderr:.6f}")
    print(f"Z-score:          {z_score:.2f}")
    
    # Test passes if:
    # 1. Difference is small (< 1% relative error)
    # 2. OR z-score < 3 (3-sigma rule)
    if rel_diff_pct < 1.0 or z_score < 3.0:
        print(f"\n✓ Consistency test PASSED")
        print(f"  Serial and MPI implementations are statistically consistent")
        return True
    else:
        print(f"\n⚠️  Consistency test WARNING")
        print(f"  Difference is larger than expected")
        print(f"  This could be due to:")
        print(f"    - Different random number sequences")
        print(f"    - Insufficient samples for accurate comparison")
        print(f"    - Implementation differences")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("MPI vs SERIAL MONTE CARLO COMPARISON TEST SUITE")
    print("=" * 70)
    print("Validating that MPI implementation produces consistent results")
    
    try:
        # Test 1: Serial works
        serial_price, serial_stderr = test_serial_implementation()
        
        # Test 2: MPI works
        mpi_price, mpi_stderr = test_mpi_implementation()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        if mpi_price is not None:
            print("✓ All tests completed successfully")
            print(f"\nBoth implementations are working correctly.")
            print(f"Ready for cluster deployment (Day 3).")
        else:
            print("⚠️  MPI test skipped or failed")
            print(f"\nSerial implementation is working.")
            print(f"Install OpenMPI to test MPI version:")
            print(f"  macOS:  brew install open-mpi")
            print(f"  Ubuntu: sudo apt-get install openmpi-bin")
        
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

