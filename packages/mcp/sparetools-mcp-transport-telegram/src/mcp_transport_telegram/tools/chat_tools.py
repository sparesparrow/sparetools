"""Chat and message management tools for MCP Telegram transport."""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp.types import TextContent

from ..telegram_client import TelegramClientWrapper, TelegramAPIError
from ..mcp_types import create_tool_response, create_error_response, validate_tool_arguments, MessageInfo
from ..exceptions import MCPTelegramError


class ChatTools:
    """Tools for managing Telegram chats and messages."""

    def __init__(self, telegram_client: TelegramClientWrapper):
        """Initialize chat tools.

        Args:
            telegram_client: Telegram client wrapper
        """
        self.telegram_client = telegram_client

    async def list_chats(self, limit: int = 50) -> List[TextContent]:
        """List available Telegram chats.

        Args:
            limit: Maximum number of chats to return

        Returns:
            Formatted response with chat list
        """
        try:
            dialogs = await self.telegram_client.get_dialogs(limit=limit)

            chats_info = []
            for dialog in dialogs:
                chat_info = {
                    "id": dialog.id,
                    "title": getattr(dialog, 'title', None),
                    "username": getattr(dialog, 'username', None),
                    "type": type(dialog).__name__.lower(),
                    "participants": getattr(dialog, 'participants_count', None),
                    "last_message_date": dialog.date.isoformat() if hasattr(dialog, 'date') and dialog.date else None
                }
                chats_info.append(chat_info)

            response_text = f"📋 Found {len(chats_info)} chats:\n\n"
            for chat in chats_info:
                title = chat.get('title') or chat.get('username') or f"Chat {chat['id']}"
                chat_type = chat['type']
                participants = chat.get('participants', 'Unknown')
                response_text += f"• **{title}** ({chat_type}, {participants} members)\n"
                response_text += f"  ID: `{chat['id']}`\n"
                if chat.get('username'):
                    response_text += f"  Username: @{chat['username']}\n"
                response_text += "\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to list chats: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error listing chats: {e}")

    async def get_messages(
        self,
        chat_id: Any,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[TextContent]:
        """Get messages from a specific chat.

        Args:
            chat_id: Chat identifier (ID or username)
            limit: Maximum messages to retrieve
            unread_only: Only return unread messages

        Returns:
            Formatted response with messages
        """
        try:
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=limit
            )

            messages_info = []
            for msg in messages:
                # Skip if we only want unread and this is read
                if unread_only and getattr(msg, 'is_read', False):
                    continue

                msg_info = MessageInfo(
                    id=msg.id,
                    chat_id=getattr(msg, 'chat_id', chat_id),
                    sender_id=msg.sender_id,
                    sender_name=getattr(msg.sender, 'first_name', None) if hasattr(msg, 'sender') and msg.sender else None,
                    text=msg.text or "",
                    timestamp=msg.date.isoformat() if msg.date else datetime.now().isoformat(),
                    has_media=bool(msg.media),
                    media_type=type(msg.media).__name__ if msg.media else None,
                    reply_to_message_id=getattr(msg, 'reply_to_msg_id', None),
                    thread_id=None  # Would need additional logic for threads
                )
                messages_info.append(msg_info)

            if not messages_info:
                return create_tool_response(f"📭 No {'unread ' if unread_only else ''}messages found in chat {chat_id}")

            response_text = f"💬 Found {len(messages_info)} {'unread ' if unread_only else ''}messages in chat {chat_id}:\n\n"

            for msg in messages_info[-10:]:  # Show last 10 messages
                sender = msg.sender_name or f"User {msg.sender_id}" or "Unknown"
                time_str = msg.timestamp.split('T')[1][:5] if 'T' in msg.timestamp else msg.timestamp
                response_text += f"**{sender}** ({time_str}): {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}\n"
                if msg.has_media:
                    response_text += f"📎 Contains {msg.media_type}\n"
                response_text += "\n"

            if len(messages_info) > 10:
                response_text += f"\n... and {len(messages_info) - 10} more messages"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to get messages from chat {chat_id}: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error getting messages: {e}")

    async def send_message(
        self,
        chat_id: Any,
        text: str,
        reply_to_message_id: Optional[int] = None
    ) -> List[TextContent]:
        """Send a message to a chat.

        Args:
            chat_id: Chat identifier
            text: Message text
            reply_to_message_id: Optional message ID to reply to

        Returns:
            Confirmation of sent message
        """
        try:
            message = await self.telegram_client.send_message(
                chat_id=chat_id,
                text=text,
                reply_to=reply_to_message_id
            )

            response_text = f"✅ Message sent successfully!\n\n"
            response_text += f"**Chat:** {chat_id}\n"
            response_text += f"**Message ID:** {message.id}\n"
            response_text += f"**Content:** {text[:200]}{'...' if len(text) > 200 else ''}\n"
            if reply_to_message_id:
                response_text += f"**Reply to:** Message {reply_to_message_id}\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to send message to chat {chat_id}: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error sending message: {e}")

    async def edit_message(
        self,
        chat_id: Any,
        message_id: int,
        text: str
    ) -> List[TextContent]:
        """Edit an existing message.

        Args:
            chat_id: Chat identifier
            message_id: ID of message to edit
            text: New message text

        Returns:
            Confirmation of edited message
        """
        try:
            message = await self.telegram_client.edit_message(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )

            response_text = f"✏️ Message edited successfully!\n\n"
            response_text += f"**Chat:** {chat_id}\n"
            response_text += f"**Message ID:** {message.id}\n"
            response_text += f"**New content:** {text[:200]}{'...' if len(text) > 200 else ''}\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to edit message {message_id} in chat {chat_id}: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error editing message: {e}")

    async def get_chat_info(self, chat_id: Any) -> List[TextContent]:
        """Get detailed information about a chat.

        Args:
            chat_id: Chat identifier

        Returns:
            Detailed chat information
        """
        try:
            chat_info = await self.telegram_client.get_chat_info(chat_id)

            info = {
                "id": chat_info.id,
                "title": getattr(chat_info, 'title', None),
                "username": getattr(chat_info, 'username', None),
                "type": type(chat_info).__name__.lower(),
                "participants_count": getattr(chat_info, 'participants_count', None),
                "description": getattr(chat_info, 'about', None),
                "verified": getattr(chat_info, 'verified', False),
                "restricted": getattr(chat_info, 'restricted', False)
            }

            response_text = f"📋 Chat Information:\n\n"
            response_text += f"**Title:** {info['title'] or 'N/A'}\n"
            response_text += f"**Username:** @{info['username']} \n" if info['username'] else "**Username:** N/A\n"
            response_text += f"**Type:** {info['type']}\n"
            response_text += f"**Participants:** {info['participants_count'] or 'Unknown'}\n"
            response_text += f"**Verified:** {'✅' if info['verified'] else '❌'}\n"
            if info['description']:
                response_text += f"**Description:** {info['description'][:200]}{'...' if len(info['description']) > 200 else ''}\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to get chat info for {chat_id}: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error getting chat info: {e}")