import os
from typing import Optional, List
from urllib.parse import urlparse

import requests
from dotenv import dotenv_values, load_dotenv

load_dotenv()

SERPER_ENDPOINT = "https://google.serper.dev/images"

BAD_DOMAINS = {
    "shutterstock.com",
    "www.shutterstock.com",
    "tiktok.com",
    "www.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "lookaside.instagram.com",
    "pinterest.com",
    "www.pinterest.com",
    "facebook.com",
    "www.facebook.com",
}

GOOD_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def _read_serper_key() -> str:
    key = (os.getenv("SERPER_API_KEY") or "").strip()
    if key:
        return key

    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        values = dotenv_values(env_path)
        key = str(values.get("SERPER_API_KEY") or "").strip()
        if key:
            return key

    backend_env_path = "/home/dibs/dibs1/backend/.env"
    if os.path.exists(backend_env_path):
        values = dotenv_values(backend_env_path)
        key = str(values.get("SERPER_API_KEY") or "").strip()
        if key:
            return key

    return ""


def _extract_candidates(data: dict) -> List[dict]:
    images = data.get("images")
    if isinstance(images, list):
        return images

    candidates = []
    for key in ("items", "organic"):
        value = data.get(key)
        if isinstance(value, list):
            candidates.extend(value)
    return candidates


def _pick_image_url(item: dict) -> Optional[str]:
    for key in (
        "imageUrl",
        "image_url",
        "thumbnailUrl",
        "thumbnail_url",
        "link",
        "sourceUrl",
        "source_url",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
    return None


def _is_allowed_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()
        path = (parsed.path or "").lower()

        if domain in BAD_DOMAINS:
            return False

        if any(domain.endswith(bad) for bad in BAD_DOMAINS):
            return False

        if path.endswith(GOOD_EXTENSIONS):
            return True

        # allow some image-serving urls without extension
        if "image" in path or "upload" in path or "media" in path:
            return True

        return False
    except Exception:
        return False


def search_product_image(query: str, num: int = 8, debug: bool = False) -> Optional[str]:
    api_key = _read_serper_key()
    query = (query or "").strip()

    if not api_key:
        if debug:
            print("DEBUG: SERPER_API_KEY empty")
        return None

    if not query:
        if debug:
            print("DEBUG: query empty")
        return None

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "q": query,
        "gl": "id",
        "hl": "id",
        "type": "images",
        "engine": "google",
        "num": num,
    }

    try:
        response = requests.post(SERPER_ENDPOINT, json=payload, headers=headers, timeout=30)
        if debug:
            print("DEBUG: status", response.status_code)
            print("DEBUG: body", response.text[:1200])

        response.raise_for_status()
        data = response.json()
        candidates = _extract_candidates(data)

        # pass 1: strict filter
        for item in candidates:
            image_url = _pick_image_url(item)
            if image_url and _is_allowed_url(image_url):
                return image_url

        # pass 2: fallback but still avoid blacklisted domains
        for item in candidates:
            image_url = _pick_image_url(item)
            if not image_url:
                continue
            domain = (urlparse(image_url).netloc or "").lower()
            if domain not in BAD_DOMAINS and not any(domain.endswith(b) for b in BAD_DOMAINS):
                return image_url

        return None
    except Exception as e:
        if debug:
            print("DEBUG: exception", repr(e))
        return None


def build_visual_search_query(
    prompt: str = "",
    subject: str = "",
    product_name: str = "",
    video_type: str = "",
    style: str = "",
    scene_kind: str = "",
) -> str:
    prompt = (prompt or "").strip()
    subject = (subject or "").strip()
    product_name = (product_name or "").strip()
    video_type = (video_type or "").strip().lower()
    style = (style or "").strip().lower()
    scene_kind = (scene_kind or "").strip().lower()

    base = product_name or subject or prompt or "content visual"

    if video_type in {"tutorial", "education", "edukasi", "howto"}:
        return f"{base} tutorial illustration vertical social media"
    if video_type in {"story", "storytelling"}:
        return f"{base} cinematic storytelling poster vertical"
    if video_type in {"review"}:
        return f"{base} review visual poster vertical"
    if video_type in {"promo", "marketing", "ads"}:
        if scene_kind == "product":
            return f"{base} product photo packaging vertical advertisement"
        if scene_kind == "offer":
            return f"{base} promotional sale banner vertical advertisement"
        if scene_kind == "cta":
            return f"{base} call to action marketing poster vertical"
        return f"{base} premium promotional poster vertical advertisement"

    return f"{base} vertical social media visual {style}".strip()
