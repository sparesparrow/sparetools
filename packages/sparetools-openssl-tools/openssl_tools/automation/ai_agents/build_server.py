#!/usr/bin/env python3
"""
OpenSSL Build MCP Server - Production Implementation
Integrates with existing working build system via MCP protocol
"""

import asyncio
import subprocess
import os
import sys
import json
from pathlib import Path

# MCP Server imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, CallToolResult
except ImportError:
    print("❌ MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
server = Server("openssl-build")

# Get workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
os.chdir(WORKSPACE_ROOT)

@server.list_tools()
async def handle_list_tools():
    """List available tools for OpenSSL build operations"""
    return [
        Tool(
            name="build_all_components",
            description="Execute the working build-all-components.sh script",
            inputSchema={
                "type": "object",
                "properties": {
                    "clean": {
                        "type": "boolean",
                        "default": False,
                        "description": "Clean Conan cache before building"
                    }
                }
            }
        ),
        Tool(
            name="check_conan_cache",
            description="Show Conan cache status for OpenSSL components",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_build_status",
            description="Get recent build status from database",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of recent builds to show"
                    }
                }
            }
        ),
        Tool(
            name="build_single_component",
            description="Build a single OpenSSL component",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["crypto", "ssl", "tools"],
                        "description": "Component to build"
                    },
                    "profile": {
                        "type": "string",
                        "default": "Release",
                        "description": "Build profile (Release/Debug)"
                    }
                },
                "required": ["component"]
            }
        ),
        Tool(
            name="upload_to_registries",
            description="Upload packages to configured registries",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution requests"""
    
    try:
        if name == "build_all_components":
            return await build_all_components(arguments.get("clean", False))
            
        elif name == "check_conan_cache":
            return await check_conan_cache()
            
        elif name == "get_build_status":
            return await get_build_status(arguments.get("limit", 5))
            
        elif name == "build_single_component":
            component = arguments["component"]
            profile = arguments.get("profile", "Release")
            return await build_single_component(component, profile)
            
        elif name == "upload_to_registries":
            return await upload_to_registries()
            
        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error executing {name}: {str(e)}")]

async def build_all_components(clean: bool = False) -> list[TextContent]:
    """Execute the existing working build script"""
    
    output = "🔨 Building All OpenSSL Components\n"
    output += "=" * 50 + "\n"
    
    try:
        # Clean cache if requested
        if clean:
            output += "🧹 Cleaning Conan cache...\n"
            clean_result = subprocess.run(
                ["conan", "remove", "openssl-*", "-f"],
                capture_output=True, text=True
            )
            output += f"Cache cleaned: {clean_result.returncode == 0}\n\n"
        
        # Execute existing working script
        output += "🚀 Executing build-all-components.sh...\n"
        result = subprocess.run(
            ["./scripts/build/build-all-components.sh"],
            capture_output=True, text=True, timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            output += "✅ Build completed successfully!\n\n"
            output += "📊 Build Output:\n"
            output += result.stdout[-1000:]  # Last 1000 chars
        else:
            output += "❌ Build failed!\n\n"
            output += "🔍 Error Output:\n"
            output += result.stderr[-1000:]  # Last 1000 chars
            
    except subprocess.TimeoutExpired:
        output += "⏰ Build timed out after 10 minutes\n"
    except Exception as e:
        output += f"💥 Unexpected error: {str(e)}\n"
    
    return [TextContent(type="text", text=output)]

async def check_conan_cache() -> list[TextContent]:
    """Check Conan cache status for OpenSSL packages"""
    
    output = "📦 Conan Cache Status\n"
    output += "=" * 30 + "\n"
    
    components = ["openssl-crypto", "openssl-ssl", "openssl-tools"]
    
    for component in components:
        try:
            # Check if package exists in cache
            result = subprocess.run(
                ["conan", "cache", "path", f"{component}/3.2.0"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                output += f"✅ {component}: Cached\n"
                output += f"   Path: {result.stdout.strip()}\n"
            else:
                output += f"❌ {component}: Not in cache\n"
                
        except Exception as e:
            output += f"⚠️  {component}: Error checking - {str(e)}\n"
    
    return [TextContent(type="text", text=output)]

async def get_build_status(limit: int) -> list[TextContent]:
    """Get build status from PostgreSQL database"""
    
    output = f"📊 Recent Build Status (Last {limit})\n"
    output += "=" * 40 + "\n"
    
    try:
        # Use existing database connection via Docker
        result = subprocess.run([
            "docker", "exec", "openssl-build-db", "psql",
            "-U", "openssl_admin", "-d", "openssl_builds",
            "-c", f"""
                SELECT 
                    c.name as component,
                    b.status,
                    b.build_duration_seconds as duration,
                    b.build_date
                FROM builds b
                JOIN components c ON b.component_id = c.id
                ORDER BY b.build_date DESC
                LIMIT {limit};
            """
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            output += "Database connection: ✅\n\n"
            output += result.stdout
        else:
            output += "❌ Database connection failed\n"
            output += "💡 Make sure PostgreSQL container is running\n"
            output += "   Command: docker-compose -f docker-compose.postgres.yml up -d\n"
            
    except Exception as e:
        output += f"💥 Database error: {str(e)}\n"
    
    return [TextContent(type="text", text=output)]

async def build_single_component(component: str, profile: str) -> list[TextContent]:
    """Build a single OpenSSL component"""
    
    output = f"🔨 Building OpenSSL {component.title()} Component\n"
    output += "=" * 50 + "\n"
    
    try:
        component_dir = f"openssl-{component}"
        if not os.path.exists(component_dir):
            return [TextContent(type="text", text=f"❌ Component directory {component_dir} not found")]
        
        # Execute Conan build
        cmd = [
            "conan", "create", f"{component_dir}/",
            "--profile:build=default", "--profile:host=default",
            f"-s build_type={profile}",
            "-o", "*:shared=True",
            "--build=missing"
        ]
        
        output += f"🚀 Executing: {' '.join(cmd)}\n\n"
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            output += f"✅ {component} build completed successfully!\n\n"
            output += "📝 Build Summary:\n"
            # Extract key information from stdout
            lines = result.stdout.split('\n')
            for line in lines[-20:]:  # Last 20 lines
                if any(word in line.lower() for word in ['package', 'created', 'exported', 'success']):
                    output += f"   {line}\n"
        else:
            output += f"❌ {component} build failed!\n\n"
            output += "🔍 Error Details:\n"
            output += result.stderr[-500:]  # Last 500 chars
            
    except subprocess.TimeoutExpired:
        output += f"⏰ {component} build timed out after 5 minutes\n"
    except Exception as e:
        output += f"💥 Build error: {str(e)}\n"
    
    return [TextContent(type="text", text=output)]

async def upload_to_registries() -> list[TextContent]:
    """Execute registry upload script"""
    
    output = "📤 Uploading to Registries\n"
    output += "=" * 30 + "\n"
    
    try:
        # Execute existing upload script
        result = subprocess.run(
            ["./scripts/upload/upload-to-registries.sh"],
            capture_output=True, text=True, timeout=300
        )
        
        if result.returncode == 0:
            output += "✅ Upload completed successfully!\n\n"
            output += "📋 Upload Summary:\n"
            output += result.stdout[-800:]  # Last 800 chars
        else:
            output += "❌ Upload failed!\n\n"
            output += "🔍 Error Details:\n"
            output += result.stderr[-500:]
            
    except subprocess.TimeoutExpired:
        output += "⏰ Upload timed out after 5 minutes\n"
    except Exception as e:
        output += f"💥 Upload error: {str(e)}\n"
    
    return [TextContent(type="text", text=output)]

async def main():
    """Main entry point for MCP server"""
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="openssl-build",
                server_version="1.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
