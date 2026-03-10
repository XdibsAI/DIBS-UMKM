"""
Video Editor Core - Promo Engine V8
Full-screen product visual + Ken Burns + TikTok captions + narrator-safe layout
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
import tempfile
import urllib.request
import textwrap

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
                    "title": str(scene.get("title", "")).strip()[:100],
                    "body": str(scene.get("text", "")).strip()[:200],
                    "brand": str(scene.get("brand", "")).strip()[:40],
                    "price_text": str(scene.get("price_text", "")).strip()[:50],
                    "cta_text": str(scene.get("cta_text", "")).strip()[:70],
                    "product_name": str(scene.get("product_name", "")).strip()[:80],
                    "product_image_url": str(scene.get("product_image_url", "")).strip(),
                    "image_path": str(scene.get("image_path", "")).strip(),
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
            return {"accent": "#00F5FF", "badge_bg": (10, 16, 36), "cta_bg": (0, 245, 255)}
        if scene_type == "product":
            return {"accent": "#FFD54F", "badge_bg": (28, 18, 52), "cta_bg": (255, 213, 79)}
        if scene_type == "benefit":
            return {"accent": "#7CFFB2", "badge_bg": (18, 40, 30), "cta_bg": (124, 255, 178)}
        if scene_type == "offer":
            return {"accent": "#FFB84D", "badge_bg": (48, 20, 20), "cta_bg": (255, 184, 77)}
        if scene_type == "cta":
            return {"accent": "#00FFCC", "badge_bg": (12, 42, 42), "cta_bg": (0, 255, 204)}
        return {"accent": "#E5E7EB", "badge_bg": (28, 28, 36), "cta_bg": (229, 231, 235)}

    def _make_text_clip(self, TextClip, text, fontsize, color, size, duration, pos, align="center", font=None, stroke_color=None, stroke_width=0):
        kwargs = {
            "fontsize": fontsize,
            "color": color,
            "method": "caption",
            "size": size,
            "align": align,
            "stroke_color": stroke_color,
            "stroke_width": stroke_width,
        }
        if font:
            kwargs["font"] = font

        clip = TextClip(text, **kwargs)
        clip = clip.set_duration(duration).set_position(pos)
        clip = clip.fadein(0.22).fadeout(0.22)
        return clip

    def _make_bg_image(self, ImageClip, image_path: Optional[str], duration: float):
        if not image_path or not os.path.exists(image_path):
            return None
        try:
            bg = ImageClip(image_path).set_duration(duration)
            if bg.w < bg.h:
                bg = bg.resize(height=2020)
            else:
                bg = bg.resize(width=1160)

            # Ken Burns motion
            base_scale = 1.00
            end_scale = 1.08
            bg = bg.resize(lambda t: base_scale + (end_scale - base_scale) * (t / max(duration, 0.01)))

            bg = bg.set_position(lambda t: (-20 - 25 * (t / max(duration, 0.01)), -30 - 40 * (t / max(duration, 0.01))))
            return bg
        except Exception as e:
            logger.warning(f"Background image render failed: {e}")
            return None

    def _caption_chunks(self, scene: Dict[str, str]) -> List[str]:
        scene_type = scene.get("type", "body")
        title = (scene.get("title") or "").strip()
        body = (scene.get("body") or "").strip()
        product_name = (scene.get("product_name") or "").strip()
        price_text = (scene.get("price_text") or "").strip()
        cta_text = (scene.get("cta_text") or "").strip()

        if scene_type == "hook":
            return [title, body] if body else [title]
        if scene_type == "product":
            return [product_name or title, body]
        if scene_type == "benefit":
            return [title, body]
        if scene_type == "offer":
            return [title or "Promo", price_text or body]
        if scene_type == "cta":
            return [title or "Aksi Sekarang", cta_text or body]
        return [title or body]

    def _wrap_text(self, value: str, width: int) -> str:
        value = (value or "").strip()
        if not value:
            return ""
        return "\n".join(textwrap.wrap(value, width=width))

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
        generated_image_path = (scene.get("image_path") or "").strip()

        image_path = generated_image_path if generated_image_path and os.path.exists(generated_image_path) else self._safe_download_image(product_image_url)

        theme = self._theme_for_scene(scene_type)
        layers = []

        bg_image = self._make_bg_image(ImageClip, image_path, duration)
        if bg_image is not None:
            layers.append(bg_image)
        else:
            layers.append(ColorClip(size=(1080, 1920), color=(10, 10, 18), duration=duration))

        # cinematic dark overlay
        layers.append(ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration).set_opacity(0.36))

        # top badge
        layers.append(
            ColorClip(size=(860, 110), color=theme["badge_bg"], duration=duration)
            .set_opacity(0.72)
            .set_position(("center", 120))
        )
        layers.append(self._make_text_clip(
            TextClip, f"{brand} VISUAL", 40, "white", (780, 70), duration, ("center", 145),
            font="DejaVu-Sans-Bold"
        ))

        # safe center panel
        layers.append(
            ColorClip(size=(940, 980), color=(10, 10, 15), duration=duration)
            .set_opacity(0.22)
            .set_position(("center", 420))
        )

        title_text = ""
        body_text = ""
        label_text = ""

        if scene_type == "hook":
            title_text = title
            body_text = body
        elif scene_type == "product":
            label_text = title or "Produk Unggulan"
            title_text = product_name or title
            body_text = body
        elif scene_type == "benefit":
            label_text = title
            title_text = ""
            body_text = body
        elif scene_type == "offer":
            label_text = title or "Promo"
            title_text = price_text or body
            body_text = ""
        elif scene_type == "cta":
            label_text = title or "Aksi Sekarang"
            title_text = cta_text or body
            body_text = ""
        else:
            title_text = title
            body_text = body

        title_text = self._wrap_text(title_text, 18)
        body_text = self._wrap_text(body_text, 34)
        label_text = self._wrap_text(label_text, 24)

        if label_text:
            layers.append(self._make_text_clip(
                TextClip, label_text, 42, theme["accent"], (840, 70), duration, ("center", 610),
                font="DejaVu-Sans-Bold"
            ))

        if title_text:
            title_y = 760 if label_text else 690
            layers.append(self._make_text_clip(
                TextClip, title_text, 68, "white", (880, 260), duration, ("center", title_y),
                font="DejaVu-Sans-Bold", stroke_color="#000000", stroke_width=2
            ))

        if body_text:
            body_y = 1080 if title_text else 910
            layers.append(self._make_text_clip(
                TextClip, body_text, 36, "#F3F4F6", (840, 150), duration, ("center", body_y),
                font="DejaVu-Sans", stroke_color="#000000", stroke_width=1
            ))

        # TikTok style captions at bottom
        caption_chunks = [c for c in self._caption_chunks(scene) if c and c.strip()]
        if caption_chunks:
            caption_area = ColorClip(size=(980, 138), color=(8, 8, 10), duration=duration)\
                .set_opacity(0.70).set_position(("center", 1490))
            layers.append(caption_area)

            chunk_duration = duration / len(caption_chunks)
            for idx, chunk in enumerate(caption_chunks):
                start = idx * chunk_duration
                end = min(duration, (idx + 1) * chunk_duration)
                txt = self._wrap_text(chunk.upper(), 26)
                cap = self._make_text_clip(
                    TextClip, txt, 32, "white", (920, 100), end - start, ("center", 1512),
                    font="DejaVu-Sans-Bold", stroke_color="#000000", stroke_width=2
                ).set_start(start)
                layers.append(cap)

        # footer
        layers.append(
            ColorClip(size=(860, 86), color=(12, 12, 20), duration=duration)
            .set_opacity(0.60)
            .set_position(("center", 1708))
        )
        footer_text = brand if scene_type != "cta" else f"{brand} • ORDER NOW"
        layers.append(self._make_text_clip(
            TextClip, footer_text, 30, "#F3F4F6", (780, 50), duration, ("center", 1726),
            font="DejaVu-Sans"
        ))

        scene_clip = CompositeVideoClip(layers, size=(1080, 1920)).set_duration(duration)
        scene_clip = scene_clip.fadein(0.25).fadeout(0.25)
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
