import re
from typing import Dict, List


class SimplePanelObserver:
    ACTION_WORDS = [
        "buat", "tambah", "implement", "gunakan", "pakai", "hubungkan",
        "integrasi", "simpan", "ubah", "cek", "bangun", "siapkan",
        "aktifkan", "catat", "load", "link",
    ]

    def _split_lines(self, text: str) -> List[str]:
        return [x.strip() for x in (text or "").splitlines() if x.strip()]

    def _extract_bullets(self, text: str) -> List[str]:
        points = []
        for line in self._split_lines(text):
            if re.match(r"^[-•]\s+", line) or re.match(r"^\d+\.\s+", line):
                clean = re.sub(r"^[-•]\s+", "", line)
                clean = re.sub(r"^\d+\.\s+", "", clean)
                if clean:
                    points.append(clean.strip())
        return points

    def _action_items(self, points: List[str]) -> List[str]:
        out = []
        for p in points:
            low = p.lower()
            if any(word in low for word in self.ACTION_WORDS):
                out.append(p)
        return out[:6]

    def observe(
        self,
        topic: str,
        nemo_reply: str,
        kimi_reply: str,
        moderator_summary: str,
    ) -> Dict[str, object]:
        nemo_points = self._extract_bullets(nemo_reply)
        kimi_points = self._extract_bullets(kimi_reply)

        key_points = []
        for item in nemo_points[:3] + kimi_points[:3]:
            if item not in key_points:
                key_points.append(item)

        action_items = self._action_items(key_points)

        raw_summary = (
            f"Diskusi membahas: {topic}. "
            f"Moderator menekankan irisan paling realistis. "
            f"Nemo fokus ke sisi teknis/stabilitas, Kimi fokus ke opsi strategi/efisiensi."
        )

        return {
            "raw_summary": raw_summary,
            "key_points": key_points[:6],
            "action_items": action_items[:6],
        }
