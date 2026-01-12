# Sparetools MCP Integration Plan

## Phase 1: Foundation (Weeks 1-2)

### 1.1 MCP Client Infrastructure

**File: `sparetools/mcp/client.py`**

Create a robust MCP client that wraps both mcp-prompts and unified-dev-tools:

```python
from typing import Dict, List, Optional
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SparetoolsMCPClient:
    """Unified client for mcp-prompts and unified-dev-tools servers"""
    
    def __init__(self):
        self.prompts_session: Optional[ClientSession] = None
        self.devtools_session: Optional[ClientSession] = None
    
    async def connect_prompts(self):
        """Connect to mcp-prompts server"""
        server_params = StdioServerParameters(
            command="node",
            args=["/path/to/mcp-prompts/dist/index.js"],
            env={"STORAGE_TYPE": "file", "STORAGE_PATH": "~/.sparetools/prompts"}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.prompts_session = session
                
    async def connect_devtools(self):
        """Connect to unified-dev-tools server"""
        server_params = StdioServerParameters(
            command="node",
            args=["/path/to/unified-dev-tools/build/index.js"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.devtools_session = session
    
    async def query_knowledge(self, domain: str, topic: str) -> Dict:
        """Query development knowledge from unified-dev-tools"""
        result = await self.devtools_session.call_tool(
            "query_development_knowledge",
            arguments={"domain": domain, "topic": topic}
        )
        return result
    
    async def capture_learning(self, domain: str, pattern: str, 
                               context: str, tags: List[str]) -> Dict:
        """Capture new development learning"""
        result = await self.devtools_session.call_tool(
            "capture_development_learning",
            arguments={
                "domain": domain,
                "pattern": pattern,
                "context": context,
                "tags": tags
            }
        )
        return result
    
    async def store_prompt(self, name: str, description: str, 
                          content: str, metadata: Dict) -> Dict:
        """Store a prompt in mcp-prompts"""
        result = await self.prompts_session.call_tool(
            "add_prompt",
            arguments={
                "name": name,
                "description": description,
                "content": content,
                "metadata": metadata
            }
        )
        return result
    
    async def get_prompt(self, name: str) -> Dict:
        """Retrieve a prompt by name"""
        result = await self.prompts_session.call_tool(
            "get_prompt",
            arguments={"name": name}
        )
        return result
    
    async def list_prompts(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """List prompts with optional tag filtering"""
        result = await self.prompts_session.call_tool(
            "list_prompts",
            arguments={"tags": tags} if tags else {}
        )
        return result
```

### 1.2 Project Context Detection

**File: `sparetools/context/detector.py`**

Implement perceptual layer to understand project characteristics:

```python
import os
from pathlib import Path
from typing import Dict, List
from enum import Enum

class ProjectType(Enum):
    PYTHON_CLI = "python_cli"
    CPP_LIBRARY = "cpp_library"
    EMBEDDED_FIRMWARE = "embedded_firmware"
    ANDROID_APP = "android_app"
    MIXED_PYTHON_CPP = "mixed_python_cpp"

class ProjectContextDetector:
    """Detect project type and characteristics (Layer 1: Perceptual)"""
    
    def detect(self, project_path: Path) -> Dict:
        """Analyze project structure and return context"""
        context = {
            "project_path": str(project_path),
            "project_type": self._detect_type(project_path),
            "languages": self._detect_languages(project_path),
            "build_system": self._detect_build_system(project_path),
            "has_tests": self._has_tests(project_path),
            "has_ci": self._has_ci(project_path),
            "frameworks": self._detect_frameworks(project_path),
            "performance_critical": self._is_performance_critical(project_path),
            "security_sensitive": self._is_security_sensitive(project_path)
        }
        return context
    
    def _detect_type(self, path: Path) -> ProjectType:
        """Determine primary project type"""
        if (path / "platformio.ini").exists():
            return ProjectType.EMBEDDED_FIRMWARE
        elif (path / "build.gradle.kts").exists():
            return ProjectType.ANDROID_APP
        elif (path / "conanfile.py").exists():
            return ProjectType.CPP_LIBRARY
        elif (path / "setup.py").exists() or (path / "pyproject.toml").exists():
            # Check for C++ extensions
            if (path / "CMakeLists.txt").exists():
                return ProjectType.MIXED_PYTHON_CPP
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
```

