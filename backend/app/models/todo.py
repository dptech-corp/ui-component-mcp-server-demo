"""Todo data models."""

from typing import Optional
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Base todo model."""
    title: str
    description: Optional[str] = ""
    completed: bool = False
    session_id: Optional[str] = "default_session"
    plan_id: Optional[str] = None


class TodoCreate(TodoBase):
    """Todo creation model."""
    pass


class TodoUpdate(BaseModel):
    """Todo update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    session_id: Optional[str] = None
    plan_id: Optional[str] = None


class Todo(TodoBase):
    """Complete todo model."""
    id: str
    created_at: int
    updated_at: int
    
    class Config:
        from_attributes = True
