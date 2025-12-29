#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#

"""
Performance Benchmarking Tests for SpareTools
==============================================

This module provides comprehensive performance benchmarking for sparetools components,
measuring execution times, memory usage, and scalability metrics.
"""

import time
import psutil
import os
import sys
import statistics
from typing import Dict, List, Callable, Any
import tracemalloc
import cProfile
import pstats
import io

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes


class PerformanceTestHarness(NgapyTestHarnes):
    """Test harness for performance benchmarking."""

    def __init__(self):
        super().__init__()
        self.benchmarks = {}
        self.memory_snapshots = []

    def benchmark_function(self, name: str, func: Callable, *args, iterations: int = 100, **kwargs) -> Dict[str, float]:
        """Benchmark a function with multiple iterations."""
        times = []

        # Warm up
        for _ in range(10):
            func(*args, **kwargs)

        # Actual benchmarking
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)

        # Calculate statistics
        stats = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }

        self.benchmarks[name] = stats
        return stats

    def memory_benchmark(self, name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark memory usage of a function."""
        tracemalloc.start()
        start_snapshot = tracemalloc.take_snapshot()

        result = func(*args, **kwargs)

        end_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Calculate memory difference
        stats = end_snapshot.compare_to(start_snapshot, 'lineno')
        total_memory = sum(stat.size_diff for stat in stats)

        memory_stats = {
            'total_memory_delta': total_memory,
            'peak_memory': max((stat.size for stat in end_snapshot.statistics('lineno')), default=0),
            'memory_stats': [{'file': stat.traceback[0].filename if stat.traceback else 'unknown',
                            'line': stat.traceback[0].lineno if stat.traceback else 0,
                            'size': stat.size_diff} for stat in stats[:10]]  # Top 10
        }

        if name not in self.benchmarks:
            self.benchmarks[name] = {}
        self.benchmarks[name]['memory'] = memory_stats

        return memory_stats

    def profile_function(self, name: str, func: Callable, *args, **kwargs) -> str:
        """Profile a function using cProfile."""
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Get profile stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions

        profile_output = s.getvalue()

        if name not in self.benchmarks:
            self.benchmarks[name] = {}
        self.benchmarks[name]['profile'] = profile_output

        return profile_output

    def test_import_performance(self) -> bool:
        """Test import performance for sparetools modules."""
        success = True

        # Benchmark core imports
        import_times = {}

        def benchmark_import(module_name: str):
            start = time.perf_counter()
            __import__(module_name)
            end = time.perf_counter()
            return end - start

        core_modules = [
            'sparetools',
            'sparetools.core',
            'sparetools.test_environments',
            'sparetools.core.configuration'
        ]

        for module in core_modules:
            try:
                import_time = self.benchmark_function(
                    f'import_{module.replace(".", "_")}',
                    benchmark_import, module,
                    iterations=5
                )['mean']

                import_times[module] = import_time

                # Check reasonable import times
                success &= self.verify_lt(
                    import_time, 2.0,
                    f"{module} import time < 2s",
                    test_num=1
                )

            except ImportError:
                success &= self.verify(
                    False, True,
                    f"Failed to import {module}",
                    test_num=1
                )

        return success

    def test_core_functionality_performance(self) -> bool:
        """Test performance of core sparetools functionality."""
        success = True

        # Test harness operations
        th = NgapyTestHarnes()

        # Benchmark verify operations
        verify_stats = self.benchmark_function(
            'verify_operations',
            lambda: [th.verify(i, i, f"test {i}") for i in range(100)],
            iterations=10
        )

        success &= self.verify_lt(
            verify_stats['mean'], 1.0,
            "Verify operations performance",
            test_num=2
        )

        # Memory benchmark for verify operations
        self.memory_benchmark(
            'verify_memory',
            lambda: [th.verify(i, i, f"test {i}") for i in range(1000)]
        )

        return success

    def test_file_operation_performance(self) -> bool:
        """Test file operation performance."""
        success = True

        import tempfile
        from pathlib import Path

        # Benchmark file I/O
        def file_io_test():
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
                # Write test
                for i in range(1000):
                    f.write(f"Line {i}: This is a test line with some content\n")
                f.flush()

                # Read test
                f.seek(0)
                content = f.read()

                # Cleanup
                os.unlink(f.name)

            return len(content)

        file_stats = self.benchmark_function(
            'file_io_operations',
            file_io_test,
            iterations=5
        )

        success &= self.verify_lt(
            file_stats['mean'], 5.0,
            "File I/O operations performance",
            test_num=3
        )

        return success

    def test_memory_usage_patterns(self) -> bool:
        """Test memory usage patterns."""
        success = True

        # Test memory growth with repeated operations
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        th = NgapyTestHarnes()
        for i in range(1000):
            th.verify(i % 2, i % 2, f"Memory test {i}")

        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        success &= self.verify_lt(
            memory_growth, 50.0,  # Less than 50MB growth
            f"Memory growth: {memory_growth:.2f}MB",
            test_num=4
        )

        return success

    def test_concurrent_performance(self) -> bool:
        """Test performance under concurrent load (simulated)."""
        success = True

        import threading

        results = []
        errors = []

        def worker_thread(thread_id: int):
            try:
                th = NgapyTestHarnes()
                start = time.perf_counter()

                for i in range(100):
                    th.verify(i, i, f"Thread {thread_id} test {i}")

                end = time.perf_counter()
                results.append(end - start)

            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker_thread, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        if errors:
            success &= self.verify(
                False, True,
                f"Concurrent execution errors: {errors}",
                test_num=5
            )
        else:
            avg_time = statistics.mean(results)
            success &= self.verify_lt(
                avg_time, 2.0,
                f"Concurrent execution time: {avg_time:.3f}s",
                test_num=5
            )

        return success

    def test_scalability_metrics(self) -> bool:
        """Test scalability with increasing load."""
        success = True

        scalability_data = []

        for load_factor in [10, 50, 100, 500]:
            th = NgapyTestHarnes()

            start = time.perf_counter()
            for i in range(load_factor):
                th.verify(i % 2, i % 2, f"Scalability test {i}")
            end = time.perf_counter()

            execution_time = end - start
            scalability_data.append((load_factor, execution_time))

        # Check for reasonable scaling (should be roughly linear)
        if len(scalability_data) >= 2:
            first_time = scalability_data[0][1]
            last_time = scalability_data[-1][1]
            scaling_ratio = last_time / first_time

            # Should scale reasonably (not exponentially worse)
            success &= self.verify_lt(
                scaling_ratio, 100.0,  # Arbitrary reasonable limit
                f"Scalability ratio: {scaling_ratio:.2f}",
                test_num=6
            )

        return success

    def generate_performance_report(self, output_file: str = "performance_report.json") -> bool:
        """Generate a comprehensive performance report."""
        success = True

        try:
            import json

            report = {
                'metadata': {
                    'timestamp': time.time(),
                    'platform': {
                        'system': os.uname().sysname if hasattr(os, 'uname') else 'Unknown',
                        'cpu_count': os.cpu_count(),
                        'python_version': sys.version
                    }
                },
                'benchmarks': self.benchmarks
            }

            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

            success &= self.verify(
                True, True,
                f"Performance report generated: {output_file}",
                test_num=7
            )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Failed to generate performance report: {str(e)}",
                test_num=7
            )

        return success

    def run_performance_tests(self) -> bool:
        """Run all performance tests."""
        print("Running Performance Benchmark Tests...")

        results = []

        results.append(("Import Performance", self.test_import_performance()))
        results.append(("Core Functionality", self.test_core_functionality_performance()))
        results.append(("File Operations", self.test_file_operation_performance()))
        results.append(("Memory Usage", self.test_memory_usage_patterns()))
        results.append(("Concurrent Performance", self.test_concurrent_performance()))
        results.append(("Scalability", self.test_scalability_metrics()))
        results.append(("Report Generation", self.generate_performance_report()))

        print("\nPerformance Test Results:")
        all_passed = True
        for test_name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"  {test_name}: {status}")
            all_passed &= passed

        return all_passed


def run_performance_tests():
    """Main function to run performance tests."""
    harness = PerformanceTestHarness()
    success = harness.run_performance_tests()

    print(f"\nOverall Performance Tests: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)