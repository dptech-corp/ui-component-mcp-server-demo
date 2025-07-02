import uuid
import time
import os
from typing import Dict, Any
from ..redis_client import RedisClient

async def create_file(name: str, path: str, content: str, redis_client: RedisClient) -> Dict[str, Any]:
    """Create a new file."""
    try:
        file_data = {
            "id": str(uuid.uuid4()),
            "session_id": os.getenv("SESSION_ID", "default_session"),
            "name": name,
            "type": "file",
            "path": path,
            "content": content,
            "size": len(content.encode('utf-8')),
            "created_at": int(time.time() * 1000),
            "updated_at": int(time.time() * 1000)
        }
        
        message = {
            "type": "file_action",
            "component": "file-browser",
            "payload": {
                "action": "create",
                "data": file_data
            }
        }
        
        await redis_client.publish_message("file:actions", message)
        
        return {
            "success": True,
            "message": f"File {name} created at {path}",
            "file_id": file_data["id"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create file: {str(e)}"
        }

async def list_files(redis_client: RedisClient) -> Dict[str, Any]:
    """List all files."""
    try:
        message = {
            "type": "file_action",
            "component": "file-browser",
            "payload": {
                "action": "list",
                "data": {}
            }
        }
        
        await redis_client.publish_message("file:actions", message)
        
        return {
            "success": True,
            "message": "File list request sent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list files: {str(e)}"
        }

def register_file_tools(mcp, redis_client: RedisClient):
    """Register file tools with the MCP server."""
    
    @mcp.tool()
    async def create_file_tool(name: str, path: str, content: str) -> dict:
        """Create a new file with the given name, path, and content"""
        return await create_file(name, path, content, redis_client)
    
    @mcp.tool()
    async def list_files_tool() -> dict:
        """List all files in the system"""
        return await list_files(redis_client)
    
    print("Registered file tools: create_file_tool, list_files_tool")
