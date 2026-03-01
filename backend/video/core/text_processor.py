"""
Text Processor - No Streamlit
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TextProcessor:
    """Process text for videos"""
    
    def __init__(self):
        self.max_line_length = 50
        self.max_lines = 5
    
    def split_into_scenes(self, text: str, max_scenes: int = 5) -> List[str]:
        """Split text into scenes for video"""
        # Split by sentences
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Group into scenes
        scenes = []
        sentences_per_scene = max(1, len(sentences) // max_scenes)
        
        for i in range(0, len(sentences), sentences_per_scene):
            scene = '. '.join(sentences[i:i+sentences_per_scene])
            if scene:
                scenes.append(scene + '.')
                
        return scenes[:max_scenes]
    
    def format_for_subtitle(self, text: str, max_chars: int = 70) -> List[str]:
        """Format text for subtitles (line breaks)"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#(\w+)', text)
    
    def remove_hashtags(self, text: str) -> str:
        """Remove hashtags from text"""
        return re.sub(r'#\w+', '', text).strip()
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def estimate_reading_time(self, text: str, words_per_second: float = 3.0) -> float:
        """Estimate reading time in seconds"""
        return self.count_words(text) / words_per_second


text_processor = TextProcessor()
