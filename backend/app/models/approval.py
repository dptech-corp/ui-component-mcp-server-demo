"""Approval data models."""

import time
from typing import Optional
from pydantic import BaseModel


class ApprovalBase(BaseModel):
    """Base approval model."""
    session_id: str
    function_call_id: str
    description: str
    status: str = "pending"


class ApprovalCreate(ApprovalBase):
    """Approval creation model."""
    pass


class ApprovalUpdate(BaseModel):
    """Approval update model."""
    status: str


class Approval(ApprovalBase):
    """Approval model."""
    id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class ApprovalResponse(BaseModel):
    """Approval response model."""
    success: bool
    message: str
    approval: Optional[Approval] = None
