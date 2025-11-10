#!/usr/bin/env python3
"""
MPI Parallel Monte Carlo European Option Pricing

This module implements a parallel Monte Carlo simulation using MPI (Message Passing Interface)
for pricing European options under the Black-Scholes model.

Usage:
    mpirun -n 4 python mpi_monte_carlo.py --n-samples 1000000 --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2
    
    Or with srun on Slurm:
    srun python mpi_monte_carlo.py --n-samples 1000000 --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2
"""

import argparse
import time
import numpy as np
from typing import Tuple, Optional
import sys

try:
    from mpi4py import MPI
except ImportError:
    print("Error: mpi4py not found. Install with: pip install mpi4py")
    print("Note: OpenMPI must be installed first.")
    sys.exit(1)

# Import option pricing functions
from option_pricing import (
    validate_option_params,
    black_scholes_call
)
from utils import (
    log_message,
    format_time,
    format_number,
    print_header,
    print_separator,
    write_results_csv,
    get_git_commit_hash
)


def monte_carlo_european_call_mpi(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    n_samples: int,
    seed: int = 42,
    comm: Optional[MPI.Comm] = None
) -> Tuple[float, float, float, int]:
    """
    Price a European call option using parallel Monte Carlo simulation with MPI.
    
    Algorithm (Embarrassingly Parallel):
        1. Each MPI rank generates n_samples // size local samples
        2. Each rank computes local payoff statistics
        3. Root rank aggregates results using MPI.reduce()
        4. Root rank computes final price and standard error
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)
        n_samples: Total number of Monte Carlo samples (across all ranks)
        seed: Base random seed for reproducibility
        comm: MPI communicator (defaults to MPI.COMM_WORLD)
        
    Returns:
        Tuple of (option_price, standard_error, elapsed_time, rank)
    """
    # Get MPI communicator
    if comm is None:
        comm = MPI.COMM_WORLD
    
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # Validate inputs (all ranks do this for error checking)
    validate_option_params(S0, K, T, r, sigma)
    assert n_samples > 0, "Number of samples must be positive"
    assert n_samples >= size, f"n_samples ({n_samples}) must be >= num_ranks ({size})"
    
    # Barrier to synchronize all ranks before starting
    comm.Barrier()
    start_time = time.perf_counter()
    
    # Distribute work: each rank gets approximately n_samples // size
    local_n = n_samples // size
    remainder = n_samples % size
    
    # Give remainder samples to first few ranks
    if rank < remainder:
        local_n += 1
    
    # Set rank-dependent random seed for independent samples
    # Each rank gets a different seed to ensure statistical independence
    local_seed = seed + rank
    np.random.seed(local_seed)
    
    if rank == 0:
        log_message(f"Starting MPI Monte Carlo with {size} ranks", rank=0)
        log_message(f"Total samples: {format_number(n_samples)}", rank=0)
        log_message(f"Samples per rank: ~{format_number(n_samples // size)}", rank=0)
    
    # Generate local random samples: Z ~ N(0,1)
    Z = np.random.normal(0.0, 1.0, local_n)
    
    # Simulate terminal stock prices using GBM
    # S_T = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z
    S_T = S0 * np.exp(drift + diffusion)
    
    # Calculate local payoffs: max(S_T - K, 0)
    local_payoffs = np.maximum(S_T - K, 0.0)
    
    # Compute local statistics
    local_sum = np.sum(local_payoffs)
    local_sum_sq = np.sum(local_payoffs**2)
    local_count = local_n
    
    # Aggregate results across all ranks using MPI.reduce()
    # Sum up payoffs and squared payoffs from all ranks
    global_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
    global_sum_sq = comm.reduce(local_sum_sq, op=MPI.SUM, root=0)
    global_count = comm.reduce(local_count, op=MPI.SUM, root=0)
    
    # Synchronize all ranks
    comm.Barrier()
    elapsed_time = time.perf_counter() - start_time
    
    # Root rank computes final results
    if rank == 0:
        # Compute mean payoff
        mean_payoff = global_sum / global_count
        
        # Compute standard deviation of payoffs
        # Var(X) = E[X^2] - E[X]^2
        mean_payoff_sq = global_sum_sq / global_count
        variance_payoff = mean_payoff_sq - mean_payoff**2
        std_payoff = np.sqrt(variance_payoff)
        
        # Discount to present value
        discount_factor = np.exp(-r * T)
        option_price = discount_factor * mean_payoff
        
        # Standard error: std(payoffs) / sqrt(N)
        standard_error = discount_factor * std_payoff / np.sqrt(global_count)
        
        log_message(f"MPI Monte Carlo completed in {format_time(elapsed_time)}", rank=0)
        
        return option_price, standard_error, elapsed_time, rank
    else:
        # Non-root ranks return None values (won't be used)
        return None, None, elapsed_time, rank


