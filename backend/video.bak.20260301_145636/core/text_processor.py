import streamlit as st
import re

class TextProcessor:
    def __init__(self):
        pass

    def create_punctuation_aware_karaoke(self, text, total_duration):
        """
        Create punctuation-aware karaoke timing with punctuation handling
        Returns list of words with start/end times and punctuation info
        """
        try:
            if not text or not isinstance(text, str):
                st.warning("⚠️ Teks kosong atau tidak valid")
                return []

            # Split text into words
            words = text.split()
            if not words:
                st.warning("⚠️ Tidak ada kata yang dapat diproses")
                return []

            # Calculate duration per word
            total_words = len(words)
            word_duration = total_duration / total_words if total_words > 0 else total_duration
            timings = []
            current_time = 0.0

            for word in words:
                # Detect punctuation
                punctuation_match = re.search(r'[.!?]', word)
                has_punctuation = bool(punctuation_match)
                punctuation = punctuation_match.group(0) if punctuation_match else ''
                clean_word = re.sub(r'[.!?]', '', word)  # Remove punctuation from word

                end_time = min(current_time + word_duration, total_duration)

                timings.append({
                    'text': clean_word,
                    'start_time': current_time,
                    'end_time': end_time,
                    'has_punctuation': has_punctuation,
                    'punctuation': punctuation
                })

                current_time = end_time

            st.info(f"✅ Generated {len(timings)} karaoke segments with punctuation handling")
            return timings

        except Exception as e:
            st.error(f"❌ Failed to create karaoke timings: {str(e)}")
            return []

    def create_word_by_word_karaoke(self, text, total_duration):
        """
        Create word-by-word karaoke timing
        Returns list of words with start and end times
        """
        words = text.split()
        total_words = len(words)

        if total_words == 0:
            return []

        word_duration = total_duration / total_words
        timings = []

        for i, word in enumerate(words):
            start_time = i * word_duration
            end_time = (i + 1) * word_duration

            timings.append({
                'text': word,
                'start_time': start_time,
                'end_time': end_time,
                'is_current': True
            })

        return timings

    def create_progressive_karaoke(self, text, total_duration):
        """
        Create progressive karaoke - show all words up to current position
        Returns list of progressive text segments
        """
        words = text.split()
        total_words = len(words)

        if total_words == 0:
            return []

        word_duration = total_duration / total_words
        segments = []

        for i in range(total_words):
            start_time = i * word_duration
            end_time = (i + 1) * word_duration

            # Progressive text: all words up to current position
            current_text = ' '.join(words[:i+1])

            segments.append({
                'text': current_text,
                'start_time': start_time,
                'end_time': end_time,
                'current_word': words[i],
                'word_index': i
            })

        return segments

    def optimize_for_display(self, text, max_line_length=25):
        """Optimize text for display by splitting into lines"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) <= max_line_length:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

# Singleton instance
text_processor = TextProcessor()
