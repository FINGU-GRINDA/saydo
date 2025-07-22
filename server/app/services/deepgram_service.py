from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
from typing import Optional, Callable, Dict, Any
import asyncio
import json
from config import settings


class DeepgramTranscriptionService:
    def __init__(self):
        self.client = DeepgramClient(settings.deepgram_api_key)
        self.connection = None
        self.transcript_callback = None
        self.speakers = {}  # Track speaker identities
        
    async def start_transcription(
        self, 
        on_transcript: Callable[[Dict[str, Any]], None],
        on_speaker_change: Optional[Callable[[int, str], None]] = None
    ):
        """Start live transcription with speaker diarization"""
        
        # Store callbacks
        self.transcript_callback = on_transcript
        self.speaker_change_callback = on_speaker_change
        
        # Create websocket connection
        self.connection = self.client.listen.asyncwebsocket.v("1")
        
        # Configure handlers
        self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
        self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
        self.connection.on(LiveTranscriptionEvents.Error, self._on_error)
        self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
        
        # Configure options with diarization
        options = LiveOptions(
            model="nova-3",
            language="en-US",
            punctuate=True,
            smart_format=True,
            diarize=True,  # Enable speaker identification
            interim_results=True,  # Get real-time results
            utterance_end_ms=1000,  # End utterance after 1 second of silence
            vad_events=True,  # Voice activity detection
            endpointing=300  # Milliseconds of silence before finalizing
        )
        
        # Start the connection
        if await self.connection.start(options):
            print("Deepgram connection opened")
            return True
        return False
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to Deepgram"""
        if self.connection and self.connection.is_connected():
            await self.connection.send(audio_data)
    
    async def stop_transcription(self):
        """Stop the transcription and close connection"""
        if self.connection:
            await self.connection.finish()
            self.connection = None
    
    def _on_open(self, *args, **kwargs):
        print("Deepgram connection opened")
    
    def _on_transcript(self, *args, **kwargs):
        result = kwargs.get("result")
        if not result:
            return
            
        # Extract transcript data
        channel = result.channel
        alternatives = channel.alternatives
        
        if not alternatives:
            return
            
        alternative = alternatives[0]
        transcript = alternative.transcript
        
        if not transcript:
            return
        
        # Process speaker information if available
        words = alternative.words if hasattr(alternative, 'words') else []
        speaker_segments = []
        
        current_speaker = None
        current_text = []
        
        for word in words:
            speaker_id = word.speaker if hasattr(word, 'speaker') else 0
            
            if current_speaker is None:
                current_speaker = speaker_id
                
            if speaker_id != current_speaker:
                # Speaker changed, save the segment
                if current_text:
                    speaker_segments.append({
                        "speaker": current_speaker,
                        "text": " ".join(current_text)
                    })
                current_speaker = speaker_id
                current_text = [word.word]
            else:
                current_text.append(word.word)
        
        # Add the last segment
        if current_text:
            speaker_segments.append({
                "speaker": current_speaker,
                "text": " ".join(current_text)
            })
        
        # Create transcript data
        transcript_data = {
            "transcript": transcript,
            "is_final": result.is_final if hasattr(result, 'is_final') else True,
            "speaker_segments": speaker_segments,
            "confidence": alternative.confidence if hasattr(alternative, 'confidence') else 1.0,
            "duration": result.duration if hasattr(result, 'duration') else 0,
            "start": result.start if hasattr(result, 'start') else 0
        }
        
        # Call the callback
        if self.transcript_callback:
            self.transcript_callback(transcript_data)
    
    def _on_error(self, *args, **kwargs):
        error = kwargs.get("error")
        print(f"Deepgram error: {error}")
    
    def _on_close(self, *args, **kwargs):
        print("Deepgram connection closed")


class TranscriptionManager:
    """Manages transcription for a meeting"""
    
    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.service = DeepgramTranscriptionService()
        self.full_transcript = []
        self.speaker_map = {}  # Map speaker IDs to names
        
    async def start(self):
        """Start transcription for the meeting"""
        await self.service.start_transcription(
            on_transcript=self._handle_transcript
        )
    
    def _handle_transcript(self, data: Dict[str, Any]):
        """Handle incoming transcript data"""
        if data.get("is_final"):
            # Store final transcript
            self.full_transcript.append({
                "timestamp": data.get("start", 0),
                "duration": data.get("duration", 0),
                "segments": data.get("speaker_segments", []),
                "text": data.get("transcript", "")
            })
    
    async def send_audio(self, audio_data: bytes):
        """Forward audio to transcription service"""
        await self.service.send_audio(audio_data)
    
    async def stop(self):
        """Stop transcription and return results"""
        await self.service.stop_transcription()
        return self.get_formatted_transcript()
    
    def get_formatted_transcript(self) -> str:
        """Get the full transcript formatted with speakers"""
        formatted_lines = []
        
        for entry in self.full_transcript:
            for segment in entry.get("segments", []):
                speaker_id = segment.get("speaker", 0)
                speaker_name = self.speaker_map.get(speaker_id, f"Speaker {speaker_id + 1}")
                text = segment.get("text", "")
                
                if text.strip():
                    formatted_lines.append(f"{speaker_name}: {text}")
        
        return "\n".join(formatted_lines)
    
    def set_speaker_name(self, speaker_id: int, name: str):
        """Map a speaker ID to a name"""
        self.speaker_map[speaker_id] = name