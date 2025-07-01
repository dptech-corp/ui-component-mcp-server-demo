from fastapi import APIRouter, HTTPException
from typing import List
from ..models.approval import Approval, ApprovalRequest, ApprovalResponse
from ..services.approval_service import approval_service

router = APIRouter()

@router.get("/approvals", response_model=List[Approval])
async def get_approvals():
    """Get all approval requests."""
    try:
        approvals = await approval_service.get_all_approvals()
        return approvals
    except Exception as e:
        print(f"Error getting approvals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approvals/{approval_id}", response_model=Approval)
async def get_approval(approval_id: str):
    """Get a specific approval request."""
    approval = await approval_service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval

@router.post("/approvals/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_request(approval_id: str):
    """Approve an approval request."""
    try:
        from ..main import sse_service
        
        # Update approval status in the database
        approval = await approval_service.update_approval_status(approval_id, "approved", "Request approved by human")
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        # Send SSE event for real-time updates
        await sse_service.send_event("approval_updated", {
            "approval": approval.dict(),
            "action": "approved"
        })
        
        return ApprovalResponse(
            id=approval.id,
            status=approval.status,
            result=approval.result
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error approving request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_request(approval_id: str):
    """Reject an approval request."""
    try:
        from ..main import sse_service
        
        # Update approval status in the database
        approval = await approval_service.update_approval_status(approval_id, "rejected", "Request rejected by human")
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        # Send SSE event for real-time updates
        await sse_service.send_event("approval_updated", {
            "approval": approval.dict(),
            "action": "rejected"
        })
        
        return ApprovalResponse(
            id=approval.id,
            status=approval.status,
            result=approval.result
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error rejecting request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
