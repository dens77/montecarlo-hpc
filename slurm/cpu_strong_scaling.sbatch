#!/bin/bash
#SBATCH --job-name=mc-strong          # Job name
#SBATCH --nodes=1                     # Will be overridden by --nodes= when submitting
#SBATCH --ntasks-per-node=2           # MPI ranks per node (cluster has 2 CPUs/node)
#SBATCH --cpus-per-task=1             # CPUs per MPI rank
#SBATCH --mem-per-cpu=512M            # Increased memory to prevent OOM errors
#SBATCH --time=01:00:00               # 1 hour
#SBATCH --output=results/logs/strong_%j.out
#SBATCH --error=results/logs/strong_%j.err

# NOTE: Submit this with different node counts:
# sbatch --nodes=1 slurm/cpu_strong_scaling.sbatch
# sbatch --nodes=2 slurm/cpu_strong_scaling.sbatch
# sbatch --nodes=4 slurm/cpu_strong_scaling.sbatch
# sbatch --nodes=8 slurm/cpu_strong_scaling.sbatch

set -euo pipefail

# Fixed problem size for strong scaling
# Reduced from 100M to avoid OOM errors with 256M default memory
N_SAMPLES=20000000  # 20 million samples (good balance of accuracy and memory usage)

echo "========================================"
echo "Strong Scaling Experiment"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Total tasks: $SLURM_NTASKS"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE"
echo "Total samples: $N_SAMPLES"
echo "Samples per rank: $(($N_SAMPLES / $SLURM_NTASKS))"
echo "Started at: $(date)"
echo "========================================"

# Load modules
module purge
module load gcc
module load python/3
module load mpi4py

echo ""
echo "Loaded modules:"
module list
echo ""

# Note: Packages installed with --user, no venv needed

# Print environment
echo "Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
echo "========================================"

# Run strong scaling test
echo ""
echo "Running strong scaling with $N_SAMPLES samples on $SLURM_NTASKS ranks..."
echo ""

srun python src/mpi_monte_carlo.py \
    --n-samples $N_SAMPLES \
    --S0 100 \
    --K 100 \
    --T 1.0 \
    --r 0.05 \
    --sigma 0.2 \
    --output results/strong_scaling_${SLURM_JOB_NUM_NODES}nodes_${SLURM_JOB_ID}.csv

echo ""
echo "========================================"
echo "Job finished at: $(date)"
echo "Results: results/strong_scaling_${SLURM_JOB_NUM_NODES}nodes_${SLURM_JOB_ID}.csv"
echo "========================================"

# Job statistics
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Elapsed,MaxRSS,State,ExitCode

