"""Agent data models."""

from typing import List, Optional, Any
from pydantic import BaseModel


class MessagePart(BaseModel):
    """Message part model."""
    text: str


class NewMessage(BaseModel):
    """New message model."""
    parts: List[MessagePart]
    role: str = "user"


class AgentRequest(BaseModel):
    """Agent request model."""
    appName: str = "agent"
    userId: str = "user"
    sessionId: str = "demo"
    newMessage: NewMessage
    streaming: bool = False


class AgentMessageRequest(BaseModel):
    """Agent message request from frontend."""
    message: str
    sessionId: Optional[str] = "demo"


class AgentResponse(BaseModel):
    """Agent response model."""
    success: bool
    response: Any
    error: Optional[str] = None
