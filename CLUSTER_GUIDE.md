# Complete Cluster Deployment Guide

**Cluster:** `user91@login1.hpcie.labs.faculty.ie.edu`

This guide takes you from zero to running all experiments in ~30 minutes.

---

## 📋 Prerequisites

- Git repository pushed to GitHub (with `env/` files)
- SSH access to cluster

---

## 🚀 Part 1: Initial Setup (10 minutes)

### Step 1: Connect and Clone

```bash
# SSH to cluster
ssh user91@login1.hpcie.labs.faculty.ie.edu

# Clone your repository
cd ~
git clone https://github.com/YOUR-USERNAME/montecarlo-hpc.git
cd montecarlo-hpc

# Verify files present
ls -la
```

Expected: src/, env/, slurm/, data/, results/, tests/ directories

### Step 2: Check Cluster Configuration

```bash
# Check available modules
module spider python
module spider gcc
module spider openmpi

# Check available resources
sinfo
scontrol show partition

# Check your account/allocation
sacctmgr show assoc where user=user91
```

**Note:** You may need to add `#SBATCH --partition=<name>` or `#SBATCH --account=<name>` to job scripts.

### Step 3: Load Modules

```bash
module purge
module load gcc
module load openmpi
module load python/3

# Verify
module list
python --version
which mpirun
```

**Update `env/modules.txt`** with the actual module names/versions that work on your cluster.

### Step 4: Install Python Packages

```bash
# Install to user directory
pip install --user -r env/requirements.txt

# Verify installation
python -c "import numpy, scipy, mpi4py, pandas, matplotlib; print('✅ All packages installed')"
```

If mpi4py fails, ensure OpenMPI module is loaded first.

### Step 5: Quick Functionality Test

```bash
# Test serial version
python src/monte_carlo.py --n-samples 100000 --validate
```

**Expected output:** Price ≈ $10.45, error < 1%, validation PASSED

---

## 🧪 Part 2: Test Job (5 minutes)

### Submit Your First Job

```bash
# Create results/logs directory
mkdir -p results/logs

# Submit test job (1 node, 5 minutes)
sbatch slurm/test_run.sbatch

# Note the job ID
# Expected output: "Submitted batch job 12345"
```

### Monitor Job

```bash
# Check status
squeue -u user91

# Job states:
# PD = Pending (waiting in queue)
# R  = Running
# CD = Completed
```

### Check Results

```bash
# After job completes (no longer in squeue)
ls results/logs/
cat results/logs/test_*.out

# Look for:
# "✓ Validation PASSED (error < 1%)"

# Check CSV
cat results/test_*.csv
```

**✅ If test job succeeds, you're ready for full experiments!**

**❌ If test job fails:**
- Check error log: `cat results/logs/test_*.err`
- Check job details: `scontrol show job JOBID`
- Common issues: module loading, pip packages, partition/account settings

---

## 📊 Part 3: Run All Experiments (5 minutes to submit)

Once test job succeeds, submit all experiments at once:

```bash
./run.sh submit-all
```

This submits:
- 1 test job
- 4 strong scaling jobs (1, 2, 4, 8 nodes)
- 4 weak scaling jobs (1, 2, 4, 8 nodes)
- 1 convergence test
- 1 profiling run

**Total: 11 jobs**

### Monitor All Jobs

```bash
# Watch job queue
watch -n 10 'squeue -u user91'
# Press Ctrl+C to exit

# Check summary
./run.sh status

# Or manually
sacct -u user91 --format=JobID,JobName,State,Elapsed,MaxRSS
```

**Experiments will complete in ~2-4 hours** (depending on queue time).

---

## 📥 Part 4: Collect Results (5 minutes)

### Download Results to Local Machine

```bash
# From your LOCAL machine (not cluster)
scp -r user91@login1.hpcie.labs.faculty.ie.edu:~/montecarlo-hpc/results ./
```

### Verify Results

```bash
# Check what was downloaded
ls -lh results/*.csv
ls -lh results/logs/*.out

# Expected files:
# results/strong_scaling_1nodes_*.csv
# results/strong_scaling_2nodes_*.csv
# results/strong_scaling_4nodes_*.csv
# results/strong_scaling_8nodes_*.csv
# results/weak_scaling_*nodes_*.csv (×4)
# results/convergence_*.csv
# results/logs/profile_*/
```

---

## 📈 Part 5: Generate Plots (2 minutes)

```bash
# On local machine
cd /Users/denis/Dev/montecarlo-hpc
source venv/bin/activate

# Generate all plots
python src/plot_results.py --all results/

# View plots
ls results/*.png
open results/strong_scaling.png
open results/weak_scaling.png
open results/convergence.png
open results/optimization.png
```

**You now have all 4 figures for your paper!**

---

## ✅ Verification Checklist

### Before Submitting Jobs:
- [ ] Repository cloned on cluster
- [ ] Modules load successfully (`module list`)
- [ ] Python packages installed (`python -c "import numpy..."`)
- [ ] Test job completes successfully
- [ ] Test CSV created in `results/`

### After All Jobs Complete:
- [ ] All jobs show "COMPLETED" status (`sacct`)
- [ ] Strong scaling CSVs (4 files)
- [ ] Weak scaling CSVs (4 files)
- [ ] Convergence CSV (1 file)
- [ ] Profiling results in `results/logs/profile_*/`
- [ ] All logs in `results/logs/`

### After Downloading:
- [ ] Results downloaded to local machine
- [ ] 4 plots generated
- [ ] Plots show expected trends
- [ ] Ready for paper writing

---

## 🎯 Expected Results

### Strong Scaling (1B samples fixed)

| Nodes | Time | Speedup | Efficiency |
|-------|------|---------|------------|
| 1 | 100s | 1.0x | 100% |
| 2 | 55s | 1.8x | 90% |
| 4 | 30s | 3.3x | 83% |
| 8 | 18s | 5.6x | 70% |

### Weak Scaling (100M samples per node)

| Nodes | Samples | Time | Efficiency |
|-------|---------|------|------------|
| 1 | 100M | 10s | 100% |
| 2 | 200M | 11s | 91% |
| 4 | 400M | 12s | 83% |
| 8 | 800M | 14s | 71% |

### Convergence

Error should follow O(1/√N) with slope ≈ -0.5 on log-log plot.

### Profiling

Top bottlenecks: RNG generation (60%), exp/sqrt functions (30%)

---

## 🔧 Troubleshooting

### Job won't start

```bash
# Check queue
squeue

# Check limits
sinfo
scontrol show partition
```

May need to add to job scripts:
```bash
#SBATCH --partition=<name>
#SBATCH --account=<account>
```

### Module load fails

```bash
# Use whatever's available
module load gcc  # Loads default version
module load python

# Update slurm/*.sbatch scripts with correct module names
```

### Results not appearing

```bash
# Check job completed successfully
sacct -j JOBID --format=JobID,State,ExitCode

# Check error logs
cat results/logs/strong_*.err
```

---

## 📞 Getting Help

- **Cluster issues:** Contact HPC admin
- **Code issues:** Check `TESTING.md`
- **Slurm:** `man sbatch`, `man squeue`

---

**This guide should get you from setup to results in one session!**

**Quick path:**
1. SSH + clone (2 min)
2. Load modules + pip install (3 min)
3. Test job (5 min)
4. Submit all experiments (1 min)
5. Wait for completion (2-4 hours)
6. Download + plot (5 min)
7. Write paper! (Days 10-12)

