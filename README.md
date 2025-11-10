# Monte Carlo European Option Pricing - HPC Project

High-Performance Computing project implementing parallel Monte Carlo simulation for European option pricing using the Black-Scholes model.

## Project Status

**Phase:** Day 1 Complete - Serial Implementation & Validation  
**Next:** Day 2 - MPI Parallelization

## Quick Start

### Setup Environment (First Time)

```bash
# Automated setup
./setup_venv.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r env/requirements.txt
```

See [SETUP.md](SETUP.md) for detailed setup instructions.

### Run Validation Tests

**Important**: Always activate the virtual environment first:
```bash
source venv/bin/activate
```

Then run tests:

```bash
./run.sh test
```

This will run the complete validation suite comparing Monte Carlo prices against Black-Scholes analytical formula for:
- At-the-money (ATM) options
- In-the-money (ITM) options  
- Out-of-the-money (OTM) options

All tests should pass with relative error < 1% for N=1,000,000 samples.

### Run Example Pricing

```bash
./run.sh example
```

### Price a Custom Option

```bash
python3 src/monte_carlo.py \
  --n-samples 1000000 \
  --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
  --validate
```

**Parameters:**
- `--S0`: Initial stock price (default: 100.0)
- `--K`: Strike price (default: 100.0)
- `--T`: Time to maturity in years (default: 1.0)
- `--r`: Risk-free rate (default: 0.05)
- `--sigma`: Volatility (default: 0.20)
- `--n-samples`: Number of Monte Carlo samples (required)
- `--validate`: Compare with Black-Scholes analytical price
- `--output`: Save results to CSV file

## Repository Structure

```
montecarlo-hpc/
├── src/                    # Source code
│   ├── option_pricing.py   # Black-Scholes analytical formulas
│   ├── monte_carlo.py      # Serial Monte Carlo implementation
│   ├── mpi_monte_carlo.py  # (Coming in Day 2) MPI parallel version
│   └── utils.py            # (Coming in Day 2) Utilities
├── tests/                  # Validation tests
│   └── test_black_scholes.py  # MC vs analytical validation
├── data/                   # Input parameters
│   ├── sample_params.csv   # 5 test cases (ITM, ATM, OTM, etc.)
│   └── README.md           # Parameter documentation
├── results/                # Output directory for results
│   └── logs/               # Slurm job logs
├── slurm/                  # (Coming in Day 3) Slurm batch scripts
├── env/                    # (Coming in Day 3) Environment setup
├── docs/                   # Documentation
└── run.sh                  # Main entry point
```

## Implementation Details

### Black-Scholes Model

European call option price under Black-Scholes:

```
C = S₀ · N(d₁) - K · e^(-rT) · N(d₂)

where:
  d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
  d₂ = d₁ - σ√T
  N(x) = cumulative standard normal distribution
```

### Monte Carlo Algorithm

1. Generate N random samples Z ~ N(0,1)
2. Simulate terminal stock prices: S_T = S₀ · exp((r - 0.5σ²)T + σ√T·Z)
3. Calculate payoffs: max(S_T - K, 0)
4. Discount to present: C = e^(-rT) · mean(payoffs)
5. Compute standard error: stderr = e^(-rT) · std(payoffs) / √N

### Validation Results (Expected)

For N=1,000,000 samples, Monte Carlo prices should match Black-Scholes within 1%:

| Scenario | S₀ | K | BS Price | MC Price | Error |
|----------|-----|-----|----------|----------|-------|
| ATM | $100 | $100 | $10.45 | ~$10.45 | < 1% |
| ITM | $110 | $100 | $16.71 | ~$16.71 | < 1% |
| OTM | $90 | $100 | $5.54 | ~$5.54 | < 1% |

## Dependencies

- Python 3.8+
- numpy >= 1.24.3
- scipy >= 1.11.4
- pandas >= 2.1.4 (for CSV output)
- matplotlib >= 3.8.2 (for plotting, coming in Day 8)
- mpi4py >= 3.1.5 (coming in Day 2)

Install dependencies:

```bash
pip install numpy scipy pandas matplotlib
```

## Convergence Properties

Monte Carlo error follows O(1/√N):
- N = 10,000 → ~1% error
- N = 1,000,000 → ~0.1% error  
- N = 100,000,000 → ~0.01% error

## Development Timeline

- [x] **Day 1**: Serial implementation with validation
- [ ] **Day 2**: MPI parallelization
- [ ] **Day 3**: Cluster deployment (Slurm + Apptainer)
- [ ] **Days 4-7**: Scaling experiments & optimization
- [ ] **Days 8-9**: Analysis & visualization
- [ ] **Days 10-12**: Documentation (paper, proposal, pitch)
- [ ] **Days 13-14**: Final testing & submission

## Team

5-7 students working on HPC class project

## References

- Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. *Journal of Political Economy*, 81(3), 637-654.
- Glasserman, P. (2003). *Monte Carlo Methods in Financial Engineering*. Springer.
- Hull, J. C. (2022). *Options, Futures, and Other Derivatives* (11th ed.). Pearson.

## License

Educational project for HPC coursework.
