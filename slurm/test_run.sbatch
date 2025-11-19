#!/bin/bash
#SBATCH --job-name=mc-test           # Job name
#SBATCH --nodes=1                    # Number of nodes
#SBATCH --ntasks-per-node=4          # MPI ranks per node (adjust based on cluster)
#SBATCH --cpus-per-task=1            # CPUs per MPI rank
#SBATCH --time=00:05:00              # 5 minutes
#SBATCH --output=results/logs/test_%j.out
#SBATCH --error=results/logs/test_%j.err

# NOTE: You may need to add:
# #SBATCH --partition=<partition-name>
# #SBATCH --account=<account-name>
# Check with: sinfo, sacctmgr show assoc where user=$USER

set -euo pipefail

echo "========================================"
echo "Monte Carlo Test Run"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Tasks: $SLURM_NTASKS"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE"
echo "CPUs per task: $SLURM_CPUS_PER_TASK"
echo "Node list: $SLURM_NODELIST"
echo "Started at: $(date)"
echo "Working directory: $(pwd)"
echo "========================================"

# Load modules
# Adjust these based on what's available on your cluster
# Check with: module avail
module purge
module load gcc || module load GCC || true
module load openmpi || module load OpenMPI || true
module load python/3 || module load Python/3 || true

echo ""
echo "Loaded modules:"
module list
echo ""

# If using virtual environment:
# source ~/venvs/montecarlo/bin/activate

# Print environment info
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo "Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
echo "========================================"

# Run test
echo ""
echo "Running MPI Monte Carlo test..."
echo "Parameters: 1M samples, S0=100, K=100, ATM option"
echo ""

srun python src/mpi_monte_carlo.py \
    --n-samples 1000000 \
    --S0 100 \
    --K 100 \
    --T 1.0 \
    --r 0.05 \
    --sigma 0.2 \
    --validate \
    --output results/test_${SLURM_JOB_ID}.csv

echo ""
echo "========================================"
echo "Job finished at: $(date)"
echo "Results saved to: results/test_${SLURM_JOB_ID}.csv"
echo "========================================"

# Print job statistics
sacct -j $SLURM_JOB_ID --format=JobID,Elapsed,MaxRSS,State