def main():
    """Main entry point for MPI Monte Carlo simulation."""
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # Parse command-line arguments (all ranks do this)
    parser = argparse.ArgumentParser(
        description="MPI parallel Monte Carlo pricing for European call options",
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
                        help="Total number of Monte Carlo samples")
    parser.add_argument("--seed", type=int, default=42,
                        help="Base random seed for reproducibility")
    
    # Output options
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV file path (optional)")
    parser.add_argument("--validate", action="store_true",
                        help="Compare MC result with Black-Scholes analytical price")
    
    args = parser.parse_args()
    
    # Root rank prints configuration
    if rank == 0:
        print_header("MPI Parallel Monte Carlo European Call Option Pricing")
        print(f"MPI Configuration:")
        print(f"  Number of ranks:      {size}")
        print(f"  Samples per rank:     ~{args.n_samples // size:,}")
        print(f"\nOption Parameters:")
        print(f"  S0 (Initial price):   ${args.S0:.2f}")
        print(f"  K (Strike price):     ${args.K:.2f}")
        print(f"  T (Time to maturity):  {args.T:.2f} years")
        print(f"  r (Risk-free rate):    {args.r:.4f} ({args.r*100:.2f}%)")
        print(f"  sigma (Volatility):    {args.sigma:.4f} ({args.sigma*100:.2f}%)")
        print(f"\nMonte Carlo Settings:")
        print(f"  Total samples:         {format_number(args.n_samples)}")
        print(f"  Base random seed:      {args.seed}")
        print(f"  Git commit:            {get_git_commit_hash()[:8]}")
        print_separator()
    
    # Run MPI Monte Carlo simulation
    mc_price, mc_stderr, elapsed, _ = monte_carlo_european_call_mpi(
        S0=args.S0,
        K=args.K,
        T=args.T,
        r=args.r,
        sigma=args.sigma,
        n_samples=args.n_samples,
        seed=args.seed,
        comm=comm
    )
    
    # Only root rank prints results and saves output
    if rank == 0:
        # Calculate throughput
        throughput = args.n_samples / elapsed
        
        # Print results
        print(f"\nResults:")
        print(f"  Monte Carlo price:    ${mc_price:.6f}")
        print(f"  Standard error:       ${mc_stderr:.6f}")
        print(f"  95% Confidence Int.:  [${mc_price - 1.96*mc_stderr:.6f}, "
              f"${mc_price + 1.96*mc_stderr:.6f}]")
        print(f"\nPerformance:")
        print(f"  Wall-clock time:      {format_time(elapsed)}")
        print(f"  Throughput:           {throughput:,.0f} samples/sec")
        print(f"  Throughput per rank:  {throughput/size:,.0f} samples/sec/rank")
        
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
        
        print_separator()
        
        # Save to CSV if requested
        if args.output:
            # Calculate analytical price for reference
            bs_price = black_scholes_call(args.S0, args.K, args.T, args.r, args.sigma)
            
            results_data = [{
                'method': 'mpi_mc',
                'n_ranks': size,
                'n_samples': args.n_samples,
                'samples_per_rank': args.n_samples // size,
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
                'throughput_per_rank': throughput / size,
                'seed': args.seed,
                'git_commit': get_git_commit_hash()[:8]
            }]
            
            write_results_csv(args.output, results_data)
            log_message(f"Results saved to: {args.output}", rank=0)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

