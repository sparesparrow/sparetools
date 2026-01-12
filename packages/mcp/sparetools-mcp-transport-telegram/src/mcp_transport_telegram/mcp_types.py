"""MCP-specific type definitions and utilities."""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from mcp.types import (
    Tool, Resource, TextContent, ImageContent,
    EmbeddedResource, LoggingLevel
)


class MCPToolName(str, Enum):
    """Enumeration of available MCP tool names."""
    LIST_CHATS = "list_chats"
    GET_MESSAGES = "get_messages"
    SEND_MESSAGE = "send_message"
    EDIT_MESSAGE = "edit_message"
    GET_MEDIA = "get_media"
    GET_CONTACTS = "get_contacts"


class MCPResourceType(str, Enum):
    """Enumeration of available MCP resource types."""
    CHAT_INFO = "chat"
    MESSAGE_THREAD = "thread"
    MEDIA_ATTACHMENT = "media"
    CONTACT_INFO = "contact"


@dataclass
class ChatInfo:
    """Information about a Telegram chat."""
    id: int
    title: Optional[str]
    username: Optional[str]
    chat_type: str  # 'private', 'group', 'supergroup', 'channel'
    participant_count: Optional[int]
    description: Optional[str]


@dataclass
class MessageInfo:
    """Information about a Telegram message."""
    id: int
    chat_id: int
    sender_id: Optional[int]
    sender_name: Optional[str]
    text: str
    timestamp: str
    has_media: bool
    media_type: Optional[str]
    reply_to_message_id: Optional[int]
    thread_id: Optional[int]


@dataclass
class ContactInfo:
    """Information about a Telegram contact."""
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    is_bot: bool


@dataclass
class MCPToolCall:
    """Represents an MCP tool call."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class MCPToolResult:
    """Represents the result of an MCP tool call."""
    tool_call_id: str
    content: List[Union[TextContent, ImageContent, EmbeddedResource]]
    is_error: bool = False


@dataclass
class MCPResourceContent:
    """Content for MCP resources."""
    uri: str
    content: Union[str, bytes]
    mime_type: str
    encoding: Optional[str] = None


class MCPErrorCode(str, Enum):
    """MCP error codes."""
    INVALID_REQUEST = "INVALID_REQUEST"
    METHOD_NOT_FOUND = "METHOD_NOT_FOUND"
    INVALID_PARAMS = "INVALID_PARAMS"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"


@dataclass
class MCPError:
    """MCP error response."""
    code: MCPErrorCode
    message: str
    data: Optional[Any] = None


# Utility functions for converting between Telegram and MCP types

def chat_to_resource(chat: ChatInfo) -> Resource:
    """Convert ChatInfo to MCP Resource."""
    return Resource(
        uri=f"telegram://chat/{chat.id}",
        name=f"Chat: {chat.title or chat.username or str(chat.id)}",
        description=f"Telegram {chat.chat_type} chat",
        mime_type="application/json"
    )


def message_to_resource(message: MessageInfo) -> Resource:
    """Convert MessageInfo to MCP Resource."""
    return Resource(
        uri=f"telegram://message/{message.chat_id}/{message.id}",
        name=f"Message {message.id}",
        description=f"Message from {message.sender_name or 'Unknown'}",
        mime_type="application/json"
    )


def contact_to_resource(contact: ContactInfo) -> Resource:
    """Convert ContactInfo to MCP Resource."""
    display_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
    if not display_name and contact.username:
        display_name = f"@{contact.username}"

    return Resource(
        uri=f"telegram://contact/{contact.id}",
        name=f"Contact: {display_name or str(contact.id)}",
        description="Telegram contact information",
        mime_type="application/json"
    )


def create_tool_response(content: Union[str, List[Union[TextContent, ImageContent, EmbeddedResource]]]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Create a standardized tool response."""
    if isinstance(content, str):
        return [TextContent(type="text", text=content)]
    elif isinstance(content, list):
        return content
    else:
        return [TextContent(type="text", text=str(content))]


def create_error_response(error: Union[str, MCPError, Exception]) -> List[TextContent]:
    """Create an error response for tool calls."""
    if isinstance(error, str):
        message = error
    elif isinstance(error, MCPError):
        message = f"Error {error.code}: {error.message}"
    elif isinstance(error, Exception):
        message = f"Error: {str(error)}"
    else:
        message = "An unknown error occurred"

    return [TextContent(
        type="text",
        text=f"❌ {message}"
    )]


def validate_tool_arguments(args: Dict[str, Any], required: List[str]) -> Optional[str]:
    """Validate that required arguments are present.

    Returns error message if validation fails, None if valid.
    """
    missing = [arg for arg in required if arg not in args or args[arg] is None]
    if missing:
        return f"Missing required arguments: {', '.join(missing)}"
    return None