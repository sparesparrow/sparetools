"""
Cross-Domain Transfer Learning Engine

Layer 6: Transfer - Automatically identifies patterns that work across different domains
and adapts them for new contexts.
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass

from sparetools.mcp.client import get_mcp_client


@dataclass
class TransferPattern:
    """A pattern that can be transferred across domains"""
    source_domain: str
    target_domain: str
    original_pattern: Dict[str, Any]
    adapted_pattern: Dict[str, Any]
    adaptation_rules: List[str]
    confidence: float
    examples: List[str]


class CrossDomainTransferEngine:
    """
    Automatically discovers and applies patterns across different development domains

    Key capabilities:
    1. Domain similarity analysis
    2. Pattern abstraction and adaptation
    3. Transfer opportunity identification
    4. Automated pattern migration
    """

    def __init__(self):
        self.mcp_client = get_mcp_client()

        # Domain similarity mappings
        self.domain_relationships = {
            'embedded_esp32': {
                'similar_domains': ['cpp_library', 'embedded_firmware'],
                'shared_concepts': ['memory_management', 'performance', 'hardware_interaction'],
                'transfer_confidence': 0.8
            },
            'cpp_library': {
                'similar_domains': ['embedded_esp32', 'python_cli', 'android_app'],
                'shared_concepts': ['build_systems', 'dependency_management', 'code_organization'],
                'transfer_confidence': 0.7
            },
            'android_app': {
                'similar_domains': ['cpp_library', 'python_cli'],
                'shared_concepts': ['ui_patterns', 'resource_management', 'platform_abstraction'],
                'transfer_confidence': 0.6
            },
            'python_cli': {
                'similar_domains': ['cpp_library', 'android_app'],
                'shared_concepts': ['scripting', 'configuration', 'error_handling'],
                'transfer_confidence': 0.7
            }
        }

        # Pattern adaptation rules
        self.adaptation_rules = {
            'memory_management': {
                'embedded_esp32': ['Use static allocation', 'Avoid heap fragmentation', 'Implement custom allocators'],
                'cpp_library': ['Use smart pointers', 'RAII patterns', 'Avoid memory leaks'],
                'python_cli': ['Use context managers', 'Garbage collection awareness', 'Memory profiling']
            },
            'error_handling': {
                'cpp_library': ['Exception safety', 'RAII cleanup', 'Error codes vs exceptions'],
                'python_cli': ['Try/except blocks', 'Context managers', 'Logging'],
                'android_app': ['Try/catch with resources', 'Async error handling', 'UI error states']
            },
            'performance_optimization': {
                'embedded_esp32': ['Interrupt optimization', 'Memory access patterns', 'Power management'],
                'cpp_library': ['Algorithm optimization', 'Memory layout', 'Cache efficiency'],
                'python_cli': ['Profiling', 'C extensions', 'Async processing']
            }
        }

    async def initialize(self):
        """Initialize the transfer engine"""
        await self.mcp_client.initialize()
        print("🔄 Cross-Domain Transfer Engine initialized")

    async def identify_transfer_opportunities(self) -> List[TransferPattern]:
        """
        Scan existing patterns and identify cross-domain transfer opportunities

        Returns patterns that could be adapted for use in other domains
        """
        print("🔍 Scanning for cross-domain transfer opportunities...")

        # Get all existing patterns
        all_patterns = await self.mcp_client.list_prompts()

        transfer_opportunities = []

        # Group patterns by domain
        domain_patterns = defaultdict(list)
        for pattern in all_patterns:
            domain = pattern.get('domain', 'General')
            domain_patterns[domain].append(pattern)

        # Look for transfer opportunities between related domains
        for source_domain, source_patterns in domain_patterns.items():
            for target_domain in self._get_related_domains(source_domain):
                opportunities = await self._find_domain_transfers(
                    source_domain, target_domain, source_patterns
                )
                transfer_opportunities.extend(opportunities)

        print(f"📋 Found {len(transfer_opportunities)} potential transfer opportunities")

        return transfer_opportunities

    async def execute_transfers(self, transfer_opportunities: List[TransferPattern]) -> List[Dict[str, Any]]:
        """
        Execute the identified transfer opportunities by creating adapted patterns

        Returns successfully transferred patterns
        """
        successful_transfers = []

        for opportunity in transfer_opportunities[:5]:  # Limit to avoid spam
            try:
                # Create adapted pattern
                adapted_pattern = await self._adapt_pattern_for_domain(opportunity)

                # Store the adapted pattern
                await self.mcp_client.store_prompt(
                    name=f"{opportunity.original_pattern['name']}_adapted_for_{opportunity.target_domain}",
                    description=f"Adapted {opportunity.original_pattern['description']} for {opportunity.target_domain}",
                    content=adapted_pattern['content'],
                    metadata={
                        "layer": "Transfer",
                        "domain": opportunity.target_domain,
                        "original_pattern": opportunity.original_pattern['name'],
                        "adaptation_rules": opportunity.adaptation_rules,
                        "transfer_confidence": opportunity.confidence,
                        "derived_from_domain": opportunity.source_domain,
                        "applicable_domains": [opportunity.target_domain],
                        "tags": adapted_pattern.get('tags', []) + ['transferred', 'adapted']
                    }
                )

                successful_transfers.append({
                    'original_pattern': opportunity.original_pattern['name'],
                    'adapted_pattern': adapted_pattern['name'],
                    'source_domain': opportunity.source_domain,
                    'target_domain': opportunity.target_domain,
                    'confidence': opportunity.confidence
                })

                print(f"✅ Transferred pattern: {opportunity.original_pattern['name']} "
                      f"→ {opportunity.target_domain} (confidence: {opportunity.confidence:.2f})")

            except Exception as e:
                print(f"❌ Transfer failed for {opportunity.original_pattern['name']}: {e}")

        return successful_transfers

    def _get_related_domains(self, domain: str) -> List[str]:
        """Get domains related to the given domain"""
        if domain in self.domain_relationships:
            return self.domain_relationships[domain]['similar_domains']
        return []

    async def _find_domain_transfers(self, source_domain: str, target_domain: str,
                                   source_patterns: List[Dict[str, Any]]) -> List[TransferPattern]:
        """Find patterns that can transfer from source to target domain"""
        transfer_opportunities = []

        for pattern in source_patterns:
            # Check if this pattern has transfer potential
            transfer_potential = self._assess_transfer_potential(pattern, source_domain, target_domain)

            if transfer_potential['can_transfer'] and transfer_potential['confidence'] > 0.5:
                # Identify specific adaptation rules
                adaptation_rules = self._identify_adaptation_rules(pattern, source_domain, target_domain)

                transfer_pattern = TransferPattern(
                    source_domain=source_domain,
                    target_domain=target_domain,
                    original_pattern=pattern,
                    adapted_pattern={},  # Will be filled during adaptation
                    adaptation_rules=adaptation_rules,
                    confidence=transfer_potential['confidence'],
                    examples=transfer_potential.get('examples', [])
                )

                transfer_opportunities.append(transfer_pattern)

        return transfer_opportunities

    def _assess_transfer_potential(self, pattern: Dict[str, Any],
                                 source_domain: str, target_domain: str) -> Dict[str, Any]:
        """
        Assess how well a pattern can transfer between domains
        """
        confidence = 0.0
        can_transfer = False
        examples = []

        # Get domain relationship info
        domain_info = self.domain_relationships.get(source_domain, {})
        transfer_base_confidence = domain_info.get('transfer_confidence', 0.5)

        # Analyze pattern content for transferable concepts
        content = pattern.get('content', '').lower()
        tags = pattern.get('tags', [])

        # Check for shared concepts
        shared_concepts = domain_info.get('shared_concepts', [])
        concept_matches = []

        for concept in shared_concepts:
            concept_keywords = self._get_concept_keywords(concept)

            # Check content and tags for concept keywords
            content_matches = any(kw in content for kw in concept_keywords)
            tag_matches = any(kw in tag.lower() for tag in tags for kw in concept_keywords)

            if content_matches or tag_matches:
                concept_matches.append(concept)
                confidence += 0.2
                examples.append(f"Shared {concept} concept found")

        # Boost confidence for patterns with high effectiveness
        effectiveness = pattern.get('effectiveness_score', 0.5)
        if effectiveness > 0.7:
            confidence += 0.1
            examples.append("High effectiveness pattern")

        # Domain-specific transfer logic
        if source_domain == 'embedded_esp32' and target_domain == 'cpp_library':
            if 'memory' in content or 'performance' in content:
                confidence += 0.3
                examples.append("Embedded memory patterns apply to C++ libraries")

        elif source_domain == 'cpp_library' and target_domain == 'android_app':
            if 'resource' in content or 'lifecycle' in content:
                confidence += 0.25
                examples.append("C++ resource management applies to Android")

        elif source_domain == 'python_cli' and target_domain == 'android_app':
            if 'async' in content or 'ui' in content:
                confidence += 0.2
                examples.append("Python async patterns inform Android UI")

        confidence = min(confidence + transfer_base_confidence, 1.0)
        can_transfer = confidence > 0.5 and len(concept_matches) > 0

        return {
            'can_transfer': can_transfer,
            'confidence': confidence,
            'examples': examples
        }

    def _identify_adaptation_rules(self, pattern: Dict[str, Any],
                                 source_domain: str, target_domain: str) -> List[str]:
        """Identify specific rules for adapting a pattern to a new domain"""
        rules = []

        content = pattern.get('content', '').lower()

        # Apply concept-based adaptation rules
        for concept, domain_rules in self.adaptation_rules.items():
            if concept in content or any(concept in tag.lower() for tag in pattern.get('tags', [])):
                if target_domain in domain_rules:
                    rules.extend(domain_rules[target_domain])

        # Domain-specific adaptation rules
        if source_domain == 'embedded_esp32' and target_domain == 'cpp_library':
            rules.extend([
                "Replace hardware-specific memory constraints with general RAII patterns",
                "Adapt interrupt-driven patterns to event-driven architectures",
                "Translate real-time requirements to performance guidelines"
            ])

        elif source_domain == 'cpp_library' and target_domain == 'android_app':
            rules.extend([
                "Adapt native memory management to Android Java/Kotlin patterns",
                "Translate build system constraints to Gradle dependencies",
                "Map C++ exceptions to Android error handling patterns"
            ])

        return list(set(rules))  # Remove duplicates

    async def _adapt_pattern_for_domain(self, transfer_opportunity: TransferPattern) -> Dict[str, Any]:
        """Adapt a pattern for use in the target domain"""
        original = transfer_opportunity.original_pattern
        target_domain = transfer_opportunity.target_domain

        # Create adapted content
        adapted_content = self._adapt_content(
            original.get('content', ''),
            transfer_opportunity.source_domain,
            target_domain,
            transfer_opportunity.adaptation_rules
        )

        # Generate adapted name and description
        adapted_name = f"{original['name']}_for_{target_domain}"
        adapted_description = f"{original['description']} (adapted for {target_domain})"

        # Generate appropriate tags
        adapted_tags = self._generate_adapted_tags(original.get('tags', []), target_domain)

        return {
            'name': adapted_name,
            'description': adapted_description,
            'content': adapted_content,
            'tags': adapted_tags,
            'original_pattern': original['name'],
            'adaptation_rules': transfer_opportunity.adaptation_rules
        }

    def _adapt_content(self, original_content: str, source_domain: str,
                      target_domain: str, adaptation_rules: List[str]) -> str:
        """Adapt pattern content for the target domain"""
        adapted_content = original_content

        # Add adaptation notes
        adaptation_header = f"""
