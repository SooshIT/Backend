# LOCAL AI SETUP GUIDE

**Set up Ollama + Coqui TTS for offline AI testing**

This guide helps you run the entire AI voice flow locally without any API costs!

---

## 📋 **ARCHITECTURE**

```
User speaks → Mic → Expo Audio
                ↓
         Whisper API (your existing ngrok endpoint)
                ↓
         User text transcribed
                ↓
         Ollama LLM (local, FREE)
                ↓
         AI generates reply text
                ↓
         Coqui TTS (local, FREE)
                ↓
         Speech audio generated
                ↓
         Audio played + transcript shown
```

**Cost**: $0.00 (everything runs locally!)

---

## 🚀 **STEP 1: INSTALL OLLAMA**

### **macOS/Linux**:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve
```

### **Windows**:

Download from: https://ollama.com/download/windows

### **Pull a model**:

```bash
# Option 1: Llama 3.1 (8B - recommended, fast)
ollama pull llama3.1:latest

# Option 2: Mistral (7B - smaller, faster)
ollama pull mistral:latest

# Option 3: Phi-3 (3.8B - very fast)
ollama pull phi3:latest

# Check available models
ollama list
```

### **Test Ollama**:

```bash
# Test in terminal
ollama run llama3.1

# Or test via API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

**Ollama runs on**: `http://localhost:11434`

---

## 🎤 **STEP 2: INSTALL COQUI TTS**

### **Install via pip**:

```bash
# Create virtual environment
python3 -m venv tts-env
source tts-env/bin/activate  # On Windows: tts-env\Scripts\activate

# Install Coqui TTS
pip install TTS

# Test installation
tts --text "Hello! This is a test." --out_path test.wav
```

### **Start TTS Server**:

```bash
# Simple server (built-in)
tts-server --model_name tts_models/en/ljspeech/tacotron2-DDC

# Or create custom server (better)
python tts_server.py
```

**Create `tts_server.py`**:

```python
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS
import io

app = Flask(__name__)

# Load TTS model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Generate audio
        audio_buffer = io.BytesIO()
        tts.tts_to_file(text=text, file_path=audio_buffer, speaker=None)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='speech.wav'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": "tacotron2-DDC"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
```

**Run TTS server**:

```bash
python tts_server.py
```

**TTS runs on**: `http://localhost:5002`

### **Test TTS**:

```bash
curl -X POST http://localhost:5002/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! This is Sooshi, your learning buddy!"}' \
  --output test.wav

# Play the audio
afplay test.wav  # macOS
# or
aplay test.wav   # Linux
```

---

## 🔧 **STEP 3: CONFIGURE BACKEND**

### **Update `.env`**:

```bash
# ========================================
# AI PROVIDER CONFIGURATION
# ========================================

# MAIN SWITCH (change to "openai" for production)
PROVIDER=local

# LOCAL PROVIDERS
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest
OLLAMA_TIMEOUT=120

COQUI_TTS_URL=http://localhost:5002
COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC

# WHISPER (your existing endpoint)
WHISPER_API_URL=https://cf4d52b914ef.ngrok-free.app/api/v1/whisper/transcribe
WHISPER_API_KEY=

# OPENAI (for when you switch to production)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### **Update API router** (`backend/app/api/v1/__init__.py`):

```python
from app.api.v1.endpoints import voice_chat

# Add to router
api_router.include_router(voice_chat.router, prefix="/voice", tags=["Voice Chat"])
```

---

## 🧪 **STEP 4: TEST THE SETUP**

### **Test 1: Check Provider**

```bash
curl http://localhost:8000/api/v1/voice/provider
```

**Expected**:
```json
{
  "provider": "local",
  "provider_name": "Local (Ollama + Coqui TTS)",
  "status": "active"
}
```

---

### **Test 2: Test Text Chat**

```bash
curl -X POST http://localhost:8000/api/v1/voice/test-flow \
  -F "test_text=Hello! I want to learn programming."
```

**Expected**:
```json
{
  "user_text": "Hello! I want to learn programming.",
  "ai_text": "That's great! Programming is an excellent skill...",
  "ai_audio": "base64_encoded_audio_data",
  "provider": "Local (Ollama + Coqui TTS)",
  "status": "success"
}
```

---

### **Test 3: Test Complete Voice Flow**

**Record audio on your phone**, then:

```bash
curl -X POST http://localhost:8000/api/v1/voice/voice-conversation \
  -F "audio=@test-audio.m4a" \
  -F "system_prompt=You are Sooshi, a friendly AI for kids. Use simple words and emojis!"
```

**Expected**:
```json
{
  "user_text": "I love drawing!",
  "ai_text": "Wow! Drawing is so cool! 🎨✨ Let's find fun art classes for you!",
  "ai_audio": "base64_audio_here",
  "provider": "local"
}
```

---

## 📱 **STEP 5: TEST FROM REACT NATIVE**

Create test component:

```typescript
// app/test-voice.tsx
import { useState } from 'react';
import { View, Button, Text } from 'react-native';
import { Audio } from 'expo-av';

