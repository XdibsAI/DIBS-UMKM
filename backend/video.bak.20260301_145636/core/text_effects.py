"""
Text Effects for Video
"""
import logging

logger = logging.getLogger(__name__)

class TextEffects:
    """Apply text effects for video subtitles"""
    
    @staticmethod
    def apply_fade_in(text: str, duration: float = 1.0) -> dict:
        """Apply fade-in effect"""
        return {
            'text': text,
            'effect': 'fade_in',
            'duration': duration
        }
    
    @staticmethod
    def apply_typing(text: str, speed: float = 0.1) -> dict:
        """Apply typing effect"""
        return {
            'text': text,
            'effect': 'typing',
            'speed': speed
        }
    
    @staticmethod
    def apply_highlight(text: str, color: str = 'yellow') -> dict:
        """Apply highlight effect"""
        return {
            'text': text,
            'effect': 'highlight',
            'color': color
        }


# Global instance
text_effects = TextEffects()
