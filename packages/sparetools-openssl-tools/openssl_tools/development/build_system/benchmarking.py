#!/usr/bin/env python3
"""
Performance Benchmarking Script for OpenSSL Conan Package
Based on ngapy-dev patterns with comprehensive performance analysis
"""

import os
import sys
import time
import json
import logging
import subprocess
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import argparse
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Benchmark result data class"""
    name: str
    algorithm: str
    key_size: int
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    throughput: float
    platform: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceBaseline:
    """Performance baseline data class"""
    name: str
    algorithm: str
    key_size: int
    expected_avg_time: float
    expected_throughput: float
    tolerance_percent: float
    platform: str
    version: str
    timestamp: str

class OpenSSLPerformanceBenchmark:
    """OpenSSL performance benchmarking with baseline comparison"""
    
    def __init__(self, results_dir: Path, baseline_file: Optional[Path] = None):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Load baselines
        self.baselines = self._load_baselines(baseline_file)
        
        # Platform detection
        self.platform = self._detect_platform()
        
        # Benchmark configurations
        self.benchmark_configs = self._get_benchmark_configs()
        
        logger.info(f"🚀 Performance benchmark initialized for {self.platform}")
    
    def _detect_platform(self) -> str:
        """Detect current platform"""
        import platform
        system = platform.system().lower()
        arch = platform.machine().lower()
        return f"{system}-{arch}"
    
    def _load_baselines(self, baseline_file: Optional[Path]) -> Dict[str, PerformanceBaseline]:
        """Load performance baselines"""
        baselines = {}
        
        if baseline_file and baseline_file.exists():
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
            
            for baseline_info in baseline_data.get("baselines", []):
                key = f"{baseline_info['algorithm']}_{baseline_info['key_size']}"
                baselines[key] = PerformanceBaseline(**baseline_info)
            
            logger.info(f"📊 Loaded {len(baselines)} performance baselines")
        else:
            # Create default baselines
            baselines = self._create_default_baselines()
            logger.info("📊 Using default performance baselines")
        
        return baselines
    
    def _create_default_baselines(self) -> Dict[str, PerformanceBaseline]:
        """Create default performance baselines"""
        baselines = {}
        
        # Default baselines for common algorithms
        default_configs = [
            {"algorithm": "rsa", "key_size": 2048, "expected_avg_time": 0.1, "expected_throughput": 10.0},
            {"algorithm": "rsa", "key_size": 4096, "expected_avg_time": 0.5, "expected_throughput": 2.0},
            {"algorithm": "aes-128-cbc", "key_size": 128, "expected_avg_time": 0.01, "expected_throughput": 100.0},
            {"algorithm": "aes-256-cbc", "key_size": 256, "expected_avg_time": 0.02, "expected_throughput": 50.0},
            {"algorithm": "sha256", "key_size": 256, "expected_avg_time": 0.005, "expected_throughput": 200.0},
            {"algorithm": "sha512", "key_size": 512, "expected_avg_time": 0.01, "expected_throughput": 100.0},
        ]
        
        for config in default_configs:
            key = f"{config['algorithm']}_{config['key_size']}"
            baselines[key] = PerformanceBaseline(
                name=f"{config['algorithm']}_{config['key_size']}",
                algorithm=config["algorithm"],
                key_size=config["key_size"],
                expected_avg_time=config["expected_avg_time"],
                expected_throughput=config["expected_throughput"],
                tolerance_percent=20.0,  # 20% tolerance
                platform=self.platform,
                version="3.5.0",
                timestamp=datetime.now().isoformat()
            )
        
        return baselines
    
    def _get_benchmark_configs(self) -> List[Dict[str, Any]]:
        """Get benchmark configurations"""
        return [
            {"algorithm": "rsa", "key_size": 2048, "iterations": 100},
            {"algorithm": "rsa", "key_size": 4096, "iterations": 50},
            {"algorithm": "aes-128-cbc", "key_size": 128, "iterations": 1000},
            {"algorithm": "aes-256-cbc", "key_size": 256, "iterations": 1000},
            {"algorithm": "sha256", "key_size": 256, "iterations": 2000},
            {"algorithm": "sha512", "key_size": 512, "iterations": 2000},
            {"algorithm": "ecdsa", "key_size": 256, "iterations": 200},
            {"algorithm": "ecdsa", "key_size": 384, "iterations": 100},
        ]
    
    def _run_openssl_speed_test(self, algorithm: str, key_size: int, iterations: int) -> List[float]:
        """Run OpenSSL speed test for specific algorithm"""
        logger.info(f"⚡ Running speed test: {algorithm} {key_size} bits ({iterations} iterations)")
        
        # Prepare OpenSSL speed command
        if algorithm.startswith("rsa"):
            cmd = ["openssl", "speed", "-elapsed", f"{algorithm}{key_size}"]
        elif algorithm.startswith("aes"):
            cmd = ["openssl", "speed", "-elapsed", algorithm]
        elif algorithm.startswith("sha"):
            cmd = ["openssl", "speed", "-elapsed", algorithm]
        elif algorithm.startswith("ecdsa"):
            cmd = ["openssl", "speed", "-elapsed", f"ecdsa{key_size}"]
        else:
            cmd = ["openssl", "speed", "-elapsed", algorithm]
        
        try:
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"❌ OpenSSL speed test failed: {result.stderr}")
                return []
            
            # Parse results
            times = self._parse_openssl_speed_output(result.stdout, algorithm, key_size)
            
            if not times:
                logger.warning(f"⚠️ No timing data found for {algorithm} {key_size}")
                return []
            
            # Limit to requested iterations
            return times[:iterations]
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ OpenSSL speed test timed out for {algorithm} {key_size}")
            return []
        except Exception as e:
            logger.error(f"❌ OpenSSL speed test error: {e}")
            return []
    
    def _parse_openssl_speed_output(self, output: str, algorithm: str, key_size: int) -> List[float]:
        """Parse OpenSSL speed test output"""
        times = []
        
        try:
            lines = output.split('\n')
            
            for line in lines:
                # Look for timing data
                if algorithm in line.lower() and str(key_size) in line:
                    # Parse timing data from line
                    parts = line.split()
                    for part in parts:
                        try:
                            # Look for time values (usually in seconds)
                            if 's' in part and part.replace('s', '').replace('.', '').isdigit():
                                time_val = float(part.replace('s', ''))
                                if 0.001 <= time_val <= 10.0:  # Reasonable time range
                                    times.append(time_val)
                        except ValueError:
                            continue
            
            # If no specific times found, try to extract from general format
            if not times:
                for line in lines:
                    if 'sign' in line.lower() or 'verify' in line.lower():
                        parts = line.split()
                        for part in parts:
                            try:
                                if part.replace('.', '').isdigit():
                                    time_val = float(part)
                                    if 0.001 <= time_val <= 10.0:
                                        times.append(time_val)
                            except ValueError:
                                continue
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing OpenSSL output: {e}")
        
        return times
    
    def _run_custom_benchmark(self, algorithm: str, key_size: int, iterations: int) -> List[float]:
        """Run custom benchmark for algorithms not well supported by openssl speed"""
        logger.info(f"🔧 Running custom benchmark: {algorithm} {key_size} bits")
        
        times = []
        
        try:
            for i in range(iterations):
                start_time = time.time()
                
                if algorithm.startswith("rsa"):
                    # RSA key generation benchmark
                    cmd = ["openssl", "genrsa", str(key_size)]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                elif algorithm.startswith("aes"):
                    # AES encryption benchmark
                    cmd = ["openssl", "enc", "-aes-256-cbc", "-in", "/dev/zero", "-out", "/dev/null", "-pass", "pass:test"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                elif algorithm.startswith("sha"):
                    # Hash benchmark
                    cmd = ["openssl", "dgst", f"-{algorithm}", "/dev/zero"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                end_time = time.time()
                
                if result.returncode == 0:
                    times.append(end_time - start_time)
                else:
                    logger.warning(f"⚠️ Custom benchmark iteration {i} failed")
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"❌ Custom benchmark error: {e}")
        
        return times
    
    def run_benchmark(self, algorithm: str, key_size: int, iterations: int) -> Optional[BenchmarkResult]:
        """Run benchmark for specific algorithm and key size"""
        logger.info(f"🚀 Starting benchmark: {algorithm} {key_size} bits")
        
        # Try OpenSSL speed first
        times = self._run_openssl_speed_test(algorithm, key_size, iterations)
        
        # Fallback to custom benchmark if needed
        if not times:
            times = self._run_custom_benchmark(algorithm, key_size, iterations)
        
        if not times:
            logger.error(f"❌ No timing data collected for {algorithm} {key_size}")
            return None
        
        # Calculate statistics
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        
        # Calculate throughput (operations per second)
        throughput = len(times) / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            name=f"{algorithm}_{key_size}",
            algorithm=algorithm,
            key_size=key_size,
            iterations=len(times),
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            throughput=throughput,
            platform=self.platform,
            timestamp=datetime.now().isoformat(),
            metadata={
                "raw_times": times,
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
        )
        
        logger.info(f"✅ Benchmark completed: {algorithm} {key_size} - "
                   f"Avg: {avg_time:.4f}s, Throughput: {throughput:.2f} ops/s")
        
        return result
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all configured benchmarks"""
        logger.info("🚀 Running all performance benchmarks...")
        
        results = []
        
        for config in self.benchmark_configs:
            result = self.run_benchmark(
                config["algorithm"],
                config["key_size"],
                config["iterations"]
            )
            
            if result:
                results.append(result)
        
        logger.info(f"✅ Completed {len(results)} benchmarks")
        return results
    
    def compare_with_baseline(self, result: BenchmarkResult) -> Dict[str, Any]:
        """Compare benchmark result with baseline"""
        key = f"{result.algorithm}_{result.key_size}"
        baseline = self.baselines.get(key)
        
        if not baseline:
            return {
                "has_baseline": False,
                "message": f"No baseline found for {key}"
            }
        
        # Calculate performance difference
        time_diff_percent = ((result.avg_time - baseline.expected_avg_time) / 
                           baseline.expected_avg_time) * 100
        
        throughput_diff_percent = ((result.throughput - baseline.expected_throughput) / 
                                 baseline.expected_throughput) * 100
        
        # Check if within tolerance
        time_within_tolerance = abs(time_diff_percent) <= baseline.tolerance_percent
        throughput_within_tolerance = abs(throughput_diff_percent) <= baseline.tolerance_percent
        
        overall_pass = time_within_tolerance and throughput_within_tolerance
        
        return {
            "has_baseline": True,
            "baseline_name": baseline.name,
            "time_diff_percent": time_diff_percent,
            "throughput_diff_percent": throughput_diff_percent,
            "time_within_tolerance": time_within_tolerance,
            "throughput_within_tolerance": throughput_within_tolerance,
            "overall_pass": overall_pass,
            "tolerance_percent": baseline.tolerance_percent,
            "baseline_avg_time": baseline.expected_avg_time,
            "baseline_throughput": baseline.expected_throughput
        }
    
    def generate_report(self, results: List[BenchmarkResult]) -> Path:
        """Generate comprehensive performance report"""
        logger.info("📊 Generating performance report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"performance_report_{timestamp}.json"
        
        # Generate report data
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "total_benchmarks": len(results),
            "benchmarks": [],
            "summary": {
                "passed_baselines": 0,
                "failed_baselines": 0,
                "no_baseline": 0
            }
        }
        
        for result in results:
            # Compare with baseline
            comparison = self.compare_with_baseline(result)
            
            benchmark_data = {
                "name": result.name,
                "algorithm": result.algorithm,
                "key_size": result.key_size,
                "iterations": result.iterations,
                "total_time": result.total_time,
                "avg_time": result.avg_time,
                "min_time": result.min_time,
                "max_time": result.max_time,
                "median_time": result.median_time,
                "throughput": result.throughput,
                "platform": result.platform,
                "timestamp": result.timestamp,
                "baseline_comparison": comparison,
                "metadata": result.metadata
            }
            
            report_data["benchmarks"].append(benchmark_data)
            
            # Update summary
            if comparison["has_baseline"]:
                if comparison["overall_pass"]:
                    report_data["summary"]["passed_baselines"] += 1
                else:
                    report_data["summary"]["failed_baselines"] += 1
            else:
                report_data["summary"]["no_baseline"] += 1
        
        # Write report
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📊 Performance report generated: {report_path}")
        
        # Print summary
        summary = report_data["summary"]
        logger.info(f"📈 Performance Summary:")
        logger.info(f"   ✅ Passed baselines: {summary['passed_baselines']}")
        logger.info(f"   ❌ Failed baselines: {summary['failed_baselines']}")
        logger.info(f"   ⚠️ No baseline: {summary['no_baseline']}")
        
        return report_path
    
    def save_baseline(self, results: List[BenchmarkResult], baseline_name: str = "current") -> Path:
        """Save current results as new baseline"""
        logger.info(f"💾 Saving baseline: {baseline_name}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        baseline_path = self.results_dir / f"baseline_{baseline_name}_{timestamp}.json"
        
        baseline_data = {
            "name": baseline_name,
            "platform": self.platform,
            "timestamp": datetime.now().isoformat(),
            "baselines": []
        }
        
        for result in results:
            baseline_info = {
                "name": result.name,
                "algorithm": result.algorithm,
                "key_size": result.key_size,
                "expected_avg_time": result.avg_time,
                "expected_throughput": result.throughput,
                "tolerance_percent": 20.0,
                "platform": self.platform,
                "version": "3.5.0",
                "timestamp": result.timestamp
            }
            baseline_data["baselines"].append(baseline_info)
        
        with open(baseline_path, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        logger.info(f"💾 Baseline saved: {baseline_path}")
        return baseline_path

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OpenSSL Performance Benchmark")
    parser.add_argument("--results-dir", type=Path, default=Path("performance_results"),
                       help="Results directory")
    parser.add_argument("--baseline-file", type=Path,
                       help="Baseline file for comparison")
    parser.add_argument("--algorithm", 
                       help="Specific algorithm to benchmark")
    parser.add_argument("--key-size", type=int,
                       help="Specific key size to benchmark")
    parser.add_argument("--iterations", type=int, default=100,
                       help="Number of iterations")
    parser.add_argument("--save-baseline", 
                       help="Save results as baseline with given name")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize benchmark
    benchmark = OpenSSLPerformanceBenchmark(args.results_dir, args.baseline_file)
    
    try:
        if args.algorithm and args.key_size:
            # Run specific benchmark
            result = benchmark.run_benchmark(args.algorithm, args.key_size, args.iterations)
            if result:
                results = [result]
            else:
                logger.error("❌ Benchmark failed")
                sys.exit(1)
        else:
            # Run all benchmarks
            results = benchmark.run_all_benchmarks()
        
        if not results:
            logger.error("❌ No benchmark results")
            sys.exit(1)
        
        # Generate report
        report_path = benchmark.generate_report(results)
        
        # Save baseline if requested
        if args.save_baseline:
            baseline_path = benchmark.save_baseline(results, args.save_baseline)
            logger.info(f"💾 New baseline saved: {baseline_path}")
        
        logger.info(f"🎉 Performance benchmarking completed!")
        logger.info(f"📊 Report: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Benchmarking failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()