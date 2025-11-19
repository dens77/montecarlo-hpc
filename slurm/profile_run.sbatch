#!/bin/bash
#SBATCH --job-name=mc-profile         # Job name
#SBATCH --nodes=1                     # Single node for profiling
#SBATCH --ntasks-per-node=16          # MPI ranks per node
#SBATCH --cpus-per-task=1             # CPUs per MPI rank
#SBATCH --time=00:30:00               # 30 minutes
#SBATCH --output=results/logs/profile_%j.out
#SBATCH --error=results/logs/profile_%j.err

# Profiling run to identify performance bottlenecks
# Uses Python's cProfile or perf stat if available

set -euo pipefail

echo "========================================"
echo "Monte Carlo Profiling Run"
echo "========================================"
echo "Job ID: $SLURM_JOB_ID"
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

# Problem size for profiling (not too large, not too small)
N_SAMPLES=10000000  # 10M samples

echo "Profiling with N=$N_SAMPLES samples"
echo "========================================"

# Profile output directory
PROFILE_DIR="results/logs/profile_${SLURM_JOB_ID}"
mkdir -p $PROFILE_DIR

#
# Method 1: Python cProfile (always available)
#
echo ""
echo "Running with Python cProfile..."
echo "----------------------------------------"

srun python -m cProfile -o ${PROFILE_DIR}/mpi_monte_carlo.prof \
    src/mpi_monte_carlo.py \
    --n-samples $N_SAMPLES \
    --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
    --output ${PROFILE_DIR}/profile_results.csv

# Generate text report from profile
echo ""
echo "Top 30 functions by cumulative time:"
python -c "import pstats; p = pstats.Stats('${PROFILE_DIR}/mpi_monte_carlo.prof'); p.sort_stats('cumulative'); p.print_stats(30)" > ${PROFILE_DIR}/profile_cumulative.txt 2>&1

echo ""
echo "Top 30 functions by total time:"
python -c "import pstats; p = pstats.Stats('${PROFILE_DIR}/mpi_monte_carlo.prof'); p.sort_stats('time'); p.print_stats(30)" > ${PROFILE_DIR}/profile_time.txt 2>&1

#
# Method 2: perf stat (if available)
#
if command -v perf &> /dev/null; then
    echo ""
    echo "Running with perf stat..."
    echo "----------------------------------------"
    
    srun perf stat -o ${PROFILE_DIR}/perf_stats.txt \
        python src/mpi_monte_carlo.py \
        --n-samples $N_SAMPLES \
        --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
        2>&1 | tee ${PROFILE_DIR}/perf_output.txt
    
    echo "perf stat results saved to: ${PROFILE_DIR}/perf_stats.txt"
else
    echo "perf not available, skipping hardware counters"
fi

#
# Method 3: time command (always available)
#
echo ""
echo "Running with /usr/bin/time for resource usage..."
echo "----------------------------------------"

/usr/bin/time -v srun python src/mpi_monte_carlo.py \
    --n-samples $N_SAMPLES \
    --S0 100 --K 100 --T 1.0 --r 0.05 --sigma 0.2 \
    2>&1 | tee ${PROFILE_DIR}/time_output.txt

echo ""
echo "========================================"
echo "Profiling completed"
echo "Results directory: $PROFILE_DIR"
echo "Finished at: $(date)"
echo "========================================"

# Show summary
echo ""
echo "Profile Summary:"
echo "----------------------------------------"
head -40 ${PROFILE_DIR}/profile_cumulative.txt

# Job statistics
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Elapsed,MaxRSS,State,ExitCode

