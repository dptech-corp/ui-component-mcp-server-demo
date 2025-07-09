"""Plan component MCP tools."""

import os
import time
import uuid
from typing import Optional

from fastmcp import FastMCP

from ..redis_client import RedisClient

def register_plan_tools(mcp: FastMCP, redis_client: RedisClient):
    """Register plan-related MCP tools."""
    
    @mcp.tool()
    async def add_plan(title: str, description: str = "") -> dict:
        """添加新的 plan 项
        
        Args:
            title: Plan 标题
            description: Plan 描述 (可选)
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "add",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "data": {
                    "title": title,
                    "description": description
                }
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        return {"success": True, "message": f"Plan '{title}' added successfully"}
    
    @mcp.tool()
    async def delete_plan(plan_id: str) -> dict:
        """删除指定的 plan 项
        
        Args:
            plan_id: Plan 项的 ID
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "delete",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "planId": plan_id
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        return {"success": True, "message": f"Plan {plan_id} deleted successfully"}
    
    @mcp.tool()
    async def update_plan(
        plan_id: str, 
        title: str = "", 
        description: str = ""
    ) -> dict:
        """更新 plan 项内容
        
        Args:
            plan_id: Plan 项的 ID
            title: 新的标题 (可选)
            description: 新的描述 (可选)
            
        Returns:
            操作结果
        """
        data = {}
        if title and title.strip():
            data["title"] = title
        if description and description.strip():
            data["description"] = description
            
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "update",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "planId": plan_id,
                "data": data
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        return {"success": True, "message": f"Plan {plan_id} updated successfully"}
    
    @mcp.tool()
    async def toggle_plan(plan_id: str) -> dict:
        """切换 plan 完成状态
        
        Args:
            plan_id: Plan 项的 ID
            
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "toggle",
                "session_id": os.getenv("SESSION_ID", "default_session"),
                "planId": plan_id
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        return {"success": True, "message": f"Plan {plan_id} status toggled successfully"}
    
    @mcp.tool()
    async def list_plan() -> dict:
        """获取所有 plan 项列表
        
        Returns:
            包含所有 plan 项的列表
        """
        import httpx
        
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "list",
                "session_id": os.getenv("SESSION_ID", "default_session")
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://backend:8000/api/todos")
                response.raise_for_status()
                plans_data = response.json()
                
                return {
                    "success": True,
                    "plans": plans_data,
                    "count": len(plans_data)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get plans: {str(e)}",
                "plans": []
            }
    
    @mcp.tool()
    async def clear_plan() -> dict:
        """清除所有 plan 项
        
        Returns:
            操作结果
        """
        message = {
            "id": str(uuid.uuid4()),
            "type": "plan_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "plan_component",
            "component": "plan",
            "payload": {
                "action": "clear",
                "session_id": os.getenv("SESSION_ID", "default_session")
            }
        }
        
        await redis_client.publish_message("plan:actions", message)
        return {"success": True, "message": "All plans cleared successfully"}
