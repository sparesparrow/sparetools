"""Media handling tools for MCP Telegram transport."""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from mcp.types import TextContent

from ..telegram_client import TelegramClientWrapper, TelegramAPIError
from ..media_handler import MediaHandler, MediaDownloadResult
from ..mcp_types import create_tool_response, create_error_response, validate_tool_arguments
from ..exceptions import MCPTelegramError, MediaHandlingError


class MediaTools:
    """Tools for handling media in Telegram messages."""

    def __init__(self, telegram_client: TelegramClientWrapper, media_handler: MediaHandler):
        """Initialize media tools.

        Args:
            telegram_client: Telegram client wrapper
            media_handler: Media handler instance
        """
        self.telegram_client = telegram_client
        self.media_handler = media_handler

    async def download_media(
        self,
        chat_id: Any,
        message_id: int,
        save_path: Optional[str] = None
    ) -> List[TextContent]:
        """Download media from a specific message.

        Args:
            chat_id: Chat identifier
            message_id: Message ID containing media
            save_path: Optional custom save path

        Returns:
            Information about downloaded media
        """
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
            download_result = await self.media_handler.download_media(
                message,
                save_path
            )

            if download_result.success and download_result.local_path and download_result.media_info:
                media_info = download_result.media_info

                response_text = f"📥 Media downloaded successfully!\n\n"
                response_text += f"**Type:** {media_info.media_type.value}\n"
                response_text += f"**File:** {media_info.file_name}\n"
                response_text += f"**Size:** {self._format_file_size(media_info.file_size)}\n"
                if media_info.width and media_info.height:
                    response_text += f"**Dimensions:** {media_info.width}×{media_info.height}\n"
                if media_info.duration:
                    response_text += f"**Duration:** {media_info.duration} seconds\n"
                response_text += f"**Saved to:** {download_result.local_path}\n"

                # Add MIME type if available
                if media_info.mime_type:
                    response_text += f"**MIME Type:** {media_info.mime_type}\n"

                return create_tool_response(response_text)
            else:
                return create_error_response(f"Failed to download media: {download_result.error_message}")

        except TelegramAPIError as e:
            return create_error_response(f"Telegram API error downloading media: {e}")
        except MediaHandlingError as e:
            return create_error_response(f"Media handling error: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error downloading media: {e}")

    async def get_media_info(
        self,
        chat_id: Any,
        message_id: int
    ) -> List[TextContent]:
        """Get information about media in a message without downloading.

        Args:
            chat_id: Chat identifier
            message_id: Message ID

        Returns:
            Media information
        """
        try:
            # Get the message
            messages = await self.telegram_client.get_messages(
                chat_id=chat_id,
                limit=1
            )

            message = next((m for m in messages if m.id == message_id), None)
            if not message:
                return create_error_response(f"Message {message_id} not found in chat {chat_id}")

            if not message.media:
                return create_error_response(f"Message {message_id} has no media attachment")

            # Extract media information without downloading
            media_class = message.media.__class__.__name__

            info = {
                "media_type": media_class,
                "has_media": True
            }

            # Add specific information based on media type
            if hasattr(message.media, 'document'):
                doc = message.media.document
                if hasattr(doc, 'size'):
                    info["file_size"] = doc.size
                if hasattr(doc, 'mime_type'):
                    info["mime_type"] = doc.mime_type

                # Try to get filename
                if hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if hasattr(attr, 'file_name'):
                            info["file_name"] = attr.file_name
                        elif hasattr(attr, 'w') and hasattr(attr, 'h'):
                            info["width"] = attr.w
                            info["height"] = attr.h
                        elif hasattr(attr, 'duration'):
                            info["duration"] = attr.duration

            elif hasattr(message.media, 'photo'):
                photo = message.media.photo
                if hasattr(photo, 'sizes') and photo.sizes:
                    # Get largest size
                    largest = max(photo.sizes, key=lambda s: (s.size if hasattr(s, 'size') else 0))
                    if hasattr(largest, 'w') and hasattr(largest, 'h'):
                        info["width"] = largest.w
                        info["height"] = largest.h
                    if hasattr(largest, 'size'):
                        info["file_size"] = largest.size
                info["mime_type"] = "image/jpeg"

            response_text = f"📋 Media Information for Message {message_id}:\n\n"
            response_text += f"**Type:** {info['media_type']}\n"

            if 'file_name' in info:
                response_text += f"**File:** {info['file_name']}\n"
            if 'file_size' in info:
                response_text += f"**Size:** {self._format_file_size(info['file_size'])}\n"
            if 'mime_type' in info:
                response_text += f"**MIME Type:** {info['mime_type']}\n"
            if 'width' in info and 'height' in info:
                response_text += f"**Dimensions:** {info['width']}×{info['height']}\n"
            if 'duration' in info:
                response_text += f"**Duration:** {info['duration']} seconds\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Telegram API error getting media info: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error getting media info: {e}")

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> List[TextContent]:
        """Clean up old temporary media files.

        Args:
            max_age_hours: Maximum age of files to keep

        Returns:
            Cleanup status
        """
        try:
            cleaned_count = await self.media_handler.cleanup_temp_files(max_age_hours)

            response_text = f"🧹 Cleanup completed!\n\n"
            response_text += f"**Files cleaned:** {cleaned_count}\n"
            response_text += f"**Max age:** {max_age_hours} hours\n"
            response_text += f"**Temp directory:** {self.media_handler.temp_dir}\n"

            return create_tool_response(response_text)

        except Exception as e:
            return create_error_response(f"Error during cleanup: {e}")

    async def get_temp_directory_info(self) -> List[TextContent]:
        """Get information about the temporary media directory.

        Returns:
            Directory information
        """
        try:
            total_size = self.media_handler.get_temp_dir_size()
            file_count = len(list(self.media_handler.temp_dir.glob("*")))

            response_text = f"📁 Temporary Media Directory Info:\n\n"
            response_text += f"**Location:** {self.media_handler.temp_dir}\n"
            response_text += f"**Files:** {file_count}\n"
            response_text += f"**Total size:** {self._format_file_size(total_size)}\n"
            response_text += f"**Max file size:** {self._format_file_size(self.media_handler.max_file_size)}\n"

            return create_tool_response(response_text)

        except Exception as e:
            return create_error_response(f"Error getting directory info: {e}")

    def _format_file_size(self, size_bytes: Optional[int]) -> str:
        """Format file size in human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes is None:
            return "Unknown"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"