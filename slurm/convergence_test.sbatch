#!/bin/bash
#SBATCH --job-name=mc-convergence    # Job name
#SBATCH --nodes=1                    # Single node for convergence test
#SBATCH --ntasks-per-node=16         # MPI ranks per node
#SBATCH --cpus-per-task=1            # CPUs per MPI rank
#SBATCH --time=01:00:00              # 1 hour
#SBATCH --output=results/logs/convergence_%j.out
#SBATCH --error=results/logs/convergence_%j.err

# Convergence test: verify error scales as O(1/√N)
# Run with multiple sample sizes to measure error vs N

set -euo pipefail

echo "========================================"
echo "Monte Carlo Convergence Test"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Testing convergence rate: error should scale as O(1/√N)"
echo "Sample sizes: 1e4, 1e5, 1e6, 1e7, 1e8, 1e9"
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

# Test parameters (ATM option)
S0=100
K=100
T=1.0
r=0.05
sigma=0.2

echo "Test parameters: S0=$S0, K=$K, T=$T, r=$r, sigma=$sigma"
echo "========================================"

# Array of sample sizes to test
SAMPLE_SIZES=(10000 100000 1000000 10000000 100000000 1000000000)

# Output file
OUTPUT_FILE="results/convergence_${SLURM_JOB_ID}.csv"

# Create CSV header
echo "n_samples,mc_price,mc_stderr,bs_price,abs_error,rel_error_pct,elapsed_sec,throughput" > $OUTPUT_FILE

# Run convergence tests
for N in "${SAMPLE_SIZES[@]}"; do
    echo ""
    echo "Testing with N=$N samples..."
    echo "----------------------------------------"
    
    # Run Monte Carlo
    srun python src/mpi_monte_carlo.py \
        --n-samples $N \
        --S0 $S0 \
        --K $K \
        --T $T \
        --r $r \
        --sigma $sigma \
        --output results/convergence_${N}_${SLURM_JOB_ID}.csv
    
    # Append to main convergence file
    tail -n 1 results/convergence_${N}_${SLURM_JOB_ID}.csv >> $OUTPUT_FILE
    
    echo "Completed N=$N"
done

echo ""
echo "========================================"
echo "Convergence test completed"
echo "Results saved to: $OUTPUT_FILE"
echo "Finished at: $(date)"
echo "========================================"

# Show convergence data
echo ""
echo "Convergence Results Summary:"
cat $OUTPUT_FILE

# Job statistics
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Elapsed,MaxRSS,State,ExitCode

