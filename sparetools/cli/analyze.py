"""
Sparetools CLI - Knowledge-augmented development tools
"""

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

    async def run():
        orchestrator = KnowledgeAwareOrchestrator()

        # Initialize MCP connections
        await orchestrator.initialize()

        # Run analysis
        results = await orchestrator.analyze_project(
            Path(project_path),
            goal=goal
        )

        # Display results
        click.echo(click.style("✓ Analysis complete!", fg='green', bold=True))
        click.echo(f"\nFindings: {len(results.get('findings', []))}")

        if results.get('novel_findings'):
            click.echo(click.style("\n🆕 Novel patterns discovered!", fg='yellow'))
            for finding in results.get('findings', []):
                click.echo(f"  • {finding}")

        # Show connection status
        status = await orchestrator.mcp_client.get_connection_status()
        click.echo(f"\n🔌 MCP Status:")
        for service, info in status.items():
            color = 'green' if info['available'] else 'red'
            click.echo(click.style(f"  {service}: {info['type']}", fg=color))

    asyncio.run(run())


@cli.command()
def knowledge():
    """Query and manage development knowledge"""

    async def run():
        orchestrator = KnowledgeAwareOrchestrator()
        await orchestrator.initialize()

        # List available prompts
        prompts = await orchestrator.mcp_client.list_prompts()

        click.echo(click.style("📚 Available Knowledge:", fg='blue', bold=True))
        click.echo(f"   {len(prompts)} prompts stored")

        for prompt in prompts[:10]:  # Show first 10
            click.echo(f"\n• {prompt['name']}")
            click.echo(f"  {prompt['description']}")
            click.echo(f"  Tags: {', '.join(prompt['tags'])}")

        if len(prompts) > 10:
            click.echo(f"\n... and {len(prompts) - 10} more")

    asyncio.run(run())


@cli.command()
@click.argument('project_name')
def learn(project_name):
    """Interactive mode to teach sparetools new patterns"""

    click.echo(f"🎓 Teaching Sparetools about {project_name}...")
    click.echo("This mode captures YOUR expertise as reusable prompts")

    # Map project names to paths
    projects_base = Path.home() / "projects"
    project_paths = {
        "esp32-bpm-detector": projects_base / "embedded" / "esp32-bpm-detector",
        "mia": projects_base / "embedded" / "mia",
        "cliphist-android": projects_base / "android" / "cliphist-android",
        "sparetools": projects_base / "dev-tools" / "sparetools"
    }

    project_path = project_paths.get(project_name)
    if not project_path or not project_path.exists():
        click.echo(click.style(f"❌ Project '{project_name}' not found", fg='red'))
        click.echo(f"Available projects: {', '.join(project_paths.keys())}")
        return

    click.echo(f"\nDescribe the analysis workflow you use for {project_name}:")
    click.echo("(Type 'done' when finished)\n")

    steps = []
    while True:
        step = input(f"Step {len(steps)+1}: ").strip()
        if step.lower() == 'done':
            break
        steps.append(step)

    tools = input("\nWhich tools do you use? (comma-separated): ").strip().split(',')
    tools = [t.strip() for t in tools if t.strip()]

    tags = input("Tags for this workflow (comma-separated): ").strip().split(',')
    tags = [t.strip() for t in tags if t.strip()]

    async def store():
        orchestrator = KnowledgeAwareOrchestrator()
        await orchestrator.initialize()

        # Create prompt content
        prompt_content = f"""Learned workflow for {project_name}:

Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(steps))}

Tools: {', '.join(tools)}
"""

        # Store the learned workflow
        await orchestrator.mcp_client.store_prompt(
            name=f"workflow-{project_name}-{tags[0] if tags else 'custom'}",
            description=f"Learned workflow for {project_name}",
            content=prompt_content,
            metadata={
                "layer": "Procedural",
                "domain": project_name,
                "tags": tags + [project_name],
                "abstraction_level": 3,
                "effectiveness_score": 0.9,  # User-taught patterns are highly effective
                "usage_count": 0
            }
        )

        click.echo(click.style(f"\n✅ Learned workflow stored!", fg='green'))

    asyncio.run(store())


if __name__ == '__main__':
    cli()