"""
Webhook endpoints for external services
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import asyncio
import json

from app.services.meeting_bot_service import meeting_bot_orchestrator
from app.services.meet_bot import meet_bot_manager

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/recall/{session_id}")
async def recall_webhook(session_id: str, request: Request):
    """Receive webhooks from Recall.ai for meeting bot updates"""
    try:
        body = await request.json()
        event_type = body.get("event", "")
        
        print(f"Recall.ai webhook for session {session_id}: {event_type}")
        
        # Get the bot session
        session = meet_bot_manager.get_session(session_id)
        if not session:
            print(f"Session {session_id} not found")
            return {"status": "error", "message": "Session not found"}
        
        # Handle different event types
        if event_type == "bot.status_change":
            # Bot status changed (joining, recording, leaving, etc.)
            status = body.get("data", {}).get("status", "")
            print(f"Bot status changed to: {status}")
            
        elif event_type == "bot.transcription.partial":
            # Partial transcription (real-time)
            transcript_data = body.get("data", {})
            text = transcript_data.get("text", "")
            speaker = transcript_data.get("speaker", "Unknown")
            
            if text.strip():
                # Add partial transcript
                await session.add_transcript_chunk(text, speaker=speaker, is_final=False)
                print(f"Added partial transcript from {speaker}: {text[:50]}...")
                
        elif event_type == "bot.transcription.final":
            # Final transcription
            transcript_data = body.get("data", {})
            text = transcript_data.get("text", "")
            speaker = transcript_data.get("speaker", "Unknown")
            
            if text.strip():
                # Add final transcript
                await session.add_transcript_chunk(text, speaker=speaker, is_final=True)
                print(f"Added final transcript from {speaker}: {text[:50]}...")
                
        elif event_type == "bot.meeting_ended":
            # Meeting ended, process final results
            print(f"Meeting ended for session {session_id}")
            
            # Stop the bot session automatically
            try:
                await meeting_bot_orchestrator.stop_bot_session(session_id)
            except Exception as e:
                print(f"Error auto-stopping session {session_id}: {e}")
                
        elif event_type == "bot.error":
            # Bot encountered an error
            error = body.get("data", {}).get("error", "Unknown error")
            print(f"Bot error for session {session_id}: {error}")
            
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        print(f"Error processing Recall.ai webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.post("/deepgram/{session_id}")
async def deepgram_webhook(session_id: str, request: Request):
    """Receive webhooks from Deepgram for direct transcription"""
    try:
        body = await request.json()
        
        # Get the session
        session = meet_bot_manager.get_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        # Process Deepgram webhook format
        channel = body.get("channel", {})
        alternatives = channel.get("alternatives", [])
        
        if alternatives:
            transcript = alternatives[0].get("transcript", "")
            confidence = alternatives[0].get("confidence", 0.0)
            
            # Deepgram speaker diarization
            words = alternatives[0].get("words", [])
            speaker = "Unknown"
            if words and "speaker" in words[0]:
                speaker = f"Speaker {words[0]['speaker']}"
            
            is_final = body.get("is_final", False)
            
            if transcript.strip() and confidence > 0.5:
                await session.add_transcript_chunk(transcript, speaker=speaker, is_final=is_final)
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Error processing Deepgram webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.get("/test/{session_id}")
async def test_webhook(session_id: str):
    """Test webhook endpoint for development"""
    try:
        session = meet_bot_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add test transcript
        await session.add_transcript_chunk(
            "This is a test transcript from the webhook endpoint.",
            speaker="Test Speaker"
        )
        
        return {
            "status": "success",
            "message": f"Test transcript added to session {session_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing webhook: {str(e)}")