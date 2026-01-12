"""
FlatBuffers Integration for SpareTools MCP Client

Provides high-performance zero-copy prompt storage and retrieval
using FlatBuffers binary format for the cognitive architecture.
"""

import flatbuffers
from pathlib import Path
from typing import Dict, Any, Optional, List
import time
import os

# Import generated FlatBuffers classes
try:
    from mcp.fbs.v1.CognitivePrompt import CognitivePrompt
    from mcp.fbs.v1.PromptLayer import PromptLayer
    from mcp.fbs.v1.Domain import Domain
    from mcp.fbs.v1.Confidence import Confidence
    from mcp.fbs.v1.EffectivenessMetrics import EffectivenessMetrics
    from mcp.fbs.v1.DomainMapping import DomainMapping
    from mcp.fbs.v1.KeyValue import KeyValue
    from mcp.fbs.v1.Metadata import Metadata
    from mcp.fbs.v1.UUID import UUID
    from mcp.fbs.v1.Timestamp import Timestamp
    from mcp.fbs.v1.SemanticVersion import SemanticVersion
except ImportError:
    # Fallback if FlatBuffers modules not available
    CognitivePrompt = None
    PromptLayer = None
    Domain = None
    Confidence = None
    EffectivenessMetrics = None
    DomainMapping = None
    KeyValue = None
    Metadata = None
    UUID = None
    Timestamp = None
    SemanticVersion = None


