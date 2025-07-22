from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import asyncio
from datetime import datetime

from app.services.deepgram_transcription import TranscriptionManager
from app.core.auth import verify_token

router = APIRouter(prefix="/ws", tags=["websocket"])

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Active transcription sessions
transcription_sessions: Dict[str, TranscriptionManager] = {}


@router.websocket("/transcription/{meeting_id}")
async def transcription_websocket(websocket: WebSocket, meeting_id: str):
    """WebSocket endpoint for real-time transcription"""
    await websocket.accept()
    
    # Store connection
    active_connections[meeting_id] = websocket
    
    # Create transcription manager
    transcription_manager = TranscriptionManager(meeting_id)
    transcription_sessions[meeting_id] = transcription_manager
    
    try:
        # Start transcription with live updates
        success = await transcription_manager.start(
            on_live_update=lambda data: asyncio.create_task(
                send_transcription_update(meeting_id, data)
            )
        )
        
        if not success:
            await websocket.send_json({
                "type": "error",
                "message": "Failed to start transcription"
            })
            await websocket.close()
            return
        
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "message": "Transcription started",
            "meeting_id": meeting_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "audio":
                # Forward audio to Deepgram
                audio_bytes = data.get("audio", "").encode('latin-1')  # Convert from string
                await transcription_manager.send_audio(audio_bytes)
                
            elif data.get("type") == "speaker_identify":
                # Update speaker name
                speaker_id = data.get("speaker_id")
                name = data.get("name")
                if speaker_id is not None and name:
                    transcription_manager.set_speaker_name(speaker_id, name)
                    
            elif data.get("type") == "stop":
                # Stop transcription
                break
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for meeting {meeting_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        # Clean up
        if meeting_id in active_connections:
            del active_connections[meeting_id]
        
        if meeting_id in transcription_sessions:
            result = await transcription_sessions[meeting_id].stop()
            del transcription_sessions[meeting_id]
            
            # Send final transcript
            try:
                await websocket.send_json({
                    "type": "final_transcript",
                    "data": result
                })
            except:
                pass
        
        await websocket.close()


async def send_transcription_update(meeting_id: str, data: Dict[str, Any]):
    """Send transcription update to connected client"""
    if meeting_id in active_connections:
        websocket = active_connections[meeting_id]
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Error sending update: {e}")


@router.websocket("/meeting/{meeting_id}/audio")
async def audio_stream_websocket(websocket: WebSocket, meeting_id: str):
    """WebSocket endpoint for streaming audio from client to server"""
    await websocket.accept()
    
    try:
        # Get transcription manager for this meeting
        if meeting_id not in transcription_sessions:
            await websocket.send_json({
                "type": "error",
                "message": "No active transcription session for this meeting"
            })
            await websocket.close()
            return
        
        transcription_manager = transcription_sessions[meeting_id]
        
        # Stream audio
        while True:
            # Receive audio data (binary)
            audio_data = await websocket.receive_bytes()
            
            # Forward to Deepgram
            await transcription_manager.send_audio(audio_data)
            
    except WebSocketDisconnect:
        print(f"Audio stream disconnected for meeting {meeting_id}")
    except Exception as e:
        print(f"Audio stream error: {e}")
    finally:
        await websocket.close()