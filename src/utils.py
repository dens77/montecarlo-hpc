"""
Utility Functions for Monte Carlo HPC Project

This module provides helper functions for timing, logging, and data output
used across serial and parallel Monte Carlo implementations.
"""

import time
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
import os


def format_timestamp() -> str:
    """
    Get current timestamp formatted for logging.
    
    Returns:
        Timestamp string in format: YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_message(message: str, rank: Optional[int] = None, flush: bool = True) -> None:
    """
    Print a log message with timestamp and optional rank information.
    
    Args:
        message: The message to log
        rank: MPI rank (if applicable)
        flush: Whether to flush stdout immediately (important for Slurm)
    """
    timestamp = format_timestamp()
    if rank is not None:
        print(f"[{timestamp}] [Rank {rank}] {message}", flush=flush)
    else:
        print(f"[{timestamp}] {message}", flush=flush)


def format_time(seconds: float) -> str:
    """
    Format elapsed time in human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "1m 23.45s" or "45.67s")
    """
    if seconds >= 60:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"
    else:
        return f"{seconds:.2f}s"


def format_number(n: int) -> str:
    """
    Format large numbers with commas for readability.
    
    Args:
        n: Integer to format
        
    Returns:
        Formatted string (e.g., "1,000,000")
    """
    return f"{n:,}"


class Timer:
    """
    Simple context manager for timing code blocks.
    
    Usage:
        with Timer() as t:
            # do something
        print(f"Elapsed: {t.elapsed:.4f} seconds")
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time


def write_results_csv(
    filename: str,
    data: List[Dict[str, Any]],
    append: bool = False
) -> None:
    """
    Write results to CSV file.
    
    Args:
        filename: Output CSV file path
        data: List of dictionaries with result data
        append: If True, append to existing file; otherwise overwrite
        
    Example:
        data = [{
            'n_samples': 1000000,
            'time_sec': 0.123,
            'price': 10.45,
            'stderr': 0.02
        }]
        write_results_csv('results/output.csv', data)
    """
    if not data:
        return
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    mode = 'a' if append else 'w'
    file_exists = os.path.isfile(filename) and append
    
    with open(filename, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        
        # Write header only if file is new or we're overwriting
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(data)


def compute_speedup(time_serial: float, time_parallel: float) -> float:
    """
    Compute speedup factor.
    
    Args:
        time_serial: Time for serial execution
        time_parallel: Time for parallel execution
        
    Returns:
        Speedup factor (time_serial / time_parallel)
    """
    if time_parallel == 0:
        return float('inf')
    return time_serial / time_parallel


def compute_efficiency(speedup: float, num_processors: int) -> float:
    """
    Compute parallel efficiency.
    
    Args:
        speedup: Speedup factor
        num_processors: Number of processors used
        
    Returns:
        Efficiency as a fraction (0 to 1)
    """
    if num_processors == 0:
        return 0.0
    return speedup / num_processors


def compute_efficiency_percent(speedup: float, num_processors: int) -> float:
    """
    Compute parallel efficiency as percentage.
    
    Args:
        speedup: Speedup factor
        num_processors: Number of processors used
        
    Returns:
        Efficiency as percentage (0 to 100)
    """
    return compute_efficiency(speedup, num_processors) * 100.0


def print_separator(char: str = "=", length: int = 70) -> None:
    """
    Print a separator line.
    
    Args:
        char: Character to use for separator
        length: Length of separator line
    """
    print(char * length)


def print_header(title: str, char: str = "=", length: int = 70) -> None:
    """
    Print a formatted header.
    
    Args:
        title: Header title
        char: Character to use for separator
        length: Length of separator line
    """
    print_separator(char, length)
    print(title)
    print_separator(char, length)


def get_git_commit_hash() -> str:
    """
    Get current git commit hash for reproducibility.
    
    Returns:
        Git commit hash or "unknown" if not in a git repo
    """
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def format_bytes(num_bytes: int) -> str:
    """
    Format bytes in human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.23 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


if __name__ == "__main__":
    # Example usage
    print_header("Utils Module Demo")
    
    # Timing demo
    print("\nTiming demo:")
    with Timer() as t:
        time.sleep(0.1)
    print(f"Elapsed: {format_time(t.elapsed)}")
    
    # Formatting demo
    print("\nFormatting demo:")
    print(f"Large number: {format_number(1000000)}")
    print(f"Memory: {format_bytes(1234567890)}")
    
    # Parallel efficiency demo
    print("\nParallel efficiency demo:")
    speedup = 3.5
    processors = 4
    efficiency = compute_efficiency_percent(speedup, processors)
    print(f"Speedup: {speedup:.2f}x on {processors} processors")
    print(f"Efficiency: {efficiency:.1f}%")
    
    # Git commit
    print(f"\nGit commit: {get_git_commit_hash()[:8]}")

