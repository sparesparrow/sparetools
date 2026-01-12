# MCP Transport: Telegram

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-API-blue.svg)](https://core.telegram.org/)

A Model Context Protocol (MCP) transport implementation that enables bi-directional communication between [MIA (Lean IoT Assistant)](https://github.com/sparrowaitech/mia) and Telegram users. This transport allows MIA to receive messages from Telegram chats and respond directly within the same conversation threads.

## Features

- **Bi-directional Messaging**: Send and receive messages between MIA and Telegram
- **Media Support**: Download and process photos, documents, audio, and video files
- **Contact Management**: Access and manage Telegram contacts
- **Context Preservation**: Maintain conversation context across sessions and threads
- **Rate Limiting**: Built-in protection against API rate limits
- **Error Handling**: Comprehensive error handling and recovery mechanisms
- **Logging**: Structured logging with correlation IDs
- **Docker Support**: Containerized deployment with Docker and Kubernetes manifests

## Architecture

```
Telegram User ↔ Telegram API ↔ MCP Transport ↔ MIA Orchestrator ↔ MCP Tools
     ↓              ↓              ↓              ↓              ↓
Messages    Message Polling/   Telegram Client   Enhanced NLP   Hardware Control
Media       Webhook Receiver   Media Handler     Intent Routing  Audio Control
Contacts    Message Queue      Contact Tools     Context Mgmt   Home Automation
```

## Quick Start

### Prerequisites

1. **Telegram API Credentials**: Obtain from [my.telegram.org](https://my.telegram.org/)
   - `api_id`: Your Telegram API ID
   - `api_hash`: Your Telegram API hash

2. **Bot Token**: Create a bot via [@BotFather](https://t.me/botfather)
   - Required for bot functionality
   - Optional for user account access

3. **Python 3.9+**: Required for running the transport

### Installation

1. **Clone and navigate to the package**:
   ```bash
   git clone https://github.com/sparrowaitech/ai-mcp-monorepo.git
   cd ai-mcp-monorepo/packages/mcp-transport-telegram
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   export TELEGRAM_API_ID="your_api_id"
   export TELEGRAM_API_HASH="your_api_hash"
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   # Optional: export TELEGRAM_PHONE="+1234567890"
   ```

4. **Run the MCP server**:
   ```bash
   python -m mcp_transport_telegram
   ```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_API_ID` | Yes | Telegram API ID from my.telegram.org |
| `TELEGRAM_API_HASH` | Yes | Telegram API hash from my.telegram.org |
| `TELEGRAM_BOT_TOKEN` | Yes* | Bot token from @BotFather (*required for bot mode) |
| `TELEGRAM_PHONE` | No | Phone number for user authentication |
| `TELEGRAM_SESSION_NAME` | No | Telethon session name (default: mcp_transport_telegram) |
| `TELEGRAM_POLLING_INTERVAL` | No | Message polling interval in seconds (default: 30) |
| `TELEGRAM_MAX_MESSAGE_AGE` | No | Maximum message age to process in seconds (default: 3600) |
| `TELEGRAM_RATE_LIMIT_PER_MINUTE` | No | API rate limit per minute (default: 30) |

### Configuration Files

- `config/telegram_config.yaml`: Telegram API configuration template
- `config/mcp_telegram_integration.yaml`: MIA integration settings
- `config/telegram_integration.yaml`: MIA integration configuration

## MCP Tools

The transport provides the following MCP tools:

### Chat Management
- **`list_chats`**: Enumerate available Telegram dialogs
- **`get_messages`**: Fetch messages from specific chats
- **`send_message`**: Send replies to Telegram chats
- **`edit_message`**: Modify sent messages

### Media Handling
- **`get_media`**: Download media attachments from messages

### Contact Management
- **`get_contacts`**: Retrieve Telegram contact information

## MCP Resources

The transport exposes the following MCP resources:

- **Chat Resources**: `telegram://chat/{chat_id}` - Chat metadata and information
- **Message Resources**: `telegram://message/{chat_id}/{message_id}` - Individual message data
- **Media Resources**: `telegram://media/{chat_id}/{message_id}` - Media attachment information

## MIA Integration

The Telegram transport integrates with MIA through the enhanced orchestrator:

1. **Service Registration**: Automatically registers as an MCP service
2. **Message Routing**: Routes Telegram messages to appropriate MIA prompts
3. **Context Preservation**: Maintains chat and thread context across interactions
4. **Response Formatting**: Formats MIA responses for Telegram display

### Integration Steps

1. **Configure MIA**:
   ```yaml
   # Add to MIA config
   telegram_mcp:
     enabled: true
     transport:
       command: ["python", "-m", "mcp_transport_telegram"]
   ```

2. **Environment Variables**: Set the required Telegram credentials in MIA's environment

3. **Start MIA**: The orchestrator will automatically start the Telegram transport

## Docker Deployment

### Using Docker Compose

1. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Start the service**:
   ```bash
   docker-compose up -d
   ```

### Using Docker Directly

```bash
docker build -t mcp-transport-telegram .
docker run -e TELEGRAM_API_ID=... -e TELEGRAM_API_HASH=... mcp-transport-telegram
```

## Kubernetes Deployment

1. **Update secrets**:
   ```bash
   kubectl create secret generic telegram-credentials \
     --from-literal=api-id=YOUR_API_ID \
     --from-literal=api-hash=YOUR_API_HASH \
     --from-literal=bot-token=YOUR_BOT_TOKEN
   ```

2. **Deploy**:
   ```bash
   kubectl apply -f k8s-deployment.yaml
   ```

## Usage Examples

### Basic Message Handling

```python
from mcp_transport_telegram import TelegramMCPServer

# Initialize server
server = TelegramMCPServer(config)

# Send a message
result = await server.call_tool("send_message", {
    "chat_id": "@username",
    "text": "Hello from MIA!"
})

# List chats
chats = await server.call_tool("list_chats", {"limit": 10})
```

### Media Download

```python
# Download media from a message
result = await server.call_tool("get_media", {
    "chat_id": "@chat",
    "message_id": 12345
})
```

### MIA Integration Example

```python
# Telegram user sends: "What devices are offline?"
# MIA processes through orchestrator
# Routes to device monitoring tools
# Responds in Telegram: "Device 3 (ESP32-Living) offline for 15 minutes"
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/

# Run specific test
pytest tests/test_telegram_client.py -v
```

### Project Structure

```
mcp-transport-telegram/
├── src/mcp_transport_telegram/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py              # Configuration management
│   ├── telegram_client.py     # Telegram API wrapper
│   ├── message_handler.py     # Message processing
│   ├── telegram_polling.py    # Polling infrastructure
│   ├── telegram_webhook.py    # Webhook support
│   ├── media_handler.py       # Media utilities
│   ├── media_types.py         # Media type definitions
│   ├── mcp_server.py         # MCP server implementation
│   ├── mcp_types.py           # MCP type definitions
│   ├── exceptions.py          # Custom exceptions
│   ├── logging.py             # Logging utilities
│   ├── tools/                 # MCP tools
│   │   ├── __init__.py
│   │   ├── chat_tools.py
│   │   ├── media_tools.py
│   │   └── contact_tools.py
│   └── resources/             # MCP resources
│       ├── __init__.py
│       ├── chat_resources.py
│       └── media_resources.py
├── tests/                     # Unit tests
├── config/                    # Configuration templates
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Docker Compose setup
├── k8s-deployment.yaml        # Kubernetes manifests
├── pyproject.toml             # Python project config
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Security Considerations

- **API Credentials**: Never commit credentials to version control
- **Rate Limiting**: Built-in protection against API abuse
- **Message Filtering**: Optional content filtering for sensitive deployments
- **Access Control**: Configurable chat/user allowlists and blocklists
- **Encryption**: All communication with Telegram API is encrypted

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Verify API credentials
   - Check network connectivity
   - Ensure correct phone number format (for user auth)

2. **Messages Not Processing**:
   - Check polling interval settings
   - Verify bot permissions in chats
   - Review message age limits

3. **Media Download Errors**:
   - Check file size limits
   - Verify supported media types
   - Ensure sufficient disk space

### Logging

Enable debug logging:
```bash
export PYTHONPATH=src
PYTHONPATH=src python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_transport_telegram.logging import setup_logging
setup_logging('DEBUG')
"
```

### Health Checks

The service provides health check endpoints:
- `GET /health`: Basic health check
- Container health checks are configured in Docker/K8s manifests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [MIA (Lean IoT Assistant)](https://github.com/sparrowaitech/mia)
- [MCP Prompts](https://github.com/sparrowaitech/mcp-prompts)
- [MCP Router](https://github.com/sparrowaitech/mcp-router)
- [TinyMCP](https://github.com/sparrowaitech/tinymcp)

## Support

- **Issues**: [GitHub Issues](https://github.com/sparrowaitech/ai-mcp-monorepo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sparrowaitech/ai-mcp-monorepo/discussions)
- **Telegram**: [@sparrow_ai_tech](https://t.me/sparrow_ai_tech)