import re
from typing import Dict, Any, List


class VideoPlanner:
    """
    Prompt -> Video Plan
    V3: better subject extraction + better promo scenes
    """

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

        promo_keywords = [
            "promo", "diskon", "jualan", "produk", "order", "beli",
            "ramadan", "stok", "harga", "murah", "sale"
        ]
        edu_keywords = [
            "tips", "cara", "tutorial", "belajar", "edukasi", "how to", "panduan"
        ]
        motivation_keywords = [
            "motivasi", "semangat", "mindset", "inspirasi"
        ]
        story_keywords = [
            "cerita", "kisah", "story", "perjalanan", "pengalaman"
        ]

        if any(k in t for k in promo_keywords):
            return "promo"
        if any(k in t for k in edu_keywords):
            return "education"
        if any(k in t for k in motivation_keywords):
            return "motivation"
        if any(k in t for k in story_keywords):
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

        replacements = [
            "promo", "tentang", "mengenai", "soal",
            "yang", "untuk", "dengan", "buat", "bikin"
        ]
        tokens = [tok for tok in re.split(r'\s+', s) if tok]
        filtered = [tok for tok in tokens if tok not in replacements]

        s = " ".join(filtered)
        s = re.sub(r'\s+', ' ', s).strip(" ,.-")
        return s

    def _extract_subject(self, prompt: str, video_type: str) -> str:
        base = self._extract_core_subject(prompt)
        prompt_l = prompt.lower()

        if not base:
            if video_type == "promo":
                base = "Produk Andalan"
            elif video_type == "education":
                base = "Tips Bisnis"
            elif video_type == "motivation":
                base = "Motivasi Usaha"
            elif video_type == "story":
                base = "Cerita Inspiratif"
            else:
                base = "Topik Utama"

        base = self._title_case_subject(base[:60])

        if video_type == "promo":
            if "ramadan" in prompt_l and "Ramadan" not in base:
                return f"{base} Promo Ramadan"
            if "promo" not in base.lower():
                return f"{base} Promo"

        return base

    def _promo_scenes(self, subject: str, prompt: str) -> List[Dict[str, Any]]:
        t = prompt.lower()
        is_ramadan = "ramadan" in t
        is_premium = "premium" in t or "mewah" in t

        hook = f"{subject}"
        subtitle = "Promo spesial hari ini"
        if is_ramadan:
            subtitle = "Promo spesial Ramadan"
        if is_premium:
            subtitle = f"{subtitle} • Edisi premium"

        return [
            {"kind": "hook", "title": subject, "text": subtitle},
            {"kind": "product", "title": "Produk Unggulan", "text": f"{subject} siap menarik perhatian pelanggan"},
            {"kind": "benefit", "title": "Kenapa Menarik?", "text": "Visual kuat, positioning jelas, dan cocok untuk konten jualan cepat"},
            {"kind": "offer", "title": "Penawaran", "text": "Saatnya ambil momentum promo sebelum kompetitor bergerak"},
            {"kind": "cta", "title": "Order Sekarang", "text": "Jangan tunggu lama, dorong penjualan mulai hari ini"},
        ]

    def _education_scenes(self, subject: str) -> List[Dict[str, Any]]:
        return [
            {"kind": "hook", "title": subject, "text": "Pelajari inti pentingnya dalam waktu singkat"},
            {"kind": "point", "title": "Poin 1", "text": "Mulai dari hal yang paling mendasar tapi paling penting"},
            {"kind": "point", "title": "Poin 2", "text": "Gunakan langkah yang praktis dan mudah diterapkan"},
            {"kind": "point", "title": "Poin 3", "text": "Jangan abaikan detail yang sering dianggap sepele"},
            {"kind": "cta", "title": "Follow Untuk Lanjutannya", "text": "Masih banyak insight yang bisa dipakai langsung"},
        ]

    def _motivation_scenes(self, subject: str) -> List[Dict[str, Any]]:
        return [
            {"kind": "hook", "title": subject, "text": "Bangun langkah besar dari keputusan hari ini"},
            {"kind": "mindset", "title": "Mindset", "text": "Kemajuan datang dari konsistensi, bukan dari motivasi sesaat"},
            {"kind": "action", "title": "Aksi", "text": "Mulai kecil, bergerak terus, dan evaluasi dengan jujur"},
            {"kind": "reinforce", "title": "Penguat", "text": "Setiap proses yang dijalani akan membentuk hasil yang kuat"},
            {"kind": "cta", "title": "Mulai Hari Ini", "text": "Jangan tunggu sempurna untuk bergerak"},
        ]

    def _story_scenes(self, subject: str) -> List[Dict[str, Any]]:
        return [
            {"kind": "hook", "title": subject, "text": "Sebuah kisah singkat yang layak didengar"},
            {"kind": "setup", "title": "Awal Cerita", "text": "Semua dimulai dari situasi sederhana"},
            {"kind": "conflict", "title": "Tantangan", "text": "Ada hambatan, tapi proses tetap berjalan"},
            {"kind": "resolution", "title": "Perubahan", "text": "Dari konsistensi lahir hasil yang mulai terlihat"},
            {"kind": "cta", "title": "Ambil Pelajarannya", "text": "Sekarang giliranmu menulis cerita sendiri"},
        ]

    def _general_scenes(self, subject: str) -> List[Dict[str, Any]]:
        return [
            {"kind": "hook", "title": subject, "text": "Sampaikan inti pesannya dengan tajam"},
            {"kind": "body", "title": "Inti Utama", "text": "Bangun pesan utama yang mudah dipahami"},
            {"kind": "body", "title": "Penguat", "text": "Tambahkan alasan kenapa ini penting"},
            {"kind": "body", "title": "Relevansi", "text": "Hubungkan dengan kebutuhan penonton"},
            {"kind": "cta", "title": "Penutup", "text": "Akhiri dengan ajakan yang jelas"},
        ]

    def build_plan(
        self,
        prompt: str,
        duration: int = 15,
        style: str = "engaging",
        language: str = "id",
    ) -> Dict[str, Any]:
        prompt = self._clean_text(prompt)
        final_duration = self._extract_duration(prompt, fallback=duration)
        video_type = self._detect_type(prompt)
        platform = self._detect_platform(prompt)
        final_style = self._detect_style(prompt, fallback=style)
        subject = self._extract_subject(prompt, video_type)

        if video_type == "promo":
            scenes = self._promo_scenes(subject, prompt)
        elif video_type == "education":
            scenes = self._education_scenes(subject)
        elif video_type == "motivation":
            scenes = self._motivation_scenes(subject)
        elif video_type == "story":
            scenes = self._story_scenes(subject)
        else:
            scenes = self._general_scenes(subject)

        return {
            "prompt": prompt,
            "type": video_type,
            "platform": platform,
            "style": final_style,
            "language": language,
            "duration": final_duration,
            "subject": subject,
            "scenes": scenes,
        }


video_planner = VideoPlanner()
