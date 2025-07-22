"""
Google Meet Bot Service
Automates joining Google Meet sessions as a virtual participant
"""

import asyncio
import subprocess
from typing import Optional, Dict, Any, Callable
import os
import signal
from datetime import datetime
import tempfile
import uuid

from .deepgram_transcription import TranscriptionManager
from .meet_bot import MeetBotSession
from .meet_bot_puppeteer import PuppeteerMeetBot


class GoogleMeetBot:
    """
    Automated Google Meet participant using Puppeteer for real audio capture
    This bot joins meetings independently and captures audio for transcription
    """
    
    def __init__(self, session: MeetBotSession):
        self.session = session
        self.puppeteer_bot: Optional[PuppeteerMeetBot] = None
        self.is_recording = False
        
    async def join_meeting(self) -> bool:
        """Join the Google Meet as an automated bot"""
        try:
            print(f"Bot joining meeting: {self.session.meet_url}")
            
            # Create Puppeteer bot instance
            self.puppeteer_bot = PuppeteerMeetBot(self.session)
            
            # Join meeting using Puppeteer
            success = await self.puppeteer_bot.join_meeting()
            
            if success:
                self.is_recording = True
                print("Bot successfully joined meeting and started recording")
                return True
            else:
                print("Failed to join meeting")
                return False
                
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False
    
    async def _launch_browser_bot(self) -> bool:
        """Launch a headless browser to join the meeting"""
        try:
            # Create a browser user script for joining the meeting
            bot_script = self._generate_bot_script()
            script_path = os.path.join(self.temp_dir, "meetbot.js")
            
            with open(script_path, 'w') as f:
                f.write(bot_script)
            
            # Chrome arguments for headless operation
            chrome_args = [
                'google-chrome-stable',
                '--headless',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--use-fake-ui-for-media-stream',  # Auto-approve camera/mic
                '--use-fake-device-for-media-stream',  # Use fake audio/video
                '--allow-running-insecure-content',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--autoplay-policy=no-user-gesture-required',
                f'--user-data-dir={self.temp_dir}/chrome_data',
                '--enable-logging',
                '--log-level=0',
                # Audio capture for virtual microphone
                '--enable-features=WebRTCPipeWireCapturer',
                f'--load-extension={self.temp_dir}',
                self.session.meet_url
            ]
            
            # Launch Chrome process
            self.browser_process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Check if process started successfully
            await asyncio.sleep(2)
            if self.browser_process.poll() is None:
                print("Browser bot launched successfully")
                return True
            else:
                print("Browser bot failed to start")
                return False
                
        except Exception as e:
            print(f"Error launching browser bot: {e}")
            return False
    
    def _generate_bot_script(self) -> str:
        """Generate JavaScript to control the meeting bot"""
        return f"""
// Google Meet Bot Controller
console.log('Meet Bot starting for session: {self.session.session_id}');

class MeetBot {{
    constructor() {{
        this.botName = 'AI Assistant Bot';
        this.isJoined = false;
        this.audioContext = null;
        this.mediaRecorder = null;
    }}
    
    async init() {{
        console.log('Initializing Meet Bot...');
        
        // Wait for page to load
        await this.waitForPageLoad();
        
        // Join the meeting
        await this.joinMeeting();
        
        // Setup audio capture
        await this.setupAudioCapture();
        
        console.log('Meet Bot initialized successfully');
    }}
    
    async waitForPageLoad() {{
        return new Promise((resolve) => {{
            const checkInterval = setInterval(() => {{
                if (document.readyState === 'complete') {{
                    clearInterval(checkInterval);
                    setTimeout(resolve, 1000); // Additional delay
                }}
            }}, 100);
        }});
    }}
    
    async joinMeeting() {{
        console.log('Attempting to join meeting...');
        
        try {{
            // Dismiss any initial prompts
            await this.dismissPrompts();
            
            // Turn off camera and microphone initially
            await this.configureMediaSettings();
            
            // Join the meeting
            await this.clickJoinButton();
            
            this.isJoined = true;
            console.log('Successfully joined meeting');
            
        }} catch (error) {{
            console.error('Error joining meeting:', error);
        }}
    }}
    
    async dismissPrompts() {{
        // Common selectors for Google Meet prompts
        const selectors = [
            '[aria-label*="Dismiss"]',
            '[aria-label*="Got it"]',
            '[aria-label*="Allow"]',
            'button[jsname="b3VHJd"]',  // Got it button
            'button[jsname="Qx7uuf"]'   // Allow button
        ];
        
        for (const selector of selectors) {{
            const element = document.querySelector(selector);
            if (element) {{
                element.click();
                await new Promise(r => setTimeout(r, 500));
            }}
        }}
    }}
    
    async configureMediaSettings() {{
        // Turn off camera
        const cameraButton = document.querySelector('[aria-label*="camera"], [data-tooltip*="camera"]');
        if (cameraButton && !cameraButton.classList.contains('Ij0rWb')) {{
            cameraButton.click();
            await new Promise(r => setTimeout(r, 500));
        }}
        
        // Keep microphone on for audio capture
        const micButton = document.querySelector('[aria-label*="microphone"], [data-tooltip*="microphone"]');
        if (micButton && micButton.classList.contains('Ij0rWb')) {{
            micButton.click();
            await new Promise(r => setTimeout(r, 500));
        }}
    }}
    
    async clickJoinButton() {{
        const joinSelectors = [
            '[aria-label*="Join"]',
            'button[jsname="Qx7uuf"]',
            '.NPEfkd.RveJvd.snByac',
            'span:contains("Join now")'
        ];
        
        for (const selector of joinSelectors) {{
            const button = document.querySelector(selector);
            if (button) {{
                console.log('Clicking join button:', selector);
                button.click();
                await new Promise(r => setTimeout(r, 2000));
                return;
            }}
        }}
        
        console.warn('Join button not found');
    }}
    
    async setupAudioCapture() {{
        try {{
            // Get user media for audio capture
            const stream = await navigator.mediaDevices.getUserMedia({{
                audio: {{
                    echoCancellation: false,
                    noiseSuppression: false,
                    sampleRate: 16000
                }},
                video: false
            }});
            
            // Create audio context for processing
            this.audioContext = new AudioContext({{sampleRate: 16000}});
            const source = this.audioContext.createMediaStreamSource(stream);
            
            // Send audio data via WebSocket to server
            this.setupWebSocketConnection();
            
            console.log('Audio capture initialized');
            
        }} catch (error) {{
            console.error('Error setting up audio capture:', error);
        }}
    }}
    
    setupWebSocketConnection() {{
        const wsUrl = 'ws://localhost:8000/ws/meeting/{self.session.session_id}/audio';
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {{
            console.log('WebSocket connected for audio streaming');
        }};
        
        this.websocket.onerror = (error) => {{
            console.error('WebSocket error:', error);
        }};
    }}
    
    // Monitor meeting for participants and events
    startMonitoring() {{
        setInterval(() => {{
            this.checkMeetingStatus();
        }}, 5000);
    }}
    
    checkMeetingStatus() {{
        // Check if still in meeting
        const meetingContainer = document.querySelector('[data-allocation-index]');
        if (!meetingContainer) {{
            console.log('Meeting ended or disconnected');
            this.cleanup();
        }}
        
        // Monitor participant count
        const participants = document.querySelectorAll('[data-participant-id]');
        console.log(`Participants in meeting: ${{participants.length}}`);
    }}
    
    cleanup() {{
        if (this.audioContext) {{
            this.audioContext.close();
        }}
        if (this.websocket) {{
            this.websocket.close();
        }}
        console.log('Meet Bot cleanup completed');
    }}
}}

// Initialize the bot
const meetBot = new MeetBot();
meetBot.init().then(() => {{
    meetBot.startMonitoring();
}});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {{
    meetBot.cleanup();
}});
        """
    
    async def _handle_transcription_update(self, data: Dict[str, Any]):
        """Handle transcription updates from Deepgram"""
        try:
            # Forward to session
            if data.get('type') == 'transcript' and data.get('data', {}).get('is_final'):
                transcript_text = data['data'].get('transcript', '')
                speaker_segments = data['data'].get('speaker_segments', [])
                
                # Format transcript with speakers
                if speaker_segments:
                    formatted_text = []
                    for segment in speaker_segments:
                        speaker_id = segment.get('speaker', 0)
                        text = segment.get('text', '').strip()
                        if text:
                            formatted_text.append(f"Speaker {speaker_id + 1}: {text}")
                    
                    if formatted_text:
                        await self.session.add_transcript_chunk('\n'.join(formatted_text))
                elif transcript_text.strip():
                    await self.session.add_transcript_chunk(transcript_text)
            
        except Exception as e:
            print(f"Error handling transcription update: {e}")
    
    async def leave_meeting(self):
        """Leave the meeting and cleanup"""
        try:
            print("Bot leaving meeting...")
            
            self.is_recording = False
            
            # Stop transcription
            if self.transcription_manager:
                await self.transcription_manager.stop()
                self.transcription_manager = None
            
            # Terminate browser process
            if self.browser_process and self.browser_process.poll() is None:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.browser_process.pid), signal.SIGTERM)
                
                # Wait for graceful shutdown
                try:
                    self.browser_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not responsive
                    os.killpg(os.getpgid(self.browser_process.pid), signal.SIGKILL)
                    self.browser_process.wait()
                
                self.browser_process = None
            
            # Cleanup temporary files
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            # Stop session recording
            await self.session.stop_recording()
            
            print("Bot successfully left meeting")
            
        except Exception as e:
            print(f"Error leaving meeting: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            "session_id": self.session.session_id,
            "is_recording": self.is_recording,
            "browser_active": self.browser_process and self.browser_process.poll() is None,
            "transcription_active": self.transcription_manager is not None,
            "meet_url": self.session.meet_url,
            "status": self.session.status
        }


