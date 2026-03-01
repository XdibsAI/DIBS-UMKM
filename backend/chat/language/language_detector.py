"""
DIBS Language Detection Module
Gabungan dari semua file language detection:
- language_intelligence.py (paling lengkap)
- language_detector.py (yang lama)
- Bagian language dari nvidia_wrapper.py
"""

import re
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# REGIONAL LANGUAGE PATTERNS
# ============================================================================

# Bahasa Jawa
JAVANESE_PATTERNS = {
    'greetings': ['kabare', 'pripun', 'matur nuwun', 'sugeng', 'monggo', 'nuwun'],
    'numbers': ['siji', 'loro', 'telu', 'papat', 'limo', 'enem', 'pitu', 'wolu', 'songo', 'sepuluh'],
    'common': ['sampun', 'dereng', 'pinten', 'niku', 'napa', 'punapa', 'wonten', 'mboten', 'sinten', 'pundi'],
    'keywords': ['nggih', 'sampun', 'dereng', 'pundi', 'menapa', 'piye', 'opo', 'ning', 'wis', 'durung', 'saiki', 'kowe', 'aku']
}

# Bahasa Sunda
SUNDANESE_PATTERNS = {
    'greetings': ['kumaha', 'damang', 'hatur nuhun', 'wilujeng', 'mangga', 'punten'],
    'common': ['parantos', 'teu acan', 'sabaraha', 'naon', 'dimana', 'iraha', 'saha', 'aya', 'teu', 'muhun'],
    'keywords': ['kumaha', 'naon', 'saha', 'iraha', 'dimana', 'abdi', 'anjeun']
}

# Bahasa Betawi
BETAWI_PATTERNS = {
    'greetings': ['ape kabar', 'gimane', 'makasih ye'],
    'common': ['udah', 'belom', 'berape', 'apaan', 'dimane', 'kagak', 'kaga', 'gue', 'loe'],
    'keywords': ['ape', 'kagak', 'gue', 'loe', 'kaga', 'udah', 'belom']
}

# Bahasa Melayu
MELAYU_PATTERNS = {
    'greetings': ['apa khabar', 'terima kasih', 'sila'],
    'common': ['betul', 'salah', 'hendak', 'boleh', 'khabar', 'hendak', 'betul'],
    'keywords': ['khabar', 'hendak', 'betul']
}

# ============================================================================
# REGIONAL DICTIONARY (for translation)
# ============================================================================

REGIONAL_DICT = {
    'jawa': {
        'nuwun': 'terima kasih',
        'sampun': 'sudah',
        'dereng': 'belum',
        'menapa': 'apa',
        'pundi': 'mana',
        'pinten': 'berapa',
        'mangga': 'silakan',
        'pripun': 'bagaimana',
        'sinten': 'siapa',
        'wonten': 'ada',
    },
    'sunda': {
        'hatur nuhun': 'terima kasih',
        'punten': 'permisi/maaf',
        'kumaha': 'bagaimana',
        'naon': 'apa',
        'dimana': 'di mana',
        'sabaraha': 'berapa',
        'saha': 'siapa',
        'aya': 'ada',
        'teu': 'tidak',
        'muhun': 'ya',
    },
    'melayu': {
        'apa khabar': 'apa kabar',
        'terima kasih': 'terima kasih',
        'sila': 'silakan',
        'betul': 'benar',
        'salah': 'salah',
        'hendak': 'mau',
        'boleh': 'bisa',
    },
    'betawi': {
        'ape': 'apa',
        'kagak': 'tidak',
        'gue': 'saya',
        'loe': 'kamu',
        'kaga': 'tidak',
        'udah': 'sudah',
        'belom': 'belum',
    }
}

# ============================================================================
# MAIN LANGUAGE DETECTOR CLASS
# ============================================================================

