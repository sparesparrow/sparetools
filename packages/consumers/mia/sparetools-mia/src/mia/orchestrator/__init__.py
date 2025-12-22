"""
MIA Project Orchestrator Integration

Integrates the MCP Project Orchestrator for managing MIA project lifecycle,
including template management, prompt management, and architecture visualization.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import asyncio

# Import MCP Project Orchestrator components
try:
    from mcp_orchestrator.fastmcp_integration import FastMCPIntegration
    from mcp_orchestrator.mcp_server import MCPServer
    from mcp_orchestrator.mermaid_generator import MermaidGenerator
    from mcp_orchestrator.project_orchestration import ProjectOrchestrator
except ImportError:
    # Fallback for development
    class FastMCPIntegration:
        def __init__(self): pass
        def get_available_templates(self): return []
        def get_template(self, name): return {}

    class MCPServer:
        def __init__(self, name): self.name = name

    class MermaidGenerator:
        def generate_diagram(self, config): return ""

    class ProjectOrchestrator:
        def __init__(self): pass
        def get_project_templates(self): return []
        def create_project_from_template(self, template, config): return {}


class MIAOrchestrator:
    """MIA-specific project orchestrator using MCP Project Orchestrator."""

    def __init__(self, templates_dir: Optional[str] = None, prompts_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.fastmcp = FastMCPIntegration()
        self.mermaid_generator = MermaidGenerator()
        self.project_orchestrator = ProjectOrchestrator()

        # Template and prompt directories
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent.parent / "templates"
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path(__file__).parent.parent / "prompts"

        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        # Load MIA-specific templates and prompts
        self._load_mia_templates()
        self._load_mia_prompts()

        self.logger.info("MIA Orchestrator initialized")

    def _load_mia_templates(self):
        """Load MIA-specific project templates."""
        # Define standard MIA project templates
        self.mia_templates = {
            "basic_iot": {
                "name": "Basic IoT Project",
                "description": "Simple IoT device with GPIO control and basic connectivity",
                "components": ["gpio_worker", "connectivity", "device_manager"],
                "config": {
                    "workers": {
                        "gpio": {"port": 5555},
                        "obd": {"port": 5556},
                        "rf": {"port": 5557}
                    },
                    "mcp": {
                        "enabled": True,
                        "transports": ["stdio", "http"]
                    }
                }
            },
            "automotive_gateway": {
                "name": "Automotive Gateway",
                "description": "OBD-II diagnostic gateway with RF capabilities",
                "components": ["gpio_worker", "obd_worker", "rf_worker", "connectivity"],
                "config": {
                    "workers": {
                        "gpio": {"port": 5555},
                        "obd": {"port": 5556, "protocol": "CAN"},
                        "rf": {"port": 5557, "frequency": 433920000}
                    },
                    "mcp": {
                        "enabled": True,
                        "transports": ["stdio", "http", "telegram"]
                    },
                    "automotive": {
                        "protocols": ["OBD-II", "CAN", "J1939"],
                        "rf_modules": ["CC1101", "NRF24L01"]
                    }
                }
            },
            "home_automation_hub": {
                "name": "Home Automation Hub",
                "description": "Central hub for home automation with multiple protocols",
                "components": ["gpio_worker", "rf_worker", "connectivity", "device_manager"],
                "config": {
                    "workers": {
                        "gpio": {"port": 5555, "pins": [17, 18, 27, 22]},
                        "rf": {"port": 5557, "protocols": ["433MHz", "868MHz", "2.4GHz"]}
                    },
                    "mcp": {
                        "enabled": True,
                        "transports": ["stdio", "http"]
                    },
                    "home_automation": {
                        "protocols": ["MQTT", "Zigbee", "Z-Wave", "RF433"],
                        "devices": ["lights", "sensors", "switches", "thermostats"]
                    }
                }
            }
        }

    def _load_mia_prompts(self):
        """Load MIA-specific AI prompts."""
        # Define standard MIA prompts for AI interactions
        self.mia_prompts = {
            "hardware-control": {
                "name": "Hardware Control Assistant",
                "description": "Prompt for controlling MIA hardware through MCP",
                "content": """
You are an AI assistant that can control physical hardware through the MIA (Modular IoT Architecture) system.

Available hardware controls:
- GPIO pins: Set digital pins high/low, configure as input/output
- OBD-II: Query vehicle diagnostic data (RPM, temperature, DTC codes)
- RF signals: Capture and replay radio frequency signals

Always provide clear feedback about what actions you're taking and their results.
Be cautious with hardware operations and confirm potentially destructive actions.
                """,
                "variables": ["hardware_type", "operation", "parameters"]
            },
            "diagnostic-analysis": {
                "name": "Vehicle Diagnostic Analyst",
                "description": "Prompt for analyzing vehicle diagnostic data",
                "content": """
You are a vehicle diagnostic expert analyzing data from OBD-II systems through MIA.

Capabilities:
- Interpret OBD-II PIDs and diagnostic trouble codes (DTCs)
- Analyze vehicle performance metrics
- Identify potential issues and recommend actions
- Generate diagnostic reports

Always explain your findings clearly and provide actionable recommendations.
                """,
                "variables": ["vehicle_data", "symptoms", "diagnostic_results"]
            },
            "rf-signal-analysis": {
                "name": "RF Signal Analyst",
                "description": "Prompt for analyzing RF signals captured by MIA",
                "content": """
You are an RF signal analysis expert working with signals captured by MIA hardware.

