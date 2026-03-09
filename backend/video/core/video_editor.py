"""
Video Editor Core - Promo Video V1
Portrait 1080x1920
Scene-based text promo renderer
"""
import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import tempfile

logger = logging.getLogger(__name__)


class VideoEditor:
    """Core video editing functionality for promo videos"""

    def __init__(self, output_dir: str = "videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _clean_lines(self, script: str) -> List[str]:
        raw_lines = [line.strip() for line in script.split('\n')]
        lines = [line for line in raw_lines if line]
        return lines

    def _build_scenes(self, script: str) -> List[Dict[str, str]]:
        lines = self._clean_lines(script)

        if not lines:
            return [
                {
                    "type": "title",
                    "title": "Promo Hari Ini",
                    "body": "Yuk cek produk terbaik hari ini",
                },
                {
                    "type": "cta",
                    "title": "Order Sekarang",
                    "body": "Jangan sampai kehabisan",
                },
            ]

        first = lines[0]
        rest = lines[1:]

        scenes: List[Dict[str, str]] = []

        # Scene 1: hook
        scenes.append({
            "type": "hook",
            "title": first[:80],
            "body": "",
        })

        # Scene 2-4: isi utama
        grouped = []
        current = []
        for line in rest[:6]:
            current.append(line)
            if len(current) == 2:
                grouped.append(current)
                current = []
        if current:
            grouped.append(current)

        for group in grouped[:3]:
            body = " ".join(group).strip()
            if body:
                scenes.append({
                    "type": "body",
                    "title": "",
                    "body": body[:180],
                })

        # Scene akhir CTA
        scenes.append({
            "type": "cta",
            "title": "Coba Sekarang",
            "body": "Rasakan bedanya hari ini",
        })

        return scenes[:5]

    async def create_video_from_script(
        self,
        script: str,
        audio_path: str,
        output_filename: str,
        duration: int = 30,
        text_effects: Dict[str, Any] = None
    ) -> str:
        """
        Create promo video from script with multiple portrait scenes.
        """
        try:
            from moviepy.editor import (
                TextClip,
                CompositeVideoClip,
                AudioFileClip,
                ColorClip,
                concatenate_videoclips,
            )

            output_path = self.output_dir / output_filename
            scenes = self._build_scenes(script)

            scene_count = max(1, len(scenes))
            per_scene_duration = max(2, duration / scene_count)

            clips = []

            for index, scene in enumerate(scenes):
                # warna background per jenis scene
                if scene["type"] == "hook":
                    bg_color = (10, 10, 25)
                    accent_color = "#00F5FF"
                elif scene["type"] == "cta":
                    bg_color = (5, 25, 15)
                    accent_color = "#00FF99"
                else:
                    bg_color = (15, 10, 20)
                    accent_color = "#FFD54F"

                bg_clip = ColorClip(
                    size=(1080, 1920),
                    color=bg_color,
                    duration=per_scene_duration
                )

                layer_clips = [bg_clip]

                # small top label
                label_clip = TextClip(
                    "DIBS AI PROMO",
                    fontsize=48,
                    color=accent_color,
                    font="Arial",
                    method="caption",
                    size=(900, 80),
                    align="center",
                ).set_duration(per_scene_duration).set_position(("center", 140))
                layer_clips.append(label_clip)

                # title
                if scene["title"]:
                    title_clip = TextClip(
                        scene["title"],
                        fontsize=78,
                        color="white",
                        font="Arial",
                        method="caption",
                        size=(900, 360),
                        align="center",
                    ).set_duration(per_scene_duration).set_position(("center", 420))
                    layer_clips.append(title_clip)

                # body
                if scene["body"]:
                    body_y = 760 if scene["title"] else 620
                    body_clip = TextClip(
                        scene["body"],
                        fontsize=56,
                        color="#F3F4F6",
                        font="Arial",
                        method="caption",
                        size=(900, 700),
                        align="center",
                    ).set_duration(per_scene_duration).set_position(("center", body_y))
                    layer_clips.append(body_clip)

                # bottom accent / CTA bar
                footer_text = "DIBS AI • UMKM Growth Engine"
                if scene["type"] == "cta":
                    footer_text = "Order sekarang • Promo terbatas"

                footer_clip = TextClip(
                    footer_text,
                    fontsize=42,
                    color=accent_color,
                    font="Arial",
                    method="caption",
                    size=(900, 100),
                    align="center",
                ).set_duration(per_scene_duration).set_position(("center", 1700))
                layer_clips.append(footer_clip)

                composite = CompositeVideoClip(layer_clips, size=(1080, 1920)).set_duration(per_scene_duration)
                composite = composite.fadein(0.35).fadeout(0.35)
                clips.append(composite)

            final_video = concatenate_videoclips(clips, method="compose")

            if audio_path and os.path.exists(audio_path):
                try:
                    audio = AudioFileClip(audio_path)
                    if audio.duration > final_video.duration:
                        audio = audio.subclip(0, final_video.duration)
                    elif audio.duration < final_video.duration:
                        final_video = final_video.set_duration(audio.duration)
                    final_video = final_video.set_audio(audio)
                except Exception as e:
                    logger.warning(f"Audio attachment failed: {e}")

            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=2,
                verbose=False,
                logger=None,
            )

            try:
                final_video.close()
            except Exception:
                pass

            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass

            logger.info(f"✅ Promo video created: {output_path}")
            return str(output_path)

        except ImportError as e:
            logger.error(f"MoviePy not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Video creation error: {e}")
            raise

    async def generate_audio_from_text(self, text: str, language: str = "id") -> Optional[str]:
        """
        Generate audio from text using TTS
        """
        try:
            from gtts import gTTS

            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

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

    async def combine_video_audio(
        self,
        video_path: str,
        audio_path: str,
        output_filename: str
    ) -> Optional[str]:
        """Combine video and audio"""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip

            output_path = self.output_dir / output_filename

            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)

            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)

            final = video.set_audio(audio)
            final.write_videofile(str(output_path), codec="libx264", audio_codec="aac")

            video.close()
            audio.close()
            final.close()

            return str(output_path)

        except Exception as e:
            logger.error(f"Combine error: {e}")
            return None


video_editor = VideoEditor()
