"""
MIA Hardware MCP Server

Exposes MIA hardware control as MCP tools that AI agents can call.
Uses TinyMCP framework for MCP protocol implementation.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import zmq
import zmq.asyncio

# Import TinyMCP (will be available via Conan dependency)
try:
    from tinymcp import MCPServer
except ImportError:
    # Fallback for development
    class MCPServer:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}

        def tool(self, name: str):
            def decorator(func):
                self.tools[name] = func
                return func
            return decorator

        async def serve(self):
            # Placeholder serve method
            print(f"MCP Server {self.name} started (TinyMCP not available)")

# Import ICD-generated types and tool implementations
from ..core.messaging.messages import (
    GPIOCommand, GPIOResponse, GPIOMode,
    OBDQuery, OBDResponse, OBDService,
    RFCaptureStart, RFReplay, RFModulation,
    MessageEnvelope
)
from .tools.hardware_tools import HardwareTools


class MIAHardwareMCPServer:
    """MCP server exposing MIA hardware control tools"""

    def __init__(self,
                 gpio_worker_address: str = "tcp://127.0.0.1:5555",
                 obd_worker_address: str = "tcp://127.0.0.1:5556",
                 rf_worker_address: str = "tcp://127.0.0.1:5557"):
        self.gpio_address = gpio_worker_address
        self.obd_address = obd_worker_address
        self.rf_address = rf_worker_address

        # Hardware tools instance
        self.tools = HardwareTools(gpio_worker_address, obd_worker_address, rf_worker_address)

        # MCP server
        self.mcp_server = MCPServer("mia-hardware")
        self._setup_tools()

        self.logger = logging.getLogger(__name__)

    def _setup_tools(self):
        """Register MCP tools"""

        @self.mcp_server.tool("set_gpio_pin")
        async def set_gpio_pin(pin: int, state: bool, mode: str = "OUTPUT") -> Dict[str, Any]:
            """Control GPIO pins on Raspberry Pi

            Args:
                pin: GPIO pin number (0-40)
                state: Desired state (true = HIGH, false = LOW)
                mode: Pin mode - "INPUT", "OUTPUT", "INPUT_PULLUP", or "INPUT_PULLDOWN"

            Returns:
                Operation result with telemetry
            """
            return await self.tools.set_gpio_pin(pin, state, mode)

        @self.mcp_server.tool("query_obd")
        async def query_obd(pid: str, service: str = "CURRENT_DATA") -> Dict[str, Any]:
            """Query OBD-II diagnostic data from vehicle

            Args:
                pid: Parameter ID as hex string (e.g., "0x01", "0x0C")
                service: OBD service - "CURRENT_DATA", "FREEZE_FRAME", etc.

            Returns:
                OBD-II response with decoded data
            """
            return await self.tools.query_obd(pid, service)

        @self.mcp_server.tool("start_rf_capture")
        async def start_rf_capture(frequency: int = 433920000,
                                 modulation: str = "FSK",
                                 duration_ms: int = 10000) -> Dict[str, Any]:
            """Start RF signal capture on NucleusESP32

            Args:
                frequency: Frequency in Hz (default: 433.92MHz)
                modulation: Modulation type - "ASK", "FSK", "OOK", etc.
                duration_ms: Capture duration in milliseconds

            Returns:
                Capture operation result
            """
            return await self.tools.start_rf_capture(frequency, modulation, duration_ms)

        @self.mcp_server.tool("replay_rf_signal")
        async def replay_rf_signal(frame_data: list,
                                 frequency: int = 433920000,
                                 modulation: str = "FSK") -> Dict[str, Any]:
            """Replay captured RF signal on NucleusESP32

            Args:
                frame_data: RF frame data as byte array
                frequency: Frequency in Hz
                modulation: Modulation type

            Returns:
                Replay operation result
            """
            return await self.tools.replay_rf_signal(frame_data, frequency, modulation)

    async def start(self):
        """Start the MCP server"""
        self.logger.info("Starting MIA Hardware MCP Server")
        try:
            await self.mcp_server.serve()
        except Exception as e:
            self.logger.error(f"MCP server error: {e}")
        finally:
            await self.tools.close()

    async def stop(self):
        """Stop the MCP server"""
        await self.tools.close()
        self.logger.info("MIA Hardware MCP Server stopped")


async def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    server = MIAHardwareMCPServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())