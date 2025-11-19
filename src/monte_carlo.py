#!/usr/bin/env python3
"""
Serial Monte Carlo European Option Pricing

This module implements a serial (single-process) Monte Carlo simulation
for pricing European options under the Black-Scholes model.

Usage:
    python monte_carlo.py --n-samples 1000000 --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2
"""

import argparse
import time
import numpy as np
from typing import Tuple
import sys

# Import option pricing functions
from option_pricing import (
    validate_option_params,
    black_scholes_call,
    simulate_gbm_terminal_price,
    call_payoff
)
from variance_reduction import (
    antithetic_variates_samples,
    antithetic_monte_carlo_prices
)


def monte_carlo_european_call(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    n_samples: int,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Price a European call option using Monte Carlo simulation.
    
    Algorithm:
        1. Generate n_samples random paths for stock price
        2. Calculate payoff for each path: max(S_T - K, 0)
        3. Average the payoffs and discount to present value
        4. Compute standard error for confidence intervals
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)
        n_samples: Number of Monte Carlo samples
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (option_price, standard_error, elapsed_time)
    """
    # Validate inputs
    validate_option_params(S0, K, T, r, sigma)
    assert n_samples > 0, "Number of samples must be positive"
    
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Start timing
    start_time = time.perf_counter()
    
    # Generate random normal samples: Z ~ N(0,1)
    Z = np.random.normal(0.0, 1.0, n_samples)
    
    # Simulate terminal stock prices using GBM
    # S_T = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z
    S_T = S0 * np.exp(drift + diffusion)
    
    # Calculate payoffs: max(S_T - K, 0)
    payoffs = np.maximum(S_T - K, 0.0)
    
    # Compute option price: discounted expected payoff
    discount_factor = np.exp(-r * T)
    option_price = discount_factor * np.mean(payoffs)
    
    # Compute standard error: std(payoffs) / sqrt(n_samples)
    std_payoffs = np.std(payoffs, ddof=1)  # Use sample std (N-1)
    standard_error = discount_factor * std_payoffs / np.sqrt(n_samples)
    
    # End timing
    elapsed_time = time.perf_counter() - start_time
    
    return option_price, standard_error, elapsed_time


def monte_carlo_european_call_antithetic(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    n_samples: int,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Price a European call option using Monte Carlo with antithetic variates.
    
    Antithetic variates variance reduction:
        For each random number Z, also use -Z.
        This creates negatively correlated pairs that reduce variance.
        Achieves ~2x variance reduction for same computational cost.
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)
        n_samples: Total number of Monte Carlo samples (must be even)
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (option_price, standard_error, elapsed_time)
    """
    # Validate inputs
    validate_option_params(S0, K, T, r, sigma)
    assert n_samples > 0, "Number of samples must be positive"
    assert n_samples % 2 == 0, "Number of samples must be even for antithetic variates"
    
    # Set random seed
    np.random.seed(seed)
    
    # Start timing
    start_time = time.perf_counter()
    
    # Generate N/2 antithetic pairs (total N samples)
    n_pairs = n_samples // 2
    Z_positive, Z_negative = antithetic_variates_samples(n_pairs, seed=seed)
    
    # Compute payoffs for both paths
    payoffs_pos, payoffs_neg = antithetic_monte_carlo_prices(
        S0, K, T, r, sigma, Z_positive, Z_negative
    )
    
    # Combine payoffs
    all_payoffs = np.concatenate([payoffs_pos, payoffs_neg])
    
    # Compute option price: discounted expected payoff
    discount_factor = np.exp(-r * T)
    option_price = discount_factor * np.mean(all_payoffs)
    
    # Compute standard error
    std_payoffs = np.std(all_payoffs, ddof=1)
    standard_error = discount_factor * std_payoffs / np.sqrt(n_samples)
    
    # End timing
    elapsed_time = time.perf_counter() - start_time
    
    return option_price, standard_error, elapsed_time


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Monte Carlo pricing for European call options",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Option parameters
    parser.add_argument("--S0", type=float, default=100.0,
                        help="Initial stock price")
    parser.add_argument("--K", type=float, default=100.0,
                        help="Strike price")
    parser.add_argument("--T", type=float, default=1.0,
                        help="Time to maturity (years)")
    parser.add_argument("--r", type=float, default=0.05,
                        help="Risk-free rate (annual)")
    parser.add_argument("--sigma", type=float, default=0.20,
                        help="Volatility (annual)")
    
    # Monte Carlo parameters
    parser.add_argument("--n-samples", type=int, required=True,
                        help="Number of Monte Carlo samples")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--antithetic", action="store_true",
                        help="Use antithetic variates for variance reduction")
    
    # Output options
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV file path (optional)")
    parser.add_argument("--validate", action="store_true",
                        help="Compare MC result with Black-Scholes analytical price")
    
    args = parser.parse_args()
    
    # Print configuration
    print("=" * 70)
    print("Monte Carlo European Call Option Pricing")
    if args.antithetic:
        print("(with Antithetic Variates Variance Reduction)")
    print("=" * 70)
    print(f"Parameters:")
    print(f"  S0 (Initial price):  ${args.S0:.2f}")
    print(f"  K (Strike price):    ${args.K:.2f}")
    print(f"  T (Time to maturity): {args.T:.2f} years")
    print(f"  r (Risk-free rate):   {args.r:.4f} ({args.r*100:.2f}%)")
    print(f"  sigma (Volatility):   {args.sigma:.4f} ({args.sigma*100:.2f}%)")
    print(f"\nMonte Carlo settings:")
    print(f"  N (samples):          {args.n_samples:,}")
    print(f"  Random seed:          {args.seed}")
    print(f"  Variance reduction:   {'Antithetic variates' if args.antithetic else 'None'}")
    print("=" * 70)
    
    # Run Monte Carlo simulation
    if args.antithetic:
        # Ensure even number of samples for antithetic variates
        if args.n_samples % 2 != 0:
            print(f"\nWarning: n_samples must be even for antithetic variates.")
            print(f"         Adjusting from {args.n_samples} to {args.n_samples + 1}")
            args.n_samples += 1
        
        mc_price, mc_stderr, elapsed = monte_carlo_european_call_antithetic(
            S0=args.S0,
            K=args.K,
            T=args.T,
            r=args.r,
            sigma=args.sigma,
            n_samples=args.n_samples,
            seed=args.seed
        )
    else:
        mc_price, mc_stderr, elapsed = monte_carlo_european_call(
            S0=args.S0,
            K=args.K,
            T=args.T,
            r=args.r,
            sigma=args.sigma,
            n_samples=args.n_samples,
            seed=args.seed
        )
    
    # Calculate throughput
    throughput = args.n_samples / elapsed
    
    # Print results
    print(f"\nResults:")
    print(f"  Monte Carlo price:    ${mc_price:.6f}")
    print(f"  Standard error:       ${mc_stderr:.6f}")
    print(f"  95% Confidence Int.:  [${mc_price - 1.96*mc_stderr:.6f}, "
          f"${mc_price + 1.96*mc_stderr:.6f}]")
    print(f"\nPerformance:")
    print(f"  Elapsed time:         {elapsed:.4f} seconds")
    print(f"  Throughput:           {throughput:,.0f} samples/sec")
    
    # Validate against Black-Scholes if requested
    if args.validate:
        bs_price = black_scholes_call(args.S0, args.K, args.T, args.r, args.sigma)
        abs_error = abs(mc_price - bs_price)
        rel_error = abs_error / bs_price * 100
        
        print(f"\nValidation vs Black-Scholes:")
        print(f"  Analytical price:     ${bs_price:.6f}")
        print(f"  Absolute error:       ${abs_error:.6f}")
        print(f"  Relative error:       {rel_error:.4f}%")
        
        # Check if MC price is within confidence interval
        within_ci = abs(mc_price - bs_price) <= 1.96 * mc_stderr
        print(f"  Within 95% CI:        {within_ci}")
        
        if rel_error < 1.0:
            print(f"  ✓ Validation PASSED (error < 1%)")
        else:
            print(f"  ✗ Validation WARNING (error >= 1%, may need more samples)")
    
    print("=" * 70)
    
    # Save to CSV if requested
    if args.output:
        import pandas as pd
        
        # Calculate analytical price for reference
        bs_price = black_scholes_call(args.S0, args.K, args.T, args.r, args.sigma)
        
        method_name = 'serial_mc_antithetic' if args.antithetic else 'serial_mc'
        results_df = pd.DataFrame([{
            'method': method_name,
            'n_samples': args.n_samples,
            'S0': args.S0,
            'K': args.K,
            'T': args.T,
            'r': args.r,
            'sigma': args.sigma,
            'mc_price': mc_price,
            'mc_stderr': mc_stderr,
            'bs_price': bs_price,
            'abs_error': abs(mc_price - bs_price),
            'rel_error_pct': abs(mc_price - bs_price) / bs_price * 100,
            'elapsed_sec': elapsed,
            'throughput_samples_per_sec': throughput,
            'antithetic': args.antithetic,
            'seed': args.seed
        }])
        
        results_df.to_csv(args.output, index=False)
        print(f"Results saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

