import asyncio
import os
import json
import uuid
import redis.asyncio as redis
from typing import Dict, Any
from ..redis_client import RedisClient

_pending_approvals: Dict[str, Dict[str, Any]] = {}

async def wait_for_approval(description: str, redis_client: RedisClient) -> Dict[str, Any]:
    """
    Request human approval for an action.
    
    This tool follows the Google ADK LongRunningFunctionTool pattern:
    1. Returns immediately with status: "pending" and a ticketId
    2. External process (approval service) updates the result
    3. Agent can check status using the ticketId
    
    Args:
        description: Description of the action requiring approval
        
    Returns:
        Dict with status and ticketId for long-running job pattern
    """
    ticket_id = f"approval-{uuid.uuid4().hex[:8]}"
    
    _pending_approvals[ticket_id] = {
        "status": "pending",
        "description": description,
        "result": None,
        "ticket_id": ticket_id
    }
    
    try:
        approval_data = {
            "id": ticket_id,
            "session_id": "default_session",
            "function_call_id": ticket_id,
            "description": description,
            "status": "pending"
        }
        
        # 使用 RedisClient 的 publish_message 方法发布消息
        # 格式化消息以符合后端期望的格式
        message = {
            "type": "approval_request",
            "component": "approval",
            "payload": approval_data
        }
        
        await redis_client.publish_message("approval:requests", message)
        
        print(f"Published approval request: {ticket_id}")
        
    except Exception as e:
        print(f"Failed to publish approval request: {str(e)}")
    
    return {
        "status": "pending",
        "ticketId": ticket_id,
        "message": f"Approval request submitted. Waiting for human decision on: {description}"
    }

async def check_approval_status(ticket_id: str) -> Dict[str, Any]:
    """
    Check the status of a pending approval request.
    
    Args:
        ticket_id: The ticket ID returned by wait_for_approval
        
    Returns:
        Dict with current status and result if completed
    """
    if ticket_id not in _pending_approvals:
        return {
            "status": "not_found",
            "message": f"Approval request {ticket_id} not found"
        }
    
    approval = _pending_approvals[ticket_id]
    return {
        "status": approval["status"],
        "ticketId": ticket_id,
        "result": approval.get("result"),
        "description": approval.get("description")
    }

async def update_approval_result(ticket_id: str, status: str, result: str) -> bool:
    """
    Update the result of a pending approval (called by approval service).
    
    Args:
        ticket_id: The ticket ID of the approval request
        status: New status ("approved" or "rejected")
        result: Result message
        
    Returns:
        True if update was successful, False otherwise
    """
    if ticket_id not in _pending_approvals:
        print(f"Approval {ticket_id} not found in pending approvals")
        return False
    
    _pending_approvals[ticket_id].update({
        "status": status,
        "result": result
    })
    
    print(f"Updated approval {ticket_id}: {status} - {result}")
    return True


def register_approval_tools(mcp, redis_client: RedisClient):
    """Register approval tools with the MCP server."""
    
    @mcp.tool()
    async def ask_for_approval(description: str) -> dict:
        """Request human approval before proceeding with an action"""
        return await wait_for_approval(description, redis_client)
   
    print("Registered approval tools: ask_for_approval")

