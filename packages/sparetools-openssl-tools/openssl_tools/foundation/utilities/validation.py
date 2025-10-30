#!/usr/bin/env python3
"""
MCP Configuration Validation Script
Validates MCP server configuration and dependencies for the GitHub Workflow Fixer.
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class MCPConfigValidator:
    """Validates MCP server configuration and dependencies."""
    
    def __init__(self, project_root: str = None):
        """Initialize validator with project root path."""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.successes = []
    
    def validate_dependencies(self) -> bool:
        """Validate that all required dependencies are installed."""
        print("🔍 Checking MCP dependencies...")
        
        required_packages = [
            'mcp',
            'fastmcp', 
            'httpx',
            'tenacity',
            'jinja2',
            'pydantic'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                self.successes.append(f"✓ {package} is installed")
            except ImportError:
                missing_packages.append(package)
                self.errors.append(f"✗ {package} is not installed")
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All MCP dependencies are installed")
        return True
    
    def validate_github_token(self) -> bool:
        """Validate GitHub token configuration."""
        print("🔍 Checking GitHub token...")
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            self.errors.append("✗ GITHUB_TOKEN environment variable is not set")
            print("❌ GITHUB_TOKEN environment variable is not set")
            print("Set it with: export GITHUB_TOKEN=your_token_here")
            return False
        
        if not token.startswith(('ghp_', 'github_pat_')):
            self.warnings.append("⚠ GITHUB_TOKEN format may be incorrect (should start with 'ghp_' or 'github_pat_')")
            print("⚠ Warning: GITHUB_TOKEN format may be incorrect")
        
        self.successes.append("✓ GITHUB_TOKEN is configured")
        print("✅ GitHub token is configured")
        return True
    
    def validate_mcp_server_file(self) -> bool:
        """Validate MCP server file exists and is valid."""
        print("🔍 Checking MCP server file...")
        
        mcp_server_path = self.project_root / "scripts" / "mcp" / "github_workflow_fixer_mcp.py"
        
        if not mcp_server_path.exists():
            self.errors.append(f"✗ MCP server file not found: {mcp_server_path}")
            print(f"❌ MCP server file not found: {mcp_server_path}")
            return False
        
        # Try to import the module to check for syntax errors
        try:
            spec = importlib.util.spec_from_file_location("github_workflow_fixer_mcp", mcp_server_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.successes.append("✓ MCP server file is valid")
            print("✅ MCP server file is valid")
            return True
        except Exception as e:
            self.errors.append(f"✗ MCP server file has errors: {e}")
            print(f"❌ MCP server file has errors: {e}")
            return False
    
    def validate_cursor_config(self) -> bool:
        """Validate Cursor configuration files."""
        print("🔍 Checking Cursor configuration...")
        
        cursor_dir = self.project_root / ".cursor"
        mcp_config_path = cursor_dir / "mcp.json"
        cli_config_path = cursor_dir / "cli-config.json"
        
        if not cursor_dir.exists():
            self.errors.append("✗ .cursor directory not found")
            print("❌ .cursor directory not found")
            return False
        
        # Check mcp.json
        if not mcp_config_path.exists():
            self.errors.append("✗ .cursor/mcp.json not found")
            print("❌ .cursor/mcp.json not found")
            return False
        
        try:
            with open(mcp_config_path, 'r') as f:
                mcp_config = json.load(f)
            
            if "mcpServers" not in mcp_config:
                self.errors.append("✗ .cursor/mcp.json missing 'mcpServers' key")
                print("❌ .cursor/mcp.json missing 'mcpServers' key")
                return False
            
            if "github-workflow-fixer" not in mcp_config["mcpServers"]:
                self.errors.append("✗ github-workflow-fixer not found in .cursor/mcp.json")
                print("❌ github-workflow-fixer not found in .cursor/mcp.json")
                return False
            
            self.successes.append("✓ .cursor/mcp.json is valid")
            
        except json.JSONDecodeError as e:
            self.errors.append(f"✗ .cursor/mcp.json has invalid JSON: {e}")
            print(f"❌ .cursor/mcp.json has invalid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"✗ Error reading .cursor/mcp.json: {e}")
            print(f"❌ Error reading .cursor/mcp.json: {e}")
            return False
        
        # Check cli-config.json
        if not cli_config_path.exists():
            self.errors.append("✗ .cursor/cli-config.json not found")
            print("❌ .cursor/cli-config.json not found")
            return False
        
        try:
            with open(cli_config_path, 'r') as f:
                cli_config = json.load(f)
            
            if "mcp" not in cli_config:
                self.errors.append("✗ .cursor/cli-config.json missing 'mcp' key")
                print("❌ .cursor/cli-config.json missing 'mcp' key")
                return False
            
            mcp_config = cli_config["mcp"]
            if not mcp_config.get("enabled", False):
                self.warnings.append("⚠ MCP is disabled in .cursor/cli-config.json")
                print("⚠ Warning: MCP is disabled in .cursor/cli-config.json")
            
            servers = mcp_config.get("servers", [])
            if "github-workflow-fixer" not in servers:
                self.errors.append("✗ github-workflow-fixer not found in MCP servers list")
                print("❌ github-workflow-fixer not found in MCP servers list")
                return False
            
            self.successes.append("✓ .cursor/cli-config.json is valid")
            
        except json.JSONDecodeError as e:
            self.errors.append(f"✗ .cursor/cli-config.json has invalid JSON: {e}")
            print(f"❌ .cursor/cli-config.json has invalid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"✗ Error reading .cursor/cli-config.json: {e}")
            print(f"❌ Error reading .cursor/cli-config.json: {e}")
            return False
        
        print("✅ Cursor configuration is valid")
        return True
    
    def validate_unified_manager(self) -> bool:
        """Validate unified workflow manager file."""
        print("🔍 Checking unified workflow manager...")
        
        manager_path = self.project_root / "scripts" / "unified_workflow_manager.py"
        
        if not manager_path.exists():
            self.errors.append(f"✗ Unified workflow manager not found: {manager_path}")
            print(f"❌ Unified workflow manager not found: {manager_path}")
            return False
        
        # Try to import the module
        try:
            spec = importlib.util.spec_from_file_location("unified_workflow_manager", manager_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.successes.append("✓ Unified workflow manager is valid")
            print("✅ Unified workflow manager is valid")
            return True
        except Exception as e:
            self.errors.append(f"✗ Unified workflow manager has errors: {e}")
            print(f"❌ Unified workflow manager has errors: {e}")
            return False
    
    def test_github_api_connection(self) -> bool:
        """Test connection to GitHub API."""
        print("🔍 Testing GitHub API connection...")
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            self.errors.append("✗ Cannot test GitHub API without token")
            print("❌ Cannot test GitHub API without token")
            return False
        
        try:
            import requests
            
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'MCP-Config-Validator'
            }
            
            # Test with a simple API call
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.successes.append(f"✓ GitHub API connection successful (user: {user_data.get('login', 'unknown')})")
                print(f"✅ GitHub API connection successful (user: {user_data.get('login', 'unknown')})")
                return True
            elif response.status_code == 401:
                self.errors.append("✗ GitHub API authentication failed (invalid token)")
                print("❌ GitHub API authentication failed (invalid token)")
                return False
            else:
                self.errors.append(f"✗ GitHub API request failed (status: {response.status_code})")
                print(f"❌ GitHub API request failed (status: {response.status_code})")
                return False
                
        except requests.RequestException as e:
            self.errors.append(f"✗ GitHub API connection failed: {e}")
            print(f"❌ GitHub API connection failed: {e}")
            return False
        except ImportError:
            self.errors.append("✗ requests library not available for API testing")
            print("❌ requests library not available for API testing")
            return False
    
    def test_mcp_server_startup(self) -> bool:
        """Test if MCP server can start successfully."""
        print("🔍 Testing MCP server startup...")
        
        mcp_server_path = self.project_root / "scripts" / "mcp" / "github_workflow_fixer_mcp.py"
        
        if not mcp_server_path.exists():
            self.errors.append("✗ MCP server file not found for startup test")
            print("❌ MCP server file not found for startup test")
            return False
        
        try:
            # Try to run the MCP server with --help to test startup
            result = subprocess.run([
                sys.executable, str(mcp_server_path), '--help'
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            if result.returncode == 0:
                self.successes.append("✓ MCP server can start successfully")
                print("✅ MCP server can start successfully")
                return True
            else:
                self.errors.append(f"✗ MCP server startup failed: {result.stderr}")
                print(f"❌ MCP server startup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.errors.append("✗ MCP server startup test timed out")
            print("❌ MCP server startup test timed out")
            return False
        except Exception as e:
            self.errors.append(f"✗ MCP server startup test failed: {e}")
            print(f"❌ MCP server startup test failed: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🚀 Starting MCP configuration validation...\n")
        
        checks = [
            self.validate_dependencies,
            self.validate_github_token,
            self.validate_mcp_server_file,
            self.validate_cursor_config,
            self.validate_unified_manager,
            self.test_github_api_connection,
            self.test_mcp_server_startup
        ]
        
        all_passed = True
        
        for check in checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"✗ Validation check failed: {e}")
                print(f"❌ Validation check failed: {e}")
                all_passed = False
            print()  # Add spacing between checks
        
        return all_passed
    
    def print_summary(self):
        """Print validation summary."""
        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"  {success}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ VALIDATION FAILED")
            print("Fix the errors above before using the MCP server.")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print("The MCP server should work, but consider addressing the warnings.")
            return True
        else:
            print("✅ VALIDATION PASSED")
            print("The MCP server is ready to use!")
            return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate MCP configuration")
    parser.add_argument("--project-root", help="Project root directory (default: auto-detect)")
    parser.add_argument("--quiet", action="store_true", help="Only show errors and summary")
    
    args = parser.parse_args()
    
    validator = MCPConfigValidator(args.project_root)
    
    if args.quiet:
        # Suppress print output for quiet mode
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            all_passed = validator.validate_all()
    else:
        all_passed = validator.validate_all()
    
    summary_passed = validator.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if (all_passed and summary_passed) else 1)


if __name__ == "__main__":
    main()
