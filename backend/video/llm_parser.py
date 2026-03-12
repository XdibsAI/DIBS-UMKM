"""
LLM Parser for Video Prompts
Uses AIProvider (Nemotron -> Kimi -> Ollama fallback)
Does NOT interfere with toko/kasir system
"""

import json
import logging
from typing import Optional, Dict, Any, List

from chat.core import ollama_ai  # This is actually AIProvider instance

logger = logging.getLogger(__name__)

# System prompt khusus untuk parse video
VIDEO_SYSTEM_PROMPT = """You are a video script parser for DIBS AI.
Your ONLY job is to convert user's video prompt into valid JSON.
Do NOT add explanations, comments, or markdown.
Output RAW JSON only."""

# Template untuk prompt ke LLM
VIDEO_PROMPT_TEMPLATE = """
Convert this video script to JSON format.

USER PROMPT:
{user_prompt}

INSTRUCTIONS:
1. Identify scenes (3-5 scenes typical)
2. Each scene MUST have:
   - kind: type of scene (hook, problem, product, benefit, offer, cta, tutorial, transformation, climax)
   - title: short title (max 50 chars)
   - text: narration text (max 200 chars)
   - caption: very short text for display (max 30 chars)
   - visual: visual description (optional)
   - duration: seconds per scene (2-6 seconds)

3. Output ONLY this JSON structure with NO additional text:
{{
  "scenes": [
    {{
      "kind": "hook",
      "title": "Attention Grabber",
      "text": "Narration for this scene",
      "caption": "Short display text",
      "visual": "Visual description (if any)",
      "duration": 5
    }}
  ]
}}

VALID KINDS: hook, problem, product, benefit, offer, cta, tutorial, transformation, climax, motivation, education

EXAMPLE 1:
Input: "Scene 1 - Hook: Kenapa bola mengambang? Narasi: Gaya menarik air membuat bola ringan."
Output:
{{
  "scenes": [
    {{
      "kind": "hook",
      "title": "Mengapa Bola Mengambang?",
      "text": "Bola kecil bisa mengambang karena gaya menarik air.",
      "caption": "Gaya menarik",
      "visual": "Teks pertanyaan di layar",
      "duration": 5
    }}
  ]
}}

EXAMPLE 2:
Input: "Video edukasi 15 detik: 1. Hook pertanyaan, 2. Penjelasan singkat, 3. Demo"
Output:
{{
  "scenes": [
    {{
      "kind": "hook",
      "title": "Tahukah Kamu?",
      "text": "Fenomena ini terjadi karena gaya tarik air.",
      "caption": "Tahukah kamu?",
      "visual": "Teks pertanyaan",
      "duration": 4
    }},
    {{
      "kind": "education",
      "title": "Penjelasan",
      "text": "Air menarik benda ringan ke permukaan.",
      "caption": "Penjelasan",
      "visual": "Animasi bola di air",
      "duration": 6
    }},
    {{
      "kind": "cta",
      "title": "Coba Sendiri",
      "text": "Praktikkan di rumah dengan bola pingpong.",
      "caption": "Coba sendiri",
      "visual": "Demo mangkuk air",
      "duration": 5
    }}
  ]
}}

Now parse the user prompt above.
"""


async def parse_prompt_with_llm(user_prompt: str) -> Optional[Dict[str, Any]]:
    """
    Parse user prompt using AIProvider (Nemotron -> Kimi -> Ollama)
    Returns dict with 'scenes' list or None if failed
    """
    if not user_prompt or len(user_prompt.strip()) < 10:
        logger.warning("Prompt too short for LLM parsing")
        return None

    # Build full prompt
    full_prompt = VIDEO_PROMPT_TEMPLATE.format(user_prompt=user_prompt.strip())
    
    try:
        logger.info("🎬 Calling LLM to parse video prompt...")
        
        # Panggil AIProvider (otomatis: Nemotron -> fallback)
        response = await ollama_ai.generate(
            prompt=full_prompt,
            system_prompt=VIDEO_SYSTEM_PROMPT,
            session_id="video_parser"  # Optional, for context
        )
        
        if not response:
            logger.warning("Empty response from LLM")
            return None
            
        # Clean response - remove markdown code blocks if present
        cleaned = response.strip()
        
        # Handle ```json blocks
        if "```json" in cleaned:
            parts = cleaned.split("```json")
            if len(parts) > 1:
                cleaned = parts[1].split("```")[0].strip()
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) > 1:
                cleaned = parts[1].split("```")[0].strip()
        
        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', cleaned, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise
        
        # Validate structure
        if not isinstance(data, dict):
            logger.warning(f"LLM response not a dict: {type(data)}")
            return None
            
        if "scenes" not in data:
            # Maybe it's a list directly?
            if isinstance(data, list):
                return {"scenes": data}
            logger.warning("No 'scenes' key in LLM response")
            return None
            
        scenes = data["scenes"]
        if not isinstance(scenes, list) or len(scenes) == 0:
            logger.warning("Invalid scenes data from LLM")
            return None
            
        # Validate each scene has required fields
        validated_scenes = []
        required_fields = ["kind", "title", "text", "caption"]
        
        for i, scene in enumerate(scenes):
            if not isinstance(scene, dict):
                continue
                
            # Ensure required fields exist
            valid_scene = {}
            for field in required_fields:
                valid_scene[field] = str(scene.get(field, "")).strip()
            
            # Optional fields
            valid_scene["visual"] = str(scene.get("visual", "")).strip()
            valid_scene["duration"] = int(scene.get("duration", 4))
            
            # Ensure kind is valid (or default)
            kind = valid_scene["kind"].lower()
            valid_kinds = ["hook", "problem", "product", "benefit", "offer", 
                          "cta", "tutorial", "transformation", "climax", 
                          "motivation", "education", "solution"]
            
            if kind not in valid_kinds:
                # Map common terms
                if "tanya" in kind or "hook" in kind:
                    kind = "hook"
                elif "ajar" in kind or "tutorial" in kind:
                    kind = "tutorial"
                elif "demo" in kind:
                    kind = "product"
                else:
                    kind = "scene"
            
            valid_scene["kind"] = kind
            
            # Ensure duration is reasonable
            valid_scene["duration"] = max(2, min(8, valid_scene["duration"]))
            
            validated_scenes.append(valid_scene)
        
        if not validated_scenes:
            logger.warning("No valid scenes after validation")
            return None
            
        logger.info(f"✅ LLM parsed {len(validated_scenes)} scenes")
        return {"scenes": validated_scenes}
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from LLM: {e}")
        logger.debug(f"Raw response: {response[:500]}")
        return None
    except Exception as e:
        logger.error(f"LLM parsing error: {e}")
        return None


async def enhance_with_llm(scenes: List[Dict]) -> List[Dict]:
    """
    Optional: Use LLM to enhance existing scenes with better titles/captions
    Not implemented yet - for future use
    """
    return scenes
