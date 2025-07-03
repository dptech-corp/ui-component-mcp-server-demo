"""
MCP Server for UI Component Demo

This server provides MCP tools for controlling UI components through Redis messaging.
"""

import os
from fastmcp import FastMCP
from mcp.server.session import ServerSession
from approval_tools import register_approval_tools

old_received_request = ServerSession._received_request

async def _received_request_wrapper(self, *args, **kwargs):
    try:
        return await old_received_request(self, *args, **kwargs)
    except RuntimeError as e:
        if "Received request before initialization was complete" in str(e):
            print(f"WARNING: Ignoring initialization error: {e}")
            return
        raise

ServerSession._received_request = _received_request_wrapper


def main():
    """Main entry point for the MCP server."""

    # TODO P1 改造成 google adk mcp toolset 来使用 context, long running 等
    port = int(os.getenv("MCP_PORT", "8001"))
    
    mcp = FastMCP("ui-component-demo")
    
    register_approval_tools(mcp)
    
    print(f"Starting MCP server on port {port} with SSE transport")
    
    mcp.run(transport="sse", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
