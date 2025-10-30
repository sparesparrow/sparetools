#!/usr/bin/env python3
"""
OpenSSL Tools - Main CLI Entry Point

This is the main command-line interface for OpenSSL development tools.
It provides access to all major functionality through a unified CLI.
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the path to import openssl_tools
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from openssl_tools.automation.workflow_management import WorkflowManager, UnifiedWorkflowManager
from openssl_tools.development.build_system import BuildCacheManager, BuildOptimizer
from openssl_tools.development.package_management import ConanRemoteManager, ConanOrchestrator
# from openssl_tools.foundation.utilities import validate_mcp_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenSSL Tools - Comprehensive OpenSSL Development Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s workflow analyze --repo sparesparrow/openssl-tools
  %(prog)s build optimize --cache-dir ~/.openssl-cache
  %(prog)s conan setup-remote --token $GITHUB_TOKEN
  %(prog)s validate mcp-config
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="OpenSSL Tools 1.2.0"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True
    )
    
    # Workflow management commands
    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Workflow management commands"
    )
    workflow_subparsers = workflow_parser.add_subparsers(
        dest="workflow_action",
        help="Workflow actions",
        required=True
    )
    
    # Workflow analyze
    analyze_parser = workflow_subparsers.add_parser(
        "analyze",
        help="Analyze workflow failures"
    )
    analyze_parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo'")
    analyze_parser.add_argument("--limit", type=int, default=20, help="Maximum workflow runs to analyze")
    analyze_parser.add_argument("--unified", action="store_true", help="Use unified MCP-powered analysis")
    
    # Workflow monitor
    monitor_parser = workflow_subparsers.add_parser(
        "monitor",
        help="Monitor workflow status"
    )
    monitor_parser.add_argument("--repo", required=True, help="Repository in format 'owner/repo'")
    monitor_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    
    # Build optimization commands
    build_parser = subparsers.add_parser(
        "build",
        help="Build optimization commands"
    )
    build_subparsers = build_parser.add_subparsers(
        dest="build_action",
        help="Build actions",
        required=True
    )
    
    # Build optimize
    optimize_parser = build_subparsers.add_parser(
        "optimize",
        help="Optimize build configuration"
    )
    optimize_parser.add_argument("--cache-dir", help="Build cache directory")
    optimize_parser.add_argument("--max-size", type=int, default=10, help="Maximum cache size in GB")
    
    # Conan management commands
    conan_parser = subparsers.add_parser(
        "conan",
        help="Conan package management commands"
    )
    conan_subparsers = conan_parser.add_subparsers(
        dest="conan_action",
        help="Conan actions",
        required=True
    )
    
    # Conan setup-remote
    setup_remote_parser = conan_subparsers.add_parser(
        "setup-remote",
        help="Setup Conan remote for GitHub Packages"
    )
    setup_remote_parser.add_argument("--token", help="GitHub token")
    setup_remote_parser.add_argument("--username", help="GitHub username")
    
    # Validation commands
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validation commands"
    )
    validate_subparsers = validate_parser.add_subparsers(
        dest="validate_action",
        help="Validation actions",
        required=True
    )
    
    # Validate MCP config
    mcp_config_parser = validate_subparsers.add_parser(
        "mcp-config",
        help="Validate MCP configuration"
    )
    mcp_config_parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    
    # Security commands
    security_parser = subparsers.add_parser("security", help="Security commands")
    security_subparsers = security_parser.add_subparsers(dest="security_action", help="Security actions")
    
    # Security validate
    security_validate_parser = security_subparsers.add_parser("validate", help="Validate build security")
    security_validate_parser.add_argument("--config", help="Security configuration file")
    
    # Test commands
    test_parser = subparsers.add_parser("test", help="Testing commands")
    test_subparsers = test_parser.add_subparsers(dest="test_action", help="Test actions")
    
    # Test run
    test_run_parser = test_subparsers.add_parser("run", help="Run test harness")
    test_run_parser.add_argument("--suite", help="Test suite to run")
    
    # Monitor commands
    monitor_parser = subparsers.add_parser("monitor", help="Monitoring commands")
    monitor_subparsers = monitor_parser.add_subparsers(dest="monitor_action", help="Monitor actions")
    
    # Monitor status
    monitor_status_parser = monitor_subparsers.add_parser("status", help="Report system status")
    monitor_status_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    try:
        if args.command == "workflow":
            handle_workflow_command(args)
        elif args.command == "build":
            handle_build_command(args)
        elif args.command == "conan":
            handle_conan_command(args)
        elif args.command == "validate":
            handle_validate_command(args)
        elif args.command == "security":
            handle_security_command(args)
        elif args.command == "test":
            handle_test_command(args)
        elif args.command == "monitor":
            handle_monitor_command(args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_workflow_command(args):
    """Handle workflow management commands."""
    if args.workflow_action == "analyze":
        if args.unified:
            import asyncio
            manager = UnifiedWorkflowManager(args.repo)
            result = asyncio.run(manager.analyze_workflows(args.limit))
            print(result)
        else:
            repo_owner, repo_name = args.repo.split('/', 1)
            manager = WorkflowManager(repo_owner, repo_name)
            result = manager.check_status()
            print(result)
    elif args.workflow_action == "monitor":
        repo_owner, repo_name = args.repo.split('/', 1)
        manager = WorkflowManager(repo_owner, repo_name)
        result = manager.check_status(args.hours)
        print(result)


def handle_build_command(args):
    """Handle build optimization commands."""
    if args.build_action == "optimize":
        cache_dir = Path(args.cache_dir) if args.cache_dir else None
        optimizer = BuildCacheManager(cache_dir, max_cache_size_gb=args.max_size)
        result = optimizer.optimize_cache()
        print(f"Build optimization completed: {result}")


def handle_conan_command(args):
    """Handle Conan management commands."""
    if args.conan_action == "setup-remote":
        manager = ConanRemoteManager(args.token, args.username)
        success = manager.setup_github_packages_remote()
        if success:
            print("✅ GitHub Packages remote setup successfully")
        else:
            print("❌ Failed to setup GitHub Packages remote")
            sys.exit(1)


def handle_validate_command(args):
    """Handle validation commands."""
    if args.validate_action == "mcp-config":
        # Import the validation script directly
        import sys
        sys.path.insert(0, str(project_root))
        from openssl_tools.foundation.utilities.validation import MCPConfigValidator
        validator = MCPConfigValidator()
        success = validator.validate_all()
        if not args.quiet:
            validator.print_summary()
        sys.exit(0 if success else 1)


def handle_security_command(args):
    """Handle security commands."""
    if args.security_action == "validate":
        from openssl_tools.security.build_validation import PreBuildValidator
        validator = PreBuildValidator()
        success = validator.validate_build_security(args.config)
        print("Security validation completed" if success else "Security validation failed")
        sys.exit(0 if success else 1)


def handle_test_command(args):
    """Handle test commands."""
    if args.test_action == "run":
        from openssl_tools.testing.test_harness import NgapyTestHarness
        harness = NgapyTestHarness()
        success = harness.run_tests(args.suite)
        print("Tests completed" if success else "Tests failed")
        sys.exit(0 if success else 1)


def handle_monitor_command(args):
    """Handle monitor commands."""
    if args.monitor_action == "status":
        from openssl_tools.monitoring.status_reporter import StatusReporter
        reporter = StatusReporter()
        status = reporter.get_system_status()
        if args.format == "json":
            import json
            print(json.dumps(status, indent=2))
        else:
            print(f"System Status: {status.get('status', 'unknown')}")
            print(f"Details: {status.get('details', 'No details available')}")


if __name__ == "__main__":
    main()
