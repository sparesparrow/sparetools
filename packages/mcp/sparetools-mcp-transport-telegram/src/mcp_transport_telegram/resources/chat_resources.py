"""Chat-related MCP resources for Telegram transport."""

import json
from typing import List, Optional, Dict, Any

from mcp.types import Resource

from ..telegram_client import TelegramClientWrapper, TelegramAPIError
from ..mcp_types import ChatInfo, MessageInfo, chat_to_resource, message_to_resource
from ..exceptions import MCPTelegramError


class ChatResources:
    """MCP Resources for Telegram chats and messages."""

    def __init__(self, telegram_client: TelegramClientWrapper):
        """Initialize chat resources.

        Args:
            telegram_client: Telegram client wrapper
        """
        self.telegram_client = telegram_client

    async def list_chat_resources(self, limit: int = 50) -> List[Resource]:
        """List available chat resources.

        Args:
            limit: Maximum number of chats to include

        Returns:
            List of MCP Resources for chats
        """
        try:
            dialogs = await self.telegram_client.get_dialogs(limit=limit)

            resources = []
            for dialog in dialogs:
                try:
                    # Create ChatInfo from dialog
                    chat_info = ChatInfo(
                        id=dialog.id,
                        title=getattr(dialog, 'title', None),
                        username=getattr(dialog, 'username', None),
                        chat_type=type(dialog).__name__.lower(),
                        participant_count=getattr(dialog, 'participants_count', None),
                        description=None  # Would need additional API call to get description
                    )

                    resource = chat_to_resource(chat_info)
                    resources.append(resource)

                except Exception as e:
                    # Skip problematic dialogs but continue with others
                    continue

            return resources

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to list chat resources: {e}")
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error listing chat resources: {e}")

    async def list_message_resources(self, chat_id: int, limit: int = 20) -> List[Resource]:
        """List message resources for a specific chat.

        Args:
            chat_id: Chat identifier
            limit: Maximum number of messages to include

        Returns:
            List of MCP Resources for messages
        """
        try:
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=limit
            )

            resources = []
            for message in messages:
                try:
                    # Create MessageInfo from message
                    msg_info = MessageInfo(
                        id=message.id,
                        chat_id=chat_id,
                        sender_id=message.sender_id,
                        sender_name=self._get_sender_name(message),
                        text=message.text or "",
                        timestamp=message.date.isoformat() if message.date else "",
                        has_media=bool(message.media),
                        media_type=type(message.media).__name__ if message.media else None,
                        reply_to_message_id=getattr(message, 'reply_to_msg_id', None),
                        thread_id=None
                    )

                    resource = message_to_resource(msg_info)
                    resources.append(resource)

                except Exception as e:
                    # Skip problematic messages but continue with others
                    continue

            return resources

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to list message resources for chat {chat_id}: {e}")
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error listing message resources: {e}")

    async def read_chat_resource(self, chat_id: int) -> str:
        """Read detailed chat resource content.

        Args:
            chat_id: Chat identifier

        Returns:
            JSON string with chat details
        """
        try:
            chat_info = await self.telegram_client.get_chat_info(chat_id)

            # Build comprehensive chat data
            chat_data = {
                "id": chat_info.id,
                "title": getattr(chat_info, 'title', None),
                "username": getattr(chat_info, 'username', None),
                "type": type(chat_info).__name__.lower(),
                "participants_count": getattr(chat_info, 'participants_count', None),
                "description": getattr(chat_info, 'about', None),
                "verified": getattr(chat_info, 'verified', False),
                "restricted": getattr(chat_info, 'restricted', False),
                "scam": getattr(chat_info, 'scam', False),
                "fake": getattr(chat_info, 'fake', False),
                "access_hash": getattr(chat_info, 'access_hash', None),
                "date_created": getattr(chat_info, 'date', None).isoformat() if hasattr(chat_info, 'date') and chat_info.date else None
            }

            # Add additional chat-specific information
            if hasattr(chat_info, 'photo'):
                chat_data["has_photo"] = True
                if hasattr(chat_info.photo, 'photo_id'):
                    chat_data["photo_id"] = chat_info.photo.photo_id
            else:
                chat_data["has_photo"] = False

            # Add permissions if available
            if hasattr(chat_info, 'default_banned_rights'):
                chat_data["default_restrictions"] = str(chat_info.default_banned_rights)

            return json.dumps(chat_data, indent=2, ensure_ascii=False, default=str)

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to read chat resource {chat_id}: {e}")
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error reading chat resource {chat_id}: {e}")

    async def read_message_resource(self, chat_id: int, message_id: int) -> str:
        """Read detailed message resource content.

        Args:
            chat_id: Chat identifier
            message_id: Message identifier

        Returns:
            JSON string with message details
        """
        try:
            # Get the specific message
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=1
            )

            message = next((m for m in messages if m.id == message_id), None)
            if not message:
                raise MCPTelegramError(f"Message {message_id} not found in chat {chat_id}")

            # Build comprehensive message data
            message_data = {
                "id": message.id,
                "chat_id": chat_id,
                "sender_id": message.sender_id,
                "sender_name": self._get_sender_name(message),
                "text": message.text or "",
                "timestamp": message.date.isoformat() if message.date else None,
                "edit_date": message.edit_date.isoformat() if getattr(message, 'edit_date', None) else None,
                "has_media": bool(message.media),
                "media_type": type(message.media).__name__ if message.media else None,
                "reply_to_message_id": getattr(message, 'reply_to_msg_id', None),
                "forward_from": getattr(message, 'forward', None),
                "views": getattr(message, 'views', None),
                "forwards": getattr(message, 'forwards', None),
                "replies": getattr(message, 'replies', None),
                "is_reply": bool(getattr(message, 'reply_to_msg_id', None)),
                "is_forward": bool(getattr(message, 'forward', None)),
                "is_edited": bool(getattr(message, 'edit_date', None)),
                "mentioned": getattr(message, 'mentioned', False),
                "pinned": getattr(message, 'pinned', False),
                "from_scheduled": getattr(message, 'from_scheduled', False)
            }

            # Add media-specific information
            if message.media:
                media_info = self._extract_media_info(message.media)
                message_data["media_info"] = media_info

            # Add reactions if available
            if hasattr(message, 'reactions') and message.reactions:
                message_data["reactions"] = self._extract_reactions_info(message.reactions)

            return json.dumps(message_data, indent=2, ensure_ascii=False, default=str)

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to read message resource {chat_id}/{message_id}: {e}")
        except MCPTelegramError:
            raise
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error reading message resource {chat_id}/{message_id}: {e}")

    def _get_sender_name(self, message) -> Optional[str]:
        """Extract sender name from message."""
        if hasattr(message, 'sender') and message.sender:
            sender = message.sender
            first_name = getattr(sender, 'first_name', None)
            last_name = getattr(sender, 'last_name', None)
            username = getattr(sender, 'username', None)

            if first_name and last_name:
                return f"{first_name} {last_name}"
            elif first_name:
                return first_name
            elif username:
                return f"@{username}"

        return None

    def _extract_media_info(self, media) -> Dict[str, Any]:
        """Extract media information."""
        media_info = {
            "type": type(media).__name__
        }

        try:
            # Document/File media
            if hasattr(media, 'document'):
                doc = media.document
                media_info.update({
                    "file_name": None,
                    "mime_type": getattr(doc, 'mime_type', None),
                    "file_size": getattr(doc, 'size', None),
                    "file_id": getattr(doc, 'id', None)
                })

                # Extract attributes
                if hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if hasattr(attr, 'file_name'):
                            media_info["file_name"] = attr.file_name
                        elif hasattr(attr, 'duration'):
                            media_info["duration"] = attr.duration
                        elif hasattr(attr, 'w') and hasattr(attr, 'h'):
                            media_info["width"] = attr.w
                            media_info["height"] = attr.h
                        elif hasattr(attr, 'performer') and hasattr(attr, 'title'):
                            media_info["performer"] = attr.performer
                            media_info["title"] = attr.title

            # Photo media
            elif hasattr(media, 'photo'):
                photo = media.photo
                media_info.update({
                    "file_id": getattr(photo, 'id', None)
                })

                # Get sizes information
                if hasattr(photo, 'sizes') and photo.sizes:
                    sizes_info = []
                    for size in photo.sizes:
                        size_info = {
                            "type": getattr(size, 'type', None),
                            "width": getattr(size, 'w', None),
                            "height": getattr(size, 'h', None),
                            "size": getattr(size, 'size', None)
                        }
                        sizes_info.append(size_info)
                    media_info["sizes"] = sizes_info

            # Audio/Video specific attributes
            for attr_name in ['duration', 'title', 'performer', 'waveform']:
                if hasattr(media, attr_name):
                    media_info[attr_name] = getattr(media, attr_name)

        except Exception as e:
            media_info["extraction_error"] = str(e)

        return media_info

    def _extract_reactions_info(self, reactions) -> Dict[str, Any]:
        """Extract reactions information."""
        reactions_info = {}

        try:
            if hasattr(reactions, 'results'):
                reaction_list = []
                for reaction in reactions.results:
                    reaction_data = {
                        "reaction": str(getattr(reaction, 'reaction', '')),
                        "count": getattr(reaction, 'count', 0),
                        "chosen": getattr(reaction, 'chosen', False)
                    }
                    reaction_list.append(reaction_data)
                reactions_info["reactions"] = reaction_list

            reactions_info["total_count"] = getattr(reactions, 'count', 0)

        except Exception as e:
            reactions_info["extraction_error"] = str(e)

        return reactions_info