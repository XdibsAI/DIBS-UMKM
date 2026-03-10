import re
from typing import Any, Dict, List, Optional


SCENE_KIND_MAP = {
    "pembuka": "hook",
    "opening": "hook",
    "hook": "hook",
    "akuisisi": "problem",
    "masalah": "problem",
    "problem": "problem",
    "transformasi": "transformation",
    "perubahan": "transformation",
    "solusi": "solution",
    "klimaks": "climax",
    "penutup": "cta",
    "closing": "cta",
    "cta": "cta",
    "call to action": "cta",
    "review": "review",
    "tutorial": "tutorial",
    "edukasi": "education",
    "motivasi": "motivation",
}


def _clean(text: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _parse_duration(text: str, default: int = 15) -> int:
    if not text:
        return default

    patterns = [
        r"durasi\s*[:\-]?\s*(\d+)\s*[–-]\s*(\d+)\s*detik",
        r"durasi\s*[:\-]?\s*(\d+)\s*[–-]\s*(\d+)\s*dtk",
        r"durasi\s*[:\-]?\s*(\d+)\s*detik",
        r"durasi\s*[:\-]?\s*(\d+)\s*dtk",
    ]
    lowered = text.lower()
    for p in patterns:
        m = re.search(p, lowered)
        if m:
            if len(m.groups()) == 2:
                return max(10, int((int(m.group(1)) + int(m.group(2))) / 2))
            return max(10, int(m.group(1)))
    return default


def _extract_field(prompt: str, label: str) -> str:
    pattern = rf"{label}\s*[:\-]\s*(.+?)(?=\n\s*\n|\n\s*[A-ZA-ZÀ-ÿ][^:\n]{{0,40}}[:\-]|$)"
    m = re.search(pattern, prompt, flags=re.I | re.S)
    return _clean(m.group(1)) if m else ""


def _guess_type(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["motivasi", "inspirasi", "bangkit", "semangat hidup"]):
        return "motivasi"
    if any(k in p for k in ["tutorial", "cara ", "langkah", "how to"]):
        return "tutorial"
    if any(k in p for k in ["edukasi", "penjelasan", "fakta", "belajar"]):
        return "edukasi"
    if any(k in p for k in ["review", "ulasan"]):
        return "review"
    if any(k in p for k in ["promo", "jualan", "iklan", "order", "diskon"]):
        return "promo"
    return "general"


def _scene_kind_from_title(title: str, default_kind: str = "scene") -> str:
    t = title.lower()
    for key, value in SCENE_KIND_MAP.items():
        if key in t:
            return value
    return default_kind


def _short_caption(title: str, text: str) -> str:
    source = _clean(title) or _clean(text)
    if not source:
        return ""
    words = source.split()
    return " ".join(words[:5]).strip()


def _split_scene_line(scene_title: str, raw: str) -> Dict[str, str]:
    raw = raw.strip(" –-")
    parts = re.split(r"\s+[–-]\s+|:\s+", raw, maxsplit=1)
    visual = ""
    text = raw
    if len(parts) == 2:
        text = _clean(parts[1])
    visual_match = re.search(r"visual\s+(.+)", raw, flags=re.I)
    if visual_match:
        visual = _clean(visual_match.group(1))
    return {
        "kind": _scene_kind_from_title(scene_title),
        "title": _clean(scene_title),
        "text": _clean(text),
        "visual": visual,
        "caption": _short_caption(scene_title, text),
    }


def _parse_structured_scenes(prompt: str) -> List[Dict[str, Any]]:
    blocks = []
    scene_block_match = re.search(
        r"struktur\s+narasi\s*[:\-]?\s*(.+?)(?=\n\s*(visual\s*&\s*musik|visual|musik|tips produksi|tips|logo)\s*[:\-]|$)",
        prompt,
        flags=re.I | re.S,
    )
    if scene_block_match:
        block = scene_block_match.group(1).strip()
        pattern = r"(?:^|\n)\s*(\d+)\.\s*\*\*(.*?)\*\*\s*(?:\((.*?)\))?\s*[–-]\s*(.+?)(?=(?:\n\s*\d+\.\s*\*\*|$))"
        matches = list(re.finditer(pattern, block, flags=re.S))
        if matches:
            for m in matches:
                title = _clean(m.group(2))
                timing = _clean(m.group(3))
                body = _clean(m.group(4))
                scene = _split_scene_line(title, body)
                if timing:
                    scene["timing"] = timing
                blocks.append(scene)

    if blocks:
        return blocks

    lines = [x.strip() for x in prompt.splitlines() if x.strip()]
    numbered = []
    for line in lines:
        m = re.match(r"^\d+\.\s*(.+)$", line)
        if m:
            numbered.append(m.group(1).strip())
    for line in numbered[:8]:
        scene = _split_scene_line(line.split("–")[0].split("-")[0], line)
        blocks.append(scene)

    return blocks


def _fallback_scenes(
    prompt: str,
    video_type: str,
    subject: str,
    cta_text: str,
    price_text: str,
) -> List[Dict[str, Any]]:
    if video_type == "motivasi":
        return [
            {"kind": "hook", "title": "Awal Baru", "text": "Setiap pagi adalah kesempatan untuk memulai lagi.", "caption": "Awal baru"},
            {"kind": "problem", "title": "Jatuh Itu Wajar", "text": "Kegagalan kecil bukan alasan untuk berhenti.", "caption": "Tetap jalan"},
            {"kind": "transformation", "title": "Mulai Bergerak", "text": "Langkah kecil yang konsisten akan mengubah hidupmu.", "caption": "Mulai bangkit"},
            {"kind": "climax", "title": "Saatnya Bersinar", "text": "Keberhasilan lahir dari proses yang terus dijalani.", "caption": "Saatnya bersinar"},
            {"kind": "cta", "title": "Bangkit Hari Ini", "text": cta_text or "Bagikan video ini untuk menyemangati orang lain.", "caption": "Bagikan motivasi"},
        ]
    if video_type in {"tutorial", "edukasi"}:
        return [
            {"kind": "hook", "title": "Mulai dari Dasar", "text": subject, "caption": "Mulai dari dasar"},
            {"kind": "tutorial", "title": "Langkah 1", "text": "Pahami inti masalah dan tujuan utamanya.", "caption": "Langkah 1"},
            {"kind": "tutorial", "title": "Langkah 2", "text": "Lakukan proses inti dengan fokus dan konsisten.", "caption": "Langkah 2"},
            {"kind": "solution", "title": "Hasil", "text": "Evaluasi hasil dan perbaiki langkah yang kurang.", "caption": "Evaluasi hasil"},
            {"kind": "cta", "title": "Praktik Sekarang", "text": cta_text or "Simpan video ini untuk dipraktikkan nanti.", "caption": "Praktik sekarang"},
        ]
    return [
        {"kind": "hook", "title": subject, "text": "Promo spesial yang layak dilihat sekarang.", "caption": "Lihat sekarang"},
        {"kind": "product", "title": "Produk Unggulan", "text": subject, "caption": "Produk unggulan"},
        {"kind": "benefit", "title": "Kenapa Menarik", "text": "Visual kuat, positioning jelas, dan cocok untuk konten jualan cepat.", "caption": "Kenapa menarik"},
        {"kind": "offer", "title": "Penawaran", "text": f"Mulai dari {price_text}" if price_text else "Ada penawaran spesial untuk waktu terbatas.", "caption": "Penawaran spesial"},
        {"kind": "cta", "title": "Aksi Sekarang", "text": cta_text or "Order sekarang sebelum kehabisan.", "caption": "Order sekarang"},
    ]


def build_plan(
    prompt: str,
    duration: int = 15,
    style: str = "premium",
    language: str = "id",
    product_name: Optional[str] = None,
    price_text: Optional[str] = None,
    cta_text: Optional[str] = None,
    brand_name: Optional[str] = None,
    product_image_url: Optional[str] = None,
) -> Dict[str, Any]:
    prompt = (prompt or "").strip()
    title = _extract_field(prompt, "judul") or product_name or _clean(prompt[:80]) or "Video"
    parsed_duration = _parse_duration(prompt, duration)
    theme = _extract_field(prompt, "tema")
    visual_music = _extract_field(prompt, r"visual\s*&\s*musik") or _extract_field(prompt, "visual") or _extract_field(prompt, "musik")
    tips = _extract_field(prompt, r"tips produksi") or _extract_field(prompt, "tips")
    final_type = _guess_type(prompt)
    brand = brand_name or "Dibs AI"
    final_cta = cta_text or (
        "Bagikan video ini dengan yang membutuhkan motivasi!"
        if final_type == "motivasi"
        else "Order sekarang"
    )

    scenes = _parse_structured_scenes(prompt)
    if not scenes:
        scenes = _fallback_scenes(
            prompt=prompt,
            video_type=final_type,
            subject=product_name or title,
            cta_text=final_cta,
            price_text=price_text or "",
        )

    cleaned_scenes: List[Dict[str, Any]] = []
    for idx, scene in enumerate(scenes[:8], start=1):
        title_text = _clean(scene.get("title") or f"Scene {idx}")
        body_text = _clean(scene.get("text") or "")
        if len(body_text.split()) > 16:
            body_text = " ".join(body_text.split()[:16]).strip()
        cleaned_scenes.append({
            "kind": scene.get("kind") or "scene",
            "title": title_text,
            "text": body_text,
            "caption": _short_caption(scene.get("caption") or title_text, body_text),
            "brand": brand,
            "visual": _clean(scene.get("visual") or ""),
            "timing": _clean(scene.get("timing") or ""),
            "product_name": product_name or "",
            "price_text": price_text or "",
            "cta_text": final_cta if scene.get("kind") == "cta" else "",
            "product_image_url": product_image_url or "",
            "image_prompt": _clean(scene.get("visual") or body_text or title_text),
        })

    return {
        "prompt": prompt,
        "type": final_type,
        "platform": "shorts",
        "style": style,
        "language": language,
        "duration": parsed_duration,
        "title": title,
        "subject": product_name or title,
        "theme": theme,
        "visual_music": visual_music,
        "tips": tips,
        "product_name": product_name or "",
        "price_text": price_text or "",
        "cta_text": final_cta,
        "brand_name": brand,
        "product_image_url": product_image_url or "",
        "scenes": cleaned_scenes,
    }


class VideoPlanner:
    def build_plan(
        self,
        prompt: str,
        duration: int = 15,
        style: str = "premium",
        language: str = "id",
        product_name=None,
        price_text=None,
        cta_text=None,
        brand_name=None,
        product_image_url=None,
    ):
        return build_plan(
            prompt=prompt,
            duration=duration,
            style=style,
            language=language,
            product_name=product_name,
            price_text=price_text,
            cta_text=cta_text,
            brand_name=brand_name,
            product_image_url=product_image_url,
        )


video_planner = VideoPlanner()
