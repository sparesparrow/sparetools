#!/usr/bin/env python3
"""
Sparetools MCP Integration - Quick Start Implementation
========================================================

This file contains working code you can run TODAY to start building
the self-improving development intelligence system.

Usage:
    python sparetools_mcp_quickstart.py --mode setup
    python sparetools_mcp_quickstart.py --mode analyze --project esp32-bpm-detector
    python sparetools_mcp_quickstart.py --mode learn --project mia
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ProjectType(Enum):
    """Project type classifications"""
    EMBEDDED_ESP32 = "embedded_esp32"
    ANDROID_APP = "android_app"
    PYTHON_CLI = "python_cli"
    CPP_LIBRARY = "cpp_library"
    MIXED = "mixed"


@dataclass
class ProjectContext:
    """Detected project characteristics (Layer 1: Perceptual)"""
    path: str
    name: str
    project_type: ProjectType
    languages: List[str]
    build_system: str
    has_tests: bool
    has_ci: bool
    frameworks: List[str]
    performance_critical: bool
    security_sensitive: bool


class SimpleContextDetector:
    """Lightweight context detection for quick start"""
    
    def detect(self, project_path: Path) -> ProjectContext:
        """Analyze project structure"""
        
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
        """Determine project type from structure"""
        if (path / "platformio.ini").exists():
            return ProjectType.EMBEDDED_ESP32
        elif (path / "build.gradle.kts").exists() or (path / "app" / "build.gradle.kts").exists():
            return ProjectType.ANDROID_APP
        elif (path / "conanfile.py").exists():
            return ProjectType.CPP_LIBRARY
        elif (path / "setup.py").exists() or (path / "pyproject.toml").exists():
            if (path / "CMakeLists.txt").exists():
                return ProjectType.MIXED
            return ProjectType.PYTHON_CLI
        return ProjectType.PYTHON_CLI
    
    def _detect_languages(self, path: Path) -> List[str]:
        """Quick language detection"""
        languages = []
        if list(path.rglob("*.py")):
            languages.append("python")
        if list(path.rglob("*.cpp")) or list(path.rglob("*.c")):
            languages.append("cpp")
        if list(path.rglob("*.kt")):
            languages.append("kotlin")
        return languages
    
    def _detect_build_system(self, path: Path) -> str:
        """Identify build system"""
        systems = {
            "platformio.ini": "platformio",
            "CMakeLists.txt": "cmake",
            "conanfile.py": "conan",
            "setup.py": "setuptools",
            "build.gradle.kts": "gradle"
        }
        for file, system in systems.items():
            if (path / file).exists():
                return system
        return "unknown"
    
    def _has_tests(self, path: Path) -> bool:
        """Check for test infrastructure"""
        return any((path / d).exists() for d in ["tests", "test", "spec"])
    
    def _has_ci(self, path: Path) -> bool:
        """Check for CI configuration"""
        return (path / ".github" / "workflows").exists()
    
    def _detect_frameworks(self, path: Path) -> List[str]:
        """Detect major frameworks"""
        frameworks = []
        if (path / "platformio.ini").exists():
            frameworks.append("arduino-esp32")
        # Add more framework detection as needed
        return frameworks
    
    def _is_performance_critical(self, path: Path) -> bool:
        """Heuristic for performance sensitivity"""
        critical_keywords = ["embedded", "real-time", "bpm", "audio"]
        return any(kw in str(path).lower() for kw in critical_keywords)
    
    def _is_security_sensitive(self, path: Path) -> bool:
        """Heuristic for security sensitivity"""
        sensitive_keywords = ["auth", "credential", "openssl", "crypto"]
        return any(kw in str(path).lower() for kw in sensitive_keywords)


class LocalPromptStore:
    """Simple file-based prompt storage (before MCP integration)"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def store_prompt(self, name: str, content: Dict):
        """Store a prompt locally"""
        file_path = self.storage_path / f"{name}.json"
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"✓ Stored prompt: {name}")
    
    def get_prompt(self, name: str) -> Optional[Dict]:
        """Retrieve a prompt"""
        file_path = self.storage_path / f"{name}.json"
        if not file_path.exists():
            return None
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_prompts(self, tag: Optional[str] = None) -> List[str]:
        """List stored prompts"""
        prompts = []
        for file in self.storage_path.glob("*.json"):
            if tag:
                # Simple tag filtering
                with open(file, 'r') as f:
                    data = json.load(f)
                    if tag in data.get('tags', []):
                        prompts.append(file.stem)
            else:
                prompts.append(file.stem)
        return prompts


