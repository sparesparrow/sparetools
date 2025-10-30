#!/usr/bin/env python3
"""
OpenSSL Build Matrix Manager
Manages comprehensive build matrix configurations for OpenSSL Conan builds
Based on misc-openssl exported assets
"""

import json
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenSSLBuildMatrixManager:
    """Manages OpenSSL build matrix configurations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dev_dir = project_root / "conan-dev"
        self.profiles_dir = self.conan_dev_dir / "profiles"
        self.build_matrix_file = self.conan_dev_dir / "openssl_build_matrix.json"
        self.docs_dir = project_root / "docs"
        
    def load_build_matrix(self) -> Dict[str, Any]:
        """Load build matrix configuration from JSON file"""
        try:
            with open(self.build_matrix_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Build matrix file not found: {self.build_matrix_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in build matrix file: {e}")
            return {}
    
    def generate_conan_profiles(self) -> None:
        """Generate Conan profiles from build matrix configuration"""
        logger.info("Generating Conan profiles from build matrix...")
        
        matrix = self.load_build_matrix()
        if not matrix:
            logger.error("Cannot generate profiles without valid build matrix")
            return
        
        profiles_generated = 0
        
        for platform in matrix.get("platforms", []):
            for compiler in matrix.get("compilers", []):
                if platform["conan_os"] in compiler["platforms"]:
                    profile_name = f"{platform['name']}-{compiler['name']}"
                    profile_content = self._generate_profile_content(platform, compiler)
                    
                    profile_path = self.profiles_dir / f"{profile_name}.profile"
                    with open(profile_path, 'w') as f:
                        f.write(profile_content)
                    
                    logger.info(f"Generated profile: {profile_name}")
                    profiles_generated += 1
        
        logger.info(f"Generated {profiles_generated} Conan profiles")
    
    def _generate_profile_content(self, platform: Dict, compiler: Dict) -> str:
        """Generate profile content for a platform/compiler combination"""
        content = f"""[settings]
os={platform['conan_os']}
arch={platform['conan_arch']}
compiler={compiler['conan_compiler']}
compiler.version={compiler['versions'][0]}
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
tools.system.package_manager:mode=install
tools.system.package_manager:sudo=True
tools.cmake.cmaketoolchain:jobs=8

[buildenv]
CC={compiler['name']}
CXX={compiler['name']}++
CFLAGS=-O2 -g
CXXFLAGS=-O2 -g
"""
        return content
    
    def generate_ci_workflow(self) -> None:
        """Generate GitHub Actions workflow from build matrix"""
        logger.info("Generating GitHub Actions workflow...")
        
        matrix = self.load_build_matrix()
        if not matrix:
            logger.error("Cannot generate workflow without valid build matrix")
            return
        
        workflow_content = self._generate_workflow_content(matrix)
        
        workflow_path = self.project_root / ".github" / "workflows" / "conan-ci-generated.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"Generated workflow: {workflow_path}")
    
    def _generate_workflow_content(self, matrix: Dict[str, Any]) -> str:
        """Generate GitHub Actions workflow content"""
        workflow = """name: Conan CI/CD (Generated)
