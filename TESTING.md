# Testing & Deployment Guide

Complete guide for testing locally and deploying to the HPC cluster.

---

## 🧪 Local Testing (Optional)

### Quick Test

```bash
cd /Users/denis/Dev/montecarlo-hpc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (skip mpi4py if no OpenMPI)
pip install numpy==1.24.3 scipy==1.11.4 pandas==2.1.4 matplotlib==3.8.2 pytest==7.4.3

# Run tests
python src/option_pricing.py
python src/monte_carlo.py --n-samples 100000 --validate
python tests/test_black_scholes.py

# Test variance reduction
python src/variance_reduction.py
python src/monte_carlo.py --n-samples 100000 --antithetic --validate
```

**Expected:** All tests pass, prices match Black-Scholes within 1%.

---

## 🚀 Cluster Deployment

**Cluster:** `user91@login1.hpcie.labs.faculty.ie.edu`

### Step 1: Initial Setup

```bash
# SSH to cluster
ssh user91@login1.hpcie.labs.faculty.ie.edu

# Clone repository
git clone https://github.com/YOUR-USERNAME/montecarlo-hpc.git
cd montecarlo-hpc

# Create results directory
mkdir -p results/logs
```

### Step 2: Load Modules

```bash
# Check available modules
module spider python
module spider gcc
module spider openmpi

# Load modules (adjust versions based on what's available)
module purge
module load gcc
module load openmpi  
module load python/3

# Verify
module list
python --version
which mpirun
```

### Step 3: Install Python Packages

```bash
# Install to user directory
pip install --user -r env/requirements.txt

# Verify
python -c "import numpy, scipy, mpi4py, pandas; print('✅ OK')"
```

###Step 4: Test on Cluster

```bash
# Test serial version
python src/monte_carlo.py --n-samples 100000 --validate

# Test MPI interactively
salloc --nodes=1 --ntasks=4 --time=00:05:00
srun python src/mpi_monte_carlo.py --n-samples 1000000 --validate
exit
```

### Step 5: Submit Test Job

```bash
# Submit first test job
sbatch slurm/test_run.sbatch

# Check status
squeue -u user91

# Once complete (status CD), view results
cat results/logs/test_*.out
cat results/test_*.csv
```

**If test job succeeds, proceed to experiments!**

---

## 📊 Running Experiments

### Run All Experiments (Copy-Paste)

```bash
# Strong scaling (fixed 1B samples)
sbatch --nodes=1 slurm/cpu_strong_scaling.sbatch
sbatch --nodes=2 slurm/cpu_strong_scaling.sbatch
sbatch --nodes=4 slurm/cpu_strong_scaling.sbatch
sbatch --nodes=8 slurm/cpu_strong_scaling.sbatch

# Weak scaling (proportional problem size)
sbatch --nodes=1 slurm/cpu_weak_scaling.sbatch
sbatch --nodes=2 slurm/cpu_weak_scaling.sbatch
sbatch --nodes=4 slurm/cpu_weak_scaling.sbatch
sbatch --nodes=8 slurm/cpu_weak_scaling.sbatch

# Convergence test
sbatch slurm/convergence_test.sbatch

# Profiling
sbatch slurm/profile_run.sbatch

# Check all jobs
squeue -u user91
```

### Monitor Progress

```bash
# Watch queue
watch -n 5 'squeue -u user91'

# Check specific job
scontrol show job JOBID

# View completed jobs
sacct -u user91 --format=JobID,JobName,State,Elapsed,MaxRSS
```

---

## 📥 Collecting Results

### Download Results to Local Machine

```bash
# From your LOCAL machine
scp -r user91@login1.hpcie.labs.faculty.ie.edu:~/montecarlo-hpc/results .
```

### Generate Plots

```bash
# On your local machine
cd /Users/denis/Dev/montecarlo-hpc
source venv/bin/activate

# Generate all plots
python src/plot_results.py --all results/

# View plots
open results/*.png
```

**You'll get 4 plots:** strong_scaling.png, weak_scaling.png, convergence.png, optimization.png

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `module spider <name>`, use closest version |
| mpi4py import error | `module load openmpi` before `pip install` |
| Job won't start | Check: `scontrol show partition`, may need `#SBATCH --partition=<name>` |
| Permission denied | Use `pip install --user` |
| Job fails immediately | Check `results/logs/*_*.err` file |

---

## ✅ Verification Checklist

Before running experiments:
- [ ] Repository cloned on cluster
- [ ] Modules load successfully
- [ ] Python packages installed
- [ ] Test job completes successfully
- [ ] Results CSV created

After experiments:
- [ ] All jobs completed (check `sacct`)
- [ ] CSV files in `results/`
- [ ] Logs in `results/logs/`
- [ ] Plots generated
- [ ] Ready for paper writing

---

**For detailed troubleshooting, see assignment requirements or ask cluster admin.**

