import requests
from config.logging import logger

class KimiAI:
    def __init__(self, api_key: str, model: str = "moonshotai/kimi-k2.5"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        logger.info(f"✅ Kimi AI initialized with model: {model}")
    
    async def generate(self, prompt: str, session_id: str = None, context: list = None, system_prompt: str = None):
        """Generate response using Kimi AI"""
        
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context
        if context:
            messages.extend(context)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 16384,
            "temperature": 0.7,
            "top_p": 1.0,
            "stream": False,
            "chat_template_kwargs": {"thinking": True}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            result = response.json()
            
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Kimi error: {result}")
                return "Maaf, terjadi error pada Kimi AI."
                
        except Exception as e:
            logger.error(f"Kimi exception: {e}")
            raise
