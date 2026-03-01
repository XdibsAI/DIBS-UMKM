"""
DIBS Language Intelligence Module
Multilingual understanding untuk bahasa-bahasa Indonesia
"""

import re
import json
from typing import Dict, Tuple, Optional
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

class LanguageIntelligence:
    def __init__(self):
        # Using deep-translator for better stability
        
        # Dictionary bahasa daerah Indonesia yang umum
        self.regional_dict = {
            # Bahasa Jawa
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
            # Bahasa Sunda
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
            # Bahasa Melayu
            'melayu': {
                'apa khabar': 'apa kabar',
                'terima kasih': 'terima kasih',
                'sila': 'silakan',
                'betul': 'benar',
                'salah': 'salah',
                'hendak': 'mau',
                'boleh': 'bisa',
            },
            # Bahasa Betawi
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
        
        # Patterns untuk deteksi bahasa regional
        self.regional_patterns = {
            'jawa': ['nggih', 'sampun', 'dereng', 'pundi', 'menapa'],
            'sunda': ['hatur', 'kumaha', 'naon', 'sabaraha', 'punten'],
            'melayu': ['khabar', 'hendak', 'betul'],
            'betawi': ['kagak', 'kaga', 'ape'],
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Deteksi bahasa dari text
        Returns: (language_code, confidence)
        """
        text_lower = text.lower()
        
        # Check regional language patterns first
        for lang, patterns in self.regional_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            if matches >= 2:  # Minimal 2 matches
                confidence = min(0.9, 0.5 + (matches * 0.1))
                logger.info(f"Detected regional language: {lang} (confidence: {confidence})")
                return lang, confidence
        
        # Fallback to langdetect
        try:
            detected = detect(text)
            return detected, 0.7
        except LangDetectException:
            return 'id', 0.5  # Default to Indonesian
    
    def translate_regional(self, text: str, source_lang: str) -> str:
        """Translate dari bahasa daerah ke Bahasa Indonesia"""
        if source_lang not in self.regional_dict:
            return text
        
        translated = text
        word_dict = self.regional_dict[source_lang]
        
        # Replace known words/phrases
        for regional, indonesian in word_dict.items():
            pattern = re.compile(re.escape(regional), re.IGNORECASE)
            translated = pattern.sub(indonesian, translated)
        
        return translated
    
    def smart_translate(self, text: str) -> Tuple[str, str, bool]:
        """
        Smart translation dengan language detection
        Returns: (translated_text, detected_language, was_translated)
        """
        # Detect language
        lang_code, confidence = self.detect_language(text)
        
        # If already Indonesian, return as-is
        if lang_code == 'id' and confidence > 0.6:
            return text, 'id', False
        
        # Try regional translation first
        if lang_code in self.regional_dict:
            translated = self.translate_regional(text, lang_code)
            if translated != text:
                logger.info(f"Regional translation ({lang_code}): {text[:50]} → {translated[:50]}")
                return translated, lang_code, True
        
        # Fallback to Google Translate for other languages
        try:
            if lang_code not in ['id', 'unknown']:
                translated = GoogleTranslator(source=lang_code, target='id').translate(text)
                class Result:
                    def __init__(self, t): self.text = t
                result = Result(translated)
                logger.info(f"Google Translate ({lang_code}→id): {text[:50]} → {result.text[:50]}")
                return result.text, lang_code, True
        except Exception as e:
            logger.error(f"Translation error: {e}")
        
        return text, lang_code, False
    
    def learn_phrase(self, original: str, translation: str, language: str) -> Dict:
        """
        Buat entry untuk disimpan ke knowledge sebagai pembelajaran bahasa
        """
        return {
            'original': original,
            'translation': translation,
            'language': language,
            'type': 'language_learning',
            'category': 'linguistic'
        }

# Global instance
language_ai = LanguageIntelligence()
