"""
Quality Assessment Engine

Layer 7: Evaluative - Automatically assesses pattern quality, effectiveness,
and provides feedback for continuous improvement.
"""

import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from sparetools.mcp.client import get_mcp_client


class QualityAssessmentEngine:
    """
    Automatically evaluates pattern quality and effectiveness

    Key capabilities:
    1. Pattern effectiveness tracking
    2. Quality scoring algorithms
    3. Automated feedback generation
    4. Pattern lifecycle management
    5. Statistical analysis of pattern performance
    """

    def __init__(self):
        self.mcp_client = get_mcp_client()

        # Quality thresholds
        self.min_effectiveness_threshold = 0.4
        self.deprecation_threshold = 0.3
        self.excellence_threshold = 0.8

        # Assessment criteria weights
        self.criteria_weights = {
            'effectiveness': 0.4,
            'usage_frequency': 0.2,
            'user_satisfaction': 0.15,
            'consistency': 0.15,
            'freshness': 0.1
        }

    async def initialize(self):
        """Initialize the quality assessment engine"""
        await self.mcp_client.initialize()
        print("📊 Quality Assessment Engine initialized")

    async def assess_all_patterns(self) -> Dict[str, Any]:
        """
        Perform comprehensive quality assessment of all patterns

        Returns assessment results and recommendations
        """
        print("🔍 Performing comprehensive pattern quality assessment...")

        all_patterns = await self.mcp_client.list_prompts()

        assessment_results = {
            'total_patterns': len(all_patterns),
            'excellent_patterns': [],
            'good_patterns': [],
            'needs_improvement': [],
            'deprecated_patterns': [],
            'quality_distribution': {},
            'recommendations': [],
            'statistics': {}
        }

        pattern_scores = {}

        for pattern in all_patterns:
            pattern_name = pattern.get('name', '')
            quality_score = await self._assess_pattern_quality(pattern)

            pattern_scores[pattern_name] = quality_score

            # Categorize patterns
            if quality_score >= self.excellence_threshold:
                assessment_results['excellent_patterns'].append(pattern_name)
            elif quality_score >= 0.6:
                assessment_results['good_patterns'].append(pattern_name)
            elif quality_score >= self.min_effectiveness_threshold:
                assessment_results['needs_improvement'].append(pattern_name)
            else:
                assessment_results['deprecated_patterns'].append(pattern_name)

        # Generate quality distribution
        assessment_results['quality_distribution'] = self._calculate_distribution(pattern_scores)

        # Generate recommendations
        assessment_results['recommendations'] = await self._generate_recommendations(
            all_patterns, pattern_scores
        )

        # Calculate statistics
        assessment_results['statistics'] = self._calculate_quality_statistics(pattern_scores)

        print(f"✅ Assessment complete: {len(assessment_results['excellent_patterns'])} excellent, "
              f"{len(assessment_results['deprecated_patterns'])} deprecated")

        return assessment_results

    async def _assess_pattern_quality(self, pattern: Dict[str, Any]) -> float:
        """
        Assess the quality of a single pattern using multiple criteria
        """
        criteria_scores = {}

        # Effectiveness score (from metadata or usage data)
        criteria_scores['effectiveness'] = pattern.get('effectiveness_score', 0.5)

        # Usage frequency (how often it's been applied successfully)
        usage_count = pattern.get('usage_count', 0)
        criteria_scores['usage_frequency'] = min(1.0, usage_count / 10.0)  # Normalize to 0-1

        # User satisfaction (placeholder - would come from user feedback)
        criteria_scores['user_satisfaction'] = pattern.get('user_satisfaction_score', 0.7)

        # Consistency (how consistently it produces good results)
        criteria_scores['consistency'] = await self._calculate_consistency_score(pattern)

        # Freshness (how recently it's been relevant/updated)
        criteria_scores['freshness'] = self._calculate_freshness_score(pattern)

        # Calculate weighted quality score
        quality_score = sum(
            criteria_scores[criterion] * weight
            for criterion, weight in self.criteria_weights.items()
        )

        return round(quality_score, 3)

    async def _calculate_consistency_score(self, pattern: Dict[str, Any]) -> float:
        """
        Calculate how consistently a pattern produces good results
        """
        # This would ideally use historical success/failure data
        # For now, use a heuristic based on effectiveness and usage

        effectiveness = pattern.get('effectiveness_score', 0.5)
        usage_count = pattern.get('usage_count', 0)

        # Patterns with high usage and good effectiveness are consistent
        if usage_count > 5:
            consistency = min(1.0, effectiveness + 0.1)  # Slight boost for proven usage
        else:
            consistency = effectiveness * 0.8  # Discount for low usage

        return consistency

    def _calculate_freshness_score(self, pattern: Dict[str, Any]) -> float:
        """
        Calculate how fresh/relevant a pattern is
        """
        # Use creation/update timestamps
        created_at = pattern.get('created_at', 0)
        updated_at = pattern.get('updated_at', created_at)

        if isinstance(created_at, str):
            # Handle string timestamps
            try:
                created_at = float(created_at)
                updated_at = float(updated_at) if updated_at != created_at else created_at
            except ValueError:
                created_at = 0
                updated_at = 0

        current_time = datetime.now().timestamp()

        # Calculate age in days
        age_days = (current_time - updated_at) / (24 * 3600)

        # Freshness score: decays over time but never below 0.3
        freshness = max(0.3, 1.0 - (age_days / 365))  # Full year decay

        return freshness

    def _calculate_distribution(self, pattern_scores: Dict[str, float]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        distribution = {
            'excellent': 0,  # 0.8+
            'good': 0,       # 0.6-0.8
            'fair': 0,       # 0.4-0.6
            'poor': 0        # <0.4
        }

        for score in pattern_scores.values():
            if score >= 0.8:
                distribution['excellent'] += 1
            elif score >= 0.6:
                distribution['good'] += 1
            elif score >= 0.4:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1

        return distribution

    async def _generate_recommendations(self, patterns: List[Dict[str, Any]],
                                       pattern_scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on assessment"""
        recommendations = []

        # Find patterns that need improvement
        needs_improvement = [
            name for name, score in pattern_scores.items()
            if score < 0.6
        ]

        if needs_improvement:
            recommendations.append(
                f"Consider improving {len(needs_improvement)} patterns with scores below 0.6: "
                f"{', '.join(needs_improvement[:3])}{'...' if len(needs_improvement) > 3 else ''}"
            )

        # Find patterns that should be deprecated
        deprecated = [
            name for name, score in pattern_scores.items()
            if score < self.deprecation_threshold
        ]

        if deprecated:
            recommendations.append(
                f"Consider deprecating {len(deprecated)} low-quality patterns: "
                f"{', '.join(deprecated[:3])}{'...' if len(deprecated) > 3 else ''}"
            )

        # Check for domain balance
        domain_counts = defaultdict(int)
        for pattern in patterns:
            domain = pattern.get('domain', 'Unknown')
            domain_counts[domain] += 1

        if len(domain_counts) < 3:
            recommendations.append(
                "Consider capturing patterns from more domains to improve cross-domain transfer learning"
            )

        # Check for recent pattern creation
        recent_patterns = 0
        current_time = datetime.now().timestamp()
        for pattern in patterns:
            created_at = pattern.get('created_at', 0)
            if isinstance(created_at, str):
                try:
                    created_at = float(created_at)
                except ValueError:
                    created_at = 0

            if current_time - created_at < (30 * 24 * 3600):  # Last 30 days
                recent_patterns += 1

        if recent_patterns < 2:
            recommendations.append(
                "Knowledge base could benefit from more recent patterns - consider more analysis sessions"
            )

        return recommendations

    def _calculate_quality_statistics(self, pattern_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate statistical measures of pattern quality"""
        if not pattern_scores:
            return {}

        scores = list(pattern_scores.values())

        stats = {
            'mean_quality': round(statistics.mean(scores), 3),
            'median_quality': round(statistics.median(scores), 3),
            'std_dev_quality': round(statistics.stdev(scores) if len(scores) > 1 else 0, 3),
            'min_quality': min(scores),
            'max_quality': max(scores),
            'quality_range': round(max(scores) - min(scores), 3)
        }

        return stats

    async def identify_pattern_improvements(self, pattern: Dict[str, Any]) -> List[str]:
        """
        Identify specific improvements for a pattern
        """
        improvements = []

        # Check effectiveness
        effectiveness = pattern.get('effectiveness_score', 0.5)
        if effectiveness < 0.6:
            improvements.append("Increase effectiveness through better success criteria")

        # Check usage
        usage_count = pattern.get('usage_count', 0)
        if usage_count < 3:
            improvements.append("Increase usage through better applicability")

        # Check freshness
        freshness = self._calculate_freshness_score(pattern)
        if freshness < 0.7:
            improvements.append("Update for current best practices")

        # Check completeness
        content = pattern.get('content', '')
        if len(content.split()) < 50:
            improvements.append("Expand with more detailed examples and context")

        return improvements

    async def get_quality_trends(self) -> Dict[str, Any]:
        """
        Analyze quality trends over time
        """
        all_patterns = await self.mcp_client.list_prompts()

        # Group by creation time periods
        periods = defaultdict(list)
        current_time = datetime.now().timestamp()

        for pattern in all_patterns:
            created_at = pattern.get('created_at', 0)
            if isinstance(created_at, str):
                try:
                    created_at = float(created_at)
                except ValueError:
                    continue

            # Calculate age in weeks
            age_weeks = int((current_time - created_at) / (7 * 24 * 3600))
            periods[age_weeks].append(pattern.get('effectiveness_score', 0.5))

        # Calculate average quality by age
        trends = {}
        for age, scores in sorted(periods.items()):
            trends[f"{age}_weeks_old"] = round(statistics.mean(scores), 3)

        return trends

    async def generate_quality_report(self) -> str:
        """
        Generate a comprehensive quality report
        """
        assessment = await self.assess_all_patterns()
        trends = await self.get_quality_trends()

        report = f"""
# SpareTools Pattern Quality Report

## Executive Summary
- **Total Patterns**: {assessment['total_patterns']}
- **Excellent Patterns**: {len(assessment['excellent_patterns'])}
- **Needs Improvement**: {len(assessment['needs_improvement'])}
- **Deprecated Patterns**: {len(assessment['deprecated_patterns'])}

## Quality Distribution
- **Excellent (≥0.8)**: {assessment['quality_distribution']['excellent']}
- **Good (0.6-0.8)**: {assessment['quality_distribution']['good']}
- **Fair (0.4-0.6)**: {assessment['quality_distribution']['fair']}
- **Poor (<0.4)**: {assessment['quality_distribution']['poor']}

## Quality Statistics
- **Mean Quality**: {assessment['statistics']['mean_quality']}
- **Median Quality**: {assessment['statistics']['median_quality']}
- **Quality Range**: {assessment['statistics']['quality_range']}

## Recommendations
{chr(10).join(f"- {rec}" for rec in assessment['recommendations'])}

## Quality Trends
{chr(10).join(f"- Patterns {age}: {score}" for age, score in trends.items())}

## Top Performing Patterns
{chr(10).join(f"- {pattern}" for pattern in assessment['excellent_patterns'][:5])}
        """.strip()

        return report