"""
MIA MCP Transport Layer

Provides multiple transport mechanisms for MCP (Model Context Protocol) communication:
- Stdio: Direct process communication for AI agents
- HTTP/SSE: Web-based communication for browser clients
- Telegram: Bot-based communication via Telegram

This abstraction layer allows MCP servers to communicate over different protocols
while maintaining the same tool interface.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, Awaitable, Union
from abc import ABC, abstractmethod
import sys
import os


class MCPTransport(ABC):
    """Abstract base class for MCP transports."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.connected = False

    @abstractmethod
    async def start(self) -> None:
        """Start the transport."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport."""
        pass

    @abstractmethod
    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send a response to the client."""
        pass

    @abstractmethod
    async def receive_request(self) -> Optional[Dict[str, Any]]:
        """Receive a request from the client."""
        pass


class StdioTransport(MCPTransport):
    """Stdio-based MCP transport for direct AI agent communication."""

    def __init__(self):
        super().__init__("stdio")
        self.input_stream = sys.stdin
        self.output_stream = sys.stdout

    async def start(self) -> None:
        """Start stdio transport."""
        self.connected = True
        self.logger.info("Stdio transport started")

    async def stop(self) -> None:
        """Stop stdio transport."""
        self.connected = False
        self.logger.info("Stdio transport stopped")

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response via stdout."""
        try:
            response_json = json.dumps(response, separators=(',', ':'))
            print(response_json, flush=True)
        except Exception as e:
            self.logger.error(f"Failed to send response: {e}")

    async def receive_request(self) -> Optional[Dict[str, Any]]:
        """Receive request from stdin."""
        try:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, self.input_stream.readline)
            if not line:
                return None  # EOF

            line = line.strip()
            if not line:
                return None

            return json.loads(line)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON received: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading from stdin: {e}")
            return None


class HTTPTransport(MCPTransport):
    """HTTP/SSE-based MCP transport for web clients."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        super().__init__("http")
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()  # Connected SSE clients

    async def start(self) -> None:
        """Start HTTP server."""
        try:
            # Try to import aiohttp
            try:
                import aiohttp
                from aiohttp import web
            except ImportError:
                self.logger.warning("aiohttp not available, HTTP transport disabled")
                return

            app = web.Application()

            async def handle_mcp_request(request):
                """Handle MCP tool calls via HTTP POST."""
                try:
                    data = await request.json()
                    # Process request and return response
                    # This would integrate with the MCP server
                    return web.json_response({"status": "received", "request": data})
                except Exception as e:
                    return web.json_response({"error": str(e)}, status=400)

            async def handle_sse(request):
                """Handle Server-Sent Events for real-time communication."""
                response = web.StreamResponse()
                response.headers['Content-Type'] = 'text/event-stream'
                response.headers['Cache-Control'] = 'no-cache'
                response.headers['Connection'] = 'keep-alive'
                await response.prepare(request)

                # Add client to connected clients
                self.clients.add(response)

                try:
                    while True:
                        # Keep connection alive
                        await asyncio.sleep(30)
                        await response.write(b': keepalive\n\n')
                except Exception:
                    pass
                finally:
                    self.clients.discard(response)

                return response

            app.router.add_post('/mcp', handle_mcp_request)
            app.router.add_get('/sse', handle_sse)

            self.server = await asyncio.get_event_loop().create_server(
                app._make_handler(), self.host, self.port
            )

            self.connected = True
            self.logger.info(f"HTTP transport started on {self.host}:{self.port}")

        except Exception as e:
            self.logger.error(f"Failed to start HTTP transport: {e}")

    async def stop(self) -> None:
        """Stop HTTP server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        # Close all SSE connections
        for client in self.clients.copy():
            try:
                await client.write(b'event: close\ndata: {}\n\n')
            except Exception:
                pass
        self.clients.clear()

        self.connected = False
        self.logger.info("HTTP transport stopped")

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response to all connected SSE clients."""
        if not self.clients:
            return

        try:
            event_data = json.dumps(response, separators=(',', ':'))
            message = f'event: mcp\ndata: {event_data}\n\n'

            # Send to all connected clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.write(message.encode('utf-8'))
                except Exception:
                    disconnected.add(client)

            # Remove disconnected clients
            self.clients -= disconnected

        except Exception as e:
            self.logger.error(f"Failed to send SSE response: {e}")

    async def receive_request(self) -> Optional[Dict[str, Any]]:
        """HTTP transport doesn't actively receive requests in this implementation."""
        # Requests are handled via the HTTP endpoints
        return None


