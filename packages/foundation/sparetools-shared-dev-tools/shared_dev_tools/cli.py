#!/usr/bin/env python3
"""
Shared Development Tools CLI

Command-line interface for shared development tools.
"""

import argparse
import logging
import sys
from pathlib import Path


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def conan_command(args):
    """Handle Conan-related commands."""
    from shared_dev_tools.conan import get_default_conan, get_conan_version

    if args.subcommand == 'version':
        version = get_conan_version()
        if version:
            print(f"Conan version: {version}")
        else:
            print("Failed to get Conan version")
            return 1

    elif args.subcommand == 'path':
        conan_exe = get_default_conan()
        print(f"Conan executable: {conan_exe}")

    elif args.subcommand == 'list-packages':
        from shared_dev_tools.conan import get_all_packages_in_cache
        packages = get_all_packages_in_cache()
        if packages:
            print("Packages in cache:")
            for package in packages:
                print(f"  {package}")
        else:
            print("No packages found in cache")

    return 0


def test_command(args):
    """Handle test-related commands."""
    from pathlib import Path

    project_root = Path.cwd()

    if args.project_type == 'esp32':
        return run_esp32_tests(project_root, args)
    else:
        print(f"Unsupported project type: {args.project_type}")
        print("Supported types: esp32")
        return 1


def run_esp32_tests(project_root: Path, args) -> int:
    """Run ESP32 project tests."""
    try:
        # Import test runner
        from shared_dev_tools.test_runner import ESP32TestRunner

        runner = ESP32TestRunner(project_root, verbose=args.verbose)

        # Configure test options
        test_options = {
            'unit_only': args.unit_only,
            'integration_only': args.integration_only,
            'hardware_only': args.hardware_only,
            'coverage': args.coverage,
            'parallel': not args.no_parallel,
            'report_dir': Path(args.report_dir) if args.report_dir else None,
            'formats': args.format if args.format else ['console']
        }

        # Run tests
        return runner.run_tests(**test_options)

    except ImportError as e:
        print(f"❌ Test runner not available: {e}")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


def bootstrap_command(args):
    """Handle bootstrap-related commands."""
    from pathlib import Path

    project_root = Path.cwd()

    if args.project_type == 'esp32':
        return bootstrap_esp32_project(project_root, args.dry_run, args.verbose)
    else:
        print(f"Unsupported project type: {args.project_type}")
        print("Supported types: esp32")
        return 1


def bootstrap_esp32_project(project_root: Path, dry_run: bool = False, verbose: bool = False):
    """Bootstrap an ESP32 project."""
    try:
        # Import ESP32 bootstrap components
        from sparetools_bootstrap.esp32.platformio_setup import PlatformIOSetup
        from sparetools_bootstrap.esp32.esp32_config import ESP32ConfigManager

        print("🚀 ESP32 Project Bootstrap")
        print(f"Project root: {project_root}")

        # Initialize bootstrap components
        platformio_setup = PlatformIOSetup(project_root, dry_run, verbose)
        config_manager = ESP32ConfigManager(project_root, dry_run, verbose)

        # Generate ESP32 configuration
        config = config_manager.generate_config("esp32-project", "embedded/esp32")

        # Setup PlatformIO
        if not platformio_setup.setup(config.get('platformio', {})):
            print("❌ PlatformIO setup failed")
            return 1

        # Save configuration
        if not config_manager.save_config(config):
            print("❌ Configuration save failed")
            return 1

        # Generate environment file
        env_file = project_root / '.env'
        if not config_manager.generate_env_file(config, env_file):
            print("❌ Environment file generation failed")
            return 1

        print("✅ ESP32 project bootstrap completed successfully")
        print("\nNext steps:")
        print("  1. Review generated configuration in .esp32-config.json")
        print("  2. Update platformio.ini with your specific board configurations")
        print("  3. Run 'pio run' to build your project")

        return 0

    except ImportError as e:
        print(f"❌ Bootstrap components not available: {e}")
        print("Make sure sparetools-bootstrap package is available")
        return 1
    except Exception as e:
        print(f"❌ Bootstrap failed: {e}")
        return 1


def file_command(args):
    """Handle file-related commands."""
    if args.subcommand == 'symlink':
        from shared_dev_tools.util import symlink_with_check
        symlink_with_check(args.source, args.target)
        print(f"Created symlink: {args.target} -> {args.source}")

    elif args.subcommand == 'mkdir':
        from shared_dev_tools.util import create_whole_dir_path
        path = create_whole_dir_path(args.path)
        print(f"Created directory: {path}")

    return 0


