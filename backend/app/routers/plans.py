from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
import time
import uuid

from ..models.plan import Plan, PlanRequest, PlanResponse, PlanUpdate
from ..services.plan_service import plan_service

router = APIRouter()


@router.get("/plans", response_model=List[Plan])
async def get_plans(request: Request, session_id: Optional[str] = None):
    """Get all plans, optionally filtered by session_id."""
    try:
        plans = await plan_service.get_all_plans(session_id=session_id)
        return plans
    except Exception as e:
        print(f"Error getting plans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(plan_id: str):
    """Get a specific plan."""
    plan = await plan_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/plans", response_model=Plan)
async def create_plan(plan_data: PlanRequest, request: Request):
    """Create a new plan."""
    try:
        sse_service = request.app.state.sse_service
        
        plan = Plan(
            id=str(uuid.uuid4()),
            session_id=plan_data.session_id,
            title=plan_data.title,
            description=plan_data.description,
            status="active",
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000)
        )
        
        created_plan = await plan_service.create_plan(plan)
        
        await sse_service.send_event("plan_created", {
            "plan": created_plan.dict(),
            "action": "created"
        })
        
        return created_plan
    except Exception as e:
        print(f"Error creating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/plans/{plan_id}", response_model=Plan)
async def update_plan(plan_id: str, plan_data: PlanUpdate, request: Request):
    """Update a plan."""
    try:
        sse_service = request.app.state.sse_service
        
        update_data = {k: v for k, v in plan_data.dict().items() if v is not None}
        
        plan = await plan_service.update_plan(plan_id, **update_data)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        await sse_service.send_event("plan_updated", {
            "plan": plan.dict(),
            "action": "updated"
        })
        
        return plan
    except Exception as e:
        print(f"Error updating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, request: Request):
    """Delete a plan."""
    try:
        sse_service = request.app.state.sse_service
        
        success = await plan_service.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        await sse_service.send_event("plan_deleted", {"planId": plan_id})
        
        return {"message": "Plan deleted successfully"}
    except Exception as e:
        print(f"Error deleting plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