class KnowledgeCapture:
    """Capture development knowledge (Layer 5: Meta-cognitive)"""
    
    def __init__(self, storage_path: Path):
        self.prompt_store = LocalPromptStore(storage_path / "prompts")
        self.episodes_path = storage_path / "episodes"
        self.episodes_path.mkdir(parents=True, exist_ok=True)
    
    def capture_analysis_pattern(self, context: ProjectContext, 
                                 analysis_results: Dict,
                                 what_worked: str):
        """Capture a successful analysis pattern"""
        
        # Generate unique name
        pattern_name = f"analyze-{context.project_type.value}-{context.build_system}"
        
        # Store as prompt
        prompt_content = {
            "name": pattern_name,
            "description": f"Analysis workflow for {context.project_type.value} projects",
            "layer": "Procedural",
            "domain": context.project_type.value,
            "context": {
                "path": context.path,
                "name": context.name,
                "project_type": context.project_type.value,  # Convert enum to string
                "languages": context.languages,
                "build_system": context.build_system,
                "has_tests": context.has_tests,
                "has_ci": context.has_ci,
                "frameworks": context.frameworks,
                "performance_critical": context.performance_critical,
                "security_sensitive": context.security_sensitive
            },
            "workflow": {
                "steps": analysis_results.get("steps", []),
                "tools_used": analysis_results.get("tools_used", []),
                "configurations": analysis_results.get("configs", {})
            },
            "what_worked": what_worked,
            "tags": [
                context.project_type.value,
                context.build_system,
                *context.languages,
                "analysis"
            ],
            "effectiveness": {
                "usage_count": 1,
                "success_rate": 1.0
            }
        }
        
        self.prompt_store.store_prompt(pattern_name, prompt_content)
        
        # Also store as episode memory
        episode_file = self.episodes_path / f"{context.name}_{len(list(self.episodes_path.glob('*')))}.json"
        with open(episode_file, 'w') as f:
            json.dump({
                "context": {
                    "path": context.path,
                    "name": context.name,
                    "project_type": context.project_type.value,  # Convert enum to string
                    "languages": context.languages,
                    "build_system": context.build_system,
                    "has_tests": context.has_tests,
                    "has_ci": context.has_ci,
                    "frameworks": context.frameworks,
                    "performance_critical": context.performance_critical,
                    "security_sensitive": context.security_sensitive
                },
                "analysis": analysis_results,
                "learning": what_worked
            }, f, indent=2)
        
        print(f"\n💡 Captured new pattern: {pattern_name}")
        print(f"   Tags: {', '.join(prompt_content['tags'])}")


