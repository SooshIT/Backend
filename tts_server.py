"""
COQUI TTS SERVER
Simple Flask server for local text-to-speech
Run this: python tts_server.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from TTS.api import TTS
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native

# Initialize TTS model
logger.info("Loading TTS model...")
try:
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    logger.info("✅ TTS model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Failed to load TTS model: {e}")
    tts = None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok" if tts else "error",
        "model": "tacotron2-DDC" if tts else None,
        "message": "TTS server is running" if tts else "TTS model not loaded"
    })


@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech

    Request body:
    {
        "text": "Text to convert to speech"
    }

    Returns: WAV audio file
    """
    if not tts:
        return jsonify({"error": "TTS model not loaded"}), 500

    try:
        # Get text from request
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data['text']

        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400

        logger.info(f"Generating speech for: {text[:50]}...")

        # Generate speech
        # Note: tts_to_file expects a file path, so we use a temporary approach
        import tempfile
        import os

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Generate audio to temp file
            tts.tts_to_file(text=text, file_path=temp_path)

            # Read audio data
            with open(temp_path, 'rb') as f:
                audio_data = f.read()

            # Create in-memory buffer
            audio_buffer = io.BytesIO(audio_data)
            audio_buffer.seek(0)

            logger.info("✅ Speech generated successfully")

            return send_file(
                audio_buffer,
                mimetype='audio/wav',
                as_attachment=True,
                download_name='speech.wav'
            )

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"❌ TTS error: {str(e)}")
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500


@app.route('/models', methods=['GET'])
def list_models():
    """List available TTS models"""
    try:
        from TTS.utils.manage import ModelManager
        manager = ModelManager()
        models = manager.list_models()

        return jsonify({
            "models": models,
            "current_model": "tts_models/en/ljspeech/tacotron2-DDC"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "name": "Coqui TTS Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "tts": "/api/tts (POST)",
            "models": "/models",
        }
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎤 COQUI TTS SERVER")
    print("="*60)
    print(f"✅ Server starting on http://localhost:5002")
    print(f"✅ Model: tacotron2-DDC")
    print(f"✅ Health check: http://localhost:5002/health")
    print("\nTest with:")
    print('  curl -X POST http://localhost:5002/api/tts \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"text": "Hello from Soosh!"}\' \\')
    print('    --output test.wav')
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5002,
        debug=False,  # Set to True for development
        threaded=True
    )
