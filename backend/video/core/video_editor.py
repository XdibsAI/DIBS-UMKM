import os
import logging
import tempfile
import urllib.request
import textwrap
from pathlib import Path
from typing import Optional, Dict, List, Any

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
            logger.warning(f"Image open/download failed: {e}")
            return None

    def _wrap(self, text: str, width: int) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        return "\n".join(textwrap.wrap(text, width=width))

    def _estimate_scene_seconds(self, scenes: List[Dict[str, Any]], total_duration: float) -> List[float]:
        weights = []
        for s in scenes:
            basis = f"{s.get('title','')} {s.get('text','')} {s.get('caption','')}".strip()
            wc = max(3, len(basis.split()))
            weights.append(wc)
        total = sum(weights) or 1
        durations = [(w / total) * total_duration for w in weights]
        durations = [max(2.2, d) for d in durations]
        scale = total_duration / sum(durations)
        return [d * scale for d in durations]

    def _make_text_clip(self, TextClip, text, fontsize, color, size, duration, pos, font=None, stroke=2):
        kwargs = {
            "fontsize": fontsize,
            "color": color,
            "method": "caption",
            "size": size,
            "align": "center",
            "stroke_color": "#000000",
            "stroke_width": stroke,
        }
        if font:
            kwargs["font"] = font
        return TextClip(text, **kwargs).set_duration(duration).set_position(pos).fadein(0.15).fadeout(0.15)

    def _build_scenes(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        scenes = []
        for s in (plan.get("scenes") or [])[:8]:
            scenes.append({
                "kind": str(s.get("kind") or "scene"),
                "title": str(s.get("title") or "").strip(),
                "text": str(s.get("text") or "").strip(),
                "caption": str(s.get("caption") or "").strip(),
                "brand": str(s.get("brand") or plan.get("brand_name") or "Dibs AI").strip(),
                "image_path": str(s.get("assigned_image_path") or s.get("image_path") or "").strip(),
                "product_image_url": str(s.get("product_image_url") or plan.get("product_image_url") or "").strip(),
            })
        return scenes

    def _make_scene_clip(self, scene: Dict[str, Any], duration: float):
        from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, ImageClip

        title = self._wrap(scene.get("title") or "", 18)
        body = self._wrap(scene.get("text") or "", 26)
        caption = self._wrap(scene.get("caption") or "", 24)
        brand = scene.get("brand") or "Dibs AI"

        image_path = scene.get("image_path") or ""
        if not image_path or not os.path.exists(image_path):
            image_path = self._safe_download_image(scene.get("product_image_url") or "")

        layers = []
        base = ColorClip(size=(1080, 1920), color=(8, 10, 14), duration=duration)
        layers.append(base)

        if image_path and os.path.exists(image_path):
            try:
                bg = ImageClip(image_path).set_duration(duration)
                if bg.w < bg.h:
                    bg = bg.resize(height=1920)
                else:
                    bg = bg.resize(width=1080)
                bg = bg.resize(lambda t: 1.0 + (0.06 * (t / max(duration, 0.01))))
                bg = bg.set_position(lambda t: (-18 * (t / max(duration, 0.01)), -22 * (t / max(duration, 0.01))))
                layers.append(bg)
            except Exception as e:
                logger.warning(f"BG render failed: {e}")

        layers.append(ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration).set_opacity(0.30))

        layers.append(ColorClip(size=(820, 92), color=(10, 18, 38), duration=duration).set_opacity(0.75).set_position(("center", 110)))
        layers.append(self._make_text_clip(TextClip, brand, 34, "white", (760, 48), duration, ("center", 132), font="DejaVu-Sans-Bold"))

        layers.append(ColorClip(size=(960, 1040), color=(15, 15, 18), duration=duration).set_opacity(0.18).set_position(("center", 350)))

        if title:
            layers.append(self._make_text_clip(TextClip, title, 62, "white", (860, 240), duration, ("center", 690), font="DejaVu-Sans-Bold"))

        if body:
            layers.append(self._make_text_clip(TextClip, body, 34, "#F3F4F6", (800, 220), duration, ("center", 1030), font="DejaVu-Sans", stroke=1.8))

        if caption:
            layers.append(ColorClip(size=(900, 88), color=(8, 8, 12), duration=duration).set_opacity(0.68).set_position(("center", 1560)))
            layers.append(self._make_text_clip(TextClip, caption.upper(), 24, "white", (820, 54), duration, ("center", 1581), font="DejaVu-Sans-Bold", stroke=1.2))

        layers.append(ColorClip(size=(760, 64), color=(12, 12, 18), duration=duration).set_opacity(0.6).set_position(("center", 1712)))
        layers.append(self._make_text_clip(TextClip, brand, 24, "white", (700, 40), duration, ("center", 1724), font="DejaVu-Sans", stroke=1.0))

        return CompositeVideoClip(layers, size=(1080, 1920)).set_duration(duration)

    async def create_video_from_script(
        self,
        script: str,
        audio_path: str,
        output_filename: str,
        duration: int = 30,
        text_effects: Dict[str, Any] = None
    ) -> str:
        from moviepy.editor import AudioFileClip, concatenate_videoclips

        plan = (text_effects or {}).get("plan") or {}
        scenes = self._build_scenes(plan)
        if not scenes:
            scenes = [{
                "kind": "scene",
                "title": "Video",
                "text": script[:120],
                "caption": "Video",
                "brand": plan.get("brand_name") or "Dibs AI",
                "image_path": "",
                "product_image_url": plan.get("product_image_url") or "",
            }]

        target_duration = float(duration)
        audio = None
        if audio_path and os.path.exists(audio_path):
            try:
                audio = AudioFileClip(audio_path)
                if audio.duration and audio.duration > 1:
                    target_duration = float(audio.duration)
            except Exception as e:
                logger.warning(f"Audio open failed: {e}")
                audio = None

        scene_durations = self._estimate_scene_seconds(scenes, target_duration)
        clips = [self._make_scene_clip(scene, d) for scene, d in zip(scenes, scene_durations)]
        final_video = concatenate_videoclips(clips, method="compose")

        if audio is not None:
            if audio.duration > final_video.duration:
                audio = audio.subclip(0, final_video.duration)
            elif audio.duration < final_video.duration:
                final_video = final_video.subclip(0, audio.duration)
            final_video = final_video.set_audio(audio)

        output_path = self.output_dir / output_filename
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
        if audio is not None:
            try:
                audio.close()
            except Exception:
                pass
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass

        return str(output_path)

    async def generate_audio_from_text(self, text: str, language: str = 'id') -> Optional[str]:
        try:
            from gtts import gTTS
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(path)
            return path
        except Exception as e:
            logger.error(f"Audio generation error: {e}")
            return None

    async def create_thumbnail_from_video(self, video_path: str, output_filename: str, second: float = 1.0):
        try:
            import subprocess
            if not video_path or not os.path.exists(video_path):
                return None
            output_path = self.output_dir / output_filename
            cmd = [
                "ffmpeg", "-y", "-ss", str(second), "-i", str(video_path),
                "-frames:v", "1", "-q:v", "2", str(output_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 or not output_path.exists():
                return None
            return str(output_path)
        except Exception:
            return None


video_editor = VideoEditor()