class SimplifiedAnalyzer:
    """Quick-start analyzer before full MCP integration"""
    
    def __init__(self, knowledge_base_path: Path):
        self.detector = SimpleContextDetector()
        self.knowledge = KnowledgeCapture(knowledge_base_path)
    
    def analyze_project(self, project_path: Path) -> Dict:
        """Analyze project using simple heuristics"""
        
        print(f"\n🔍 Analyzing {project_path.name}...")
        
        # Layer 1: Detect context
        context = self.detector.detect(project_path)
        print(f"\n📋 Project Context:")
        print(f"   Type: {context.project_type.value}")
        print(f"   Languages: {', '.join(context.languages)}")
        print(f"   Build: {context.build_system}")
        print(f"   Performance critical: {context.performance_critical}")
        
        # Layer 2-4: Check if we have learned patterns
        pattern_name = f"analyze-{context.project_type.value}-{context.build_system}"
        learned_pattern = self.knowledge.prompt_store.get_prompt(pattern_name)
        
        if learned_pattern:
            print(f"\n💡 Using learned pattern: {pattern_name}")
            print(f"   Previous success rate: {learned_pattern['effectiveness']['success_rate']}")
            workflow = learned_pattern['workflow']
        else:
            print(f"\n🆕 No learned pattern found - using defaults")
            workflow = self._default_workflow(context)
        
        # Execute analysis (simplified for quick start)
        results = self._execute_workflow(project_path, context, workflow)
        
        return {
            "context": context,
            "workflow": workflow,
            "results": results
        }
    
    def _default_workflow(self, context: ProjectContext) -> Dict:
        """Default analysis workflow based on project type"""
        
        if context.project_type == ProjectType.EMBEDDED_ESP32:
            return {
                "steps": [
                    "Check PlatformIO configuration",
                    "Run static analysis on C++ code",
                    "Check memory usage patterns",
                    "Verify timing constraints"
                ],
                "tools_used": ["platformio", "cppcheck"],
                "configs": {
                    "cppcheck": {
                        "enable": ["warning", "performance", "portability"],
                        "platform": "unix32"
                    }
                }
            }
        
        elif context.project_type == ProjectType.ANDROID_APP:
            return {
                "steps": [
                    "Run Kotlin lint",
                    "Build APK",
                    "Check for security issues"
                ],
                "tools_used": ["gradle", "ktlint"],
                "configs": {
                    "gradle": {
                        "tasks": ["clean", "build", "lintDebug"]
                    }
                }
            }
        
        elif context.project_type == ProjectType.PYTHON_CLI:
            return {
                "steps": [
                    "Run pylint/flake8",
                    "Check dependencies",
                    "Run tests if available"
                ],
                "tools_used": ["pylint", "pytest"],
                "configs": {
                    "pylint": {
                        "disable": ["C0111"]  # Missing docstrings
                    }
                }
            }
        
        else:
            return {
                "steps": ["Basic file structure check"],
                "tools_used": [],
                "configs": {}
            }
    
    def _execute_workflow(self, project_path: Path, 
                         context: ProjectContext, 
                         workflow: Dict) -> Dict:
        """Execute the analysis workflow (simplified)"""
        
        results = {
            "steps_executed": [],
            "findings": [],
            "tools_used": workflow['tools_used']
        }
        
        print(f"\n🔧 Executing workflow:")
        for step in workflow['steps']:
            print(f"   • {step}")
            results["steps_executed"].append(step)
        
        # In real implementation, actually run tools here
        # For now, just simulate
        results["findings"] = [
            "Example finding 1: Code quality issue detected",
            "Example finding 2: Performance optimization opportunity"
        ]
        
        return results


def setup_environment():
    """Initialize the sparetools knowledge base"""
    
    print("🚀 Setting up Sparetools Knowledge Base...")
    
    # Create directory structure
    base_path = Path.home() / ".sparetools"
    base_path.mkdir(exist_ok=True)
    
    (base_path / "prompts").mkdir(exist_ok=True)
    (base_path / "episodes").mkdir(exist_ok=True)
    (base_path / "cache").mkdir(exist_ok=True)
    
    print(f"✓ Created knowledge base at {base_path}")
    
    # Create sample initial prompts
    knowledge = KnowledgeCapture(base_path)
    
    # ESP32 example prompt
    knowledge.prompt_store.store_prompt(
        "cppcheck-esp32-baseline",
        {
            "name": "cppcheck-esp32-baseline",
            "description": "Baseline C++ analysis for ESP32 projects",
            "content": """
For ESP32 embedded projects:
1. Use cppcheck with --platform=unix32
2. Enable: warning, performance, portability checks
3. Focus on memory usage and timing constraints
4. Check for blocking calls in ISRs
""",
            "tags": ["esp32", "embedded", "cppcheck", "baseline"],
            "layer": "Procedural"
        }
    )
    
    print("\n✓ Initial knowledge base populated")
    print(f"\nYou can now run:")
    print(f"  python {__file__} --mode analyze --project <path>")


