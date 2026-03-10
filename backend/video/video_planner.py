import re
from typing import Dict, Any, List, Optional


class VideoPlanner:
    STOP_PREFIXES = [
        "buat video",
        "buatkan video",
        "bikin video",
        "tolong buat video",
        "generate video",
        "buat",
        "bikin",
    ]

    def _clean_text(self, text: str) -> str:
        text = (text or "").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _detect_type(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["promo", "diskon", "jualan", "produk", "order", "beli", "ramadan", "stok", "harga", "sale"]):
            return "promo"
        if any(k in t for k in ["tips", "cara", "tutorial", "belajar", "edukasi", "how to", "panduan"]):
            return "education"
        if any(k in t for k in ["motivasi", "semangat", "mindset", "inspirasi"]):
            return "motivation"
        if any(k in t for k in ["cerita", "kisah", "story", "perjalanan", "pengalaman"]):
            return "story"
        return "general"

    def _detect_platform(self, text: str) -> str:
        t = text.lower()
        if "youtube shorts" in t or "shorts" in t:
            return "shorts"
        if "tiktok" in t:
            return "tiktok"
        if "reels" in t or "instagram" in t:
            return "reels"
        return "shorts"

    def _detect_style(self, text: str, fallback: str = "engaging") -> str:
        t = text.lower()
        if "premium" in t or "mewah" in t:
            return "premium"
        if "cinematic" in t:
            return "cinematic"
        if "fun" in t or "seru" in t:
            return "fun"
        if "formal" in t:
            return "formal"
        return fallback

    def _extract_duration(self, text: str, fallback: int = 15) -> int:
        m = re.search(r'(\d{1,3})\s*(detik|seconds|sec|s)\b', text.lower())
        if m:
            try:
                value = int(m.group(1))
                return max(5, min(value, 180))
            except Exception:
                pass
        return fallback

    def _title_case_subject(self, subject: str) -> str:
        if not subject:
            return "Video Baru"
        words = subject.split()
        small_words = {"dan", "untuk", "di", "ke", "dengan", "yang", "atau"}
        result = []
        for i, word in enumerate(words):
            if i > 0 and word.lower() in small_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        return " ".join(result)

    def _extract_core_subject(self, prompt: str) -> str:
        s = prompt.lower().strip()

        for prefix in self.STOP_PREFIXES:
            if s.startswith(prefix):
                s = s[len(prefix):].strip()

        removable_patterns = [
            r'\b\d{1,3}\s*(detik|seconds|sec|s)\b',
            r'\bgaya\s+[a-zA-Z]+\b',
            r'\buntuk\s+ramadan\b',
            r'\buntuk\s+tiktok\b',
            r'\buntuk\s+reels\b',
            r'\buntuk\s+shorts\b',
            r'\bdengan\s+ajakan\s+order\s+sekarang\b',
            r'\bdengan\s+cta\b',
            r'\bdengan\s+call to action\b',
            r'\bvideo\b',
            r'\bpremium\b',
            r'\bcinematic\b',
            r'\bformal\b',
            r'\bfun\b',
            r'\bseru\b',
        ]
        for pattern in removable_patterns:
            s = re.sub(pattern, '', s).strip()

        replacements = ["promo", "tentang", "mengenai", "soal", "yang", "untuk", "dengan", "buat", "bikin"]
        tokens = [tok for tok in re.split(r'\s+', s) if tok]
        filtered = [tok for tok in tokens if tok not in replacements]

        s = " ".join(filtered)
        s = re.sub(r'\s+', ' ', s).strip(" ,.-")
        return s

    def _extract_subject(self, prompt: str, video_type: str, product_name: Optional[str] = None) -> str:
        if product_name and product_name.strip():
            base = product_name.strip()
        else:
            base = self._extract_core_subject(prompt)

        prompt_l = prompt.lower()

        if not base:
            defaults = {
                "promo": "Produk Andalan",
                "education": "Tips Bisnis",
                "motivation": "Motivasi Usaha",
                "story": "Cerita Inspiratif",
                "general": "Topik Utama",
            }
            base = defaults.get(video_type, "Topik Utama")

        base = self._title_case_subject(base[:60])

        if video_type == "promo":
            if "ramadan" in prompt_l and "Ramadan" not in base:
                return f"{base} Promo Ramadan"
            if "promo" not in base.lower():
                return f"{base} Promo"
        return base

    def _default_cta(self, prompt: str, cta_text: Optional[str]) -> str:
        if cta_text and cta_text.strip():
            return cta_text.strip()[:70]
        if "whatsapp" in prompt.lower():
            return "Chat WhatsApp sekarang"
        return "Order sekarang sebelum kehabisan"

    def _default_offer(self, prompt: str, price_text: Optional[str]) -> str:
        if price_text and price_text.strip():
            return f"Mulai dari {price_text.strip()}"
        if "diskon" in prompt.lower():
            return "Diskon spesial hari ini"
        if "ramadan" in prompt.lower():
            return "Promo terbatas selama Ramadan"
        return "Promo terbatas, ambil sekarang"

    def _promo_scenes(
        self,
        subject: str,
        prompt: str,
        product_name: Optional[str] = None,
        price_text: Optional[str] = None,
        cta_text: Optional[str] = None,
        brand_name: Optional[str] = None,
        product_image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        t = prompt.lower()
        is_ramadan = "ramadan" in t
        is_premium = "premium" in t or "mewah" in t

        hook_subtitle = "Promo spesial hari ini"
        if is_ramadan:
            hook_subtitle = "Promo spesial Ramadan"
        if is_premium:
            hook_subtitle = f"{hook_subtitle} • Edisi premium"

        product_display = product_name.strip() if product_name and product_name.strip() else subject
        offer_display = self._default_offer(prompt, price_text)
        cta_display = self._default_cta(prompt, cta_text)
        brand_display = brand_name.strip() if brand_name and brand_name.strip() else "DIBS AI"

        return [
            {
                "kind": "hook",
                "title": subject,
                "text": hook_subtitle,
                "brand": brand_display,
            },
            {
                "kind": "product",
                "title": "Produk Unggulan",
                "text": f"{product_display} siap menarik perhatian pelanggan",
                "product_name": product_display,
                "brand": brand_display,
                "product_image_url": product_image_url or "",
            },
            {
                "kind": "benefit",
                "title": "Kenapa Menarik?",
                "text": "Visual kuat, positioning jelas, dan cocok untuk konten jualan cepat",
                "brand": brand_display,
            },
            {
                "kind": "offer",
                "title": "Penawaran",
                "text": offer_display,
                "price_text": price_text or "",
                "brand": brand_display,
            },
            {
                "kind": "cta",
                "title": "Aksi Sekarang",
                "text": cta_display,
                "cta_text": cta_display,
                "brand": brand_display,
            },
        ]

    def _education_scenes(self, subject: str, brand_name: Optional[str] = None) -> List[Dict[str, Any]]:
        brand_display = brand_name.strip() if brand_name and brand_name.strip() else "DIBS AI"
        return [
            {"kind": "hook", "title": subject, "text": "Pelajari inti pentingnya dalam waktu singkat", "brand": brand_display},
            {"kind": "point", "title": "Poin 1", "text": "Mulai dari hal yang paling mendasar tapi paling penting", "brand": brand_display},
            {"kind": "point", "title": "Poin 2", "text": "Gunakan langkah yang praktis dan mudah diterapkan", "brand": brand_display},
            {"kind": "point", "title": "Poin 3", "text": "Jangan abaikan detail yang sering dianggap sepele", "brand": brand_display},
            {"kind": "cta", "title": "Follow Untuk Lanjutannya", "text": "Masih banyak insight yang bisa dipakai langsung", "brand": brand_display},
        ]

    def _motivation_scenes(self, subject: str, brand_name: Optional[str] = None) -> List[Dict[str, Any]]:
        brand_display = brand_name.strip() if brand_name and brand_name.strip() else "DIBS AI"
        return [
            {"kind": "hook", "title": subject, "text": "Bangun langkah besar dari keputusan hari ini", "brand": brand_display},
            {"kind": "mindset", "title": "Mindset", "text": "Kemajuan datang dari konsistensi, bukan motivasi sesaat", "brand": brand_display},
            {"kind": "action", "title": "Aksi", "text": "Mulai kecil, bergerak terus, dan evaluasi dengan jujur", "brand": brand_display},
            {"kind": "reinforce", "title": "Penguat", "text": "Setiap proses yang dijalani akan membentuk hasil yang kuat", "brand": brand_display},
            {"kind": "cta", "title": "Mulai Hari Ini", "text": "Jangan tunggu sempurna untuk bergerak", "brand": brand_display},
        ]

    def _story_scenes(self, subject: str, brand_name: Optional[str] = None) -> List[Dict[str, Any]]:
        brand_display = brand_name.strip() if brand_name and brand_name.strip() else "DIBS AI"
        return [
            {"kind": "hook", "title": subject, "text": "Sebuah kisah singkat yang layak didengar", "brand": brand_display},
            {"kind": "setup", "title": "Awal Cerita", "text": "Semua dimulai dari situasi sederhana", "brand": brand_display},
            {"kind": "conflict", "title": "Tantangan", "text": "Ada hambatan, tapi proses tetap berjalan", "brand": brand_display},
            {"kind": "resolution", "title": "Perubahan", "text": "Dari konsistensi lahir hasil yang mulai terlihat", "brand": brand_display},
            {"kind": "cta", "title": "Ambil Pelajarannya", "text": "Sekarang giliranmu menulis cerita sendiri", "brand": brand_display},
        ]

    def _general_scenes(self, subject: str, brand_name: Optional[str] = None) -> List[Dict[str, Any]]:
        brand_display = brand_name.strip() if brand_name and brand_name.strip() else "DIBS AI"
        return [
            {"kind": "hook", "title": subject, "text": "Sampaikan inti pesannya dengan tajam", "brand": brand_display},
            {"kind": "body", "title": "Inti Utama", "text": "Bangun pesan utama yang mudah dipahami", "brand": brand_display},
            {"kind": "body", "title": "Penguat", "text": "Tambahkan alasan kenapa ini penting", "brand": brand_display},
            {"kind": "body", "title": "Relevansi", "text": "Hubungkan dengan kebutuhan penonton", "brand": brand_display},
            {"kind": "cta", "title": "Penutup", "text": "Akhiri dengan ajakan yang jelas", "brand": brand_display},
        ]

    def build_plan(
        self,
        prompt: str,
        duration: int = 15,
        style: str = "engaging",
        language: str = "id",
        product_name: Optional[str] = None,
        price_text: Optional[str] = None,
        cta_text: Optional[str] = None,
        brand_name: Optional[str] = None,
        product_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt = self._clean_text(prompt)
        final_duration = self._extract_duration(prompt, fallback=duration)
        video_type = self._detect_type(prompt)
        platform = self._detect_platform(prompt)
        final_style = self._detect_style(prompt, fallback=style)
        subject = self._extract_subject(prompt, video_type, product_name=product_name)

        if video_type == "promo":
            scenes = self._promo_scenes(
                subject,
                prompt,
                product_name=product_name,
                price_text=price_text,
                cta_text=cta_text,
                brand_name=brand_name,
                product_image_url=product_image_url,
            )
        elif video_type == "education":
            scenes = self._education_scenes(subject, brand_name=brand_name)
        elif video_type == "motivation":
            scenes = self._motivation_scenes(subject, brand_name=brand_name)
        elif video_type == "story":
            scenes = self._story_scenes(subject, brand_name=brand_name)
        else:
            scenes = self._general_scenes(subject, brand_name=brand_name)

        return {
            "prompt": prompt,
            "type": video_type,
            "platform": platform,
            "style": final_style,
            "language": language,
            "duration": final_duration,
            "subject": subject,
            "product_name": product_name,
            "price_text": price_text,
            "cta_text": cta_text,
            "brand_name": brand_name,
            "product_image_url": product_image_url,
            "scenes": scenes,
        }


video_planner = VideoPlanner()
