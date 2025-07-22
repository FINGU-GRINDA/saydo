from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    CALENDAR_EVENT = "calendar_event"
    EMAIL = "email"
    SHEET_UPDATE = "sheet_update"
    DOCUMENT_CREATE = "document_create"
    TODO = "todo"


class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    COMPLETED = "completed"
    EXECUTING = "executing"


class MeetingAction(BaseModel):
    id: str
    action_type: ActionType
    description: str
    details: Dict[str, Any]
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime
    executed_at: Optional[datetime] = None


class Meeting(BaseModel):
    id: str
    user_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str]
    transcript: Optional[str] = None
    summary: Optional[str] = None
    actions: List[MeetingAction] = []
    raw_recording_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MeetingCreate(BaseModel):
    title: str
    start_time: datetime
    participants: List[str]


class MeetingResponse(BaseModel):
    id: str
    user_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str]
    transcript: Optional[str] = None
    summary: Optional[str] = None
    actions: List[MeetingAction] = []
    raw_recording_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TranscriptInput(BaseModel):
    text: str