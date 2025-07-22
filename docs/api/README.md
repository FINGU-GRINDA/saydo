# Saydo CallOps API Reference

## Overview

The Saydo CallOps API is a RESTful API built with FastAPI that provides endpoints for meeting management, AI processing, and action execution.

Base URL: `http://localhost:8000/api`

## Authentication

All API endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "demo",
  "password": "demo"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/google/login`
Initiate Google OAuth login flow.

#### GET `/api/auth/google/callback`
Handle Google OAuth callback.

### Meetings

#### GET `/api/meetings`
Get all meetings for the authenticated user.

**Response:**
```json
[
  {
    "id": "meeting_123",
    "title": "Q3 Roadmap Sync",
    "start_time": "2024-01-22T12:00:00Z",
    "end_time": "2024-01-22T12:30:00Z",
    "participants": ["Magdy", "Cuzin"],
    "transcript": "...",
    "summary": "...",
    "actions": []
  }
]
```

#### GET `/api/meetings/{meeting_id}`
Get a specific meeting by ID.

#### POST `/api/meetings`
Create a new meeting record.

**Request Body:**
```json
{
  "title": "Team Standup",
  "meet_url": "https://meet.google.com/xxx-yyyy-zzz"
}
```

#### PUT `/api/meetings/{meeting_id}`
Update meeting details.

#### DELETE `/api/meetings/{meeting_id}`
Delete a meeting.

### Meeting Bot

#### POST `/api/bot/start`
Start a meeting bot for a Google Meet URL.

**Request Body:**
```json
{
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "meeting_title": "Q3 Planning"
}
```

**Response:**
```json
{
  "meeting_id": "meeting_123",
  "bot_id": "bot_456",
  "status": "joining"
}
```

#### POST `/api/bot/stop/{meeting_id}`
Stop the meeting bot and process the transcript.

#### GET `/api/bot/status/{meeting_id}`
Get the current status of a meeting bot.

**Response:**
```json
{
  "status": "recording",
  "duration": 120,
  "participant_count": 2
}
```

### AI Agent

#### GET `/api/agent/preferences`
Get user's AI agent preferences.

**Response:**
```json
{
  "user_id": "user_123",
  "enabled_capabilities": [
    "summary",
    "calendar_event",
    "email",
    "todo"
  ]
}
```

#### PUT `/api/agent/preferences`
Update AI agent preferences.

**Request Body:**
```json
{
  "enabled_capabilities": [
    "summary",
    "calendar_event",
    "email",
    "todo",
    "sheet_update"
  ]
}
```

#### POST `/api/agent/process/{meeting_id}`
Manually trigger AI processing for a meeting.

### Actions

#### GET `/api/meetings/{meeting_id}/actions`
Get all actions for a meeting.

#### POST `/api/actions/{action_id}/execute`
Execute a pending action.

**Response:**
```json
{
  "action_id": "action_123",
  "status": "completed",
  "result": {
    "calendar_event_id": "event_456"
  }
}
```

### Integrations

#### GET `/api/integrations/google/status`
Check Google integration status.

#### POST `/api/integrations/google/connect`
Connect Google account for integrations.

## WebSocket Endpoints

### `/ws/transcription/{meeting_id}`
Real-time transcription updates during meeting.

**Message Format:**
```json
{
  "type": "transcript",
  "speaker": "Magdy",
  "text": "Let's schedule a follow-up",
  "timestamp": "2024-01-22T12:05:30Z"
}
```

### `/ws/meeting/{meeting_id}/audio`
Stream audio data for processing.

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated endpoints

## Example Usage

### Starting a Meeting Bot

```python
import requests

# Login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "demo", "password": "demo"}
)
token = login_response.json()["access_token"]

# Start bot
headers = {"Authorization": f"Bearer {token}"}
bot_response = requests.post(
    "http://localhost:8000/api/bot/start",
    headers=headers,
    json={
        "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
        "meeting_title": "Team Sync"
    }
)

meeting_id = bot_response.json()["meeting_id"]
print(f"Bot started for meeting: {meeting_id}")
```