"""
Automated Learning Orchestrator

Coordinates the entire automated learning process across all cognitive layers.
Implements Layer 5 (Meta-Cognitive) decision making about when and what to learn.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from sparetools.learning.pattern_discovery import AutomatedPatternDiscovery, DiscoveredPattern
from sparetools.learning.cross_domain_transfer import CrossDomainTransferEngine
from sparetools.learning.quality_assessment import QualityAssessmentEngine
from sparetools.learning.pattern_evolution import PatternEvolutionSystem
from sparetools.context.detector import ProjectContext
from sparetools.mcp.client import get_mcp_client


class AutomatedLearningOrchestrator:
    """
    Orchestrates automated learning across the cognitive architecture

    Key responsibilities:
    1. Decide when learning should occur (Layer 5: Meta-cognitive)
    2. Coordinate pattern discovery and capture
    3. Trigger cross-domain transfer learning
    4. Monitor and evolve pattern effectiveness
    """

    def __init__(self, knowledge_base_path: Optional[Path] = None):
        if knowledge_base_path is None:
            knowledge_base_path = Path.home() / ".sparetools"

        self.knowledge_base_path = knowledge_base_path
        self.mcp_client = get_mcp_client(knowledge_base_path)

        # Initialize learning components
        self.pattern_discovery = AutomatedPatternDiscovery()
        self.cross_domain_transfer = CrossDomainTransferEngine()
        self.quality_assessment = QualityAssessmentEngine()
        self.pattern_evolution = PatternEvolutionSystem()

        # Learning thresholds
        self.min_learning_confidence = 0.6
        self.max_patterns_per_session = 3
        self.learning_cooldown_seconds = 300  # 5 minutes between learning sessions

        # Track learning activity
        self.last_learning_time = 0
        self.learning_sessions_count = 0

    async def initialize(self):
        """Initialize the learning orchestrator and all components"""
        await self.mcp_client.initialize()
        await self.cross_domain_transfer.initialize()
        await self.quality_assessment.initialize()
        await self.pattern_evolution.initialize()
        print("🧠 Automated Learning Orchestrator initialized with all components")

    async def evaluate_learning_opportunity(self, context: ProjectContext,
                                          analysis_results: Dict[str, Any]) -> bool:
        """
        Decide whether this analysis presents a learning opportunity

        Layer 5: Meta-cognitive decision making
        """
        # Check cooldown period
        current_time = time.time()
        if current_time - self.last_learning_time < self.learning_cooldown_seconds:
            return False

        # Evaluate learning potential
        learning_potential = await self._assess_learning_potential(context, analysis_results)

        # Decide based on multiple factors
        should_learn = (
            learning_potential['confidence'] >= self.min_learning_confidence and
            learning_potential['novelty'] > 0.3 and
            learning_potential['impact'] >= 0.5
        )

        if should_learn:
            print(f"🧠 Learning opportunity detected: confidence={learning_potential['confidence']:.2f}, "
                  f"novelty={learning_potential['novelty']:.2f}, impact={learning_potential['impact']:.2f}")

        return should_learn

    async def execute_learning_session(self, context: ProjectContext,
                                     analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete automated learning session

        Returns learning outcomes and captured patterns
        """
        self.last_learning_time = time.time()
        self.learning_sessions_count += 1

        print(f"🎓 Executing automated learning session #{self.learning_sessions_count}")

        learning_outcomes = {
            'session_id': f"learning_session_{int(time.time())}",
            'patterns_discovered': 0,
            'patterns_captured': 0,
            'cross_domain_transfers': 0,
            'quality_improvements': 0,
            'start_time': time.time()
        }

        try:
                # Phase 1: Pattern Discovery
            discovered_patterns = self.pattern_discovery.discover_patterns(context, analysis_results)
            learning_outcomes['patterns_discovered'] = len(discovered_patterns)

            print(f"🔍 Discovered {len(discovered_patterns)} potential patterns")

            # Phase 2: Pattern Evaluation and Capture
            captured_patterns = await self._capture_high_quality_patterns(discovered_patterns, context)
            learning_outcomes['patterns_captured'] = len(captured_patterns)

            # Phase 3: Cross-Domain Transfer Learning
            if captured_patterns:
                transfer_opportunities = await self.cross_domain_transfer.identify_transfer_opportunities()
                successful_transfers = await self.cross_domain_transfer.execute_transfers(transfer_opportunities)
                learning_outcomes['cross_domain_transfers'] = len(successful_transfers)
            else:
                learning_outcomes['cross_domain_transfers'] = 0

            # Phase 4: Quality Assessment and Evolution
            evolution_results = await self.pattern_evolution.evolve_patterns()
            learning_outcomes['quality_improvements'] = evolution_results.get('patterns_evolved', 0)

            # Phase 5: Comprehensive Quality Assessment
            quality_report = await self.quality_assessment.assess_all_patterns()
            learning_outcomes['quality_assessment'] = {
                'excellent_patterns': len(quality_report.get('excellent_patterns', [])),
                'deprecated_patterns': len(quality_report.get('deprecated_patterns', [])),
                'recommendations_count': len(quality_report.get('recommendations', []))
            }

            # Phase 5: Learning Summary
            learning_outcomes['end_time'] = time.time()
            learning_outcomes['duration_seconds'] = learning_outcomes['end_time'] - learning_outcomes['start_time']

            print(f"✅ Learning session complete: {learning_outcomes['patterns_captured']} patterns captured, "
                  f"{learning_outcomes['cross_domain_transfers']} transfers, "
                  f"{learning_outcomes['quality_improvements']} improvements")

        except Exception as e:
            print(f"❌ Learning session failed: {e}")
            learning_outcomes['error'] = str(e)

        return learning_outcomes

    async def _assess_learning_potential(self, context: ProjectContext,
                                       analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Assess the learning potential of this analysis session
        """
        confidence = 0.0
        novelty = 0.0
        impact = 0.0

        # Confidence: Based on analysis completeness and results quality
        findings = analysis_results.get('findings', [])
        steps_executed = analysis_results.get('steps_executed', [])

        if findings and steps_executed:
            confidence = min(0.9, (len(findings) / 5.0) * (len(steps_executed) / 4.0))

        # Novelty: How different this is from existing knowledge
        project_type = context.project_type.value
        existing_patterns = await self.mcp_client.list_prompts()

        # Count patterns for this project type
        project_patterns = [p for p in existing_patterns if project_type in p.get('domain', '')]
        novelty = 1.0 - min(0.8, len(project_patterns) / 10.0)  # Less novel if many similar patterns

        # Impact: Based on project characteristics and potential reuse
        impact_factors = 0
        if context.performance_critical:
            impact_factors += 1
        if context.security_sensitive:
            impact_factors += 1
        if len(context.languages) > 1:
            impact_factors += 1
        if context.build_system in ['cmake', 'platformio', 'gradle']:
            impact_factors += 1

        impact = min(1.0, impact_factors / 4.0)

        return {
            'confidence': confidence,
            'novelty': novelty,
            'impact': impact
        }

    async def _capture_high_quality_patterns(self, discovered_patterns: List[DiscoveredPattern],
                                           context: ProjectContext) -> List[Dict[str, Any]]:
        """
        Capture only high-quality patterns to avoid knowledge pollution
        """
        captured_patterns = []

        for pattern in discovered_patterns[:self.max_patterns_per_session]:
            # Additional quality checks
            if await self._validate_pattern_quality(pattern, context):
                # Convert to MCP prompt format
                prompt_data = self._convert_pattern_to_prompt(pattern, context)

                # Store in knowledge base
                await self.mcp_client.store_prompt(
                    name=pattern.name,
                    description=pattern.description,
                    content=self._format_pattern_content(pattern),
                    metadata={
                        "layer": "Procedural",
                        "domain": pattern.context.get('project_type', 'General'),
                        "tags": self._generate_pattern_tags(pattern),
                        "abstraction_level": 4,
                        "effectiveness_score": pattern.confidence,
                        "usage_count": 0,
                        "discovered_automatically": True,
                        "applicability_score": pattern.applicability_score
                    }
                )

                captured_patterns.append(prompt_data)
                print(f"✅ Captured pattern: {pattern.name} (confidence: {pattern.confidence:.2f})")

        return captured_patterns

    async def _validate_pattern_quality(self, pattern: DiscoveredPattern,
                                      context: ProjectContext) -> bool:
        """
        Additional validation beyond the discovery engine
        """
        # Check for duplicates
        existing_patterns = await self.mcp_client.list_prompts()
        for existing in existing_patterns:
            if self._patterns_similar(pattern, existing):
                return False  # Don't capture duplicates

        # Check pattern completeness
        required_fields = ['steps', 'tools_used', 'success_indicators']
        for field in required_fields:
            if not getattr(pattern, field, None):
                return False

        # Check applicability
        if pattern.applicability_score < 0.4:
            return False

        return True


    def _convert_pattern_to_prompt(self, pattern: DiscoveredPattern, context: ProjectContext) -> Dict[str, Any]:
        """Convert discovered pattern to MCP prompt format"""
        return {
            'name': pattern.name,
            'description': pattern.description,
            'domain': pattern.context.get('project_type', 'General'),
            'pattern_type': pattern.pattern_type,
            'confidence': pattern.confidence,
            'applicability_score': pattern.applicability_score,
            'discovered_in': context.name,
            'timestamp': int(time.time())
        }

    def _format_pattern_content(self, pattern: DiscoveredPattern) -> str:
        """Format pattern as readable content"""
        content = f"""
Pattern Type: {pattern.pattern_type}
Confidence: {pattern.confidence:.2f}
Applicability: {pattern.applicability_score:.2f}

Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(pattern.steps))}

