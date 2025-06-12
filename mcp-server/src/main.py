"""
MCP Server for UI Component Demo

This server provides MCP tools for controlling UI components through Redis messaging.
"""

import asyncio
import json
import os
from typing import Optional

from fastmcp import FastMCP
from redis.asyncio import Redis

from .redis_client import RedisClient
from .tools.todo_tools import register_todo_tools


async def main():
    """Main entry point for the MCP server."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = RedisClient(redis_url)
    await redis_client.connect()
    
    mcp = FastMCP("ui-component-demo")
    
    register_todo_tools(mcp, redis_client)
    
    port = int(os.getenv("MCP_PORT", "8001"))
    print(f"Starting MCP server on port {port}")
    
    try:
        await mcp.run(port=port)
    finally:
        await redis_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
