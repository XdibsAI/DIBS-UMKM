"""
Video Editor Core - Promo Engine V2
Portrait 1080x1920
Scene-based layout engine
"""
import os
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
        return [line for line in raw_lines if line]

    def _build_scenes(self, script: str, plan: Dict[str, Any] = None) -> List[Dict[str, str]]:
        plan = plan or {}
        planned_scenes = plan.get("scenes") or []

        if planned_scenes:
            mapped = []
            for scene in planned_scenes[:5]:
                kind = str(scene.get("kind", "body")).strip() or "body"
                title = str(scene.get("title", "")).strip()
                text = str(scene.get("text", "")).strip()

                if not title and not text:
                    continue

                mapped.append({
                    "type": kind,
                    "title": title[:80],
                    "body": text[:180],
                })

            if mapped:
                return mapped

        lines = self._clean_lines(script)
        if not lines:
            return [
                {"type": "hook", "title": "Promo Hari Ini", "body": "Yuk cek produk terbaik hari ini"},
                {"type": "cta", "title": "Order Sekarang", "body": "Jangan sampai kehabisan"},
            ]

        first = lines[0]
        rest = lines[1:]
        scenes = [{"type": "hook", "title": first[:80], "body": ""}]

        for line in rest[:3]:
            scenes.append({"type": "body", "title": "", "body": line[:180]})

        scenes.append({"type": "cta", "title": "Coba Sekarang", "body": "Rasakan bedanya hari ini"})
        return scenes[:5]

    def _theme_for_scene(self, scene_type: str):
        if scene_type == "hook":
            return {
                "bg": (8, 10, 32),
                "accent": "#00F5FF",
                "panel": (18, 24, 58),
            }
        if scene_type == "product":
            return {
                "bg": (14, 10, 28),
                "accent": "#FFD54F",
                "panel": (28, 18, 52),
            }
        if scene_type == "benefit":
            return {
                "bg": (10, 20, 16),
                "accent": "#7CFFB2",
                "panel": (18, 40, 30),
            }
        if scene_type == "offer":
            return {
                "bg": (22, 10, 10),
                "accent": "#FFB84D",
                "panel": (48, 20, 20),
            }
        if scene_type == "cta":
            return {
                "bg": (6, 18, 18),
                "accent": "#00FFCC",
                "panel": (12, 42, 42),
            }
        return {
            "bg": (12, 12, 18),
            "accent": "#D1D5DB",
            "panel": (28, 28, 36),
        }

    def _make_text_clip(self, TextClip, text, fontsize, color, size, duration, pos_y):
        clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            method="caption",
            size=size,
            align="center",
        )
        clip = clip.set_duration(duration).set_position(("center", pos_y))
        clip = clip.fadein(0.3).fadeout(0.3)
        return clip

    def _make_scene_clip(self, scene: Dict[str, str], duration: float):
        from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

        scene_type = scene.get("type", "body")
        title = (scene.get("title") or "").strip()
        body = (scene.get("body") or "").strip()

        theme = self._theme_for_scene(scene_type)

        bg_clip = ColorClip(size=(1080, 1920), color=theme["bg"], duration=duration)

        top_bar = ColorClip(size=(900, 120), color=theme["panel"], duration=duration)\
            .set_opacity(0.65).set_position(("center", 120))

        center_panel = ColorClip(size=(920, 760), color=theme["panel"], duration=duration)\
            .set_opacity(0.28).set_position(("center", 480))

        bottom_bar = ColorClip(size=(900, 110), color=theme["panel"], duration=duration)\
            .set_opacity(0.55).set_position(("center", 1670))

        layers = [bg_clip, top_bar, center_panel, bottom_bar]

        brand_clip = self._make_text_clip(
            TextClip,
            "DIBS AI PROMO",
            46,
            theme["accent"],
            (860, 80),
            duration,
            145
        )
        layers.append(brand_clip)

        if scene_type == "hook":
            if title:
                layers.append(self._make_text_clip(TextClip, title, 84, "white", (860, 260), duration, 560))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 48, "#E5E7EB", (820, 200), duration, 860))

        elif scene_type in ("product", "offer", "cta"):
            if title:
                layers.append(self._make_text_clip(TextClip, title, 58, theme["accent"], (820, 120), duration, 560))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 64, "white", (840, 420), duration, 760))

        else:
            if title:
                layers.append(self._make_text_clip(TextClip, title, 54, theme["accent"], (820, 120), duration, 560))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 60, "white", (840, 420), duration, 760))

        footer_text = "DIBS AI • UMKM Growth Engine"
        if scene_type == "cta":
            footer_text = "Aksi sekarang • hasilkan penjualan"

        footer_clip = self._make_text_clip(
            TextClip,
            footer_text,
            40,
            theme["accent"],
            (860, 80),
            duration,
            1685
        )
        layers.append(footer_clip)

        scene_clip = CompositeVideoClip(layers, size=(1080, 1920)).set_duration(duration)
        scene_clip = scene_clip.fadein(0.35).fadeout(0.35)
        return scene_clip

    async def create_video_from_script(
        self,
        script: str,
        audio_path: str,
        output_filename: str,
        duration: int = 30,
        text_effects: Dict[str, Any] = None
    ) -> str:
        try:
            from moviepy.editor import AudioFileClip, concatenate_videoclips

            output_path = self.output_dir / output_filename
            plan = (text_effects or {}).get("plan") or {}
            scenes = self._build_scenes(script, plan=plan)

            scene_count = max(1, len(scenes))
            per_scene_duration = max(2, duration / scene_count)

            clips = [self._make_scene_clip(scene, per_scene_duration) for scene in scenes]
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