class TelegramTransport(MCPTransport):
    """Telegram bot-based MCP transport."""

    def __init__(self, bot_token: str, chat_id: str):
        super().__init__("telegram")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.update_offset = 0

    async def start(self) -> None:
        """Start Telegram transport."""
        try:
            # Try to import aiohttp for HTTP requests
            try:
                import aiohttp
            except ImportError:
                self.logger.warning("aiohttp not available, Telegram transport disabled")
                return

            # Test bot connection
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status != 200:
                        raise Exception(f"Telegram API error: {response.status}")

            self.connected = True
            self.logger.info("Telegram transport started")

        except Exception as e:
            self.logger.error(f"Failed to start Telegram transport: {e}")

    async def stop(self) -> None:
        """Stop Telegram transport."""
        self.connected = False
        self.logger.info("Telegram transport stopped")

    async def send_response(self, response: Dict[str, Any]) -> None:
        """Send response via Telegram message."""
        try:
            import aiohttp

            message = f"🤖 **MIA MCP Response**\n\n```\n{json.dumps(response, indent=2)}\n```"

            async with aiohttp.ClientSession() as session:
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                async with session.post(f"{self.base_url}/sendMessage", json=data) as resp:
                    if resp.status != 200:
                        self.logger.error(f"Failed to send Telegram message: {resp.status}")

        except ImportError:
            self.logger.warning("aiohttp not available for Telegram transport")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram response: {e}")

    async def receive_request(self) -> Optional[Dict[str, Any]]:
        """Receive requests from Telegram messages."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {'offset': self.update_offset, 'timeout': 30}
                async with session.get(f"{self.base_url}/getUpdates", params=params) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()
                    updates = data.get('result', [])

                    for update in updates:
                        self.update_offset = max(self.update_offset, update['update_id'] + 1)

                        if 'message' in update and 'text' in update['message']:
                            text = update['message']['text']
                            chat_id = update['message']['chat']['id']

                            # Only process messages from our configured chat
                            if str(chat_id) != str(self.chat_id):
                                continue

                            # Try to parse as JSON MCP request
                            try:
                                request = json.loads(text)
                                return request
                            except json.JSONDecodeError:
                                # Not a JSON request, skip
                                continue

        except ImportError:
            self.logger.warning("aiohttp not available for Telegram transport")
        except Exception as e:
            self.logger.error(f"Error receiving Telegram updates: {e}")

        return None


class MCPTransportManager:
    """Manages multiple MCP transports."""

    def __init__(self):
        self.transports: Dict[str, MCPTransport] = {}
        self.logger = logging.getLogger(__name__)

    def add_transport(self, transport: MCPTransport):
        """Add a transport."""
        self.transports[transport.name] = transport
        self.logger.info(f"Added transport: {transport.name}")

    def get_transport(self, name: str) -> Optional[MCPTransport]:
        """Get a transport by name."""
        return self.transports.get(name)

    async def start_all(self):
        """Start all transports."""
        tasks = []
        for name, transport in self.transports.items():
            tasks.append(transport.start())

        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info(f"Started {len(self.transports)} transports")

    async def stop_all(self):
        """Stop all transports."""
        tasks = []
        for name, transport in self.transports.items():
            tasks.append(transport.stop())

        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info("Stopped all transports")

    def get_available_transports(self) -> list:
        """Get list of available transport names."""
        return list(self.transports.keys())

    def get_transport_status(self) -> Dict[str, bool]:
        """Get status of all transports."""
        return {name: transport.connected for name, transport in self.transports.items()}


def create_transport_manager(config: Dict[str, Any]) -> MCPTransportManager:
    """Create and configure transport manager from configuration."""
    manager = MCPTransportManager()

    # Add stdio transport (always available)
    manager.add_transport(StdioTransport())

    # Add HTTP transport if configured
    http_config = config.get('http', {})
    if http_config:
        host = http_config.get('host', '127.0.0.1')
        port = http_config.get('port', 8080)
        manager.add_transport(HTTPTransport(host=host, port=port))

    # Add Telegram transport if configured
    telegram_config = config.get('telegram', {})
    if telegram_config and 'bot_token' in telegram_config and 'chat_id' in telegram_config:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or telegram_config['bot_token']
        chat_id = os.getenv('TELEGRAM_CHAT_ID') or telegram_config['chat_id']
        manager.add_transport(TelegramTransport(bot_token=bot_token, chat_id=chat_id))

    return manager