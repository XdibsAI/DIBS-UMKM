"""
Text Effects for Video - No Streamlit
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TextEffects:
    """Apply text effects for video subtitles"""
    
    @staticmethod
    def apply_fade_in(text: str, duration: float = 1.0) -> Dict[str, Any]:
        """Apply fade-in effect"""
        return {
            'text': text,
            'effect': 'fade_in',
            'duration': duration,
            'css': f'animation: fadeIn {duration}s;'
        }
    
    @staticmethod
    def apply_fade_out(text: str, duration: float = 1.0) -> Dict[str, Any]:
        """Apply fade-out effect"""
        return {
            'text': text,
            'effect': 'fade_out',
            'duration': duration,
            'css': f'animation: fadeOut {duration}s;'
        }
    
    @staticmethod
    def apply_slide_in(text: str, direction: str = 'left', duration: float = 1.0) -> Dict[str, Any]:
        """Apply slide-in effect"""
        return {
            'text': text,
            'effect': f'slide_in_{direction}',
            'duration': duration,
            'css': f'animation: slideIn{direction.title()} {duration}s;'
        }
    
    @staticmethod
    def apply_typing(text: str, speed: float = 0.1) -> Dict[str, Any]:
        """Apply typing effect"""
        return {
            'text': text,
            'effect': 'typing',
            'speed': speed,
            'css': 'overflow: hidden; white-space: nowrap; animation: typing 3s steps(40, end);'
        }
    
    @staticmethod
    def apply_highlight(text: str, color: str = 'yellow') -> Dict[str, Any]:
        """Apply highlight effect"""
        return {
            'text': text,
            'effect': 'highlight',
            'color': color,
            'css': f'background-color: {color}; padding: 2px;'
        }
    
    def get_available_effects(self) -> List[str]:
        """Get list of available effects"""
        return ['fade_in', 'fade_out', 'slide_in_left', 'slide_in_right', 
                'typing', 'highlight', 'bounce', 'pulse']


text_effects = TextEffects()
