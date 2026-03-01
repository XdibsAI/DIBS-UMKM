"""
Text-to-Speech Handler - No Streamlit
"""
import os
import tempfile
import logging
from typing import Optional
import asyncio

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
            from gtts import gTTS
            
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(path)
            
            logger.info(f"✅ Audio generated with gTTS: {path}")
            return path
            
        except ImportError:
            logger.error("gTTS not installed")
            return None
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None
    
    async def _edge_generate(self, text: str, language: str) -> Optional[str]:
        """Generate using Microsoft Edge TTS"""
        try:
            import edge_tts
            
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
            
            logger.info(f"✅ Audio generated with Edge TTS: {path}")
            return path
            
        except ImportError:
            logger.warning("edge_tts not installed, falling back to gTTS")
            return await self._gtts_generate(text, language)
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return await self._gtts_generate(text, language)


# Global instance
tts_handler = TTSHandler()
