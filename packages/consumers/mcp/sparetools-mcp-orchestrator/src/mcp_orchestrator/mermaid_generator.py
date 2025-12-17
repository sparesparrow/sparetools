"""Mermaid Generator - Generate architecture diagrams and visualizations."""

import logging
from typing import Dict, List, Any, Optional


class MermaidGenerator:
    """Generate Mermaid diagrams for SpareTools architecture visualization."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Mermaid Generator.

        Args:
            config: Optional generator configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

    def generate_system_architecture(self) -> str:
        """Generate system architecture diagram.

        Returns:
            Mermaid diagram as string
        """
        diagram = """graph TD
    subgraph "Layer 5: Consumers"
        C1[sparetools-openssl]
        C2[sparetools-mia]
        C3[sparetools-mcp-orchestrator]
        C4[sparetools-android]
    end

    subgraph "Layer 4: Orchestration"
        O1[sparetools-mcp-orchestrator]
        O2[sparetools-bootstrap]
    end

    subgraph "Layer 3: Utilities"
        U1[sparetools-openssl-tools]
        U2[sparetools-shared-dev-tools]
    end

    subgraph "Layer 2: Runtime"
        R1[sparetools-cpython]
        R2[sparetools-openssl]
    end

    subgraph "Layer 1: Foundation"
        F1[sparetools-base]
        F2[sparetools-bootstrap]
        F3[sparetools-shared-dev-tools]
        F4[sparetools-cpython]
    end

    C1 --> U1
    C2 --> R2
    C3 --> O1
    C4 --> R2

    O1 --> U2
    O2 --> F2

    U1 --> R1
    U2 --> F3

    R1 --> F4
    R2 --> F1

    style F1 fill:#e1f5fe
    style F4 fill:#e1f5fe
    style R1 fill:#f3e5f5
    style R2 fill:#f3e5f5
    style U1 fill:#e8f5e8
    style U2 fill:#e8f5e8
    style O1 fill:#fff3e0
    style O2 fill:#fff3e0
    style C1 fill:#fce4ec
    style C2 fill:#fce4ec
    style C3 fill:#fce4ec
    style C4 fill:#fce4ec
