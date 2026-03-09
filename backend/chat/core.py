"""Chat AI Core - Multi Provider (Nemotron, Kimi, Ollama)"""

import logging
import time
from typing import Dict, List, Optional

import httpx
from openai import OpenAI

from chat.kimi_ai import KimiAI
from config.settings import (
    ai_model,
    kimi_model,
    nvidia_api_key,
    ollama_timeout,
    ollama_url,
    use_kimi,
    use_nvidia,
)

logger = logging.getLogger("DIBS1")


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

BASE_SYSTEM_PROMPT = """CRITICAL IDENTITY RULES:
1. You are DIBS AI (Digital Intelligent Business System)
2. Your name is DIBS - NEVER say you are other AI models (Nemotron, Llama, etc.)
3. ALWAYS introduce yourself as DIBS when asked about identity
4. Created to help Indonesian UMKM businesses
5. Help debug coder in dibs1

YOUR IDENTITY:
- Name: DIBS
- Purpose: Helping Indonesian small businesses
- Language: Use the SAME language as the user (Indonesian, English, Javanese, Sundanese, etc.)
- Address: Use "Kak" for Indonesian, or appropriate local terms (Mas/Mbak) based on context

CONVERSATION RULES:
- Greet with "Halo Kak" or equivalent ONLY in the FIRST message of a conversation
- For follow-up messages, DO NOT repeat greetings - just answer directly
- Be concise, helpful, and friendly
- If user speaks in mixed languages, respond in the dominant language

EXAMPLE 1 (First message):
User: "Halo"
DIBS: "Halo Kak! Ada yang bisa saya bantu?"

EXAMPLE 2 (Follow-up):
User: "Apa itu DIBS?"
DIBS: "DIBS adalah Digital Intelligent Business System untuk membantu UMKM Indonesia..."

Keep responses under 200 words, be helpful & friendly.
"""


# ============================================================================
# LANGUAGE DETECTOR
# ============================================================================

class LanguageDetector:
    """Deteksi bahasa sederhana."""

    JAVA_KEYWORDS = [
        "piye", "opo", "ning", "wis", "durung",
        "saiki", "kowe", "aku", "mbak", "mas"
    ]
    SUNDA_KEYWORDS = [
        "kumaha", "naon", "saha", "iraha",
        "abdi", "anjeun"
    ]

    @staticmethod
    def detect(text: str) -> str:
        text_lower = (text or "").lower()

        java_score = sum(1 for word in LanguageDetector.JAVA_KEYWORDS if word in text_lower)
        sunda_score = sum(1 for word in LanguageDetector.SUNDA_KEYWORDS if word in text_lower)

        if java_score > sunda_score and java_score > 0:
            return "jawa"
        if sunda_score > java_score and sunda_score > 0:
            return "sunda"
        return "indonesia"


# ============================================================================
# BASE PROVIDER
# ============================================================================

class BaseProvider:
    """Base class untuk session-aware greeting logic."""

    def __init__(self):
        self.conversation_history: Dict[str, int] = {}

    def is_first_message(self, session_id: Optional[str]) -> bool:
        if not session_id:
            return False

        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = 1
            return True

        self.conversation_history[session_id] += 1
        return False

    def build_system_prompt(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        language = LanguageDetector.detect(prompt)
        final_system = system_prompt or BASE_SYSTEM_PROMPT

        if self.is_first_message(session_id):
            final_system += "\n\nThis is the FIRST message in conversation. You may greet the user."
        else:
            final_system += "\n\nThis is a FOLLOW-UP message. DO NOT repeat greetings. Answer directly."

        final_system += f"\n\nUser is speaking in {language.upper()} language. Respond in the SAME language."
        return final_system


# ============================================================================
# NEMOTRON PROVIDER
# ============================================================================

class NemotronAI(BaseProvider):
    """Nemotron via NVIDIA API using OpenAI SDK."""

    def __init__(self):
        super().__init__()
        self.api_key = nvidia_api_key
        self.model = "nvidia/nemotron-3-nano-30b-a3b"

        if not self.api_key:
            self.client = None
            logger.warning("⚠️ NVIDIA API key not configured")
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://integrate.api.nvidia.com/v1",
            )
            logger.info("✅ Nemotron initialized")

    async def generate(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        if not self.client:
            raise RuntimeError("Nemotron client not available")

        final_system = self.build_system_prompt(prompt, session_id, system_prompt)
        language = LanguageDetector.detect(prompt)

        messages = [{"role": "system", "content": final_system}]
        if context:
            messages.extend(context[-8:])
        messages.append({"role": "user", "content": prompt})

        logger.info(f"📝 Using Nemotron with {language.upper()}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2048,
            temperature=0.8,
            timeout=60.0,
        )

        content = response.choices[0].message.content
        logger.info(f"✅ Nemotron response ({len(content)} chars)")
        return content


# ============================================================================
# OLLAMA PROVIDER
# ============================================================================

class OllamaAI(BaseProvider):
    """Ollama local provider."""

    def __init__(self):
        super().__init__()
        self.url = ollama_url
        self.model = ai_model
        self.timeout = ollama_timeout

    async def generate(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        final_system = self.build_system_prompt(prompt, session_id, system_prompt)
        language = LanguageDetector.detect(prompt)

        messages = [{"role": "system", "content": final_system}]
        if context:
            messages.extend(context[-8:])
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 512,
                        "temperature": 0.7,
                        "num_ctx": 4096,
                    },
                },
            )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama error: {response.status_code}")

        content = response.json()["message"]["content"]
        logger.info(f"✅ Ollama response ({language})")
        return content


