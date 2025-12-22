"""
MIA Hardware MCP Tools

Tool implementations for hardware control via MCP protocol.
Separated from server for better organization and testing.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import zmq
import zmq.asyncio

from ...core.messaging.messages import (
    GPIOCommand, GPIOResponse, GPIOMode,
    OBDQuery, OBDResponse, OBDService,
    RFCaptureStart, RFReplay, RFModulation,
    MessageEnvelope
)


class HardwareTools:
    """MCP tool implementations for hardware control"""

    def __init__(self,
                 gpio_worker_address: str = "tcp://127.0.0.1:5555",
                 obd_worker_address: str = "tcp://127.0.0.1:5556",
                 rf_worker_address: str = "tcp://127.0.0.1:5557"):
        self.gpio_address = gpio_worker_address
        self.obd_address = obd_worker_address
        self.rf_address = rf_worker_address
        self.zmq_context = zmq.asyncio.Context()
        self.logger = logging.getLogger(__name__)

    async def set_gpio_pin(self, pin: int, state: bool, mode: str = "OUTPUT") -> Dict[str, Any]:
        """Control GPIO pins on Raspberry Pi

        Args:
            pin: GPIO pin number (0-40)
            state: Desired state (true = HIGH, false = LOW)
            mode: Pin mode - "INPUT", "OUTPUT", "INPUT_PULLUP", or "INPUT_PULLDOWN"

        Returns:
            Operation result with telemetry
        """
        try:
            # Convert mode string to enum
            mode_enum = GPIOMode[mode.upper()]

            # Create command
            cmd = GPIOCommand(pin=pin, state=state, mode=mode_enum)

            # Send to GPIO worker
            response = await self._zmq_request(self.gpio_address, cmd, GPIOResponse)

            return {
                "success": response.success,
                "pin": response.pin,
                "state": response.state,
                "error_message": response.error_message if not response.success else "",
                "timestamp": response.timestamp
            }

        except Exception as e:
            self.logger.error(f"GPIO operation failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "pin": pin,
                "state": state
            }

    async def query_obd(self, pid: str, service: str = "CURRENT_DATA") -> Dict[str, Any]:
        """Query OBD-II diagnostic data from vehicle

        Args:
            pid: Parameter ID as hex string (e.g., "0x01", "0x0C")
            service: OBD service - "CURRENT_DATA", "FREEZE_FRAME", etc.

        Returns:
            OBD-II response with decoded data
        """
        try:
            # Convert service string to enum
            service_enum = OBDService[service.upper()]
            pid_int = int(pid, 16)

            # Create query
            query = OBDQuery(service=service_enum, pid=pid_int)

            # Send to OBD worker
            response = await self._zmq_request(self.obd_address, query, OBDResponse)

            return {
                "success": response.success,
                "service": response.service.name,
                "pid": f"0x{response.pid:02X}",
                "data": [f"0x{b:02X}" for b in response.data],
                "decoded_value": response.decoded_value,
                "unit": response.unit,
                "error_code": response.error_code,
                "timestamp": response.timestamp
            }

        except Exception as e:
            self.logger.error(f"OBD query failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "pid": pid,
                "service": service
            }

    async def start_rf_capture(self, frequency: int = 433920000,
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
        try:
            # Convert modulation string to enum
            modulation_enum = RFModulation[modulation.upper()]

            # Create capture command
            cmd = RFCaptureStart(
                frequency=frequency,
                modulation=modulation_enum,
                duration_ms=duration_ms
            )

            # Send to RF worker (when implemented)
            # For now, return placeholder response
            return {
                "success": True,
                "message": f"RF capture started at {frequency}Hz with {modulation} modulation",
                "duration_ms": duration_ms,
                "status": "Capture initiated - RF worker not yet implemented"
            }

        except Exception as e:
            self.logger.error(f"RF capture failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }

    async def replay_rf_signal(self, frame_data: list,
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
        try:
            # Convert modulation string to enum
            modulation_enum = RFModulation[modulation.upper()]

            # Create replay command
            cmd = RFReplay(
                frame_data=frame_data,
                frequency=frequency,
                modulation=modulation_enum
            )

            # Send to RF worker (when implemented)
            # For now, return placeholder response
            return {
                "success": True,
                "message": f"RF replay initiated at {frequency}Hz with {len(frame_data)} bytes",
                "status": "Replay initiated - RF worker not yet implemented"
            }

        except Exception as e:
            self.logger.error(f"RF replay failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }

    async def _zmq_request(self, address: str, command: Any, response_type: Any) -> Any:
        """Send request to ZeroMQ worker and get response"""
        socket = None
        try:
            socket = self.zmq_context.socket(zmq.REQ)
            socket.connect(address)

            # Create envelope
            envelope = MessageEnvelope(
                message_type=command.__class__.__name__,
                source="mcp-tools",
                payload=command.__dict__
            )

            # Send request
            message_data = {
                "message_type": envelope.message_type,
                "message_id": envelope.message_id,
                "source": envelope.source,
                "payload": envelope.payload
            }

            await socket.send_json(message_data)

            # Receive response
            response_data = await socket.recv_json()
            response_envelope = MessageEnvelope(**response_data)

            # Parse response
            if response_envelope.message_type == response_type.__name__:
                return response_type(**response_envelope.payload)
            else:
                raise ValueError(f"Unexpected response type: {response_envelope.message_type}")

        finally:
            if socket:
                socket.close()

    async def close(self):
        """Close ZeroMQ context"""
        self.zmq_context.term()