### 1.3 Knowledge-Aware Analysis Orchestrator

**File: `sparetools/analysis/orchestrator.py`**

Bridge between detection, MCP knowledge, and tool execution:

```python
from typing import Dict, List, Optional
from pathlib import Path
import asyncio

from sparetools.mcp.client import SparetoolsMCPClient
from sparetools.context.detector import ProjectContextDetector

class KnowledgeAwareOrchestrator:
    """Orchestrate analysis using MCP knowledge (Layers 2-5)"""
    
    def __init__(self):
        self.mcp_client = SparetoolsMCPClient()
        self.context_detector = ProjectContextDetector()
    
    async def analyze_project(self, project_path: Path, 
                             goal: str = "comprehensive") -> Dict:
        """
        Analyze project using learned patterns
        
        Args:
            project_path: Path to project root
            goal: Analysis goal (bug_finding, performance, security, quality)
        """
        # Layer 1: Detect context
        context = self.context_detector.detect(project_path)
        print(f"📍 Detected context: {context['project_type']}")
        
        # Layer 2: Query episodic memory - have we seen this before?
        similar_episodes = await self.mcp_client.query_knowledge(
            domain=context['project_type'].value,
            topic=f"{goal} analysis patterns"
        )
        
        if similar_episodes.get("found"):
            print(f"💡 Found {len(similar_episodes['patterns'])} similar cases")
            workflow_name = similar_episodes['recommended_workflow']
        else:
            # Layer 3: Use semantic knowledge - general best practices
            print("🧠 Using general domain knowledge")
            workflow_name = self._select_default_workflow(context, goal)
        
        # Layer 4: Execute procedural workflow
        results = await self._execute_workflow(
            project_path, 
            workflow_name, 
            context
        )
        
        # Layer 5: Meta-cognitive - should we save this?
        if results['success'] and results.get('novel_findings'):
            print("💾 Capturing new learning...")
            await self._capture_learning(context, results)
        
        return results
    
    async def _execute_workflow(self, project_path: Path, 
                                workflow_name: str, 
                                context: Dict) -> Dict:
        """Execute analysis workflow based on project type"""
        
        if context['project_type'].value == "embedded_firmware":
            return await self._analyze_embedded(project_path, context)
        elif context['project_type'].value == "android_app":
            return await self._analyze_android(project_path, context)
        elif "cpp" in context['languages']:
            return await self._analyze_cpp(project_path, context)
        elif "python" in context['languages']:
            return await self._analyze_python(project_path, context)
        
        return {"success": False, "error": "Unsupported project type"}
    
    async def _analyze_embedded(self, project_path: Path, context: Dict) -> Dict:
        """Specialized analysis for embedded projects (esp32-bpm-detector)"""
        print("🔧 Running embedded-specific analysis...")
        
        # Query for ESP32-specific configuration
        esp32_config = await self.mcp_client.get_prompt(
            "cppcheck-config-esp32-embedded"
        )
        
        # Execute static analysis with learned configuration
        results = {
            "static_analysis": await self._run_cppcheck(
                project_path,
                esp32_config.get("parameters", {})
            ),
            "memory_analysis": await self._check_stack_usage(project_path),
            "timing_analysis": await self._check_real_time_constraints(project_path)
        }
        
        return {
            "success": True,
            "results": results,
            "novel_findings": self._identify_novel_patterns(results)
        }
    
    async def _analyze_android(self, project_path: Path, context: Dict) -> Dict:
        """Specialized analysis for Android projects (cliphist-android)"""
        print("📱 Running Android-specific analysis...")
        
        # Use unified-dev-tools Android capabilities
        devices = await self.mcp_client.devtools_session.call_tool(
            "android_device_list",
            arguments={}
        )
        
        if not devices.get("devices"):
            return {"success": False, "error": "No Android devices connected"}
        
        # Run ktlint, build, and install for testing
        results = {
            "lint": await self._run_ktlint(project_path),
            "build": await self._gradle_build(project_path),
            "device_tests": await self._run_on_device(project_path, devices["devices"][0])
        }
        
        return {
            "success": True,
            "results": results,
            "novel_findings": self._identify_novel_patterns(results)
        }
    
    async def _capture_learning(self, context: Dict, results: Dict):
        """Capture successful patterns for future use (Meta-cognitive layer)"""
        
        # Extract the pattern that worked
        pattern_description = self._synthesize_pattern(context, results)
        
        # Store in unified-dev-tools knowledge base
        await self.mcp_client.capture_learning(
            domain=context['project_type'].value,
            pattern=pattern_description,
            context=str(context),
            tags=self._generate_tags(context, results)
        )
        
        # Also store as reusable prompt in mcp-prompts
        prompt_name = f"analyze-{context['project_type'].value}-{results['goal']}"
        await self.mcp_client.store_prompt(
            name=prompt_name,
            description=f"Learned workflow for {context['project_type']} {results['goal']}",
            content=pattern_description,
            metadata={
                "layer": "Procedural",
                "domain": context['project_type'].value,
                "effectiveness_score": results.get('effectiveness', 0.8),
                "derived_from_episode": results.get('session_id', 'unknown')
            }
        )
    
    def _synthesize_pattern(self, context: Dict, results: Dict) -> str:
        """Create textual description of successful pattern"""
        return f"""
For {context['project_type']} projects with:
- Languages: {', '.join(context['languages'])}
- Build system: {context['build_system']}
- Performance critical: {context['performance_critical']}

Successful analysis approach:
1. {results['workflow_steps'][0]}
2. {results['workflow_steps'][1]}
...

Key findings:
- {results['key_insights'][0]}
- {results['key_insights'][1]}

Configuration that worked:
{results['effective_config']}
"""
    
    def _generate_tags(self, context: Dict, results: Dict) -> List[str]:
        """Generate semantic tags for searchability"""
        tags = [
            context['project_type'].value,
            context['build_system'],
            results.get('goal', 'general'),
        ]
        tags.extend(context['languages'])
        tags.extend(context['frameworks'])
        return tags
```

