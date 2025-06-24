"""Approval API router."""

from typing import List
from fastapi import APIRouter, HTTPException

from ..models.approval import Approval, ApprovalUpdate, ApprovalResponse
from ..services.approval_service import ApprovalService

router = APIRouter()
approval_service = ApprovalService()


@router.get("/approvals", response_model=List[Approval])
async def get_approvals():
    """Get all approval requests."""
    try:
        approvals = await approval_service.get_all_approvals()
        return approvals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approvals: {str(e)}")


@router.get("/approvals/{approval_id}", response_model=Approval)
async def get_approval(approval_id: str):
    """Get a specific approval request."""
    try:
        approval = await approval_service.get_approval(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        return approval
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approval: {str(e)}")


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_request(approval_id: str):
    """Approve an approval request."""
    try:
        update_data = ApprovalUpdate(status="approved")
        approval = await approval_service.update_approval(approval_id, update_data)
        
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../../mcp-server/src'))
            from tools.approval_tools import update_approval_result
            await update_approval_result(approval.function_call_id, "approved", "Request approved by human")
        except Exception as mcp_error:
            print(f"Failed to update MCP tool status: {str(mcp_error)}")
        
        from ..main import sse_service
        await sse_service.send_event("approval_updated", {
            "approval": approval.dict(),
            "action": "approved"
        })
        
        return ApprovalResponse(
            success=True,
            message="Approval request approved successfully",
            approval=approval
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve request: {str(e)}")


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_request(approval_id: str):
    """Reject an approval request."""
    try:
        update_data = ApprovalUpdate(status="rejected")
        approval = await approval_service.update_approval(approval_id, update_data)
        
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../../mcp-server/src'))
            from tools.approval_tools import update_approval_result
            await update_approval_result(approval.function_call_id, "rejected", "Request rejected by human")
        except Exception as mcp_error:
            print(f"Failed to update MCP tool status: {str(mcp_error)}")
        
        from ..main import sse_service
        await sse_service.send_event("approval_updated", {
            "approval": approval.dict(),
            "action": "rejected"
        })
        
        return ApprovalResponse(
            success=True,
            message="Approval request rejected successfully",
            approval=approval
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject request: {str(e)}")
