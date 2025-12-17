#!/usr/bin/env python3
"""
Audit script for all Conan recipes in packages/

Validates:
- Conan 2.x API compliance (no env_info, proper buildenv_info/runenv_info)
- Required fields (name, version, description, license)
- package_type correctness
- Dependency declarations (tool_requires, python_requires, requires)
- Test package directories for key packages
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class PackageAudit:
    """Audit results for a single package"""
    path: str
    name: str = ""
    version: str = ""
    package_type: str = ""
    description: str = ""
    license: str = ""
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    has_test_package: bool = False
    dependencies: Dict[str, List[str]] = field(default_factory=lambda: {
        "tool_requires": [],
        "python_requires": [],
        "requires": []
    })
    uses_env_info: bool = False
    uses_buildenv_info: bool = False
    uses_runenv_info: bool = False
    has_package_info: bool = False


class ConanRecipeAuditor:
    """Auditor for Conan recipe files"""
    
    def __init__(self, packages_dir: Path):
        self.packages_dir = packages_dir
        self.packages: List[PackageAudit] = []
        
    def audit_all(self) -> List[PackageAudit]:
        """Audit all packages"""
        for conanfile in self.packages_dir.rglob("conanfile.py"):
            # Skip deprecated packages
            if "deprecated" in str(conanfile):
                continue
                
            audit = self.audit_package(conanfile)
            self.packages.append(audit)
            
        return self.packages
    
    def audit_package(self, conanfile_path: Path) -> PackageAudit:
        """Audit a single package"""
        audit = PackageAudit(path=str(conanfile_path.relative_to(self.packages_dir.parent)))
        
        try:
            with open(conanfile_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse AST for better analysis
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                audit.issues.append(f"Syntax error: {e}")
                return audit
            
            # Check for required fields using AST
            self._check_required_fields(audit, tree, content)
            
            # Check Conan 2.x API compliance
            self._check_conan_api(audit, content)
            
            # Check dependencies
            self._check_dependencies(audit, content)
            
            # Check test_package directory
            test_package_dir = conanfile_path.parent / "test_package"
            audit.has_test_package = test_package_dir.exists() and (test_package_dir / "conanfile.py").exists()
            
            # Check package_type correctness
            self._check_package_type(audit, content)
            
        except Exception as e:
            audit.issues.append(f"Error reading file: {e}")
        
        return audit
    
    def _check_required_fields(self, audit: PackageAudit, tree: ast.AST, content: str):
        """Check for required fields"""
        # Check for class definition
        class_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if "Conan" in node.name or "ConanFile" in "".join([base.id for base in node.bases if isinstance(base, ast.Name)]):
                    class_found = True
                    break
        
        if not class_found:
            audit.issues.append("No ConanFile class found")
        
        # Check for name
        if re.search(r'name\s*=\s*["\']', content):
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                audit.name = match.group(1)
            else:
                audit.issues.append("name field found but could not parse value")
        else:
            audit.issues.append("Missing required field: name")
        
        # Check for version
        if re.search(r'version\s*=\s*["\']', content):
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                audit.version = match.group(1)
            else:
                audit.issues.append("version field found but could not parse value")
        else:
            audit.issues.append("Missing required field: version")
        
        # Check for description
        if re.search(r'description\s*=\s*["\']', content):
            match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                audit.description = match.group(1)
            else:
                audit.warnings.append("description field found but could not parse value")
        else:
            audit.warnings.append("Missing recommended field: description")
        
        # Check for license
        if re.search(r'license\s*=\s*["\']', content):
            match = re.search(r'license\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                audit.license = match.group(1)
            else:
                audit.warnings.append("license field found but could not parse value")
        else:
            audit.warnings.append("Missing recommended field: license")
    
    def _check_conan_api(self, audit: PackageAudit, content: str):
        """Check Conan 2.x API compliance"""
        # Check for deprecated env_info
        if re.search(r'self\.env_info\.', content):
            audit.uses_env_info = True
            audit.issues.append("Uses deprecated env_info API (Conan 1.x)")
        
        # Check for buildenv_info/runenv_info (Conan 2.x)
        if re.search(r'self\.buildenv_info\.', content):
            audit.uses_buildenv_info = True
        
        if re.search(r'self\.runenv_info\.', content):
            audit.uses_runenv_info = True
        
        # Check for package_info method
        if 'def package_info' in content:
            audit.has_package_info = True
            
            # For python-require packages, should use buildenv_info
            if 'package_type = "python-require"' in content:
                if not audit.uses_buildenv_info and not audit.uses_runenv_info:
                    # Check if it's a library package (has cpp_info.libs)
                    if not re.search(r'cpp_info\.libs\s*=\s*\[', content):
                        audit.warnings.append("python-require package should use buildenv_info for PYTHONPATH")
    
    def _check_dependencies(self, audit: PackageAudit, content: str):
        """Check dependency declarations"""
        # Check tool_requires
        tool_requires_pattern = r'tool_requires\s*=\s*\[(.*?)\]'
        match = re.search(tool_requires_pattern, content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
            audit.dependencies["tool_requires"] = deps
        
        # Check python_requires
        python_requires_pattern = r'python_requires\s*=\s*["\']([^"\']+)["\']'
        match = re.search(python_requires_pattern, content)
        if match:
            audit.dependencies["python_requires"].append(match.group(1))
        else:
            # Check for tuple syntax
            python_requires_tuple_pattern = r'python_requires\s*=\s*\((.*?)\)'
            match = re.search(python_requires_tuple_pattern, content, re.DOTALL)
            if match:
                deps_str = match.group(1)
                deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
                audit.dependencies["python_requires"] = deps
        
        # Check requires
        requires_pattern = r'requires\s*=\s*\[(.*?)\]'
        match = re.search(requires_pattern, content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
            audit.dependencies["requires"] = deps
    
    def _check_package_type(self, audit: PackageAudit, content: str):
        """Check package_type is set correctly"""
        match = re.search(r'package_type\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            audit.package_type = match.group(1)
            
            # Validate package_type values
            valid_types = ["application", "library", "python-require", "shared-library", "static-library"]
            if audit.package_type not in valid_types:
                audit.warnings.append(f"package_type '{audit.package_type}' may not be standard")
        else:
            audit.warnings.append("Missing package_type field (recommended for Conan 2.x)")
    
    def generate_report(self) -> str:
        """Generate markdown audit report"""
        lines = []
        lines.append("# Conan Recipes Audit Report")
        lines.append("")
        lines.append(f"Generated: {self._get_timestamp()}")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        
        total_packages = len(self.packages)
        packages_with_issues = sum(1 for pkg in self.packages if pkg.issues)
        packages_with_warnings = sum(1 for pkg in self.packages if pkg.warnings)
        compliant_packages = sum(1 for pkg in self.packages if not pkg.issues and not pkg.uses_env_info)
        
        lines.append(f"- **Total packages audited**: {total_packages}")
        lines.append(f"- **Compliant packages**: {compliant_packages}")
        lines.append(f"- **Packages with issues**: {packages_with_issues}")
        lines.append(f"- **Packages with warnings**: {packages_with_warnings}")
        lines.append("")
        
        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        
        for pkg in sorted(self.packages, key=lambda x: x.path):
            lines.append(f"### {pkg.name or pkg.path}")
            lines.append("")
            lines.append(f"- **Path**: `{pkg.path}`")
            if pkg.version:
                lines.append(f"- **Version**: {pkg.version}")
            if pkg.package_type:
                lines.append(f"- **Package Type**: `{pkg.package_type}`")
            if pkg.description:
                lines.append(f"- **Description**: {pkg.description}")
            if pkg.license:
                lines.append(f"- **License**: {pkg.license}")
            
            # Dependencies
            if any(pkg.dependencies.values()):
                lines.append("- **Dependencies**:")
                if pkg.dependencies["tool_requires"]:
                    lines.append(f"  - tool_requires: {', '.join(pkg.dependencies['tool_requires'])}")
                if pkg.dependencies["python_requires"]:
                    lines.append(f"  - python_requires: {', '.join(pkg.dependencies['python_requires'])}")
                if pkg.dependencies["requires"]:
                    lines.append(f"  - requires: {', '.join(pkg.dependencies['requires'])}")
            
            lines.append(f"- **Has test_package**: {'✅' if pkg.has_test_package else '❌'}")
            
            # API compliance
            if pkg.uses_env_info:
                lines.append("- **Conan API**: ❌ Uses deprecated `env_info`")
            elif pkg.uses_buildenv_info or pkg.uses_runenv_info:
                lines.append("- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)")
            elif pkg.has_package_info:
                lines.append("- **Conan API**: ⚠️ Has `package_info` but no environment info")
            else:
                lines.append("- **Conan API**: ℹ️ No environment info (may be library-only)")
            
            # Issues
            if pkg.issues:
                lines.append("")
                lines.append("**Issues:**")
                for issue in pkg.issues:
                    lines.append(f"- ❌ {issue}")
            
            # Warnings
            if pkg.warnings:
                lines.append("")
                lines.append("**Warnings:**")
                for warning in pkg.warnings:
                    lines.append(f"- ⚠️ {warning}")
            
            # Status
            if not pkg.issues and not pkg.warnings:
                lines.append("")
                lines.append("**Status**: ✅ Compliant")
            elif pkg.issues:
                lines.append("")
                lines.append("**Status**: ❌ Has issues")
            else:
                lines.append("")
                lines.append("**Status**: ⚠️ Has warnings")
            
            lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        # Check for OpenSSL version references
        openssl_refs = []
        for pkg in self.packages:
            if pkg.name == "sparetools-openssl":
                continue
            # Check if package references OpenSSL
            for dep_type, deps in pkg.dependencies.items():
                for dep in deps:
                    if "openssl" in dep.lower():
                        openssl_refs.append((pkg.name, dep))
        
        if openssl_refs:
            lines.append("### OpenSSL Dependencies")
            lines.append("")
            lines.append("Packages referencing OpenSSL:")
            for pkg_name, dep in openssl_refs:
                lines.append(f"- `{pkg_name}`: {dep}")
            lines.append("")
            lines.append("**Note**: Verify all OpenSSL references use version 3.3.2")
            lines.append("")
        
        # Test package coverage
        missing_test_packages = [pkg for pkg in self.packages if not pkg.has_test_package and pkg.package_type != "python-require"]
        if missing_test_packages:
            lines.append("### Test Package Coverage")
            lines.append("")
            lines.append("Packages missing test_package directories:")
            for pkg in missing_test_packages:
                lines.append(f"- `{pkg.name}` ({pkg.path})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    packages_dir = repo_root / "packages"
    
    if not packages_dir.exists():
        print(f"Error: packages directory not found at {packages_dir}")
        return 1
    
    print("Auditing Conan recipes...")
    auditor = ConanRecipeAuditor(packages_dir)
    packages = auditor.audit_all()
    
    print(f"Audited {len(packages)} packages")
    
    # Generate report
    report = auditor.generate_report()
    
    # Write report
    output_file = repo_root / "docs" / "AUDIT-RESULTS.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report written to {output_file}")
    
    # Print summary
    issues_count = sum(len(pkg.issues) for pkg in packages)
    warnings_count = sum(len(pkg.warnings) for pkg in packages)
    
    if issues_count == 0 and warnings_count == 0:
        print("✅ All packages are compliant!")
        return 0
    elif issues_count == 0:
        print(f"⚠️ Found {warnings_count} warnings (see report for details)")
        return 0
    else:
        print(f"❌ Found {issues_count} issues and {warnings_count} warnings (see report for details)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
