#!/bin/bash
#SBATCH --job-name=mc-weak            # Job name
#SBATCH --nodes=1                     # Will be overridden by --nodes= when submitting
#SBATCH --ntasks-per-node=2           # MPI ranks per node (cluster has 2 CPUs/node)
#SBATCH --cpus-per-task=1             # CPUs per MPI rank
#SBATCH --mem-per-cpu=512M            # Prevent OOM for large weak scaling runs
#SBATCH --time=01:00:00               # 1 hour
#SBATCH --output=results/logs/weak_%j.out
#SBATCH --error=results/logs/weak_%j.err

# NOTE: Submit this with different node counts:
# sbatch --nodes=1 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=2 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=4 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=8 slurm/cpu_weak_scaling.sbatch

set -euo pipefail

# Weak scaling: problem size grows with nodes
# Keep work per rank constant
# Start with smaller problem, increase if jobs complete quickly
SAMPLES_PER_NODE=10000000  # 10M samples per node (increase to 100M if this completes fast)
N_SAMPLES=$(($SAMPLES_PER_NODE * $SLURM_JOB_NUM_NODES))

echo "========================================"
echo "Weak Scaling Experiment"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Total tasks: $SLURM_NTASKS"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE"
echo "Samples per node: $SAMPLES_PER_NODE"
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

# Run weak scaling test
echo ""
echo "Running weak scaling with $N_SAMPLES samples on $SLURM_NTASKS ranks..."
echo ""

srun python src/mpi_monte_carlo.py \
    --n-samples $N_SAMPLES \
    --S0 100 \
    --K 100 \
    --T 1.0 \
    --r 0.05 \
    --sigma 0.2 \
    --output results/weak_scaling_${SLURM_JOB_NUM_NODES}nodes_${SLURM_JOB_ID}.csv

echo ""
echo "========================================"
echo "Job finished at: $(date)"
echo "Results: results/weak_scaling_${SLURM_JOB_NUM_NODES}nodes_${SLURM_JOB_ID}.csv"
echo "========================================"

# Job statistics
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Elapsed,MaxRSS,State,ExitCode

