# Data Directory

## Sample Parameters

### `sample_params.csv`

This file contains 5 test cases for European call option pricing, covering different market scenarios:

| Case | S0 | K | T | r | σ | Scenario |
|------|-----|-----|-----|------|------|----------|
| ATM_1year | $100 | $100 | 1.0y | 5% | 20% | Standard at-the-money |
| ITM_1year | $110 | $100 | 1.0y | 5% | 20% | In-the-money (10% ITM) |
| OTM_1year | $90 | $100 | 1.0y | 5% | 20% | Out-of-the-money (10% OTM) |
| ATM_short | $100 | $100 | 0.25y | 5% | 20% | Short maturity (3 months) |
| ATM_highvol | $100 | $100 | 1.0y | 5% | 40% | High volatility scenario |

### Parameter Definitions

- **S0**: Initial stock price (spot price)
- **K**: Strike price (exercise price)
- **T**: Time to maturity in years
- **r**: Risk-free interest rate (annual, decimal format)
- **σ (sigma)**: Volatility (annual standard deviation, decimal format)

### Usage

These parameters can be used to test the Monte Carlo implementation across various scenarios:

```bash
# Example: Price the ATM 1-year option
python src/monte_carlo.py --n-samples 1000000 \
  --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 --validate
```

### Expected Results (Black-Scholes Analytical Prices)

For reference, the analytical Black-Scholes prices for these cases are approximately:

- **ATM_1year**: $10.45
- **ITM_1year**: $16.71
- **OTM_1year**: $5.54
- **ATM_short**: $4.20
- **ATM_highvol**: $15.66

Monte Carlo simulations should converge to these values as the number of samples increases.

### Data Sources

These are synthetic parameters based on typical market conditions:
- Stock price: $100 (normalized for easy interpretation)
- Risk-free rate: 5% (typical pre-2008 rate)
- Volatility: 20% (typical for large-cap stocks), 40% (typical for small-cap or during volatility spikes)

For production use, parameters would be sourced from:
- Market data providers (Bloomberg, Reuters)
- Historical stock price analysis
- Implied volatility from options markets
- Government bond yields for risk-free rates

