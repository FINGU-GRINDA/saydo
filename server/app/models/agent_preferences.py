from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AgentCapability(BaseModel):
    """Individual capability that can be enabled for the agent"""
    id: str
    name: str
    description: str
    enabled: bool = False
    settings: Optional[dict] = None


class AgentPreferences(BaseModel):
    """User's preferences for their AI agent"""
    user_id: str
    capabilities: List[AgentCapability]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "capabilities": [
                    {
                        "id": "summary",
                        "name": "Meeting Summaries",
                        "description": "Generate concise meeting summaries",
                        "enabled": True
                    },
                    {
                        "id": "calendar",
                        "name": "Calendar Management",
                        "description": "Schedule events in Google Calendar",
                        "enabled": True,
                        "settings": {
                            "default_duration": 60,
                            "reminder_minutes": 15
                        }
                    },
                    {
                        "id": "email",
                        "name": "Email Drafting",
                        "description": "Draft and send follow-up emails",
                        "enabled": False
                    },
                    {
                        "id": "sheets",
                        "name": "Google Sheets",
                        "description": "Update spreadsheets with meeting data",
                        "enabled": True,
                        "settings": {
                            "default_sheet_id": "abc123"
                        }
                    },
                    {
                        "id": "docs",
                        "name": "Google Docs",
                        "description": "Create meeting notes in Google Docs",
                        "enabled": False
                    }
                ]
            }
        }


# Default capabilities - match the frontend action definitions
DEFAULT_CAPABILITIES = [
    AgentCapability(
        id="summary",
        name="Generate Summary",
        description="Create a concise summary of any conversation",
        enabled=True  # Core AI - always enabled
    ),
    AgentCapability(
        id="todo",
        name="Extract Action Items", 
        description="Pull out clear, actionable tasks from a conversation",
        enabled=True  # Core AI - always enabled
    ),
    AgentCapability(
        id="email",
        name="Draft Follow-up Email",
        description="Write a draft email based on the conversation",
        enabled=False  # Requires Google OAuth - disabled until connected
    ),
    AgentCapability(
        id="calendar",
        name="Schedule Meeting",
        description="Identify and suggest meeting times with participants",
        enabled=False  # Requires Google OAuth - disabled until connected
    ),
    AgentCapability(
        id="sheets",
        name="Create Project Task",
        description="Add a new task to a project board like Trello or Asana",
        enabled=False  # Requires Google OAuth - disabled until connected
    ),
    AgentCapability(
        id="crm",
        name="Update CRM Contact",
        description="Automatically update contact records with conversation notes",
        enabled=False
    ),
    AgentCapability(
        id="analytics",
        name="Log Sales Activity", 
        description="Track call outcomes and update sales pipeline",
        enabled=False
    ),
    AgentCapability(
        id="slack",
        name="Share to Slack",
        description="Send key summaries or updates to a Slack channel",
        enabled=False
    )
]