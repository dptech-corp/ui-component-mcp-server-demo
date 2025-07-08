"""Todo component MCP tools."""

import os
import time
import uuid
from typing import Optional

from fastmcp import FastMCP

from ..redis_client import RedisClient


def register_todo_tools(mcp: FastMCP, redis_client: RedisClient):
    """Register todo-related MCP tools."""
    
    @mcp.tool()
    async def add_todo(plan_id: str, title: str, description: str = "") -> dict:
        """添加新的 todo 项到指定 plan
        
        Args:
            plan_id: Plan 的 ID
            title: Todo 标题
            description: Todo 描述 (可选)
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "todo_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "todo_component",
            "component": "todo",
            "payload": {
                "action": "add",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "plan_id": plan_id,
                "data": {
                    "title": title,
                    "description": description
                }
            }
        }
        
        await redis_client.publish_message("todo:actions", message)
        return {"success": True, "message": f"Todo '{title}' added to plan {plan_id} successfully"}
    
    @mcp.tool()
    async def toggle_todo(todo_id: str) -> dict:
        """切换 todo 完成状态
        
        Args:
            todo_id: Todo 项的 ID
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "todo_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "todo_component",
            "component": "todo",
            "payload": {
                "action": "toggle",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "todoId": todo_id
            }
        }
        
        await redis_client.publish_message("todo:actions", message)
        return {"success": True, "message": f"Todo {todo_id} status toggled successfully"}
    
    @mcp.tool()
    async def delete_todo(todo_id: str) -> dict:
        """删除 todo 项
        
        Args:
            todo_id: Todo 项的 ID
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "todo_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "todo_component",
            "component": "todo",
            "payload": {
                "action": "delete",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "todoId": todo_id
            }
        }
        
        await redis_client.publish_message("todo:actions", message)
        return {"success": True, "message": f"Todo {todo_id} deleted successfully"}
    
    @mcp.tool()
    async def list_todos(plan_id: Optional[str] = None) -> dict:
        """列出 todos，可选择按 plan 过滤
        
        Args:
            plan_id: Plan 的 ID (可选)
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "todo_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "todo_component",
            "component": "todo",
            "payload": {
                "action": "list",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "plan_id": plan_id
            }
        }
        
        await redis_client.publish_message("todo:actions", message)
        return {"success": True, "message": "Todo list requested successfully"}
    
    print("Registered todo tools: add_todo, toggle_todo, delete_todo, list_todos")
