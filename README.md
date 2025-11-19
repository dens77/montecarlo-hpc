# Monte Carlo European Option Pricing - HPC Project

Parallel Monte Carlo simulation for European option pricing using the Black-Scholes model.  
Demonstrates HPC scaling, profiling, and variance reduction techniques.

---

## 🚀 Quick Start

### Local Testing (Optional)

```bash
# Run automated test suite
./test_all.sh
```

See [TESTING.md](TESTING.md) for details.

### Cluster Deployment

```bash
# 1. SSH to cluster
ssh user91@login1.hpcie.labs.faculty.ie.edu

# 2. Clone and setup
git clone https://github.com/YOUR-USERNAME/montecarlo-hpc.git
cd montecarlo-hpc
module load gcc openmpi python/3
pip install --user -r env/requirements.txt
mkdir -p results/logs

# 3. Test it works
python src/monte_carlo.py --n-samples 100000 --validate

# 4. Submit test job
sbatch slurm/test_run.sbatch

# 5. Run all experiments
./run.sh submit-all

# 6. Check status
./run.sh status
```

**Complete guide:** [TESTING.md](TESTING.md)

---

## 📁 Repository Structure

```
montecarlo-hpc/
├── src/            # Source code (6 Python modules)
├── env/            # Environment config (requirements.txt, modules.txt)
├── slurm/          # Slurm job scripts (5 experiments)
├── data/           # Sample option parameters
├── results/        # Output CSV + plots + logs
├── tests/          # Unit tests
├── docs/           # Documentation (paper, proposal will go here)
├── run.sh          # Main runner script
└── test_all.sh     # Automated test suite
```

---

## 🔬 What It Does

**Application:** Monte Carlo simulation for European call option pricing

**Algorithm:**
1. Simulate stock price paths using Geometric Brownian Motion
2. Calculate option payoffs: max(S_T - K, 0)
3. Average and discount to get option price
4. Parallel implementation using MPI

**Optimization:** Antithetic variates variance reduction (~2x improvement)

---

## 📊 Experiments Included

| Experiment | Purpose | Script |
|------------|---------|--------|
| Strong scaling | Fixed problem, vary nodes | `slurm/cpu_strong_scaling.sbatch` |
| Weak scaling | Proportional problem | `slurm/cpu_weak_scaling.sbatch` |
| Convergence | Verify O(1/√N) error | `slurm/convergence_test.sbatch` |
| Profiling | Identify bottlenecks | `slurm/profile_run.sbatch` |
| Test | Basic functionality | `slurm/test_run.sbatch` |

**Submit all:** `./run.sh submit-all`

---

## 📈 Results & Plotting

```bash
# After experiments complete, download results
scp -r user91@login1.hpcie.labs.faculty.ie.edu:~/montecarlo-hpc/results .

# Generate plots
python src/plot_results.py --all results/

# Creates 4 publication-quality plots:
# - strong_scaling.png (speedup vs nodes)
# - weak_scaling.png (efficiency vs nodes)
# - convergence.png (error vs N, log-log)
# - optimization.png (baseline vs antithetic variates)
```

---

## 🎯 Assignment Requirements

| Requirement | Status | Location |
|-------------|--------|----------|
| Runs on ≥2 nodes | ✅ | All scaling scripts |
| run.sh | ✅ | Root directory |
| submit.sbatch | ✅ | `slurm/*.sbatch` (5 scripts) |
| Strong & weak scaling | ✅ | Scripts + plotting |
| Profiling | ✅ | `slurm/profile_run.sbatch` |
| Optimization | ✅ | Antithetic variates |
| Reproducibility | ✅ | Pinned versions, fixed seeds |
| Environment config | ✅ | `env/requirements.txt`, `env/modules.txt` |

**Paper & proposal:** Will be added to `docs/` (Days 10-12)

---

## 🔧 Key Features

- **Simple:** Embarrassingly parallel Monte Carlo (minimal communication)
- **Validated:** Compares against Black-Scholes analytical formula
- **Optimized:** Antithetic variates variance reduction
- **Reproducible:** Fixed random seeds, pinned package versions
- **Scalable:** MPI implementation tested on 1-8 nodes
- **Well-tested:** Comprehensive unit tests included

---

## 📚 Documentation

- **[TESTING.md](TESTING.md)** - Complete testing & deployment guide
- **[docs/README.md](docs/README.md)** - Documentation index
- **[data/README.md](data/README.md)** - Sample parameters explanation

---

## 👥 Team

5-7 students, HPC class project

## 📖 References

- Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities.
- Glasserman, P. (2003). Monte Carlo Methods in Financial Engineering.

---

**Quick commands:**
- `./test_all.sh` - Test locally
- `./run.sh submit-all` - Run all experiments on cluster
- `./run.sh plot` - Generate plots from results

**Need help?** See [TESTING.md](TESTING.md)
