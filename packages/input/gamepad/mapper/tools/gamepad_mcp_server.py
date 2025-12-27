#!/usr/bin/env python3
"""
Gamepad Mapper MCP Server
Provides MCP (Model Context Protocol) interface for gamepad control
"""

import json
import sys
import subprocess
import os
from typing import Any, Dict, List
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GamepadMCPServer:
    def __init__(self):
        self.gamepad_process = None
        self.config_file = None

    def initialize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server"""
        logger.info("Initializing Gamepad MCP Server")

        # Find gamepad mapper binary
        self.gamepad_binary = self._find_gamepad_binary()

        # Load configuration
        self.config_file = config.get("config_file", "config/default_mappings.json")

        return {
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "gamepad-mapper",
                "version": "1.0.0"
            }
        }

    def _find_gamepad_binary(self) -> str:
        """Find the gamepad mapper binary"""
        # Check common locations
        possible_paths = [
            "./gamepad_mapper_app",
            "/usr/local/bin/gamepad_mapper_app",
            "/usr/bin/gamepad_mapper_app",
            os.path.expanduser("~/bin/gamepad_mapper_app")
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # Try to find in PATH
        try:
            result = subprocess.run(["which", "gamepad_mapper_app"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        raise FileNotFoundError("Could not find gamepad_mapper_app binary")

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": "start_gamepad_mapper",
                "description": "Start the gamepad mapper service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "string",
                            "description": "Configuration file to use"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Port for MCP server",
                            "default": 8080
                        }
                    }
                }
            },
            {
                "name": "stop_gamepad_mapper",
                "description": "Stop the gamepad mapper service",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_gamepad_status",
                "description": "Get the current status of the gamepad mapper",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_mappings",
                "description": "List available gamepad mappings",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "load_mapping",
                "description": "Load a specific mapping configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mapping_file": {
                            "type": "string",
                            "description": "Path to the mapping file to load"
                        }
                    },
                    "required": ["mapping_file"]
                }
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        try:
            if name == "start_gamepad_mapper":
                return self._start_gamepad_mapper(arguments)
            elif name == "stop_gamepad_mapper":
                return self._stop_gamepad_mapper()
            elif name == "get_gamepad_status":
                return self._get_gamepad_status()
            elif name == "list_mappings":
                return self._list_mappings()
            elif name == "load_mapping":
                return self._load_mapping(arguments)
            else:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
                }
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: {str(e)}"}]
            }

    def _start_gamepad_mapper(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start the gamepad mapper"""
        if self.gamepad_process and self.gamepad_process.poll() is None:
            return {
                "content": [{"type": "text", "text": "Gamepad mapper is already running"}]
            }

        config = args.get("config", self.config_file)
        port = args.get("port", 8080)

        cmd = [self.gamepad_binary, "--config", config, "--port", str(port)]

        try:
            self.gamepad_process = subprocess.Popen(cmd)
            return {
                "content": [{"type": "text", "text": f"Started gamepad mapper on port {port}"}]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Failed to start gamepad mapper: {e}"}]
            }

    def _stop_gamepad_mapper(self) -> Dict[str, Any]:
        """Stop the gamepad mapper"""
        if not self.gamepad_process or self.gamepad_process.poll() is not None:
            return {
                "content": [{"type": "text", "text": "Gamepad mapper is not running"}]
            }

        try:
            self.gamepad_process.terminate()
            self.gamepad_process.wait(timeout=5)
            return {
                "content": [{"type": "text", "text": "Stopped gamepad mapper"}]
            }
        except subprocess.TimeoutExpired:
            self.gamepad_process.kill()
            return {
                "content": [{"type": "text", "text": "Force stopped gamepad mapper"}]
            }

    def _get_gamepad_status(self) -> Dict[str, Any]:
        """Get gamepad mapper status"""
        if self.gamepad_process and self.gamepad_process.poll() is None:
            status = "running"
            pid = self.gamepad_process.pid
        else:
            status = "stopped"
            pid = None

        return {
            "content": [{"type": "text", "text": json.dumps({
                "status": status,
                "pid": pid,
                "config_file": self.config_file
            }, indent=2)}]
        }

    def _list_mappings(self) -> Dict[str, Any]:
        """List available mappings"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            return {
                "content": [{"type": "text", "text": "Config directory not found"}]
            }

        mappings = []
        for file in os.listdir(config_dir):
            if file.endswith(".json"):
                mappings.append(file)

        return {
            "content": [{"type": "text", "text": json.dumps(mappings, indent=2)}]
        }

    def _load_mapping(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Load a specific mapping"""
        mapping_file = args.get("mapping_file")
        if not mapping_file or not os.path.exists(mapping_file):
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Mapping file not found: {mapping_file}"}]
            }

        # Send signal to reload configuration (if supported)
        # This would need to be implemented in the gamepad mapper
        return {
            "content": [{"type": "text", "text": f"Requested to load mapping: {mapping_file}"}]
        }


def main():
    """Main MCP server loop"""
    server = GamepadMCPServer()

    # Read messages from stdin
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            logger.info(f"Received message: {message}")

            if message.get("method") == "initialize":
                result = server.initialize(message.get("params", {}))
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            elif message.get("method") == "tools/list":
                tools = server.list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {"tools": tools}
                }
            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                result = server.call_tool(params.get("name"), params.get("arguments", {}))
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            print(json.dumps(response), flush=True)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")


if __name__ == "__main__":
    main()