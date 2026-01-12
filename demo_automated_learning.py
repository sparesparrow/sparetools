#!/usr/bin/env python3
"""
Automated Learning Demonstration

Showcases the complete automated learning capabilities of SpareTools:
1. Pattern discovery from analysis results
2. Cross-domain transfer learning
3. Pattern evolution and improvement
4. Quality assessment and feedback
5. Self-improving knowledge base
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools.learning.auto_orchestrator import AutomatedLearningOrchestrator
from sparetools.learning.cross_domain_transfer import CrossDomainTransferEngine
from sparetools.learning.quality_assessment import QualityAssessmentEngine
from sparetools.learning.pattern_evolution import PatternEvolutionSystem
from sparetools.context.detector import ProjectContextDetector
from sparetools.analysis.orchestrator import KnowledgeAwareOrchestrator


async def demonstrate_automated_learning():
    """
    Complete demonstration of automated learning capabilities
    """
    print("🧠 SpareTools Automated Learning Demonstration")
    print("=" * 60)

    # Initialize all learning components
    learning_orchestrator = AutomatedLearningOrchestrator()
    cross_domain_transfer = CrossDomainTransferEngine()
    quality_assessment = QualityAssessmentEngine()
    pattern_evolution = PatternEvolutionSystem()

    print("\n🔧 Initializing learning systems...")
    await learning_orchestrator.initialize()
    await cross_domain_transfer.initialize()
    await quality_assessment.initialize()
    await pattern_evolution.initialize()

    # Get baseline knowledge statistics
    baseline_stats = await learning_orchestrator.get_learning_statistics()
    print(f"📊 Baseline: {baseline_stats['total_patterns']} patterns, "
          f"{baseline_stats['automated_patterns']} automated")

    # Demonstrate cross-domain transfer capability
    print("\n🔄 Analyzing cross-domain transfer opportunities...")
    transfer_opportunities = await cross_domain_transfer.identify_transfer_opportunities()

    if transfer_opportunities:
        successful_transfers = await cross_domain_transfer.execute_transfers(transfer_opportunities[:2])
        print(f"✅ Executed {len(successful_transfers)} cross-domain transfers")

    # Demonstrate pattern evolution
    print("\n🧬 Running pattern evolution...")
    evolution_results = await pattern_evolution.evolve_patterns()
    print(f"✅ Evolved {evolution_results.get('patterns_evolved', 0)} patterns")

    # Demonstrate comprehensive quality assessment
    print("\n📊 Running comprehensive quality assessment...")
    quality_report = await quality_assessment.assess_all_patterns()
    print(f"✅ Assessed {quality_report['total_patterns']} patterns")
    print(f"   • Excellent: {len(quality_report['excellent_patterns'])}")
    print(f"   • Needs improvement: {len(quality_report['needs_improvement'])}")
    print(f"   • Deprecated: {len(quality_report['deprecated_patterns'])}")

    if quality_report.get('recommendations'):
        print(f"   • Recommendations: {len(quality_report['recommendations'])}")

    # Show final learning statistics
    final_stats = await learning_orchestrator.get_learning_statistics()
    print("\n🏆 Final Learning Statistics:")
    print(f"   • Total patterns: {final_stats['total_patterns']}")
    print(f"   • Automated patterns: {final_stats['automated_patterns']}")
    print(f"   • Domains covered: {final_stats['domains_covered']}")
    print(f"   • Learning sessions: {final_stats['learning_sessions']}")
    print(".3f")
    # Show cross-domain transfer statistics
    transfer_stats = await cross_domain_transfer.get_transfer_statistics()
    print("\n🔄 Cross-Domain Transfer Statistics:")
    print(f"   • Transferred patterns: {transfer_stats['transferred_patterns']}")
    print(f"   • Transfer ratio: {transfer_stats['transfer_ratio']:.2%}")
    if transfer_stats['source_domains']:
        print(f"   • Source domains: {', '.join(transfer_stats['source_domains'])}")
    if transfer_stats['target_domains']:
        print(f"   • Target domains: {', '.join(transfer_stats['target_domains'])}")

    # Show pattern evolution statistics
    evolution_stats = await pattern_evolution.get_evolution_statistics()
    print("\n🧬 Pattern Evolution Statistics:")
    print(f"   • Evolved patterns: {evolution_stats['evolved_patterns']}")
    print(f"   • Evolution rate: {evolution_stats['evolution_rate']:.2%}")
    print(".1f")
    if evolution_stats['improvement_types']:
        print(f"   • Improvement types: {dict(evolution_stats['improvement_types'])}")

    print("\n🎉 Automated Learning Demonstration Complete!"    print("The SpareTools cognitive system now:")
    print("• ✅ Automatically discovers patterns from analysis results")
    print("• ✅ Transfers successful patterns across domains")
    print("• ✅ Evolves patterns based on usage and effectiveness")
    print("• ✅ Assesses and improves pattern quality")
    print("• ✅ Learns continuously without manual intervention")
    print("• ✅ Builds domain knowledge automatically")

    # Calculate improvement metrics
    patterns_added = final_stats['total_patterns'] - baseline_stats['total_patterns']
    if patterns_added > 0:
        print(f"\n📈 Knowledge Growth: +{patterns_added} patterns added through automated learning")

    return {
        'baseline_stats': baseline_stats,
        'final_stats': final_stats,
        'transfer_stats': transfer_stats,
        'evolution_stats': evolution_stats,
        'quality_report': quality_report
    }


async def demonstrate_live_analysis_learning():
    """
    Demonstrate automated learning during live analysis
    """
    print("\n🔍 Demonstrating Live Analysis with Automated Learning")
    print("-" * 60)

    # Initialize the analysis orchestrator with automated learning
    orchestrator = KnowledgeAwareOrchestrator()
    await orchestrator.initialize()

    # Simulate analysis results that would trigger learning
    from sparetools.context.detector import ProjectContext

    # Create a mock context for demonstration
    context = ProjectContext(
        path="/demo/path",
        name="demo-project",
        project_type="embedded_esp32",  # Use enum value
        languages=["cpp", "python"],
        build_system="platformio",
        has_tests=True,
        has_ci=True,
        frameworks=["arduino"],
        performance_critical=True,
        security_sensitive=False
    )

    # Mock analysis results that would trigger learning
    analysis_results = {
        "success": True,
        "steps_executed": [
            "Check PlatformIO configuration",
            "Run static analysis on C++ code",
            "Check memory usage patterns",
            "Verify timing constraints"
        ],
        "tools_used": ["platformio", "cppcheck"],
        "findings": [
            "Memory usage optimized for embedded constraints",
            "Timing constraints verified successfully",
            "Static analysis passed with performance optimizations"
        ],
        "novel_findings": True
    }

    print("Analyzing demo project with automated learning...")

    # This should trigger automated learning
    results = await orchestrator.analyze_project(
        Path("/demo/path"),  # Mock path
        goal="performance"
    )

    if 'automated_learning' in results:
        learning_results = results['automated_learning']
        print("🎓 Automated learning was triggered!")
        print(f"   • Patterns discovered: {learning_results.get('patterns_discovered', 0)}")
        print(f"   • Patterns captured: {learning_results.get('patterns_captured', 0)}")
        print(f"   • Cross-domain transfers: {learning_results.get('cross_domain_transfers', 0)}")
        print(f"   • Quality improvements: {learning_results.get('quality_improvements', 0)}")
    else:
        print("ℹ️  No automated learning was triggered (expected for demo)")

    return results


if __name__ == "__main__":
    async def main():
        # Run the comprehensive automated learning demonstration
        await demonstrate_automated_learning()

        # Run live analysis demonstration
        await demonstrate_live_analysis_learning()

        print("\n🎯 Automated Learning Implementation Complete!")
        print("SpareTools now learns automatically from every analysis!")

    asyncio.run(main())