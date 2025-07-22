import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime
import websockets
from config import settings
from app.services.deepgram_transcription import TranscriptionManager


class ZoomMeetingBot:
    """Zoom meeting bot that joins meetings and transcribes audio"""
    
    def __init__(self, meeting_id: str, meeting_password: str):
        self.meeting_id = meeting_id
        self.meeting_password = meeting_password
        self.transcription_manager = TranscriptionManager(meeting_id)
        self.is_recording = False
        self.meeting_data = {
            "id": meeting_id,
            "start_time": None,
            "participants": [],
            "transcript": "",
            "status": "initialized"
        }
    
    async def join_meeting(self) -> bool:
        """Join the Zoom meeting"""
        # Note: In a real implementation, you would use the zoom-meeting-sdk
        # For demo purposes, we'll simulate the connection
        
        try:
            # Simulate joining meeting
            self.meeting_data["status"] = "joining"
            self.meeting_data["start_time"] = datetime.utcnow().isoformat()
            
            # In real implementation:
            # 1. Generate JWT token
            # 2. Initialize Zoom SDK
            # 3. Join meeting with bot
            # 4. Request recording permission
            
            await asyncio.sleep(2)  # Simulate connection time
            
            self.meeting_data["status"] = "connected"
            print(f"Bot joined meeting {self.meeting_id}")
            
            # Start transcription with live updates
            await self.transcription_manager.start(
                on_live_update=self._handle_live_update
            )
            self.is_recording = True
            
            return True
            
        except Exception as e:
            print(f"Failed to join meeting: {e}")
            self.meeting_data["status"] = "failed"
            return False
    
    def _handle_live_update(self, update: Dict[str, Any]):
        """Handle live transcription updates"""
        # Store update in meeting data for real-time access
        if "live_updates" not in self.meeting_data:
            self.meeting_data["live_updates"] = []
        
        self.meeting_data["live_updates"].append(update)
        
        # Keep only last 100 updates to prevent memory issues
        if len(self.meeting_data["live_updates"]) > 100:
            self.meeting_data["live_updates"] = self.meeting_data["live_updates"][-100:]
    
    async def process_audio_stream(self):
        """Process audio from the meeting"""
        # In real implementation, this would:
        # 1. Capture audio from Zoom SDK
        # 2. Convert to appropriate format
        # 3. Send to Deepgram for transcription
        
        # Demo: Simulate audio streaming
        demo_audio_chunks = [
            b"Hello everyone, welcome to the meeting.",
            b"Today we'll discuss the Q2 roadmap.",
            b"John, can you share the product updates?",
            b"Sure, we've made progress on three key features.",
            b"First, the new dashboard is almost complete.",
            b"Sarah, please schedule a demo for next week.",
            b"Mike, can you update the project tracker?"
        ]
        
        for chunk in demo_audio_chunks:
            if not self.is_recording:
                break
                
            # Simulate audio chunk processing
            await asyncio.sleep(2)
            
            # In real implementation, send actual audio bytes
            # await self.transcription_manager.send_audio(chunk)
            
            # For demo, we'll add simulated transcript
            self._simulate_transcript_update()
    
    def _simulate_transcript_update(self):
        """Simulate transcript updates for demo"""
        # In real implementation, this would be handled by Deepgram callbacks
        timestamp = datetime.utcnow().isoformat()
        
        # Simulate different speakers
        demo_segments = [
            {"speaker": 0, "name": "Host", "text": "Welcome everyone to today's meeting."},
            {"speaker": 1, "name": "John", "text": "Thanks for joining. Let's discuss the Q2 roadmap."},
            {"speaker": 2, "name": "Sarah", "text": "I'll take notes and send them after."},
            {"speaker": 1, "name": "John", "text": "We need to schedule a follow-up for next Tuesday."},
            {"speaker": 3, "name": "Mike", "text": "I'll update the project tracker with our progress."},
        ]
        
        # Add to transcript
        for segment in demo_segments[:2]:  # Add a few segments at a time
            speaker_text = f"{segment['name']}: {segment['text']}"
            self.meeting_data["transcript"] += speaker_text + "\n"
    
    async def leave_meeting(self) -> Dict[str, Any]:
        """Leave the meeting and return transcript"""
        self.is_recording = False
        
        # Stop transcription
        final_transcript = await self.transcription_manager.stop()
        
        # In demo mode, use simulated transcript
        if not final_transcript:
            final_transcript = self.meeting_data["transcript"]
        
        self.meeting_data["status"] = "completed"
        self.meeting_data["end_time"] = datetime.utcnow().isoformat()
        self.meeting_data["final_transcript"] = final_transcript
        
        return self.meeting_data
    
    async def get_participants(self) -> list:
        """Get list of meeting participants"""
        # In real implementation, this would query Zoom API
        # For demo, return simulated participants
        return [
            {"id": "1", "name": "John Smith", "email": "john@example.com"},
            {"id": "2", "name": "Sarah Johnson", "email": "sarah@example.com"},
            {"id": "3", "name": "Mike Wilson", "email": "mike@example.com"}
        ]


class MeetingBotManager:
    """Manages multiple meeting bots"""
    
    def __init__(self):
        self.active_bots = {}
    
    async def create_bot(self, meeting_id: str, meeting_password: str) -> ZoomMeetingBot:
        """Create and start a new meeting bot"""
        bot = ZoomMeetingBot(meeting_id, meeting_password)
        
        if await bot.join_meeting():
            self.active_bots[meeting_id] = bot
            
            # Start audio processing in background
            asyncio.create_task(bot.process_audio_stream())
            
            return bot
        
        raise Exception("Failed to create meeting bot")
    
    async def stop_bot(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Stop a meeting bot and get results"""
        bot = self.active_bots.get(meeting_id)
        if bot:
            result = await bot.leave_meeting()
            del self.active_bots[meeting_id]
            return result
        return None
    
    def get_bot_status(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a bot"""
        bot = self.active_bots.get(meeting_id)
        if bot:
            return {
                "meeting_id": meeting_id,
                "status": bot.meeting_data["status"],
                "is_recording": bot.is_recording,
                "transcript_length": len(bot.meeting_data.get("transcript", ""))
            }
        return None


# Global bot manager instance
bot_manager = MeetingBotManager()