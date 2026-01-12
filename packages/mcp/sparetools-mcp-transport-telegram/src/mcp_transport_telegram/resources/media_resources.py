"""Media-related MCP resources for Telegram transport."""

import json
from typing import List, Optional, Dict, Any

from mcp.types import Resource

from ..telegram_client import TelegramClientWrapper, TelegramAPIError
from ..media_handler import MediaHandler
from ..mcp_types import MediaInfo
from ..exceptions import MCPTelegramError


class MediaResources:
    """MCP Resources for Telegram media attachments."""

    def __init__(self, telegram_client: TelegramClientWrapper, media_handler: MediaHandler):
        """Initialize media resources.

        Args:
            telegram_client: Telegram client wrapper
            media_handler: Media handler instance
        """
        self.telegram_client = telegram_client
        self.media_handler = media_handler

    async def list_media_resources(self, chat_id: int, limit: int = 50) -> List[Resource]:
        """List media resources in a chat.

        Args:
            chat_id: Chat identifier
            limit: Maximum number of media resources to list

        Returns:
            List of MCP Resources for media
        """
        try:
            # Get recent messages from the chat
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=min(limit * 3, 100)  # Get more messages to filter for media
            )

            resources = []
            media_count = 0

            for message in messages:
                if message.media and media_count < limit:
                    try:
                        resource = self._message_media_to_resource(message, chat_id)
                        if resource:
                            resources.append(resource)
                            media_count += 1

                    except Exception as e:
                        # Skip problematic media but continue
                        continue

            return resources

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to list media resources for chat {chat_id}: {e}")
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error listing media resources: {e}")

    async def read_media_resource(self, chat_id: int, message_id: int) -> str:
        """Read media resource content.

        Args:
            chat_id: Chat identifier
            message_id: Message identifier

        Returns:
            JSON string with media information
        """
        try:
            # Get the message
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=1
            )

            message = next((m for m in messages if m.id == message_id), None)
            if not message:
                raise MCPTelegramError(f"Message {message_id} not found in chat {chat_id}")

            if not message.media:
                raise MCPTelegramError(f"Message {message_id} has no media")

            # Extract media information
            media_data = {
                "message_id": message_id,
                "chat_id": chat_id,
                "timestamp": message.date.isoformat() if message.date else None,
                "sender_id": message.sender_id,
                "media_type": type(message.media).__name__,
                "media_info": self._extract_detailed_media_info(message.media),
                "caption": getattr(message, 'caption', None),
                "file_available": True
            }

            # Try to get local file information if it was downloaded
            # This is a simplified implementation - in practice you'd track downloads
            temp_files = list(self.media_handler.temp_dir.glob("*"))
            message_files = [f for f in temp_files if f.name.startswith(f"{chat_id}_{message_id}_")]

            if message_files:
                media_data["local_files"] = [
                    {
                        "path": str(f),
                        "size": f.stat().st_size,
                        "modified": f.stat().st_mtime
                    }
                    for f in message_files
                ]

            return json.dumps(media_data, indent=2, ensure_ascii=False, default=str)

        except TelegramAPIError as e:
            raise MCPTelegramError(f"Failed to read media resource {chat_id}/{message_id}: {e}")
        except MCPTelegramError:
            raise
        except Exception as e:
            raise MCPTelegramError(f"Unexpected error reading media resource {chat_id}/{message_id}: {e}")

    def _message_media_to_resource(self, message, chat_id: int) -> Optional[Resource]:
        """Convert message media to MCP Resource.

        Args:
            message: Telegram message with media
            chat_id: Chat identifier

        Returns:
            MCP Resource or None if conversion fails
        """
        try:
            if not message.media:
                return None

            # Determine media type and description
            media_class = message.media.__class__.__name__
            media_type = "unknown"

            if 'Photo' in media_class:
                media_type = "photo"
            elif 'Document' in media_class:
                media_type = "document"
            elif 'Voice' in media_class:
                media_type = "voice"
            elif 'Audio' in media_class:
                media_type = "audio"
            elif 'Video' in media_class:
                media_type = "video"
            elif 'Sticker' in media_class:
                media_type = "sticker"
            elif 'Animation' in media_class:
                media_type = "animation"

            # Get file name if available
            file_name = f"media_{message.id}"
            if hasattr(message.media, 'document') and message.media.document:
                doc = message.media.document
                if hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if hasattr(attr, 'file_name') and attr.file_name:
                            file_name = attr.file_name
                            break

            # Create resource
            resource = Resource(
                uri=f"telegram://media/{chat_id}/{message.id}",
                name=f"{media_type.title()}: {file_name}",
                description=f"Media attachment from message {message.id} in chat {chat_id}",
                mime_type=self._guess_mime_type(message.media)
            )

            return resource

        except Exception as e:
            # Return None for problematic media
            return None

    def _guess_mime_type(self, media) -> str:
        """Guess MIME type for media.

        Args:
            media: Telegram media object

        Returns:
            MIME type string
        """
        try:
            media_class = media.__class__.__name__

            # Photo
            if 'Photo' in media_class:
                return "image/jpeg"

            # Document with MIME type
            if hasattr(media, 'document') and media.document:
                doc = media.document
                if hasattr(doc, 'mime_type') and doc.mime_type:
                    return doc.mime_type

                # Guess from file extension in attributes
                if hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if hasattr(attr, 'file_name') and attr.file_name:
                            ext = attr.file_name.split('.')[-1].lower()
                            mime_types = {
                                'pdf': 'application/pdf',
                                'doc': 'application/msword',
                                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                'txt': 'text/plain',
                                'jpg': 'image/jpeg',
                                'jpeg': 'image/jpeg',
                                'png': 'image/png',
                                'gif': 'image/gif',
                                'mp4': 'video/mp4',
                                'avi': 'video/avi',
                                'mp3': 'audio/mpeg',
                                'wav': 'audio/wav'
                            }
                            return mime_types.get(ext, 'application/octet-stream')

            # Audio/Video
            if 'Voice' in media_class:
                return "audio/ogg"
            if 'Audio' in media_class:
                return "audio/mpeg"
            if 'Video' in media_class:
                return "video/mp4"
            if 'Animation' in media_class:
                return "video/mp4"
            if 'Sticker' in media_class:
                return "image/webp"

        except Exception:
            pass

        return "application/octet-stream"

    def _extract_detailed_media_info(self, media) -> Dict[str, Any]:
        """Extract detailed media information.

        Args:
            media: Telegram media object

        Returns:
            Dictionary with media details
        """
        info = {
            "type": type(media).__name__,
            "size_bytes": None,
            "file_id": None,
            "access_hash": None,
            "file_reference": None
        }

        try:
            # Extract common attributes
            for attr in ['size', 'id', 'access_hash', 'file_reference']:
                if hasattr(media, attr):
                    value = getattr(media, attr)
                    # Convert bytes to hex for file_reference
                    if attr == 'file_reference' and isinstance(value, bytes):
                        value = value.hex()
                    info[f"file_{attr}"] = value

            # Document-specific information
            if hasattr(media, 'document') and media.document:
                doc = media.document
                info["document_id"] = getattr(doc, 'id', None)
                info["document_size"] = getattr(doc, 'size', None)
                info["mime_type"] = getattr(doc, 'mime_type', None)

                # Document attributes
                if hasattr(doc, 'attributes'):
                    attributes = []
                    for attr in doc.attributes:
                        attr_info = {
                            "type": type(attr).__name__
                        }

                        # Extract common attribute fields
                        for field in ['file_name', 'duration', 'w', 'h', 'performer', 'title']:
                            if hasattr(attr, field):
                                attr_info[field] = getattr(attr, field)

                        attributes.append(attr_info)

                    info["attributes"] = attributes

            # Photo-specific information
            elif hasattr(media, 'photo') and media.photo:
                photo = media.photo
                info["photo_id"] = getattr(photo, 'id', None)

                # Photo sizes
                if hasattr(photo, 'sizes') and photo.sizes:
                    sizes = []
                    for size in photo.sizes:
                        size_info = {}
                        for field in ['type', 'w', 'h', 'size']:
                            if hasattr(size, field):
                                size_info[field] = getattr(size, field)
                        sizes.append(size_info)
                    info["sizes"] = sizes

            # Audio/Video specific attributes
            for attr_name in ['duration', 'title', 'performer', 'waveform']:
                if hasattr(media, attr_name):
                    info[attr_name] = getattr(media, attr_name)

        except Exception as e:
            info["extraction_error"] = str(e)

        return info