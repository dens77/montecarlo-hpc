#!/usr/bin/env python3
"""
Result Plotting and Visualization

This module generates publication-quality plots from experimental results:
1. Strong scaling: speedup vs nodes
2. Weak scaling: efficiency vs nodes
3. Convergence: error vs N (log-log scale)
4. Optimization: baseline vs antithetic variates

Usage:
    python src/plot_results.py --strong results/strong_*.csv --weak results/weak_*.csv
    python src/plot_results.py --convergence results/convergence_*.csv
    python src/plot_results.py --all results/
"""

import argparse
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional
import sys
import os

# Set publication-quality defaults
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def plot_strong_scaling(csv_files: List[str], output_path: str = "results/strong_scaling.png") -> None:
    """
    Generate strong scaling plot: speedup vs number of nodes.
    
    Args:
        csv_files: List of CSV files with strong scaling data
        output_path: Output path for the plot
    """
    # Read and combine all CSV files
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        # Extract node count from filename or data
        if 'n_ranks' in df.columns:
            # Calculate nodes assuming 16 tasks per node (adjust if needed)
            df['nodes'] = df['n_ranks'] / 16
        dfs.append(df)
    
    if not dfs:
        print("No strong scaling data found")
        return
    
    data = pd.concat(dfs, ignore_index=True)
    
    # Group by node count and compute speedup
    grouped = data.groupby('nodes')['elapsed_sec'].mean().reset_index()
    grouped = grouped.sort_values('nodes')
    
    # Compute speedup relative to 1 node
    baseline_time = grouped[grouped['nodes'] == grouped['nodes'].min()]['elapsed_sec'].values[0]
    grouped['speedup'] = baseline_time / grouped['elapsed_sec']
    grouped['efficiency'] = grouped['speedup'] / grouped['nodes'] * 100
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot actual speedup
    ax.plot(grouped['nodes'], grouped['speedup'], 
            marker='o', markersize=10, linewidth=2, 
            label='Measured Speedup', color='#2E86AB')
    
    # Plot ideal speedup
    ax.plot(grouped['nodes'], grouped['nodes'], 
            linestyle='--', linewidth=2, 
            label='Ideal (Linear) Speedup', color='#A23B72')
    
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Speedup')
    ax.set_title('Strong Scaling: Speedup vs Number of Nodes')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add efficiency annotations
    for _, row in grouped.iterrows():
        ax.annotate(f"{row['efficiency']:.1f}%", 
                   (row['nodes'], row['speedup']),
                   textcoords="offset points", 
                   xytext=(0,10), 
                   ha='center',
                   fontsize=10,
                   alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Strong scaling plot saved to: {output_path}")
    plt.close()


def plot_weak_scaling(csv_files: List[str], output_path: str = "results/weak_scaling.png") -> None:
    """
    Generate weak scaling plot: efficiency vs number of nodes.
    
    Args:
        csv_files: List of CSV files with weak scaling data
        output_path: Output path for the plot
    """
    # Read and combine all CSV files
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        if 'n_ranks' in df.columns:
            df['nodes'] = df['n_ranks'] / 16
        dfs.append(df)
    
    if not dfs:
        print("No weak scaling data found")
        return
    
    data = pd.concat(dfs, ignore_index=True)
    
    # Group by node count
    grouped = data.groupby('nodes')['elapsed_sec'].mean().reset_index()
    grouped = grouped.sort_values('nodes')
    
    # Compute efficiency relative to 1 node
    baseline_time = grouped[grouped['nodes'] == grouped['nodes'].min()]['elapsed_sec'].values[0]
    grouped['efficiency'] = (baseline_time / grouped['elapsed_sec']) * 100
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot efficiency
    ax.plot(grouped['nodes'], grouped['efficiency'], 
            marker='s', markersize=10, linewidth=2, 
            label='Measured Efficiency', color='#F18F01')
    
    # Plot ideal 100% efficiency line
    ax.axhline(y=100, linestyle='--', linewidth=2, 
              label='Ideal (100% Efficiency)', color='#A23B72')
    
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Parallel Efficiency (%)')
    ax.set_title('Weak Scaling: Efficiency vs Number of Nodes')
    ax.set_ylim([0, 105])
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add value labels
    for _, row in grouped.iterrows():
        ax.annotate(f"{row['efficiency']:.1f}%", 
                   (row['nodes'], row['efficiency']),
                   textcoords="offset points", 
                   xytext=(0,5), 
                   ha='center',
                   fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Weak scaling plot saved to: {output_path}")
    plt.close()


def plot_convergence(csv_file: str, output_path: str = "results/convergence.png") -> None:
    """
    Generate convergence plot: error vs N samples (log-log scale).
    
    Args:
        csv_file: CSV file with convergence data
        output_path: Output path for the plot
    """
    # Read convergence data
    data = pd.read_csv(csv_file)
    
    if 'n_samples' not in data.columns or 'abs_error' not in data.columns:
        print(f"Error: CSV must have 'n_samples' and 'abs_error' columns")
        return
    
    data = data.sort_values('n_samples')
    
    # Create log-log plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot measured error
    ax.loglog(data['n_samples'], data['abs_error'], 
             marker='o', markersize=10, linewidth=2, 
             label='Measured Error', color='#06A77D')
    
    # Plot theoretical O(1/√N) line
    N_range = data['n_samples'].values
    # Fit to first point to get constant
    C = data['abs_error'].iloc[0] * np.sqrt(data['n_samples'].iloc[0])
    theoretical = C / np.sqrt(N_range)
    
    ax.loglog(N_range, theoretical, 
             linestyle='--', linewidth=2, 
             label='O(1/√N) Theory', color='#A23B72')
    
    ax.set_xlabel('Number of Samples (N)')
    ax.set_ylabel('Absolute Error ($)')
    ax.set_title('Convergence: Error vs Sample Size')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend()
    
    # Add slope annotation
    if len(data) >= 2:
        # Compute slope from first and last points
        log_n1, log_n2 = np.log10(data['n_samples'].iloc[0]), np.log10(data['n_samples'].iloc[-1])
        log_e1, log_e2 = np.log10(data['abs_error'].iloc[0]), np.log10(data['abs_error'].iloc[-1])
        slope = (log_e2 - log_e1) / (log_n2 - log_n1)
        
        ax.text(0.05, 0.95, f'Measured slope: {slope:.2f}\nTheoretical: -0.50',
               transform=ax.transAxes, 
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Convergence plot saved to: {output_path}")
    plt.close()


def plot_optimization_comparison(
    baseline_csv: str, 
    antithetic_csv: str, 
    output_path: str = "results/optimization.png"
) -> None:
    """
    Generate optimization comparison: baseline vs antithetic variates.
    
    Args:
        baseline_csv: CSV file with baseline results
        antithetic_csv: CSV file with antithetic variates results
        output_path: Output path for the plot
    """
    # Read data
    baseline = pd.read_csv(baseline_csv)
    antithetic = pd.read_csv(antithetic_csv)
    
    # Extract key metrics
    baseline_time = baseline['elapsed_sec'].mean()
    antithetic_time = antithetic['elapsed_sec'].mean()
    
    baseline_stderr = baseline['mc_stderr'].mean()
    antithetic_stderr = antithetic['mc_stderr'].mean()
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Standard Error Comparison
    methods = ['Baseline', 'Antithetic\nVariates']
    stderr_values = [baseline_stderr, antithetic_stderr]
    colors = ['#2E86AB', '#06A77D']
    
    bars1 = ax1.bar(methods, stderr_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Standard Error ($)')
    ax1.set_title('Variance Reduction: Standard Error Comparison')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars1, stderr_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${val:.4f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add improvement annotation
    improvement = (1 - antithetic_stderr / baseline_stderr) * 100
    ax1.text(0.5, 0.95, f'Variance Reduction: {improvement:.1f}%',
            transform=ax1.transAxes,
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
            fontsize=12, fontweight='bold')
    
    # Plot 2: Execution Time Comparison
    time_values = [baseline_time, antithetic_time]
    
    bars2 = ax2.bar(methods, time_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Execution Time (seconds)')
    ax2.set_title('Computational Cost Comparison')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars2, time_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}s',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add time overhead annotation
    overhead = (antithetic_time / baseline_time - 1) * 100
    overhead_text = f'Time Overhead: {overhead:+.1f}%' if overhead > 0 else f'Time Speedup: {-overhead:.1f}%'
    ax2.text(0.5, 0.95, overhead_text,
            transform=ax2.transAxes,
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7),
            fontsize=12, fontweight='bold')
    
    plt.suptitle('Optimization Results: Antithetic Variates Variance Reduction', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Optimization comparison plot saved to: {output_path}")
    plt.close()


def plot_all_from_directory(results_dir: str) -> None:
    """
    Automatically find and plot all available results from a directory.
    
    Args:
        results_dir: Directory containing result CSV files
    """
    results_dir = Path(results_dir)
    
    print("=" * 70)
    print("Generating All Plots from Results Directory")
    print("=" * 70)
    print(f"Searching in: {results_dir}")
    print()
    
    # Find strong scaling files
    strong_files = list(results_dir.glob("strong_scaling_*.csv"))
    if strong_files:
        print(f"Found {len(strong_files)} strong scaling file(s)")
        plot_strong_scaling([str(f) for f in strong_files])
    else:
        print("⚠️  No strong scaling files found (strong_scaling_*.csv)")
    
    # Find weak scaling files
    weak_files = list(results_dir.glob("weak_scaling_*.csv"))
    if weak_files:
        print(f"Found {len(weak_files)} weak scaling file(s)")
        plot_weak_scaling([str(f) for f in weak_files])
    else:
        print("⚠️  No weak scaling files found (weak_scaling_*.csv)")
    
    # Find convergence file
    convergence_files = list(results_dir.glob("convergence_*.csv"))
    if convergence_files:
        print(f"Found {len(convergence_files)} convergence file(s)")
        # Use the most recent one
        plot_convergence(str(convergence_files[-1]))
    else:
        print("⚠️  No convergence files found (convergence_*.csv)")
    
    # Find baseline and antithetic files for optimization comparison
    baseline_files = list(results_dir.glob("*baseline*.csv")) or list(results_dir.glob("test_standard.csv"))
    antithetic_files = list(results_dir.glob("*antithetic*.csv"))
    
    if baseline_files and antithetic_files:
        print(f"Found baseline and antithetic files")
        plot_optimization_comparison(str(baseline_files[0]), str(antithetic_files[0]))
    else:
        print("⚠️  No optimization comparison files found")
        print("    Run: python src/monte_carlo.py --n-samples 1M --output results/baseline.csv")
        print("    Run: python src/monte_carlo.py --n-samples 1M --antithetic --output results/antithetic.csv")
    
    print()
    print("=" * 70)
    print("Plotting complete!")
    print("=" * 70)


def generate_sample_data(output_dir: str = "results/sample_data") -> None:
    """
    Generate sample/mock data for testing plots before running actual experiments.
    
    Args:
        output_dir: Directory to save sample data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating sample data for plot testing...")
    
    # Sample strong scaling data
    # Simulate realistic speedup with some overhead
    nodes = [1, 2, 4, 8]
    ranks = [16, 32, 64, 128]
    n_samples = 1_000_000_000
    baseline_time = 100.0  # seconds for 1 node
    
    strong_data = []
    for n, r in zip(nodes, ranks):
        # Realistic speedup: not perfect due to overhead
        speedup = n * 0.85  # 85% efficiency
        time_sec = baseline_time / speedup
        
        strong_data.append({
            'method': 'mpi_mc',
            'n_ranks': r,
            'n_samples': n_samples,
            'mc_price': 10.45 + np.random.normal(0, 0.001),
            'mc_stderr': 0.02 / np.sqrt(n),
            'bs_price': 10.450583,
            'abs_error': 0.001,
            'rel_error_pct': 0.01,
            'elapsed_sec': time_sec,
            'throughput_samples_per_sec': n_samples / time_sec
        })
    
    pd.DataFrame(strong_data).to_csv(f"{output_dir}/strong_scaling_sample.csv", index=False)
    
    # Sample weak scaling data
    weak_data = []
    for n, r in zip(nodes, ranks):
        # Each node does 100M samples
        n_samples_weak = 100_000_000 * n
        # Time should be roughly constant (weak scaling)
        time_sec = 10.0 * (1 + 0.05 * (n - 1))  # Small increase
        
        weak_data.append({
            'method': 'mpi_mc',
            'n_ranks': r,
            'n_samples': n_samples_weak,
            'mc_price': 10.45 + np.random.normal(0, 0.001),
            'mc_stderr': 0.02,
            'bs_price': 10.450583,
            'abs_error': 0.001,
            'rel_error_pct': 0.01,
            'elapsed_sec': time_sec,
            'throughput_samples_per_sec': n_samples_weak / time_sec
        })
    
    pd.DataFrame(weak_data).to_csv(f"{output_dir}/weak_scaling_sample.csv", index=False)
    
    # Sample convergence data
    n_values = [10**i for i in range(4, 10)]  # 1e4 to 1e9
    convergence_data = []
    
    for n in n_values:
        # Error should scale as 1/sqrt(N)
        error = 0.1 / np.sqrt(n) + np.random.normal(0, 0.1 / np.sqrt(n) * 0.1)
        time_sec = n / 12_000_000  # ~12M samples/sec
        
        convergence_data.append({
            'n_samples': n,
            'mc_price': 10.45 + error,
            'mc_stderr': 0.02 / np.sqrt(n / 1000000),
            'bs_price': 10.450583,
            'abs_error': abs(error),
            'rel_error_pct': abs(error) / 10.45 * 100,
            'elapsed_sec': time_sec,
            'throughput': n / time_sec
        })
    
    pd.DataFrame(convergence_data).to_csv(f"{output_dir}/convergence_sample.csv", index=False)
    
    # Sample baseline vs antithetic
    baseline_data = [{
        'method': 'serial_mc',
        'n_samples': 1_000_000,
        'mc_price': 10.4505,
        'mc_stderr': 0.0206,
        'bs_price': 10.450583,
        'abs_error': 0.000083,
        'rel_error_pct': 0.0008,
        'elapsed_sec': 0.083,
        'throughput_samples_per_sec': 12_048_000,
        'antithetic': False
    }]
    pd.DataFrame(baseline_data).to_csv(f"{output_dir}/baseline_sample.csv", index=False)
    
    antithetic_data = [{
        'method': 'serial_mc_antithetic',
        'n_samples': 1_000_000,
        'mc_price': 10.4504,
        'mc_stderr': 0.0145,  # ~70% of baseline (1.4x reduction)
        'bs_price': 10.450583,
        'abs_error': 0.000183,
        'rel_error_pct': 0.0018,
        'elapsed_sec': 0.095,  # Slightly slower
        'throughput_samples_per_sec': 10_526_000,
        'antithetic': True
    }]
    pd.DataFrame(antithetic_data).to_csv(f"{output_dir}/antithetic_sample.csv", index=False)
    
    print(f"✅ Sample data generated in: {output_dir}/")
    print(f"   - strong_scaling_sample.csv")
    print(f"   - weak_scaling_sample.csv")
    print(f"   - convergence_sample.csv")
    print(f"   - baseline_sample.csv")
    print(f"   - antithetic_sample.csv")


def main():
    """Main entry point for plot generation."""
    parser = argparse.ArgumentParser(
        description="Generate plots from Monte Carlo experiment results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--strong", nargs='+', 
                       help="Strong scaling CSV file(s)")
    parser.add_argument("--weak", nargs='+',
                       help="Weak scaling CSV file(s)")
    parser.add_argument("--convergence", type=str,
                       help="Convergence CSV file")
    parser.add_argument("--baseline", type=str,
                       help="Baseline CSV file for optimization comparison")
    parser.add_argument("--antithetic", type=str,
                       help="Antithetic variates CSV file for optimization comparison")
    
    parser.add_argument("--all", type=str,
                       help="Directory containing all results (auto-detect files)")
    
    parser.add_argument("--generate-sample", action="store_true",
                       help="Generate sample data for testing plots")
    
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate sample data if requested
    if args.generate_sample:
        generate_sample_data(f"{args.output_dir}/sample_data")
        print("\nTo test plots with sample data:")
        print(f"  python src/plot_results.py --all {args.output_dir}/sample_data")
        return 0
    
    # Auto-detect mode
    if args.all:
        plot_all_from_directory(args.all)
        return 0
    
    # Manual mode
    generated_any = False
    
    if args.strong:
        plot_strong_scaling(args.strong, f"{args.output_dir}/strong_scaling.png")
        generated_any = True
    
    if args.weak:
        plot_weak_scaling(args.weak, f"{args.output_dir}/weak_scaling.png")
        generated_any = True
    
    if args.convergence:
        plot_convergence(args.convergence, f"{args.output_dir}/convergence.png")
        generated_any = True
    
    if args.baseline and args.antithetic:
        plot_optimization_comparison(
            args.baseline, 
            args.antithetic, 
            f"{args.output_dir}/optimization.png"
        )
        generated_any = True
    
    if not generated_any:
        print("No plots generated. Use --help for usage information.")
        print("\nQuick start:")
        print("  1. Generate sample data: python src/plot_results.py --generate-sample")
        print("  2. Test plots: python src/plot_results.py --all results/sample_data")
        print("  3. Or provide specific CSV files: python src/plot_results.py --strong results/strong_*.csv")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

