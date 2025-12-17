"""
Performance benchmarking utilities.

Provides tools for measuring and reporting performance metrics
for the league system.
"""

import time
import tracemalloc
import asyncio
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
from functools import wraps
import statistics


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    function_name: str
    num_runs: int
    avg_time_seconds: float
    min_time_seconds: float
    max_time_seconds: float
    std_time_seconds: float
    peak_memory_mb: float
    success_count: int
    failure_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function": self.function_name,
            "runs": self.num_runs,
            "avg_time_ms": round(self.avg_time_seconds * 1000, 2),
            "min_time_ms": round(self.min_time_seconds * 1000, 2),
            "max_time_ms": round(self.max_time_seconds * 1000, 2),
            "std_time_ms": round(self.std_time_seconds * 1000, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "success_rate": f"{self.success_count}/{self.num_runs}",
        }


class PerformanceTimer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: float = 0
        self.end_time: float = 0
        self.elapsed: float = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time


def benchmark_sync(
    func: Callable,
    *args,
    num_runs: int = 3,
    warmup: bool = True,
    **kwargs
) -> BenchmarkResult:
    """
    Run comprehensive performance benchmarks on a sync function.

    Args:
        func: Function to benchmark
        *args: Positional arguments for function
        num_runs: Number of timed runs
        warmup: Whether to do a warmup run
        **kwargs: Keyword arguments for function

    Returns:
        BenchmarkResult with timing data
    """
    times: List[float] = []
    success_count = 0
    failure_count = 0
    peak_memory = 0

    # Warmup run
    if warmup:
        try:
            func(*args, **kwargs)
        except Exception:
            pass

    # Timed runs
    for _ in range(num_runs):
        tracemalloc.start()

        try:
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()

            current, peak = tracemalloc.get_traced_memory()
            peak_memory = max(peak_memory, peak)

            times.append(end - start)
            success_count += 1
        except Exception:
            failure_count += 1
        finally:
            tracemalloc.stop()

    if not times:
        times = [0]

    return BenchmarkResult(
        function_name=func.__name__,
        num_runs=num_runs,
        avg_time_seconds=statistics.mean(times),
        min_time_seconds=min(times),
        max_time_seconds=max(times),
        std_time_seconds=statistics.stdev(times) if len(times) > 1 else 0,
        peak_memory_mb=peak_memory / 1024 / 1024,
        success_count=success_count,
        failure_count=failure_count,
    )


async def benchmark_async(
    func: Callable,
    *args,
    num_runs: int = 3,
    warmup: bool = True,
    **kwargs
) -> BenchmarkResult:
    """
    Run comprehensive performance benchmarks on an async function.

    Args:
        func: Async function to benchmark
        *args: Positional arguments for function
        num_runs: Number of timed runs
        warmup: Whether to do a warmup run
        **kwargs: Keyword arguments for function

    Returns:
        BenchmarkResult with timing data
    """
    times: List[float] = []
    success_count = 0
    failure_count = 0
    peak_memory = 0

    # Warmup run
    if warmup:
        try:
            await func(*args, **kwargs)
        except Exception:
            pass

    # Timed runs
    for _ in range(num_runs):
        tracemalloc.start()

        try:
            start = time.perf_counter()
            await func(*args, **kwargs)
            end = time.perf_counter()

            current, peak = tracemalloc.get_traced_memory()
            peak_memory = max(peak_memory, peak)

            times.append(end - start)
            success_count += 1
        except Exception:
            failure_count += 1
        finally:
            tracemalloc.stop()

    if not times:
        times = [0]

    return BenchmarkResult(
        function_name=func.__name__,
        num_runs=num_runs,
        avg_time_seconds=statistics.mean(times),
        min_time_seconds=min(times),
        max_time_seconds=max(times),
        std_time_seconds=statistics.stdev(times) if len(times) > 1 else 0,
        peak_memory_mb=peak_memory / 1024 / 1024,
        success_count=success_count,
        failure_count=failure_count,
    )


def timed(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed*1000:.2f}ms")
        return result
    return wrapper


def print_benchmark_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results as a formatted table."""
    print("\n" + "=" * 70)
    print("  PERFORMANCE BENCHMARKS")
    print("=" * 70)
    print(f"  {'Function':<25} {'Avg (ms)':<10} {'Min':<10} {'Max':<10} {'Mem (MB)':<10}")
    print(f"  {'-'*65}")

    for r in results:
        print(f"  {r.function_name:<25} "
              f"{r.avg_time_seconds*1000:<10.2f} "
              f"{r.min_time_seconds*1000:<10.2f} "
              f"{r.max_time_seconds*1000:<10.2f} "
              f"{r.peak_memory_mb:<10.2f}")

    print("=" * 70 + "\n")
