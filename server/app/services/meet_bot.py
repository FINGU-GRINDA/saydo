"""
Google Meet Bot Service
Handles automated meeting recording and processing
"""

import asyncio
import base64
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from .firebase_service import firebase_service
from .openai_agent import MeetingAgent
from .action_executor import ActionExecutor


class MeetBotSession:
    """Manages a single meeting bot session"""
    
    def __init__(self, user_id: str, meet_url: str):
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.meet_url = meet_url
        self.status = "preparing"  # preparing -> recording -> processing -> completed
        self.start_time = None
        self.end_time = None
        self.transcript = ""
        self.summary = None
        self.actions = []
        self.meeting_id = None
        
        # Real-time callbacks
        self.on_transcript_update: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
        self.on_action_generated: Optional[Callable] = None

    async def start_recording(self) -> bool:
        """Start the recording session"""
        try:
            self.status = "recording"
            self.start_time = datetime.utcnow()
            
            # Create meeting record in Firebase
            meeting_id = str(uuid.uuid4())
            meeting_data = {
                "id": meeting_id,
                "user_id": self.user_id,
                "title": f"Google Meet Bot Recording - {self.start_time.strftime('%Y-%m-%d %H:%M')}",
                "start_time": self.start_time.isoformat(),
                "end_time": None,
                "participants": [],
                "transcript": "",
                "summary": "",
                "actions": [],
                "raw_recording_url": None,
                "meet_url": self.meet_url,
                "session_id": self.session_id,
                "created_at": self.start_time.isoformat(),
                "updated_at": self.start_time.isoformat()
            }
            
            created_meeting_id = await firebase_service.create_meeting(meeting_data)
            self.meeting_id = created_meeting_id
            
            print(f"Created meeting record with ID: {self.meeting_id}")
            
            # Notify status change
            if self.on_status_change:
                await self.on_status_change({
                    "status": self.status,
                    "session_id": self.session_id,
                    "meeting_id": self.meeting_id,
                    "start_time": self.start_time.isoformat()
                })
            
            return True
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.status = "error"
            return False

    async def add_transcript_chunk(self, text: str, speaker: Optional[str] = None):
        """Add transcript text from speech recognition"""
        if text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            speaker_prefix = f"[{timestamp}] {speaker}: " if speaker else f"[{timestamp}] "
            chunk = speaker_prefix + text.strip() + "\n"
            
            self.transcript += chunk
            
            # Notify transcript update
            if self.on_transcript_update:
                await self.on_transcript_update({
                    "session_id": self.session_id,
                    "transcript_chunk": chunk,
                    "full_transcript": self.transcript,
                    "speaker": speaker,
                    "timestamp": timestamp
                })

    async def stop_recording(self) -> Dict[str, Any]:
        """Stop recording and process the meeting"""
        try:
            self.status = "processing"
            self.end_time = datetime.utcnow()
            
            if self.on_status_change:
                await self.on_status_change({
                    "status": self.status,
                    "session_id": self.session_id,
                    "end_time": self.end_time.isoformat()
                })
            
            # Process the meeting with AI
            result = await self.process_with_ai()
            
            self.status = "completed"
            
            if self.on_status_change:
                await self.on_status_change({
                    "status": self.status,
                    "session_id": self.session_id,
                    "summary": self.summary,
                    "actions_count": len(self.actions)
                })
            
            return result
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            self.status = "error"
            raise e

    async def process_with_ai(self) -> Dict[str, Any]:
        """Process transcript with AI agent"""
        if not self.meeting_id:
            raise ValueError("No meeting ID available")
        
        # Wait for meaningful transcript content
        await self._wait_for_transcript()
        
        if not self.transcript.strip():
            print("⚠️  No transcript content available after waiting")
            return self._create_empty_result()
        
        try:
            # Initialize AI agent with user capabilities
            agent = MeetingAgent(user_id=self.user_id)
            await agent.initialize_capabilities()
            
            # Process transcript
            result = await agent.process_transcript(self.transcript)
            
            self.summary = result.get("summary", "")
            
            # Update meeting in Firebase
            meeting_updates = {
                "transcript": self.transcript,
                "summary": self.summary,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await firebase_service.update_meeting(self.meeting_id, meeting_updates)
            
            # Store actions in Firebase
            self.actions = []
            for action_data in result.get("actions", []):
                action_data.update({
                    "meeting_id": self.meeting_id,
                    "user_id": self.user_id,
                    "session_id": self.session_id
                })
                
                action_id = await firebase_service.create_action(action_data)
                action_data["id"] = action_id
                self.actions.append(action_data)
                
                # Notify action generated
                if self.on_action_generated:
                    await self.on_action_generated(action_data)
            
            return {
                "session_id": self.session_id,
                "meeting_id": self.meeting_id,
                "summary": self.summary,
                "actions": self.actions,
                "transcript_length": len(self.transcript),
                "enabled_capabilities": result.get("enabled_capabilities", [])
            }
            
        except Exception as e:
            print(f"Error processing with AI: {e}")
            raise e
    
    async def _wait_for_transcript(self, max_wait_seconds: int = 30, min_words: int = 10):
        """Wait for meaningful transcript content to be available"""
        import asyncio
        
        wait_time = 0
        check_interval = 2
        
        print(f"⏳ Waiting for transcript content (current length: {len(self.transcript.strip())} chars)")
        
        while wait_time < max_wait_seconds:
            word_count = len(self.transcript.split()) if self.transcript.strip() else 0
            
            if word_count >= min_words:
                print(f"✅ Transcript ready with {word_count} words")
                break
            
            print(f"⏳ Transcript has {word_count} words, waiting for {min_words} minimum...")
            await asyncio.sleep(check_interval)
            wait_time += check_interval
        
        final_word_count = len(self.transcript.split()) if self.transcript.strip() else 0
        print(f"📝 Final transcript: {final_word_count} words ({len(self.transcript)} chars)")
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result when no transcript is available"""
        empty_summary = "No transcript content was captured during this meeting."
        
        # Update meeting with empty result
        asyncio.create_task(self._update_meeting_with_empty_result(empty_summary))
        
        return {
            "session_id": self.session_id,
            "meeting_id": self.meeting_id,
            "summary": empty_summary,
            "actions": [],
            "transcript_length": 0,
            "enabled_capabilities": []
        }
    
    async def _update_meeting_with_empty_result(self, summary: str):
        """Update meeting record with empty result"""
        try:
            meeting_updates = {
                "transcript": "",
                "summary": summary,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "updated_at": datetime.utcnow().isoformat()
            }
            await firebase_service.update_meeting(self.meeting_id, meeting_updates)
        except Exception as e:
            print(f"Error updating meeting with empty result: {e}")

    async def execute_action(self, action_id: str) -> Dict[str, Any]:
        """Execute a specific action"""
        try:
            # Find the action
            action_dict = next((a for a in self.actions if a.get("id") == action_id), None)
            if not action_dict:
                raise ValueError(f"Action {action_id} not found")
            
            # Update status to executing
            await firebase_service.update_action(action_id, {
                "status": "executing",
                "updated_at": datetime.utcnow()
            })
            
            # Create MeetingAction object from dictionary
            from app.models.meeting import MeetingAction, ActionType, ActionStatus
            action = MeetingAction(
                id=action_dict["id"],
                action_type=ActionType(action_dict.get("action_type", action_dict.get("type"))),
                description=action_dict["description"],
                details=action_dict["details"],
                status=ActionStatus(action_dict.get("status", "pending")),
                created_at=action_dict.get("created_at", datetime.utcnow())
            )
            
            # Execute with ActionExecutor
            executor = ActionExecutor(self.user_id)
            result = await executor.execute_action(action)
            
            # Update final status
            final_status = "completed" if result.get("success") else "failed"
            await firebase_service.update_action(action_id, {
                "status": final_status,
                "result": result,
                "updated_at": datetime.utcnow()
            })
            
            # Update local action status
            for i, a in enumerate(self.actions):
                if a.get("id") == action_id:
                    self.actions[i]["status"] = final_status
                    self.actions[i]["result"] = result
                    break
            
            return {
                "action_id": action_id,
                "status": final_status,
                "result": result
            }
            
        except Exception as e:
            print(f"Error executing action: {e}")
            # Update action status to failed
            await firebase_service.update_action(action_id, {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow()
            })
            raise e


class MeetBotManager:
    """Manages multiple meeting bot sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, MeetBotSession] = {}
    
    async def create_session(self, user_id: str, meet_url: str) -> MeetBotSession:
        """Create a new meeting bot session"""
        session = MeetBotSession(user_id, meet_url)
        self.active_sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[MeetBotSession]:
        """Get an active session"""
        return self.active_sessions.get(session_id)
    
    async def cleanup_session(self, session_id: str):
        """Remove and cleanup a session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if session.status == "recording":
                await session.stop_recording()
            del self.active_sessions[session_id]
    
    def list_user_sessions(self, user_id: str) -> list:
        """List all sessions for a user"""
        return [
            {
                "session_id": s.session_id,
                "meet_url": s.meet_url,
                "status": s.status,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "meeting_id": s.meeting_id
            }
            for s in self.active_sessions.values() 
            if s.user_id == user_id
        ]


# Global manager instance
meet_bot_manager = MeetBotManager()