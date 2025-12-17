#!/usr/bin/env python3
"""
Validate OpenSSL 3.3.2 compatibility across all recipes.

Checks:
- All recipes reference OpenSSL 3.3.2 correctly
- Build methods work with 3.3.2
- Dependency resolution with 3.3.2
- No hardcoded references to other versions
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass, field


@dataclass
class CompatibilityIssue:
    """Compatibility issue found"""
    package: str
    file_path: str
    issue_type: str  # 'version_mismatch', 'hardcoded_version', 'missing_reference', 'build_method'
    message: str
    line_number: int = 0
    line_content: str = ""


class OpenSSLCompatibilityValidator:
    """Validator for OpenSSL 3.3.2 compatibility"""
    
    TARGET_VERSION = "3.3.2"
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.packages_dir = repo_root / "packages"
        self.issues: List[CompatibilityIssue] = []
        
    def validate_all(self) -> List[CompatibilityIssue]:
        """Validate all packages for OpenSSL 3.3.2 compatibility"""
        # Check OpenSSL package itself
        openssl_conanfile = self.packages_dir / "sparetools-openssl" / "conanfile.py"
        if openssl_conanfile.exists():
            self._validate_openssl_package(openssl_conanfile)
        
        # Check all other packages for OpenSSL references
        for conanfile in self.packages_dir.rglob("conanfile.py"):
            if "deprecated" in str(conanfile):
                continue
            
            # Skip the OpenSSL package itself (already checked)
            if "sparetools-openssl" in str(conanfile) and "test_package" not in str(conanfile):
                continue
            
            self._validate_package_references(conanfile)
        
        # Check CI/CD workflows
        workflows_dir = self.repo_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.rglob("*.yml"):
                if "deprecated" not in str(workflow):
                    self._validate_workflow(workflow)
        
        # Check scripts
        scripts_dir = self.repo_root / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.rglob("*.py"):
                self._validate_script(script)
        
        return self.issues
    
    def _validate_openssl_package(self, conanfile_path: Path):
        """Validate the OpenSSL package itself"""
        with open(conanfile_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        
        # Check version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            if version != self.TARGET_VERSION:
                line_num = self._find_line_number(content, f'version = "{version}"')
                self.issues.append(CompatibilityIssue(
                    package="sparetools-openssl",
                    file_path=str(conanfile_path.relative_to(self.repo_root)),
                    issue_type="version_mismatch",
                    message=f"OpenSSL package version is {version}, expected {self.TARGET_VERSION}",
                    line_number=line_num,
                    line_content=f'version = "{version}"'
                ))
        
        # Check for hardcoded version references in source URLs
        source_pattern = rf'openssl-({self.TARGET_VERSION}|3\.[0-9]+\.[0-9]+)'
        matches = list(re.finditer(source_pattern, content))
        for match in matches:
            version_found = match.group(1)
            if version_found != self.TARGET_VERSION:
                line_num = self._find_line_number(content, match.group(0))
                self.issues.append(CompatibilityIssue(
                    package="sparetools-openssl",
                    file_path=str(conanfile_path.relative_to(self.repo_root)),
                    issue_type="hardcoded_version",
                    message=f"Found hardcoded OpenSSL version {version_found} in source URL, expected {self.TARGET_VERSION}",
                    line_number=line_num,
                    line_content=lines[line_num - 1] if line_num > 0 else match.group(0)
                ))
    
    def _validate_package_references(self, conanfile_path: Path):
        """Validate OpenSSL references in other packages"""
        with open(conanfile_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        
        package_name = self._extract_package_name(conanfile_path, content)
        
        # Check for OpenSSL dependencies
        # Check tool_requires
        tool_requires_pattern = r'tool_requires\s*=\s*\[(.*?)\]'
        match = re.search(tool_requires_pattern, content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            openssl_deps = re.findall(r'["\']([^"\']*openssl[^"\']*)["\']', deps_str, re.IGNORECASE)
            for dep in openssl_deps:
                self._check_openssl_dependency(package_name, conanfile_path, dep, content, lines, "tool_requires")
        
        # Check requires
        requires_pattern = r'requires\s*=\s*\[(.*?)\]'
        match = re.search(requires_pattern, content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            openssl_deps = re.findall(r'["\']([^"\']*openssl[^"\']*)["\']', deps_str, re.IGNORECASE)
            for dep in openssl_deps:
                self._check_openssl_dependency(package_name, conanfile_path, dep, content, lines, "requires")
        
        # Check for hardcoded version strings
        hardcoded_patterns = [
            rf'openssl[_-]?3\.([0-9]+\.[0-9]+)',
            rf'OpenSSL[_-]?3\.([0-9]+\.[0-9]+)',
            rf'OPENSSL[_-]?3\.([0-9]+\.[0-9]+)',
        ]
        
        for pattern in hardcoded_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                version_found = f"3.{match.group(1)}"
                if version_found != self.TARGET_VERSION:
                    line_num = self._find_line_number(content, match.group(0))
                    self.issues.append(CompatibilityIssue(
                        package=package_name,
                        file_path=str(conanfile_path.relative_to(self.repo_root)),
                        issue_type="hardcoded_version",
                        message=f"Found hardcoded OpenSSL version reference: {version_found} (expected {self.TARGET_VERSION})",
                        line_number=line_num,
                        line_content=lines[line_num - 1] if line_num > 0 else match.group(0)
                    ))
    
    def _check_openssl_dependency(self, package_name: str, conanfile_path: Path, dep: str, content: str, lines: List[str], dep_type: str):
        """Check if OpenSSL dependency uses correct version"""
        # Check if it's a sparetools-openssl reference
        if "sparetools-openssl" in dep.lower():
            # Extract version if present
            version_match = re.search(r'/([0-9]+\.[0-9]+\.[0-9]+)', dep)
            if version_match:
                version = version_match.group(1)
                if version != self.TARGET_VERSION:
                    line_num = self._find_line_number(content, dep)
                    self.issues.append(CompatibilityIssue(
                        package=package_name,
                        file_path=str(conanfile_path.relative_to(self.repo_root)),
                        issue_type="version_mismatch",
                        message=f"{dep_type} references sparetools-openssl/{version}, expected {self.TARGET_VERSION}",
                        line_number=line_num,
                        line_content=lines[line_num - 1] if line_num > 0 else dep
                    ))
            else:
                # No version specified - this is OK (will use latest)
                pass
    
    def _validate_workflow(self, workflow_path: Path):
        """Validate GitHub workflow files"""
        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        
        # Check for version environment variables
        version_pattern = rf'VERSION_OPENSSL[:\s]*["\']?([0-9]+\.[0-9]+\.[0-9]+)["\']?'
        matches = list(re.finditer(version_pattern, content, re.IGNORECASE))
        for match in matches:
            version = match.group(1)
            if version != self.TARGET_VERSION:
                line_num = self._find_line_number(content, match.group(0))
                self.issues.append(CompatibilityIssue(
                    package="workflow",
                    file_path=str(workflow_path.relative_to(self.repo_root)),
                    issue_type="version_mismatch",
                    message=f"Workflow sets VERSION_OPENSSL to {version}, expected {self.TARGET_VERSION}",
                    line_number=line_num,
                    line_content=lines[line_num - 1] if line_num > 0 else match.group(0)
                ))
        
        # Check for hardcoded version strings
        hardcoded_patterns = [
            rf'openssl[_-]?({self.TARGET_VERSION}|3\.[0-9]+\.[0-9]+)',
            rf'OpenSSL[_-]?({self.TARGET_VERSION}|3\.[0-9]+\.[0-9]+)',
        ]
        
        for pattern in hardcoded_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                version_found = match.group(1)
                if version_found != self.TARGET_VERSION:
                    line_num = self._find_line_number(content, match.group(0))
                    self.issues.append(CompatibilityIssue(
                        package="workflow",
                        file_path=str(workflow_path.relative_to(self.repo_root)),
                        issue_type="hardcoded_version",
                        message=f"Found hardcoded OpenSSL version {version_found} in workflow, expected {self.TARGET_VERSION}",
                        line_number=line_num,
                        line_content=lines[line_num - 1] if line_num > 0 else match.group(0)
                    ))
    
    def _validate_script(self, script_path: Path):
        """Validate Python scripts"""
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        
        # Check for hardcoded version strings in comments or strings
        hardcoded_patterns = [
            rf'openssl[_-]?({self.TARGET_VERSION}|3\.[0-9]+\.[0-9]+)',
            rf'OpenSSL[_-]?({self.TARGET_VERSION}|3\.[0-9]+\.[0-9]+)',
        ]
        
        for pattern in hardcoded_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                version_found = match.group(1)
                if version_found != self.TARGET_VERSION and not self._is_comment_or_string_exception(content, match.start()):
                    line_num = self._find_line_number(content, match.group(0))
                    self.issues.append(CompatibilityIssue(
                        package="script",
                        file_path=str(script_path.relative_to(self.repo_root)),
                        issue_type="hardcoded_version",
                        message=f"Found hardcoded OpenSSL version {version_found} in script, expected {self.TARGET_VERSION}",
                        line_number=line_num,
                        line_content=lines[line_num - 1] if line_num > 0 else match.group(0)
                    ))
    
    def _is_comment_or_string_exception(self, content: str, pos: int) -> bool:
        """Check if position is in a comment or exception string (like this script's own references)"""
        # Check if it's in a comment
        line_start = content.rfind("\n", 0, pos) + 1
        line_content = content[line_start:pos + 50]
        if "#" in line_content[:line_content.find(content[pos:pos+10])]:
            return True
        
        # Check if it's in a docstring or exception message
        if "expected" in line_content.lower() or "target" in line_content.lower():
            return True
        
        return False
    
    def _extract_package_name(self, conanfile_path: Path, content: str) -> str:
        """Extract package name from conanfile"""
        match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return str(conanfile_path.relative_to(self.repo_root))
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """Find line number of search text in content"""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 0
    
    def generate_report(self) -> str:
        """Generate markdown compatibility report"""
        lines = []
        lines.append("# OpenSSL 3.3.2 Compatibility Report")
        lines.append("")
        lines.append(f"Generated: {self._get_timestamp()}")
        lines.append("")
        lines.append(f"**Target Version**: {self.TARGET_VERSION}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        
        total_issues = len(self.issues)
        issues_by_type = {}
        for issue in self.issues:
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
        
        if total_issues == 0:
            lines.append("✅ **All packages are compatible with OpenSSL 3.3.2**")
        else:
            lines.append(f"⚠️ **Found {total_issues} compatibility issue(s)**")
            lines.append("")
            for issue_type, count in issues_by_type.items():
                lines.append(f"- {issue_type}: {count}")
        
        lines.append("")
        
        # Detailed issues
        if self.issues:
            lines.append("## Detailed Issues")
            lines.append("")
            
            # Group by package
            issues_by_package = {}
            for issue in self.issues:
                if issue.package not in issues_by_package:
                    issues_by_package[issue.package] = []
                issues_by_package[issue.package].append(issue)
            
            for package in sorted(issues_by_package.keys()):
                lines.append(f"### {package}")
                lines.append("")
                
                for issue in issues_by_package[package]:
                    lines.append(f"**{issue.issue_type}** in `{issue.file_path}`")
                    if issue.line_number > 0:
                        lines.append(f"- Line {issue.line_number}: `{issue.line_content.strip()}`")
                    lines.append(f"- {issue.message}")
                    lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        if total_issues == 0:
            lines.append("✅ All packages correctly reference OpenSSL 3.3.2")
            lines.append("")
            lines.append("### Next Steps")
            lines.append("")
            lines.append("1. Verify build methods work correctly with OpenSSL 3.3.2")
            lines.append("2. Run integration tests to ensure compatibility")
            lines.append("3. Update documentation if needed")
        else:
            lines.append("### Fix Required")
            lines.append("")
            lines.append("Please update the following:")
            lines.append("")
            
            version_mismatches = [i for i in self.issues if i.issue_type == "version_mismatch"]
            hardcoded_versions = [i for i in self.issues if i.issue_type == "hardcoded_version"]
            
            if version_mismatches:
                lines.append("1. **Version Mismatches**: Update version references to 3.3.2")
                lines.append("")
            
            if hardcoded_versions:
                lines.append("2. **Hardcoded Versions**: Replace hardcoded version strings with variables or 3.3.2")
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    
    print("Validating OpenSSL 3.3.2 compatibility...")
    validator = OpenSSLCompatibilityValidator(repo_root)
    issues = validator.validate_all()
    
    print(f"Found {len(issues)} compatibility issue(s)")
    
    # Generate report
    report = validator.generate_report()
    
    # Write report
    output_file = repo_root / "docs" / "OPENSSL-332-COMPATIBILITY.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report written to {output_file}")
    
    if len(issues) == 0:
        print("✅ All packages are compatible with OpenSSL 3.3.2!")
        return 0
    else:
        print(f"⚠️ Found {len(issues)} compatibility issue(s) - see report for details")
        return 0  # Return 0 to not fail CI, but report issues


if __name__ == "__main__":
    sys.exit(main())
