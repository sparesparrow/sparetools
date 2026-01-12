"""
Docker Tool Adapter

Adapter for Docker container orchestration and analysis.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class DockerAdapter(BaseToolAdapter):
    """Adapter for Docker container management and analysis"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("docker", executable)

    @property
    def tool_category(self):
        return ToolCategory.CONTAINERIZATION

    def get_capabilities(self) -> ToolCapabilities:
        """Get Docker capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if docker is available
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="docker",
            version=version,
            category=ToolCategory.CONTAINERIZATION,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=[],  # Language agnostic
            supported_file_types=["Dockerfile", ".dockerfile"],
            can_analyze_directories=True,
            can_analyze_files=True,
            requires_compilation=False,
            supports_custom_rules=False,
            supports_parallel_execution=False,
            has_timeout_support=True,
            output_formats=["json", "text"],
            metadata={
                "description": "Container platform for building, running, and managing containers",
                "website": "https://docker.com/",
                "features": [
                    "container_building", "image_management", "container_scanning",
                    "networking", "storage", "security_scanning"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if docker is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "Docker version 20.10.21, build baeda1f"
                version_match = re.search(r'Docker version (\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build Docker command"""
        cmd = [self.executable]

        # Subcommand
        subcommand = kwargs.get('subcommand', 'build')

        if subcommand == 'build':
            cmd.append('build')

            # Build context
            context = kwargs.get('context', '.')
            cmd.append(str(context))

            # Dockerfile
            dockerfile = kwargs.get('dockerfile')
            if dockerfile:
                cmd.extend(['-f', str(dockerfile)])

            # Tags
            tags = kwargs.get('tags', [])
            if tags:
                for tag in tags:
                    cmd.extend(['-t', tag])

            # Build args
            build_args = kwargs.get('build_args', {})
            for key, value in build_args.items():
                cmd.extend(['--build-arg', f'{key}={value}'])

            # No cache
            if kwargs.get('no_cache', False):
                cmd.append('--no-cache')

            # Pull latest base images
            if kwargs.get('pull', False):
                cmd.append('--pull')

        elif subcommand == 'run':
            cmd.append('run')

            # Detached mode
            if kwargs.get('detached', False):
                cmd.append('-d')

            # Remove container after execution
            if kwargs.get('rm', True):
                cmd.append('--rm')

            # Environment variables
            env_vars = kwargs.get('env_vars', {})
            for key, value in env_vars.items():
                cmd.extend(['-e', f'{key}={value}'])

            # Volumes
            volumes = kwargs.get('volumes', [])
            for volume in volumes:
                cmd.extend(['-v', volume])

            # Ports
            ports = kwargs.get('ports', [])
            for port in ports:
                cmd.extend(['-p', port])

            # Image name
            image = kwargs.get('image')
            if image:
                cmd.append(image)

            # Command to run
            container_command = kwargs.get('command')
            if container_command:
                if isinstance(container_command, list):
                    cmd.extend(container_command)
                else:
                    cmd.append(container_command)

        elif subcommand == 'scan':
            # Docker Scout or similar scanning
            cmd.extend(['scout', 'cves'])

            # Image to scan
            image = kwargs.get('image')
            if image:
                cmd.append(image)

        elif subcommand == 'inspect':
            cmd.append('inspect')

            # Format output as JSON
            cmd.extend(['--format', '{{json .}}'])

            # Target (container or image)
            inspect_target = kwargs.get('target')
            if inspect_target:
                cmd.append(inspect_target)

        # Additional arguments
        extra_args = kwargs.get('extra_args')
        if extra_args:
            if isinstance(extra_args, list):
                cmd.extend(extra_args)
            else:
                cmd.append(extra_args)

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse Docker output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Determine subcommand from context or parse accordingly
            if 'inspect' in full_output and full_output.strip().startswith('{'):
                return self._parse_inspect_output(full_output, exit_code)
            elif 'scout' in full_output or 'vulnerabilities' in full_output.lower():
                return self._parse_scan_output(full_output, exit_code)
            else:
                return self._parse_build_run_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse Docker output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_inspect_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse docker inspect output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        try:
            data = json.loads(output.strip())
            metrics = {}

            # Extract basic information
            if isinstance(data, list) and data:
                container_info = data[0]
            else:
                container_info = data

            # Basic container/image info
            metrics.update({
                'id': container_info.get('Id'),
                'created': container_info.get('Created'),
                'architecture': container_info.get('Architecture'),
                'os': container_info.get('Os')
            })

            # Size information
            size = container_info.get('Size')
            if size:
                metrics['size'] = size

            # Health check
            health = container_info.get('State', {}).get('Health')
            if health:
                metrics['health_status'] = health.get('Status')
                if health.get('Status') != 'healthy':
                    issue = ToolIssue(
                        severity=Severity.MEDIUM,
                        message=f"Container health check failed: {health.get('Status')}",
                        category="health_check",
                        metadata={'health': health}
                    )
                    result.issues = [issue]

            result.metrics = metrics

        except json.JSONDecodeError:
            result.error_message = "Invalid JSON output from docker inspect"

        return result

    def _parse_scan_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse docker scan output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Parse vulnerability information
        lines = output.strip().split('\n')

        for line in lines:
            # Look for vulnerability patterns
            vuln_match = re.search(r'(HIGH|MEDIUM|LOW|CRITICAL)\s+(.+)', line, re.IGNORECASE)
            if vuln_match:
                severity_str, description = vuln_match.groups()

                severity_map = {
                    'CRITICAL': Severity.CRITICAL,
                    'HIGH': Severity.HIGH,
                    'MEDIUM': Severity.MEDIUM,
                    'LOW': Severity.LOW
                }

                issue = ToolIssue(
                    severity=severity_map.get(severity_str.upper(), Severity.MEDIUM),
                    message=f"Security vulnerability: {description}",
                    category="security_vulnerability",
                    metadata={'severity': severity_str}
                )
                issues.append(issue)

        result.issues = issues
        result.metrics = metrics

        return result

    def _parse_build_run_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse docker build/run output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        lines = output.strip().split('\n')

        # Extract build information
        for line in lines:
            # Build step completion
            if 'Step ' in line and '/' in line:
                step_match = re.search(r'Step (\d+)/(\d+)', line)
                if step_match:
                    current_step = int(step_match.group(1))
                    total_steps = int(step_match.group(2))
                    metrics.update({
                        'current_step': current_step,
                        'total_steps': total_steps,
                        'progress': f"{current_step}/{total_steps}"
                    })

            # Error detection
            if 'error' in line.lower() or 'failed' in line.lower():
                issue = ToolIssue(
                    severity=Severity.HIGH,
                    message=f"Docker operation failed: {line}",
                    category="build_error"
                )
                issues.append(issue)

        result.issues = issues
        result.metrics = metrics

        return result