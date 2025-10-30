#!/usr/bin/env python3
"""MCP Server for OpenSSL Database Operations"""

import asyncio
import json
import os
import sys
from typing import Any, Sequence

import psycopg2
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent
)

class DatabaseMCPServer:
    def __init__(self):
        self.server = Server("openssl-database")
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', 5432),
            'database': os.getenv('POSTGRES_DB', 'openssl_builds'),
            'user': os.getenv('POSTGRES_USER', 'openssl_admin'),
            'password': os.getenv('POSTGRES_PASSWORD', 'openssl_secure_pass')
        }
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_build_status",
                    description="Get recent build status from database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 10}
                        }
                    }
                ),
                Tool(
                    name="get_component_history", 
                    description="Get build history for specific component",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component": {"type": "string"},
                            "limit": {"type": "integer", "default": 20}
                        },
                        "required": ["component"]
                    }
                ),
                Tool(
                    name="get_build_metrics",
                    description="Get build performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {"type": "integer", "default": 7}
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "get_build_status":
                return await self.get_build_status(arguments.get("limit", 10))
            elif name == "get_component_history":
                return await self.get_component_history(
                    arguments["component"], 
                    arguments.get("limit", 20)
                )
            elif name == "get_build_metrics":
                return await self.get_build_metrics(arguments.get("days", 7))
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def get_build_status(self, limit: int) -> list[TextContent]:
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.name, b.status, b.build_duration_seconds, b.build_date
                        FROM builds b
                        JOIN components c ON b.component_id = c.id
                        ORDER BY b.build_date DESC
                        LIMIT %s
                    """, (limit,))
                    results = cur.fetchall()
                    
            status_text = "Recent Build Status:\n"
            for name, status, duration, date in results:
                status_text += f"• {name}: {status} ({duration}s) at {date}\n"
                
            return [TextContent(type="text", text=status_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Database error: {e}")]
    
    async def get_component_history(self, component: str, limit: int) -> list[TextContent]:
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT b.status, b.build_duration_seconds, b.build_date, b.platform, b.profile
                        FROM builds b
                        JOIN components c ON b.component_id = c.id
                        WHERE c.name = %s
                        ORDER BY b.build_date DESC
                        LIMIT %s
                    """, (component, limit))
                    results = cur.fetchall()
                    
            history_text = f"Build History for {component}:\n"
            for status, duration, date, platform, profile in results:
                history_text += f"• {date}: {status} ({duration}s) - {platform}/{profile}\n"
                
            return [TextContent(type="text", text=history_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Database error: {e}")]
    
    async def get_build_metrics(self, days: int) -> list[TextContent]:
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total_builds,
                            COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
                            AVG(build_duration_seconds) as avg_duration
                        FROM builds
                        WHERE build_date >= NOW() - INTERVAL '%s days'
                    """, (days,))
                    total, successful, avg_duration = cur.fetchone()
                    
            success_rate = (successful / total * 100) if total > 0 else 0
            metrics_text = f"Build Metrics (Last {days} days):\n"
            metrics_text += f"• Total builds: {total}\n"
            metrics_text += f"• Successful: {successful}\n"
            metrics_text += f"• Success rate: {success_rate:.1f}%\n"
            metrics_text += f"• Average duration: {avg_duration:.1f}s\n"
                
            return [TextContent(type="text", text=metrics_text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Database error: {e}")]

async def main():
    server_instance = DatabaseMCPServer()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, write_stream, InitializationOptions(
                server_name="openssl-database",
                server_version="1.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
