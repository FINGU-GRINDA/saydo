"""
Google Meet Bot using Puppeteer/Playwright for real audio capture
"""

import asyncio
import base64
import json
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import tempfile
import uuid
import os

from pyppeteer import launch
from pyppeteer.errors import TimeoutError as PyppeteerTimeout

from .deepgram_transcription import TranscriptionManager
from .meet_bot import MeetBotSession


class PuppeteerMeetBot:
    """
    Google Meet bot using Puppeteer for browser automation with audio capture
    """
    
    def __init__(self, session: MeetBotSession):
        self.session = session
        self.browser = None
        self.page = None
        self.transcription_manager = None
        self.is_recording = False
        self.temp_dir = None
        
    async def join_meeting(self) -> bool:
        """Join Google Meet using Puppeteer"""
        try:
            print(f"Bot joining meeting via Puppeteer: {self.session.meet_url}")
            
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix=f"meetbot_{self.session.session_id}_")
            
            # Launch browser with audio capture capabilities
            self.browser = await launch({
                'headless': False,  # Run with GUI for audio capture
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--use-fake-ui-for-media-stream',
                    '--use-fake-device-for-media-stream',
                    '--autoplay-policy=no-user-gesture-required',
                    '--enable-experimental-web-platform-features',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--flag-switches-begin',
                    '--enable-audio-service-sandbox=false',
                    '--flag-switches-end',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins',
                    '--disable-site-isolation-trials',
                    '--allow-running-insecure-content',
                ],
                'ignoreDefaultArgs': ['--mute-audio'],
                'userDataDir': os.path.join(self.temp_dir, 'chrome_data')
            })
            
            # Create new page
            self.page = await self.browser.newPage()
            
            # Set user agent to appear as real Chrome
            await self.page.setUserAgent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Navigate to meeting
            await self.page.goto(self.session.meet_url, {'waitUntil': 'networkidle2'})
            
            # Wait a bit for page to load
            await asyncio.sleep(3)
            
            # Join the meeting
            success = await self._join_meeting_flow()
            
            if success:
                # Start audio capture and transcription
                await self._setup_audio_capture()
                await self.session.start_recording()
                self.is_recording = True
                print("Bot successfully joined meeting and started recording")
                return True
            else:
                print("Failed to join meeting")
                return False
                
        except Exception as e:
            print(f"Error joining meeting with Puppeteer: {e}")
            return False
    
    async def _join_meeting_flow(self) -> bool:
        """Handle the Google Meet join flow"""
        try:
            # Wait for and handle permission prompts
            await self._handle_permissions()
            
            # Turn off camera and mic UI buttons
            await self._configure_media_settings()
            
            # Set bot name
            await self._set_bot_name()
            
            # Click join button
            await self._click_join_button()
            
            # Wait to ensure we're in the meeting
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"Error in join flow: {e}")
            return False
    
    async def _handle_permissions(self):
        """Handle browser permission prompts"""
        try:
            # Auto-accept any permission dialogs
            self.page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
            
            # Wait for any permission buttons and click them
            permission_selectors = [
                'button[aria-label*="Allow"]',
                'button[aria-label*="Got it"]',
                'button[jsname="b3VHJd"]',
                'button[jsname="Qx7uuf"]'
            ]
            
            for selector in permission_selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 1000})
                    await self.page.click(selector)
                    await asyncio.sleep(0.5)
                except:
                    pass  # Selector not found, continue
                    
        except Exception as e:
            print(f"Error handling permissions: {e}")
    
    async def _configure_media_settings(self):
        """Turn off camera and configure microphone"""
        try:
            # Turn off camera
            camera_selectors = [
                'div[data-tooltip*="camera"]',
                'button[aria-label*="camera"]',
                'div[jscontroller="R6JM3d"][data-tooltip*="camera"]'
            ]
            
            for selector in camera_selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 2000})
                    await self.page.click(selector)
                    break
                except:
                    pass
                    
            await asyncio.sleep(0.5)
            
            # Keep microphone on for audio capture
            mic_selectors = [
                'div[data-tooltip*="microphone"]',
                'button[aria-label*="microphone"]',
                'div[jscontroller="R6JM3d"][data-tooltip*="microphone"]'
            ]
            
            for selector in mic_selectors:
                try:
                    element = await self.page.querySelector(selector)
                    if element:
                        # Check if mic is off and turn it on
                        classes = await self.page.evaluate('(element) => element.className', element)
                        if 'FTMc0c' in str(classes):  # Off state class
                            await self.page.click(selector)
                    break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error configuring media: {e}")
    
    async def _set_bot_name(self):
        """Set the bot's display name"""
        try:
            # Look for name input field
            name_selectors = [
                'input[placeholder*="name"]',
                'input[aria-label*="name"]',
                'input[type="text"]'
            ]
            
            for selector in name_selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 2000})
                    await self.page.click(selector, {'clickCount': 3})  # Select all
                    await self.page.type(selector, 'AI Meeting Assistant')
                    break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error setting bot name: {e}")
    
    async def _click_join_button(self):
        """Click the join button"""
        try:
            join_selectors = [
                'button[jsname="Qx7uuf"]:not([aria-label*="microphone"]):not([aria-label*="camera"])',
                'button span[jsname="V67aGc"]:has-text("Join now")',
                'button:has-text("Join now")',
                'button:has-text("Ask to join")',
                'button[aria-label*="Join"]'
            ]
            
            for selector in join_selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 3000})
                    await self.page.click(selector)
                    print(f"Clicked join button: {selector}")
                    break
                except:
                    pass
                    
        except Exception as e:
            print(f"Error clicking join button: {e}")
    
    async def _setup_audio_capture(self):
        """Setup audio capture from the meeting"""
        try:
            # Initialize transcription manager
            self.transcription_manager = TranscriptionManager(self.session.session_id)
            
            # Start transcription
            success = await self.transcription_manager.start(
                on_live_update=self._handle_transcription_update
            )
            
            if not success:
                print("Failed to start transcription manager")
                return False
            
            # Inject audio capture script into the page
            await self._inject_audio_capture_script()
            
            return True
            
        except Exception as e:
            print(f"Error setting up audio capture: {e}")
            return False
    
    async def _inject_audio_capture_script(self):
        """Inject JavaScript to capture meeting audio"""
        audio_capture_script = """
        (() => {
            console.log('Injecting audio capture script...');
            
            // Capture audio from all video elements (participant streams)
            const captureAudioFromVideos = () => {
                const videos = document.querySelectorAll('video');
                const audioContext = new AudioContext();
                const destination = audioContext.createMediaStreamDestination();
                
                videos.forEach((video, index) => {
                    if (video.srcObject && video.srcObject instanceof MediaStream) {
                        try {
                            const source = audioContext.createMediaStreamSource(video.srcObject);
                            source.connect(destination);
                            console.log(`Connected audio from video ${index}`);
                        } catch (e) {
                            console.error(`Failed to capture audio from video ${index}:`, e);
                        }
                    }
                });
                
                // Get the mixed audio stream
                const mixedStream = destination.stream;
                
                // Set up MediaRecorder
                const mediaRecorder = new MediaRecorder(mixedStream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                // Send audio chunks to our server
                mediaRecorder.ondataavailable = async (event) => {
                    if (event.data.size > 0) {
                        // Convert to base64 and send to server
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64Audio = reader.result.split(',')[1];
                            // Send to server via WebSocket or fetch
                            window.postMessage({
                                type: 'audio_chunk',
                                data: base64Audio
                            }, '*');
                        };
                        reader.readAsDataURL(event.data);
                    }
                };
                
                // Start recording in chunks
                mediaRecorder.start(250); // 250ms chunks
                
                window.meetBotRecorder = mediaRecorder;
                console.log('Audio capture started');
            };
            
            // Wait for videos to be available
            const startCapture = () => {
                const videos = document.querySelectorAll('video');
                if (videos.length > 0) {
                    captureAudioFromVideos();
                } else {
                    setTimeout(startCapture, 1000);
                }
            };
            
            // Start after a delay
            setTimeout(startCapture, 3000);
            
            // Re-capture when new participants join
            const observer = new MutationObserver(() => {
                const videos = document.querySelectorAll('video');
                if (videos.length > window.lastVideoCount || 0) {
                    window.lastVideoCount = videos.length;
                    captureAudioFromVideos();
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        })();
        """
        
        await self.page.evaluateOnNewDocument(audio_capture_script)
        
        # Listen for audio chunks
        await self.page.evaluateHandle("""
            window.addEventListener('message', async (event) => {
                if (event.data.type === 'audio_chunk') {
                    // Forward to Python via console.log (intercepted by Puppeteer)
                    console.log('AUDIO_CHUNK:' + event.data.data);
                }
            });
        """)
        
        # Intercept console logs for audio data
        self.page.on('console', self._handle_console_message)
    
    async def _handle_console_message(self, msg):
        """Handle console messages from the page"""
        text = msg.text()
        if text.startswith('AUDIO_CHUNK:'):
            # Extract base64 audio data
            base64_audio = text[12:]
            audio_bytes = base64.b64decode(base64_audio)
            
            # Send to Deepgram
            if self.transcription_manager:
                await self.transcription_manager.send_audio(audio_bytes)
    
    async def _handle_transcription_update(self, data: Dict[str, Any]):
        """Handle transcription updates from Deepgram"""
        try:
            if data.get('type') == 'transcript' and data.get('data', {}).get('is_final'):
                transcript_text = data['data'].get('transcript', '')
                speaker_segments = data['data'].get('speaker_segments', [])
                
                if speaker_segments:
                    for segment in speaker_segments:
                        speaker_id = segment.get('speaker', 0)
                        text = segment.get('text', '').strip()
                        if text:
                            await self.session.add_transcript_chunk(
                                text, 
                                speaker=f"Speaker {speaker_id + 1}"
                            )
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
            
            # Close browser
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            # Stop session recording
            await self.session.stop_recording()
            
            # Cleanup temp files
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            print("Bot successfully left meeting")
            
        except Exception as e:
            print(f"Error leaving meeting: {e}")