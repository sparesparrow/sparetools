"""
Optional diagram renderer for Mermaid diagrams.

This module provides functionality for rendering Mermaid diagrams to various formats.
Requires mermaid CLI to be installed for actual rendering.
"""

from pathlib import Path
from typing import Optional
import subprocess
import json

from .diagram_types import DiagramType, RenderFormat, RenderConfig


class MermaidRenderer:
    """Renderer for Mermaid diagrams to various output formats."""
    
    def __init__(self, mermaid_cli_path: Optional[str] = None):
        """Initialize the renderer.
        
        Args:
            mermaid_cli_path: Optional path to mermaid CLI executable.
                            If None, assumes 'mmdc' is in PATH.
        """
        self.mermaid_cli = mermaid_cli_path or "mmdc"
        
    def check_cli_available(self) -> bool:
        """Check if mermaid CLI is available.
        
        Returns:
            True if CLI is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.mermaid_cli, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def render_to_file(
        self,
        diagram: str,
        output_path: Path,
        format: RenderFormat = RenderFormat.SVG,
        config: Optional[RenderConfig] = None
    ) -> Path:
        """Render a diagram to a file.
        
        Args:
            diagram: Mermaid diagram definition
            output_path: Path to save rendered output
            format: Output format (SVG, PNG, PDF)
            config: Optional render configuration
            
        Returns:
            Path to rendered file
            
        Raises:
            RuntimeError: If mermaid CLI is not available or rendering fails
        """
        if not self.check_cli_available():
            raise RuntimeError(
                f"Mermaid CLI ({self.mermaid_cli}) not found. "
                "Install with: npm install -g @mermaid-js/mermaid-cli"
            )
        
        # Create temporary input file
        input_file = output_path.with_suffix(".mmd")
        input_file.write_text(diagram)
        
        try:
            # Build command
            cmd = [
                self.mermaid_cli,
                "-i", str(input_file),
                "-o", str(output_path),
                "-f", format.value
            ]
            
            if config:
                # Create config file if needed
                config_file = output_path.with_suffix(".config.json")
                config_file.write_text(json.dumps(config.to_dict(), indent=2))
                cmd.extend(["-c", str(config_file)])
            
            # Execute rendering
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"Mermaid CLI failed: {result.stderr}"
                )
            
            return output_path
            
        finally:
            # Clean up temporary files
            if input_file.exists():
                input_file.unlink()
    
    def render_to_string(
        self,
        diagram: str,
        format: RenderFormat = RenderFormat.SVG
    ) -> str:
        """Render a diagram to a string.
        
        Args:
            diagram: Mermaid diagram definition
            format: Output format (SVG, PNG, PDF)
            
        Returns:
            Rendered diagram as string
            
        Raises:
            RuntimeError: If mermaid CLI is not available or rendering fails
        """
        if not self.check_cli_available():
            raise RuntimeError(
                f"Mermaid CLI ({self.mermaid_cli}) not found. "
                "Install with: npm install -g @mermaid-js/mermaid-cli"
            )
        
        # Create temporary input file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            input_file = Path(f.name)
            input_file.write_text(diagram)
        
        try:
            # Create temporary output file
            output_file = input_file.with_suffix(f".{format.value}")
            
            # Build command
            cmd = [
                self.mermaid_cli,
                "-i", str(input_file),
                "-o", str(output_file),
                "-f", format.value
            ]
            
            # Execute rendering
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"Mermaid CLI failed: {result.stderr}"
                )
            
            return output_file.read_text()
            
        finally:
            # Clean up temporary files
            if input_file.exists():
                input_file.unlink()
            if output_file.exists() and format != RenderFormat.SVG:
                output_file.unlink()





