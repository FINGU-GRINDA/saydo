from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.core.auth import get_current_user
from app.services.openai_agent import MeetingAgent
from app.services.action_executor import ActionExecutor
from app.services.firebase_service import firebase_service
from app.models.meeting import MeetingCreate, MeetingResponse, ActionType, TranscriptInput

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/", response_model=List[MeetingResponse])
async def get_meetings(current_user: dict = Depends(get_current_user)):
    """Get all meetings for the current user"""
    try:
        meetings = await firebase_service.get_user_meetings(current_user["sub"])
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific meeting"""
    try:
        meeting = await firebase_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Ensure user owns this meeting
        if meeting.get("user_id") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=MeetingResponse)
async def create_meeting(meeting: MeetingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new meeting"""
    try:
        meeting_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["sub"],
            "title": meeting.title,
            "start_time": meeting.start_time,
            "participants": meeting.participants,
            "transcript": "",
            "summary": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        created_meeting = await firebase_service.create_meeting(meeting_data)
        return created_meeting
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{meeting_id}/transcript")
async def process_meeting_transcript(
    meeting_id: str, 
    transcript: TranscriptInput, 
    current_user: dict = Depends(get_current_user)
):
    """Process a meeting transcript and extract actions"""
    try:
        # Get the meeting
        meeting = await firebase_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Ensure user owns this meeting
        if meeting.get("user_id") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Initialize agent with user's capabilities
        agent = MeetingAgent(user_id=current_user["sub"])
        await agent.initialize_capabilities()
        
        # Process the transcript
        result = await agent.process_transcript(transcript.text)
        
        # Update meeting with transcript and summary
        meeting_updates = {
            "transcript": transcript.text,
            "summary": result["summary"],
            "updated_at": datetime.utcnow()
        }
        
        await firebase_service.update_meeting(meeting_id, meeting_updates)
        
        # Store actions in Firebase
        action_ids = []
        for action_data in result["actions"]:
            action_data.update({
                "meeting_id": meeting_id,
                "user_id": current_user["sub"]
            })
            
            action_id = await firebase_service.create_action(action_data)
            action_ids.append(action_id)
        
        return {
            "message": "Transcript processed successfully",
            "summary": result["summary"],
            "actions_created": len(result["actions"]),
            "action_ids": action_ids,
            "enabled_capabilities": result.get("enabled_capabilities", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/actions")
async def get_meeting_actions(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Get all actions for a meeting"""
    try:
        # Verify meeting ownership
        meeting = await firebase_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.get("user_id") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        actions = await firebase_service.get_meeting_actions(meeting_id)
        return actions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{meeting_id}/actions/{action_id}/execute")
async def execute_action(
    meeting_id: str, 
    action_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Execute a pending action"""
    try:
        # Verify meeting ownership
        meeting = await firebase_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.get("user_id") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the action
        action = await firebase_service.get_action(action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        if action.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Action is not pending")
        
        # Update action status to executing
        await firebase_service.update_action(action_id, {
            "status": "executing",
            "updated_at": datetime.utcnow()
        })
        
        # Execute the action
        executor = ActionExecutor()
        result = await executor.execute_action(action, current_user["sub"])
        
        # Update action with result
        final_status = "completed" if result.get("success") else "failed"
        await firebase_service.update_action(action_id, {
            "status": final_status,
            "result": result,
            "updated_at": datetime.utcnow()
        })
        
        return {
            "message": f"Action {final_status}",
            "action_id": action_id,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error executing action: {e}")
        raise HTTPException(status_code=500, detail=str(e))