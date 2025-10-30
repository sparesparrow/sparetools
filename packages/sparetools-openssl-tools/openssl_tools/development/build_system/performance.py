#!/usr/bin/env python3
"""
Performance analyzer for OpenSSL CI builds.

Analyzes Conan build output and generates performance metrics including
cache hit rates, build times, and package statistics.
"""

import argparse
import json
import sys
from typing import Dict, Any, List


class PerformanceAnalyzer:
    """Analyzes build performance from Conan output."""
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze_build(self, conan_output: Dict[str, Any], build_time: int) -> Dict[str, Any]:
        """Analyze Conan build output and generate performance report."""
        try:
            # Check if packages were downloaded (cache hit) or built
            cache_hit = False
            packages_analyzed = 0
            
            if "installed" in conan_output:
                installed_packages = conan_output.get("installed", [])
                packages_analyzed = len(installed_packages)
                
                # If all packages were "downloaded" not "built", it's a cache hit
                if packages_analyzed > 0:
                    cache_hit = all(
                        pkg.get("binary") == "Download" 
                        for pkg in installed_packages
                    )
            
            # Calculate cache hit rate
            cache_hit_rate = 1.0 if cache_hit else 0.0
            
            # Generate performance report
            report = {
                "status": "success",
                "build_time": build_time,
                "cache_hit": cache_hit,
                "cache_hit_rate": cache_hit_rate,
                "packages_analyzed": packages_analyzed,
                "timestamp": conan_output.get("timestamp", ""),
                "packages": packages_analyzed,
                "performance_metrics": {
                    "build_time_seconds": build_time,
                    "packages_per_second": packages_analyzed / build_time if build_time > 0 else 0,
                    "cache_efficiency": cache_hit_rate,
                    "build_type": "cache_hit" if cache_hit else "full_build"
                }
            }
            
            # Add detailed package analysis if available
            if "installed" in conan_output:
                report["package_details"] = self._analyze_packages(conan_output["installed"])
            
            return report
            
        except Exception as e:
            print(f"Error analyzing build: {e}", file=sys.stderr)
            # Generate minimal report on error
            return {
                "status": "error",
                "build_time": build_time,
                "cache_hit": False,
                "cache_hit_rate": 0.0,
                "packages_analyzed": 0,
                "error": str(e),
                "performance_metrics": {
                    "build_time_seconds": build_time,
                    "packages_per_second": 0,
                    "cache_efficiency": 0.0,
                    "build_type": "error"
                }
            }
    
    def _analyze_packages(self, installed_packages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual package details."""
        package_details = {
            "total_packages": len(installed_packages),
            "downloaded": 0,
            "built": 0,
            "by_binary_type": {},
            "by_package_type": {}
        }
        
        for pkg in installed_packages:
            binary_type = pkg.get("binary", "unknown")
            package_type = pkg.get("type", "unknown")
            
            # Count by binary type
            if binary_type not in package_details["by_binary_type"]:
                package_details["by_binary_type"][binary_type] = 0
            package_details["by_binary_type"][binary_type] += 1
            
            # Count by package type
            if package_type not in package_details["by_package_type"]:
                package_details["by_package_type"][package_type] = 0
            package_details["by_package_type"][package_type] += 1
            
            # Count downloaded vs built
            if binary_type == "Download":
                package_details["downloaded"] += 1
            elif binary_type == "Build":
                package_details["built"] += 1
        
        return package_details
    
    def generate_summary(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from multiple build reports."""
        if not reports:
            return {"error": "No reports to analyze"}
        
        total_builds = len(reports)
        successful_builds = sum(1 for r in reports if r.get("status") == "success")
        failed_builds = total_builds - successful_builds
        
        total_build_time = sum(r.get("build_time", 0) for r in reports)
        average_build_time = total_build_time / total_builds if total_builds > 0 else 0
        
        cache_hits = sum(1 for r in reports if r.get("cache_hit", False))
        cache_hit_rate = cache_hits / total_builds if total_builds > 0 else 0
        
        total_packages = sum(r.get("packages_analyzed", 0) for r in reports)
        average_packages = total_packages / total_builds if total_builds > 0 else 0
        
        return {
            "summary": {
                "total_builds": total_builds,
                "successful_builds": successful_builds,
                "failed_builds": failed_builds,
                "success_rate": successful_builds / total_builds if total_builds > 0 else 0
            },
            "performance": {
                "total_build_time": total_build_time,
                "average_build_time": average_build_time,
                "cache_hits": cache_hits,
                "cache_misses": total_builds - cache_hits,
                "cache_hit_rate": cache_hit_rate,
                "total_packages": total_packages,
                "average_packages": average_packages
            },
            "builds": reports
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze OpenSSL build performance')
    parser.add_argument('--input', required=True, help='Input Conan JSON file')
    parser.add_argument('--output', required=True, help='Output performance report file')
    parser.add_argument('--build-time', type=int, required=True, help='Build time in seconds')
    parser.add_argument('--summary', help='Generate summary from multiple reports (comma-separated files)')
    
    args = parser.parse_args()
    
    try:
        analyzer = PerformanceAnalyzer()
        
        if args.summary:
            # Generate summary from multiple reports
            report_files = args.summary.split(',')
            reports = []
            
            for report_file in report_files:
                try:
                    with open(report_file.strip()) as f:
                        report = json.load(f)
                        reports.append(report)
                except Exception as e:
                    print(f"Error reading {report_file}: {e}", file=sys.stderr)
            
            summary = analyzer.generate_summary(reports)
            
            with open(args.output, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"Summary report generated: {args.output}", file=sys.stderr)
            print(f"Analyzed {len(reports)} build reports", file=sys.stderr)
            
        else:
            # Analyze single build
            with open(args.input) as f:
                conan_output = json.load(f)
            
            report = analyzer.analyze_build(conan_output, args.build_time)
            
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Performance report generated: {args.output}", file=sys.stderr)
            print(f"Build time: {args.build_time}s", file=sys.stderr)
            print(f"Cache hit: {report.get('cache_hit', False)}", file=sys.stderr)
            print(f"Packages analyzed: {report.get('packages_analyzed', 0)}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error analyzing performance: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()