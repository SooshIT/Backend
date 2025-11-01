# Voice Chat Setup Guide

## Current Status: ✅ FULLY OPERATIONAL

Your voice chat system is now running with:
- **Ollama** (llama3.2:latest) - AI text generation
- **Coqui TTS** - Text-to-speech (local)
- **Whisper** - Speech-to-text (external ngrok)

---

## 🚀 Quick Start

### Start All Servers

```bash
# Terminal 1: Start Coqui TTS Server
cd /Users/vivekkumar/Soosh/SooshAI/backend
python3 tts_server.py

# Terminal 2: Start Backend Server
cd /Users/vivekkumar/Soosh/SooshAI/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Verify Services

```bash
# Check Ollama
curl http://localhost:11434/api/version

# Check TTS Server
curl http://localhost:5002/health

# Check Backend
curl http://localhost:8000/
```

---

## 🔄 Switching to OpenAI

To switch from local Ollama to OpenAI, **change ONE line** in your config:

### Step 1: Update Config File

Edit `/Users/vivekkumar/Soosh/SooshAI/backend/app/core/ai_config.py`:

```python
# Line 22 - Change this:
PROVIDER: AIProvider = AIProvider.LOCAL

# To this:
PROVIDER: AIProvider = AIProvider.OPENAI
```

### Step 2: Add OpenAI API Key

Edit `/Users/vivekkumar/Soosh/SooshAI/backend/.env`:

```bash
# Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Restart Backend

```bash
# Stop the current backend (Ctrl+C)
# Then restart:
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**That's it!** Your app will now use:
- ✅ OpenAI GPT-4 for chat
- ✅ OpenAI TTS for voice synthesis
- ✅ Whisper still for speech-to-text

---

## 📊 Provider Comparison

| Feature | LOCAL (Current) | OPENAI |
|---------|----------------|---------|
| **LLM** | Ollama (llama3.2) | GPT-4 Turbo |
| **TTS** | Coqui (free) | OpenAI TTS ($$$) |
| **Cost** | Free | ~$0.01-0.03/request |
| **Speed** | Slower | Faster |
| **Privacy** | Full | Shared with OpenAI |
| **Quality** | Good | Better |

---

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Check if running
ps aux | grep ollama

# Restart
brew services restart ollama
# OR
ollama serve
```

### TTS Server Fails to Start

```bash
# Check if already running
lsof -i :5002

# If port is busy, kill it
kill -9 $(lsof -t -i:5002)

# Restart
python3 tts_server.py
```

### Backend Can't Find Ollama

Check the model name in `/backend/app/core/ai_config.py`:

```python
OLLAMA_MODEL: str = "llama3.2:latest"  # Must match `ollama list`
```

Verify your model:
```bash
ollama list
```

---

## 🔧 Configuration Files

### Main Config
`/backend/app/core/ai_config.py` - Switch providers here

### Environment Variables
`/backend/.env` - API keys and secrets

### Voice Chat Endpoints
`/backend/app/api/v1/endpoints/voice_chat.py` - REST API

### TTS Server
`/backend/tts_server.py` - Local text-to-speech

---

## 📱 Testing Voice Chat

### Test TTS Directly
```bash
curl -X POST http://localhost:5002/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Soosh!"}' \
  --output test.wav

# Play the audio
afplay test.wav
```

### Test Ollama Chat
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"llama3.2:latest\", \"prompt\": \"Say hello\", \"stream\": false}"
```

### Test Full Voice Chat (via Backend)
```bash
curl -X POST http://localhost:8000/api/v1/voice/test-tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing voice chat"}' \
  --output backend_test.wav
```

---

## 🎤 Available Models in Ollama

To see what models you have:
```bash
ollama list
```

To download a different model:
```bash
ollama pull llama3.1
ollama pull mistral
ollama pull phi3
```

Then update `ai_config.py`:
```python
OLLAMA_MODEL: str = "mistral:latest"
```

---

## 🔐 Security Notes

- **Never commit** `.env` file with real API keys
- **Use environment variables** for production
- **Ollama runs locally** - no data sent to cloud
- **OpenAI mode** sends data to OpenAI servers

---

## 📞 Support

- **Issues**: Check backend logs in Terminal 2
- **TTS Issues**: Check TTS server logs in Terminal 1
- **Ollama Issues**: Run `ollama logs`

---

**Last Updated**: November 1, 2025
**Status**: ✅ Operational with Local AI (Ollama + Coqui TTS)