export default function TestVoiceScreen() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [result, setResult] = useState<any>(null);

  const startRecording = async () => {
    const { recording } = await Audio.Recording.createAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY
    );
    setRecording(recording);
  };

  const stopRecording = async () => {
    if (!recording) return;

    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();

    // Send to backend
    const formData = new FormData();
    formData.append('audio', {
      uri: uri!,
      type: 'audio/m4a',
      name: 'recording.m4a',
    } as any);

    const response = await fetch('http://localhost:8000/api/v1/voice/voice-conversation', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setResult(data);

    // Play audio response
    if (data.ai_audio) {
      const { sound } = await Audio.Sound.createAsync({
        uri: `data:audio/wav;base64,${data.ai_audio}`
      });
      await sound.playAsync();
    }
  };

  return (
    <View style={{padding: 20}}>
      <Button
        title={recording ? "Stop Recording" : "Start Recording"}
        onPress={recording ? stopRecording : startRecording}
      />

      {result && (
        <View style={{marginTop: 20}}>
          <Text>You said: {result.user_text}</Text>
          <Text>AI said: {result.ai_text}</Text>
          <Text>Provider: {result.provider}</Text>
        </View>
      )}
    </View>
  );
}
```

---

## 🔄 **SWITCHING TO OPENAI (LATER)**

When you're ready to use OpenAI APIs:

### **Option 1: Change .env**

```bash
# Just change this one line!
PROVIDER=openai

# Make sure you have your API key
OPENAI_API_KEY=sk-your-actual-api-key
```

### **Option 2: Change in code**

```python
# backend/app/core/ai_config.py
class AIProviderConfig(BaseSettings):
    PROVIDER: AIProvider = AIProvider.OPENAI  # Changed from LOCAL
```

**That's it!** No other code changes needed. The abstraction layer handles everything.

---

## 📊 **COMPARISON: LOCAL VS OPENAI**

| Feature | Local (Ollama + Coqui) | OpenAI (GPT-4 + TTS) |
|---------|------------------------|----------------------|
| **Cost** | $0 (FREE!) | ~$0.01-0.03 per conversation |
| **Speed** | Fast (depends on your CPU) | Very fast (cloud) |
| **Quality** | Good (Llama 3.1 is decent) | Excellent (GPT-4) |
| **Voice Quality** | Robotic (Tacotron2) | Natural (OpenAI TTS) |
| **Offline** | ✅ Yes | ❌ No (needs internet) |
| **Privacy** | ✅ Full privacy | ⚠️ Data sent to OpenAI |
| **Setup** | 🔧 Requires installation | ✅ Just API key |

---

## 🐛 **TROUBLESHOOTING**

### **Ollama not responding**:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### **Coqui TTS errors**:

```bash
# Reinstall TTS
pip uninstall TTS
pip install TTS --no-cache-dir

# Try a simpler model
tts-server --model_name tts_models/en/ljspeech/glow-tts
```

### **Port conflicts**:

```bash
# Change Ollama port (if 11434 is taken)
OLLAMA_PORT=11435 ollama serve

# Change TTS port (if 5002 is taken)
# Edit tts_server.py: app.run(port=5003)
```

### **Audio playback issues on React Native**:

Make sure you have:
```bash
npm install expo-av
```

And request audio permissions:
```typescript
import { Audio } from 'expo-av';

await Audio.requestPermissionsAsync();
await Audio.setAudioModeAsync({
  allowsRecordingIOS: true,
  playsInSilentModeIOS: true,
});
```

---

## 📈 **PERFORMANCE TIPS**

### **Make Ollama faster**:

```bash
# Use smaller models
ollama pull phi3  # 3.8B params, much faster

# Or use quantized models (4-bit)
ollama pull llama3.1:8b-instruct-q4_0
```

### **Make TTS faster**:

```python
# Use faster model
tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")  # Faster than Tacotron2
```

---

## ✅ **FINAL CHECKLIST**

Before starting development:

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull llama3.1`)
- [ ] TTS server running (`python tts_server.py`)
- [ ] FastAPI backend running (`uvicorn main:app --reload`)
- [ ] `.env` set to `PROVIDER=local`
- [ ] Test endpoint works (`curl http://localhost:8000/api/v1/voice/test-flow`)
- [ ] React Native can record audio
- [ ] React Native can play audio

---

## 🎯 **NEXT STEPS**

1. **Test locally** - Make sure everything works
2. **Build features** - Use the voice chat in your app
3. **Gather feedback** - See what users think
4. **Switch to OpenAI** - When ready for production, just change `PROVIDER=openai`

**You're all set!** Start building without worrying about API costs. 🚀

---

## 📚 **RESOURCES**

- Ollama docs: https://ollama.com/
- Coqui TTS docs: https://github.com/coqui-ai/TTS
- Available TTS models: https://github.com/coqui-ai/TTS/wiki/Released-Models
- Ollama models: https://ollama.com/library
