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


def main():
    """Main entry point for the MCP server."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    port = int(os.getenv("MCP_PORT", "8001"))
    
    mcp = FastMCP("ui-component-demo")
    
    redis_client = RedisClient(redis_url)
    register_todo_tools(mcp, redis_client)
    
    print(f"Starting MCP server on port {port} with SSE transport")
    
    mcp.run(transport="sse", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
