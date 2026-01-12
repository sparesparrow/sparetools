"""
Interpretation Engine

Engine for fetching interpretation templates from MCP-Prompts server
and applying them to analysis results for intelligent interpretation.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

from .prompts_client import MCPPromptsClient
from ..tool_adapters.base_adapter import ToolResult


@dataclass
class InterpretationContext:
    """Context for result interpretation"""
    project_type: str
    language: Optional[str] = None
    framework: Optional[str] = None
    severity_threshold: str = "medium"
    include_suggestions: bool = True
    domain_context: Optional[Dict[str, Any]] = None


@dataclass
class InterpretationResult:
    """Result of interpretation analysis"""
    tool_name: str
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    contextual_insights: List[str]
    next_steps: List[str]
    metadata: Dict[str, Any]


class InterpretationEngine:
    """
    Engine for intelligent interpretation of analysis results.

    Uses MCP-Prompts server to fetch interpretation templates and
    applies them to tool results for contextual analysis.
    """

    def __init__(self,
                 prompts_client: Optional[MCPPromptsClient] = None,
                 cache_enabled: bool = True):
        """
        Initialize the interpretation engine.

        Args:
            prompts_client: MCP-Prompts client instance
            cache_enabled: Whether to cache interpretation results
        """
        self.prompts_client = prompts_client or MCPPromptsClient()
        self.cache_enabled = cache_enabled
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._cache: Dict[str, Any] = {}

    def _get_cache_key(self, tool_name: str, context: InterpretationContext) -> str:
        """Generate cache key for interpretation results"""
        return f"{tool_name}_{context.project_type}_{context.language}_{context.severity_threshold}"

    async def interpret_results(self,
                              tool_name: str,
                              results: Union[ToolResult, List[ToolResult]],
                              context: InterpretationContext) -> InterpretationResult:
        """
        Interpret analysis results using MCP-Prompts intelligence.

        Args:
            tool_name: Name of the analysis tool
            results: ToolResult object(s) to interpret
            context: Interpretation context

        Returns:
            InterpretationResult with intelligent analysis
        """
        # Handle single result vs list
        if isinstance(results, ToolResult):
            results = [results]

        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(tool_name, context)
            if cache_key in self._cache:
                self.logger.debug(f"Using cached interpretation for {cache_key}")
                return self._cache[cache_key]

        try:
            # Get interpretation prompt from MCP-Prompts
            prompt_context = {
                'project_type': context.project_type,
                'language': context.language,
                'framework': context.framework,
                'severity_threshold': context.severity_threshold,
                'include_suggestions': context.include_suggestions,
                'domain_context': context.domain_context,
                'result_count': len(results),
                'total_issues': sum(len(r.issues) for r in results),
                'success_rate': sum(1 for r in r.success) / len(results) if results else 0
            }

            interpretation_prompt = await self.prompts_client.get_interpretation_prompt(
                tool_name, prompt_context
            )

            if not interpretation_prompt:
                # Fallback to basic interpretation
                return self._basic_interpretation(tool_name, results, context)

            # Apply interpretation logic
            interpretation = await self._apply_interpretation(
                tool_name, results, context, interpretation_prompt
            )

            # Cache result
            if self.cache_enabled:
                self._cache[cache_key] = interpretation

            return interpretation

        except Exception as e:
            self.logger.error(f"Error in interpretation: {e}")
            return self._basic_interpretation(tool_name, results, context)

    def interpret_results_sync(self,
                             tool_name: str,
                             results: Union[ToolResult, List[ToolResult]],
                             context: InterpretationContext) -> InterpretationResult:
        """Synchronous version of interpret_results"""
        import asyncio
        return asyncio.run(self.interpret_results(tool_name, results, context))

    async def _apply_interpretation(self,
                                  tool_name: str,
                                  results: List[ToolResult],
                                  context: InterpretationContext,
                                  prompt_template: str) -> InterpretationResult:
        """
        Apply interpretation template to results.

        This is a simplified implementation. In a real system, this would
        use AI/LLM to process the template with the results.
        """
        # Aggregate metrics from all results
        total_issues = sum(len(r.issues) for r in results)
        successful_runs = sum(1 for r in results if r.success)
        failed_runs = len(results) - successful_runs

        # Categorize issues by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for result in results:
            for issue in result.issues:
                severity = issue.severity.value.lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1

        # Generate basic interpretation based on patterns
        summary = self._generate_summary(tool_name, results, severity_counts)
        key_findings = self._extract_key_findings(results, context)
        recommendations = self._generate_recommendations(tool_name, results, context)
        risk_assessment = self._assess_risks(severity_counts, context)
        contextual_insights = self._generate_contextual_insights(tool_name, results, context)
        next_steps = self._suggest_next_steps(tool_name, results, context)

        return InterpretationResult(
            tool_name=tool_name,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            contextual_insights=contextual_insights,
            next_steps=next_steps,
            metadata={
                'interpretation_timestamp': datetime.now().isoformat(),
                'results_count': len(results),
                'total_issues': total_issues,
                'severity_breakdown': severity_counts,
                'success_rate': successful_runs / len(results) if results else 0
            }
        )

    def _basic_interpretation(self,
                            tool_name: str,
                            results: List[ToolResult],
                            context: InterpretationContext) -> InterpretationResult:
        """Fallback basic interpretation when MCP-Prompts is unavailable"""
        total_issues = sum(len(r.issues) for r in results)
        successful_runs = sum(1 for r in results if r.success)

        summary = f"{tool_name} analysis completed with {total_issues} issues found across {len(results)} runs."

        key_findings = []
        if total_issues > 0:
            key_findings.append(f"Found {total_issues} issues requiring attention")
        if successful_runs < len(results):
            key_findings.append(f"{len(results) - successful_runs} analysis runs failed")

        recommendations = [
            "Review all issues found during analysis",
            "Prioritize critical and high-severity issues",
            "Consider fixing issues in order of impact"
        ]

        risk_assessment = {
            'overall_risk': 'medium' if total_issues > 0 else 'low',
            'confidence': 'medium',
            'factors': ['Analysis completed', f'{total_issues} issues detected']
        }

        return InterpretationResult(
            tool_name=tool_name,
            summary=summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            contextual_insights=[],
            next_steps=["Review analysis results", "Address critical issues"],
            metadata={
                'basic_interpretation': True,
                'results_count': len(results),
                'total_issues': total_issues
            }
        )

    def _generate_summary(self, tool_name: str, results: List[ToolResult],
                         severity_counts: Dict[str, int]) -> str:
        """Generate a summary of the analysis results"""
        total_issues = sum(severity_counts.values())
        successful_runs = sum(1 for r in results if r.success)

        if total_issues == 0 and successful_runs == len(results):
            return f"{tool_name} analysis completed successfully with no issues found."

        summary_parts = [f"{tool_name} analysis completed"]

        if successful_runs < len(results):
            summary_parts.append(f"with {len(results) - successful_runs} failed runs")
        else:
            summary_parts.append("successfully")

        if total_issues > 0:
            critical_high = severity_counts['critical'] + severity_counts['high']
            if critical_high > 0:
                summary_parts.append(f"finding {critical_high} critical/high severity issues")
            summary_parts.append(f"and {total_issues} total issues")

        return " ".join(summary_parts) + "."

    def _extract_key_findings(self, results: List[ToolResult],
                            context: InterpretationContext) -> List[str]:
        """Extract key findings from analysis results"""
        findings = []

        # Aggregate issues by type/pattern
        issue_patterns = {}
        for result in results:
            for issue in result.issues:
                pattern = f"{issue.category}: {issue.severity.value}"
                issue_patterns[pattern] = issue_patterns.get(pattern, 0) + 1

        # Find most common patterns
        for pattern, count in sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            findings.append(f"Found {count} issues of type: {pattern}")

        # Check for unusual patterns
        failed_runs = sum(1 for r in results if not r.success)
        if failed_runs > 0:
            findings.append(f"{failed_runs} analysis runs failed - investigate tool configuration")

        # Check execution times
        slow_runs = [r for r in results if r.execution_time and r.execution_time > 300]  # 5 minutes
        if slow_runs:
            findings.append(f"{len(slow_runs)} analysis runs took unusually long to complete")

        return findings

    def _generate_recommendations(self, tool_name: str, results: List[ToolResult],
                                context: InterpretationContext) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []

        # Basic recommendations
        total_issues = sum(len(r.issues) for r in results)
        if total_issues > 0:
            recommendations.append("Review and prioritize issues by severity and impact")

        # Tool-specific recommendations
        if tool_name == "cppcheck":
            recommendations.append("Consider using clang-tidy for additional C++ analysis")
        elif tool_name == "valgrind":
            recommendations.append("Address memory leaks and undefined behavior issues")
        elif tool_name == "pytest":
            if any(not r.success for r in results):
                recommendations.append("Fix failing tests before deployment")
        elif tool_name == "jest":
            recommendations.append("Ensure test coverage meets project requirements")

        # Context-specific recommendations
        if context.project_type == "web":
            recommendations.append("Consider security scanning for web applications")
        elif context.project_type == "library":
            recommendations.append("Ensure API stability and backward compatibility")

        return recommendations

    def _assess_risks(self, severity_counts: Dict[str, int],
                     context: InterpretationContext) -> Dict[str, Any]:
        """Assess overall risk level based on findings"""
        total_issues = sum(severity_counts.values())
        critical_high = severity_counts['critical'] + severity_counts['high']

        # Calculate risk score (0-100)
        risk_score = min(100, (critical_high * 20) + (severity_counts['medium'] * 10) + (severity_counts['low'] * 2))

        # Determine risk level
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        elif risk_score >= 20:
            risk_level = "low"
        else:
            risk_level = "minimal"

        # Confidence based on result consistency
        confidence = "high" if total_issues > 5 else "medium" if total_issues > 0 else "low"

        return {
            'overall_risk': risk_level,
            'risk_score': risk_score,
            'confidence': confidence,
            'factors': [
                f"{critical_high} critical/high severity issues",
                f"{severity_counts['medium']} medium severity issues",
                f"{total_issues} total issues found"
            ]
        }

    def _generate_contextual_insights(self, tool_name: str, results: List[ToolResult],
                                    context: InterpretationContext) -> List[str]:
        """Generate contextual insights based on project and domain knowledge"""
        insights = []

        # Project type insights
        if context.project_type == "web":
            if tool_name == "pytest":
                insights.append("Test coverage is crucial for web application reliability")
        elif context.project_type == "library":
            if any(r.execution_time and r.execution_time > 60 for r in results):
                insights.append("Consider optimizing build times for library distribution")

        # Language-specific insights
        if context.language == "python":
            if tool_name == "pytest":
                insights.append("Python testing best practices recommend >80% coverage")
        elif context.language == "c++":
            if tool_name == "cppcheck":
                insights.append("C++ analysis should be complemented with sanitizers")

        # Framework-specific insights
        if context.framework == "react":
            if tool_name == "jest":
                insights.append("React testing should include component and integration tests")

        return insights

    def _suggest_next_steps(self, tool_name: str, results: List[ToolResult],
                          context: InterpretationContext) -> List[str]:
        """Suggest next steps based on analysis results"""
        next_steps = []

        total_issues = sum(len(r.issues) for r in results)
        failed_runs = sum(1 for r in results if not r.success)

        if failed_runs > 0:
            next_steps.append("Investigate and resolve analysis tool failures")

        if total_issues > 0:
            next_steps.append("Create tickets for critical and high-severity issues")
            next_steps.append("Schedule code review for identified issues")

        # Tool chaining suggestions
        if tool_name == "cppcheck":
            next_steps.append("Consider running clang-tidy for deeper analysis")
        elif tool_name == "pytest":
            next_steps.append("Run integration tests in staging environment")

        next_steps.append("Monitor issue trends in future analyses")

        return next_steps