class MeetBotOrchestrator:
    """Manages multiple meeting bots"""
    
    def __init__(self):
        self.active_bots: Dict[str, GoogleMeetBot] = {}
    
    async def create_and_join_meeting(self, user_id: str, meet_url: str) -> Dict[str, Any]:
        """Create a new bot session and join the meeting"""
        try:
            # Import here to avoid circular imports
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
                # Cleanup failed bot
                await self.cleanup_bot(session.session_id)
                raise Exception("Failed to join meeting")
                
        except Exception as e:
            print(f"Error creating meeting bot: {e}")
            raise e
    
    async def stop_bot_session(self, session_id: str) -> Dict[str, Any]:
        """Stop a bot session"""
        if session_id in self.active_bots:
            bot = self.active_bots[session_id]
            await bot.leave_meeting()
            
            # Get final results
            result = bot.session
            
            # Cleanup
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
        """Cleanup a specific bot"""
        if session_id in self.active_bots:
            try:
                await self.active_bots[session_id].leave_meeting()
            except Exception as e:
                print(f"Error during bot cleanup: {e}")
            finally:
                del self.active_bots[session_id]
    
    def get_bot_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific bot"""
        if session_id in self.active_bots:
            return self.active_bots[session_id].get_status()
        return None
    
    def list_active_bots(self) -> list:
        """List all active bots"""
        return [bot.get_status() for bot in self.active_bots.values()]
    
    async def cleanup_all(self):
        """Cleanup all active bots"""
        for session_id in list(self.active_bots.keys()):
            await self.cleanup_bot(session_id)


# Global orchestrator instance
meeting_bot_orchestrator = MeetBotOrchestrator()