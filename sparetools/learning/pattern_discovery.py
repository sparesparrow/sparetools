"""
Automated Pattern Discovery Engine

Layer 5: Meta-Cognitive - Automatically discovers and captures successful patterns
from analysis results without manual intervention.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict, Counter

from sparetools.context.detector import ProjectContext


@dataclass
class DiscoveredPattern:
    """A pattern discovered from analysis results"""
    name: str
    description: str
    pattern_type: str  # 'workflow', 'configuration', 'diagnostic', 'optimization'
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any]
    steps: List[str]
    tools_used: List[str]
    success_indicators: List[str]
    applicability_score: float  # How broadly applicable this pattern is


class AutomatedPatternDiscovery:
    """
    Automatically discovers patterns from analysis results

    Uses multiple discovery strategies:
    1. Workflow pattern mining
    2. Configuration pattern analysis
    3. Success factor correlation
    4. Failure mode pattern recognition
    """

    def __init__(self):
        self.discovery_strategies = {
            'workflow': self._discover_workflow_patterns,
            'configuration': self._discover_configuration_patterns,
            'diagnostic': self._discover_diagnostic_patterns,
            'optimization': self._discover_optimization_patterns
        }

    def discover_patterns(self, context: ProjectContext,
                         analysis_results: Dict[str, Any]) -> List[DiscoveredPattern]:
        """
        Automatically discover patterns from analysis results

        Args:
            context: Project context information
            analysis_results: Results from analysis workflow

        Returns:
            List of discovered patterns with confidence scores
        """
        discovered_patterns = []

        # Apply all discovery strategies
        for pattern_type, strategy_func in self.discovery_strategies.items():
            patterns = strategy_func(context, analysis_results)
            discovered_patterns.extend(patterns)

        # Filter and rank patterns by confidence and applicability
        filtered_patterns = self._filter_patterns(discovered_patterns, context)

        return sorted(filtered_patterns, key=lambda p: p.confidence * p.applicability_score, reverse=True)

    def _discover_workflow_patterns(self, context: ProjectContext,
                                  analysis_results: Dict[str, Any]) -> List[DiscoveredPattern]:
        """Discover successful workflow patterns"""
        patterns = []

        steps_executed = analysis_results.get('steps_executed', [])
        tools_used = analysis_results.get('tools_used', [])
        findings = analysis_results.get('findings', [])

        if not steps_executed:
            return patterns

        # Pattern 1: Successful step sequence
        if len(steps_executed) >= 2 and findings:
            pattern_name = f"workflow-{context.project_type.value}-{len(steps_executed)}-step"
            confidence = min(0.8, len(findings) / 5.0)  # Higher confidence with more findings

            pattern = DiscoveredPattern(
                name=pattern_name,
                description=f"Successful {len(steps_executed)}-step workflow for {context.project_type.value} projects",
                pattern_type='workflow',
                confidence=confidence,
                context={
                    'project_type': context.project_type.value,
                    'languages': context.languages,
                    'build_system': context.build_system,
                    'performance_critical': context.performance_critical
                },
                steps=steps_executed,
                tools_used=tools_used,
                success_indicators=findings,
                applicability_score=self._calculate_applicability(context)
            )
            patterns.append(pattern)

        # Pattern 2: Tool combination effectiveness
        if len(tools_used) >= 2:
            tool_combo_name = f"tool-combo-{'-'.join(sorted(tools_used))}"
            confidence = 0.6 + (len(tools_used) - 2) * 0.1  # More tools = potentially better combo

            pattern = DiscoveredPattern(
                name=tool_combo_name,
                description=f"Effective tool combination: {', '.join(tools_used)}",
                pattern_type='workflow',
                confidence=min(confidence, 0.9),
                context={'tools_used': tools_used},
                steps=['Apply combined tool analysis'],
                tools_used=tools_used,
                success_indicators=['Tool combination synergy detected'],
                applicability_score=0.7  # Tool combos are moderately applicable
            )
            patterns.append(pattern)

        return patterns

    def _discover_configuration_patterns(self, context: ProjectContext,
                                       analysis_results: Dict[str, Any]) -> List[DiscoveredPattern]:
        """Discover configuration patterns that worked"""
        patterns = []

        # Look for configuration hints in findings
        findings = analysis_results.get('findings', [])
        config_indicators = ['config', 'setting', 'parameter', 'flag', 'option']

        config_findings = [f for f in findings if any(ind in f.lower() for ind in config_indicators)]

        if config_findings:
            pattern_name = f"config-{context.project_type.value}-{context.build_system}"

            pattern = DiscoveredPattern(
                name=pattern_name,
                description=f"Configuration pattern for {context.project_type.value} with {context.build_system}",
                pattern_type='configuration',
                confidence=0.7,
                context={
                    'project_type': context.project_type.value,
                    'build_system': context.build_system,
                    'languages': context.languages
                },
                steps=['Apply recommended configuration', 'Verify settings'],
                tools_used=['configuration_analyzer'],
                success_indicators=config_findings,
                applicability_score=self._calculate_applicability(context)
            )
            patterns.append(pattern)

        return patterns

    def _discover_diagnostic_patterns(self, context: ProjectContext,
                                    analysis_results: Dict[str, Any]) -> List[DiscoveredPattern]:
        """Discover diagnostic patterns from error identification"""
        patterns = []

        findings = analysis_results.get('findings', [])
        diagnostic_keywords = ['error', 'issue', 'problem', 'warning', 'fix', 'diagnostic']

        diagnostic_findings = [f for f in findings if any(kw in f.lower() for kw in diagnostic_keywords)]

        if diagnostic_findings:
            pattern_name = f"diagnostic-{context.project_type.value}-issues"

            # Determine diagnostic confidence based on findings
            confidence = min(0.9, 0.4 + len(diagnostic_findings) * 0.2)

            pattern = DiscoveredPattern(
                name=pattern_name,
                description=f"Diagnostic pattern for identifying {context.project_type.value} issues",
                pattern_type='diagnostic',
                confidence=confidence,
                context={
                    'project_type': context.project_type.value,
                    'performance_critical': context.performance_critical,
                    'security_sensitive': context.security_sensitive
                },
                steps=[
                    'Run comprehensive diagnostic analysis',
                    'Identify root cause patterns',
                    'Apply targeted fixes'
                ],
                tools_used=['diagnostic_analyzer', 'pattern_matcher'],
                success_indicators=diagnostic_findings,
                applicability_score=self._calculate_applicability(context)
            )
            patterns.append(pattern)

        return patterns

    def _discover_optimization_patterns(self, context: ProjectContext,
                                      analysis_results: Dict[str, Any]) -> List[DiscoveredPattern]:
        """Discover optimization patterns, especially for performance-critical projects"""
        patterns = []

        if not context.performance_critical:
            return patterns

        findings = analysis_results.get('findings', [])
        optimization_keywords = ['performance', 'optimization', 'speed', 'memory', 'efficiency', 'bottleneck']

        optimization_findings = [f for f in findings if any(kw in f.lower() for kw in optimization_keywords)]

        if optimization_findings:
            pattern_name = f"optimization-{context.project_type.value}-performance"

            pattern = DiscoveredPattern(
                name=pattern_name,
                description=f"Performance optimization pattern for {context.project_type.value}",
                pattern_type='optimization',
                confidence=0.8,  # High confidence for performance optimizations
                context={
                    'project_type': context.project_type.value,
                    'performance_critical': True,
                    'languages': context.languages,
                    'build_system': context.build_system
                },
                steps=[
                    'Profile performance characteristics',
                    'Identify optimization opportunities',
                    'Apply targeted optimizations',
                    'Validate performance improvements'
                ],
                tools_used=['performance_profiler', 'optimization_analyzer'],
                success_indicators=optimization_findings,
                applicability_score=self._calculate_applicability(context) * 1.2  # Bonus for performance patterns
            )
            patterns.append(pattern)

        return patterns

    def _calculate_applicability(self, context: ProjectContext) -> float:
        """Calculate how broadly applicable a pattern might be"""
        base_score = 0.5

        # Language diversity increases applicability
        if len(context.languages) > 1:
            base_score += 0.1

        # Popular build systems increase applicability
        popular_build_systems = ['cmake', 'platformio', 'gradle', 'setuptools']
        if context.build_system in popular_build_systems:
            base_score += 0.1

        # Performance-critical patterns are more applicable
        if context.performance_critical:
            base_score += 0.1

        # Security-sensitive patterns are broadly applicable
        if context.security_sensitive:
            base_score += 0.1

        return min(base_score, 1.0)

    def _filter_patterns(self, patterns: List[DiscoveredPattern],
                        context: ProjectContext) -> List[DiscoveredPattern]:
        """Filter and refine discovered patterns"""
        filtered = []

        for pattern in patterns:
            # Only keep patterns with reasonable confidence
            if pattern.confidence >= 0.5:
                # Enhance pattern with additional context
                pattern.context['discovered_in'] = context.name
                pattern.context['timestamp'] = 'now'
                filtered.append(pattern)

        # Remove duplicates by merging similar patterns
        merged = self._merge_similar_patterns(filtered)

        return merged

    def _merge_similar_patterns(self, patterns: List[DiscoveredPattern]) -> List[DiscoveredPattern]:
        """Merge similar patterns to avoid duplication"""
        pattern_groups = defaultdict(list)

        # Group by pattern type and context similarity
        for pattern in patterns:
            key = f"{pattern.pattern_type}_{pattern.context.get('project_type', '')}"
            pattern_groups[key].append(pattern)

        merged_patterns = []

        for group_patterns in pattern_groups.values():
            if len(group_patterns) == 1:
                merged_patterns.extend(group_patterns)
            else:
                # Merge multiple similar patterns
                merged = self._merge_pattern_group(group_patterns)
                merged_patterns.append(merged)

        return merged_patterns

    def _merge_pattern_group(self, patterns: List[DiscoveredPattern]) -> DiscoveredPattern:
        """Merge a group of similar patterns into one enhanced pattern"""
        if not patterns:
            raise ValueError("Cannot merge empty pattern group")

        # Use the highest confidence pattern as base
        base_pattern = max(patterns, key=lambda p: p.confidence)

        # Combine success indicators from all patterns
        all_indicators = []
        for pattern in patterns:
            all_indicators.extend(pattern.success_indicators)

        # Remove duplicates while preserving order
        seen = set()
        unique_indicators = []
        for indicator in all_indicators:
            if indicator not in seen:
                unique_indicators.append(indicator)
                seen.add(indicator)

        # Enhance confidence based on pattern agreement
        agreement_bonus = min(0.2, len(patterns) * 0.05)
        enhanced_confidence = min(base_pattern.confidence + agreement_bonus, 1.0)

        # Create merged pattern
        merged = DiscoveredPattern(
            name=f"{base_pattern.name}_enhanced",
            description=f"{base_pattern.description} (enhanced from {len(patterns)} similar patterns)",
            pattern_type=base_pattern.pattern_type,
            confidence=enhanced_confidence,
            context=base_pattern.context,
            steps=base_pattern.steps,
            tools_used=list(set(base_pattern.tools_used)),  # Remove duplicates
            success_indicators=unique_indicators[:5],  # Limit to top 5
            applicability_score=base_pattern.applicability_score
        )

        return merged