"""
Variance Reduction Techniques for Monte Carlo Simulation

This module implements variance reduction methods to improve Monte Carlo
convergence rates and reduce the number of samples needed for a given accuracy.

References:
    Glasserman, P. (2003). Monte Carlo Methods in Financial Engineering.
    Springer. Chapter 4: Variance Reduction Techniques.
"""

import numpy as np
from typing import Tuple, Optional


def antithetic_variates_samples(n_pairs: int, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    if seed is not None:
        np.random.seed(seed)
    
    # Generate N/2 random normals
    Z_positive = np.random.normal(0.0, 1.0, n_pairs)
    
    # Create antithetic pairs
    Z_negative = -Z_positive
    
    return Z_positive, Z_negative


def antithetic_monte_carlo_prices(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    Z_positive: np.ndarray,
    Z_negative: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:

    # GBM parameters
    drift = (r - 0.5 * sigma**2) * T
    diffusion_factor = sigma * np.sqrt(T)
    
    # Simulate terminal prices for both paths
    S_T_positive = S0 * np.exp(drift + diffusion_factor * Z_positive)
    S_T_negative = S0 * np.exp(drift + diffusion_factor * Z_negative)
    
    # Compute payoffs
    payoffs_positive = np.maximum(S_T_positive - K, 0.0)
    payoffs_negative = np.maximum(S_T_negative - K, 0.0)
    
    return payoffs_positive, payoffs_negative


def control_variate_adjustment(
    mc_payoffs: np.ndarray,
    control_values: np.ndarray,
    control_mean: float
) -> float:

    # Compute optimal coefficient
    covariance = np.cov(mc_payoffs, control_values)[0, 1]
    variance_control = np.var(control_values, ddof=1)
    
    if variance_control > 0:
        beta = covariance / variance_control
    else:
        beta = 0
    
    # Apply control variate adjustment
    adjusted_payoffs = mc_payoffs - beta * (control_values - control_mean)
    
    return np.mean(adjusted_payoffs)


if __name__ == "__main__":
    # Demonstrate variance reduction
    print("=" * 70)
    print("Variance Reduction Demonstration")
    print("=" * 70)
    
    # Test antithetic variates
    n_pairs = 1000
    Z1, Z2 = antithetic_variates_samples(n_pairs, seed=42)
    
    print(f"\nAntithetic Variates Test:")
    print(f"  Generated {n_pairs} pairs ({2*n_pairs} total samples)")
    print(f"  Z1 mean: {np.mean(Z1):.6f} (should be ~0)")
    print(f"  Z2 mean: {np.mean(Z2):.6f} (should be ~0)")
    print(f"  Z1 + Z2 sum: {np.sum(Z1 + Z2):.10f} (should be exactly 0)")
    print(f"  Correlation(Z1, Z2): {np.corrcoef(Z1, Z2)[0,1]:.6f} (should be -1)")
    
    # Compare standard vs antithetic variance
    from option_pricing import black_scholes_call
    
    S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    # Standard Monte Carlo
    n_samples = 10000
    Z_standard = np.random.normal(0, 1, n_samples)
    drift = (r - 0.5 * sigma**2) * T
    S_T = S0 * np.exp(drift + sigma * np.sqrt(T) * Z_standard)
    payoffs_standard = np.maximum(S_T - K, 0)
    price_standard = np.exp(-r * T) * np.mean(payoffs_standard)
    stderr_standard = np.exp(-r * T) * np.std(payoffs_standard, ddof=1) / np.sqrt(n_samples)
    
    # Antithetic variates
    Z_pos, Z_neg = antithetic_variates_samples(n_samples // 2, seed=42)
    payoffs_pos, payoffs_neg = antithetic_monte_carlo_prices(S0, K, T, r, sigma, Z_pos, Z_neg)
    payoffs_anti = np.concatenate([payoffs_pos, payoffs_neg])
    price_anti = np.exp(-r * T) * np.mean(payoffs_anti)
    stderr_anti = np.exp(-r * T) * np.std(payoffs_anti, ddof=1) / np.sqrt(n_samples)
    
    print(f"\nVariance Reduction Comparison ({n_samples} samples):")
    print(f"  Black-Scholes price: ${bs_price:.6f}")
    print(f"\n  Standard MC:")
    print(f"    Price: ${price_standard:.6f}")
    print(f"    Std Error: ${stderr_standard:.6f}")
    print(f"    Error vs BS: ${abs(price_standard - bs_price):.6f}")
    print(f"\n  Antithetic Variates MC:")
    print(f"    Price: ${price_anti:.6f}")
    print(f"    Std Error: ${stderr_anti:.6f}")
    print(f"    Error vs BS: ${abs(price_anti - bs_price):.6f}")
    print(f"\n  Variance Reduction:")
    print(f"    Ratio: {stderr_standard / stderr_anti:.2f}x")
    print(f"    Improvement: {(1 - stderr_anti/stderr_standard)*100:.1f}%")
    
    print("=" * 70)

