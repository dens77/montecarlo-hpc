# Monte Carlo European Option Pricing - HPC Project

Parallel Monte Carlo simulation for European option pricing using the Black-Scholes model.  
Demonstrates HPC scaling, profiling, and variance reduction techniques.

---

## 🚀 Quick Start


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


#. Run all experiments
./run.sh submit-all
```

### Generation of plots

# Download everything from cluster


### Generate Plots

```bash
# On your laptop
# Generate all plots
./run.sh plot

# View plots
open results/strong_scaling.png
open results/weak_scaling.png
open results/convergence.png
open results/optimization.png
```


