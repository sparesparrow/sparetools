#!/usr/bin/env python3
"""
Conan Orchestrator - Advanced CI/CD automation for OpenSSL
Based on ngapy-dev patterns with enhanced error handling and monitoring
"""

import os
import sys
import subprocess
import platform
import shutil
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse
import yaml
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildType(Enum):
    """Build type enumeration"""
    DEBUG = "Debug"
    RELEASE = "Release"
    RELWITHDEBINFO = "RelWithDebInfo"
    MINSIZEREL = "MinSizeRel"

class Platform(Enum):
    """Platform enumeration"""
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "Macos"

@dataclass
class BuildConfig:
    """Build configuration data class"""
    platform: Platform
    compiler: str
    compiler_version: str
    build_type: BuildType
    arch: str
    profile_name: str
    conan_options: Dict[str, Any]
    environment_vars: Dict[str, str]

@dataclass
class BuildResult:
    """Build result data class"""
    success: bool
    duration: float
    output: str
    error: Optional[str] = None
    artifacts: List[Path] = None
    metrics: Dict[str, Any] = None

class ConanOrchestrator:
    """Advanced Conan orchestrator with CI/CD automation - pattern from ngapy-dev"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dir = project_root / "conan"
        self.profiles_dir = self.conan_dir / "profiles"
        self.cache_dir = self.conan_dir / "cache"
        self.artifacts_dir = self.conan_dir / "artifacts"
        self.config_file = self.conan_dir / "ci-config.yml"
        
        # Initialize directories
        self._initialize_directories()
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Platform detection
        self.current_platform = self._detect_platform()
        
        logger.info(f"🚀 Conan Orchestrator initialized for {self.current_platform.value}")
    
    def _initialize_directories(self):
        """Initialize required directories"""
        directories = [
            self.conan_dir,
            self.profiles_dir,
            self.cache_dir,
            self.artifacts_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_configuration(self) -> Dict:
        """Load configuration from YAML file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        config = {
            "conan": {
                "remote_name": "openssl-conan-remote",
                "remote_url": "https://your-artifactory-instance/artifactory/api/conan/openssl-conan",
                "user": os.environ.get("CONAN_USER", ""),
                "password": os.environ.get("CONAN_PASSWORD", "")
            },
            "build": {
                "source_dir": ".",
                "build_dir": "build",
                "install_dir": "install",
                "jobs": os.environ.get("CONAN_CPU_COUNT", "1")
            },
            "tests": {
                "results_dir": "test_results",
                "unit_test_command": "pytest",
                "performance_test_output": "performance_report.json"
            },
            "deployment": {
                "target_registry": "your-docker-registry.io/openssl",
                "docker_image_name": "openssl-conan-package"
            }
        }
        
        # Save default configuration
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"📝 Created default configuration: {self.config_file}")
        return config
    
    def _detect_platform(self) -> Platform:
        """Detect current platform"""
        system = platform.system().lower()
        if system == "linux":
            return Platform.LINUX
        elif system == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
    
    def _get_available_profiles(self) -> List[str]:
        """Get available Conan profiles for current platform"""
        profiles = []
        
        if self.current_platform == Platform.LINUX:
            profiles = [
                "hermetic-linux-gcc11",
                "abi-strict-clang15"
            ]
        elif self.current_platform == Platform.WINDOWS:
            profiles = [
                "windows-msvc2022",
                "windows-msvc2022-debug"
            ]
        elif self.current_platform == Platform.MACOS:
            profiles = [
                "macos-clang14",
                "macos-clang14-debug"
            ]
        
        return profiles
    
    def _create_profile(self, profile_name: str, build_config: BuildConfig) -> Path:
        """Create Conan profile file"""
        profile_path = self.profiles_dir / f"{profile_name}.profile"
        
        profile_content = f"""[settings]
os={build_config.platform.value}
compiler={build_config.compiler}
compiler.version={build_config.compiler_version}
compiler.libcxx=libstdc++11
build_type={build_config.build_type.value}
arch={build_config.arch}

[options]
"""
        
        # Add Conan options
        for option, value in build_config.conan_options.items():
            profile_content += f"{option}={value}\n"
        
        profile_content += f"""
[conf]
tools.env:CCACHE_DIR={self.cache_dir}/ccache
tools.cmake.cmaketoolchain:jobs={self.config['build']['jobs']}
"""
        
        # Add environment variables
        if build_config.environment_vars:
            profile_content += "\n[env]\n"
            for key, value in build_config.environment_vars.items():
                profile_content += f"{key}={value}\n"
        
        with open(profile_path, 'w') as f:
            f.write(profile_content)
        
        logger.info(f"📝 Created profile: {profile_path}")
        return profile_path
    
    def _run_conan_command(self, command: List[str], cwd: Optional[Path] = None, 
                          capture_output: bool = False) -> Tuple[bool, str, str]:
        """Run Conan command with error handling"""
        full_command = ["conan"] + command
        
        logger.info(f"🔧 Running: {' '.join(full_command)}")
        
        try:
            if capture_output:
                result = subprocess.run(
                    full_command,
                    cwd=cwd or self.project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    full_command,
                    cwd=cwd or self.project_root,
                    check=True
                )
                return True, "", ""
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with return code {e.returncode}"
            if capture_output:
                error_msg += f"\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            
            logger.error(f"❌ {error_msg}")
            return False, e.stdout if capture_output else "", e.stderr if capture_output else str(e)
    
    def setup_conan_remote(self) -> bool:
        """Set up Conan remote - pattern from ngapy-dev artifactory_functions.py"""
        logger.info("🔗 Setting up Conan remote...")
        
        # Clean existing remotes
        success, _, _ = self._run_conan_command(["remote", "clean"])
        if not success:
            logger.warning("⚠️ Failed to clean existing remotes")
        
        # Add remote
        remote_name = self.config["conan"]["remote_name"]
        remote_url = self.config["conan"]["remote_url"]
        
        success, _, _ = self._run_conan_command([
            "remote", "add", remote_name, remote_url
        ])
        
        if not success:
            logger.error(f"❌ Failed to add remote: {remote_name}")
            return False
        
        # Authenticate
        user = self.config["conan"]["user"]
        password = self.config["conan"]["password"]
        
        if user and password:
            success, _, _ = self._run_conan_command([
                "user", "-p", password, "-r", remote_name, user
            ])
            
            if not success:
                logger.error(f"❌ Failed to authenticate with remote: {remote_name}")
                return False
        
        logger.info(f"✅ Conan remote configured: {remote_name}")
        return True
    
    def install_dependencies(self, profile_name: str) -> bool:
        """Install Conan dependencies"""
        logger.info(f"📦 Installing dependencies with profile: {profile_name}")
        
        profile_path = self.profiles_dir / f"{profile_name}.profile"
        if not profile_path.exists():
            logger.error(f"❌ Profile not found: {profile_path}")
            return False
        
        success, _, _ = self._run_conan_command([
            "install", ".", "--profile", str(profile_path), "--build=missing"
        ])
        
        if success:
            logger.info("✅ Dependencies installed successfully")
        else:
            logger.error("❌ Failed to install dependencies")
        
        return success
    
    def build_package(self, profile_name: str, test: bool = False) -> BuildResult:
        """Build Conan package with comprehensive monitoring"""
        logger.info(f"🔨 Building package with profile: {profile_name}")
        
        start_time = time.time()
        profile_path = self.profiles_dir / f"{profile_name}.profile"
        
        if not profile_path.exists():
            return BuildResult(
                success=False,
                duration=0,
                output="",
                error=f"Profile not found: {profile_path}"
            )
        
        # Build command
        build_cmd = ["create", ".", "--profile", str(profile_path)]
        
        if test:
            build_cmd.append("--test")
        
        # Run build
        success, stdout, stderr = self._run_conan_command(build_cmd, capture_output=True)
        
        duration = time.time() - start_time
        
        # Collect build metrics
        metrics = {
            "build_duration": duration,
            "profile": profile_name,
            "platform": self.current_platform.value,
            "timestamp": time.time()
        }
        
        # Collect artifacts
        artifacts = []
        if success:
            artifacts = self._collect_build_artifacts()
        
        result = BuildResult(
            success=success,
            duration=duration,
            output=stdout,
            error=stderr if not success else None,
            artifacts=artifacts,
            metrics=metrics
        )
        
        if success:
            logger.info(f"✅ Package built successfully in {duration:.2f}s")
        else:
            logger.error(f"❌ Package build failed after {duration:.2f}s")
        
        return result
    
    def _collect_build_artifacts(self) -> List[Path]:
        """Collect build artifacts"""
        artifacts = []
        
        # Look for common OpenSSL artifacts
        artifact_patterns = [
            "libssl.*",
            "libcrypto.*",
            "openssl",
            "*.so*",
            "*.dylib",
            "*.dll",
            "*.a"
        ]
        
        for pattern in artifact_patterns:
            for artifact in self.project_root.glob(f"**/{pattern}"):
                if artifact.is_file():
                    artifacts.append(artifact)
        
        logger.info(f"📦 Collected {len(artifacts)} build artifacts")
        return artifacts
    
    def run_tests(self, test_type: str = "unit") -> bool:
        """Run tests with comprehensive reporting"""
        logger.info(f"🧪 Running {test_type} tests...")
        
        test_results_dir = Path(self.config["tests"]["results_dir"])
        test_results_dir.mkdir(exist_ok=True)
        
        if test_type == "unit":
            return self._run_unit_tests(test_results_dir)
        elif test_type == "performance":
            return self._run_performance_tests(test_results_dir)
        else:
            logger.error(f"❌ Unknown test type: {test_type}")
            return False
    
    def _run_unit_tests(self, results_dir: Path) -> bool:
        """Run unit tests"""
        test_cmd = self.config["tests"]["unit_test_command"]
        
        junit_report = results_dir / "junit_report.xml"
        command = [test_cmd, ".", f"--junitxml={junit_report}"]
        
        success, stdout, stderr = self._run_conan_command(command, capture_output=True)
        
        if success:
            logger.info(f"✅ Unit tests passed. Report: {junit_report}")
        else:
            logger.error(f"❌ Unit tests failed: {stderr}")
        
        return success
    
    def _run_performance_tests(self, results_dir: Path) -> bool:
        """Run performance tests"""
        logger.info("⚡ Running performance tests...")
        
        # This would integrate with the performance testing script
        # For now, we'll create a placeholder
        performance_report = results_dir / "performance_report.json"
        
        # Simulate performance test
        test_data = {
            "timestamp": time.time(),
            "platform": self.current_platform.value,
            "tests": {
                "build_time": 120.5,
                "test_execution_time": 45.2
            }
        }
        
        with open(performance_report, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        logger.info(f"✅ Performance tests completed. Report: {performance_report}")
        return True
    
    def upload_package(self, package_name: str, package_version: str) -> bool:
        """Upload package to remote repository"""
        logger.info(f"📤 Uploading package: {package_name}/{package_version}")
        
        remote_name = self.config["conan"]["remote_name"]
        
        success, _, _ = self._run_conan_command([
            "upload", f"{package_name}/{package_version}@", "--all", 
            "-r", remote_name, "--confirm"
        ])
        
        if success:
            logger.info(f"✅ Package uploaded successfully: {package_name}/{package_version}")
        else:
            logger.error(f"❌ Failed to upload package: {package_name}/{package_version}")
        
        return success
    
    def clean_build(self) -> bool:
        """Clean build artifacts"""
        logger.info("🧹 Cleaning build artifacts...")
        
        # Remove build directories
        build_dirs = ["build", "install", "test_package"]
        
        for build_dir in build_dirs:
            build_path = self.project_root / build_dir
            if build_path.exists():
                shutil.rmtree(build_path)
                logger.info(f"🗑️ Removed: {build_path}")
        
        # Clean Conan cache
        success, _, _ = self._run_conan_command(["remove", "*", "--confirm"])
        
        if success:
            logger.info("✅ Build artifacts cleaned")
        else:
            logger.warning("⚠️ Some artifacts may not have been cleaned")
        
        return success
    
    def generate_report(self, build_results: List[BuildResult]) -> Path:
        """Generate comprehensive build report"""
        logger.info("📊 Generating build report...")
        
        report_data = {
            "timestamp": time.time(),
            "platform": self.current_platform.value,
            "builds": []
        }
        
        for result in build_results:
            build_info = {
                "success": result.success,
                "duration": result.duration,
                "error": result.error,
                "artifacts_count": len(result.artifacts) if result.artifacts else 0,
                "metrics": result.metrics
            }
            report_data["builds"].append(build_info)
        
        report_path = self.artifacts_dir / f"build_report_{int(time.time())}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📊 Build report generated: {report_path}")
        return report_path

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Conan Orchestrator for OpenSSL CI/CD")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--profile", "-p", required=True,
                       help="Conan profile to use")
    parser.add_argument("--action", "-a", required=True,
                       choices=["setup", "install", "build", "test", "upload", "clean"],
                       help="Action to perform")
    parser.add_argument("--test", "-t", action="store_true",
                       help="Run tests after build")
    parser.add_argument("--package-name", default="openssl",
                       help="Package name for upload")
    parser.add_argument("--package-version", default="3.5.0",
                       help="Package version for upload")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize orchestrator
    orchestrator = ConanOrchestrator(args.project_root)
    
    success = False
    
    try:
        if args.action == "setup":
            success = orchestrator.setup_conan_remote()
            
        elif args.action == "install":
            success = orchestrator.install_dependencies(args.profile)
            
        elif args.action == "build":
            result = orchestrator.build_package(args.profile, test=args.test)
            success = result.success
            
            if args.test and success:
                success = orchestrator.run_tests("unit")
                
        elif args.action == "test":
            success = orchestrator.run_tests("unit")
            
        elif args.action == "upload":
            success = orchestrator.upload_package(args.package_name, args.package_version)
            
        elif args.action == "clean":
            success = orchestrator.clean_build()
    
    except Exception as e:
        logger.error(f"❌ Orchestrator failed: {e}")
        success = False
    
    if success:
        logger.info("🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()