#!/usr/bin/env python
"""
SpareTools CLI

Command-line interface for running test procedures and managing the test framework.
"""

import click
import sys
import os

# Add the sparetools package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sparetools.test_framework.procedures.test_procedure import exec as run_test_procedure


@click.group()
def cli():
    """SpareTools - Test Framework CLI"""
    pass


@cli.command()
@click.argument('test_path')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output', '-o', help='Output directory for results')
def run(test_path, config, output):
    """Run test procedures using existing logic"""
    try:
        # Call existing exec logic with new interface
        # Note: This is a simplified interface - the actual exec function
        # may need additional parameters based on the original implementation
        run_test_procedure(test_path, header_dict=None)
        click.echo(f"Test procedure completed: {test_path}")
    except Exception as e:
        click.echo(f"Error running test procedure: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', help='Configuration file path')
def validate(config):
    """Validate configuration and environment setup"""
    click.echo("Configuration validation not yet implemented")


if __name__ == '__main__':
    cli()