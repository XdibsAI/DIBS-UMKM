import os
import re
import logging
import tempfile
import urllib.request
import textwrap
from pathlib import Path
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


def _scene_text_layout(kind: str):
    k = str(kind or "").strip().lower()
    layouts = {
        "hook": {"title_y": 760, "body_y": 1040, "title_size": 80, "body_size": 42, "align": "center"},
        "education": {"title_y": 820, "body_y": 1090, "title_size": 68, "body_size": 40, "align": "center"},
        "motivasi": {"title_y": 860, "body_y": 1120, "title_size": 72, "body_size": 40, "align": "center"},
        "motivation": {"title_y": 860, "body_y": 1120, "title_size": 72, "body_size": 40, "align": "center"},
        "product": {"title_y": 720, "body_y": 1210, "title_size": 66, "body_size": 38, "align": "center"},
        "offer": {"title_y": 760, "body_y": 1150, "title_size": 70, "body_size": 42, "align": "center"},
        "cta": {"title_y": 900, "body_y": 1180, "title_size": 64, "body_size": 36, "align": "center"},
    }
    return layouts.get(k, {"title_y": 820, "body_y": 1080, "title_size": 70, "body_size": 40, "align": "center"})



def _clean_video_text(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    # buang bullet / numbering
    text = re.sub(r'^[\-\*\d\.\)\s]+', '', text)

    # buang label storyboard umum
    text = re.sub(
        r'\b(Pembuka|Hook|Intro|Akuisisi|Transformasi|Klimaks|Penutup|CTA|Closing|Scene\s*\d+)\b\s*\([^\)]*\)',
        '',
        text,
        flags=re.I
    )

    # buang frasa prompt-ish yang sering nyangkut
    bad_prefixes = [
        "buat video",
        "video motivasi",
        "video promo",
        "video edukasi",
        "video tutorial",
        "judul:",
        "durasi:",
        "tema:",
        "struktur narasi:",
        "visual & musik:",
        "tips produksi:",
    ]
    lowered = text.lower()
    for bp in bad_prefixes:
        if lowered.startswith(bp):
            text = ""
            break

    text = text.replace("**", "").replace("__", "").replace("•", " ")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r'\s+', ' ', text).strip(" -–—:;,.")
    return text


def _pick_display_text(title: str, text: str, caption: str) -> tuple[str, str, str]:
    title = _clean_video_text(title)
    text = _clean_video_text(text)
    caption = _clean_video_text(caption)

    # prioritas isi nyata
    main_text = caption or text or title
    sub_text = ""

    # kalau title beda dan pendek, boleh jadi sub kecil
    if title and title.lower() != main_text.lower():
        title_words = set(title.lower().split())
        main_words = set(main_text.lower().split())
        overlap = 0
        if title_words and main_words:
            overlap = len(title_words & main_words) / max(1, len(title_words))
        if overlap < 0.6 and len(title.split()) <= 5:
            sub_text = title

    return title, main_text, sub_text



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
            raw_title = str(s.get("title") or "").strip()
            raw_text = str(s.get("text") or "").strip()
            raw_caption = str(s.get("caption") or "").strip()

            _, main_text, sub_text = _pick_display_text(raw_title, raw_text, raw_caption)

            scenes.append({
                "kind": str(s.get("kind") or "scene"),
                "title": sub_text,
                "text": main_text,
                "caption": "",
                "brand": str(s.get("brand") or plan.get("brand_name") or "Dibs AI").strip(),
                "image_path": str(s.get("assigned_image_path") or s.get("image_path") or "").strip(),
                "product_image_url": str(s.get("product_image_url") or plan.get("product_image_url") or "").strip(),
            })
        return scenes

    def _make_scene_clip(self, scene: Dict[str, Any], duration: float):
        from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, ImageClip

        raw_title = scene.get("title") or ""
        raw_text = scene.get("text") or ""
        raw_caption = scene.get("caption") or ""
        _, main_text, sub_text = _pick_display_text(raw_title, raw_text, raw_caption)
        kind = scene.get("kind") or scene.get("type") or "scene"
        layout = _scene_text_layout(kind)

        title = self._wrap(main_text, 18) if main_text else ""
        body = self._wrap(sub_text, 22) if sub_text else ""
        brand = scene.get("brand") or "Dibs AI"

        image_path = scene.get("image_path") or ""
        if not image_path or not os.path.exists(image_path):
            image_path = self._safe_download_image(scene.get("product_image_url") or "")

        layers = []

        # full background
        if image_path and os.path.exists(image_path):
            bg = ImageClip(image_path).set_duration(duration)
            bg = bg.resize(height=1920)
            if bg.w < 1080:
                bg = bg.resize(width=1080)
            bg = bg.set_position(("center", "center"))
            bg = bg.resize(lambda t: 1 + (0.04 * (t / max(duration, 0.1))))
            layers.append(bg)
        else:
            layers.append(ColorClip(size=(1080, 1920), color=(8, 10, 14), duration=duration))

        # soft dark overlay
        layers.append(
            ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration).set_opacity(0.32)
        )

        # brand top
        brand_clip = self._make_text_clip(
            TextClip,
            str(brand),
            34,
            "white",
            (860, 70),
            duration,
            ("center", 110),
            stroke=2,
        )
        layers.append(brand_clip)

        # main headline only
        if title:
            title_clip = self._make_text_clip(
                TextClip,
                title,
                layout["title_size"],
                "white",
                (820, 260),
                duration,
                ("center", layout["title_y"]),
                stroke=3,
            )
            layers.append(title_clip)

        # subtext only if different
        if body and body.lower() != title.lower():
            body_clip = self._make_text_clip(
                TextClip,
                body,
                layout["body_size"],
                "#E5E7EB",
                (760, 180),
                duration,
                ("center", layout["body_y"]),
                stroke=2,
            )
            layers.append(body_clip)

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
