"""
Video Editor Core - Promo Engine V4
Portrait 1080x1920
Scene-based layout engine with image support + thumbnail generation
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import tempfile
import urllib.request

logger = logging.getLogger(__name__)


class VideoEditor:
    def __init__(self, output_dir: str = "videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _safe_download_image(self, image_url: str) -> Optional[str]:
        try:
            if not image_url:
                return None

            if image_url.startswith("/") and os.path.exists(image_url):
                return image_url

            if image_url.startswith("http://") or image_url.startswith("https://"):
                suffix = ".jpg"
                if image_url.lower().endswith(".png"):
                    suffix = ".png"
                fd, temp_path = tempfile.mkstemp(suffix=suffix)
                os.close(fd)
                urllib.request.urlretrieve(image_url, temp_path)
                return temp_path

            if os.path.exists(image_url):
                return image_url

            return None
        except Exception as e:
            logger.warning(f"Image download/open failed: {e}")
            return None

    def _clean_lines(self, script: str) -> List[str]:
        raw_lines = [line.strip() for line in script.split('\n')]
        return [line for line in raw_lines if line]

    def _build_scenes(self, script: str, plan: Dict[str, Any] = None) -> List[Dict[str, str]]:
        plan = plan or {}
        planned_scenes = plan.get("scenes") or []

        if planned_scenes:
            mapped = []
            for scene in planned_scenes[:5]:
                mapped.append({
                    "type": str(scene.get("kind", "body")).strip() or "body",
                    "title": str(scene.get("title", "")).strip()[:80],
                    "body": str(scene.get("text", "")).strip()[:180],
                    "brand": str(scene.get("brand", "")).strip()[:40],
                    "price_text": str(scene.get("price_text", "")).strip()[:50],
                    "cta_text": str(scene.get("cta_text", "")).strip()[:70],
                    "product_name": str(scene.get("product_name", "")).strip()[:70],
                    "product_image_url": str(scene.get("product_image_url", "")).strip(),
                })
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
            return {"bg": (8, 10, 32), "accent": "#00F5FF", "panel": (18, 24, 58)}
        if scene_type == "product":
            return {"bg": (14, 10, 28), "accent": "#FFD54F", "panel": (28, 18, 52)}
        if scene_type == "benefit":
            return {"bg": (10, 20, 16), "accent": "#7CFFB2", "panel": (18, 40, 30)}
        if scene_type == "offer":
            return {"bg": (22, 10, 10), "accent": "#FFB84D", "panel": (48, 20, 20)}
        if scene_type == "cta":
            return {"bg": (6, 18, 18), "accent": "#00FFCC", "panel": (12, 42, 42)}
        return {"bg": (12, 12, 18), "accent": "#D1D5DB", "panel": (28, 28, 36)}

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

    def _base_layers(self, ColorClip, duration, theme):
        bg_clip = ColorClip(size=(1080, 1920), color=theme["bg"], duration=duration)

        top_bar = ColorClip(size=(900, 120), color=theme["panel"], duration=duration)\
            .set_opacity(0.65).set_position(("center", 120))

        center_panel = ColorClip(size=(920, 760), color=theme["panel"], duration=duration)\
            .set_opacity(0.28).set_position(("center", 480))

        bottom_bar = ColorClip(size=(900, 110), color=theme["panel"], duration=duration)\
            .set_opacity(0.55).set_position(("center", 1670))

        return [bg_clip, top_bar, center_panel, bottom_bar]

    def _append_product_image(self, layers, ImageClip, image_path: Optional[str], duration: float):
        if not image_path:
            return
        try:
            img = ImageClip(image_path).set_duration(duration)
            img = img.resize(width=340)
            img = img.set_position(("center", 700))
            img = img.fadein(0.3).fadeout(0.3)
            layers.append(img)
        except Exception as e:
            logger.warning(f"Product image render failed: {e}")

    def _make_scene_clip(self, scene: Dict[str, str], duration: float):
        from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, ImageClip

        scene_type = scene.get("type", "body")
        title = (scene.get("title") or "").strip()
        body = (scene.get("body") or "").strip()
        brand = (scene.get("brand") or "DIBS AI").strip()
        price_text = (scene.get("price_text") or "").strip()
        cta_text = (scene.get("cta_text") or "").strip()
        product_name = (scene.get("product_name") or "").strip()
        product_image_url = (scene.get("product_image_url") or "").strip()
        local_image = self._safe_download_image(product_image_url)

        theme = self._theme_for_scene(scene_type)
        layers = self._base_layers(ColorClip, duration, theme)

        brand_clip = self._make_text_clip(
            TextClip,
            f"{brand} PROMO",
            44,
            theme["accent"],
            (860, 80),
            duration,
            145
        )
        layers.append(brand_clip)

        if scene_type == "hook":
            if title:
                layers.append(self._make_text_clip(TextClip, title, 74, "white", (820, 240), duration, 560))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 42, "#E5E7EB", (760, 180), duration, 910))

        elif scene_type == "product":
            if title:
                layers.append(self._make_text_clip(TextClip, title, 52, theme["accent"], (760, 100), duration, 560))
            self._append_product_image(layers, ImageClip, local_image, duration)
            product_text = product_name or body
            if product_text:
                y = 1120 if local_image else 820
                layers.append(self._make_text_clip(TextClip, product_text, 56, "white", (780, 220), duration, y))

        elif scene_type == "benefit":
            if title:
                layers.append(self._make_text_clip(TextClip, title, 54, theme["accent"], (760, 110), duration, 610))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 52, "white", (800, 360), duration, 810))

        elif scene_type == "offer":
            badge = ColorClip(size=(500, 110), color=(255, 184, 77), duration=duration)\
                .set_opacity(0.9).set_position(("center", 610))
            layers.append(badge)
            layers.append(self._make_text_clip(TextClip, "PROMO SPESIAL", 40, "#111827", (460, 70), duration, 635))
            if title:
                layers.append(self._make_text_clip(TextClip, title, 54, "white", (760, 110), duration, 790))
            offer_text = price_text or body or "Harga spesial hari ini"
            layers.append(self._make_text_clip(TextClip, offer_text, 68, theme["accent"], (760, 180), duration, 980))

        elif scene_type == "cta":
            cta_box = ColorClip(size=(660, 150), color=(0, 255, 204), duration=duration)\
                .set_opacity(0.92).set_position(("center", 930))
            layers.append(cta_box)
            if title:
                layers.append(self._make_text_clip(TextClip, title, 50, "white", (760, 90), duration, 710))
            final_cta = cta_text or body or "Order sekarang"
            layers.append(self._make_text_clip(TextClip, final_cta, 40, "#111827", (590, 100), duration, 968))
            if body and body != final_cta:
                layers.append(self._make_text_clip(TextClip, body, 42, "white", (760, 160), duration, 1140))

        else:
            if title:
                layers.append(self._make_text_clip(TextClip, title, 52, theme["accent"], (760, 100), duration, 620))
            if body:
                layers.append(self._make_text_clip(TextClip, body, 54, "white", (800, 360), duration, 820))

        footer_text = f"{brand} • UMKM Growth Engine"
        if scene_type == "cta":
            footer_text = f"{brand} • Saatnya Closing"

        footer_clip = self._make_text_clip(
            TextClip,
            footer_text,
            38,
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

    async def create_thumbnail_from_video(
        self,
        video_path: str,
        output_filename: str,
        second: float = 1.0,
    ) -> Optional[str]:
        try:
            import subprocess

            if not video_path or not os.path.exists(video_path):
                return None

            output_path = self.output_dir / output_filename

            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                str(second),
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Thumbnail generation failed: {result.stderr}")
                return None

            if not output_path.exists():
                return None

            return str(output_path)
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {e}")
            return None

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
