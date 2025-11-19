#!/bin/bash
#SBATCH --job-name=mc-weak            # Job name
#SBATCH --nodes=1                     # Will be overridden by job array or manual submission
#SBATCH --ntasks-per-node=16          # MPI ranks per node (adjust to cluster specs)
#SBATCH --cpus-per-task=1             # CPUs per MPI rank
#SBATCH --time=00:30:00               # 30 minutes
#SBATCH --output=results/logs/weak_%j_n%N.out
#SBATCH --error=results/logs/weak_%j_n%N.err

# NOTE: Submit this with different node counts:
# sbatch --nodes=1 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=2 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=4 slurm/cpu_weak_scaling.sbatch
# sbatch --nodes=8 slurm/cpu_weak_scaling.sbatch

set -euo pipefail

# Weak scaling: problem size grows with nodes
# Keep work per rank constant (~6.25M samples per rank for 16 ranks/node)
SAMPLES_PER_NODE=100000000  # 100M samples per node
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
module load gcc || module load GCC || true
module load openmpi || module load OpenMPI || true
module load python/3 || module load Python/3 || true

echo ""
echo "Loaded modules:"
module list
echo ""

# If using virtual environment:
# source ~/venvs/montecarlo/bin/activate

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

