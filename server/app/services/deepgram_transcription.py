from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
from typing import Optional, Callable, Dict, Any, List
import asyncio
import json
from datetime import datetime
from config import settings


class DeepgramTranscriptionService:
    def __init__(self):
        self.client = DeepgramClient(settings.deepgram_api_key)
        self.connection = None
        self.transcript_callback = None
        self.speaker_change_callback = None
        self.is_connected = False
        
    async def start_transcription(
        self, 
        on_transcript: Callable[[Dict[str, Any]], None],
        on_speaker_change: Optional[Callable[[int, str], None]] = None
    ):
        """Start live transcription with speaker diarization"""
        
        # Store callbacks
        self.transcript_callback = on_transcript
        self.speaker_change_callback = on_speaker_change
        
        try:
            # Create websocket connection
            self.connection = self.client.listen.live.v("1")
            
            # Configure options with diarization
            options = LiveOptions(
                model="nova-2",  # Latest stable model
                language="en-US",
                punctuate=True,
                smart_format=True,
                diarize=True,  # Enable speaker identification
                interim_results=True,  # Get real-time results
                utterance_end_ms=1000,  # End utterance after 1 second of silence
                vad_events=True,  # Voice activity detection
                endpointing=300,  # Milliseconds of silence before finalizing
                encoding="linear16",  # Audio encoding
                sample_rate=16000  # Sample rate
            )
            
            # Define event handlers
            self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
            self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
            self.connection.on(LiveTranscriptionEvents.Metadata, self._on_metadata)
            self.connection.on(LiveTranscriptionEvents.Error, self._on_error)
            self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
            
            # Start the connection
            if self.connection.start(options):
                self.is_connected = True
                print("Deepgram connection opened successfully")
                return True
                
        except Exception as e:
            print(f"Failed to start Deepgram connection: {e}")
            self.is_connected = False
            return False
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to Deepgram"""
        if self.connection and self.is_connected:
            try:
                self.connection.send(audio_data)
            except Exception as e:
                print(f"Error sending audio to Deepgram: {e}")
    
    async def stop_transcription(self):
        """Stop the transcription and close connection"""
        if self.connection:
            try:
                self.connection.finish()
                self.is_connected = False
            except Exception as e:
                print(f"Error closing Deepgram connection: {e}")
            finally:
                self.connection = None
    
    def _on_open(self, *args, **kwargs):
        print("Deepgram WebSocket opened")
    
    def _on_metadata(self, *args, **kwargs):
        """Handle metadata events"""
        metadata = kwargs.get("metadata")
        if metadata:
            print(f"Deepgram metadata: {metadata}")
    
    def _on_transcript(self, *args, **kwargs):
        """Handle transcript events with speaker diarization"""
        result = kwargs.get("result")
        if not result:
            return
            
        try:
            # Extract transcript data
            channel = result.channel
            alternatives = channel.alternatives
            
            if not alternatives:
                return
                
            alternative = alternatives[0]
            transcript = alternative.transcript
            
            if not transcript:
                return
            
            # Process speaker information
            words = alternative.words if hasattr(alternative, 'words') else []
            speaker_segments = self._process_speaker_segments(words)
            
            # Create transcript data
            transcript_data = {
                "transcript": transcript,
                "is_final": result.is_final if hasattr(result, 'is_final') else True,
                "speaker_segments": speaker_segments,
                "confidence": alternative.confidence if hasattr(alternative, 'confidence') else 1.0,
                "duration": result.duration if hasattr(result, 'duration') else 0,
                "start": result.start if hasattr(result, 'start') else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call the callback
            if self.transcript_callback:
                self.transcript_callback(transcript_data)
                
        except Exception as e:
            print(f"Error processing transcript: {e}")
    
    def _process_speaker_segments(self, words: List[Any]) -> List[Dict[str, Any]]:
        """Process words into speaker segments"""
        if not words:
            return []
            
        segments = []
        current_speaker = None
        current_text = []
        current_start = None
        
        for word in words:
            try:
                speaker_id = word.speaker if hasattr(word, 'speaker') else 0
                word_text = word.word if hasattr(word, 'word') else word.punctuated_word
                start_time = word.start if hasattr(word, 'start') else 0
                end_time = word.end if hasattr(word, 'end') else 0
                
                if current_speaker is None:
                    current_speaker = speaker_id
                    current_start = start_time
                    
                if speaker_id != current_speaker:
                    # Speaker changed, save the segment
                    if current_text:
                        segments.append({
                            "speaker": current_speaker,
                            "text": " ".join(current_text),
                            "start": current_start,
                            "end": end_time
                        })
                        
                        # Notify about speaker change if callback provided
                        if self.speaker_change_callback:
                            self.speaker_change_callback(speaker_id, f"Speaker {speaker_id + 1}")
                    
                    current_speaker = speaker_id
                    current_text = [word_text]
                    current_start = start_time
                else:
                    current_text.append(word_text)
                    
            except Exception as e:
                print(f"Error processing word: {e}")
        
        # Add the last segment
        if current_text and current_speaker is not None:
            segments.append({
                "speaker": current_speaker,
                "text": " ".join(current_text),
                "start": current_start,
                "end": words[-1].end if hasattr(words[-1], 'end') else 0
            })
        
        return segments
    
    def _on_error(self, *args, **kwargs):
        error = kwargs.get("error")
        print(f"Deepgram error: {error}")
        self.is_connected = False
    
    def _on_close(self, *args, **kwargs):
        print("Deepgram connection closed")
        self.is_connected = False


class TranscriptionManager:
    """Manages transcription for a meeting with speaker identification"""
    
    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.service = DeepgramTranscriptionService()
        self.full_transcript = []
        self.speaker_map = {}  # Map speaker IDs to names
        self.current_speakers = set()  # Track active speakers
        
    async def start(self, on_live_update: Optional[Callable[[Dict[str, Any]], None]] = None):
        """Start transcription for the meeting"""
        self.on_live_update = on_live_update
        
        success = await self.service.start_transcription(
            on_transcript=self._handle_transcript,
            on_speaker_change=self._handle_speaker_change
        )
        
        return success
    
    def _handle_transcript(self, data: Dict[str, Any]):
        """Handle incoming transcript data"""
        # Send live update if callback provided
        if self.on_live_update:
            self.on_live_update({
                "type": "transcript",
                "data": data
            })
        
        # Store final transcripts
        if data.get("is_final"):
            self.full_transcript.append({
                "timestamp": data.get("timestamp"),
                "start": data.get("start", 0),
                "duration": data.get("duration", 0),
                "segments": data.get("speaker_segments", []),
                "text": data.get("transcript", ""),
                "confidence": data.get("confidence", 1.0)
            })
    
    def _handle_speaker_change(self, speaker_id: int, speaker_label: str):
        """Handle speaker change events"""
        self.current_speakers.add(speaker_id)
        
        if self.on_live_update:
            self.on_live_update({
                "type": "speaker_change",
                "data": {
                    "speaker_id": speaker_id,
                    "speaker_label": speaker_label,
                    "total_speakers": len(self.current_speakers)
                }
            })
    
    async def send_audio(self, audio_data: bytes):
        """Forward audio to transcription service"""
        await self.service.send_audio(audio_data)
    
    async def stop(self):
        """Stop transcription and return results"""
        await self.service.stop_transcription()
        
        return {
            "meeting_id": self.meeting_id,
            "formatted_transcript": self.get_formatted_transcript(),
            "raw_transcript": self.full_transcript,
            "speaker_count": len(self.current_speakers),
            "speaker_map": self.speaker_map
        }
    
    def get_formatted_transcript(self) -> str:
        """Get the full transcript formatted with speakers"""
        formatted_lines = []
        
        for entry in self.full_transcript:
            for segment in entry.get("segments", []):
                speaker_id = segment.get("speaker", 0)
                speaker_name = self.speaker_map.get(speaker_id, f"Speaker {speaker_id + 1}")
                text = segment.get("text", "").strip()
                
                if text:
                    formatted_lines.append(f"{speaker_name}: {text}")
        
        return "\n\n".join(formatted_lines)
    
    def set_speaker_name(self, speaker_id: int, name: str):
        """Map a speaker ID to a name"""
        self.speaker_map[speaker_id] = name
        
        if self.on_live_update:
            self.on_live_update({
                "type": "speaker_identified",
                "data": {
                    "speaker_id": speaker_id,
                    "name": name
                }
            })
    
    def get_speaker_stats(self) -> Dict[str, Any]:
        """Get statistics about speakers"""
        speaker_stats = {}
        
        for entry in self.full_transcript:
            for segment in entry.get("segments", []):
                speaker_id = segment.get("speaker", 0)
                duration = segment.get("end", 0) - segment.get("start", 0)
                
                if speaker_id not in speaker_stats:
                    speaker_stats[speaker_id] = {
                        "total_duration": 0,
                        "word_count": 0,
                        "segments": 0
                    }
                
                speaker_stats[speaker_id]["total_duration"] += duration
                speaker_stats[speaker_id]["word_count"] += len(segment.get("text", "").split())
                speaker_stats[speaker_id]["segments"] += 1
        
        return speaker_stats