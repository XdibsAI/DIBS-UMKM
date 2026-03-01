"""
Video Editor Core - MoviePy based video generation
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
import tempfile

logger = logging.getLogger(__name__)

class VideoEditor:
    """Core video editing functionality"""
    
    def __init__(self, output_dir: str = "videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_video_from_script(self, script: str, audio_path: str, 
                                       output_filename: str, duration: int = 30) -> str:
        """
        Create video with text overlay from script
        """
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ColorClip
            
            # Buat output path
            output_path = self.output_dir / output_filename
            
            # Buat background (hitam)
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
            
            # Buat text clip dari script
            text_lines = script.split('\n')[:3]  # Ambil 3 baris pertama
            text_content = '\n'.join(text_lines)
            
            txt_clip = TextClip(text_content, fontsize=40, color='white', size=(1800, 800),
                               method='caption', align='center', font='Arial')
            txt_clip = txt_clip.set_duration(duration).set_position('center')
            
            # Gabungkan
            video = CompositeVideoClip([bg_clip, txt_clip])
            
            # Tambah audio kalau ada
            if os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                video = video.set_audio(audio)
            
            # Render
            video.write_videofile(str(output_path), fps=24, codec='libx264', audio_codec='aac')
            
            logger.info(f"✅ Video created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Video creation error: {e}")
            raise
    
    async def generate_audio_from_text(self, text: str, language: str = 'id') -> str:
        """
        Generate audio from text using TTS
        """
        try:
            from gtts import gTTS
            
            # Buat temp file
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            
            # Generate TTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(path)
            
            return path
            
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            # Fallback ke empty audio
            return ""


# Global instance
video_editor = VideoEditor()
