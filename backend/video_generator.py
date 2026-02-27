"""
DIBS Full Video Generator
Script → TTS → Video Rendering
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Full video generation: Script → Audio → Video"""
    
    def __init__(self, output_dir: str = "/home/dibs/dibs1/video_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_audio_from_script(self, script_data: dict, language: str = "id") -> str:
        """Generate audio dari script menggunakan gTTS"""
        try:
            # Combine script parts
            full_text = f"{script_data['hook']}. {script_data['body']}. {script_data['cta']}"
            
            # Generate audio
            from gtts import gTTS
            audio_file = self.output_dir / f"audio_{uuid.uuid4().hex[:8]}.mp3"
            
            tts = gTTS(text=full_text, lang=language, slow=False)
            tts.save(str(audio_file))
            
            logger.info(f"✅ Audio generated: {audio_file}")
            return str(audio_file)
            
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            raise
    
    async def create_video_with_text(
        self,
        audio_path: str,
        script_data: dict,
        output_filename: str,
        duration: int = 60
    ) -> str:
        """Create video dengan text overlay & audio"""
        try:
            from moviepy.editor import (
                ColorClip, TextClip, CompositeVideoClip,
                AudioFileClip, concatenate_videoclips
            )
            
            # Load audio
            audio = AudioFileClip(audio_path)
            actual_duration = min(audio.duration, duration)
            
            # Background
            bg_clip = ColorClip(
                size=(1080, 1920),  # Portrait 9:16
                color=(20, 20, 40),
                duration=actual_duration
            )
            
            # Title text
            title_txt = TextClip(
                script_data['title'],
                fontsize=70,
                color='white',
                font='Arial-Bold',
                size=(1000, None),
                method='caption'
            ).set_position(('center', 200)).set_duration(actual_duration)
            
            # Body text (scrolling effect bisa ditambahkan)
            body_txt = TextClip(
                script_data['body'][:200],  # Limit text
                fontsize=50,
                color='white',
                font='Arial',
                size=(1000, None),
                method='caption'
            ).set_position(('center', 'center')).set_duration(actual_duration)
            
            # Composite
            video = CompositeVideoClip([bg_clip, title_txt, body_txt])
            video = video.set_audio(audio)
            
            # Output
            output_path = self.output_dir / output_filename
            video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='medium'
            )
            
            # Cleanup
            audio.close()
            video.close()
            
            logger.info(f"✅ Video generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise

# Global instance
video_generator = VideoGenerator()
