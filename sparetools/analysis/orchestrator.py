"""
Knowledge-Aware Analysis Orchestrator

Layer 4-5: Executes workflows using learned patterns and captures new learning
"""

from pathlib import Path
from typing import Dict, List, Optional
import time

from sparetools.mcp.client import get_mcp_client
from sparetools.context.detector import ProjectContextDetector, ProjectContext
from sparetools.learning.auto_orchestrator import AutomatedLearningOrchestrator


class KnowledgeAwareOrchestrator:
    """Orchestrate analysis using MCP knowledge (Layers 2-5)"""

    def __init__(self, knowledge_base_path: Optional[Path] = None):
        if knowledge_base_path is None:
            knowledge_base_path = Path.home() / ".sparetools"

        self.mcp_client = get_mcp_client(knowledge_base_path)
        self.context_detector = ProjectContextDetector()
        self.auto_learning = AutomatedLearningOrchestrator(knowledge_base_path)

    async def initialize(self):
        """Initialize MCP connections and automated learning"""
        await self.mcp_client.initialize()
        await self.auto_learning.initialize()

    async def analyze_project(self, project_path: Path,
                             goal: str = "comprehensive") -> Dict:
        """
        Analyze project using learned patterns

        Args:
            project_path: Path to project root
            goal: Analysis goal (bug_finding, performance, security, quality)
        """
        print(f"🔍 Analyzing {project_path.name}...")

        # Layer 1: Detect context
        context = self.context_detector.detect(project_path)
        print(f"📋 Context: {context.project_type.value} project")
        print(f"   Languages: {', '.join(context.languages)}")
        print(f"   Build: {context.build_system}")
        print(f"   Performance critical: {context.performance_critical}")

        # Layer 2-3: Query episodic and semantic memory
        learned_pattern = await self._query_knowledge(context, goal)

        if learned_pattern.get("found"):
            print(f"💡 Found learned pattern: {learned_pattern['pattern']['name']}")
            workflow = learned_pattern["pattern"]
        else:
            print("🆕 No learned pattern found - using defaults")
            workflow = self._default_workflow(context, goal)

        # Layer 4: Execute procedural workflow
        results = await self._execute_workflow(project_path, context, workflow)

        # Layer 5: Meta-cognitive automated learning
        learning_triggered = await self.auto_learning.evaluate_learning_opportunity(context, results)

        if learning_triggered:
            print("🎓 Automated learning opportunity detected!")
            learning_results = await self.auto_learning.execute_learning_session(context, results)
            results['automated_learning'] = learning_results
            print(f"✅ Automated learning session completed: {learning_results.get('patterns_captured', 0)} patterns captured")

        return results

    async def _query_knowledge(self, context: ProjectContext, goal: str) -> Dict:
        """Query MCP for relevant knowledge"""

        # First try project-specific patterns (e.g., "mia" patterns)
        project_name = context.name.lower()
        knowledge = await self.mcp_client.query_development_knowledge(project_name, goal)

        if knowledge.get("found"):
            return knowledge

        # Then try domain + goal patterns
        domain = context.project_type.value
        topic = f"{goal} analysis"

        knowledge = await self.mcp_client.query_development_knowledge(domain, topic)

        # If no specific pattern found, look for general domain patterns
        if not knowledge.get("found"):
            knowledge = await self.mcp_client.query_development_knowledge(domain, "analysis")

        return knowledge

    def _default_workflow(self, context: ProjectContext, goal: str) -> Dict:
        """Default analysis workflow based on project type"""

        if context.project_type.value == "embedded_esp32":
            return {
                "name": f"analyze-{context.project_type.value}-{goal}",
                "description": f"Default {goal} analysis for ESP32 projects",
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
                },
                "effectiveness": 0.5
            }

        elif context.project_type.value == "android_app":
            return {
                "name": f"analyze-{context.project_type.value}-{goal}",
                "description": f"Default {goal} analysis for Android projects",
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
                },
                "effectiveness": 0.5
            }

        elif context.project_type.value == "python_cli":
            return {
                "name": f"analyze-{context.project_type.value}-{goal}",
                "description": f"Default {goal} analysis for Python projects",
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
                },
                "effectiveness": 0.5
            }

        else:
            return {
                "name": f"analyze-{context.project_type.value}-{goal}",
                "description": f"Default {goal} analysis for {context.project_type.value} projects",
                "steps": ["Basic file structure check"],
                "tools_used": [],
                "configs": {},
                "effectiveness": 0.3
            }

    async def _execute_workflow(self, project_path: Path,
                               context: ProjectContext,
                               workflow: Dict) -> Dict:
        """Execute the analysis workflow"""

        results = {
            "success": True,
            "workflow_name": workflow["name"],
            "steps_executed": [],
            "findings": [],
            "tools_used": workflow.get("tools_used", []),
            "goal": workflow.get("goal", "general")
        }

        print("🔧 Executing workflow:")
        for step in workflow.get("steps", []):
            print(f"   • {step}")
            results["steps_executed"].append(step)

        # Simulate analysis execution
        # In real implementation, this would run actual tools
        results["findings"] = [
            "Example finding 1: Code quality issue detected",
            "Example finding 2: Performance optimization opportunity"
        ]

        # Check if this is novel (different from learned patterns)
        results["novel_findings"] = self._identify_novel_patterns(results, workflow)

        return results

    def _identify_novel_patterns(self, results: Dict, workflow: Dict) -> bool:
        """Check if analysis revealed novel insights"""

        # Simple heuristic: if we have findings but workflow is default,
        # consider it potentially novel
        if results.get("findings") and workflow.get("effectiveness", 0) < 0.6:
            return True

        # TODO: More sophisticated novelty detection
        return False

    async def _capture_learning(self, context: ProjectContext,
                               results: Dict, goal: str):
        """Capture successful patterns for future use"""

        # Synthesize the pattern that worked
        pattern_description = self._synthesize_pattern(context, results)

        # Store in MCP knowledge base
        await self.mcp_client.capture_development_learning(
            domain=context.project_type.value,
            pattern=pattern_description,
            context=f"Analysis of {context.name} for {goal}",
            tags=[
                context.project_type.value,
                context.build_system,
                goal,
                "analysis",
                "learned"
            ] + context.languages
        )

    def _synthesize_pattern(self, context: ProjectContext, results: Dict) -> str:
        """Create textual description of successful pattern"""

        workflow = results.get("workflow_name", "unknown")

        return f"""For {context.project_type.value} projects with:
- Languages: {', '.join(context.languages)}
- Build system: {context.build_system}
- Performance critical: {context.performance_critical}

Successful {results.get('goal', 'analysis')} approach:
1. {results['steps_executed'][0] if results['steps_executed'] else 'Analysis step'}

Key findings:
- {results['findings'][0] if results['findings'] else 'Code quality checks'}

Configuration that worked:
{{
  "tools": {results.get('tools_used', [])},
  "steps": {results.get('steps_executed', [])}
}}

This pattern was effective for {context.name} project."""