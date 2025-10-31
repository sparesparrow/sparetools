#!/usr/bin/env python3
"""
SpareTools OpenSSL CLI - Command-line interface for OpenSSL build tools.
"""

import sys
import json
import argparse
from pathlib import Path

from openssl_tools.openssl.build_matrix import SmartBuildMatrix


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="SpareTools OpenSSL build tools CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a high-optimization build matrix
  %(prog)s matrix generate --optimization high --output matrix.json

  # Generate a medium-optimization build matrix and print to stdout
  %(prog)s matrix generate --optimization medium

  # Use a custom config file
  %(prog)s matrix generate --config my-config.json --output matrix.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Matrix command
    matrix_parser = subparsers.add_parser("matrix", help="Build matrix generation")
    matrix_subparsers = matrix_parser.add_subparsers(dest="matrix_command", help="Matrix operations")

    # Generate subcommand
    generate_parser = matrix_subparsers.add_parser(
        "generate",
        help="Generate an optimized build matrix for CI/CD"
    )
    generate_parser.add_argument(
        "--optimization",
        choices=["high", "medium", "low"],
        default="high",
        help="Optimization level (default: high)"
    )
    generate_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (optional)"
    )
    generate_parser.add_argument(
        "--output",
        type=str,
        help="Output file path (optional, prints to stdout if not specified)"
    )
    generate_parser.add_argument(
        "--github-actions",
        action="store_true",
        help="Output in GitHub Actions matrix format"
    )

    return parser


def generate_matrix(args) -> int:
    """Generate build matrix based on arguments."""
    try:
        # Initialize the matrix generator
        config_file = args.config if hasattr(args, 'config') and args.config else None
        matrix_gen = SmartBuildMatrix(config_file=config_file)

        # Get optimization level
        optimization = getattr(args, 'optimization', 'high')

        # Generate matrix
        if getattr(args, 'github_actions', False):
            # GitHub Actions format
            matrix_json = matrix_gen.generate_github_actions_matrix(optimization)
        else:
            # Standard format
            matrix = matrix_gen.generate_matrix(optimization)
            matrix_json = json.dumps(
                [config.to_dict() for config in matrix],
                indent=2
            )

        # Output
        output_file = getattr(args, 'output', None)
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(matrix_json)
            print(f"✓ Build matrix generated: {output_path}", file=sys.stderr)
            return 0
        else:
            print(matrix_json)
            return 0

    except Exception as e:
        print(f"✗ Error generating matrix: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Handle matrix commands
    if args.command == "matrix":
        if not hasattr(args, 'matrix_command') or not args.matrix_command:
            parser.print_help()
            return 0

        if args.matrix_command == "generate":
            return generate_matrix(args)

    # Unknown command
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
