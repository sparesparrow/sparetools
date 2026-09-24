"""Entry point: python -m sparetools.mcp_servers.orchestrator"""

from .server import create_server

if __name__ == "__main__":
    server = create_server()
    server.run()