ADAPTED FOR {target_domain.upper()}
==========================
Original domain: {source_domain}
Adaptation rules applied:
{chr(10).join(f"• {rule}" for rule in adaptation_rules)}

ADAPTED CONTENT:
================
"""

        adapted_content = adaptation_header + adapted_content

        # Apply domain-specific content transformations
        adapted_content = self._apply_domain_transformations(
            adapted_content, source_domain, target_domain
        )

        return adapted_content

    def _apply_domain_transformations(self, content: str, source_domain: str, target_domain: str) -> str:
        """Apply domain-specific content transformations"""
        transformed = content

        # ESP32 → C++ Library transformations
        if source_domain == 'embedded_esp32' and target_domain == 'cpp_library':
            transformations = [
                ('static allocation', 'RAII with smart pointers'),
                ('interrupt service routine', 'event handler'),
                ('real-time constraint', 'performance requirement'),
                ('ESP32-specific', 'cross-platform'),
                ('FreeRTOS', 'standard threading')
            ]

        # C++ Library → Android transformations
        elif source_domain == 'cpp_library' and target_domain == 'android_app':
            transformations = [
                ('raw pointers', 'Android managed objects'),
                ('CMake', 'Gradle with native build'),
                ('C++ exceptions', 'Java/Kotlin exceptions'),
                ('manual memory management', 'automatic garbage collection'),
                ('stdio', 'Android logging')
            ]

        # Python → Android transformations
        elif source_domain == 'python_cli' and target_domain == 'android_app':
            transformations = [
                ('argparse', 'Android Intent/extras'),
                ('sys.stdout', 'Android Log'),
                ('python threading', 'Android AsyncTask/Threads'),
                ('pip install', 'Gradle dependencies'),
                ('python scripts', 'Android services/activities')
            ]

        else:
            transformations = []

        # Apply transformations
        for old_term, new_term in transformations:
            # Case-insensitive replacement with word boundaries
            pattern = re.compile(r'\b' + re.escape(old_term) + r'\b', re.IGNORECASE)
            transformed = pattern.sub(new_term, transformed)

        return transformed

    def _generate_adapted_tags(self, original_tags: List[str], target_domain: str) -> List[str]:
        """Generate appropriate tags for the adapted pattern"""
        adapted_tags = original_tags.copy()

        # Add transfer-related tags
        adapted_tags.extend(['transferred', 'adapted', target_domain])

        # Remove domain-specific tags that don't apply
        domain_specific_removals = {
            'android_app': ['gradle', 'kotlin', 'java'],
            'embedded_esp32': ['esp32', 'platformio', 'freertos'],
            'python_cli': ['python', 'pip', 'argparse'],
            'cpp_library': ['cmake', 'conan']
        }

        # Don't remove tags that might still be relevant
        # (e.g., 'memory' tag is relevant across domains)

        return list(set(adapted_tags))  # Remove duplicates

    def _get_concept_keywords(self, concept: str) -> List[str]:
        """Get keywords associated with a concept"""
        concept_keywords = {
            'memory_management': ['memory', 'allocation', 'leak', 'heap', 'stack', 'pointer', 'malloc', 'free'],
            'performance': ['performance', 'speed', 'optimization', 'efficiency', 'bottleneck', 'profiling'],
            'error_handling': ['error', 'exception', 'try', 'catch', 'handling', 'recovery'],
            'resource_management': ['resource', 'lifecycle', 'cleanup', 'dispose', 'close'],
            'concurrency': ['thread', 'async', 'concurrent', 'parallel', 'lock', 'mutex'],
            'build_systems': ['build', 'compile', 'cmake', 'gradle', 'platformio', 'make']
        }

        return concept_keywords.get(concept, [])

    async def get_transfer_statistics(self) -> Dict[str, Any]:
        """Get statistics about cross-domain transfers"""
        all_patterns = await self.mcp_client.list_prompts()

        transferred_patterns = [p for p in all_patterns if 'transferred' in p.get('tags', [])]

        stats = {
            'total_patterns': len(all_patterns),
            'transferred_patterns': len(transferred_patterns),
            'transfer_ratio': len(transferred_patterns) / max(len(all_patterns), 1),
            'source_domains': set(),
            'target_domains': set()
        }

        for pattern in transferred_patterns:
            metadata = pattern.get('metadata', {})
            source = metadata.get('derived_from_domain')
            target = pattern.get('domain')

            if source:
                stats['source_domains'].add(source)
            if target:
                stats['target_domains'].add(target)

        stats['source_domains'] = list(stats['source_domains'])
        stats['target_domains'] = list(stats['target_domains'])

        return stats