from pydantic import BaseModel
from typing import Optional


class PlanBase(BaseModel):
    session_id: str
    title: str
    description: Optional[str] = ""
    status: str = "active"


class Plan(PlanBase):
    id: str
    created_at: int
    updated_at: int
    
    class Config:
        from_attributes = True


class PlanRequest(BaseModel):
    session_id: str
    title: str
    description: Optional[str] = ""


class PlanResponse(BaseModel):
    id: str
    session_id: str
    title: str
    description: Optional[str] = ""
    status: str
    created_at: int
    updated_at: int


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
