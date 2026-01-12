"""Contact management tools for MCP Telegram transport."""

from typing import Dict, List, Any, Optional

from mcp.types import TextContent

from ..telegram_client import TelegramClientWrapper, TelegramAPIError
from ..mcp_types import create_tool_response, create_error_response, ContactInfo
from ..exceptions import MCPTelegramError


class ContactTools:
    """Tools for managing Telegram contacts."""

    def __init__(self, telegram_client: TelegramClientWrapper):
        """Initialize contact tools.

        Args:
            telegram_client: Telegram client wrapper
        """
        self.telegram_client = telegram_client

    async def get_contacts(self, limit: int = 100) -> List[TextContent]:
        """Get list of Telegram contacts.

        Note: Telegram doesn't provide a direct contacts API.
        This implementation gets contacts from private dialogs.

        Args:
            limit: Maximum number of contacts to return

        Returns:
            List of contacts
        """
        try:
            # Get dialogs to find private chats (which represent contacts)
            dialogs = await self.telegram_client.get_dialogs(limit=limit * 2)  # Get more to filter

            contacts = []
            for dialog in dialogs:
                # Check if this is a private chat (User type)
                if hasattr(dialog, 'entity') and hasattr(dialog.entity, '__class__'):
                    entity_class = dialog.entity.__class__.__name__
                    if entity_class == 'User':
                        contact_info = ContactInfo(
                            id=dialog.entity.id,
                            first_name=getattr(dialog.entity, 'first_name', None),
                            last_name=getattr(dialog.entity, 'last_name', None),
                            username=getattr(dialog.entity, 'username', None),
                            phone=getattr(dialog.entity, 'phone', None),
                            is_bot=getattr(dialog.entity, 'bot', False)
                        )
                        contacts.append(contact_info)

                        if len(contacts) >= limit:
                            break

            if not contacts:
                return create_tool_response("📞 No contacts found. Note: Contacts are derived from private chat dialogs.")

            response_text = f"📞 Found {len(contacts)} contacts:\n\n"

            for contact in contacts:
                display_name = self._format_contact_name(contact)
                response_text += f"• **{display_name}**\n"
                response_text += f"  ID: `{contact.id}`\n"
                if contact.username:
                    response_text += f"  Username: @{contact.username}\n"
                if contact.phone:
                    response_text += f"  Phone: {contact.phone}\n"
                response_text += f"  Type: {'🤖 Bot' if contact.is_bot else '👤 User'}\n"
                response_text += "\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to get contacts: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error getting contacts: {e}")

    async def get_contact_info(self, contact_id: int) -> List[TextContent]:
        """Get detailed information about a specific contact.

        Args:
            contact_id: Contact's Telegram ID

        Returns:
            Detailed contact information
        """
        try:
            # Get the user entity
            user = await self.telegram_client.get_chat_info(contact_id)

            # Ensure it's a user
            if not hasattr(user, '__class__') or user.__class__.__name__ != 'User':
                return create_error_response(f"ID {contact_id} is not a user/contact")

            contact_info = ContactInfo(
                id=user.id,
                first_name=getattr(user, 'first_name', None),
                last_name=getattr(user, 'last_name', None),
                username=getattr(user, 'username', None),
                phone=getattr(user, 'phone', None),
                is_bot=getattr(user, 'bot', False)
            )

            response_text = f"👤 Contact Information:\n\n"
            response_text += f"**Name:** {self._format_contact_name(contact_info)}\n"
            response_text += f"**ID:** {contact_info.id}\n"
            if contact_info.username:
                response_text += f"**Username:** @{contact_info.username}\n"
            if contact_info.phone:
                response_text += f"**Phone:** {contact_info.phone}\n"
            response_text += f"**Type:** {'🤖 Bot' if contact_info.is_bot else '👤 User'}\n"

            # Additional user information
            if hasattr(user, 'verified') and user.verified:
                response_text += "**Verified:** ✅\n"
            if hasattr(user, 'premium') and user.premium:
                response_text += "**Premium:** ⭐\n"
            if hasattr(user, 'lang_code'):
                response_text += f"**Language:** {user.lang_code}\n"

            return create_tool_response(response_text)

        except TelegramAPIError as e:
            return create_error_response(f"Failed to get contact info for {contact_id}: {e}")
        except Exception as e:
            return create_error_response(f"Unexpected error getting contact info: {e}")

    async def search_contacts(self, query: str, limit: int = 50) -> List[TextContent]:
        """Search for contacts by name or username.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            Matching contacts
        """
        try:
            # Get all contacts first
            all_contacts = await self.get_contacts(limit=200)  # Get more to search through

            if not all_contacts or not isinstance(all_contacts[0], TextContent):
                return create_error_response("Failed to retrieve contacts for searching")

            # Parse the contact list to search through
            # This is a simplified implementation - in practice you'd want to search server-side
            contacts_text = all_contacts[0].text
            matching_contacts = []

            # Very basic text search - would need improvement for production
            query_lower = query.lower()
            lines = contacts_text.split('\n')

            current_contact = {}
            for line in lines:
                if line.startswith('• **'):
                    # New contact
                    if current_contact and self._contact_matches_query(current_contact, query_lower):
                        matching_contacts.append(current_contact)
                        if len(matching_contacts) >= limit:
                            break
                    current_contact = {'name': line[4:-2]}  # Remove • ** and **
                elif ': ' in line and current_contact:
                    # Contact detail
                    key, value = line.split(': ', 1)
                    current_contact[key.strip()] = value.strip()

            # Check last contact
            if current_contact and self._contact_matches_query(current_contact, query_lower):
                matching_contacts.append(current_contact)

            if not matching_contacts:
                return create_tool_response(f"🔍 No contacts found matching '{query}'")

            response_text = f"🔍 Found {len(matching_contacts)} contacts matching '{query}':\n\n"

            for contact in matching_contacts:
                response_text += f"• **{contact.get('name', 'Unknown')}**\n"
                for key, value in contact.items():
                    if key != 'name':
                        response_text += f"  {key}: {value}\n"
                response_text += "\n"

            return create_tool_response(response_text)

        except Exception as e:
            return create_error_response(f"Error searching contacts: {e}")

    def _format_contact_name(self, contact: ContactInfo) -> str:
        """Format a contact's display name.

        Args:
            contact: Contact information

        Returns:
            Formatted display name
        """
        if contact.first_name and contact.last_name:
            return f"{contact.first_name} {contact.last_name}"
        elif contact.first_name:
            return contact.first_name
        elif contact.last_name:
            return contact.last_name
        elif contact.username:
            return f"@{contact.username}"
        else:
            return f"User {contact.id}"

    def _contact_matches_query(self, contact: Dict[str, str], query: str) -> bool:
        """Check if a contact matches the search query.

        Args:
            contact: Contact information dict
            query: Lowercase search query

        Returns:
            True if contact matches
        """
        # Search in name
        name = contact.get('name', '').lower()
        if query in name:
            return True

        # Search in username
        username = contact.get('Username', '').lower().lstrip('@')
        if query in username:
            return True

        # Search in phone (partial match)
        phone = contact.get('Phone', '').replace(' ', '').replace('-', '')
        if query in phone:
            return True

        return False