"""
Simplified Google Meet Bot Service
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from .meet_bot import MeetBotSession
from .meet_bot_puppeteer import PuppeteerMeetBot


class GoogleMeetBot:
    """Simplified Google Meet Bot using Puppeteer"""
    
    def __init__(self, session: MeetBotSession):
        self.session = session
        self.puppeteer_bot: Optional[PuppeteerMeetBot] = None
        self.is_recording = False
        
    async def join_meeting(self) -> bool:
        """Join Google Meet and start recording"""
        try:
            print(f"Bot joining meeting: {self.session.meet_url}")
            
            # Create Puppeteer bot
            self.puppeteer_bot = PuppeteerMeetBot(self.session)
            
            # Join meeting
            success = await self.puppeteer_bot.join_meeting()
            
            if success:
                self.is_recording = True
                print("Bot successfully joined and started recording")
                return True
            else:
                print("Failed to join meeting")
                return False
                
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False
    
    async def leave_meeting(self):
        """Leave meeting and cleanup"""
        try:
            print("Bot leaving meeting...")
            
            self.is_recording = False
            
            if self.puppeteer_bot:
                await self.puppeteer_bot.leave_meeting()
                self.puppeteer_bot = None
            
            print("Bot successfully left meeting")
            
        except Exception as e:
            print(f"Error leaving meeting: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "session_id": self.session.session_id,
            "is_recording": self.is_recording,
            "browser_active": self.puppeteer_bot is not None,
            "transcription_active": self.puppeteer_bot.transcription_manager is not None if self.puppeteer_bot else False,
            "meet_url": self.session.meet_url,
            "status": self.session.status
        }


class MeetBotOrchestrator:
    """Manages multiple meeting bots"""
    
    def __init__(self):
        self.active_bots: Dict[str, GoogleMeetBot] = {}
    
    async def create_and_join_meeting(self, user_id: str, meet_url: str) -> Dict[str, Any]:
        """Create bot session and join meeting"""
        try:
            from .meet_bot import meet_bot_manager
            
            # Create session
            session = await meet_bot_manager.create_session(user_id, meet_url)
            
            # Create bot
            bot = GoogleMeetBot(session)
            self.active_bots[session.session_id] = bot
            
            # Join meeting
            success = await bot.join_meeting()
            
            if success:
                return {
                    "session_id": session.session_id,
                    "status": "recording",
                    "message": "Bot successfully joined meeting",
                    "meet_url": meet_url
                }
            else:
                await self.cleanup_bot(session.session_id)
                raise Exception("Failed to join meeting")
                
        except Exception as e:
            print(f"Error creating meeting bot: {e}")
            raise e
    
    async def stop_bot_session(self, session_id: str) -> Dict[str, Any]:
        """Stop bot session"""
        if session_id in self.active_bots:
            bot = self.active_bots[session_id]
            await bot.leave_meeting()
            
            result = bot.session
            await self.cleanup_bot(session_id)
            
            return {
                "session_id": session_id,
                "status": "completed",
                "transcript": result.transcript,
                "summary": result.summary,
                "actions": result.actions
            }
        else:
            raise ValueError(f"Bot session {session_id} not found")
    
    async def cleanup_bot(self, session_id: str):
        """Cleanup bot"""
        if session_id in self.active_bots:
            try:
                await self.active_bots[session_id].leave_meeting()
            except:
                pass
            finally:
                del self.active_bots[session_id]
    
    def get_bot_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get bot status"""
        if session_id in self.active_bots:
            return self.active_bots[session_id].get_status()
        return None
    
    def list_active_bots(self) -> list:
        """List active bots"""
        return [bot.get_status() for bot in self.active_bots.values()]
    
    async def cleanup_all(self):
        """Cleanup all bots"""
        for session_id in list(self.active_bots.keys()):
            await self.cleanup_bot(session_id)


# Global instance
meeting_bot_orchestrator = MeetBotOrchestrator()