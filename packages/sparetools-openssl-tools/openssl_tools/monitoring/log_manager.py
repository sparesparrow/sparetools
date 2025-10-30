#!/usr/bin/env python3
"""
Log Whitelist Management System
Inspired by oms-dev patterns for deterministic CI logs and noise filtering
"""

import os
import sys
import json
import yaml
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import fnmatch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LogWhitelistManager:
    """Log whitelist management system based on oms-dev patterns"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.whitelist_config_path = project_root / "conan-dev" / "log-whitelist.yml"
        self.log_filters_dir = project_root / "scripts" / "logging"
        self.reports_dir = project_root / "conan-dev" / "log-reports"
        
        # Create directories
        self.whitelist_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_filters_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_log_whitelist_config(self):
        """Set up log whitelist configuration based on oms-dev patterns"""
        config = {
            "log_whitelist": {
                "enabled": True,
                "deterministic_logs": True,
                "signal_real_faults": True,
                "documented_filters": True,
                "log_whitelist_faults": [
                    "SW_INTERNAL_WARNING",
                    "INFO",
                    "DEBUG"
                ],
                "log_whitelist_full_faults": [
                    "2003 SW_CAS_MASTER_DATA_VALIDITY_FAULT .* Cas master is not running",
                    "2003 SW_CAS_MASTER_DATA_VALIDITY_FAULT .* At least one of CAS Master signals is invalid",
                    "1026 SW_INTERNAL_EXCEPTION_FAULT .* PCC Channels are not available during ASE runtime",
                    "1029 SW_INTERNAL_EXCEPTION_FAULT .* MS CMCF2 ContId not found!",
                    "1002 SW_INTERNAL_EXCEPTION_FAULT .* FlexiHandleFactory::createReadFlexiHandle  unknown parameterData type",
                    "1003 SW_DB_LOAD_FAULT .* Pdb Db does not exist",
                    "1003 SW_DB_LOAD_FAULT .* Hdb Db does not exist"
                ],
                "log_whitelist_regex_faults": [
                    "1000 SW_SLDB_LDI_RESOLUTION_FAULT \\(.+\\) Missing static equation Id [\\d]+",
                    "^(INFO)",
                    "^(DEBUG)",
                    ".*\\[INFO\\].*",
                    ".*\\[DEBUG\\].*"
                ],
                "openssl_specific_filters": {
                    "crypto_traces": [
                        ".*crypto.*INFO.*",
                        ".*crypto.*DEBUG.*"
                    ],
                    "provider_tests": [
                        ".*provider.*INFO.*",
                        ".*provider.*DEBUG.*"
                    ],
                    "fips_validation": [
                        ".*FIPS.*INFO.*",
                        ".*FIPS.*DEBUG.*"
                    ]
                },
                "security_filters": {
                    "never_whitelist": [
                        ".*memory corruption.*",
                        ".*failed verification.*",
                        ".*RNG failures.*",
                        ".*FIPS violations.*",
                        ".*security.*error.*",
                        ".*vulnerability.*"
                    ]
                }
            },
            "ci_integration": {
                "filter_logs_before_assertion": True,
                "track_suppressed_lines": True,
                "fail_on_new_patterns": True,
                "opt_in_mode": True
            },
            "monitoring": {
                "collect_filter_metrics": True,
                "track_whitelist_drift": True,
                "generate_filter_reports": True
            }
        }
        
        with open(self.whitelist_config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Create filter utility
        self._create_filter_utility()
        
        logger.info(f"✅ Log whitelist configuration created: {self.whitelist_config_path}")
    
    def filter_logs(self, log_file_path: Path, output_path: Optional[Path] = None) -> Dict:
        """Filter logs using whitelist patterns"""
        logger.info(f"🔍 Filtering logs: {log_file_path}")
        
        filter_results = {
            "filter_timestamp": datetime.now().isoformat(),
            "input_file": str(log_file_path),
            "output_file": str(output_path) if output_path else "",
            "total_lines": 0,
            "filtered_lines": 0,
            "suppressed_lines": 0,
            "suppressed_patterns": {},
            "new_patterns": [],
            "security_violations": []
        }
        
        try:
            with open(self.whitelist_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config["log_whitelist"]["enabled"]:
                logger.info("⏸️ Log filtering is disabled")
                return filter_results
            
            # Load whitelist patterns
            whitelist_patterns = self._load_whitelist_patterns(config)
            
            # Process log file
            filtered_lines = []
            suppressed_count = 0
            suppressed_patterns = {}
            new_patterns = []
            security_violations = []
            
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    filter_results["total_lines"] += 1
                    
                    # Check for security violations first
                    if self._check_security_violations(line, config):
                        security_violations.append({
                            "line_number": line_num,
                            "line": line.strip(),
                            "violation_type": "security_related"
                        })
                        continue
                    
                    # Check if line should be filtered
                    should_filter, matched_pattern = self._should_filter_line(line, whitelist_patterns)
                    
                    if should_filter:
                        suppressed_count += 1
                        if matched_pattern:
                            if matched_pattern not in suppressed_patterns:
                                suppressed_patterns[matched_pattern] = 0
                            suppressed_patterns[matched_pattern] += 1
                    else:
                        filtered_lines.append(line)
                        
                        # Check for new patterns (opt-in mode)
                        if config["ci_integration"]["fail_on_new_patterns"] and config["ci_integration"]["opt_in_mode"]:
                            new_pattern = self._detect_new_pattern(line)
                            if new_pattern:
                                new_patterns.append({
                                    "line_number": line_num,
                                    "pattern": new_pattern,
                                    "line": line.strip()
                                })
            
            # Update results
            filter_results["filtered_lines"] = len(filtered_lines)
            filter_results["suppressed_lines"] = suppressed_count
            filter_results["suppressed_patterns"] = suppressed_patterns
            filter_results["new_patterns"] = new_patterns
            filter_results["security_violations"] = security_violations
            
            # Write filtered output
            if output_path:
                with open(output_path, 'w') as f:
                    f.writelines(filtered_lines)
                filter_results["output_file"] = str(output_path)
            
            # Save filter metrics
            self._save_filter_metrics(filter_results)
            
            # Check for new patterns
            if new_patterns and config["ci_integration"]["fail_on_new_patterns"]:
                logger.warning(f"⚠️ {len(new_patterns)} new log patterns detected")
                self._report_new_patterns(new_patterns)
            
            # Check for security violations
            if security_violations:
                logger.error(f"🚨 {len(security_violations)} security-related log entries found")
                self._report_security_violations(security_violations)
            
            logger.info(f"✅ Log filtering complete: {suppressed_count}/{filter_results['total_lines']} lines suppressed")
            
        except Exception as e:
            logger.error(f"❌ Log filtering failed: {e}")
        
        return filter_results
    
    def validate_whitelist_patterns(self) -> Dict:
        """Validate whitelist patterns for correctness"""
        logger.info("🔍 Validating whitelist patterns...")
        
        validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_patterns": 0,
            "valid_patterns": 0,
            "invalid_patterns": [],
            "duplicate_patterns": [],
            "conflicting_patterns": []
        }
        
        try:
            with open(self.whitelist_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            whitelist_patterns = self._load_whitelist_patterns(config)
            validation_results["total_patterns"] = len(whitelist_patterns)
            
            # Validate each pattern
            for pattern_type, patterns in whitelist_patterns.items():
                for pattern in patterns:
                    if self._validate_pattern(pattern, pattern_type):
                        validation_results["valid_patterns"] += 1
                    else:
                        validation_results["invalid_patterns"].append({
                            "pattern": pattern,
                            "type": pattern_type,
                            "error": "Invalid regex or pattern"
                        })
            
            # Check for duplicates
            all_patterns = []
            for patterns in whitelist_patterns.values():
                all_patterns.extend(patterns)
            
            seen_patterns = set()
            for pattern in all_patterns:
                if pattern in seen_patterns:
                    validation_results["duplicate_patterns"].append(pattern)
                else:
                    seen_patterns.add(pattern)
            
            # Check for conflicts
            validation_results["conflicting_patterns"] = self._check_pattern_conflicts(whitelist_patterns)
            
            # Save validation results
            self._save_validation_results(validation_results)
            
            logger.info(f"✅ Pattern validation complete: {validation_results['valid_patterns']}/{validation_results['total_patterns']} patterns valid")
            
        except Exception as e:
            logger.error(f"❌ Pattern validation failed: {e}")
        
        return validation_results
    
    def generate_whitelist_report(self) -> str:
        """Generate comprehensive whitelist report"""
        logger.info("📋 Generating whitelist report...")
        
        try:
            with open(self.whitelist_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Collect metrics
            metrics = self._collect_whitelist_metrics()
            
            # Generate report data
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "configuration": config,
                "metrics": metrics,
                "recommendations": self._generate_whitelist_recommendations(config, metrics)
            }
            
            # Generate HTML report
            html_report = self._generate_whitelist_html_report(report_data)
            html_path = self.reports_dir / f"whitelist-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
            
            with open(html_path, 'w') as f:
                f.write(html_report)
            
            # Generate JSON report
            json_path = self.reports_dir / f"whitelist-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            with open(json_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"✅ Whitelist report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate whitelist report: {e}")
            return ""
    
    def _load_whitelist_patterns(self, config: Dict) -> Dict[str, List[str]]:
        """Load whitelist patterns from configuration"""
        patterns = {}
        
        whitelist_config = config["log_whitelist"]
        
        # Fixed message patterns
        patterns["fixed_faults"] = whitelist_config.get("log_whitelist_faults", [])
        
        # Full message patterns
        patterns["full_faults"] = whitelist_config.get("log_whitelist_full_faults", [])
        
        # Regex patterns
        patterns["regex_faults"] = whitelist_config.get("log_whitelist_regex_faults", [])
        
        # OpenSSL specific patterns
        openssl_patterns = whitelist_config.get("openssl_specific_filters", {})
        for category, category_patterns in openssl_patterns.items():
            patterns[f"openssl_{category}"] = category_patterns
        
        return patterns
    
    def _should_filter_line(self, line: str, whitelist_patterns: Dict[str, List[str]]) -> Tuple[bool, Optional[str]]:
        """Check if line should be filtered based on whitelist patterns"""
        line = line.strip()
        
        # Check fixed message patterns
        for pattern in whitelist_patterns.get("fixed_faults", []):
            if pattern in line:
                return True, f"fixed:{pattern}"
        
        # Check full message patterns
        for pattern in whitelist_patterns.get("full_faults", []):
            if pattern in line:
                return True, f"full:{pattern}"
        
        # Check regex patterns
        for pattern in whitelist_patterns.get("regex_faults", []):
            try:
                if re.search(pattern, line):
                    return True, f"regex:{pattern}"
            except re.error:
                logger.warning(f"Invalid regex pattern: {pattern}")
        
        # Check OpenSSL specific patterns
        for category, patterns in whitelist_patterns.items():
            if category.startswith("openssl_"):
                for pattern in patterns:
                    try:
                        if re.search(pattern, line):
                            return True, f"{category}:{pattern}"
                    except re.error:
                        logger.warning(f"Invalid regex pattern: {pattern}")
        
        return False, None
    
    def _check_security_violations(self, line: str, config: Dict) -> bool:
        """Check if line contains security-related content that should never be whitelisted"""
        security_patterns = config["log_whitelist"]["security_filters"]["never_whitelist"]
        
        for pattern in security_patterns:
            try:
                if re.search(pattern, line, re.IGNORECASE):
                    return True
            except re.error:
                logger.warning(f"Invalid security pattern: {pattern}")
        
        return False
    
    def _detect_new_pattern(self, line: str) -> Optional[str]:
        """Detect new log patterns that might need whitelisting"""
        # Simple pattern detection - in real implementation, this would be more sophisticated
        line = line.strip()
        
        # Look for common log patterns
        if re.match(r'^\d{4}-\d{2}-\d{2}', line):  # Timestamp
            return "timestamp_pattern"
        elif re.match(r'^\[.*\]', line):  # Bracket format
            return "bracket_format"
        elif re.match(r'^\w+:\s', line):  # Category format
            return "category_format"
        
        return None
    
    def _validate_pattern(self, pattern: str, pattern_type: str) -> bool:
        """Validate a whitelist pattern"""
        if pattern_type in ["regex_faults", "openssl_crypto_traces", "openssl_provider_tests", "openssl_fips_validation"]:
            try:
                re.compile(pattern)
                return True
            except re.error:
                return False
        else:
            # For fixed and full patterns, just check they're not empty
            return bool(pattern.strip())
    
    def _check_pattern_conflicts(self, whitelist_patterns: Dict[str, List[str]]) -> List[Dict]:
        """Check for conflicting patterns"""
        conflicts = []
        
        # Check for overlapping patterns
        all_patterns = []
        for pattern_type, patterns in whitelist_patterns.items():
            for pattern in patterns:
                all_patterns.append((pattern, pattern_type))
        
        for i, (pattern1, type1) in enumerate(all_patterns):
            for j, (pattern2, type2) in enumerate(all_patterns[i+1:], i+1):
                if self._patterns_conflict(pattern1, pattern2):
                    conflicts.append({
                        "pattern1": pattern1,
                        "type1": type1,
                        "pattern2": pattern2,
                        "type2": type2,
                        "conflict_type": "overlapping"
                    })
        
        return conflicts
    
    def _patterns_conflict(self, pattern1: str, pattern2: str) -> bool:
        """Check if two patterns conflict"""
        # Simple conflict detection - in real implementation, this would be more sophisticated
        if pattern1 == pattern2:
            return True
        
        # Check if one pattern is a subset of another
        if pattern1 in pattern2 or pattern2 in pattern1:
            return True
        
        return False
    
    def _collect_whitelist_metrics(self) -> Dict:
        """Collect whitelist usage metrics"""
        metrics = {
            "total_patterns": 0,
            "pattern_categories": {},
            "recent_usage": {},
            "effectiveness": {}
        }
        
        try:
            # Load configuration
            with open(self.whitelist_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            whitelist_patterns = self._load_whitelist_patterns(config)
            
            # Count patterns by category
            for category, patterns in whitelist_patterns.items():
                metrics["pattern_categories"][category] = len(patterns)
                metrics["total_patterns"] += len(patterns)
            
            # Load recent filter metrics if available
            metrics_files = list(self.reports_dir.glob("filter-metrics-*.json"))
            if metrics_files:
                latest_metrics_file = max(metrics_files, key=lambda f: f.stat().st_mtime)
                with open(latest_metrics_file, 'r') as f:
                    recent_metrics = json.load(f)
                    metrics["recent_usage"] = recent_metrics.get("suppressed_patterns", {})
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
        
        return metrics
    
    def _generate_whitelist_recommendations(self, config: Dict, metrics: Dict) -> List[str]:
        """Generate recommendations for whitelist improvement"""
        recommendations = []
        
        # Check for unused patterns
        if metrics.get("recent_usage"):
            for category, patterns in config["log_whitelist"].items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if pattern not in metrics["recent_usage"]:
                            recommendations.append(f"Consider removing unused pattern: {pattern}")
        
        # Check for too many patterns
        total_patterns = metrics.get("total_patterns", 0)
        if total_patterns > 100:
            recommendations.append("Consider consolidating whitelist patterns - too many patterns may indicate over-filtering")
        
        # Check for missing security patterns
        security_patterns = config["log_whitelist"]["security_filters"]["never_whitelist"]
        if len(security_patterns) < 5:
            recommendations.append("Consider adding more security-related patterns to never-whitelist")
        
        return recommendations
    
    def _generate_whitelist_html_report(self, report_data: Dict) -> str:
        """Generate HTML report for whitelist analysis"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Log Whitelist Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }}
        .pattern-category {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Log Whitelist Report</h1>
        <p>Generated: {report_data['report_timestamp']}</p>
    </div>
    
    <div class="section">
        <h2>Pattern Summary</h2>
        <div class="metric">
            <strong>Total Patterns: {report_data['metrics']['total_patterns']}</strong>
        </div>
    </div>
    
    <div class="section">
        <h2>Pattern Categories</h2>
"""
        
        for category, count in report_data['metrics']['pattern_categories'].items():
            html += f"""
        <div class="pattern-category">
            <strong>{category}:</strong> {count} patterns
        </div>
"""
        
        html += """
    </div>
    
    <div class="section">
        <h2>Recent Usage</h2>
        <table>
            <tr><th>Pattern</th><th>Usage Count</th></tr>
"""
        
        for pattern, count in report_data['metrics'].get('recent_usage', {}).items():
            html += f"            <tr><td>{pattern}</td><td>{count}</td></tr>\n"
        
        html += """
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
    
    def _create_filter_utility(self):
        """Create Python utility for log filtering"""
        filter_utility = '''#!/usr/bin/env python3
"""
Log Filter Utility - Filter logs using whitelist patterns
"""

import sys
import argparse
from pathlib import Path
from log_whitelist_manager import LogWhitelistManager

def main():
    parser = argparse.ArgumentParser(description="Filter logs using whitelist patterns")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--input", type=Path, required=True,
                       help="Input log file")
    parser.add_argument("--output", type=Path,
                       help="Output filtered log file")
    parser.add_argument("--metrics", action="store_true",
                       help="Show filter metrics")
    
    args = parser.parse_args()
    
    lwm = LogWhitelistManager(args.project_root)
    results = lwm.filter_logs(args.input, args.output)
    
    if args.metrics:
        print(f"Total lines: {results['total_lines']}")
        print(f"Filtered lines: {results['filtered_lines']}")
        print(f"Suppressed lines: {results['suppressed_lines']}")
        print(f"Suppression rate: {results['suppressed_lines']/results['total_lines']*100:.1f}%")

if __name__ == "__main__":
    main()
'''
        
        filter_script_path = self.log_filters_dir / "filter_logs.py"
        with open(filter_script_path, 'w') as f:
            f.write(filter_utility)
        
        # Make executable
        os.chmod(filter_script_path, 0o755)
    
    def _save_filter_metrics(self, results: Dict):
        """Save filter metrics"""
        metrics_path = self.reports_dir / f"filter-metrics-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(metrics_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _save_validation_results(self, results: Dict):
        """Save validation results"""
        validation_path = self.reports_dir / f"pattern-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(validation_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _report_new_patterns(self, new_patterns: List[Dict]):
        """Report new patterns that need attention"""
        logger.warning("New log patterns detected that may need whitelisting:")
        for pattern_info in new_patterns:
            logger.warning(f"  Line {pattern_info['line_number']}: {pattern_info['pattern']} - {pattern_info['line']}")
    
    def _report_security_violations(self, security_violations: List[Dict]):
        """Report security-related log entries"""
        logger.error("Security-related log entries found (never whitelist these):")
        for violation in security_violations:
            logger.error(f"  Line {violation['line_number']}: {violation['line']}")

def main():
    """Main entry point for log whitelist management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Log Whitelist Management")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "filter", "validate", "report"],
                       required=True, help="Action to perform")
    parser.add_argument("--input", type=Path, help="Input log file (for filter action)")
    parser.add_argument("--output", type=Path, help="Output file (for filter action)")
    
    args = parser.parse_args()
    
    lwm = LogWhitelistManager(args.project_root)
    
    if args.action == "setup":
        lwm.setup_log_whitelist_config()
    elif args.action == "filter":
        if args.input:
            lwm.filter_logs(args.input, args.output)
        else:
            logger.error("--input argument required for filter action")
    elif args.action == "validate":
        lwm.validate_whitelist_patterns()
    elif args.action == "report":
        lwm.generate_whitelist_report()

if __name__ == "__main__":
    main()
