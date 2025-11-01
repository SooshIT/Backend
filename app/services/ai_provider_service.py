"""
AI PROVIDER SERVICE
Unified interface for local (Ollama/Coqui) and cloud (OpenAI) providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
import asyncio
from openai import AsyncOpenAI
import json

from app.core.ai_config import ai_config, AIProvider, is_using_local_provider


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class AIProviderInterface(ABC):
    """Abstract interface for AI providers"""

    @abstractmethod
    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate text response from messages"""
        pass

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """Generate speech audio from text"""
        pass

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_file: bytes
    ) -> str:
        """Transcribe audio to text (Whisper)"""
        pass


# ============================================================================
# LOCAL PROVIDER (Ollama + Coqui TTS)
# ============================================================================

class LocalAIProvider(AIProviderInterface):
    """Local AI provider using Ollama + Coqui TTS"""

    def __init__(self):
        self.ollama_url = ai_config.OLLAMA_BASE_URL
        self.ollama_model = ai_config.OLLAMA_MODEL
        self.coqui_url = ai_config.COQUI_TTS_URL
        self.whisper_url = ai_config.WHISPER_API_URL

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate text using Ollama"""

        # Convert messages to Ollama format
        prompt = self._messages_to_prompt(messages)

        async with httpx.AsyncClient(timeout=ai_config.OLLAMA_TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False,
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

            except httpx.HTTPError as e:
                raise Exception(f"Ollama API error: {str(e)}")

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """Generate speech using Coqui TTS"""

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.coqui_url}/api/tts",
                    json={
                        "text": text,
                        "model_name": ai_config.COQUI_MODEL,
                        "vocoder_name": ai_config.COQUI_VOCODER,
                    }
                )
                response.raise_for_status()
                return response.content  # WAV audio bytes

            except httpx.HTTPError as e:
                raise Exception(f"Coqui TTS error: {str(e)}")

    async def transcribe_audio(
        self,
        audio_file: bytes
    ) -> str:
        """Transcribe audio using Whisper API (existing endpoint)"""

        async with httpx.AsyncClient(timeout=30) as client:
            files = {"audio": ("audio.m4a", audio_file, "audio/m4a")}

            response = await client.post(
                self.whisper_url,
                files=files,
                headers={"Authorization": f"Bearer {ai_config.WHISPER_API_KEY}"} if ai_config.WHISPER_API_KEY else {}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt for Ollama"""

        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")

        prompt_parts.append("Assistant:")  # Prompt for response
        return "\n".join(prompt_parts)


# ============================================================================
# CLOUD PROVIDER (OpenAI)
# ============================================================================

class OpenAIProvider(AIProviderInterface):
    """OpenAI provider using GPT-4 + TTS"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=ai_config.OPENAI_API_KEY)
        self.whisper_url = ai_config.WHISPER_API_URL

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate text using OpenAI GPT-4"""

        try:
            response = await self.client.chat.completions.create(
                model=ai_config.OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """Generate speech using OpenAI TTS"""

        try:
            response = await self.client.audio.speech.create(
                model=ai_config.OPENAI_TTS_MODEL,
                voice=voice or ai_config.OPENAI_TTS_VOICE,
                input=text,
            )
            return response.content

        except Exception as e:
            raise Exception(f"OpenAI TTS error: {str(e)}")

    async def transcribe_audio(
        self,
        audio_file: bytes
    ) -> str:
        """Transcribe audio using Whisper API (existing endpoint)"""
        # Same as local provider - uses your existing ngrok endpoint
        async with httpx.AsyncClient(timeout=30) as client:
            files = {"audio": ("audio.m4a", audio_file, "audio/m4a")}

            response = await client.post(
                self.whisper_url,
                files=files,
                headers={"Authorization": f"Bearer {ai_config.WHISPER_API_KEY}"} if ai_config.WHISPER_API_KEY else {}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")


# ============================================================================
# FACTORY & MAIN SERVICE
# ============================================================================

def get_ai_provider() -> AIProviderInterface:
    """
    Factory function to get the appropriate AI provider based on config

    This is the ONLY function you need to call!
    It automatically returns the right provider based on PROVIDER setting.
    """
    if is_using_local_provider():
        return LocalAIProvider()
    else:
        return OpenAIProvider()


class UnifiedAIService:
    """
    Main AI service that works with both local and cloud providers

    Usage:
        ai_service = UnifiedAIService()
        response = await ai_service.chat("Hello!")
        audio = await ai_service.text_to_speech("Hello!")
        text = await ai_service.speech_to_text(audio_bytes)
    """

    def __init__(self):
        self.provider = get_ai_provider()

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Simple chat interface

        Args:
            user_message: User's message
            conversation_history: Previous messages (optional)
            system_prompt: System instructions (optional)
            temperature: Response randomness (0-1)

        Returns:
            AI response text
        """
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response
        response = await self.provider.generate_text(
            messages=messages,
            temperature=temperature,
            max_tokens=ai_config.MAX_RESPONSE_LENGTH,
        )

        return response

    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech audio

        Args:
            text: Text to convert
            voice: Voice ID (optional, provider-specific)

        Returns:
            Audio bytes (WAV format)
        """
        return await self.provider.generate_speech(text, voice)

    async def speech_to_text(
        self,
        audio_bytes: bytes
    ) -> str:
        """
        Convert speech audio to text

        Args:
            audio_bytes: Audio file bytes

        Returns:
            Transcribed text
        """
        return await self.provider.transcribe_audio(audio_bytes)

    async def voice_conversation(
        self,
        audio_bytes: bytes,
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None,
        return_audio: bool = True,
    ) -> Dict:
        """
        Complete voice conversation flow:
        1. Transcribe user's audio to text
        2. Generate AI response text
        3. Convert AI response to speech audio

        Args:
            audio_bytes: User's audio recording
            conversation_history: Previous conversation
            system_prompt: System instructions
            return_audio: Whether to return audio response

        Returns:
            {
                "user_text": "transcribed user message",
                "ai_text": "AI response text",
                "ai_audio": bytes (if return_audio=True)
            }
        """
        # Step 1: Speech to text
        user_text = await self.speech_to_text(audio_bytes)

        # Step 2: Generate AI response
        ai_text = await self.chat(
            user_message=user_text,
            conversation_history=conversation_history,
            system_prompt=system_prompt,
        )

        result = {
            "user_text": user_text,
            "ai_text": ai_text,
        }

        # Step 3: Text to speech (if requested)
        if return_audio:
            ai_audio = await self.text_to_speech(ai_text)
            result["ai_audio"] = ai_audio

        return result

    def get_current_provider_name(self) -> str:
        """Get name of current provider"""
        return "Local (Ollama + Coqui TTS)" if is_using_local_provider() else "OpenAI (GPT-4 + TTS)"
