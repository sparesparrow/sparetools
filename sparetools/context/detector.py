"""
Project Context Detection for Sparetools Cognitive Architecture

Layer 1: Perceptual - Detects project characteristics automatically
"""

import os
from pathlib import Path
from typing import Dict, List
from enum import Enum


class ProjectType(Enum):
    """Project type classifications"""
    EMBEDDED_ESP32 = "embedded_esp32"
    ANDROID_APP = "android_app"
    PYTHON_CLI = "python_cli"
    CPP_LIBRARY = "cpp_library"
    MIXED = "mixed"


class ProjectContext:
    """Detected project characteristics"""

    def __init__(self, path: str, name: str, project_type: ProjectType,
                 languages: List[str], build_system: str, has_tests: bool,
                 has_ci: bool, frameworks: List[str], performance_critical: bool,
                 security_sensitive: bool):
        self.path = path
        self.name = name
        self.project_type = project_type
        self.languages = languages
        self.build_system = build_system
        self.has_tests = has_tests
        self.has_ci = has_ci
        self.frameworks = frameworks
        self.performance_critical = performance_critical
        self.security_sensitive = security_sensitive

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "path": self.path,
            "name": self.name,
            "project_type": self.project_type.value,
            "languages": self.languages,
            "build_system": self.build_system,
            "has_tests": self.has_tests,
            "has_ci": self.has_ci,
            "frameworks": self.frameworks,
            "performance_critical": self.performance_critical,
            "security_sensitive": self.security_sensitive
        }


class ProjectContextDetector:
    """Detect project type and characteristics (Layer 1: Perceptual)"""

    def detect(self, project_path: Path) -> ProjectContext:
        """Analyze project structure and return context"""

        name = project_path.name
        project_type = self._detect_type(project_path)

        return ProjectContext(
            path=str(project_path),
            name=name,
            project_type=project_type,
            languages=self._detect_languages(project_path),
            build_system=self._detect_build_system(project_path),
            has_tests=self._has_tests(project_path),
            has_ci=self._has_ci(project_path),
            frameworks=self._detect_frameworks(project_path),
            performance_critical=self._is_performance_critical(project_path),
            security_sensitive=self._is_security_sensitive(project_path)
        )

    def _detect_type(self, path: Path) -> ProjectType:
        """Determine primary project type"""
        if (path / "platformio.ini").exists():
            return ProjectType.EMBEDDED_ESP32
        elif (path / "build.gradle.kts").exists() or (path / "app" / "build.gradle.kts").exists():
            return ProjectType.ANDROID_APP
        elif (path / "conanfile.py").exists():
            return ProjectType.CPP_LIBRARY
        elif (path / "setup.py").exists() or (path / "pyproject.toml").exists():
            # Check for C++ extensions
            if (path / "CMakeLists.txt").exists():
                return ProjectType.MIXED
            return ProjectType.PYTHON_CLI
        return ProjectType.PYTHON_CLI  # Default

    def _detect_languages(self, path: Path) -> List[str]:
        """Detect programming languages used"""
        languages = set()

        extensions = {
            ".py": "python",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".kt": "kotlin",
            ".java": "java",
            ".rs": "rust"
        }

        for ext, lang in extensions.items():
            if list(path.rglob(f"*{ext}")):
                languages.add(lang)

        return list(languages)

    def _detect_build_system(self, path: Path) -> str:
        """Identify build system"""
        if (path / "platformio.ini").exists():
            return "platformio"
        elif (path / "CMakeLists.txt").exists():
            return "cmake"
        elif (path / "conanfile.py").exists():
            return "conan"
        elif (path / "setup.py").exists():
            return "setuptools"
        elif (path / "pyproject.toml").exists():
            return "poetry"
        elif (path / "build.gradle.kts").exists():
            return "gradle"
        return "unknown"

    def _has_tests(self, path: Path) -> bool:
        """Check if project has tests"""
        test_indicators = [
            "tests/", "test/", "spec/",
            "pytest.ini", "jest.config.js",
            ".github/workflows/"
        ]
        return any((path / indicator).exists() for indicator in test_indicators)

    def _has_ci(self, path: Path) -> bool:
        """Check for CI configuration"""
        ci_files = [
            ".github/workflows/",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
            "azure-pipelines.yml"
        ]
        return any((path / ci_file).exists() for ci_file in ci_files)

    def _detect_frameworks(self, path: Path) -> List[str]:
        """Detect frameworks and libraries"""
        frameworks = []

        # Check Python frameworks
        if (path / "requirements.txt").exists():
            with open(path / "requirements.txt") as f:
                content = f.read()
                if "flask" in content:
                    frameworks.append("flask")
                if "fastapi" in content:
                    frameworks.append("fastapi")
                if "click" in content:
                    frameworks.append("click")

        # Check C++ frameworks
        if (path / "conanfile.py").exists():
            with open(path / "conanfile.py") as f:
                content = f.read()
                if "openssl" in content:
                    frameworks.append("openssl")
                if "flatbuffers" in content:
                    frameworks.append("flatbuffers")

        # Check embedded frameworks
        if (path / "platformio.ini").exists():
            frameworks.append("arduino")

        return frameworks

    def _is_performance_critical(self, path: Path) -> bool:
        """Heuristic: performance-critical projects"""
        indicators = [
            "embedded",
            "real-time",
            "bpm-detector",
            "audio"
        ]
        path_str = str(path).lower()
        return any(indicator in path_str for indicator in indicators)

    def _is_security_sensitive(self, path: Path) -> bool:
        """Heuristic: security-sensitive projects"""
        indicators = [
            "auth",
            "credential",
            "password",
            "openssl",
            "crypto"
        ]

        # Check path
        path_str = str(path).lower()
        if any(indicator in path_str for indicator in indicators):
            return True

        # Check for security-related files
        security_files = [
            "*.key", "*.pem", "*.cert",
            "secrets.yaml", ".env"
        ]
        return any(list(path.rglob(pattern)) for pattern in security_files)