### 1.4 CLI Integration

**File: `sparetools/cli/analyze.py`**

User-facing command that leverages the cognitive architecture:

```python
import click
import asyncio
from pathlib import Path

from sparetools.analysis.orchestrator import KnowledgeAwareOrchestrator

@click.group()
def cli():
    """Sparetools - Knowledge-augmented development tools"""
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--goal', type=click.Choice([
    'bug_finding', 'performance', 'security', 'quality', 'comprehensive'
]), default='comprehensive')
@click.option('--capture-learning/--no-capture-learning', default=True)
def analyze(project_path, goal, capture_learning):
    """Analyze project using learned patterns"""
    
    orchestrator = KnowledgeAwareOrchestrator()
    
    async def run():
        results = await orchestrator.analyze_project(
            Path(project_path),
            goal=goal
        )
        
        # Display results
        click.echo(click.style("✓ Analysis complete!", fg='green', bold=True))
        click.echo(f"\nFindings: {len(results['results'])}")
        
        if results.get('novel_findings'):
            click.echo(click.style("\n🆕 Novel patterns discovered!", fg='yellow'))
            for finding in results['novel_findings']:
                click.echo(f"  • {finding}")
    
    asyncio.run(run())

@cli.command()
def teach():
    """Interactive mode to teach sparetools new patterns"""
    click.echo("🎓 Teaching mode - guide sparetools through a new workflow")
    # Implementation for interactive learning

if __name__ == '__main__':
    cli()
```

## Usage Examples

```bash
# Analyze esp32-bpm-detector with learned patterns
cd ~/projects/dev-tools/sparetools
python -m sparetools analyze ~/projects/embedded/esp32-bpm-detector \
  --goal performance

# Analyze all projects and build knowledge base
for project in mia esp32-bpm-detector cliphist-android; do
  python -m sparetools analyze ~/projects/$project --goal comprehensive
done

# Query what we've learned
python -m sparetools knowledge query --domain embedded --topic "memory optimization"

# Teach sparetools a new pattern interactively
python -m sparetools teach
```