class FlatBuffersPromptClient:
    """
    High-performance prompt access using FlatBuffers

    Target performance: <0.1ms for prompt retrieval (zero-copy)
    """

    def __init__(self):
        if CognitivePrompt is None:
            raise ImportError("FlatBuffers modules not available. Run FlatBuffers compilation first.")

    def create_prompt(self, prompt_data: Dict[str, Any]) -> bytes:
        """
        Create FlatBuffers prompt from dictionary

        Performance target: <0.5ms for typical prompt
        """
        builder = flatbuffers.Builder(2048)  # Larger buffer for complex prompts

        # Build nested structures first (reverse order for FlatBuffers)
        metadata_offset = self._build_metadata(builder, prompt_data.get('metadata'))
        tags_offset = self._build_string_vector(builder, prompt_data.get('tags', []))
        applicable_domains_offset = self._build_domain_vector(builder, prompt_data.get('applicable_domains', []))
        domain_mappings_offset = self._build_domain_mappings(builder, prompt_data.get('domain_mappings', []))
        effectiveness_offset = self._build_effectiveness_metrics(builder, prompt_data.get('effectiveness'))
        source_episodes_offset = self._build_string_vector(builder, prompt_data.get('source_episodes', []))
        related_patterns_offset = self._build_string_vector(builder, prompt_data.get('related_patterns', []))
        evolutionary_history_offset = self._build_string_vector(builder, prompt_data.get('evolutionary_history', []))

        # Build base prompt strings
        id_offset = builder.CreateString(prompt_data.get('id', ''))
        name_offset = builder.CreateString(prompt_data.get('name', ''))
        description_offset = builder.CreateString(prompt_data.get('description', ''))
        content_offset = builder.CreateString(prompt_data.get('content', ''))
        learned_from_session_offset = builder.CreateString(prompt_data.get('learned_from_session', ''))
        validation_status_offset = builder.CreateString(prompt_data.get('validation_status', 'experimental'))

        # Build timestamps
        created_at_offset = self._build_timestamp(builder, prompt_data.get('created_at'))
        updated_at_offset = self._build_timestamp(builder, prompt_data.get('updated_at'))

        # Build version
        version_offset = self._build_semantic_version(builder, prompt_data.get('version'))

        # Create the CognitivePrompt
        CognitivePrompt.Start(builder)

        # Base prompt fields
        CognitivePrompt.AddId(builder, id_offset)
        CognitivePrompt.AddName(builder, name_offset)
        CognitivePrompt.AddDescription(builder, description_offset)
        CognitivePrompt.AddContent(builder, content_offset)
        CognitivePrompt.AddDomain(builder, self._map_domain(prompt_data.get('domain')))
        CognitivePrompt.AddTags(builder, tags_offset)
        CognitivePrompt.AddMetadata(builder, metadata_offset)
        CognitivePrompt.AddCreatedAt(builder, created_at_offset)
        CognitivePrompt.AddUpdatedAt(builder, updated_at_offset)
        CognitivePrompt.AddVersion(builder, version_offset)

        # Cognitive-specific fields
        CognitivePrompt.AddLayer(builder, self._map_prompt_layer(prompt_data.get('layer')))
        CognitivePrompt.AddAbstractionLevel(builder, prompt_data.get('abstraction_level', 5))
        CognitivePrompt.AddSourceEpisodes(builder, source_episodes_offset)
        CognitivePrompt.AddRelatedPatterns(builder, related_patterns_offset)
        CognitivePrompt.AddEffectiveness(builder, effectiveness_offset)
        CognitivePrompt.AddApplicableDomains(builder, applicable_domains_offset)
        CognitivePrompt.AddDomainMappings(builder, domain_mappings_offset)
        CognitivePrompt.AddLearnedFromSession(builder, learned_from_session_offset)
        CognitivePrompt.AddValidationStatus(builder, validation_status_offset)
        CognitivePrompt.AddEvolutionaryHistory(builder, evolutionary_history_offset)

        prompt = CognitivePrompt.End(builder)
        builder.Finish(prompt)

        return bytes(builder.Output())

    def parse_prompt(self, buffer: bytes) -> Dict[str, Any]:
        """
        Parse FlatBuffers prompt to dictionary

        Performance target: <0.1ms (zero-copy!)
        """
        prompt = CognitivePrompt.GetRootAsCognitivePrompt(buffer, 0)

        return {
            'id': prompt.Id().decode('utf-8') if prompt.Id() else '',
            'name': prompt.Name().decode('utf-8') if prompt.Name() else '',
            'description': prompt.Description().decode('utf-8') if prompt.Description() else '',
            'content': prompt.Content().decode('utf-8') if prompt.Content() else '',
            'domain': Domain.Domain.Name(prompt.Domain()),
            'layer': PromptLayer.PromptLayer.Name(prompt.Layer()),
            'abstraction_level': prompt.AbstractionLevel(),
            'tags': self._extract_string_vector(prompt.Tags, prompt.TagsLength),
            'metadata': self._extract_metadata(prompt.Metadata()),
            'created_at': self._extract_timestamp(prompt.CreatedAt()),
            'updated_at': self._extract_timestamp(prompt.UpdatedAt()),
            'version': self._extract_semantic_version(prompt.Version()),
            'source_episodes': self._extract_string_vector(prompt.SourceEpisodes, prompt.SourceEpisodesLength),
            'related_patterns': self._extract_string_vector(prompt.RelatedPatterns, prompt.RelatedPatternsLength),
            'effectiveness': self._extract_effectiveness_metrics(prompt.Effectiveness()),
            'applicable_domains': self._extract_domain_vector(prompt.ApplicableDomains, prompt.ApplicableDomainsLength),
            'domain_mappings': self._extract_domain_mappings(prompt.DomainMappings, prompt.DomainMappingsLength),
            'learned_from_session': prompt.LearnedFromSession().decode('utf-8') if prompt.LearnedFromSession() else '',
            'validation_status': prompt.ValidationStatus().decode('utf-8') if prompt.ValidationStatus() else '',
            'evolutionary_history': self._extract_string_vector(prompt.EvolutionaryHistory, prompt.EvolutionaryHistoryLength)
        }

    # Builder helper methods
    def _build_metadata(self, builder: flatbuffers.Builder, metadata: Optional[Dict]) -> int:
        if not metadata or not metadata.get('entries'):
            return 0

        entries_offsets = []
        for entry in metadata['entries']:
            key_offset = builder.CreateString(entry.get('key', ''))
            value_offset = builder.CreateString(entry.get('value', ''))
            KeyValue.Start(builder)
            KeyValue.AddKey(builder, key_offset)
            KeyValue.AddValue(builder, value_offset)
            entries_offsets.append(KeyValue.End(builder))

        entries_vector = builder.CreateVectorOfTables(entries_offsets)
        Metadata.Start(builder)
        Metadata.AddEntries(builder, entries_vector)
        return Metadata.End(builder)

    def _build_string_vector(self, builder: flatbuffers.Builder, strings: List[str]) -> int:
        if not strings:
            return 0
        offsets = [builder.CreateString(s) for s in strings]
        return builder.CreateVectorOfTables(offsets)

    def _build_domain_vector(self, builder: flatbuffers.Builder, domains: List[str]) -> int:
        if not domains:
            return 0
        domain_enums = [self._map_domain(d) for d in domains]
        return builder.CreateVector(domain_enums)

    def _build_domain_mappings(self, builder: flatbuffers.Builder, mappings: List[Dict]) -> int:
        if not mappings:
            return 0

        offsets = []
        for mapping in mappings:
            DomainMapping.Start(builder)
            DomainMapping.AddSourceDomain(builder, self._map_domain(mapping.get('source_domain')))
            DomainMapping.AddTargetDomain(builder, self._map_domain(mapping.get('target_domain')))
            DomainMapping.AddMappingConfidence(builder, self._map_confidence(mapping.get('mapping_confidence')))
            DomainMapping.AddTransformationRules(builder, builder.CreateString(mapping.get('transformation_rules', '')))
            offsets.append(DomainMapping.End(builder))

        return builder.CreateVectorOfTables(offsets)

    def _build_effectiveness_metrics(self, builder: flatbuffers.Builder, effectiveness: Optional[Dict]) -> int:
        EffectivenessMetrics.Start(builder)
        EffectivenessMetrics.AddUsageCount(builder, effectiveness.get('usage_count', 0) if effectiveness else 0)
        EffectivenessMetrics.AddSuccessRate(builder, effectiveness.get('success_rate', 0.0) if effectiveness else 0.0)
        EffectivenessMetrics.AddAverageTimeSavedMinutes(builder, effectiveness.get('average_time_saved_minutes', 0.0) if effectiveness else 0.0)
        EffectivenessMetrics.AddUserSatisfactionScore(builder, effectiveness.get('user_satisfaction_score', 0.0) if effectiveness else 0.0)
        EffectivenessMetrics.AddLastUsed(builder, self._build_timestamp(builder, effectiveness.get('last_used') if effectiveness else None))
        return EffectivenessMetrics.End(builder)

    def _build_timestamp(self, builder: flatbuffers.Builder, timestamp: Optional[Dict]) -> int:
        Timestamp.Start(builder)
        Timestamp.AddSeconds(builder, timestamp.get('seconds', 0) if timestamp else int(time.time()))
        Timestamp.AddNanoseconds(builder, timestamp.get('nanoseconds', 0) if timestamp else 0)
        return Timestamp.End(builder)

    def _build_semantic_version(self, builder: flatbuffers.Builder, version: Optional[Dict]) -> int:
        SemanticVersion.Start(builder)
        SemanticVersion.AddMajor(builder, version.get('major', 1) if version else 1)
        SemanticVersion.AddMinor(builder, version.get('minor', 0) if version else 0)
        SemanticVersion.AddPatch(builder, version.get('patch', 0) if version else 0)
        SemanticVersion.AddPrerelease(builder, builder.CreateString(version.get('prerelease', '') if version else ''))
        SemanticVersion.AddBuild(builder, builder.CreateString(version.get('build', '') if version else ''))
        return SemanticVersion.End(builder)

    # Parser helper methods
    def _extract_string_vector(self, getter_func, length: int) -> List[str]:
        return [getter_func(i).decode('utf-8') if getter_func(i) else '' for i in range(length)]

    def _extract_metadata(self, metadata) -> Optional[Dict]:
        if not metadata:
            return None
        return {
            'entries': [
                {'key': metadata.Entries(i).Key().decode('utf-8'), 'value': metadata.Entries(i).Value().decode('utf-8')}
                for i in range(metadata.EntriesLength())
            ]
        }

    def _extract_timestamp(self, timestamp) -> Optional[Dict]:
        if not timestamp:
            return None
        return {
            'seconds': timestamp.Seconds(),
            'nanoseconds': timestamp.Nanoseconds()
        }

    def _extract_semantic_version(self, version) -> Optional[Dict]:
        if not version:
            return None
        return {
            'major': version.Major(),
            'minor': version.Minor(),
            'patch': version.Patch(),
            'prerelease': version.Prerelease().decode('utf-8') if version.Prerelease() else '',
            'build': version.Build().decode('utf-8') if version.Build() else ''
        }

    def _extract_effectiveness_metrics(self, effectiveness) -> Optional[Dict]:
        if not effectiveness:
            return None
        return {
            'usage_count': effectiveness.UsageCount(),
            'success_rate': effectiveness.SuccessRate(),
            'average_time_saved_minutes': effectiveness.AverageTimeSavedMinutes(),
            'user_satisfaction_score': effectiveness.UserSatisfactionScore(),
            'last_used': self._extract_timestamp(effectiveness.LastUsed())
        }

    def _extract_domain_vector(self, getter_func, length: int) -> List[str]:
        return [Domain.Domain.Name(getter_func(i)) for i in range(length)]

    def _extract_domain_mappings(self, getter_func, length: int) -> List[Dict]:
        mappings = []
        for i in range(length):
            mapping = getter_func(i)
            if mapping:
                mappings.append({
                    'source_domain': Domain.Domain.Name(mapping.SourceDomain()),
                    'target_domain': Domain.Domain.Name(mapping.TargetDomain()),
                    'mapping_confidence': Confidence.Confidence.Name(mapping.MappingConfidence()),
                    'transformation_rules': mapping.TransformationRules().decode('utf-8') if mapping.TransformationRules() else ''
                })
        return mappings

    # Enum mapping helpers
    def _map_prompt_layer(self, layer_name: str) -> int:
        mapping = {
            'Perceptual': PromptLayer.PromptLayer.Perceptual,
            'Episodic': PromptLayer.PromptLayer.Episodic,
            'Semantic': PromptLayer.PromptLayer.Semantic,
            'Procedural': PromptLayer.PromptLayer.Procedural,
            'MetaCognitive': PromptLayer.PromptLayer.MetaCognitive,
            'Transfer': PromptLayer.PromptLayer.Transfer,
            'Evaluative': PromptLayer.PromptLayer.Evaluative
        }
        return mapping.get(layer_name, PromptLayer.PromptLayer.Semantic)

    def _map_domain(self, domain_name: str) -> int:
        mapping = {
            'General': Domain.Domain.General,
            'SoftwareDevelopment': Domain.Domain.SoftwareDevelopment,
            'EmbeddedSystem': Domain.Domain.EmbeddedSystem,
            'MobileDevelopment': Domain.Domain.MobileDevelopment,
            'WebDevelopment': Domain.Domain.WebDevelopment,
            'DataScience': Domain.Domain.DataScience,
            'DevOps': Domain.Domain.DevOps,
            'Security': Domain.Domain.Security,
            'MedicalAnalysis': Domain.Domain.MedicalAnalysis,
            'FinancialModeling': Domain.Domain.FinancialModeling
        }
        return mapping.get(domain_name, Domain.Domain.General)

    def _map_confidence(self, confidence_name: str) -> int:
        mapping = {
            'Low': Confidence.Confidence.Low,
            'Medium': Confidence.Confidence.Medium,
            'High': Confidence.Confidence.High,
            'VeryHigh': Confidence.Confidence.VeryHigh
        }
        return mapping.get(confidence_name, Confidence.Confidence.Medium)


