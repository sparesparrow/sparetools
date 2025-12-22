"""
RF Hardware Worker

ZeroMQ-based RF signal capture and replay worker for NucleusESP32.
Interfaces with NucleusESP32 via serial/MQTT for RF operations.
"""

import asyncio
import logging
import zmq
import zmq.asyncio
from typing import Optional, Dict, Any, List
import time
import json
import serial
import paho.mqtt.client as mqtt

# Import ICD-generated types
from ..core.messaging.messages import (
    RFCaptureStart, RFReplay, RFModulation,
    MessageEnvelope
)


class SerialBridge:
    """Serial communication bridge to NucleusESP32"""

    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """Connect to NucleusESP32 via serial"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            await asyncio.sleep(0.1)  # Allow connection to stabilize

            # Test connection
            await self.send({"command": "ping"})
            response = await self.receive()
            if response and response.get("status") == "ok":
                self.logger.info(f"Connected to NucleusESP32 on {self.port}")
                return True
            else:
                self.logger.error("NucleusESP32 ping failed")
                return False

        except Exception as e:
            self.logger.error(f"Serial connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from NucleusESP32"""
        if self.serial:
            self.serial.close()
            self.serial = None
            self.logger.info("Disconnected from NucleusESP32")

    async def send(self, data: Dict[str, Any]) -> bool:
        """Send JSON command to NucleusESP32"""
        if not self.serial:
            return False

        try:
            json_str = json.dumps(data) + "\n"
            self.serial.write(json_str.encode('utf-8'))
            self.serial.flush()
            return True
        except Exception as e:
            self.logger.error(f"Serial send failed: {e}")
            return False

    async def receive(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Receive JSON response from NucleusESP32"""
        if not self.serial:
            return None

        try:
            # Non-blocking read with timeout
            start_time = time.time()
            buffer = ""

            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    char = self.serial.read().decode('utf-8')
                    buffer += char

                    if char == '\n':
                        # Complete line received
                        try:
                            return json.loads(buffer.strip())
                        except json.JSONDecodeError:
                            # Invalid JSON, continue reading
                            buffer = ""
                            continue

                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

            return None  # Timeout

        except Exception as e:
            self.logger.error(f"Serial receive failed: {e}")
            return None


class MQTTBridge:
    """MQTT communication bridge to NucleusESP32"""

    def __init__(self, broker: str = "localhost", port: int = 1883,
                 client_id: str = "mia-rf-worker"):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.response_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            # Connect in background
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()

            # Wait for connection
            await asyncio.sleep(0.5)

            if self.connected:
                self.logger.info(f"Connected to MQTT broker {self.broker}:{self.port}")
                return True
            else:
                self.logger.error("MQTT connection failed")
                return False

        except Exception as e:
            self.logger.error(f"MQTT connection failed: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            self.connected = True
            client.subscribe("nucleus/rf/response")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            asyncio.create_task(self.response_queue.put(payload))
        except Exception as e:
            self.logger.error(f"MQTT message error: {e}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        self.connected = False

    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
            self.connected = False
            self.logger.info("Disconnected from MQTT broker")

    async def send(self, data: Dict[str, Any]) -> bool:
        """Send command via MQTT"""
        if not self.client or not self.connected:
            return False

        try:
            self.client.publish("nucleus/rf/command", json.dumps(data))
            return True
        except Exception as e:
            self.logger.error(f"MQTT send failed: {e}")
            return False

    async def receive(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Receive response via MQTT"""
        try:
            return await asyncio.wait_for(
                self.response_queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"MQTT receive failed: {e}")
            return None


class RFZMQWorker:
    """ZeroMQ-based RF capture/replay worker"""

    def __init__(self,
                 zmq_address: str = "tcp://127.0.0.1:5557",
                 nucleus_interface: str = "serial",  # "serial" or "mqtt"
                 serial_port: str = "/dev/ttyACM0",
                 mqtt_broker: str = "localhost"):
        self.zmq_address = zmq_address
        self.nucleus_interface = nucleus_interface
        self.serial_port = serial_port
        self.mqtt_broker = mqtt_broker

        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.bridge: Optional[SerialBridge | MQTTBridge] = None

        self.logger = logging.getLogger(__name__)

        # RF operation state
        self.capture_active = False
        self.replay_active = False
        self.captured_frames: List[Dict[str, Any]] = []

    async def start(self):
        """Start the RF worker"""
        # Initialize ZeroMQ
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.zmq_address)

        # Initialize NucleusESP32 bridge
        if self.nucleus_interface == "serial":
            self.bridge = SerialBridge(self.serial_port)
        elif self.nucleus_interface == "mqtt":
            self.bridge = MQTTBridge(self.mqtt_broker)
        else:
            raise ValueError(f"Unknown interface: {self.nucleus_interface}")

        # Connect to NucleusESP32
        if not await self.bridge.connect():
            self.logger.error("Failed to connect to NucleusESP32")
            return

        self.logger.info(f"RF worker started on {self.zmq_address}")

        try:
            await self._run()
        except Exception as e:
            self.logger.error(f"RF worker error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the RF worker"""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        if self.bridge:
            await self.bridge.disconnect()
        self.logger.info("RF worker stopped")

    async def _run(self):
        """Main worker loop"""
        while True:
            try:
                # Receive message
                message_data = await self.socket.recv_json()
                self.logger.debug(f"Received message: {message_data}")

                # Parse envelope
                envelope = MessageEnvelope(**message_data)

                # Handle message based on type
                response = await self._handle_message(envelope)

                # Send response
                response_data = {
                    "message_type": response.__class__.__name__,
                    "message_id": envelope.message_id,
                    "source": "rf-worker",
                    "payload": response.__dict__
                }

                await self.socket.send_json(response_data)

            except Exception as e:
                self.logger.error(f"Error handling message: {e}")
                # Send error response
                await self.socket.send_json({
                    "message_type": "Error",
                    "message_id": 0,
                    "source": "rf-worker",
                    "payload": {"error": str(e)}
                })

    async def _handle_message(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle incoming message"""
        if envelope.message_type == "RFCaptureStart":
            cmd = RFCaptureStart(**envelope.payload)
            return await self._handle_capture_start(cmd)
        elif envelope.message_type == "RFReplay":
            cmd = RFReplay(**envelope.payload)
            return await self._handle_replay(cmd)
        else:
            raise ValueError(f"Unknown message type: {envelope.message_type}")

    async def _handle_capture_start(self, cmd: RFCaptureStart) -> Dict[str, Any]:
        """Handle RF capture start command"""
        try:
            self.logger.info(f"Starting RF capture: freq={cmd.frequency}Hz, mod={cmd.modulation}")

            # Prepare NucleusESP32 command
            nucleus_cmd = {
                "action": "start_capture",
                "frequency": cmd.frequency,
                "modulation": cmd.modulation.name.lower(),
                "sample_rate": cmd.sample_rate,
                "gain": cmd.gain,
                "bandwidth": cmd.bandwidth,
                "squelch": cmd.squelch,
                "duration_ms": cmd.duration_ms,
                "max_frames": cmd.max_frames
            }

            # Send command to NucleusESP32
            success = await self.bridge.send(nucleus_cmd)
            if not success:
                return {
                    "success": False,
                    "error_message": "Failed to send capture command",
                    "timestamp": int(time.time() * 1_000_000)
                }

            # Wait for response
            response = await self.bridge.receive(timeout=2.0)
            if response and response.get("status") == "capture_started":
                self.capture_active = True
                return {
                    "success": True,
                    "message": "RF capture started",
                    "config": nucleus_cmd,
                    "timestamp": int(time.time() * 1_000_000)
                }
            else:
                return {
                    "success": False,
                    "error_message": "NucleusESP32 capture failed",
                    "timestamp": int(time.time() * 1_000_000)
                }

        except Exception as e:
            self.logger.error(f"RF capture failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "timestamp": int(time.time() * 1_000_000)
            }

    async def _handle_replay(self, cmd: RFReplay) -> Dict[str, Any]:
        """Handle RF replay command"""
        try:
            self.logger.info(f"Starting RF replay: freq={cmd.frequency}Hz, frames={len(cmd.frame_data)}")

            # Prepare NucleusESP32 command
            nucleus_cmd = {
                "action": "replay_signal",
                "frequency": cmd.frequency,
                "modulation": cmd.modulation.name.lower(),
                "frame_data": cmd.frame_data,
                "repeat_count": cmd.repeat_count,
                "tx_power": cmd.tx_power
            }

            # Send command to NucleusESP32
            success = await self.bridge.send(nucleus_cmd)
            if not success:
                return {
                    "success": False,
                    "error_message": "Failed to send replay command",
                    "timestamp": int(time.time() * 1_000_000)
                }

            # Wait for response
            response = await self.bridge.receive(timeout=5.0)
            if response and response.get("status") == "replay_complete":
                frames_sent = response.get("frames_sent", 0)
                return {
                    "success": True,
                    "message": f"RF replay completed: {frames_sent} frames sent",
                    "frames_sent": frames_sent,
                    "timestamp": int(time.time() * 1_000_000)
                }
            else:
                return {
                    "success": False,
                    "error_message": "NucleusESP32 replay failed",
                    "timestamp": int(time.time() * 1_000_000)
                }

        except Exception as e:
            self.logger.error(f"RF replay failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "timestamp": int(time.time() * 1_000_000)
            }

    def get_capture_status(self) -> Dict[str, Any]:
        """Get current capture status"""
        return {
            "active": self.capture_active,
            "frames_captured": len(self.captured_frames)
        }

    def get_replay_status(self) -> Dict[str, Any]:
        """Get current replay status"""
        return {
            "active": self.replay_active
        }


async def main():
    """Main entry point for RF worker"""
    logging.basicConfig(level=logging.INFO)

    # Try serial first, fallback to MQTT
    worker = RFZMQWorker(nucleus_interface="serial")
    try:
        await worker.start()
    except Exception as e:
        print(f"Serial interface failed: {e}, trying MQTT...")
        worker = RFZMQWorker(nucleus_interface="mqtt")
        await worker.start()


if __name__ == "__main__":
    asyncio.run(main())