"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from .models import IdeaStatus, MessageType


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    idea_id: int
    type: MessageType
    created_at: datetime


class IdeaBase(BaseModel):
    content: str


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    content: Optional[str] = None


class IdeaResponse(IdeaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: IdeaStatus
    agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class IdeaWithMessages(IdeaResponse):
    messages: list[MessageResponse] = []


class AgentClaimRequest(BaseModel):
    agent_id: str


class AgentFeedbackRequest(BaseModel):
    agent_id: str
    content: str


class AgentAskRequest(BaseModel):
    agent_id: str
    question: str


class AgentCompleteRequest(BaseModel):
    agent_id: str
    summary: Optional[str] = None


class AgentFailRequest(BaseModel):
    agent_id: str
    reason: str


class StatusChangeResponse(BaseModel):
    id: int
    old_status: IdeaStatus
    new_status: IdeaStatus
    message: str
