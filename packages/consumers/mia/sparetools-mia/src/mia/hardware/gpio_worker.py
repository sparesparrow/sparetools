"""
GPIO Hardware Worker

Controls GPIO pins on Raspberry Pi using ZeroMQ messaging.
This will be updated to use ICD-generated GPIO types in Phase 1.2.
"""

import asyncio
import logging
import zmq
import zmq.asyncio
from typing import Optional, Dict, Any
import time

# Import ICD-generated types
from ..core.messaging.messages import GPIOCommand, GPIOResponse, MessageEnvelope, GPIOMode


class GPIOZMQWorker:
    """ZeroMQ-based GPIO control worker"""

    def __init__(self, zmq_address: str = "tcp://127.0.0.1:5555"):
        self.zmq_address = zmq_address
        self.context: Optional[zmq.asyncio.Context] = None
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.logger = logging.getLogger(__name__)

        # GPIO state tracking
        self.pin_states: Dict[int, bool] = {}
        self.pin_modes: Dict[int, GPIOMode] = {}

    async def start(self):
        """Start the GPIO worker"""
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.zmq_address)

        self.logger.info(f"GPIO worker started on {self.zmq_address}")

        try:
            await self._run()
        except Exception as e:
            self.logger.error(f"GPIO worker error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the GPIO worker"""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.logger.info("GPIO worker stopped")

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
                    "source": "gpio-worker",
                    "payload": response.__dict__
                }

                await self.socket.send_json(response_data)

            except Exception as e:
                self.logger.error(f"Error handling message: {e}")
                # Send error response
                error_response = GPIOResponse(
                    pin=0,
                    state=False,
                    success=False,
                    error_message=str(e)
                )
                await self.socket.send_json({
                    "message_type": "GPIOResponse",
                    "message_id": 0,
                    "source": "gpio-worker",
                    "payload": error_response.__dict__
                })

    async def _handle_message(self, envelope: MessageEnvelope) -> GPIOResponse:
        """Handle incoming message"""
        if envelope.message_type == "GPIOCommand":
            cmd = GPIOCommand(**envelope.payload)
            return await self._handle_gpio_command(cmd)
        else:
            raise ValueError(f"Unknown message type: {envelope.message_type}")

    async def _handle_gpio_command(self, cmd: GPIOCommand) -> GPIOResponse:
        """Handle GPIO command"""
        try:
            # Simulate GPIO operations (replace with actual RPi.GPIO calls)
            self.logger.info(f"GPIO command: pin={cmd.pin}, state={cmd.state}, mode={cmd.mode}")

            # Update internal state
            self.pin_states[cmd.pin] = cmd.state
            self.pin_modes[cmd.pin] = cmd.mode

            # Simulate GPIO operation delay
            await asyncio.sleep(0.01)

            # Return success response
            return GPIOResponse(
                pin=cmd.pin,
                state=cmd.state,
                success=True,
                timestamp=int(time.time() * 1_000_000)
            )

        except Exception as e:
            self.logger.error(f"GPIO operation failed: {e}")
            return GPIOResponse(
                pin=cmd.pin,
                state=False,
                success=False,
                error_message=str(e),
                timestamp=int(time.time() * 1_000_000)
            )

    def get_pin_state(self, pin: int) -> Optional[bool]:
        """Get current state of a pin"""
        return self.pin_states.get(pin)

    def get_pin_mode(self, pin: int) -> Optional[GPIOMode]:
        """Get current mode of a pin"""
        return self.pin_modes.get(pin)


async def main():
    """Main entry point for GPIO worker"""
    logging.basicConfig(level=logging.INFO)
    worker = GPIOZMQWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())