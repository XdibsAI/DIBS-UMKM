"""
Speech to Text - No Streamlit
Convert audio to text for subtitles
"""
import os
import tempfile
import logging
import subprocess
from typing import Optional, List

logger = logging.getLogger(__name__)

class SpeechToText:
    """Convert speech to text (requires ffmpeg)"""
    
    def __init__(self):
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if speech recognition is available"""
        try:
            import speech_recognition as sr
            return True
        except ImportError:
            logger.warning("speech_recognition not installed")
            return False
    
    async def transcribe(self, audio_path: str, language: str = 'id') -> Optional[str]:
        """Transcribe audio file to text"""
        if not self.available:
            return None
            
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Convert to wav if needed
            if not audio_path.endswith('.wav'):
                wav_path = await self._convert_to_wav(audio_path)
                audio_file = wav_path
            else:
                audio_file = audio_path
            
            # Load audio
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
                
            # Recognize
            try:
                text = recognizer.recognize_google(audio, language=language)
                return text
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Recognition error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    async def _convert_to_wav(self, audio_path: str) -> str:
        """Convert audio to WAV format using ffmpeg"""
        fd, wav_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        try:
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y', wav_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return wav_path
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return audio_path
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return audio_path
    
    async def generate_subtitles(self, audio_path: str, 
                                language: str = 'id') -> List[dict]:
        """Generate subtitles with timestamps"""
        # Simple implementation - bisa di-upgrade dengan library khusus
        text = await self.transcribe(audio_path, language)
        
        if not text:
            return []
            
        # Split into sentences for subtitles
        import re
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        subtitles = []
        for i, sentence in enumerate(sentences):
            subtitles.append({
                'index': i + 1,
                'start': i * 3,  # Dummy timing
                'end': (i + 1) * 3,
                'text': sentence
            })
            
        return subtitles


speech_to_text = SpeechToText()
