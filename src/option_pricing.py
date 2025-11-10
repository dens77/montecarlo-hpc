"""
European Option Pricing Functions

This module implements the Black-Scholes analytical formula for European options
and utility functions for option pricing calculations.

References:
    Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities.
    Journal of Political Economy, 81(3), 637-654.
"""

import numpy as np
from scipy.stats import norm
from typing import Tuple


def validate_option_params(S0: float, K: float, T: float, r: float, sigma: float) -> None:
    """
    Validate option pricing parameters.
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (in years)
        r: Risk-free interest rate (annual)
        sigma: Volatility (annual standard deviation)
        
    Raises:
        AssertionError: If any parameter is invalid
    """
    assert S0 > 0, "Initial stock price (S0) must be positive"
    assert K > 0, "Strike price (K) must be positive"
    assert T > 0, "Time to maturity (T) must be positive"
    assert r >= 0, "Risk-free rate (r) must be non-negative"
    assert sigma > 0, "Volatility (sigma) must be positive"


def black_scholes_call(S0: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Calculate European call option price using Black-Scholes formula.
    
    The Black-Scholes formula for a European call option:
        C = S0 * N(d1) - K * exp(-r*T) * N(d2)
    where:
        d1 = [ln(S0/K) + (r + sigma^2/2)*T] / (sigma*sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        N(x) = cumulative standard normal distribution
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (in years)
        r: Risk-free interest rate (annual)
        sigma: Volatility (annual standard deviation)
        
    Returns:
        Call option price
        
    Example:
        >>> price = black_scholes_call(100, 100, 1.0, 0.05, 0.2)
        >>> print(f"Call price: ${price:.2f}")
    """
    validate_option_params(S0, K, T, r, sigma)
    
    # Calculate d1 and d2
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate call option price using Black-Scholes formula
    call_price = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    return call_price


def black_scholes_put(S0: float, K: float, T: float, r: float, sigma: float) -> float:
    """
    Calculate European put option price using Black-Scholes formula.
    
    The Black-Scholes formula for a European put option:
        P = K * exp(-r*T) * N(-d2) - S0 * N(-d1)
    
    Args:
        S0: Initial stock price
        K: Strike price
        T: Time to maturity (in years)
        r: Risk-free interest rate (annual)
        sigma: Volatility (annual standard deviation)
        
    Returns:
        Put option price
    """
    validate_option_params(S0, K, T, r, sigma)
    
    # Calculate d1 and d2
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate put option price using Black-Scholes formula
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)
    
    return put_price


def call_payoff(S_T: float, K: float) -> float:
    """
    Calculate the payoff of a European call option at maturity.
    
    Payoff = max(S_T - K, 0)
    
    Args:
        S_T: Stock price at maturity
        K: Strike price
        
    Returns:
        Call option payoff
    """
    return max(S_T - K, 0.0)


def put_payoff(S_T: float, K: float) -> float:
    """
    Calculate the payoff of a European put option at maturity.
    
    Payoff = max(K - S_T, 0)
    
    Args:
        S_T: Stock price at maturity
        K: Strike price
        
    Returns:
        Put option payoff
    """
    return max(K - S_T, 0.0)


def simulate_gbm_terminal_price(S0: float, T: float, r: float, sigma: float, Z: float) -> float:
    """
    Simulate terminal stock price under Geometric Brownian Motion (GBM).
    
    Under the Black-Scholes model, stock price follows GBM:
        dS = r*S*dt + sigma*S*dW
    
    The terminal price at time T is:
        S_T = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
    where Z ~ N(0,1) is a standard normal random variable.
    
    Args:
        S0: Initial stock price
        T: Time to maturity
        r: Risk-free rate
        sigma: Volatility
        Z: Standard normal random variable
        
    Returns:
        Simulated terminal stock price
    """
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z
    S_T = S0 * np.exp(drift + diffusion)
    return S_T


if __name__ == "__main__":
    # Example usage: price a call option
    S0 = 100.0      # Initial stock price
    K = 100.0       # Strike price (at-the-money)
    T = 1.0         # 1 year to maturity
    r = 0.05        # 5% risk-free rate
    sigma = 0.20    # 20% volatility
    
    call_price = black_scholes_call(S0, K, T, r, sigma)
    put_price = black_scholes_put(S0, K, T, r, sigma)
    
    print(f"Black-Scholes Option Prices:")
    print(f"  Call: ${call_price:.4f}")
    print(f"  Put:  ${put_price:.4f}")
    print(f"\nPut-Call Parity Check:")
    print(f"  Call - Put = {call_price - put_price:.4f}")
    print(f"  S0 - K*exp(-r*T) = {S0 - K * np.exp(-r * T):.4f}")

