"""
VOICE CHAT API ENDPOINTS
Handles voice conversations using modular AI providers
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
import json
import io

from app.services.ai_provider_service import UnifiedAIService
from app.core.ai_config import get_current_provider


router = APIRouter()


@router.get("/provider")
async def get_provider_info():
    """
    Get information about current AI provider

    Returns which provider is active (Local or OpenAI)
    """
    ai_service = UnifiedAIService()

    return {
        "provider": get_current_provider().value,
        "provider_name": ai_service.get_current_provider_name(),
        "status": "active"
    }


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
):
    """
    Transcribe audio to text using Whisper

    Args:
        audio: Audio file (m4a, mp3, wav, etc.)

    Returns:
        {"text": "transcribed text"}
    """
    ai_service = UnifiedAIService()

    try:
        # Read audio file
        audio_bytes = await audio.read()

        # Transcribe
        text = await ai_service.speech_to_text(audio_bytes)

        return {
            "text": text,
            "provider": get_current_provider().value
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    voice: Optional[str] = Form(None),
):
    """
    Convert text to speech audio

    Args:
        text: Text to convert
        voice: Voice ID (optional)

    Returns:
        Audio file (WAV format)
    """
    ai_service = UnifiedAIService()

    try:
        # Generate audio
        audio_bytes = await ai_service.text_to_speech(text, voice)

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(
    message: str = Form(...),
    conversation_history: Optional[str] = Form(None),  # JSON string
    system_prompt: Optional[str] = Form(None),
):
    """
    Simple text chat

    Args:
        message: User's message
        conversation_history: JSON string of previous messages (optional)
        system_prompt: System instructions (optional)

    Returns:
        {"response": "AI response text"}
    """
    ai_service = UnifiedAIService()

    try:
        # Parse conversation history
        history = []
        if conversation_history:
            history = json.loads(conversation_history)

        # Generate response
        response = await ai_service.chat(
            user_message=message,
            conversation_history=history,
            system_prompt=system_prompt,
        )

        return {
            "response": response,
            "provider": get_current_provider().value
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    conversation_history: Optional[str] = Form(None),  # JSON string
    system_prompt: Optional[str] = Form(None),
    return_audio: bool = Form(True),
):
    """
    COMPLETE VOICE CONVERSATION
    User speaks → Whisper → LLM → TTS → Audio response

    This is the main endpoint you'll use!

    Args:
        audio: User's audio recording
        conversation_history: JSON string of previous messages
        system_prompt: System instructions (e.g., age-appropriate personality)
        return_audio: Whether to return audio response (default: True)

    Returns:
        {
            "user_text": "what user said",
            "ai_text": "AI response",
            "ai_audio_url": "/path/to/audio" (if return_audio=True)
        }
    """
    ai_service = UnifiedAIService()

    try:
        # Read audio
        audio_bytes = await audio.read()

        # Parse conversation history
        history = []
        if conversation_history:
            history = json.loads(conversation_history)

        # Process voice conversation
        result = await ai_service.voice_conversation(
            audio_bytes=audio_bytes,
            conversation_history=history,
            system_prompt=system_prompt,
            return_audio=return_audio,
        )

        response_data = {
            "user_text": result["user_text"],
            "ai_text": result["ai_text"],
            "provider": get_current_provider().value,
        }

        # If audio was generated, return it as base64
        if return_audio and "ai_audio" in result:
            import base64
            audio_base64 = base64.b64encode(result["ai_audio"]).decode('utf-8')
            response_data["ai_audio"] = audio_base64

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-flow")
async def test_voice_flow(
    test_text: str = Form("Hello! I want to learn art."),
):
    """
    Test the complete voice flow with text input (for debugging)

    Args:
        test_text: Test text to simulate user speech

    Returns:
        Complete flow result
    """
    ai_service = UnifiedAIService()

    try:
        # Simulate chat
        ai_response = await ai_service.chat(
            user_message=test_text,
            system_prompt="You are Sooshi, a friendly AI learning assistant."
        )

        # Generate audio
        audio_bytes = await ai_service.text_to_speech(ai_response)

        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return {
            "user_text": test_text,
            "ai_text": ai_response,
            "ai_audio": audio_base64,
            "provider": ai_service.get_current_provider_name(),
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