## Phase 2: Cross-Domain Transfer (Weeks 3-4)

### 2.1 Pattern Abstraction Engine

Extract abstract patterns that work across domains:

```python
# File: sparetools/transfer/abstractor.py

class PatternAbstractor:
    """Layer 6: Cross-domain transfer"""
    
    async def extract_abstract_pattern(self, concrete_episodes: List[Dict]) -> Dict:
        """
        Find common structure across different domains
        
        Example: "Two-phase analysis" pattern appears in:
        - ESP32: profiling → memory analysis
        - Android: lint → runtime testing  
        - Python: static → dynamic analysis
        """
        pass
```

### 2.2 Domain Mapper

Map concepts between domains:

```python
# Android's "try-with-resources" → C++ RAII
# Android's "LiveData" → C++ Observer pattern
# Python's "context manager" → C++ RAII
```

## Phase 3: Self-Improving Loop (Weeks 5-6)

### 3.1 Effectiveness Tracking

```python
class EffectivenessTracker:
    """Track which patterns actually help"""
    
    async def record_outcome(self, pattern_id: str, helped: bool, time_saved_minutes: int):
        """Update effectiveness scores in mcp-prompts"""
        pass
```

### 3.2 Automatic Prompt Evolution

```python
class PromptEvolver:
    """Automatically refine prompts based on usage"""
    
    async def evolve_prompt(self, prompt_name: str):
        """
        After 10+ uses, analyze:
        - Which parameters were most effective
        - Which steps were skipped
        - Where did users override
        
        Generate improved version
        """
        pass
```

## Success Metrics

1. **Knowledge Accumulation**: Number of prompts in mcp-prompts growing over time
2. **Pattern Reuse**: Percentage of analyses using learned patterns vs. default workflows
3. **Time Savings**: Reduction in time to diagnose similar issues
4. **Cross-Domain Transfer**: Evidence of patterns moving between projects
5. **Self-Improvement**: Prompts evolving through usage feedback

## File Structure

```
~/projects/dev-tools/sparetools/
├── sparetools/
│   ├── __init__.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── client.py           # MCP client wrapper
│   ├── context/
│   │   ├── __init__.py
│   │   └── detector.py         # Layer 1: Perception
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── episodic.py         # Layer 2: Episodes
│   │   └── semantic.py         # Layer 3: Concepts
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── executor.py         # Layer 4: Procedures
│   ├── meta/
│   │   ├── __init__.py
│   │   └── strategy.py         # Layer 5: Meta-cognitive
│   ├── transfer/
│   │   ├── __init__.py
│   │   └── abstractor.py       # Layer 6: Cross-domain
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── quality.py          # Layer 7: Evaluative
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── orchestrator.py     # Main orchestration
│   └── cli/
│       ├── __init__.py
│       ├── analyze.py
│       ├── knowledge.py
│       └── teach.py
├── tests/
│   ├── test_context_detector.py
│   ├── test_orchestrator.py
│   └── test_learning_loop.py
├── prompts/                    # Local prompt storage
│   ├── embedded/
│   ├── android/
│   └── python/
├── docs/
│   ├── architecture.md
│   ├── learning_loop.md
│   └── api.md
├── pyproject.toml
└── README.md
```

## Next Actions (This Week)

1. **Set up MCP servers**
   - Install and configure mcp-prompts
   - Install and configure unified-dev-tools
   - Test connectivity from Python

2. **Implement Phase 1.1**: MCP client infrastructure
   
3. **Implement Phase 1.2**: Context detector for your four projects

4. **Create first learned prompt**: 
   - Run manual analysis on esp32-bpm-detector
   - Document what worked
   - Store as prompt in mcp-prompts

5. **Test the learning loop**:
   - Use stored prompt on similar ESP32 issue
   - Measure if it helps
   - Refine based on feedback

This creates a foundation for true self-improving development intelligence!
