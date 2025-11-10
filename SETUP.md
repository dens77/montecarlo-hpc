# Environment Setup Guide

This guide covers setting up your development environment for local development and cluster deployment.

## Local Development Setup (Your Laptop)

### Prerequisites

- Python 3.8+ (Python 3.11 recommended)
- pip (Python package manager)
- OpenMPI (for mpi4py testing, Day 2+)

### Step 1: Clone and Navigate

```bash
cd /Users/denis/Dev/montecarlo-hpc
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# On Windows (if needed)
# venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal prompt.

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
pip install -r env/requirements.txt
```

This installs:
- numpy 1.24.3
- scipy 1.11.4
- mpi4py 3.1.5 (requires OpenMPI)
- pandas 2.1.4
- matplotlib 3.8.2
- pytest 7.4.3

### Step 5: Verify Installation

```bash
python -c "import numpy, scipy, pandas, matplotlib; print('✓ All core packages installed!')"
```

### Step 6: Test the Code

```bash
# Test Black-Scholes formula
python src/option_pricing.py

# Test serial Monte Carlo
python src/monte_carlo.py --n-samples 100000 --validate

# Run full test suite
python tests/test_black_scholes.py
```

### Installing OpenMPI (for mpi4py)

**macOS (Homebrew):**
```bash
brew install open-mpi
pip install mpi4py==3.1.5
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libopenmpi-dev openmpi-bin
pip install mpi4py==3.1.5
```

**Note**: If OpenMPI installation is difficult, you can skip mpi4py for Day 1 and install it before Day 2.

## Cluster Setup (Magic Castle)

### Step 1: SSH to Cluster

```bash
ssh username@magic-castle-cluster.domain
```

### Step 2: Clone Repository

```bash
git clone <your-repo-url>
cd montecarlo-hpc
```

### Step 3: Load Modules

```bash
# Load required modules
source env/modules.txt

# Or manually:
module purge
module load gcc/11.3.0
module load openmpi/4.1.5
module load python/3.11.2
```

### Step 4: Install Python Packages

On the cluster, you can either:

**Option A: User installation (simple)**
```bash
pip install --user -r env/requirements.txt
```

**Option B: Virtual environment (cleaner)**
```bash
python -m venv ~/venvs/montecarlo
source ~/venvs/montecarlo/bin/activate
pip install -r env/requirements.txt
```

**Option C: Apptainer container (most reproducible, Day 3)**
- Will be set up on Day 3 with `env/project.def`

### Step 5: Test on Cluster

```bash
# Test serial version
python src/monte_carlo.py --n-samples 100000 --validate

# Test MPI version (Day 2+)
salloc --ntasks=4 --time=00:05:00
srun python src/mpi_monte_carlo.py --n-samples 1000000
exit
```

## Daily Workflow

### Local Development

```bash
# Activate environment (every time you start working)
cd /Users/denis/Dev/montecarlo-hpc
source venv/bin/activate

# Work on code
vim src/monte_carlo.py

# Test changes
python tests/test_black_scholes.py

# Deactivate when done
deactivate
```

### Cluster Development

```bash
# SSH to cluster
ssh username@cluster

# Load modules
cd montecarlo-hpc
source env/modules.txt

# Submit jobs
sbatch slurm/cpu_strong_scaling.sbatch

# Check status
squeue -u $USER

# View results
less results/logs/job_12345.out
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"

**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### "mpi4py installation fails"

**Solution**: Install OpenMPI first (see above), or skip for now and install before Day 2

### "Permission denied" on cluster

**Solution**: Use `pip install --user` or create venv in your home directory

### "Module 'gcc/11.3.0' not found" on cluster

**Solution**: Check available modules:
```bash
module avail gcc
module avail python
# Use closest versions available
```

## Reproducibility Checklist

For grading, ensure:

- [ ] `env/requirements.txt` has exact versions (no `>=`)
- [ ] Virtual environment or modules documented
- [ ] Git repository includes setup instructions
- [ ] All runs use same Python/package versions
- [ ] Random seeds are set explicitly in code
- [ ] `.gitignore` excludes venv/ and result files

## Getting Help

- **Python packages**: Check [PyPI](https://pypi.org/)
- **MPI issues**: Check [mpi4py docs](https://mpi4py.readthedocs.io/)
- **Cluster**: Contact cluster admin or check Alliance documentation
- **Team**: Ask in your team chat/standup

## Next Steps

- [x] Environment setup complete
- [ ] Proceed to Day 2: MPI implementation
- [ ] Day 3: Apptainer container setup
- [ ] Day 4+: Scaling experiments

