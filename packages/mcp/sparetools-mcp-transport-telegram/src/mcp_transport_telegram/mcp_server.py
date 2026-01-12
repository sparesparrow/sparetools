"""Main MCP server implementation for Telegram transport."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, Resource, TextContent, ImageContent,
    EmbeddedResource, LoggingLevel, PromptMessage
)

from .config import Config
from .telegram_client import TelegramClientWrapper
from .message_handler import MessageHandler
from .telegram_polling import TelegramPoller
from .media_handler import MediaHandler
from .mcp_types import (
    MCPToolName, MCPResourceType, ChatInfo, MessageInfo,
    ContactInfo, MCPToolResult, MCPError, MCPErrorCode,
    create_tool_response, create_error_response, validate_tool_arguments
)
from .exceptions import MCPTelegramError, RateLimitError


logger = logging.getLogger(__name__)


class TelegramMCPServer:
    """MCP Server for Telegram transport integration."""

    def __init__(self, config: Config):
        """Initialize the MCP server.

        Args:
            config: Application configuration
        """
        self.config = config
        self.server = Server("mcp-transport-telegram")

        # Initialize Telegram components
        self.telegram_client = TelegramClientWrapper(config.telegram)
        self.message_handler = MessageHandler(
            self.telegram_client,
            max_age_seconds=config.max_message_age
        )
        self.media_handler = MediaHandler(
            self.telegram_client,
            max_file_size=config.max_file_size if hasattr(config, 'max_file_size') else 50 * 1024 * 1024
        )

        # Polling will be initialized when needed
        self.poller: Optional[TelegramPoller] = None

        # Setup MCP handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available MCP tools."""
            return [
                Tool(
                    name=MCPToolName.LIST_CHATS.value,
                    description="List all available Telegram chats/dialogs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of chats to return",
                                "default": 50
                            }
                        }
                    }
                ),
                Tool(
                    name=MCPToolName.GET_MESSAGES.value,
                    description="Get messages from a specific Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_id": {
                                "type": ["integer", "string"],
                                "description": "Chat ID or username to get messages from"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of messages to retrieve",
                                "default": 50
                            },
                            "unread_only": {
                                "type": "boolean",
                                "description": "Only return unread messages",
                                "default": False
                            }
                        },
                        "required": ["chat_id"]
                    }
                ),
                Tool(
                    name=MCPToolName.SEND_MESSAGE.value,
                    description="Send a message to a Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_id": {
                                "type": ["integer", "string"],
                                "description": "Chat ID or username to send message to"
                            },
                            "text": {
                                "type": "string",
                                "description": "Message text to send"
                            },
                            "reply_to_message_id": {
                                "type": "integer",
                                "description": "Message ID to reply to"
                            }
                        },
                        "required": ["chat_id", "text"]
                    }
                ),
                Tool(
                    name=MCPToolName.EDIT_MESSAGE.value,
                    description="Edit an existing message in a Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_id": {
                                "type": ["integer", "string"],
                                "description": "Chat ID or username"
                            },
                            "message_id": {
                                "type": "integer",
                                "description": "ID of the message to edit"
                            },
                            "text": {
                                "type": "string",
                                "description": "New message text"
                            }
                        },
                        "required": ["chat_id", "message_id", "text"]
                    }
                ),
                Tool(
                    name=MCPToolName.GET_MEDIA.value,
                    description="Download media from a Telegram message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_id": {
                                "type": ["integer", "string"],
                                "description": "Chat ID or username"
                            },
                            "message_id": {
                                "type": "integer",
                                "description": "ID of the message containing media"
                            }
                        },
                        "required": ["chat_id", "message_id"]
                    }
                ),
                Tool(
                    name=MCPToolName.GET_CONTACTS.value,
                    description="Get contact information from Telegram",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of contacts to return",
                                "default": 100
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == MCPToolName.LIST_CHATS.value:
                    return await self._handle_list_chats(arguments)
                elif name == MCPToolName.GET_MESSAGES.value:
                    return await self._handle_get_messages(arguments)
                elif name == MCPToolName.SEND_MESSAGE.value:
                    return await self._handle_send_message(arguments)
                elif name == MCPToolName.EDIT_MESSAGE.value:
                    return await self._handle_edit_message(arguments)
                elif name == MCPToolName.GET_MEDIA.value:
                    return await self._handle_get_media(arguments)
                elif name == MCPToolName.GET_CONTACTS.value:
                    return await self._handle_get_contacts(arguments)
                else:
                    return create_error_response(f"Unknown tool: {name}")

            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded: {e}")
                return create_error_response(f"Rate limit exceeded. Try again later.")
            except MCPTelegramError as e:
                logger.error(f"Tool error: {e}")
                return create_error_response(str(e))
            except Exception as e:
                logger.error(f"Unexpected error in tool {name}: {e}")
                return create_error_response(f"Internal error: {str(e)}")

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available MCP resources."""
            resources = []

            try:
                # Get chats as resources
                dialogs = await self.telegram_client.get_dialogs(limit=50)
                for dialog in dialogs:
                    if hasattr(dialog, 'id') and hasattr(dialog, 'title'):
                        chat_info = ChatInfo(
                            id=dialog.id,
                            title=getattr(dialog, 'title', None),
                            username=getattr(dialog, 'username', None),
                            chat_type=type(dialog).__name__.lower(),
                            participant_count=getattr(dialog, 'participants_count', None),
                            description=None
                        )
                        resources.append(self._chat_to_resource(chat_info))

            except Exception as e:
                logger.error(f"Error listing resources: {e}")

            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content."""
            try:
                # Parse URI to determine resource type
                if uri.startswith("telegram://chat/"):
                    chat_id = int(uri.split("/")[-1])
                    return await self._read_chat_resource(chat_id)
                elif uri.startswith("telegram://message/"):
                    parts = uri.split("/")
                    chat_id = int(parts[-2])
                    message_id = int(parts[-1])
                    return await self._read_message_resource(chat_id, message_id)
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise

    async def _handle_list_chats(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list_chats tool."""
        limit = arguments.get("limit", 50)

        try:
            dialogs = await self.telegram_client.get_dialogs(limit=limit)

            chats_info = []
            for dialog in dialogs:
                chat_info = {
                    "id": dialog.id,
                    "title": getattr(dialog, 'title', None),
                    "username": getattr(dialog, 'username', None),
                    "type": type(dialog).__name__.lower(),
                    "participants": getattr(dialog, 'participants_count', None)
                }
                chats_info.append(chat_info)

            return create_tool_response(
                f"Found {len(chats_info)} chats:\n" +
                json.dumps(chats_info, indent=2, ensure_ascii=False)
            )

        except Exception as e:
            return create_error_response(f"Failed to list chats: {e}")

    async def _handle_get_messages(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_messages tool."""
        validation_error = validate_tool_arguments(arguments, ["chat_id"])
        if validation_error:
            return create_error_response(validation_error)

        chat_id = arguments["chat_id"]
        limit = arguments.get("limit", 50)
        unread_only = arguments.get("unread_only", False)

        try:
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=limit
            )

            messages_info = []
            for msg in messages:
                if unread_only and msg.is_read:
                    continue

                msg_info = {
                    "id": msg.id,
                    "text": msg.text or "",
                    "sender_id": msg.sender_id,
                    "timestamp": msg.date.isoformat() if msg.date else None,
                    "has_media": bool(msg.media),
                    "media_type": type(msg.media).__name__ if msg.media else None
                }
                messages_info.append(msg_info)

            if unread_only:
                messages_info = [m for m in messages_info if not m.get("is_read")]

            return create_tool_response(
                f"Found {len(messages_info)} messages in chat {chat_id}:\n" +
                json.dumps(messages_info, indent=2, ensure_ascii=False)
            )

        except Exception as e:
            return create_error_response(f"Failed to get messages: {e}")

    async def _handle_send_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle send_message tool."""
        validation_error = validate_tool_arguments(arguments, ["chat_id", "text"])
        if validation_error:
            return create_error_response(validation_error)

        chat_id = arguments["chat_id"]
        text = arguments["text"]
        reply_to = arguments.get("reply_to_message_id")

        try:
            message = await self.telegram_client.send_message(
                chat_id=chat_id,
                text=text,
                reply_to=reply_to
            )

            result = {
                "message_id": message.id,
                "chat_id": message.chat_id,
                "text": message.text,
                "timestamp": message.date.isoformat() if message.date else None
            }

            return create_tool_response(
                f"Message sent successfully:\n" +
                json.dumps(result, indent=2, ensure_ascii=False)
            )

        except Exception as e:
            return create_error_response(f"Failed to send message: {e}")

    async def _handle_edit_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle edit_message tool."""
        validation_error = validate_tool_arguments(arguments, ["chat_id", "message_id", "text"])
        if validation_error:
            return create_error_response(validation_error)

        chat_id = arguments["chat_id"]
        message_id = arguments["message_id"]
        text = arguments["text"]

        try:
            message = await self.telegram_client.edit_message(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )

            result = {
                "message_id": message.id,
                "chat_id": message.chat_id,
                "text": message.text,
                "edited": True
            }

            return create_tool_response(
                f"Message edited successfully:\n" +
                json.dumps(result, indent=2, ensure_ascii=False)
            )

        except Exception as e:
            return create_error_response(f"Failed to edit message: {e}")

    async def _handle_get_media(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_media tool."""
        validation_error = validate_tool_arguments(arguments, ["chat_id", "message_id"])
        if validation_error:
            return create_error_response(validation_error)

        chat_id = arguments["chat_id"]
        message_id = arguments["message_id"]

        try:
            # Get the message first
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=1
            )

            message = next((m for m in messages if m.id == message_id), None)
            if not message:
                return create_error_response(f"Message {message_id} not found in chat {chat_id}")

            if not message.media:
                return create_error_response(f"Message {message_id} has no media attachment")

            # Download the media
            download_result = await self.media_handler.download_media(message)

            if download_result.success and download_result.local_path:
                result = {
                    "media_type": download_result.media_info.media_type.value if download_result.media_info else "unknown",
                    "file_name": download_result.media_info.file_name if download_result.media_info else None,
                    "file_size": download_result.media_info.file_size if download_result.media_info else None,
                    "local_path": str(download_result.local_path)
                }

                return create_tool_response(
                    f"Media downloaded successfully:\n" +
                    json.dumps(result, indent=2, ensure_ascii=False)
                )
            else:
                return create_error_response(f"Failed to download media: {download_result.error_message}")

        except Exception as e:
            return create_error_response(f"Failed to get media: {e}")

    async def _handle_get_contacts(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_contacts tool."""
        # Note: Telegram doesn't have a direct "get contacts" API
        # This would need to be implemented differently, perhaps by
        # getting dialogs and filtering for private chats
        return create_tool_response("Contact retrieval not yet implemented")

    def _chat_to_resource(self, chat: ChatInfo) -> Resource:
        """Convert ChatInfo to MCP Resource."""
        from .mcp_types import chat_to_resource
        return chat_to_resource(chat)

    async def _read_chat_resource(self, chat_id: int) -> str:
        """Read chat resource content."""
        try:
            chat_info = await self.telegram_client.get_chat_info(chat_id)
            data = {
                "id": chat_info.id,
                "title": getattr(chat_info, 'title', None),
                "username": getattr(chat_info, 'username', None),
                "type": type(chat_info).__name__.lower()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to read chat resource: {e}")

    async def _read_message_resource(self, chat_id: int, message_id: int) -> str:
        """Read message resource content."""
        try:
            messages = await self.telegram_client.get_messages(chat_id=chat_id, limit=1)
            message = next((m for m in messages if m.id == message_id), None)

            if not message:
                raise ValueError(f"Message {message_id} not found")

            data = {
                "id": message.id,
                "text": message.text,
                "sender_id": message.sender_id,
                "timestamp": message.date.isoformat() if message.date else None,
                "has_media": bool(message.media)
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to read message resource: {e}")

    async def start_polling(self) -> None:
        """Start message polling."""
        if self.poller is None:
            self.poller = TelegramPoller(
                self.telegram_client,
                self.message_handler,
                self.config
            )

        await self.poller.start_polling()

    async def stop_polling(self) -> None:
        """Stop message polling."""
        if self.poller:
            await self.poller.stop_polling()

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting Telegram MCP server...")

        # Connect to Telegram
        await self.telegram_client.connect()

        # Start message processing
        await self.message_handler.start_processing()

        # Start polling (optional - webhook could be used instead)
        await self.start_polling()

        try:
            # Run the MCP server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            await self.stop_polling()
            await self.message_handler.stop_processing()
            await self.telegram_client.disconnect()