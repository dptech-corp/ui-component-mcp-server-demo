from pydantic import BaseModel
from typing import Optional

class Approval(BaseModel):
    id: str
    session_id: str
    function_call_id: str
    description: str
    status: str = "pending"  # pending, approved, rejected
    created_at: int
    updated_at: int
    result: Optional[str] = None

class ApprovalRequest(BaseModel):
    session_id: str
    function_call_id: str
    description: str

class ApprovalResponse(BaseModel):
    id: str
    status: str
    result: Optional[str] = None