Capabilities:
- Analyze captured RF signals for protocol identification
- Decode common RF protocols (433MHz sensors, remote controls, etc.)
- Generate signal replay configurations
- Identify signal characteristics (frequency, modulation, timing)

Provide detailed technical analysis and clear explanations of your findings.
                """,
                "variables": ["signal_data", "frequency", "modulation", "protocol"]
            },
            "system-orchestration": {
                "name": "System Orchestrator",
                "description": "Prompt for orchestrating complex MIA system operations",
                "content": """
You are a system orchestrator capable of coordinating complex operations across multiple MIA components.

Capabilities:
- Execute multi-step workflows across hardware, network, and cloud components
- Coordinate parallel operations with proper sequencing
- Handle error recovery and fallback procedures
- Optimize resource usage and timing

Plan operations carefully and provide clear status updates throughout execution.
                """,
                "variables": ["workflow_type", "components", "objectives"]
            }
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get orchestrator system status."""
        return {
            "orchestrator": "mia",
            "templates_loaded": len(self.mia_templates),
            "prompts_loaded": len(self.mia_prompts),
            "templates_dir": str(self.templates_dir),
            "prompts_dir": str(self.prompts_dir),
            "timestamp": asyncio.get_event_loop().time()
        }

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available MIA project templates."""
        return [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "components": template["components"]
            }
            for template_id, template in self.mia_templates.items()
        ]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID."""
        return self.mia_templates.get(template_id)

    def get_available_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available MIA prompts."""
        return [
            {
                "id": prompt_id,
                "name": prompt["name"],
                "description": prompt["description"],
                "variables": prompt["variables"]
            }
            for prompt_id, prompt in self.mia_prompts.items()
        ]

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by ID."""
        return self.mia_prompts.get(prompt_id)

    def create_project_from_template(self, template_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a MIA project configuration from a template."""
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template {template_id} not found"}

        # Start with template config
        config = template["config"].copy()

        # Apply overrides
        if config_overrides:
            self._deep_update(config, config_overrides)

        return {
            "template": template_id,
            "name": template["name"],
            "config": config,
            "components": template["components"],
            "created": True
        }

    def _deep_update(self, base: Dict[str, Any], updates: Dict[str, Any]):
        """Deep update a dictionary with another dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def generate_architecture_diagram(self, config: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for MIA architecture."""
        # Create a simplified config for diagram generation
        diagram_config = {
            "title": "MIA Architecture",
            "components": config.get("components", []),
            "connections": self._extract_connections(config)
        }

        try:
            return self.mermaid_generator.generate_diagram(diagram_config)
        except Exception as e:
            self.logger.error(f"Failed to generate diagram: {e}")
            return self._generate_fallback_diagram(config)

    def _extract_connections(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract component connections from config."""
        connections = []

        # Extract worker connections
        workers = config.get("workers", {})
        for worker_name, worker_config in workers.items():
            port = worker_config.get("port")
            if port:
                connections.append({
                    "from": "MCP Server",
                    "to": f"{worker_name}_worker",
                    "protocol": "ZeroMQ",
                    "port": port
                })

        # Extract MCP transport connections
        mcp_config = config.get("mcp", {})
        transports = mcp_config.get("transports", [])
        for transport in transports:
            connections.append({
                "from": "AI Agent",
                "to": "MCP Server",
                "protocol": transport.upper(),
                "description": f"MCP {transport} transport"
            })

        return connections

    def _generate_fallback_diagram(self, config: Dict[str, Any]) -> str:
        """Generate a simple fallback Mermaid diagram."""
        components = config.get("components", ["core"])
        component_str = "\n".join(f"    {comp}(({comp.title()}))" for comp in components)

        return f"""graph TD
    A[AI Agent] --> B[MCP Server]
    B --> C[MIA Core]{component_str}

    subgraph "MIA Components"
    C
    end

    subgraph "Hardware Workers"
    D[GPIO Worker]
    E[OBD Worker]
    F[RF Worker]
    end

    C --> D
    C --> E
    C --> F"""

    def save_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Save a custom template."""
        try:
            template_path = self.templates_dir / f"{template_id}.json"
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            self.logger.info(f"Saved template: {template_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save template {template_id}: {e}")
            return False

    def save_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """Save a custom prompt."""
        try:
            prompt_path = self.prompts_dir / f"{prompt_id}.json"
            with open(prompt_path, 'w') as f:
                json.dump(prompt_data, f, indent=2)
            self.logger.info(f"Saved prompt: {prompt_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save prompt {prompt_id}: {e}")
            return False

    async def validate_project_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a MIA project configuration."""
        errors = []
        warnings = []

        # Check required components
        required_components = ["core"]
        components = config.get("components", [])
        for req_comp in required_components:
            if req_comp not in components:
                errors.append(f"Missing required component: {req_comp}")

        # Check worker configurations
        workers = config.get("workers", {})
        for worker_name, worker_config in workers.items():
            if "port" not in worker_config:
                warnings.append(f"Worker {worker_name} missing port configuration")

        # Check MCP configuration
        mcp_config = config.get("mcp", {})
        if mcp_config.get("enabled", False):
            transports = mcp_config.get("transports", [])
            if not transports:
                warnings.append("MCP enabled but no transports configured")

            # Validate transport configurations
            transport_configs = mcp_config.get("transports_config", {})
            for transport in transports:
                if transport not in ["stdio", "http", "telegram"]:
                    errors.append(f"Unsupported MCP transport: {transport}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }