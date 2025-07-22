from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.api.auth import get_user_by_id
from app.services.google_auth import refresh_google_credentials

router = APIRouter(prefix="/integrations", tags=["integrations"])


def get_google_credentials(user_id: str) -> Credentials:
    user = get_user_by_id(user_id)
    if not user or not user.google_tokens:
        raise HTTPException(status_code=401, detail="Google authentication required")
    
    # Refresh credentials if needed
    if user.google_tokens.get("refresh_token"):
        return refresh_google_credentials(user.google_tokens["refresh_token"])
    
    # Create credentials from stored tokens
    return Credentials(
        token=user.google_tokens.get("access_token"),
        refresh_token=user.google_tokens.get("refresh_token"),
        token_uri=user.google_tokens.get("token_uri"),
        client_id=user.google_tokens.get("client_id"),
        client_secret=user.google_tokens.get("client_secret"),
        scopes=user.google_tokens.get("scopes")
    )


@router.post("/calendar/event")
async def create_calendar_event(
    event_data: Dict[str, Any]
):
    # Demo mode - just return success
    return {
        "success": True,
        "event_id": "demo-event-123",
        "event_link": "https://calendar.google.com/event/demo",
        "demo_mode": True
    }


@router.post("/gmail/send")
async def send_email(
    email_data: Dict[str, Any]
):
    # Demo mode - just return success
    return {
        "success": True,
        "message_id": "demo-message-456",
        "demo_mode": True
    }


@router.post("/sheets/update")
async def update_google_sheet(
    sheet_data: Dict[str, Any]
):
    # Demo mode - just return success
    return {
        "success": True,
        "updated_cells": len(sheet_data.get('values', [])),
        "updated_rows": len(sheet_data.get('values', [])),
        "demo_mode": True
    }


def create_message(to: list, subject: str, body: str) -> str:
    import base64
    from email.mime.text import MIMEText
    
    message = MIMEText(body)
    message['to'] = ', '.join(to)
    message['subject'] = subject
    
    return base64.urlsafe_b64encode(message.as_bytes()).decode()