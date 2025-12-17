#!/usr/bin/env python3
"""
Report Generator for SpareTools CI/CD

Generates comprehensive reports from CI/CD pipeline results:
- Build reports (success/failure, timing, artifacts)
- Test reports (coverage, results, trends)
- Security reports (vulnerabilities, compliance)
- Performance reports (build times, resource usage)
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class BuildResult:
    """Represents a single build result."""
    consumer: str
    package: str
    platform: str
    status: str
    duration: float
    timestamp: datetime
    artifacts: List[str]
    errors: List[str]


@dataclass
class TestResult:
    """Represents test execution results."""
    consumer: str
    package: str
    platform: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    coverage_percentage: float
    timestamp: datetime


class ReportGenerator:
    """Generates comprehensive CI/CD reports."""

    def __init__(self, output_dir: str = "./reports", format: str = "html"):
        """Initialize report generator.

        Args:
            output_dir: Directory to save reports
            format: Report format ('html', 'markdown', 'json')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format

    def generate_build_report(self, build_results: List[BuildResult],
                            title: str = "SpareTools Build Report") -> str:
        """Generate build report.

        Args:
            build_results: List of build results
            title: Report title

        Returns:
            Path to generated report
        """
        if self.format == "html":
            return self._generate_build_report_html(build_results, title)
        elif self.format == "markdown":
            return self._generate_build_report_markdown(build_results, title)
        elif self.format == "json":
            return self._generate_build_report_json(build_results, title)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def generate_test_report(self, test_results: List[TestResult],
                           title: str = "SpareTools Test Report") -> str:
        """Generate test report.

        Args:
            test_results: List of test results
            title: Report title

        Returns:
            Path to generated report
        """
        if self.format == "html":
            return self._generate_test_report_html(test_results, title)
        elif self.format == "markdown":
            return self._generate_test_report_markdown(test_results, title)
        elif self.format == "json":
            return self._generate_test_report_json(test_results, title)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def generate_combined_report(self, build_results: List[BuildResult],
                               test_results: List[TestResult],
                               security_results: Optional[Dict[str, Any]] = None,
                               title: str = "SpareTools CI/CD Report") -> str:
        """Generate combined CI/CD report.

        Args:
            build_results: Build results
            test_results: Test results
            security_results: Security scan results
            title: Report title

        Returns:
            Path to generated report
        """
        if self.format == "html":
            return self._generate_combined_report_html(
                build_results, test_results, security_results, title
            )
        elif self.format == "markdown":
            return self._generate_combined_report_markdown(
                build_results, test_results, security_results, title
            )
        else:
            raise ValueError(f"Combined reports only support HTML and Markdown formats")

    def _generate_build_report_html(self, results: List[BuildResult], title: str) -> str:
        """Generate HTML build report."""
        # Calculate statistics
        total_builds = len(results)
        successful_builds = len([r for r in results if r.status == "success"])
        failed_builds = len([r for r in results if r.status == "failed"])
        total_duration = sum(r.duration for r in results)

        # Group by consumer
        consumer_stats = {}
        for result in results:
            consumer = result.consumer
            if consumer not in consumer_stats:
                consumer_stats[consumer] = {"total": 0, "success": 0, "failed": 0, "duration": 0}
            consumer_stats[consumer]["total"] += 1
            consumer_stats[consumer]["duration"] += result.duration
            if result.status == "success":
                consumer_stats[consumer]["success"] += 1
            else:
                consumer_stats[consumer]["failed"] += 1

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; }}
        .success {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-success {{ color: #27ae60; font-weight: bold; }}
        .status-failed {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Builds</h3>
            <p style="font-size: 2em; margin: 0;">{total_builds}</p>
        </div>
        <div class="stat-card">
            <h3>Successful</h3>
            <p class="success" style="font-size: 2em; margin: 0;">{successful_builds}</p>
        </div>
        <div class="stat-card">
            <h3>Failed</h3>
            <p class="failed" style="font-size: 2em; margin: 0;">{failed_builds}</p>
        </div>
        <div class="stat-card">
            <h3>Total Duration</h3>
            <p style="font-size: 1.5em; margin: 0;">{total_duration:.1f}s</p>
        </div>
    </div>

    <h2>Consumer Summary</h2>
    <table>
        <tr>
            <th>Consumer</th>
            <th>Total Builds</th>
            <th>Successful</th>
            <th>Failed</th>
            <th>Average Duration</th>
        </tr>
"""

        for consumer, stats in consumer_stats.items():
            avg_duration = stats["duration"] / stats["total"] if stats["total"] > 0 else 0
            html_content += f"""
        <tr>
            <td>{consumer}</td>
            <td>{stats['total']}</td>
            <td class="success">{stats['success']}</td>
            <td class="failed">{stats['failed']}</td>
            <td>{avg_duration:.1f}s</td>
        </tr>
"""

        html_content += """
    </table>

    <h2>Build Details</h2>
    <table>
        <tr>
            <th>Consumer</th>
            <th>Package</th>
            <th>Platform</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Timestamp</th>
        </tr>
"""

        for result in sorted(results, key=lambda x: x.timestamp, reverse=True):
            status_class = "status-success" if result.status == "success" else "status-failed"
            html_content += f"""
        <tr>
            <td>{result.consumer}</td>
            <td>{result.package}</td>
            <td>{result.platform}</td>
            <td class="{status_class}">{result.status}</td>
            <td>{result.duration:.1f}s</td>
            <td>{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
"""

        html_content += """
    </table>
</body>
</html>
"""

        report_file = self.output_dir / "build-report.html"
        with open(report_file, 'w') as f:
            f.write(html_content)

        return str(report_file)

    def _generate_build_report_markdown(self, results: List[BuildResult], title: str) -> str:
        """Generate Markdown build report."""
        # Calculate statistics
        total_builds = len(results)
        successful_builds = len([r for r in results if r.status == "success"])
        failed_builds = len([r for r in results if r.status == "failed"])
        total_duration = sum(r.duration for r in results)

        markdown_content = f"""# {title}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Builds**: {total_builds}
- **Successful**: {successful_builds} ✅
- **Failed**: {failed_builds} ❌
- **Total Duration**: {total_duration:.1f}s
- **Success Rate**: {(successful_builds/total_builds*100):.1f}%

## Build Details

| Consumer | Package | Platform | Status | Duration | Timestamp |
|----------|---------|----------|--------|----------|-----------|
"""

        for result in sorted(results, key=lambda x: x.timestamp, reverse=True):
            status_emoji = "✅" if result.status == "success" else "❌"
            markdown_content += f"| {result.consumer} | {result.package} | {result.platform} | {status_emoji} {result.status} | {result.duration:.1f}s | {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')} |\n"

        markdown_content += "\n---\n*Report generated by SpareTools CI/CD*"

        report_file = self.output_dir / "build-report.md"
        with open(report_file, 'w') as f:
            f.write(markdown_content)

        return str(report_file)

    def _generate_build_report_json(self, results: List[BuildResult], title: str) -> str:
        """Generate JSON build report."""
        report_data = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_builds": len(results),
                "successful": len([r for r in results if r.status == "success"]),
                "failed": len([r for r in results if r.status == "failed"]),
                "total_duration": sum(r.duration for r in results)
            },
            "builds": [
                {
                    "consumer": r.consumer,
                    "package": r.package,
                    "platform": r.platform,
                    "status": r.status,
                    "duration": r.duration,
                    "timestamp": r.timestamp.isoformat(),
                    "artifacts": r.artifacts,
                    "errors": r.errors
                }
                for r in results
            ]
        }

        report_file = self.output_dir / "build-report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        return str(report_file)

    def _generate_test_report_html(self, results: List[TestResult], title: str) -> str:
        """Generate HTML test report."""
        # Calculate statistics
        total_tests = sum(r.total_tests for r in results)
        passed_tests = sum(r.passed_tests for r in results)
        failed_tests = sum(r.failed_tests for r in results)
        avg_coverage = sum(r.coverage_percentage for r in results) / len(results) if results else 0

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #27ae60; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; }}
        .success {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Tests</h3>
            <p style="font-size: 2em; margin: 0;">{total_tests}</p>
        </div>
        <div class="stat-card">
            <h3>Passed</h3>
            <p class="success" style="font-size: 2em; margin: 0;">{passed_tests}</p>
        </div>
        <div class="stat-card">
            <h3>Failed</h3>
            <p class="failed" style="font-size: 2em; margin: 0;">{failed_tests}</p>
        </div>
        <div class="stat-card">
            <h3>Avg Coverage</h3>
            <p style="font-size: 1.5em; margin: 0;">{avg_coverage:.1f}%</p>
        </div>
    </div>

    <h2>Test Results by Package</h2>
    <table>
        <tr>
            <th>Consumer</th>
            <th>Package</th>
            <th>Platform</th>
            <th>Total Tests</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Coverage</th>
        </tr>
"""

        for result in results:
            html_content += f"""
        <tr>
            <td>{result.consumer}</td>
            <td>{result.package}</td>
            <td>{result.platform}</td>
            <td>{result.total_tests}</td>
            <td class="success">{result.passed_tests}</td>
            <td class="failed">{result.failed_tests}</td>
            <td>{result.coverage_percentage:.1f}%</td>
        </tr>
"""

        html_content += """
    </table>
</body>
</html>
"""

        report_file = self.output_dir / "test-report.html"
        with open(report_file, 'w') as f:
            f.write(html_content)

        return str(report_file)

    def _generate_test_report_markdown(self, results: List[TestResult], title: str) -> str:
        """Generate Markdown test report."""
        total_tests = sum(r.total_tests for r in results)
        passed_tests = sum(r.passed_tests for r in results)
        failed_tests = sum(r.failed_tests for r in results)
        avg_coverage = sum(r.coverage_percentage for r in results) / len(results) if results else 0

        markdown_content = f"""# {title}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Tests**: {total_tests}
- **Passed**: {passed_tests} ✅
- **Failed**: {failed_tests} ❌
- **Average Coverage**: {avg_coverage:.1f}%

## Test Results

| Consumer | Package | Platform | Total | Passed | Failed | Coverage |
|----------|---------|----------|-------|--------|--------|----------|
"""

        for result in results:
            markdown_content += f"| {result.consumer} | {result.package} | {result.platform} | {result.total_tests} | {result.passed_tests} | {result.failed_tests} | {result.coverage_percentage:.1f}% |\n"

        markdown_content += "\n---\n*Report generated by SpareTools CI/CD*"

        report_file = self.output_dir / "test-report.md"
        with open(report_file, 'w') as f:
            f.write(markdown_content)

        return str(report_file)

    def _generate_test_report_json(self, results: List[TestResult], title: str) -> str:
        """Generate JSON test report."""
        report_data = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tests": sum(r.total_tests for r in results),
                "passed_tests": sum(r.passed_tests for r in results),
                "failed_tests": sum(r.failed_tests for r in results),
                "average_coverage": sum(r.coverage_percentage for r in results) / len(results) if results else 0
            },
            "results": [
                {
                    "consumer": r.consumer,
                    "package": r.package,
                    "platform": r.platform,
                    "total_tests": r.total_tests,
                    "passed_tests": r.passed_tests,
                    "failed_tests": r.failed_tests,
                    "coverage_percentage": r.coverage_percentage,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in results
            ]
        }

        report_file = self.output_dir / "test-report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        return str(report_file)

    def _generate_combined_report_html(self, build_results: List[BuildResult],
                                     test_results: List[TestResult],
                                     security_results: Optional[Dict[str, Any]],
                                     title: str) -> str:
        """Generate combined HTML report."""
        # This would combine build, test, and security results into a comprehensive HTML report
        # For brevity, I'll create a simplified version

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #9b59b6; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Build Results</h2>
        <div class="metric">Total Builds: {len(build_results)}</div>
        <div class="metric">Successful: {len([r for r in build_results if r.status == 'success'])}</div>
        <div class="metric">Failed: {len([r for r in build_results if r.status == 'failed'])}</div>
    </div>

    <div class="section">
        <h2>Test Results</h2>
        <div class="metric">Total Tests: {sum(r.total_tests for r in test_results)}</div>
        <div class="metric">Passed: {sum(r.passed_tests for r in test_results)}</div>
        <div class="metric">Coverage: {sum(r.coverage_percentage for r in test_results) / len(test_results):.1f}%</div>
    </div>

    {"<div class=\"section\"><h2>Security Results</h2><pre>" + json.dumps(security_results, indent=2) + "</pre></div>" if security_results else ""}
</body>
</html>
"""

        report_file = self.output_dir / "combined-report.html"
        with open(report_file, 'w') as f:
            f.write(html_content)

        return str(report_file)

    def _generate_combined_report_markdown(self, build_results: List[BuildResult],
                                         test_results: List[TestResult],
                                         security_results: Optional[Dict[str, Any]],
                                         title: str) -> str:
        """Generate combined Markdown report."""
        markdown_content = f"""# {title}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Build Summary
- Total Builds: {len(build_results)}
- Successful: {len([r for r in build_results if r.status == 'success'])}
- Failed: {len([r for r in build_results if r.status == 'failed'])}

## Test Summary
- Total Tests: {sum(r.total_tests for r in test_results)}
- Passed: {sum(r.passed_tests for r in test_results)}
- Average Coverage: {sum(r.coverage_percentage for r in test_results) / len(test_results):.1f}%

"""

        if security_results:
            markdown_content += "## Security Results\n```json\n"
            markdown_content += json.dumps(security_results, indent=2)
            markdown_content += "\n```\n"

        markdown_content += "\n---\n*Report generated by SpareTools CI/CD*"

        report_file = self.output_dir / "combined-report.md"
        with open(report_file, 'w') as f:
            f.write(markdown_content)

        return str(report_file)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate CI/CD reports for SpareTools"
    )

    parser.add_argument(
        "--report-type",
        choices=["build", "test", "combined"],
        default="combined",
        help="Type of report to generate"
    )

    parser.add_argument(
        "--format",
        choices=["html", "markdown", "json"],
        default="html",
        help="Report format"
    )

    parser.add_argument(
        "--output-dir",
        default="./reports",
        help="Output directory for reports"
    )

    parser.add_argument(
        "--title",
        default="SpareTools CI/CD Report",
        help="Report title"
    )

    args = parser.parse_args()

    generator = ReportGenerator(args.output_dir, args.format)

    # For demonstration, create sample data
    # In real usage, this would parse actual CI/CD results

    if args.report_type == "build":
        # Sample build results
        build_results = [
            BuildResult("openssl", "sparetools-openssl", "ubuntu-latest", "success", 45.2,
                       datetime.now(), ["openssl-3.3.2.tar.gz"], []),
            BuildResult("mia", "sparetools-mia", "ubuntu-latest", "success", 23.1,
                       datetime.now(), ["mia-2.0.0.tar.gz"], []),
        ]
        report_path = generator.generate_build_report(build_results, args.title)

    elif args.report_type == "test":
        # Sample test results
        test_results = [
            TestResult("openssl", "sparetools-openssl", "ubuntu-latest", 150, 148, 2, 85.3, datetime.now()),
            TestResult("mia", "sparetools-mia", "ubuntu-latest", 75, 75, 0, 92.1, datetime.now()),
        ]
        report_path = generator.generate_test_report(test_results, args.title)

    elif args.report_type == "combined":
        # Sample combined results
        build_results = [
            BuildResult("openssl", "sparetools-openssl", "ubuntu-latest", "success", 45.2,
                       datetime.now(), ["openssl-3.3.2.tar.gz"], []),
        ]
        test_results = [
            TestResult("openssl", "sparetools-openssl", "ubuntu-latest", 150, 148, 2, 85.3, datetime.now()),
        ]
        security_results = {"vulnerabilities": 0, "compliance": "passed"}

        report_path = generator.generate_combined_report(
            build_results, test_results, security_results, args.title
        )

    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()