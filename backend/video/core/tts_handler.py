import os
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTSHandler:
    VOICE_MAP = {
        "id": "id-ID-ArdiNeural",
        "en": "en-US-GuyNeural",
        "ja": "ja-JP-KeitaNeural",
        "ko": "ko-KR-InJoonNeural",
        "zh": "zh-CN-YunxiNeural",
    }

    async def generate(self, text: str, language: str = "id", voice: Optional[str] = None) -> Optional[str]:
        path = await self._edge_generate(text, language, voice=voice)
        if path:
            return path
        return await self._gtts_generate(text, language)

    async def _edge_generate(self, text: str, language: str, voice: Optional[str] = None) -> Optional[str]:
        try:
            import edge_tts

            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            selected_voice = voice or self.VOICE_MAP.get(language, self.VOICE_MAP["id"])
            communicate = edge_tts.Communicate(
                text=text,
                voice=selected_voice,
                rate="-6%",
                volume="+0%",
                pitch="+0Hz",
            )
            await communicate.save(path)
            logger.info(f"✅ edge-tts audio generated: {path}")
            return path
        except Exception as e:
            logger.warning(f"edge-tts failed: {e}")
            return None

    async def _gtts_generate(self, text: str, language: str) -> Optional[str]:
        try:
            from gtts import gTTS

            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(path)
            logger.info(f"✅ gTTS audio generated: {path}")
            return path
        except Exception as e:
            logger.warning(f"gTTS failed: {e}")
            return None


tts_handler = TTSHandler()
