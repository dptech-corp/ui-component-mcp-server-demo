from pydantic import BaseModel
from typing import Optional

class File(BaseModel):
    id: str
    session_id: str
    name: str
    type: str
    path: str
    size: Optional[int] = None
    content: Optional[str] = None
    created_at: int
    updated_at: int

class FileCreate(BaseModel):
    name: str
    type: str
    path: str
    content: Optional[str] = None
    session_id: Optional[str] = None

class FileResponse(BaseModel):
    id: str
    name: str
    type: str
    path: str
    size: Optional[int] = None
    created_at: int
    updated_at: int
