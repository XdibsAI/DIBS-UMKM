from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import hashlib
import tempfile
import urllib.request
import os


class SceneImageGenerator:
    def __init__(self, base_dir: str = "videos/assets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _project_dir(self, project_id: str) -> Path:
        path = self.base_dir / project_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _pick_palette(self, seed_text: str):
        h = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
        idx = int(h[:2], 16) % 5
        palettes = [
            ((8, 10, 32), (0, 245, 255), (18, 24, 58)),
            ((18, 10, 28), (255, 213, 79), (35, 18, 52)),
            ((10, 22, 16), (124, 255, 178), (18, 40, 30)),
            ((22, 10, 10), (255, 184, 77), (48, 20, 20)),
            ((12, 12, 18), (220, 220, 220), (30, 30, 38)),
        ]
        return palettes[idx]

    def _safe_open_image(self, image_url: str) -> Optional[Image.Image]:
        try:
            if not image_url:
                return None

            local_path = None
            if image_url.startswith("http://") or image_url.startswith("https://"):
                fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                urllib.request.urlretrieve(image_url, temp_path)
                local_path = temp_path
            elif os.path.exists(image_url):
                local_path = image_url
            else:
                return None

            img = Image.open(local_path).convert("RGB")
            return img
        except Exception:
            return None

    def _draw_glow(self, draw, cx, cy, r, color, steps=10):
        for i in range(steps, 0, -1):
            rr = int(r * (1 + i * 0.18))
            alpha = max(6, int(110 / i))
            draw.ellipse(
                (cx - rr, cy - rr, cx + rr, cy + rr),
                fill=(color[0], color[1], color[2], alpha),
            )

    def _draw_pattern(self, img: Image.Image, scene_type: str, accent):
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        w, h = img.size

        self._draw_glow(draw, int(w * 0.14), int(h * 0.22), 120, accent)
        self._draw_glow(draw, int(w * 0.78), int(h * 0.30), 180, accent)
        self._draw_glow(draw, int(w * 0.56), int(h * 0.76), 220, accent)

        if scene_type == "product":
            draw.rounded_rectangle((180, 360, 900, 1480), radius=48, outline=(255, 255, 255, 35), width=3)
            draw.rounded_rectangle((240, 430, 840, 1120), radius=30, outline=(accent[0], accent[1], accent[2], 80), width=4)
        elif scene_type == "offer":
            for i in range(4):
                pad = 170 + i * 40
                draw.rounded_rectangle(
                    (pad, 460 + i * 36, w - pad, 1180 - i * 36),
                    radius=34,
                    outline=(accent[0], accent[1], accent[2], 70),
                    width=3,
                )
        elif scene_type == "cta":
            draw.rounded_rectangle((170, 640, 910, 1060), radius=56, outline=(accent[0], accent[1], accent[2], 110), width=5)
        else:
            for i in range(5):
                y = 300 + i * 150
                draw.rounded_rectangle((120, y, 960, y + 54), radius=20, outline=(accent[0], accent[1], accent[2], 55), width=2)

        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=6))
        img.alpha_composite(overlay)

    def _compose_with_product_image(self, canvas: Image.Image, product_img: Image.Image, accent):
        w, h = canvas.size

        # blurred bg from product image
        bg = ImageOps.fit(product_img, (w, h), method=Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=18))
        bg = Image.blend(bg, Image.new("RGB", (w, h), (8, 8, 12)), 0.45)
        canvas.alpha_composite(bg.convert("RGBA"))

        # glow
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        self._draw_glow(gd, 540, 860, 240, accent)
        self._draw_glow(gd, 540, 860, 160, (255, 255, 255))
        canvas.alpha_composite(glow)

        # hero product
        hero = product_img.copy().convert("RGBA")
        hero.thumbnail((620, 760), Image.Resampling.LANCZOS)

        # rounded card behind
        panel = Image.new("RGBA", (760, 980), (10, 10, 14, 130))
        pd = ImageDraw.Draw(panel, "RGBA")
        pd.rounded_rectangle((0, 0, 760, 980), radius=42, fill=(12, 12, 18, 120), outline=(255, 255, 255, 28), width=2)
        canvas.alpha_composite(panel, dest=(160, 430))

        hx = 540 - hero.width // 2
        hy = 860 - hero.height // 2
        canvas.alpha_composite(hero, dest=(hx, hy))

    def generate_scene_image(
        self,
        project_id: str,
        scene_index: int,
        scene_data: Dict[str, Any],
        brand_name: Optional[str] = None,
    ) -> str:
        scene_type = str(scene_data.get("kind") or scene_data.get("type") or "scene")
        seed_text = f"{scene_type}|{scene_data.get('title','')}|{scene_data.get('text','')}|{scene_data.get('image_prompt','')}"
        bg, accent, panel = self._pick_palette(seed_text)

        img = Image.new("RGBA", (1080, 1920), color=bg + (255,))
        draw = ImageDraw.Draw(img, "RGBA")

        # soft vertical gradient
        for i in range(0, 1920, 16):
            ratio = i / 1920.0
            c = (
                int(bg[0] * (1 - ratio) + panel[0] * ratio),
                int(bg[1] * (1 - ratio) + panel[1] * ratio),
                int(bg[2] * (1 - ratio) + panel[2] * ratio),
                255,
            )
            draw.rectangle((0, i, 1080, i + 16), fill=c)

        # product image if available
        product_image_url = str(scene_data.get("product_image_url") or "").strip()
        product_img = self._safe_open_image(product_image_url)
        if product_img:
            self._compose_with_product_image(img, product_img, accent)
        else:
            self._draw_pattern(img, scene_type, accent)

        # glass bars / safe frame only, NO text in background asset
        draw.rounded_rectangle((70, 110, 1010, 240), radius=26, fill=(panel[0], panel[1], panel[2], 110))
        draw.rounded_rectangle((70, 1640, 1010, 1770), radius=22, fill=(panel[0], panel[1], panel[2], 95))
        draw.rounded_rectangle((90, 360, 990, 1460), radius=40, outline=(255, 255, 255, 30), width=2)

        output_path = self._project_dir(project_id) / f"scene_{scene_index:02d}.jpg"
        img.convert("RGB").save(output_path, quality=92)
        return str(output_path)


scene_image_generator = SceneImageGenerator()
