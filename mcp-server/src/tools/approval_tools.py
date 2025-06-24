"""Approval MCP tools."""

import time
import uuid
from typing import Optional, Union

from fastmcp import FastMCP

from ..redis_client import RedisClient

_pending_approvals = {}


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
            Approval request result with pending status following Google ADK pattern
        """
        if not function_call_id:
            function_call_id = str(uuid.uuid4())
        
        ticket_id = f"approval-ticket-{function_call_id}"
            
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
                "description": description,
                "ticket_id": ticket_id
            }
        }
        
        _pending_approvals[ticket_id] = {
            "status": "pending",
            "description": description,
            "session_id": session_id,
            "function_call_id": function_call_id,
            "created_at": int(time.time() * 1000)
        }
        
        await redis_client.publish_message("approval:requests", message)
        
        return {
            "status": "pending",
            "ticketId": ticket_id,
            "message": f"Approval request submitted: {description}",
            "function_call_id": function_call_id,
            "session_id": session_id
        }
    
    @mcp.tool()
    async def get_approval_status(ticket_id: str) -> dict:
        """Get the current status of an approval request"""
        if ticket_id in _pending_approvals:
            return _pending_approvals[ticket_id]
        return {"error": f"Ticket {ticket_id} not found"}


async def update_approval_result(ticket_id: str, status: str, result: Union[str, None] = None):
    """Update approval result - called by backend when user approves/rejects"""
    if ticket_id in _pending_approvals:
        _pending_approvals[ticket_id]["status"] = status
        _pending_approvals[ticket_id]["updated_at"] = int(time.time() * 1000)
        
        if status == "approved":
            _pending_approvals[ticket_id]["result"] = result or "Request approved by human"
        elif status == "rejected":
            _pending_approvals[ticket_id]["result"] = result or "Request rejected by human"
        
        return _pending_approvals[ticket_id]
    return {"error": f"Ticket {ticket_id} not found"}
