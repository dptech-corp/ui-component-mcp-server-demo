"""Code interpreter component MCP tools."""

import os
import time
import uuid
from typing import Optional

import httpx
from fastmcp import FastMCP

from ..redis_client import RedisClient

def register_code_interpreter_tools(mcp: FastMCP, redis_client: RedisClient):
    """Register code interpreter-related MCP tools."""
    
    @mcp.tool()
    async def create_python_notebook(code: str = "", description: str = "") -> dict:
        """创建新的代码执行状态
        
        Args:
            code: 要执行的代码 (可选)
            description: 代码描述 (可选)
            
        Returns:
            包含state-id, ticket-id, status和widget URL的操作结果
        """
        token = os.getenv("CODE_INTERPRETER_TOKEN", "1234")
        
        state_id = str(uuid.uuid4())
        ticket_id = f"code-interpreter-{uuid.uuid4().hex[:8]}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://uni-interpreter.mlops.dp.tech/state/{state_id}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "source": code,
                        "description": description
                    }
                )
                response.raise_for_status()
                
                message = {
                    "id": str(uuid.uuid4()),
                    "type": "code_interpreter_action",
                    "timestamp": int(time.time() * 1000),
                    "source": "mcp",
                    "target": "code_interpreter_component",
                    "component": "code_interpreter",
                    "payload": {
                        "action": "create_python_notebook",
                        "data": {
                            "state_id": state_id,
                            "ticket_id": ticket_id,
                            "status": "pending",
                            "code": code,
                            "description": description
                        }
                    }
                }
                
                await redis_client.publish_message("code_interpreter:actions", message)
                
                widget_url = f"https://uni-interpreter.mlops.dp.tech/widget?instance_id={state_id}"
                
                return {
                    "success": True,
                    "state_id": state_id,
                    "ticket_id": ticket_id,
                    "status": "pending",
                    "widget_url": widget_url,
                    "message": f"Code interpreter state created. Please visit {widget_url} to execute the code."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create code interpreter state: {str(e)}",
                "state_id": state_id,
                "ticket_id": ticket_id,
                "status": "error"
            }
    
    @mcp.tool()
    async def get_notebook_state(state_id: str) -> dict:
        """获取代码执行状态
        
        Args:
            state_id: 状态ID
            
        Returns:
            当前状态信息
        """
        token = os.getenv("CODE_INTERPRETER_TOKEN", "1234")
        
        try:
            url = f"https://uni-interpreter.mlops.dp.tech/state/{state_id}"
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
                state_data = response.json()
                
                return {
                    "success": True,
                    "state_id": state_id,
                    "data": state_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get code interpreter state: {str(e)}",
                "state_id": state_id
            }
