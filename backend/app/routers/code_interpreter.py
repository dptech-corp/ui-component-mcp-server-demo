"""Code interpreter API router."""

from typing import List
from fastapi import APIRouter, HTTPException, Request

from ..models.code_interpreter import CodeInterpreterState, CodeInterpreterCreateRequest, CodeInterpreterUpdateRequest

router = APIRouter()

@router.get("/code-interpreter/states", response_model=List[CodeInterpreterState])
async def get_all_states(request: Request):
    """Get all code interpreter states."""
    code_interpreter_service = request.app.state.code_interpreter_service
    states = await code_interpreter_service.get_all_states()
    return states

@router.get("/code-interpreter/states/{state_id}", response_model=CodeInterpreterState)
async def get_notebook_state(state_id: str, request: Request):
    """Get a specific code interpreter state."""
    code_interpreter_service = request.app.state.code_interpreter_service
    state = await code_interpreter_service.get_notebook_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state

@router.post("/code-interpreter/states", response_model=CodeInterpreterState)
async def create_python_notebook(state_data: CodeInterpreterCreateRequest, request: Request):
    """Create a new code interpreter state."""
    code_interpreter_service = request.app.state.code_interpreter_service
    sse_service = request.app.state.sse_service
    
    state = await code_interpreter_service.create_python_notebook(
        code=state_data.code,
        description=state_data.description
    )
    
    await sse_service.send_event("code_interpreter_state_created", {"state": state.dict()})
    
    return state

@router.put("/code-interpreter/states/{state_id}", response_model=CodeInterpreterState)
async def update_state(state_id: str, state_data: CodeInterpreterUpdateRequest, request: Request):
    """Update a code interpreter state."""
    code_interpreter_service = request.app.state.code_interpreter_service
    sse_service = request.app.state.sse_service
    
    update_data = {k: v for k, v in state_data.dict().items() if v is not None}
    
    state = await code_interpreter_service.update_state(state_id, **update_data)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    await sse_service.send_event("code_interpreter_state_updated", {"state": state.dict()})
    
    return state

@router.delete("/code-interpreter/states/{state_id}")
async def delete_state(state_id: str, request: Request):
    """Delete a code interpreter state."""
    code_interpreter_service = request.app.state.code_interpreter_service
    sse_service = request.app.state.sse_service
    
    success = await code_interpreter_service.delete_state(state_id)
    if not success:
        raise HTTPException(status_code=404, detail="State not found")
    
    await sse_service.send_event("code_interpreter_state_deleted", {"stateId": state_id})
    
    return {"message": "Code interpreter state deleted successfully"}