def config_command(args):
    """Handle configuration-related commands."""
    from shared_dev_tools.config_loader import get_config_loader

    config_loader = get_config_loader()

    if args.subcommand == 'list':
        # List available configurations
        config_dir = getattr(config_loader, 'config_dir', Path('config'))
        if config_dir.exists():
            yaml_files = list(config_dir.glob('*.yaml'))
            if yaml_files:
                print("Available configurations:")
                for config_file in yaml_files:
                    print(f"  {config_file.stem}")
            else:
                print("No configuration files found")
        else:
            print(f"Configuration directory not found: {config_dir}")

    elif args.subcommand == 'show':
        if args.name:
            config = config_loader.load_yaml(args.name)
            if config:
                import yaml
                print(yaml.dump(config, default_flow_style=False))
            else:
                print(f"Configuration '{args.name}' not found")
                return 1

    return 0


def openssl_command(args):
    """Handle OpenSSL-related commands."""
    if args.subcommand == 'build-matrix':
        from shared_dev_tools.openssl import SmartBuildMatrix

        matrix_gen = SmartBuildMatrix()
        optimization_level = getattr(args, 'optimization', 'high')

        if hasattr(args, 'output') and args.output:
            matrix_gen.save_matrix_to_file(args.output, optimization_level)
        else:
            matrix_json = matrix_gen.generate_github_actions_matrix(optimization_level)
            print(matrix_json)

    elif args.subcommand == 'validate-fips':
        from shared_dev_tools.openssl import FIPSValidator

        validator = FIPSValidator()
        report = validator.validate_build()

        if hasattr(args, 'output') and args.output:
            validator.save_report(report, args.output)
        else:
            validator.print_report(report)

    elif args.subcommand == 'generate-sbom':
        from shared_dev_tools.openssl import SBOMGenerator, SBOMFormat

        generator = SBOMGenerator()
        format_type = SBOMFormat.SPDX

        if hasattr(args, 'format') and args.format:
            if args.format.lower() == 'cyclonedx':
                format_type = SBOMFormat.CYCLONEDX
            elif args.format.lower() == 'custom':
                format_type = SBOMFormat.CUSTOM

        openssl_version = getattr(args, 'version', '3.1.0')
        sbom = generator.generate_sbom(format_type=format_type, openssl_version=openssl_version)

        if hasattr(args, 'output') and args.output:
            generator.export_sbom(sbom, args.output)
        else:
            print("SBOM generation completed. Use --output to save to file.")

    elif args.subcommand == 'crypto-config':
        from shared_dev_tools.openssl import CryptoConfigManager

        config_manager = CryptoConfigManager()

        if hasattr(args, 'security_level') and args.security_level is not None:
            from shared_dev_tools.openssl.crypto_config import SecurityLevel
            level = SecurityLevel(args.security_level)
            config_manager.apply_security_level(level)
            print(f"Applied security level: {level.value}")

        if hasattr(args, 'enable_fips') and args.enable_fips:
            config_manager.enable_fips_mode()
            print("FIPS mode enabled")

        if hasattr(args, 'generate_config') and args.generate_config:
            config_manager.generate_openssl_config(args.generate_config)
            return 0

        if hasattr(args, 'validate') and args.validate:
            warnings = config_manager.validate_configuration()
            if warnings:
                print("Configuration validation warnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            else:
                print("Configuration validation passed")

        if hasattr(args, 'save') and args.save:
            config_manager.save_configuration(args.save)

        # Show current configuration
        recommendations = config_manager.get_security_recommendations()
        if recommendations:
            print("\nSecurity recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Shared Development Tools CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s conan version
  %(prog)s conan path
  %(prog)s file symlink /source /target
  %(prog)s config list
  %(prog)s config show artifactory\n  %(prog)s openssl build-matrix --optimization high\n  %(prog)s openssl validate-fips\n  %(prog)s openssl generate-sbom --format spdx\n  %(prog)s openssl crypto-config --security-level 2 --enable-fips
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Conan commands
    conan_parser = subparsers.add_parser('conan', help='Conan-related operations')
    conan_subparsers = conan_parser.add_subparsers(dest='subcommand')

    conan_subparsers.add_parser('version', help='Show Conan version')
    conan_subparsers.add_parser('path', help='Show Conan executable path')
    conan_subparsers.add_parser('list-packages', help='List packages in cache')

    # File commands
    file_parser = subparsers.add_parser('file', help='File operations')
    file_subparsers = file_parser.add_subparsers(dest='subcommand')

    symlink_parser = file_subparsers.add_parser('symlink', help='Create symlink')
    symlink_parser.add_argument('source', help='Source path')
    symlink_parser.add_argument('target', help='Target path')

    mkdir_parser = file_subparsers.add_parser('mkdir', help='Create directory structure')
    mkdir_parser.add_argument('path', help='Directory path to create')

    # Config commands
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='subcommand')

    config_subparsers.add_parser('list', help='List available configurations')

    show_parser = config_subparsers.add_parser('show', help='Show configuration content')
    show_parser.add_argument('name', nargs='?', help='Configuration name')

    # Bootstrap commands
    bootstrap_parser = subparsers.add_parser('bootstrap', help='Project bootstrap operations')
    bootstrap_parser.add_argument('project_type', choices=['esp32'], help='Project type to bootstrap')
    bootstrap_parser.add_argument('--dry-run', action='store_true', help='Perform dry run without making changes')

    # Test commands
    test_parser = subparsers.add_parser('test', help='Test execution operations')
    test_parser.add_argument('project_type', choices=['esp32'], help='Project type to test')
    test_parser.add_argument('--unit-only', action='store_true', help='Run only unit tests')
    test_parser.add_argument('--integration-only', action='store_true', help='Run only integration tests')
    test_parser.add_argument('--hardware-only', action='store_true', help='Run only hardware tests')
    test_parser.add_argument('--coverage', action='store_true', help='Generate coverage reports')
    test_parser.add_argument('--no-parallel', action='store_true', help='Disable parallel test execution')
    test_parser.add_argument('--report-dir', help='Directory for test reports')
    test_parser.add_argument('--format', action='append', choices=['console', 'json', 'html', 'junit'],
                           help='Output format (can be used multiple times)')

    # OpenSSL commands
    openssl_parser = subparsers.add_parser('openssl', help='OpenSSL development tools')
    openssl_subparsers = openssl_parser.add_subparsers(dest='subcommand')

    # build-matrix subcommand
    build_matrix_parser = openssl_subparsers.add_parser('build-matrix', help='Generate optimized build matrix')
    build_matrix_parser.add_argument('--optimization', choices=['high', 'medium', 'low'],
                                   default='high', help='Optimization level for matrix generation')
    build_matrix_parser.add_argument('--output', '-o', help='Output file for build matrix')

    # validate-fips subcommand
    validate_fips_parser = openssl_subparsers.add_parser('validate-fips', help='Validate FIPS compliance')
    validate_fips_parser.add_argument('--output', '-o', help='Output file for validation report')

    # generate-sbom subcommand
    generate_sbom_parser = openssl_subparsers.add_parser('generate-sbom', help='Generate Software Bill of Materials')
    generate_sbom_parser.add_argument('--format', choices=['spdx', 'cyclonedx', 'custom'],
                                    default='spdx', help='SBOM format')
    generate_sbom_parser.add_argument('--version', default='3.1.0', help='OpenSSL version')
    generate_sbom_parser.add_argument('--output', '-o', help='Output file for SBOM')

    # crypto-config subcommand
    crypto_config_parser = openssl_subparsers.add_parser('crypto-config', help='Cryptographic configuration management')
    crypto_config_parser.add_argument('--security-level', type=int, choices=[0, 1, 2, 3],
                                    help='Set security level (0-3)')
    crypto_config_parser.add_argument('--enable-fips', action='store_true',
                                    help='Enable FIPS mode')
    crypto_config_parser.add_argument('--generate-config', help='Generate OpenSSL config file')
    crypto_config_parser.add_argument('--validate', action='store_true',
                                    help='Validate current configuration')
    crypto_config_parser.add_argument('--save', help='Save configuration to file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)

    try:
        if args.command == 'bootstrap':
            return bootstrap_command(args)
        elif args.command == 'test':
            return test_command(args)
        elif args.command == 'conan':
            return conan_command(args)
        elif args.command == 'file':
            return file_command(args)
        elif args.command == 'config':
            return config_command(args)
        elif args.command == 'openssl':
            return openssl_command(args)
        else:
            parser.print_help()
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())