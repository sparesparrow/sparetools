#!/usr/bin/env python3
"""
Simple Automated Learning Demonstration

Shows SpareTools automated learning capabilities working
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sparetools.learning.auto_orchestrator import AutomatedLearningOrchestrator
from sparetools.learning.cross_domain_transfer import CrossDomainTransferEngine
from sparetools.learning.quality_assessment import QualityAssessmentEngine
from sparetools.learning.pattern_evolution import PatternEvolutionSystem


async def demo():
    print("🧠 SpareTools Automated Learning Demo")
    print("=" * 50)

    # Initialize components
    learning = AutomatedLearningOrchestrator()
    transfer = CrossDomainTransferEngine()
    quality = QualityAssessmentEngine()
    evolution = PatternEvolutionSystem()

    print("🔧 Initializing...")
    await learning.initialize()
    await transfer.initialize()
    await quality.initialize()
    await evolution.initialize()

    # Get baseline stats
    stats = await learning.get_learning_statistics()
    print(f"📊 Knowledge base: {stats['total_patterns']} patterns")

    # Run quality assessment
    print("📊 Running quality assessment...")
    quality_report = await quality.assess_all_patterns()
    print(f"✅ Assessed {quality_report['total_patterns']} patterns")
    print(f"   Excellent: {len(quality_report['excellent_patterns'])}")
    print(f"   Needs improvement: {len(quality_report['needs_improvement'])}")

    # Run cross-domain transfer analysis
    print("🔄 Analyzing cross-domain transfers...")
    opportunities = await transfer.identify_transfer_opportunities()
    print(f"📋 Found {len(opportunities)} transfer opportunities")

    # Run pattern evolution
    print("🧬 Running pattern evolution...")
    evolution_results = await evolution.evolve_patterns()
    print(f"✅ Evolved {evolution_results.get('patterns_evolved', 0)} patterns")

    print("\n🎉 Automated learning systems are operational!")
    print("SpareTools now learns automatically from every analysis!")


if __name__ == "__main__":
    asyncio.run(demo())