Tools Used:
{', '.join(pattern.tools_used)}

Success Indicators:
{chr(10).join(f"• {indicator}" for indicator in pattern.success_indicators)}

Context: {pattern.context}
"""
        return content.strip()

    def _generate_pattern_tags(self, pattern: DiscoveredPattern) -> List[str]:
        """Generate semantic tags for the pattern"""
        tags = [pattern.pattern_type, 'automated', 'learned']

        # Add context-based tags
        if pattern.context.get('performance_critical'):
            tags.append('performance')
        if pattern.context.get('security_sensitive'):
            tags.append('security')

        # Add language and build system tags
        languages = pattern.context.get('languages', [])
        tags.extend(languages)

        if pattern.context.get('build_system'):
            tags.append(pattern.context['build_system'])

        return tags


    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learning system's performance"""
        all_patterns = await self.mcp_client.list_prompts()

        stats = {
            'total_patterns': len(all_patterns),
            'automated_patterns': len([p for p in all_patterns if p.get('discovered_automatically')]),
            'learning_sessions': self.learning_sessions_count,
            'average_pattern_confidence': sum(p.get('effectiveness_score', 0.5) for p in all_patterns) / max(len(all_patterns), 1),
            'domains_covered': len(set(p.get('domain', 'Unknown') for p in all_patterns)),
            'last_learning_time': self.last_learning_time
        }

        return stats