"""

        return diagram

    def generate_package_dependencies(self, package_name: str) -> str:
        """Generate dependency diagram for a package.

        Args:
            package_name: Name of package to analyze

        Returns:
            Mermaid diagram as string
        """
        # Mock dependency analysis
        dependencies = {
            "sparetools-openssl": ["sparetools-base", "sparetools-cpython"],
            "sparetools-mia": ["sparetools-base", "sparetools-cpython", "sparetools-openssl"],
            "sparetools-mcp-orchestrator": ["sparetools-base", "sparetools-cpython"],
            "sparetools-android": ["sparetools-base", "sparetools-cpython", "sparetools-openssl"]
        }

        deps = dependencies.get(package_name, [])

        if not deps:
            return f"graph TD\n    {package_name}[{package_name}]\n    note[No dependencies found]"

        diagram = f"graph TD\n    {package_name}[{package_name}]\n"

        for dep in deps:
            safe_dep = dep.replace("-", "_").replace(".", "_")
            diagram += f"    {package_name} --> {safe_dep}[{dep}]\n"

        return diagram

    def generate_consumer_workflow(self, consumer_name: str) -> str:
        """Generate workflow diagram for a consumer.

        Args:
            consumer_name: Name of consumer

        Returns:
            Mermaid diagram as string
        """
        workflows = {
            "openssl": """graph TD
    A[Source Code] --> B[Select Build Method]
    B --> C{Method?}
    C -->|Perl Configure| D[Configure OpenSSL]
    C -->|CMake| E[Generate CMake]
    C -->|Autotools| F[Run Autotools]
    D --> G[Build & Install]
    E --> G
    F --> G
    G --> H[Run Tests]
    H --> I[Security Validation]
    I --> J[Package Creation]""",

            "mia": """graph TD
    A[IoT Project] --> B[Initialize MIA Core]
    B --> C[Device Discovery]
    C --> D[Connectivity Setup]
    D --> E[Cloud Integration]
    E --> F[Security Validation]
    F --> G[Deploy to Devices]""",

            "mcp": """graph TD
    A[MCP Request] --> B{Request Type}
    B -->|Tool Call| C[Route to Tool]
    B -->|Resource| D[Fetch Resource]
    C --> E[Execute Tool]
    D --> F[Return Resource]
    E --> G[Format Response]
    F --> G
    G --> H[Return to Client]"""
        }

        return workflows.get(consumer_name, f"graph TD\n    A[{consumer_name}]\n    B[Workflow not defined]")

    def generate_layer_diagram(self, layer_number: int) -> str:
        """Generate diagram for a specific layer.

        Args:
            layer_number: Layer number (1-5)

        Returns:
            Mermaid diagram as string
        """
        layers = {
            1: {
                "name": "Foundation",
                "packages": ["sparetools-base", "sparetools-bootstrap", "sparetools-shared-dev-tools", "sparetools-cpython"],
                "color": "#e1f5fe"
            },
            2: {
                "name": "Runtime",
                "packages": ["sparetools-cpython", "sparetools-openssl"],
                "color": "#f3e5f5"
            },
            3: {
                "name": "Utilities",
                "packages": ["sparetools-openssl-tools", "sparetools-shared-dev-tools"],
                "color": "#e8f5e8"
            },
            4: {
                "name": "Orchestration",
                "packages": ["sparetools-mcp-orchestrator", "sparetools-bootstrap"],
                "color": "#fff3e0"
            },
            5: {
                "name": "Consumers",
                "packages": ["sparetools-openssl", "sparetools-mia", "sparetools-mcp-orchestrator", "sparetools-android"],
                "color": "#fce4ec"
            }
        }

        if layer_number not in layers:
            return f"graph TD\n    A[Layer {layer_number}]\n    B[Invalid layer number]"

        layer = layers[layer_number]

        diagram = f"graph TD\n    subgraph \"Layer {layer_number}: {layer['name']}\"\n"

        for i, package in enumerate(layer["packages"]):
            diagram += f"        P{i}[{package}]\n"

        diagram += "    end\n"

        # Add styling
        for i in range(len(layer["packages"])):
            diagram += f"    style P{i} fill:{layer['color']}\n"

        return diagram

    def generate_integration_diagram(self) -> str:
        """Generate cross-consumer integration diagram.

        Returns:
            Mermaid diagram as string
        """
        diagram = """graph TD
    subgraph "OpenSSL Consumer"
        OSSL[sparetools-openssl]
        OSSL_TOOLS[sparetools-openssl-tools]
    end

    subgraph "MIA Consumer"
        MIA[sparetools-mia]
        OBD[sparetools-obd-sim]
    end

    subgraph "MCP Consumer"
        MCP[sparetools-mcp-orchestrator]
        TINYMCP[sparetools-tinymcp]
        MCPSERVER[sparetools-mcpserver-cpp]
    end

    subgraph "Android Consumer"
        ANDROID[sparetools-android]
    end

    subgraph "Foundation"
        BASE[sparetools-base]
        CPYTHON[sparetools-cpython]
        BOOTSTRAP[sparetools-bootstrap]
    end

    OSSL --> OSSL_TOOLS
    MIA --> OBD
    MCP --> TINYMCP
    MCP --> MCPSERVER

    OSSL --> BASE
    MIA --> BASE
    MCP --> BASE
    ANDROID --> BASE

    OSSL --> CPYTHON
    MIA --> CPYTHON
    MCP --> CPYTHON
    ANDROID --> CPYTHON

    MIA --> OSSL
    ANDROID --> OSSL

    BOOTSTRAP --> BASE
    BOOTSTRAP --> CPYTHON

    style BASE fill:#e1f5fe
    style CPYTHON fill:#e1f5fe
    style BOOTSTRAP fill:#e1f5fe
    style OSSL fill:#f3e5f5
    style OSSL_TOOLS fill:#e8f5e8
    style MIA fill:#fce4ec
    style OBD fill:#fce4ec
    style MCP fill:#fff3e0
    style TINYMCP fill:#fff3e0
    style MCPSERVER fill:#fff3e0
    style ANDROID fill:#fce4ec
"""

        return diagram

    def export_diagram(self, diagram: str, filename: str, format: str = "markdown") -> str:
        """Export diagram to file.

        Args:
            diagram: Mermaid diagram string
            filename: Output filename
            format: Output format ('markdown', 'html')

        Returns:
            Path to exported file
        """
        if format == "markdown":
            content = f"```mermaid\n{diagram}\n```"
            ext = ".md"
        elif format == "html":
            content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Diagram</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</head>
<body>
    <div class="mermaid">
{diagram}
    </div>
</body>
</html>"""
            ext = ".html"
        else:
            raise ValueError(f"Unsupported format: {format}")

        output_file = f"{filename}{ext}"
        with open(output_file, 'w') as f:
            f.write(content)

        self.logger.info(f"Diagram exported to: {output_file}")
        return output_file