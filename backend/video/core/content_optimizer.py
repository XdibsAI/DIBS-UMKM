"""
Content Optimizer - No Streamlit
"""
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """Optimize content for videos"""
    
    def __init__(self):
        self.max_length = 500
        
    def optimize_script(self, script: str, max_length: int = 500) -> str:
        """Optimize script for video"""
        if len(script) <= max_length:
            return script
            
        # Potong jadi paragraf pendek
        sentences = re.split(r'[.!?]', script)
        result = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if current_length + len(sentence) <= max_length:
                result.append(sentence)
                current_length += len(sentence)
            else:
                break
                
        return '. '.join(result) + '.'
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan'}
        
        word_count = {}
        for word in words:
            if len(word) > 3 and word not in stopwords:
                word_count[word] = word_count.get(word, 0) + 1
                
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]
    
    def suggest_hashtags(self, keywords: List[str]) -> List[str]:
        """Suggest hashtags from keywords"""
        return [f"#{keyword}" for keyword in keywords]


content_optimizer = ContentOptimizer()