def analyze_project(project_name: str):
    """Analyze a specific project"""
    
    # Map project names to paths
    projects_base = Path.home() / "projects"
    project_paths = {
        "esp32-bpm-detector": projects_base / "embedded" / "esp32-bpm-detector",
        "mia": projects_base / "oms" / "mia",
        "cliphist-android": projects_base / "cliphist-android",
        "sparetools": projects_base / "dev-tools" / "sparetools"
    }
    
    project_path = project_paths.get(project_name)
    if not project_path or not project_path.exists():
        print(f"❌ Project '{project_name}' not found at {project_path}")
        print(f"Available projects: {', '.join(project_paths.keys())}")
        return
    
    # Run analysis
    base_path = Path.home() / ".sparetools"
    analyzer = SimplifiedAnalyzer(base_path)
    
    analysis_results = analyzer.analyze_project(project_path)
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"   Steps executed: {len(analysis_results['results']['steps_executed'])}")
    print(f"   Findings: {len(analysis_results['results']['findings'])}")
    
    # Ask if we should capture this
    print(f"\n❓ Did this analysis help? Capture the pattern? (y/n)")
    response = input("> ").strip().lower()
    
    if response == 'y':
        what_worked = input("What worked well? > ").strip()
        analyzer.knowledge.capture_analysis_pattern(
            analysis_results['context'],
            analysis_results['results'],
            what_worked
        )


def learn_mode(project_name: str):
    """Interactive learning mode"""
    
    print(f"\n🎓 Teaching Sparetools about {project_name}...")
    print("This mode captures YOUR expertise as reusable prompts")
    
    print("\nDescribe the analysis workflow you use for this project:")
    print("(Type 'done' when finished)\n")
    
    steps = []
    while True:
        step = input(f"Step {len(steps)+1}: ").strip()
        if step.lower() == 'done':
            break
        steps.append(step)
    
    tools = input("\nWhich tools do you use? (comma-separated): ").strip().split(',')
    tools = [t.strip() for t in tools if t.strip()]
    
    tags = input("Tags for this workflow (comma-separated): ").strip().split(',')
    tags = [t.strip() for t in tags if t.strip()]
    
    # Store the learned workflow
    base_path = Path.home() / ".sparetools"
    knowledge = KnowledgeCapture(base_path)
    
    prompt_name = f"workflow-{project_name}-{tags[0] if tags else 'custom'}"
    knowledge.prompt_store.store_prompt(
        prompt_name,
        {
            "name": prompt_name,
            "description": f"Learned workflow for {project_name}",
            "steps": steps,
            "tools_used": tools,
            "tags": tags + [project_name],
            "layer": "Procedural",
            "source": "interactive_learning"
        }
    )
    
    print(f"\n✅ Learned workflow stored as '{prompt_name}'")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sparetools MCP Quick Start")
    parser.add_argument('--mode', choices=['setup', 'analyze', 'learn', 'list'],
                       required=True, help="Operation mode")
    parser.add_argument('--project', help="Project name")
    
    args = parser.parse_args()
    
    if args.mode == 'setup':
        setup_environment()
    
    elif args.mode == 'analyze':
        if not args.project:
            print("❌ --project required for analyze mode")
            return
        analyze_project(args.project)
    
    elif args.mode == 'learn':
        if not args.project:
            print("❌ --project required for learn mode")
            return
        learn_mode(args.project)
    
    elif args.mode == 'list':
        base_path = Path.home() / ".sparetools"
        store = LocalPromptStore(base_path / "prompts")
        prompts = store.list_prompts()
        
        print(f"\n📚 Stored Knowledge ({len(prompts)} prompts):")
        for prompt_name in prompts:
            prompt = store.get_prompt(prompt_name)
            tags = prompt.get('tags', [])
            print(f"   • {prompt_name}")
            print(f"     Tags: {', '.join(tags)}")
            print(f"     Layer: {prompt.get('layer', 'Unknown')}")
            print()


if __name__ == '__main__':
    main()
