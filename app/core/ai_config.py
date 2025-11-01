"""
AI PROVIDER CONFIGURATION
Switch between local (Ollama/Coqui) and cloud (OpenAI) providers
"""

from enum import Enum
from pydantic_settings import BaseSettings


class AIProvider(str, Enum):
    """AI service providers"""
    LOCAL = "local"      # Ollama + Coqui TTS (for testing)
    OPENAI = "openai"    # OpenAI GPT-4 + TTS (for production)


class AIProviderConfig(BaseSettings):
    """AI provider settings"""

    model_config = {"extra": "allow"}  # Allow extra env vars from shared .env file

    # MAIN SWITCH - Change this to switch providers!
    PROVIDER: AIProvider = AIProvider.LOCAL  # Change to "openai" for production

    # ========================================
    # LOCAL PROVIDERS (Ollama + Coqui TTS)
    # ========================================

    # Ollama LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"  # or "mistral", "phi3", etc.
    OLLAMA_TIMEOUT: int = 120

    # Coqui TTS
    COQUI_TTS_URL: str = "http://localhost:5002"
    COQUI_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    COQUI_VOCODER: str = "vocoder_models/en/ljspeech/hifigan_v2"

    # ========================================
    # CLOUD PROVIDERS (OpenAI)
    # ========================================

    # OpenAI GPT
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 500

    # OpenAI TTS
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "nova"  # alloy, echo, fable, onyx, nova, shimmer

    # ========================================
    # COMMON SETTINGS
    # ========================================

    # Whisper (keeping existing ngrok endpoint)
    WHISPER_API_URL: str = "https://cf4d52b914ef.ngrok-free.app/api/v1/whisper/transcribe"
    WHISPER_API_KEY: str = ""

    # Response settings
    MAX_RESPONSE_LENGTH: int = 500
    DEFAULT_TEMPERATURE: float = 0.7


# Global config instance
ai_config = AIProviderConfig()


def get_current_provider() -> AIProvider:
    """Get currently active AI provider"""
    return ai_config.PROVIDER


def is_using_local_provider() -> bool:
    """Check if using local (Ollama/Coqui) provider"""
    return ai_config.PROVIDER == AIProvider.LOCAL


def is_using_openai_provider() -> bool:
    """Check if using OpenAI provider"""
    return ai_config.PROVIDER == AIProvider.OPENAI