'on':
  push:
    branches:
    - master
    - main
    - feature/*
  pull_request:
    branches:
    - master
    - main
jobs:
  build-and-test:
    name: ${{ matrix.name }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
"""
        
        # Add matrix entries for each configuration
        for config in matrix.get("configurations", []):
            workflow += f"""        - name: {config['job_name'].replace('_', ' ').title()}
          os: ubuntu-latest
          profile: {config['compiler']}-{config.get('arch', 'x86_64')}
          conan_options: {self._format_conan_options(config['options'])}
          test: true
"""
        
        workflow += """    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v6
      with:
        python-version: '3.12'
        cache: 'pip'
    - name: Install Conan
      run: pip install conan>=2.0
    - name: Setup Conan profile
      run: conan profile detect --force || conan profile new default --detect
    - name: Install dependencies
      run: conan install . --profile=conan-dev/profiles/${{ matrix.profile }} --build=missing ${{ matrix.conan_options }}
    - name: Build OpenSSL
      run: conan build . --profile=conan-dev/profiles/${{ matrix.profile }} ${{ matrix.conan_options }}
    - name: Run tests
      if: ${{ matrix.test }}
      run: conan test . --profile=conan-dev/profiles/${{ matrix.profile }} ${{ matrix.conan_options }}
    - name: Create package
      run: conan create . --profile=conan-dev/profiles/${{ matrix.profile }} ${{ matrix.conan_options }}
"""
        
        return workflow
    
    def _format_conan_options(self, options: Dict[str, Any]) -> str:
        """Format options dictionary as Conan command line options"""
        option_strings = []
        for key, value in options.items():
            if isinstance(value, bool):
                if value:
                    option_strings.append(f"-o {key}=True")
                else:
                    option_strings.append(f"-o {key}=False")
            else:
                option_strings.append(f"-o {key}={value}")
        return " ".join(option_strings)
    
    def validate_configurations(self) -> bool:
        """Validate all build configurations"""
        logger.info("Validating build configurations...")
        
        matrix = self.load_build_matrix()
        if not matrix:
            logger.error("Cannot validate without valid build matrix")
            return False
        
        valid_configs = 0
        total_configs = len(matrix.get("configurations", []))
        
        for config in matrix.get("configurations", []):
            if self._validate_single_config(config):
                valid_configs += 1
            else:
                logger.warning(f"Invalid configuration: {config['job_name']}")
        
        logger.info(f"Validated {valid_configs}/{total_configs} configurations")
        return valid_configs == total_configs
    
    def _validate_single_config(self, config: Dict[str, Any]) -> bool:
        """Validate a single build configuration"""
        required_fields = ["job_name", "compiler", "build_type", "options"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field '{field}' in config {config.get('job_name', 'unknown')}")
                return False
        
        # Validate options
        options = config.get("options", {})
        for key, value in options.items():
            if not isinstance(value, (bool, str, int)):
                logger.error(f"Invalid option type for '{key}': {type(value)}")
                return False
        
        return True
    
    def run_build_matrix(self, selected_configs: Optional[List[str]] = None) -> bool:
        """Run build matrix for selected or all configurations"""
        logger.info("Running build matrix...")
        
        matrix = self.load_build_matrix()
        if not matrix:
            logger.error("Cannot run build matrix without valid configuration")
            return False
        
        configurations = matrix.get("configurations", [])
        if selected_configs:
            configurations = [c for c in configurations if c["job_name"] in selected_configs]
        
        success_count = 0
        total_count = len(configurations)
        
        for config in configurations:
            logger.info(f"Building configuration: {config['job_name']}")
            
            if self._run_single_build(config):
                success_count += 1
                logger.info(f"✅ {config['job_name']} - SUCCESS")
            else:
                logger.error(f"❌ {config['job_name']} - FAILED")
        
        logger.info(f"Build matrix completed: {success_count}/{total_count} successful")
        return success_count == total_count
    
    def _run_single_build(self, config: Dict[str, Any]) -> bool:
        """Run a single build configuration"""
        try:
            # Determine profile
            profile = f"{config['compiler']}-{config.get('arch', 'x86_64')}"
            if config.get('build_type') == 'Debug':
                profile += '-debug'
            
            # Format options
            options = self._format_conan_options(config['options'])
            
            # Run conan create command
            cmd = [
                "conan", "create", ".",
                f"--profile=conan-dev/profiles/{profile}.profile",
                *options.split()
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return True
            else:
                logger.error(f"Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running build: {e}")
            return False
    
    def generate_documentation(self) -> None:
        """Generate comprehensive documentation from build matrix"""
        logger.info("Generating documentation...")
        
        matrix = self.load_build_matrix()
        if not matrix:
            logger.error("Cannot generate documentation without valid build matrix")
            return
        
        # Generate configuration summary
        summary = self._generate_configuration_summary(matrix)
        
        summary_path = self.docs_dir / "BUILD_MATRIX_SUMMARY.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        logger.info(f"Generated documentation: {summary_path}")
    
    def _generate_configuration_summary(self, matrix: Dict[str, Any]) -> str:
        """Generate configuration summary documentation"""
        summary = f"""# OpenSSL Build Matrix Summary

## Overview
This document provides a comprehensive summary of the OpenSSL build matrix configuration.

## Statistics
- **Total Configurations**: {len(matrix.get('configurations', []))}
- **Platforms**: {len(matrix.get('platforms', []))}
- **Compilers**: {len(matrix.get('compilers', []))}
- **Build Types**: {len(matrix.get('build_types', []))}

## Platforms
"""
        
        for platform in matrix.get("platforms", []):
            summary += f"- **{platform['name']}**: {platform['os']} {platform['arch']}\n"
        
        summary += "\n## Compilers\n"
        for compiler in matrix.get("compilers", []):
            summary += f"- **{compiler['name']}**: {', '.join(compiler['platforms'])}\n"
        
        summary += "\n## Build Types\n"
        for build_type in matrix.get("build_types", []):
            summary += f"- **{build_type['name']}**: {build_type['conan_build_type']}\n"
        
        summary += "\n## Configurations\n"
        for config in matrix.get("configurations", []):
            summary += f"### {config['job_name']}\n"
            summary += f"- **Compiler**: {config['compiler']}\n"
            summary += f"- **Build Type**: {config['build_type']}\n"
            summary += f"- **Options**: {', '.join([f'{k}={v}' for k, v in config.get('options', {}).items()])}\n"
            summary += f"- **Config Line**: `{config.get('config_line', 'N/A')}`\n\n"
        
        return summary

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Build Matrix Manager")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--generate-profiles", action="store_true",
                       help="Generate Conan profiles from build matrix")
    parser.add_argument("--generate-workflow", action="store_true",
                       help="Generate GitHub Actions workflow")
    parser.add_argument("--validate", action="store_true",
                       help="Validate build configurations")
    parser.add_argument("--run-matrix", action="store_true",
                       help="Run build matrix")
    parser.add_argument("--configs", nargs="+",
                       help="Specific configurations to run")
    parser.add_argument("--generate-docs", action="store_true",
                       help="Generate documentation")
    parser.add_argument("--all", action="store_true",
                       help="Run all operations")
    
    args = parser.parse_args()
    
    manager = OpenSSLBuildMatrixManager(args.project_root)
    
    if args.all or args.generate_profiles:
        manager.generate_conan_profiles()
    
    if args.all or args.generate_workflow:
        manager.generate_ci_workflow()
    
    if args.all or args.validate:
        if not manager.validate_configurations():
            sys.exit(1)
    
    if args.all or args.run_matrix:
        if not manager.run_build_matrix(args.configs):
            sys.exit(1)
    
    if args.all or args.generate_docs:
        manager.generate_documentation()
    
    if not any([args.generate_profiles, args.generate_workflow, 
                args.validate, args.run_matrix, args.generate_docs, args.all]):
        parser.print_help()

if __name__ == "__main__":
    main()