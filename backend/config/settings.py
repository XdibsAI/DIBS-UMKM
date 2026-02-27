"""Configuration and Settings"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8081
    host: str = "0.0.0.0"
    db_path: str = "~/dibs1/dibs1.db"  # Pakai ~, nanti diexpand

    # Ollama (fallback)
    ollama_url: str = "http://127.0.0.1:11434"
    ai_model: str = "llama3.2:3b"
    ai_model_fallback: str = "llama3.2:1b"
    ollama_timeout: int = 180
    ollama_num_predict: int = 512
    ollama_temperature: float = 0.7

    # NVIDIA API (Kimi K2.5)
    use_nvidia: bool = False
    nvidia_api_key: str = ""
    nvidia_model: str = "nvidia/nemotron-3-nano-30b-a3b"
    nvidia_max_tokens: int = 16384
    nvidia_temperature: float = 1.0
    nvidia_thinking: bool = True

    # Other
    max_file_size: int = 104857600
    jwt_secret_key: str = "dibs-secret-key"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Expand ~ in db_path
        if self.db_path.startswith('~'):
            self.db_path = str(Path(self.db_path).expanduser())
            print(f"📁 DB Path expanded to: {self.db_path}")

settings = Settings()
