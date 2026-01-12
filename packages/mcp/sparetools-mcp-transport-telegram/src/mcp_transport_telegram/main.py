"""Main entry point for MCP Transport Telegram."""

import asyncio
import signal
import sys
from typing import Optional

from .config import Config
from .mcp_server import TelegramMCPServer
from .logging import setup_logging, get_logger, set_correlation_id, ErrorReporter
from .exceptions import MCPTelegramError, ConfigurationError


# Global variables for graceful shutdown
shutdown_event = asyncio.Event()
logger = get_logger(__name__)
error_reporter = ErrorReporter(logger)


async def main() -> None:
    """Main entry point for the MCP Transport Telegram server."""
    # Set up correlation ID for this session
    set_correlation_id()

    try:
        logger.info("Starting MCP Transport Telegram server", operation="startup")

        # Load configuration
        config = Config()
        logger.info("Configuration loaded successfully", operation="config_load")

        # Create and start MCP server
        server = TelegramMCPServer(config)
        logger.info("MCP server initialized successfully", operation="server_init")

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown", operation="shutdown")
            shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run server with shutdown handling
        try:
            await asyncio.wait_for(server.run(), timeout=None)
        except asyncio.TimeoutError:
            pass  # This shouldn't happen with timeout=None, but just in case

    except ConfigurationError as e:
        error_reporter.report_error(e, "configuration", level=logger.logger.critical)
        sys.exit(1)
    except MCPTelegramError as e:
        error_reporter.report_error(e, "initialization", level=logger.logger.error)
        sys.exit(1)
    except Exception as e:
        error_reporter.report_error(e, "startup", level=logger.logger.critical)
        sys.exit(1)
    finally:
        logger.info("MCP Transport Telegram server shutdown complete", operation="shutdown")


def cli_main() -> None:
    """CLI entry point."""
    # Set up logging
    setup_logging(
        level="INFO",
        format_type="text"  # Use text format for CLI output
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user", operation="shutdown")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", operation="fatal_error")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()