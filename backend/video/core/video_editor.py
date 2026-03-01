"""
Video Editor Core - MoviePy based video generation
No Streamlit dependencies
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import tempfile
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoEditor:
    """Core video editing functionality without Streamlit"""
    
    def __init__(self, output_dir: str = "videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_video_from_script(self, script: str, audio_path: str, 
                                       output_filename: str, duration: int = 30,
                                       text_effects: Dict[str, Any] = None) -> str:
        """
        Create video with text overlay from script
        """
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ColorClip
            
            # Buat output path
            output_path = self.output_dir / output_filename
            
            # Buat background (hitam)
            bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
            
            # Split script into lines
            lines = script.split('\n')
            # Ambil lines yang tidak kosong, max 5 baris
            text_lines = [line for line in lines if line.strip()][:5]
            text_content = '\n'.join(text_lines) if text_lines else script[:200]
            
            # Buat text clip
            txt_clip = TextClip(
                text_content, 
                fontsize=50, 
                color='white', 
                size=(1700, 900),
                method='caption', 
                align='center', 
                font='Arial'
            )
            txt_clip = txt_clip.set_duration(duration).set_position('center')
            
            # Gabungkan
            video = CompositeVideoClip([bg_clip, txt_clip])
            
            # Tambah audio kalau ada
            if audio_path and os.path.exists(audio_path):
                try:
                    audio = AudioFileClip(audio_path)
                    # Potong audio sesuai durasi video
                    if audio.duration > duration:
                        audio = audio.subclip(0, duration)
                    video = video.set_audio(audio)
                except Exception as e:
                    logger.warning(f"Audio attachment failed: {e}")
            
            # Render
            video.write_videofile(
                str(output_path), 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            video.close()
            
            logger.info(f"✅ Video created: {output_path}")
            return str(output_path)
            
        except ImportError as e:
            logger.error(f"MoviePy not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Video creation error: {e}")
            raise
    
    async def generate_audio_from_text(self, text: str, language: str = 'id') -> Optional[str]:
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
            
            logger.info(f"✅ Audio generated: {path}")
            return path
            
        except ImportError:
            logger.error("gTTS not installed")
            return None
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return None
    
    async def combine_video_audio(self, video_path: str, audio_path: str, 
                                  output_filename: str) -> Optional[str]:
        """Combine video and audio"""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            output_path = self.output_dir / output_filename
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Potong audio sesuai video
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            
            final = video.set_audio(audio)
            final.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
            
            video.close()
            audio.close()
            final.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Combine error: {e}")
            return None


# Global instance
video_editor = VideoEditor()
