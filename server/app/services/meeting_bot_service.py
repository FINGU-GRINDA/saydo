"""
Meeting Bot Service using cloud-based solutions
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime
import os

from .meet_bot import MeetBotSession
from .deepgram_transcription import TranscriptionManager
from config import settings


class CloudMeetingBot:
    """
    Cloud-based meeting bot that can actually hear audio
    Options:
    1. Recall.ai - Meeting bot infrastructure as a service
    2. Symbl.ai - Real-time conversation intelligence
    3. Custom WebRTC solution with media servers
    """
    
    def __init__(self, session: MeetBotSession):
        self.session = session
        self.bot_id = None
        self.is_recording = False
        
        # Choose your service (we'll use Recall.ai as example)
        self.api_key = settings.recall_ai_api_key
        self.region = settings.recall_ai_region
        self.base_url = f'https://{self.region}.recall.ai/api/v1'
        
    async def join_meeting(self) -> bool:
        """Deploy a cloud bot to join the meeting"""
        try:
            print(f"Recall.ai API key present: {bool(self.api_key)}")
            print(f"API key length: {len(self.api_key) if self.api_key else 0}")
            print(f"Region: {self.region}")
            print(f"Base URL: {self.base_url}")
            
            # Option 1: Use Recall.ai (they handle the bot infrastructure)
            if self.api_key:
                print("Using Recall.ai for bot deployment...")
                return await self._join_with_recall_ai()
            
            # Option 2: Use our own WebRTC solution
            else:
                print("No Recall.ai API key found, falling back to WebRTC mock...")
                return await self._join_with_webrtc()
                
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False
    
    async def _join_with_recall_ai(self) -> bool:
        """Use Recall.ai to join the meeting"""
        try:
            async with aiohttp.ClientSession() as session:
                # Create a bot using Recall.ai format
                headers = {
                    'Authorization': f'Token {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                bot_data = {
                    "meeting_url": self.session.meet_url,
                    "bot_name": "Rinda AI Meeting Assistant",
                    "recording_config": {
                        "transcript": {
                            "provider": {
                                "meeting_captions": {}
                            }
                        }
                    }
                }
                
                print(f"Making API call to: {self.base_url}/bot")
                print(f"Headers: {headers}")
                print(f"Bot data: {bot_data}")
                
                async with session.post(
                    f'{self.base_url}/bot',
                    headers=headers,
                    json=bot_data
                ) as resp:
                    print(f"Response status: {resp.status}")
                    response_text = await resp.text()
                    print(f"Response body: {response_text}")
                    
                    if resp.status == 201:
                        data = await resp.json()
                        self.bot_id = data['id']
                        
                        # Start recording
                        await self.session.start_recording()
                        self.is_recording = True
                        
                        print(f"Recall.ai bot created with ID: {self.bot_id}")
                        
                        # Start polling for transcript in background
                        asyncio.create_task(self._poll_for_transcript())
                        
                        return True
                    else:
                        print(f"Failed to create Recall.ai bot: Status {resp.status}, Response: {response_text}")
                        return False
                        
        except Exception as e:
            print(f"Error with Recall.ai: {e}")
            return False
    
    async def _poll_for_transcript(self):
        """Poll Recall.ai for transcript updates"""
        print(f"🔄 Started transcript polling for bot {self.bot_id}")
        poll_count = 0
        self._polling_active = True
        
        while self._polling_active and self.bot_id:
            try:
                poll_count += 1
                print(f"📡 Polling attempt #{poll_count} for bot {self.bot_id}")
                
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f'Token {self.api_key}'
                    }
                    
                    # First get bot status
                    async with session.get(
                        f'{self.base_url}/bot/{self.bot_id}',
                        headers=headers
                    ) as resp:
                        if resp.status == 200:
                            bot_data = await resp.json()
                            status_changes = bot_data.get('status_changes', [])
                            latest_statuses = [s.get('code', 'unknown') for s in status_changes[-3:]]
                            print(f"📊 Bot status: {latest_statuses}")
                            
                            # Check if bot is done (transcripts available)
                            bot_is_done = 'done' in latest_statuses
                            bot_is_active = any(status in ['recording', 'in_call_recording', 'in_call_not_recording'] 
                                              for status in latest_statuses)
                            bot_is_waiting = 'in_waiting_room' in latest_statuses
                            
                            if bot_is_done:
                                print(f"✅ Bot finished recording, getting final transcript...")
                                # Get final transcript and stop polling
                                await self._get_final_transcript()
                                self._polling_active = False
                                break
                            elif bot_is_active:
                                print(f"🟡 Bot is active, checking for available transcripts...")
                                # Check for any completed transcripts during recording
                                await self._check_active_transcripts(session, headers, bot_data)
                                # Increase poll interval for active bots
                                await asyncio.sleep(20)  # Wait longer between polls
                                continue
                            elif bot_is_waiting and poll_count > 20:
                                print(f"⚠️  Bot stuck in waiting room for {poll_count} attempts")
                                print(f"   This might indicate the meeting requires manual admission")
                                await asyncio.sleep(30)  # Even longer wait
                                continue
                            elif bot_is_waiting:
                                print(f"⏳ Bot waiting to join (attempt {poll_count})")
                                continue
                            else:
                                print(f"⏳ Bot not ready yet, skipping transcript check")
                                continue
                                
                        else:
                            print(f"❌ Failed to get bot status: {resp.status}")
                            continue
                    
                
                # Poll every 10 seconds
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"Error polling transcript: {e}")
                await asyncio.sleep(10)
        
        print(f"🛑 Stopped transcript polling for bot {self.bot_id}")
    
    async def _get_final_transcript(self):
        """Get the final transcript when bot is done"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.api_key}'
                }
                
                # First get bot recordings to find transcript IDs
                async with session.get(
                    f'{self.base_url}/bot/{self.bot_id}',
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        bot_data = await resp.json()
                        recordings = bot_data.get('recordings', [])
                        print(f"🎥 Found {len(recordings)} recording(s)")
                        
                        for recording in recordings:
                            recording_id = recording.get('id')
                            print(f"🎬 Processing recording: {recording_id}")
                            if recording_id:
                                await self._get_recording_transcript(session, headers, recording_id)
                            else:
                                print(f"⚠️  Recording missing ID: {recording}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ Failed to get bot data: {resp.status} - {error_text[:100]}")
                        
        except Exception as e:
            print(f"Error getting final transcript: {e}")
    
    async def _get_recording_transcript(self, session, headers, recording_id):
        """Get transcript for a specific recording"""
        try:
            # List transcripts for this recording
            async with session.get(
                f'{self.base_url}/transcript/',
                headers=headers,
                params={'recording_id': recording_id}
            ) as resp:
                if resp.status == 200:
                    transcript_list = await resp.json()
                    transcripts = transcript_list.get('results', [])
                    print(f"📝 Found {len(transcripts)} transcript(s) for recording {recording_id}")
                    
                    for transcript_info in transcripts:
                        transcript_id = transcript_info.get('id')
                        # Status is nested in status.code, not status_code
                        status_obj = transcript_info.get('status', {})
                        status = status_obj.get('code', 'unknown')
                        
                        print(f"🔍 Transcript {transcript_id} has status: {status}")
                        
                        if status in ['done', 'unknown'] and transcript_id:
                            print(f"✅ Processing transcript {transcript_id} (status: {status})")
                            await self._fetch_transcript_content(session, headers, transcript_id)
                        elif status == 'processing':
                            print(f"⏳ Transcript {transcript_id} still processing")
                        elif status == 'failed':
                            print(f"❌ Transcript {transcript_id} failed to process")
                        else:
                            print(f"❓ Transcript {transcript_id} has unhandled status: {status}")
                else:
                    error_text = await resp.text()
                    print(f"❌ Failed to list transcripts: {resp.status} - {error_text[:100]}")
        except Exception as e:
            print(f"Error getting recording transcript: {e}")
    
    async def _fetch_transcript_content(self, session, headers, transcript_id):
        """Fetch the actual transcript content"""
        try:
            async with session.get(
                f'{self.base_url}/transcript/{transcript_id}/',
                headers=headers
            ) as resp:
                if resp.status == 200:
                    transcript_data = await resp.json()
                    print(f"📄 Retrieved transcript {transcript_id}")
                    print(f"🔍 Transcript data structure: {list(transcript_data.keys())}")
                    print(f"🔍 Full transcript response: {transcript_data}")
                    await self._process_recall_transcript(transcript_data)
                else:
                    error_text = await resp.text()
                    print(f"❌ Failed to get transcript content: {resp.status} - {error_text[:100]}")
        except Exception as e:
            print(f"Error fetching transcript content: {e}")
    
    async def _process_recall_transcript(self, transcript_data):
        """Process transcript data from Recall.ai transcript endpoint"""
        try:
            # Check if we have a download URL for the transcript content
            data = transcript_data.get('data', {})
            download_url = data.get('download_url')
            
            if download_url:
                print(f"🔗 Found transcript download URL, fetching content...")
                await self._fetch_transcript_from_url(download_url)
                return
            
            # Fallback: try to parse direct transcript content
            words = transcript_data.get('words', [])
            utterances = transcript_data.get('utterances', [])
            
            if utterances:
                # Process utterances (speaker-separated segments)
                for utterance in utterances:
                    speaker = utterance.get('speaker', 'Unknown')
                    text = utterance.get('text', '').strip()
                    if text:
                        await self.session.add_transcript_chunk(text, speaker=speaker)
                        print(f"📝 Added transcript: {speaker}: {text[:50]}...")
                        
            elif words:
                # Fallback to word-level processing
                current_speaker = None
                current_text = ""
                
                for word_entry in words:
                    word = word_entry.get('word', '')
                    speaker = word_entry.get('speaker', 'Unknown')
                    
                    if current_speaker != speaker and current_text:
                        # Speaker changed, process current text
                        await self.session.add_transcript_chunk(
                            current_text.strip(), 
                            speaker=current_speaker
                        )
                        print(f"📝 Added transcript: {current_speaker}: {current_text[:50]}...")
                        current_text = ""
                    
                    current_speaker = speaker
                    current_text += word + " "
                
                # Process final text
                if current_text:
                    await self.session.add_transcript_chunk(
                        current_text.strip(), 
                        speaker=current_speaker
                    )
                    print(f"📝 Added transcript: {current_speaker}: {current_text[:50]}...")
            else:
                print(f"⚠️  No transcript content found in response")
                
        except Exception as e:
            print(f"Error processing Recall.ai transcript: {e}")
    
    async def _fetch_transcript_from_url(self, download_url):
        """Fetch transcript content from download URL"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.api_key}'
                }
                
                async with session.get(download_url, headers=headers) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            transcript_content = await resp.json()
                            print(f"📄 Downloaded JSON transcript content: {transcript_content}")
                            await self._parse_downloaded_transcript(transcript_content)
                        else:
                            # Plain text transcript
                            transcript_text = await resp.text()
                            print(f"📄 Downloaded text transcript: {len(transcript_text)} chars")
                            if transcript_text.strip():
                                await self.session.add_transcript_chunk(transcript_text.strip())
                                print(f"📝 Added full transcript: {transcript_text[:100]}...")
                    else:
                        error_text = await resp.text()
                        print(f"❌ Failed to download transcript: {resp.status} - {error_text[:100]}")
        except Exception as e:
            print(f"Error fetching transcript from URL: {e}")
    
    async def _parse_downloaded_transcript(self, transcript_content):
        """Parse downloaded JSON transcript content based on Recall.ai schema"""
        try:
            print(f"🔍 Parsing transcript content type: {type(transcript_content)}")
            
            if isinstance(transcript_content, dict):
                print(f"🔍 Dict keys available: {list(transcript_content.keys())}")
                
                # Handle Recall.ai transcript structure with parts
                if 'parts' in transcript_content:
                    parts = transcript_content.get('parts', [])
                    print(f"📋 Found {len(parts)} transcript parts")
                    
                    for part in parts:
                        await self._process_transcript_part(part)
                        
                # Handle word-level transcript data (array format)  
                elif isinstance(transcript_content, list):
                    print(f"📋 Processing {len(transcript_content)} transcript entries")
                    for entry in transcript_content:
                        participant = entry.get('participant', {})
                        speaker_name = participant.get('name', 'Unknown')
                        words = entry.get('words', [])
                        
                        if words:
                            # Combine words into sentences
                            full_text = ' '.join(word.get('text', '') for word in words if word.get('text'))
                            if full_text.strip():
                                await self.session.add_transcript_chunk(full_text.strip(), speaker=speaker_name)
                                print(f"📝 Added transcript: {speaker_name}: {full_text[:50]}...")
                
                # Fallback: try direct text content
                elif 'text' in transcript_content:
                    text = transcript_content['text'].strip()
                    if text:
                        await self.session.add_transcript_chunk(text)
                        print(f"📝 Added direct text: {text[:50]}...")
                        
                else:
                    print(f"❓ Unknown transcript structure: {transcript_content}")
                    
            elif isinstance(transcript_content, list):
                print(f"📋 Processing transcript list with {len(transcript_content)} entries")
                # Handle list format - combine consecutive entries from same speaker
                combined_entries = []
                current_speaker = None
                current_text = []
                
                for entry in transcript_content:
                    if isinstance(entry, dict):
                        participant = entry.get('participant', {})
                        speaker_name = participant.get('name', 'Unknown')
                        words = entry.get('words', [])
                        
                        if words:
                            text = ' '.join(word.get('text', '') for word in words if word.get('text'))
                            
                            # If speaker changed, save current and start new
                            if current_speaker != speaker_name and current_text:
                                combined_text = ' '.join(current_text).strip()
                                if combined_text:
                                    await self.session.add_transcript_chunk(combined_text, speaker=current_speaker)
                                    print(f"📝 Added transcript: {current_speaker}: {combined_text[:50]}...")
                                current_text = []
                            
                            current_speaker = speaker_name
                            if text.strip():
                                current_text.append(text.strip())
                
                # Add final speaker's text
                if current_text:
                    combined_text = ' '.join(current_text).strip()
                    if combined_text:
                        await self.session.add_transcript_chunk(combined_text, speaker=current_speaker)
                        print(f"📝 Added transcript: {current_speaker}: {combined_text[:50]}...")
                                
            elif isinstance(transcript_content, str):
                # Direct text content
                if transcript_content.strip():
                    await self.session.add_transcript_chunk(transcript_content.strip())
                    print(f"📝 Added transcript string: {transcript_content[:50]}...")
                    
        except Exception as e:
            print(f"Error parsing downloaded transcript: {e}")
    
    async def _process_transcript_part(self, part):
        """Process individual transcript part from Recall.ai format"""
        try:
            part_id = part.get('id', 'unknown')
            source_audio = part.get('source_audio', {})
            participant = source_audio.get('participant', {})
            speaker_name = participant.get('name', 'Unknown')
            
            # Extract data based on part type
            part_type = part.get('type', 'unknown')
            data = part.get('data', {})
            
            print(f"🔍 Processing part {part_id}, type: {part_type}")
            
            if part_type == 'webhook' and 'payload' in data:
                payload = data['payload']
                # Check if payload contains transcript text
                if isinstance(payload, dict) and 'text' in payload:
                    text = payload['text'].strip()
                    if text:
                        await self.session.add_transcript_chunk(text, speaker=speaker_name)
                        print(f"📝 Added webhook transcript: {speaker_name}: {text[:50]}...")
                        
            elif part_type == 'http_response' and 'body' in data:
                body = data['body']
                if isinstance(body, dict) and 'text' in body:
                    text = body['text'].strip()
                    if text:
                        await self.session.add_transcript_chunk(text, speaker=speaker_name)
                        print(f"📝 Added HTTP response transcript: {speaker_name}: {text[:50]}...")
                        
            elif part_type == 'websocket_message' and 'payload' in data:
                payload = data['payload']
                if isinstance(payload, dict) and 'text' in payload:
                    text = payload['text'].strip()
                    if text:
                        await self.session.add_transcript_chunk(text, speaker=speaker_name)
                        print(f"📝 Added WebSocket transcript: {speaker_name}: {text[:50]}...")
                        
        except Exception as e:
            print(f"Error processing transcript part: {e}")
    
    async def _check_active_transcripts(self, session, headers, bot_data):
        """Check for available transcripts during active recording"""
        try:
            recordings = bot_data.get('recordings', [])
            for recording in recordings:
                recording_id = recording.get('id')
                if recording_id:
                    # Check if there are any completed transcripts for this recording
                    async with session.get(
                        f'{self.base_url}/transcript/',
                        headers=headers,
                        params={'recording_id': recording_id, 'status_code': 'done'}
                    ) as resp:
                        if resp.status == 200:
                            transcript_list = await resp.json()
                            transcripts = transcript_list.get('results', [])
                            
                            for transcript_info in transcripts:
                                transcript_id = transcript_info.get('id')
                                if transcript_id and not hasattr(self, '_processed_transcripts'):
                                    self._processed_transcripts = set()
                                
                                if transcript_id and transcript_id not in self._processed_transcripts:
                                    await self._fetch_transcript_content(session, headers, transcript_id)
                                    self._processed_transcripts.add(transcript_id)
        except Exception as e:
            print(f"Error checking active transcripts: {e}")
    
    async def _process_transcript_entry(self, transcript_entry):
        """Process a transcript entry from the transcript endpoint"""
        try:
            # Check if we've already processed this transcript
            transcript_id = transcript_entry.get('id')
            if hasattr(self, '_processed_transcripts'):
                if transcript_id in self._processed_transcripts:
                    return  # Already processed
            else:
                self._processed_transcripts = set()
            
            # Get the transcript text
            words = transcript_entry.get('words', [])
            if words:
                # Combine words into sentences, grouping by speaker
                current_speaker = None
                current_text = ""
                
                for word_entry in words:
                    word = word_entry.get('word', '')
                    speaker = word_entry.get('speaker', 0)
                    
                    if current_speaker != speaker and current_text:
                        # Speaker changed, process current text
                        await self.session.add_transcript_chunk(
                            current_text.strip(), 
                            speaker=f"Speaker {current_speaker}"
                        )
                        print(f"📝 Added transcript: Speaker {current_speaker}: {current_text[:50]}...")
                        current_text = ""
                    
                    current_speaker = speaker
                    current_text += word + " "
                
                # Process final text
                if current_text:
                    await self.session.add_transcript_chunk(
                        current_text.strip(), 
                        speaker=f"Speaker {current_speaker}"
                    )
                    print(f"📝 Added transcript: Speaker {current_speaker}: {current_text[:50]}...")
                
                # Mark as processed
                self._processed_transcripts.add(transcript_id)
                
        except Exception as e:
            print(f"Error processing transcript entry: {e}")
    
    async def _join_with_webrtc(self) -> bool:
        """Use WebRTC media server to join the meeting"""
        try:
            # This would connect to your own media server infrastructure
            # Options include:
            # - Kurento Media Server
            # - Jitsi Videobridge
            # - mediasoup
            # - Janus Gateway
            
            print("WebRTC solution not implemented - using mock data")
            
            # For demo purposes, simulate joining
            await self.session.start_recording()
            self.is_recording = True
            
            # Simulate some transcript data after a delay
            asyncio.create_task(self._simulate_meeting_audio())
            
            return True
            
        except Exception as e:
            print(f"Error with WebRTC: {e}")
            return False
    
    async def _simulate_meeting_audio(self):
        """Simulate meeting audio for demo purposes"""
        await asyncio.sleep(5)
        
        # Add some sample transcript
        sample_conversations = [
            ("John", "Hello everyone, thanks for joining today's meeting."),
            ("Sarah", "Hi John, glad to be here. Should we start with the project updates?"),
            ("John", "Yes, let's do that. Sarah, can you share the latest on the AI integration?"),
            ("Sarah", "Absolutely. We've completed the Google Meet bot integration and it's now capturing audio in real-time."),
            ("Mike", "That's great progress! How's the accuracy of the transcription?"),
            ("Sarah", "With Deepgram's speaker diarization, we're seeing about 95% accuracy."),
            ("John", "Excellent. What about the action items extraction?"),
            ("Sarah", "The AI is successfully identifying action items and can create calendar events and draft emails."),
            ("Mike", "Can we see a demo in our next meeting?"),
            ("John", "Good idea. Let's schedule that for next Tuesday. Sarah, can you prepare the demo?"),
            ("Sarah", "Sure, I'll have it ready by Tuesday."),
            ("John", "Perfect. Any other updates before we wrap up?"),
            ("Mike", "Just a reminder about the client presentation on Friday."),
            ("John", "Right, thanks Mike. Let's make sure everything is polished by Thursday."),
            ("Sarah", "I'll send out the updated slides by end of day Wednesday."),
            ("John", "Great, thanks everyone. Let's catch up again on Tuesday.")
        ]
        
        # Add transcript chunks with delays
        for speaker, text in sample_conversations:
            await self.session.add_transcript_chunk(text, speaker=speaker)
            await asyncio.sleep(2)  # Simulate real-time speech
    
    async def leave_meeting(self):
        """Mark session as stopped but keep bot polling until meeting ends"""
        try:
            print(f"📱 UI requested stop for bot {self.bot_id}")
            print(f"   Bot will continue polling until meeting ends and transcript is available")
            
            # Mark session as stopped for UI purposes but keep bot active
            await self.session.stop_recording()
            
            if self.bot_id and self.api_key:
                print(f"ℹ️  Bot {self.bot_id} will continue monitoring until meeting ends")
                print(f"   (Recall.ai bots leave automatically and provide transcript when done)")
            
        except Exception as e:
            print(f"Error during stop: {e}")
            
    async def force_cleanup(self):
        """Force stop polling (called when session is actually ending)"""
        try:
            self._polling_active = False
            self.is_recording = False
            print(f"🛑 Force stopping transcript polling for bot {self.bot_id}")
        except Exception as e:
            print(f"Error during force cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "session_id": self.session.session_id,
            "is_recording": self.is_recording,
            "bot_id": self.bot_id,
            "service": "recall.ai" if self.api_key else "webrtc",
            "meet_url": self.session.meet_url,
            "status": self.session.status
        }


class MeetingBotOrchestrator:
    """Manages cloud-based meeting bots"""
    
    def __init__(self):
        self.active_bots: Dict[str, CloudMeetingBot] = {}
    
    async def create_and_join_meeting(self, user_id: str, meet_url: str) -> Dict[str, Any]:
        """Create bot session and join meeting"""
        try:
            from .meet_bot import meet_bot_manager
            
            # Create session
            session = await meet_bot_manager.create_session(user_id, meet_url)
            
            # Create cloud bot
            bot = CloudMeetingBot(session)
            self.active_bots[session.session_id] = bot
            
            # Join meeting
            success = await bot.join_meeting()
            
            if success:
                return {
                    "session_id": session.session_id,
                    "status": "recording",
                    "message": "Cloud bot successfully joined meeting",
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
            # Bot is in memory - normal path
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
            # Bot not in memory (server restart) - try to get transcript from Recall.ai
            print(f"⚠️  Bot session {session_id} not found in memory (server restart?)")
            print(f"   Attempting to retrieve final transcript from external sources...")
            
            try:
                # Try to get session info from meet_bot_manager
                from .meet_bot import meet_bot_manager
                session = meet_bot_manager.get_session(session_id)
                
                if session:
                    await session.stop_recording()
                    return {
                        "session_id": session_id,
                        "status": "completed",
                        "transcript": session.transcript or "",
                        "summary": session.summary or "",
                        "actions": session.actions or []
                    }
                else:
                    # Session not found anywhere - try to reconstruct from Firebase
                    print(f"⚠️  Session {session_id} not found in session manager")
                    print(f"   Checking Firebase for bot information...")
                    
                    # Try to get bot ID from Firebase meeting record
                    transcript_result = await self._try_recover_transcript_from_firebase(session_id)
                    if transcript_result:
                        return transcript_result
                    
                    # Final fallback - return empty result
                    print(f"⚠️  Could not recover transcript for session {session_id}")
                    return {
                        "session_id": session_id,
                        "status": "completed", 
                        "transcript": "",
                        "summary": "Session data not available (server restart)",
                        "actions": []
                    }
                    
            except Exception as e:
                print(f"Error retrieving session data: {e}")
                return {
                    "session_id": session_id,
                    "status": "error",
                    "transcript": "",
                    "summary": f"Error retrieving session: {str(e)}",
                    "actions": []
                }
    
    async def _try_recover_transcript_from_firebase(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Try to recover transcript by looking up bot ID in Firebase"""
        try:
            from .firebase_service import firebase_service
            
            # Look for meetings where the session_id might be stored
            # This is a simplified approach - in production you'd want better indexing
            print(f"🔍 Searching Firebase for session {session_id}")
            
            # For now, return None as we'd need to implement Firebase bot ID storage
            # In a production system, you'd store bot_id in the meeting record when creating the bot
            print(f"⚠️  Firebase recovery not implemented yet")
            print(f"   To fix this: store bot_id in Firebase meeting record during bot creation")
            
            return None
            
        except Exception as e:
            print(f"Error during Firebase recovery: {e}")
            return None
    
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
meeting_bot_orchestrator = MeetingBotOrchestrator()