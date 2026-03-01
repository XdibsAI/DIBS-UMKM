"""
Text-to-Speech Handler
"""
import os
import tempfile
import logging
from typing import Optional
from gtts import gTTS
import edge_tts

logger = logging.getLogger(__name__)

class TTSHandler:
    """Handle text-to-speech conversion with multiple providers"""
    
    def __init__(self):
        self.providers = {
            'gtts': self._gtts_generate,
            'edge': self._edge_generate
        }
    
    async def generate(self, text: str, language: str = 'id', 
                      provider: str = 'gtts') -> Optional[str]:
        """Generate audio from text"""
        if provider in self.providers:
            return await self.providers[provider](text, language)
        return await self._gtts_generate(text, language)
    
    async def _gtts_generate(self, text: str, language: str) -> Optional[str]:
        """Generate using Google TTS"""
        try:
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(path)
            
            return path
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None
    
    async def _edge_generate(self, text: str, language: str) -> Optional[str]:
        """Generate using Microsoft Edge TTS"""
        try:
            voice_map = {
                'id': 'id-ID-ArdiNeural',
                'en': 'en-US-JennyNeural',
                'ja': 'ja-JP-NanamiNeural',
                'ko': 'ko-KR-SunHiNeural',
                'zh': 'zh-CN-XiaoxiaoNeural'
            }
            voice = voice_map.get(language, 'id-ID-ArdiNeural')
            
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(path)
            
            return path
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return None


# Global instance
tts_handler = TTSHandler()