class LanguageDetector:
    """Unified Language Detector for Indonesian regional languages"""
    
    def __init__(self):
        self.supported_languages = ['indonesian', 'javanese', 'sundanese', 'betawi', 'melayu']
        
    def detect(self, text: str) -> str:
        """
        Detect language from text
        Returns: language code (indonesian/javanese/sundanese/betawi/melayu)
        """
        if not text or not isinstance(text, str):
            return 'indonesian'
            
        text_lower = text.lower()
        
        # Hitung skor untuk setiap bahasa
        scores = {
            'javanese': self._count_matches(text_lower, JAVANESE_PATTERNS),
            'sundanese': self._count_matches(text_lower, SUNDANESE_PATTERNS),
            'betawi': self._count_matches(text_lower, BETAWI_PATTERNS),
            'melayu': self._count_matches(text_lower, MELAYU_PATTERNS)
        }
        
        # Cari skor tertinggi
        max_lang = max(scores, key=scores.get)
        max_score = scores[max_lang]
        
        # Kalau skor terlalu rendah, return indonesian
        if max_score < 2:
            return 'indonesian'
            
        logger.debug(f"Language detected: {max_lang} (score: {max_score})")
        return max_lang
    
    def _count_matches(self, text: str, patterns: Dict) -> int:
        """Count pattern matches for a language"""
        score = 0
        for category, words in patterns.items():
            for word in words:
                if word in text:
                    score += 1
        return score
    
    def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Detect language with confidence score
        Returns: (language_code, confidence)
        """
        if not text:
            return 'indonesian', 0.5
            
        text_lower = text.lower()
        
        # Check regional patterns
        for lang, patterns in [
            ('javanese', JAVANESE_PATTERNS),
            ('sundanese', SUNDANESE_PATTERNS),
            ('betawi', BETAWI_PATTERNS),
            ('melayu', MELAYU_PATTERNS)
        ]:
            matches = self._count_matches(text_lower, patterns)
            if matches >= 2:
                confidence = min(0.9, 0.5 + (matches * 0.1))
                return lang, confidence
                
        return 'indonesian', 0.7
    
    def translate_regional(self, text: str, source_lang: str) -> str:
        """
        Translate from regional language to Indonesian
        """
        if source_lang not in REGIONAL_DICT:
            return text
            
        translated = text
        word_dict = REGIONAL_DICT[source_lang]
        
        # Replace known words/phrases
        for regional, indonesian in word_dict.items():
            pattern = re.compile(re.escape(regional), re.IGNORECASE)
            translated = pattern.sub(indonesian, translated)
            
        return translated
    
    def enhance_prompt(self, prompt: str, detected_lang: str = None) -> str:
        """
        Enhance prompt with language context for AI
        """
        if detected_lang is None:
            detected_lang = self.detect(prompt)
            
        if detected_lang == 'indonesian':
            return prompt
            
        # Add language context prefix
        lang_prefixes = {
            'javanese': "[User menggunakan Bahasa Jawa] ",
            'sundanese': "[User menggunakan Bahasa Sunda] ",
            'betawi': "[User menggunakan Bahasa Betawi] ",
            'melayu': "[User menggunakan Bahasa Melayu] "
        }
        
        prefix = lang_prefixes.get(detected_lang, "")
        return prefix + prompt
    
    def get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name"""
        names = {
            'indonesian': 'Bahasa Indonesia',
            'javanese': 'Bahasa Jawa',
            'sundanese': 'Bahasa Sunda',
            'betawi': 'Bahasa Betawi',
            'melayu': 'Bahasa Melayu'
        }
        return names.get(lang_code, lang_code)


# Global instance
detector = LanguageDetector()

# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

def detect_language(text: str) -> str:
    """Backward compatibility function"""
    return detector.detect(text)

def enhance_prompt_with_language(prompt: str, detected_lang: str = None) -> str:
    """Backward compatibility function"""
    return detector.enhance_prompt(prompt, detected_lang)

def translate_regional(text: str, source_lang: str) -> str:
    """Backward compatibility function"""
    return detector.translate_regional(text, source_lang)
