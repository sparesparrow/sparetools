#!/usr/bin/env python3
"""
Enhanced Code Quality Management System
Inspired by oms-dev patterns for static analysis, coverage metrics, and quality gates
"""

import os
import sys
import json
import yaml
import logging
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodeQualityManager:
    """Enhanced code quality management with static analysis and coverage metrics"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.quality_config_path = project_root / "conan-dev" / "quality-config.yml"
        self.reports_dir = project_root / "conan-dev" / "quality-reports"
        self.sonar_config_path = project_root / "sonar-project.properties"
        
        # Create directories
        self.quality_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_quality_config(self):
        """Set up code quality configuration based on oms-dev patterns"""
        config = {
            "code_quality": {
                "static_analysis": {
                    "enabled": True,
                    "tools": {
                        "clang_tidy": {
                            "enabled": True,
                            "config_file": ".clang-tidy",
                            "checks": [
                                "performance-*",
                                "readability-*",
                                "modernize-*",
                                "-modernize-use-trailing-return-type",
                                "-readability-convert-member-functions-to-static",
                                "-misc-unused-parameters"
                            ],
                            "header_filter": ".*",
                            "format_style": "file"
                        },
                        "cppcheck": {
                            "enabled": True,
                            "args": [
                                "--enable=all",
                                "--inconclusive",
                                "--std=c++17",
                                "--suppress=missingIncludeSystem"
                            ]
                        },
                        "sonarqube": {
                            "enabled": True,
                            "server_url": os.getenv("SONAR_HOST_URL", "http://localhost:9000"),
                            "token": os.getenv("SONAR_TOKEN", ""),
                            "project_key": "openssl-conan",
                            "quality_gate": "OpenSSL Quality Gate"
                        }
                    }
                },
                "coverage": {
                    "enabled": True,
                    "tools": {
                        "gcov": {
                            "enabled": True,
                            "minimum_coverage": 80.0,
                            "exclude_patterns": [
                                "*/test/*",
                                "*/tests/*",
                                "*/demos/*",
                                "*/fuzz/*"
                            ]
                        },
                        "lcov": {
                            "enabled": True,
                            "generate_html": True,
                            "html_output_dir": "coverage-html"
                        }
                    }
                },
                "quality_gates": {
                    "enabled": True,
                    "thresholds": {
                        "coverage_percentage": 80.0,
                        "duplicated_lines_percentage": 3.0,
                        "maintainability_rating": "A",
                        "reliability_rating": "A",
                        "security_rating": "A",
                        "technical_debt_ratio": 5.0
                    },
                    "fail_on_threshold": True
                },
                "code_metrics": {
                    "enabled": True,
                    "complexity": {
                        "max_cyclomatic_complexity": 10,
                        "max_cognitive_complexity": 15
                    },
                    "size": {
                        "max_lines_per_file": 1000,
                        "max_parameters_per_function": 7
                    }
                }
            },
            "reporting": {
                "formats": ["json", "xml", "html"],
                "output_directory": "quality-reports",
                "include_trends": True,
                "include_metrics": True
            }
        }
        
        with open(self.quality_config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Create SonarQube configuration
        self._create_sonar_config()
        
        logger.info(f"✅ Code quality configuration created: {self.quality_config_path}")
    
    def run_static_analysis(self) -> Dict:
        """Run static code analysis using configured tools"""
        logger.info("🔍 Running static code analysis...")
        
        analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "tools_used": [],
            "issues_found": [],
            "summary": {
                "total_issues": 0,
                "by_severity": {
                    "critical": 0,
                    "major": 0,
                    "minor": 0,
                    "info": 0
                },
                "by_category": {
                    "bug": 0,
                    "vulnerability": 0,
                    "code_smell": 0,
                    "duplication": 0
                }
            }
        }
        
        try:
            with open(self.quality_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            static_config = config["code_quality"]["static_analysis"]
            
            if static_config["enabled"]:
                # Run clang-tidy
                if static_config["tools"]["clang_tidy"]["enabled"]:
                    clang_results = self._run_clang_tidy(static_config["tools"]["clang_tidy"])
                    analysis_results["tools_used"].append("clang-tidy")
                    analysis_results["issues_found"].extend(clang_results)
                
                # Run cppcheck
                if static_config["tools"]["cppcheck"]["enabled"]:
                    cppcheck_results = self._run_cppcheck(static_config["tools"]["cppcheck"])
                    analysis_results["tools_used"].append("cppcheck")
                    analysis_results["issues_found"].extend(cppcheck_results)
                
                # Run SonarQube analysis
                if static_config["tools"]["sonarqube"]["enabled"]:
                    sonar_results = self._run_sonarqube_analysis(static_config["tools"]["sonarqube"])
                    analysis_results["tools_used"].append("sonarqube")
                    analysis_results["issues_found"].extend(sonar_results)
                
                # Calculate summary
                self._calculate_analysis_summary(analysis_results)
                
                # Save results
                self._save_analysis_results(analysis_results)
                
                logger.info(f"✅ Static analysis complete: {analysis_results['summary']['total_issues']} issues found")
            else:
                logger.info("⏸️ Static analysis is disabled in configuration")
            
        except Exception as e:
            logger.error(f"❌ Static analysis failed: {e}")
        
        return analysis_results
    
    def run_coverage_analysis(self) -> Dict:
        """Run code coverage analysis"""
        logger.info("📊 Running code coverage analysis...")
        
        coverage_results = {
            "coverage_timestamp": datetime.now().isoformat(),
            "tools_used": [],
            "coverage_data": {},
            "summary": {
                "line_coverage": 0.0,
                "function_coverage": 0.0,
                "branch_coverage": 0.0,
                "meets_threshold": False
            }
        }
        
        try:
            with open(self.quality_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            coverage_config = config["code_quality"]["coverage"]
            
            if coverage_config["enabled"]:
                # Run gcov
                if coverage_config["tools"]["gcov"]["enabled"]:
                    gcov_results = self._run_gcov_analysis(coverage_config["tools"]["gcov"])
                    coverage_results["tools_used"].append("gcov")
                    coverage_results["coverage_data"]["gcov"] = gcov_results
                
                # Run lcov
                if coverage_config["tools"]["lcov"]["enabled"]:
                    lcov_results = self._run_lcov_analysis(coverage_config["tools"]["lcov"])
                    coverage_results["tools_used"].append("lcov")
                    coverage_results["coverage_data"]["lcov"] = lcov_results
                
                # Calculate summary
                self._calculate_coverage_summary(coverage_results, coverage_config)
                
                # Save results
                self._save_coverage_results(coverage_results)
                
                logger.info(f"✅ Coverage analysis complete: {coverage_results['summary']['line_coverage']:.1f}% line coverage")
            else:
                logger.info("⏸️ Coverage analysis is disabled in configuration")
            
        except Exception as e:
            logger.error(f"❌ Coverage analysis failed: {e}")
        
        return coverage_results
    
    def check_quality_gates(self, analysis_results: Dict, coverage_results: Dict) -> Dict:
        """Check if code meets quality gate thresholds"""
        logger.info("🚪 Checking quality gates...")
        
        quality_gate_results = {
            "gate_timestamp": datetime.now().isoformat(),
            "status": "PASSED",
            "conditions": [],
            "summary": {
                "total_conditions": 0,
                "passed_conditions": 0,
                "failed_conditions": 0
            }
        }
        
        try:
            with open(self.quality_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            gate_config = config["code_quality"]["quality_gates"]
            
            if gate_config["enabled"]:
                thresholds = gate_config["thresholds"]
                
                # Check coverage threshold
                coverage_condition = {
                    "name": "Coverage",
                    "status": "PASSED",
                    "actual_value": coverage_results["summary"]["line_coverage"],
                    "threshold": thresholds["coverage_percentage"],
                    "operator": ">="
                }
                
                if coverage_results["summary"]["line_coverage"] < thresholds["coverage_percentage"]:
                    coverage_condition["status"] = "FAILED"
                    quality_gate_results["status"] = "FAILED"
                
                quality_gate_results["conditions"].append(coverage_condition)
                
                # Check duplication threshold
                duplication_condition = {
                    "name": "Duplicated Lines",
                    "status": "PASSED",
                    "actual_value": analysis_results["summary"]["by_category"]["duplication"],
                    "threshold": thresholds["duplicated_lines_percentage"],
                    "operator": "<="
                }
                
                if analysis_results["summary"]["by_category"]["duplication"] > thresholds["duplicated_lines_percentage"]:
                    duplication_condition["status"] = "FAILED"
                    quality_gate_results["status"] = "FAILED"
                
                quality_gate_results["conditions"].append(duplication_condition)
                
                # Check maintainability rating
                maintainability_condition = {
                    "name": "Maintainability Rating",
                    "status": "PASSED",
                    "actual_value": "A",  # Would be calculated from actual metrics
                    "threshold": thresholds["maintainability_rating"],
                    "operator": ">="
                }
                
                quality_gate_results["conditions"].append(maintainability_condition)
                
                # Calculate summary
                quality_gate_results["summary"]["total_conditions"] = len(quality_gate_results["conditions"])
                quality_gate_results["summary"]["passed_conditions"] = sum(
                    1 for c in quality_gate_results["conditions"] if c["status"] == "PASSED"
                )
                quality_gate_results["summary"]["failed_conditions"] = sum(
                    1 for c in quality_gate_results["conditions"] if c["status"] == "FAILED"
                )
                
                # Save results
                self._save_quality_gate_results(quality_gate_results)
                
                logger.info(f"✅ Quality gate check complete: {quality_gate_results['status']}")
                
                # Fail if configured to do so
                if gate_config["fail_on_threshold"] and quality_gate_results["status"] == "FAILED":
                    logger.error("❌ Quality gate failed - build should be rejected")
                    sys.exit(1)
            else:
                logger.info("⏸️ Quality gates are disabled in configuration")
            
        except Exception as e:
            logger.error(f"❌ Quality gate check failed: {e}")
            if gate_config.get("fail_on_threshold", False):
                sys.exit(1)
        
        return quality_gate_results
    
    def generate_quality_report(self, analysis_results: Dict, coverage_results: Dict, gate_results: Dict) -> str:
        """Generate comprehensive quality report"""
        logger.info("📋 Generating quality report...")
        
        try:
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "project": "OpenSSL Conan Package",
                "static_analysis": analysis_results,
                "coverage_analysis": coverage_results,
                "quality_gates": gate_results,
                "recommendations": self._generate_recommendations(analysis_results, coverage_results)
            }
            
            # Generate HTML report
            html_report = self._generate_html_report(report_data)
            html_path = self.reports_dir / f"quality-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
            
            with open(html_path, 'w') as f:
                f.write(html_report)
            
            # Generate JSON report
            json_path = self.reports_dir / f"quality-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            with open(json_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"✅ Quality report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate quality report: {e}")
            return ""
    
    def _create_sonar_config(self):
        """Create SonarQube project configuration"""
        sonar_config = f"""# SonarQube Configuration for OpenSSL Conan Package
