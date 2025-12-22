"""
OBD-II Service Worker

Handles OBD-II diagnostic communication using ZeroMQ messaging.
This will be updated to use ICD-generated OBD types in Phase 1.2.
"""

import asyncio
import logging
import zmq
import zmq.asyncio
from typing import Optional, Dict, Any, List
import time
import random

# Import ICD-generated types
from ..core.messaging.messages import OBDQuery, OBDResponse, MessageEnvelope, OBDService


class OBDZMQWorker:
    """ZeroMQ-based OBD-II diagnostic worker"""

    def __init__(self, zmq_address: str = "tcp://127.0.0.1:5556", serial_port: str = "/dev/ttyUSB0"):
        self.zmq_address = zmq_address
        self.serial_port = serial_port
        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.logger = logging.getLogger(__name__)

        # OBD-II PID decoders (simplified)
        self.pid_decoders = {
            0x01: self._decode_engine_rpm,
            0x04: self._decode_engine_load,
            0x05: self._decode_coolant_temp,
            0x0C: self._decode_vehicle_speed,
            0x0D: self._decode_intake_temp,
        }

    async def start(self):
        """Start the OBD worker"""
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.zmq_address)

        self.logger.info(f"OBD worker started on {self.zmq_address}")

        try:
            await self._run()
        except Exception as e:
            self.logger.error(f"OBD worker error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the OBD worker"""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.logger.info("OBD worker stopped")

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
                    "source": "obd-worker",
                    "payload": response.__dict__
                }

                await self.socket.send_json(response_data)

            except Exception as e:
                self.logger.error(f"Error handling message: {e}")
                # Send error response
                error_response = OBDResponse(
                    service=OBDService.CURRENT_DATA,
                    pid=0x00,
                    success=False,
                    error_code=str(e)
                )
                await self.socket.send_json({
                    "message_type": "OBDResponse",
                    "message_id": 0,
                    "source": "obd-worker",
                    "payload": error_response.__dict__
                })

    async def _handle_message(self, envelope: MessageEnvelope) -> OBDResponse:
        """Handle incoming message"""
        if envelope.message_type == "OBDQuery":
            query = OBDQuery(**envelope.payload)
            return await self._handle_obd_query(query)
        else:
            raise ValueError(f"Unknown message type: {envelope.message_type}")

    async def _handle_obd_query(self, query: OBDQuery) -> OBDResponse:
        """Handle OBD-II query"""
        try:
            self.logger.info(f"OBD query: service=0x{query.service:02X}, pid=0x{query.pid:02X}")

            # Simulate OBD-II communication delay
            await asyncio.sleep(0.1)

            # Generate simulated response data
            if query.pid in self.pid_decoders:
                raw_data, decoded_value, unit = self.pid_decoders[query.pid]()
            else:
                # Unknown PID - return dummy data
                raw_data = [0x00, 0x00]
                decoded_value = 0.0
                unit = ""

            return OBDResponse(
                service=query.service,
                pid=query.pid,
                success=True,
                data=raw_data,
                decoded_value=decoded_value,
                unit=unit,
                timestamp=int(time.time() * 1_000_000)
            )

        except Exception as e:
            self.logger.error(f"OBD query failed: {e}")
            return OBDResponse(
                service=query.service,
                pid=query.pid,
                success=False,
                error_code=str(e),
                timestamp=int(time.time() * 1_000_000)
            )

    def _decode_engine_rpm(self) -> tuple:
        """Decode engine RPM (PID 0x0C)"""
        # Simulate RPM between 800-4000
        rpm = random.randint(800, 4000)
        # OBD-II formula: RPM = ((A*256)+B)/4
        a = rpm // 4 // 256
        b = (rpm // 4) % 256
        return [a, b], float(rpm), "rpm"

    def _decode_engine_load(self) -> tuple:
        """Decode engine load (PID 0x04)"""
        # Simulate load percentage 0-100
        load = random.randint(0, 100)
        # OBD-II formula: Load = A/2.55
        a = int(load * 2.55)
        return [a], float(load), "%"

    def _decode_coolant_temp(self) -> tuple:
        """Decode coolant temperature (PID 0x05)"""
        # Simulate temperature 60-110°C
        temp = random.randint(60, 110)
        # OBD-II formula: Temp = A-40
        a = temp + 40
        return [a], float(temp), "celsius"

    def _decode_vehicle_speed(self) -> tuple:
        """Decode vehicle speed (PID 0x0D)"""
        # Simulate speed 0-120 km/h
        speed = random.randint(0, 120)
        # OBD-II formula: Speed = A
        return [speed], float(speed), "km/h"

    def _decode_intake_temp(self) -> tuple:
        """Decode intake air temperature (PID 0x0F)"""
        # Simulate temperature -40 to 100°C
        temp = random.randint(-40, 100)
        # OBD-II formula: Temp = A-40
        a = temp + 40
        return [a], float(temp), "celsius"


async def main():
    """Main entry point for OBD worker"""
    logging.basicConfig(level=logging.INFO)
    worker = OBDZMQWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())