"""Approval MCP tools."""

import time
import uuid
from typing import Optional

from fastmcp import FastMCP

from ..redis_client import RedisClient


def register_approval_tools(mcp: FastMCP, redis_client: RedisClient):
    """Register approval-related MCP tools."""
    
    @mcp.tool()
    async def wait_for_approval(
        description: str,
        session_id: str = "default",
        function_call_id: Optional[str] = None
    ) -> dict:
        """Request user approval before proceeding with an action
        
        Args:
            description: Description of the action requiring approval
            session_id: Session ID for tracking the approval request
            function_call_id: Optional function call ID for tracking
            
        Returns:
            Approval request result with pending status
        """
        if not function_call_id:
            function_call_id = str(uuid.uuid4())
            
        message = {
            "id": str(uuid.uuid4()),
            "type": "approval_request",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "approval_component",
            "component": "approval",
            "payload": {
                "session_id": session_id,
                "function_call_id": function_call_id,
                "description": description
            }
        }
        
        await redis_client.publish_message("approval:requests", message)
        
        return {
            "success": True,
            "status": "pending",
            "message": f"Approval request submitted: {description}",
            "function_call_id": function_call_id,
            "session_id": session_id
        }
