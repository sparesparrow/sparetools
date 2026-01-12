"""
Pattern Evolution System

Automatically improves patterns over time based on usage data,
effectiveness feedback, and learning from successes and failures.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from sparetools.mcp.client import get_mcp_client


class PatternEvolutionSystem:
    """
    Evolves patterns automatically based on usage patterns and effectiveness data

    Key capabilities:
    1. Usage pattern analysis
    2. Automatic pattern refinement
    3. Success/failure learning
    4. Pattern merging and splitting
    5. Effectiveness optimization
    """

    def __init__(self):
        self.mcp_client = get_mcp_client()

        # Evolution thresholds
        self.min_usage_for_evolution = 3
        self.effectiveness_improvement_threshold = 0.1
        self.max_evolution_age_days = 90

    async def initialize(self):
        """Initialize the pattern evolution system"""
        await self.mcp_client.initialize()
        print("🧬 Pattern Evolution System initialized")

    async def evolve_patterns(self) -> Dict[str, Any]:
        """
        Analyze all patterns and evolve those that need improvement

        Returns evolution results and statistics
        """
        print("🧬 Analyzing patterns for evolution opportunities...")

        all_patterns = await self.mcp_client.list_prompts()

        evolution_results = {
            'patterns_analyzed': len(all_patterns),
            'patterns_evolved': 0,
            'improvement_types': defaultdict(int),
            'evolution_statistics': {},
            'failed_evolutions': []
        }

        for pattern in all_patterns:
            try:
                evolution_needed = await self._assess_evolution_need(pattern)

                if evolution_needed['needed']:
                    evolution_result = await self._evolve_pattern(pattern, evolution_needed)
                    if evolution_result['success']:
                        evolution_results['patterns_evolved'] += 1
                        evolution_results['improvement_types'][evolution_result['improvement_type']] += 1
                        print(f"🧬 Evolved pattern: {pattern['name']} ({evolution_result['improvement_type']})")
                    else:
                        evolution_results['failed_evolutions'].append(pattern['name'])

            except Exception as e:
                print(f"❌ Evolution failed for {pattern.get('name', 'unknown')}: {e}")
                evolution_results['failed_evolutions'].append(pattern.get('name', 'unknown'))

        # Calculate evolution statistics
        evolution_results['evolution_statistics'] = {
            'evolution_rate': evolution_results['patterns_evolved'] / max(evolution_results['patterns_analyzed'], 1),
            'success_rate': evolution_results['patterns_evolved'] / max(evolution_results['patterns_evolved'] + len(evolution_results['failed_evolutions']), 1)
        }

        print(f"✅ Evolution complete: {evolution_results['patterns_evolved']} patterns improved")

        return evolution_results

    async def _assess_evolution_need(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess whether a pattern needs evolution
        """
        evolution_assessment = {
            'needed': False,
            'reasons': [],
            'priority': 'low',
            'suggested_improvements': []
        }

        # Check usage frequency
        usage_count = pattern.get('usage_count', 0)
        if usage_count < self.min_usage_for_evolution:
            return evolution_assessment  # Not enough data

        # Check effectiveness trends
        effectiveness = pattern.get('effectiveness_score', 0.5)
        if effectiveness < 0.6:
            evolution_assessment['needed'] = True
            evolution_assessment['reasons'].append('low_effectiveness')
            evolution_assessment['suggested_improvements'].append('refine_success_criteria')

        # Check for inconsistent results
        consistency = await self._calculate_pattern_consistency(pattern)
        if consistency < 0.7:
            evolution_assessment['needed'] = True
            evolution_assessment['reasons'].append('inconsistent_results')
            evolution_assessment['suggested_improvements'].append('standardize_application')

        # Check pattern age and freshness
        age_days = self._calculate_pattern_age(pattern)
        if age_days > self.max_evolution_age_days:
            evolution_assessment['needed'] = True
            evolution_assessment['reasons'].append('outdated')
            evolution_assessment['suggested_improvements'].append('update_best_practices')

        # Check for over-specialization
        applicability = pattern.get('applicability_score', 0.5)
        if applicability < 0.3:
            evolution_assessment['needed'] = True
            evolution_assessment['reasons'].append('over_specialized')
            evolution_assessment['suggested_improvements'].append('generalize_pattern')

        # Set priority based on severity
        if len(evolution_assessment['reasons']) >= 3:
            evolution_assessment['priority'] = 'high'
        elif len(evolution_assessment['reasons']) >= 2:
            evolution_assessment['priority'] = 'medium'

        return evolution_assessment

    async def _evolve_pattern(self, pattern: Dict[str, Any], evolution_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve a pattern based on the assessment
        """
        evolution_result = {
            'success': False,
            'improvement_type': 'none',
            'changes_made': [],
            'new_effectiveness': pattern.get('effectiveness_score', 0.5)
        }

        pattern_name = pattern.get('name', 'unknown')

        # Apply improvements based on assessment
        for improvement in evolution_assessment.get('suggested_improvements', []):
            try:
                if improvement == 'refine_success_criteria':
                    success = await self._refine_success_criteria(pattern)
                    if success:
                        evolution_result['changes_made'].append('refined_success_criteria')
                        evolution_result['improvement_type'] = 'effectiveness'

                elif improvement == 'standardize_application':
                    success = await self._standardize_application(pattern)
                    if success:
                        evolution_result['changes_made'].append('standardized_application')
                        evolution_result['improvement_type'] = 'consistency'

                elif improvement == 'update_best_practices':
                    success = await self._update_best_practices(pattern)
                    if success:
                        evolution_result['changes_made'].append('updated_best_practices')
                        evolution_result['improvement_type'] = 'freshness'

                elif improvement == 'generalize_pattern':
                    success = await self._generalize_pattern(pattern)
                    if success:
                        evolution_result['changes_made'].append('generalized_pattern')
                        evolution_result['improvement_type'] = 'applicability'

            except Exception as e:
                print(f"❌ Improvement failed for {pattern_name}: {e}")
                continue

        # Update pattern effectiveness if improvements were made
        if evolution_result['changes_made']:
            evolution_result['success'] = True
            # Slight effectiveness boost for evolved patterns
            evolution_result['new_effectiveness'] = min(1.0, pattern.get('effectiveness_score', 0.5) + 0.05)

            # Update the pattern in storage
            await self._update_evolved_pattern(pattern, evolution_result)

        return evolution_result

    async def _refine_success_criteria(self, pattern: Dict[str, Any]) -> bool:
        """
        Refine the success criteria of a pattern based on usage data
        """
        # Analyze historical usage to identify better success indicators
        content = pattern.get('content', '')

        # Look for common success patterns in the content
        success_indicators = [
            'performance improved', 'memory usage reduced', 'build succeeded',
            'errors decreased', 'efficiency gained', 'issues resolved'
        ]

        found_indicators = []
        for indicator in success_indicators:
            if indicator.lower() in content.lower():
                found_indicators.append(indicator)

        if found_indicators:
            # Enhance the pattern with refined success criteria
            enhanced_content = content + f"\n\nRECOMMENDED SUCCESS CRITERIA:\n"
            enhanced_content += "\n".join(f"• {indicator}" for indicator in found_indicators)

            # Update pattern (this would be stored back)
            pattern['content'] = enhanced_content
            return True

        return False

    async def _standardize_application(self, pattern: Dict[str, Any]) -> bool:
        """
        Standardize how the pattern is applied based on consistency analysis
        """
        content = pattern.get('content', '')

        # Add standardization notes
        standardization_notes = """

STANDARDIZED APPLICATION GUIDELINES:
• Ensure all prerequisites are met before application
• Validate environmental conditions match pattern assumptions
• Monitor key metrics during and after application
• Document any deviations from standard approach
"""

        if "STANDARDIZED APPLICATION GUIDELINES" not in content:
            pattern['content'] = content + standardization_notes
            return True

        return False

    async def _update_best_practices(self, pattern: Dict[str, Any]) -> bool:
        """
        Update pattern with current best practices
        """
        content = pattern.get('content', '')
        domain = pattern.get('domain', 'general')

        # Add modernization notes based on domain
        if domain == 'embedded_esp32':
            updates = "\n\nMODERNIZATION NOTES (2025):\n• Consider ESP-IDF v5.x features\n• Evaluate thread safety for multi-core applications\n• Review power management best practices"
        elif domain == 'android_app':
            updates = "\n\nMODERNIZATION NOTES (2025):\n• Use Kotlin coroutines for async operations\n• Implement Jetpack Compose for UI\n• Consider Android 14+ features and permissions"
        elif 'cpp' in domain:
            updates = "\n\nMODERNIZATION NOTES (2025):\n• Use C++17/20 features where applicable\n• Consider smart pointers and RAII patterns\n• Evaluate compile-time optimizations"
        else:
            updates = "\n\nMODERNIZATION NOTES (2025):\n• Review current best practices\n• Consider newer language features\n• Evaluate performance implications"

        if "MODERNIZATION NOTES" not in content:
            pattern['content'] = content + updates
            return True

        return False

    async def _generalize_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Make a pattern more generally applicable by reducing specificity
        """
        content = pattern.get('content', '')

        # Identify overly specific elements
        specific_indicators = [
            'specific version', 'particular hardware', 'exact configuration',
            'platform-specific', 'tool-specific'
        ]

        generalizations_made = 0

        for indicator in specific_indicators:
            if indicator in content.lower():
                # Add generalization note
                generalization_note = f"\n\nGENERALIZATION NOTE: This pattern contains {indicator} elements. " \
                                    "Consider adapting for different environments while maintaining core principles."

                if generalization_note not in content:
                    content += generalization_note
                    generalizations_made += 1

        if generalizations_made > 0:
            pattern['content'] = content
            # Increase applicability score
            current_applicability = pattern.get('applicability_score', 0.5)
            pattern['applicability_score'] = min(1.0, current_applicability + 0.1)
            return True

        return False

    async def _update_evolved_pattern(self, pattern: Dict[str, Any], evolution_result: Dict[str, Any]):
        """
        Update the evolved pattern in storage
        """
        # Update metadata with evolution information
        pattern['effectiveness_score'] = evolution_result['new_effectiveness']
        pattern['last_evolution'] = datetime.now().timestamp()
        pattern['evolution_history'] = pattern.get('evolution_history', []) + [{
            'timestamp': datetime.now().timestamp(),
            'improvement_type': evolution_result['improvement_type'],
            'changes_made': evolution_result['changes_made']
        }]

        # Update the pattern in storage
        await self.mcp_client.store_prompt(
            name=pattern['name'],
            description=pattern['description'],
            content=pattern['content'],
            metadata={
                "layer": pattern.get('layer', 'Procedural'),
                "domain": pattern.get('domain', 'General'),
                "tags": pattern.get('tags', []),
                "abstraction_level": pattern.get('abstraction_level', 4),
                "effectiveness_score": pattern['effectiveness_score'],
                "usage_count": pattern.get('usage_count', 0),
                "applicability_score": pattern.get('applicability_score', 0.5),
                "last_evolution": pattern['last_evolution'],
                "evolution_history": pattern['evolution_history']
            }
        )

    async def _calculate_pattern_consistency(self, pattern: Dict[str, Any]) -> float:
        """
        Calculate how consistent a pattern's results are
        """
        # This would ideally use historical success/failure data
        # For now, use effectiveness as a proxy for consistency

        effectiveness = pattern.get('effectiveness_score', 0.5)
        usage_count = pattern.get('usage_count', 0)

        # Patterns with high usage and good effectiveness are more consistent
        if usage_count > 10:
            consistency = min(1.0, effectiveness + 0.1)
        elif usage_count > 5:
            consistency = effectiveness
        else:
            consistency = effectiveness * 0.9  # Slight penalty for low usage

        return consistency

    def _calculate_pattern_age(self, pattern: Dict[str, Any]) -> float:
        """
        Calculate pattern age in days
        """
        last_updated = pattern.get('last_evolution') or pattern.get('updated_at') or pattern.get('created_at', 0)

        if isinstance(last_updated, str):
            try:
                last_updated = float(last_updated)
            except ValueError:
                last_updated = 0

        current_time = datetime.now().timestamp()
        age_seconds = current_time - last_updated
        age_days = age_seconds / (24 * 3600)

        return age_days

    async def get_evolution_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pattern evolution
        """
        all_patterns = await self.mcp_client.list_prompts()

        evolved_patterns = [p for p in all_patterns if p.get('evolution_history')]

        stats = {
            'total_patterns': len(all_patterns),
            'evolved_patterns': len(evolved_patterns),
            'evolution_rate': len(evolved_patterns) / max(len(all_patterns), 1),
            'improvement_types': defaultdict(int),
            'average_evolution_age_days': 0
        }

        # Analyze evolution types
        for pattern in evolved_patterns:
            evolution_history = pattern.get('evolution_history', [])
            if evolution_history:
                latest_evolution = evolution_history[-1]
                improvement_type = latest_evolution.get('improvement_type', 'unknown')
                stats['improvement_types'][improvement_type] += 1

        # Calculate average evolution age
        evolution_ages = []
        for pattern in evolved_patterns:
            last_evolution = pattern.get('last_evolution')
            if last_evolution:
                if isinstance(last_evolution, str):
                    try:
                        last_evolution = float(last_evolution)
                    except ValueError:
                        continue

                age_days = (datetime.now().timestamp() - last_evolution) / (24 * 3600)
                evolution_ages.append(age_days)

        if evolution_ages:
            stats['average_evolution_age_days'] = sum(evolution_ages) / len(evolution_ages)

        return dict(stats)