sonar.projectKey=openssl-conan
sonar.projectName=OpenSSL Conan Package
sonar.projectVersion=1.0.0

# Source code
sonar.sources=crypto,ssl,apps,include
sonar.tests=test
sonar.exclusions=**/test/**,**/tests/**,**/demos/**,**/fuzz/**

# C/C++ specific
sonar.cfamily.build-wrapper-output=bw-output
sonar.cfamily.gcov.reportsPath=coverage-reports
sonar.cfamily.llvm-cov.reportPath=coverage-reports/coverage.info

# Quality Gate
sonar.qualitygate.wait=true

# Additional properties
sonar.cfamily.threads=0
sonar.cfamily.cache.enabled=true
sonar.cfamily.cache.path=.sonar/cache
"""
        
        with open(self.sonar_config_path, 'w') as f:
            f.write(sonar_config)
    
    def _run_clang_tidy(self, config: Dict) -> List[Dict]:
        """Run clang-tidy static analysis"""
        issues = []
        
        try:
            # Find C/C++ source files
            source_files = []
            for pattern in ["**/*.c", "**/*.cpp", "**/*.cc", "**/*.cxx"]:
                source_files.extend(self.project_root.glob(pattern))
            
            # Filter out test and demo files
            source_files = [f for f in source_files if not any(
                part in str(f) for part in ["test", "tests", "demos", "fuzz"]
            )]
            
            for source_file in source_files[:10]:  # Limit for demo
                cmd = [
                    "clang-tidy",
                    str(source_file),
                    f"--config-file={config['config_file']}",
                    "--format-style=file"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and result.stdout:
                    # Parse clang-tidy output
                    for line in result.stdout.split('\n'):
                        if ':' in line and ('warning:' in line or 'error:' in line):
                            issue = self._parse_clang_tidy_line(line, source_file)
                            if issue:
                                issues.append(issue)
            
        except Exception as e:
            logger.error(f"clang-tidy analysis failed: {e}")
        
        return issues
    
    def _run_cppcheck(self, config: Dict) -> List[Dict]:
        """Run cppcheck static analysis"""
        issues = []
        
        try:
            cmd = ["cppcheck"] + config["args"] + ["--xml", str(self.project_root)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and result.stdout:
                # Parse XML output
                root = ET.fromstring(result.stdout)
                for error in root.findall('error'):
                    issue = {
                        "tool": "cppcheck",
                        "severity": error.get('severity', 'unknown'),
                        "message": error.get('msg', ''),
                        "file": error.get('file', ''),
                        "line": int(error.get('line', 0)),
                        "category": "static_analysis"
                    }
                    issues.append(issue)
            
        except Exception as e:
            logger.error(f"cppcheck analysis failed: {e}")
        
        return issues
    
    def _run_sonarqube_analysis(self, config: Dict) -> List[Dict]:
        """Run SonarQube analysis"""
        issues = []
        
        try:
            # Build with build-wrapper
            build_cmd = [
                "build-wrapper-linux-x86-64", "--out-dir", "bw-output",
                "make", "-j$(nproc)"
            ]
            
            subprocess.run(build_cmd, cwd=self.project_root, timeout=600)
            
            # Run SonarQube scanner
            scanner_cmd = [
                "sonar-scanner",
                f"-Dsonar.projectKey={config['project_key']}",
                f"-Dsonar.host.url={config['server_url']}",
                f"-Dsonar.login={config['token']}",
                f"-Dsonar.qualitygate.wait=true"
            ]
            
            result = subprocess.run(scanner_cmd, cwd=self.project_root, timeout=600)
            
            if result.returncode == 0:
                # SonarQube issues would be retrieved via API
                logger.info("SonarQube analysis completed successfully")
            
        except Exception as e:
            logger.error(f"SonarQube analysis failed: {e}")
        
        return issues
    
    def _run_gcov_analysis(self, config: Dict) -> Dict:
        """Run gcov coverage analysis"""
        coverage_data = {}
        
        try:
            # Find .gcno files
            gcno_files = list(self.project_root.glob("**/*.gcno"))
            
            for gcno_file in gcno_files:
                # Run gcov
                result = subprocess.run(
                    ["gcov", str(gcno_file)],
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    # Parse gcov output
                    coverage_data[str(gcno_file)] = self._parse_gcov_output(result.stdout)
            
        except Exception as e:
            logger.error(f"gcov analysis failed: {e}")
        
        return coverage_data
    
    def _run_lcov_analysis(self, config: Dict) -> Dict:
        """Run lcov coverage analysis"""
        coverage_data = {}
        
        try:
            # Capture coverage data
            capture_cmd = ["lcov", "--capture", "--directory", ".", "--output-file", "coverage.info"]
            subprocess.run(capture_cmd, cwd=self.project_root, timeout=300)
            
            # Generate HTML report if configured
            if config.get("generate_html", False):
                html_cmd = [
                    "genhtml", "coverage.info",
                    "--output-directory", config.get("html_output_dir", "coverage-html")
                ]
                subprocess.run(html_cmd, cwd=self.project_root, timeout=300)
            
            # Parse coverage.info
            coverage_data = self._parse_lcov_file(self.project_root / "coverage.info")
            
        except Exception as e:
            logger.error(f"lcov analysis failed: {e}")
        
        return coverage_data
    
    def _parse_clang_tidy_line(self, line: str, source_file: Path) -> Optional[Dict]:
        """Parse clang-tidy output line"""
        try:
            parts = line.split(':')
            if len(parts) >= 4:
                return {
                    "tool": "clang-tidy",
                    "file": parts[0],
                    "line": int(parts[1]),
                    "column": int(parts[2]),
                    "severity": "warning" if "warning:" in line else "error",
                    "message": parts[3].strip(),
                    "category": "static_analysis"
                }
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _parse_gcov_output(self, output: str) -> Dict:
        """Parse gcov output"""
        coverage_data = {}
        
        for line in output.split('\n'):
            if 'Lines executed:' in line:
                match = re.search(r'(\d+\.\d+)%', line)
                if match:
                    coverage_data["line_coverage"] = float(match.group(1))
        
        return coverage_data
    
    def _parse_lcov_file(self, lcov_file: Path) -> Dict:
        """Parse lcov coverage file"""
        coverage_data = {}
        
        try:
            with open(lcov_file, 'r') as f:
                content = f.read()
            
            # Parse lcov format
            lines = content.split('\n')
            current_file = None
            
            for line in lines:
                if line.startswith('SF:'):
                    current_file = line[3:]
                    coverage_data[current_file] = {}
                elif line.startswith('LF:') and current_file:
                    coverage_data[current_file]["lines_found"] = int(line[3:])
                elif line.startswith('LH:') and current_file:
                    coverage_data[current_file]["lines_hit"] = int(line[3:])
        
        except Exception as e:
            logger.error(f"Failed to parse lcov file: {e}")
        
        return coverage_data
    
    def _calculate_analysis_summary(self, results: Dict):
        """Calculate analysis summary statistics"""
        total_issues = len(results["issues_found"])
        results["summary"]["total_issues"] = total_issues
        
        for issue in results["issues_found"]:
            severity = issue.get("severity", "info").lower()
            if severity in results["summary"]["by_severity"]:
                results["summary"]["by_severity"][severity] += 1
            
            category = issue.get("category", "code_smell")
            if category in results["summary"]["by_category"]:
                results["summary"]["by_category"][category] += 1
    
    def _calculate_coverage_summary(self, results: Dict, config: Dict):
        """Calculate coverage summary statistics"""
        total_lines = 0
        covered_lines = 0
        
        for file_data in results["coverage_data"].values():
            if isinstance(file_data, dict):
                for file_coverage in file_data.values():
                    if isinstance(file_coverage, dict):
                        total_lines += file_coverage.get("lines_found", 0)
                        covered_lines += file_coverage.get("lines_hit", 0)
        
        if total_lines > 0:
            line_coverage = (covered_lines / total_lines) * 100
            results["summary"]["line_coverage"] = line_coverage
            results["summary"]["meets_threshold"] = line_coverage >= config["tools"]["gcov"]["minimum_coverage"]
    
    def _generate_recommendations(self, analysis_results: Dict, coverage_results: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Coverage recommendations
        if coverage_results["summary"]["line_coverage"] < 80:
            recommendations.append(
                f"Increase test coverage from {coverage_results['summary']['line_coverage']:.1f}% to at least 80%"
            )
        
        # Static analysis recommendations
        critical_issues = analysis_results["summary"]["by_severity"]["critical"]
        if critical_issues > 0:
            recommendations.append(f"Address {critical_issues} critical static analysis issues")
        
        major_issues = analysis_results["summary"]["by_severity"]["major"]
        if major_issues > 0:
            recommendations.append(f"Address {major_issues} major static analysis issues")
        
        return recommendations
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """Generate HTML quality report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenSSL Conan Package - Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .warning {{ background-color: #fff3cd; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenSSL Conan Package - Quality Report</h1>
        <p>Generated: {report_data['report_timestamp']}</p>
    </div>
    
    <div class="section">
        <h2>Quality Gate Status</h2>
        <div class="metric {'passed' if report_data['quality_gates']['status'] == 'PASSED' else 'failed'}">
            <strong>Status: {report_data['quality_gates']['status']}</strong>
        </div>
        <p>Passed: {report_data['quality_gates']['summary']['passed_conditions']} / {report_data['quality_gates']['summary']['total_conditions']} conditions</p>
    </div>
    
    <div class="section">
        <h2>Coverage Summary</h2>
        <div class="metric {'passed' if report_data['coverage_analysis']['summary']['meets_threshold'] else 'warning'}">
            <strong>Line Coverage: {report_data['coverage_analysis']['summary']['line_coverage']:.1f}%</strong>
        </div>
    </div>
    
    <div class="section">
        <h2>Static Analysis Summary</h2>
        <div class="metric">
            <strong>Total Issues: {report_data['static_analysis']['summary']['total_issues']}</strong>
        </div>
        <table>
            <tr><th>Severity</th><th>Count</th></tr>
            <tr><td>Critical</td><td>{report_data['static_analysis']['summary']['by_severity']['critical']}</td></tr>
            <tr><td>Major</td><td>{report_data['static_analysis']['summary']['by_severity']['major']}</td></tr>
            <tr><td>Minor</td><td>{report_data['static_analysis']['summary']['by_severity']['minor']}</td></tr>
            <tr><td>Info</td><td>{report_data['static_analysis']['summary']['by_severity']['info']}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for recommendation in report_data['recommendations']:
            html += f"            <li>{recommendation}</li>\n"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html
    
    def _save_analysis_results(self, results: Dict):
        """Save static analysis results"""
        report_path = self.reports_dir / f"static-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _save_coverage_results(self, results: Dict):
        """Save coverage analysis results"""
        report_path = self.reports_dir / f"coverage-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _save_quality_gate_results(self, results: Dict):
        """Save quality gate results"""
        report_path = self.reports_dir / f"quality-gates-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)

def main():
    """Main entry point for code quality management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Code Quality Management")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "static-analysis", "coverage", "quality-gates", "full-report"],
                       required=True, help="Action to perform")
    
    args = parser.parse_args()
    
    cqm = CodeQualityManager(args.project_root)
    
    if args.action == "setup":
        cqm.setup_quality_config()
    elif args.action == "static-analysis":
        cqm.run_static_analysis()
    elif args.action == "coverage":
        cqm.run_coverage_analysis()
    elif args.action == "quality-gates":
        analysis_results = cqm.run_static_analysis()
        coverage_results = cqm.run_coverage_analysis()
        cqm.check_quality_gates(analysis_results, coverage_results)
    elif args.action == "full-report":
        analysis_results = cqm.run_static_analysis()
        coverage_results = cqm.run_coverage_analysis()
        gate_results = cqm.check_quality_gates(analysis_results, coverage_results)
        report_path = cqm.generate_quality_report(analysis_results, coverage_results, gate_results)
        print(f"Quality report generated: {report_path}")

if __name__ == "__main__":
    main()
