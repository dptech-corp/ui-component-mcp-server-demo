from pydantic import BaseModel
from typing import Optional

class CodeInterpreterState(BaseModel):
    id: str
    session_id: str
    ticket_id: str
    code: str
    description: Optional[str] = ""
    status: str = "pending"  # pending, running, completed, error
    result: Optional[str] = None
    widget_url: Optional[str] = None
    created_at: int
    updated_at: int

class CodeInterpreterCreateRequest(BaseModel):
    session_id: str
    code: str
    description: Optional[str] = ""

class CodeInterpreterUpdateRequest(BaseModel):
    status: Optional[str] = None
    result: Optional[str] = None

class CodeInterpreterResponse(BaseModel):
    id: str
    session_id: str
    ticket_id: str
    status: str
    widget_url: Optional[str] = None
    result: Optional[str] = None
