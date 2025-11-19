#!/usr/bin/env bash
#
# Monte Carlo European Option Pricing - Main Runner
# Works on both local machine and HPC cluster
#

set -euo pipefail

# Detect if we're on a cluster (has srun/sbatch)
if command -v sbatch &> /dev/null; then
    ON_CLUSTER=true
else
    ON_CLUSTER=false
fi

function print_usage() {
    echo "Monte Carlo European Option Pricing - Runner Script"
    echo ""
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Testing Commands:"
    echo "  test           - Run validation tests"
    echo "  test-serial    - Test serial Monte Carlo"
    echo "  test-mpi       - Test MPI (local: mpirun, cluster: salloc)"
    echo ""
    echo "Cluster Commands (requires Slurm):"
    echo "  submit-test    - Submit test job"
    echo "  submit-strong  - Submit strong scaling jobs (nodes: 1,2,4,8)"
    echo "  submit-weak    - Submit weak scaling jobs (nodes: 1,2,4,8)"
    echo "  submit-all     - Submit all experiments"
    echo "  status         - Check job status"
    echo ""
    echo "Plotting Commands:"
    echo "  plot           - Generate all plots from results/"
    echo "  plot-sample    - Generate sample data and test plots"
    echo ""
    echo "Examples:"
    echo "  ./run.sh test"
    echo "  ./run.sh submit-all"
    echo "  ./run.sh plot"
}

function run_tests() {
    echo "Running validation tests..."
    python tests/test_black_scholes.py
}

function test_serial() {
    echo "Testing serial Monte Carlo..."
    python src/monte_carlo.py --n-samples 100000 --validate
}

function test_mpi() {
    if $ON_CLUSTER; then
        echo "Testing MPI on cluster (interactive allocation)..."
        salloc --nodes=1 --ntasks=4 --time=00:05:00 \
            srun python src/mpi_monte_carlo.py --n-samples 1000000 --validate
    else
        if command -v mpirun &> /dev/null; then
            echo "Testing MPI locally..."
            mpirun -n 4 python src/mpi_monte_carlo.py --n-samples 1000000 --validate
        else
            echo "Error: mpirun not found. Install OpenMPI or run on cluster."
            exit 1
        fi
    fi
}

function submit_test() {
    if ! $ON_CLUSTER; then
        echo "Error: This command requires Slurm (run on cluster)"
        exit 1
    fi
    echo "Submitting test job..."
    sbatch slurm/test_run.sbatch
    squeue -u $USER
}

function submit_strong() {
    if ! $ON_CLUSTER; then
        echo "Error: This command requires Slurm (run on cluster)"
        exit 1
    fi
    echo "Submitting strong scaling jobs..."
    for nodes in 1 2 4 8; do
        echo "  Submitting ${nodes} node(s)..."
        sbatch --nodes=$nodes slurm/cpu_strong_scaling.sbatch
    done
    sleep 1
    squeue -u $USER
}

function submit_weak() {
    if ! $ON_CLUSTER; then
        echo "Error: This command requires Slurm (run on cluster)"
        exit 1
    fi
    echo "Submitting weak scaling jobs..."
    for nodes in 1 2 4 8; do
        echo "  Submitting ${nodes} node(s)..."
        sbatch --nodes=$nodes slurm/cpu_weak_scaling.sbatch
    done
    sleep 1
    squeue -u $USER
}

function submit_all() {
    if ! $ON_CLUSTER; then
        echo "Error: This command requires Slurm (run on cluster)"
        exit 1
    fi
    echo "Submitting ALL experiments..."
    echo ""
    
    # Test job
    echo "1. Test job..."
    sbatch slurm/test_run.sbatch
    
    # Strong scaling
    echo "2. Strong scaling (1,2,4,8 nodes)..."
    for nodes in 1 2 4 8; do
        sbatch --nodes=$nodes slurm/cpu_strong_scaling.sbatch
    done
    
    # Weak scaling
    echo "3. Weak scaling (1,2,4,8 nodes)..."
    for nodes in 1 2 4 8; do
        sbatch --nodes=$nodes slurm/cpu_weak_scaling.sbatch
    done
    
    # Convergence
    echo "4. Convergence test..."
    sbatch slurm/convergence_test.sbatch
    
    # Profiling
    echo "5. Profiling run..."
    sbatch slurm/profile_run.sbatch
    
    echo ""
    echo "All jobs submitted!"
    sleep 1
    squeue -u $USER
}

function check_status() {
    if ! $ON_CLUSTER; then
        echo "Error: This command requires Slurm (run on cluster)"
        exit 1
    fi
    squeue -u $USER
    echo ""
    sacct -u $USER --format=JobID,JobName,State,Elapsed,MaxRSS
}

function generate_plots() {
    echo "Generating plots from results..."
    python src/plot_results.py --all results/
}

function generate_sample_plots() {
    echo "Generating sample data and test plots..."
    python src/plot_results.py --generate-sample
    python src/plot_results.py --all results/sample_data
    echo ""
    echo "Sample plots created in results/"
    ls -lh results/*.png
}

# Main command dispatcher
case "${1:-help}" in
    test)
        run_tests
        ;;
    test-serial)
        test_serial
        ;;
    test-mpi)
        test_mpi
        ;;
    submit-test)
        submit_test
        ;;
    submit-strong)
        submit_strong
        ;;
    submit-weak)
        submit_weak
        ;;
    submit-all)
        submit_all
        ;;
    status)
        check_status
        ;;
    plot)
        generate_plots
        ;;
    plot-sample)
        generate_sample_plots
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        print_usage
        exit 1
        ;;
esac