class SparetoolsFlatBuffersClient:
    """
    Integration with SpareTools MCP workflow

    Provides zero-copy performance for cognitive prompt operations.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.fb_client = FlatBuffersPromptClient()

    def store_learned_pattern(self, pattern: Dict[str, Any]) -> None:
        """
        Store pattern using high-performance FlatBuffers

        Performance target: <0.5ms storage time
        """
        # Convert to FlatBuffers
        buffer = self.fb_client.create_prompt(pattern)

        # Write to file
        filename = f"{pattern['name']}.fbs"
        filepath = self.storage_path / filename

        with open(filepath, 'wb') as f:
            f.write(buffer)

        print(f"✓ Stored FlatBuffers pattern: {filename} ({len(buffer)} bytes)")

    def get_pattern(self, name: str) -> Dict[str, Any]:
        """
        Retrieve pattern with zero-copy parsing

        Performance target: <0.1ms retrieval time
        """
        filepath = self.storage_path / f"{name}.fbs"

        with open(filepath, 'rb') as f:
            buffer = f.read()

        # Zero-copy parse!
        return self.fb_client.parse_prompt(buffer)

    def query_patterns(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fast query across all patterns

        Performance target: <1ms for 1000 patterns
        """
        patterns = []

        for file in self.storage_path.glob("*.fbs"):
            with open(file, 'rb') as f:
                buffer = f.read()

            # Fast parse
            pattern = self.fb_client.parse_prompt(buffer)

            # Filter by tags if specified
            if tags is None or any(tag in pattern.get('tags', []) for tag in tags):
                patterns.append(pattern)

        return patterns

    def migrate_from_json(self, json_dir: Path) -> int:
        """
        Migrate existing JSON prompts to FlatBuffers format

        Returns number of prompts migrated
        """
        migrated_count = 0

        for json_file in json_dir.glob("*.json"):
            # Read JSON
            with open(json_file, 'r') as f:
                prompt_data = json.load(f)

            # Convert and store as FlatBuffers
            self.store_learned_pattern(prompt_data)
            migrated_count += 1

            print(f"  ✓ Migrated {json_file.name}")

        return migrated_count