# ============================================================================
# MAIN AI ROUTER
# ============================================================================

class AIProvider:
    """Smart AI provider with clear fallback chain."""

    def __init__(self):
        self.nemotron = NemotronAI() if nvidia_api_key else None
        self.kimi = KimiAI(nvidia_api_key, kimi_model) if (use_kimi and nvidia_api_key) else None
        self.ollama = OllamaAI()

        self.enable_nvidia = use_nvidia and bool(nvidia_api_key)
        self.enable_kimi = use_kimi and bool(nvidia_api_key)

    async def _generate_with_kimi(
        self,
        prompt: str,
        session_id: Optional[str],
        context: Optional[List[Dict]],
        system_prompt: Optional[str],
    ) -> str:
        if not self.kimi:
            raise RuntimeError("Kimi provider not available")
        return await self.kimi.generate(prompt, session_id, context, system_prompt)

    async def _generate_with_nemotron(
        self,
        prompt: str,
        session_id: Optional[str],
        context: Optional[List[Dict]],
        system_prompt: Optional[str],
    ) -> str:
        if not self.nemotron:
            raise RuntimeError("Nemotron provider not available")
        return await self.nemotron.generate(prompt, session_id, context, system_prompt)

    async def _generate_with_ollama(
        self,
        prompt: str,
        session_id: Optional[str],
        context: Optional[List[Dict]],
        system_prompt: Optional[str],
    ) -> str:
        return await self.ollama.generate(prompt, session_id, context, system_prompt)

    async def generate(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        use_nvidia_override: Optional[bool] = None,
    ) -> str:
        start = time.time()
        language = LanguageDetector.detect(prompt)

        use_remote = self.enable_nvidia if use_nvidia_override is None else use_nvidia_override

        try:
            if use_remote and self.enable_kimi and self.kimi:
                logger.info(f"🤖 Using Kimi ({language})")
                result = await self._generate_with_kimi(
                    prompt, session_id, context, system_prompt
                )
                logger.info(f"⏱️ {time.time() - start:.1f}s (Kimi)")
                return result

            if use_remote and self.nemotron:
                logger.info(f"🤖 Using Nemotron ({language})")
                result = await self._generate_with_nemotron(
                    prompt, session_id, context, system_prompt
                )
                logger.info(f"⏱️ {time.time() - start:.1f}s (Nemotron)")
                return result

            logger.info(f"🔄 Using Ollama ({language})")
            result = await self._generate_with_ollama(
                prompt, session_id, context, system_prompt
            )
            logger.info(f"⏱️ {time.time() - start:.1f}s (Ollama)")
            return result

        except Exception as e:
            logger.error(f"❌ Primary provider failed: {e}")

            # fallback terakhir ke Ollama
            try:
                logger.info("🔄 Fallback to Ollama...")
                result = await self._generate_with_ollama(
                    prompt, session_id, context, system_prompt
                )
                logger.info(f"⏱️ {time.time() - start:.1f}s (Ollama fallback)")
                return result
            except Exception as fallback_error:
                logger.error(f"❌ Fallback Ollama failed: {fallback_error}")

            error_msgs = {
                "jawa": "Maaf Mas/Mbak, lagi error. Coba maneh ya?",
                "sunda": "Hapunten, aya gangguan. Coba deui mang?",
                "indonesia": "Maaf Kak, sistem sedang gangguan. Coba lagi ya?",
            }
            return error_msgs.get(language, "Maaf Kak, sistem sedang gangguan. Coba lagi ya?")


# Global instance
ai_provider = AIProvider()

# Backward compatibility alias
ollama_ai = ai_provider
