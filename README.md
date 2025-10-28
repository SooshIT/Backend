# SOOSH BACKEND - FastAPI + PostgreSQL + AI

**Enterprise-grade backend with modular AI providers**

---

## 🚀 **QUICK START**

### **Option 1: Local AI (FREE!)**

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-local.txt  # For local AI only

# 2. Set up PostgreSQL
psql postgres
CREATE DATABASE soosh;
\c soosh
\i database_schema.sql
\q

# 3. Install & start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.1

# 4. Start Coqui TTS server
python tts_server.py

# 5. Configure environment
cp .env.example .env
# Edit .env:
# PROVIDER=local
# OLLAMA_BASE_URL=http://localhost:11434
# COQUI_TTS_URL=http://localhost:5002

# 6. Start backend
uvicorn main:app --reload
```

**Visit**: http://localhost:8000/api/docs

---

### **Option 2: OpenAI (Production Quality)**

```bash
# 1-2. Same as above (dependencies + database)

# 3. Configure environment
cp .env.example .env
# Edit .env:
# PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here

# 4. Start backend
uvicorn main:app --reload
```

---

## 📁 **PROJECT STRUCTURE**

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── voice_chat.py      # Voice AI endpoints
│   │       └── __init__.py            # API router
│   ├── core/
│   │   ├── ai_config.py               # AI provider config
│   │   ├── config.py                  # App settings
│   │   ├── database.py                # Database connection
│   │   └── exceptions.py              # Custom exceptions
│   └── services/
│       ├── ai_provider_service.py     # Unified AI service
│       └── age_adaptive_ai.py         # Age-appropriate AI
│
├── main.py                            # FastAPI app entry
├── database_schema.sql                # Complete database
├── tts_server.py                      # Coqui TTS server
├── requirements.txt                   # Core dependencies
├── requirements-local.txt             # Local AI dependencies
├── .env.example                       # Environment template
│
└── 📚 DOCUMENTATION
    ├── README.md                      # This file
    ├── API_ENDPOINTS.md               # 150+ endpoint specs
    ├── database_schema.sql            # Database schema
    ├── AI_INTEGRATION_STRATEGY.md     # AI architecture
    ├── IMPLEMENTATION_ROADMAP.md      # 20-week plan
    └── LOCAL_AI_SETUP_GUIDE.md        # Local AI setup
```

---

## 🔧 **CONFIGURATION**

### **.env File**

```bash
# ========================================
# MAIN AI PROVIDER SWITCH
# ========================================
PROVIDER=local          # Change to "openai" for production

# ========================================
# LOCAL PROVIDERS (Ollama + Coqui TTS)
# ========================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest
COQUI_TTS_URL=http://localhost:5002

# ========================================
# CLOUD PROVIDERS (OpenAI)
# ========================================
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# ========================================
# DATABASE
# ========================================
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/soosh
DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5432/soosh

# ========================================
# OTHER SERVICES
# ========================================
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_...
WHISPER_API_URL=https://your-whisper-endpoint.com
```

---

## 📊 **DATABASE**

### **Setup**

```bash
# Create database
createdb soosh

# Run schema
psql soosh < database_schema.sql

# Or use Alembic migrations
alembic upgrade head
```

### **Schema Overview**

**20+ Tables**:
- `users` - 5 user types (beginner, mid_level, experienced, stay_at_home, disabled)
- `user_ai_profiles` - AI profiling with vector embeddings
- `categories` & `subcategories` - 22 main + 101 sub
- `opportunities` - Courses, jobs, mentorships, workshops
- `mentor_profiles` - Mentor-specific data
- `bookings` - Session scheduling
- `payments` - Stripe transactions
- `learning_paths` - Progress tracking
- `notifications` - Multi-channel
- `ai_agents` - For disabled users (unique!)

**Advanced Features**:
- ✅ pgvector - Vector similarity search
- ✅ PostGIS - Geolocation queries
- ✅ pg_trgm - Full-text search
- ✅ Partitioning - Scalability

---

## 🤖 **AI PROVIDERS**

### **Switch Providers**

Edit `.env`:
```bash
# Use local (FREE!)
PROVIDER=local

# Use OpenAI (production quality)
PROVIDER=openai
```

**That's it!** No code changes needed.

### **Provider Comparison**

| Feature | Local (Ollama + Coqui) | OpenAI (GPT-4 + TTS) |
|---------|------------------------|----------------------|
| **Cost** | FREE | ~$0.02/conversation |
| **Quality** | Good | Excellent |
| **Voice** | Robotic | Natural |
| **Setup** | 10 mins | 2 mins |
| **Offline** | ✅ Yes | ❌ No |

---

## 📡 **API ENDPOINTS**

### **Main Endpoints**

```bash
# Check current provider
GET /api/v1/voice/provider

# Complete voice conversation (main endpoint!)
POST /api/v1/voice/voice-conversation
  - audio: Audio file
  - conversation_history: JSON (optional)
  - system_prompt: AI instructions (optional)
  Returns: {user_text, ai_text, ai_audio}

# Text chat only
POST /api/v1/voice/chat
  - message: User text
  Returns: {response}

# Transcribe audio only
POST /api/v1/voice/transcribe
  - audio: Audio file
  Returns: {text}

# Text-to-speech only
POST /api/v1/voice/text-to-speech
  - text: Text to convert
  Returns: Audio file (WAV)

# Test without audio
POST /api/v1/voice/test-flow
  - test_text: Test input
  Returns: Complete flow result
```

### **Full API Documentation**

See `API_ENDPOINTS.md` for 150+ endpoints covering:
- Authentication (8 endpoints)
- AI Profiling (6 endpoints)
- Categories (4 endpoints)
- Opportunities (8 endpoints)
- Mentors (10 endpoints)
- Bookings (12 endpoints)
- Payments (8 endpoints)
- Learning Paths (10 endpoints)
- Notifications (6 endpoints)
- Messages (5 + WebSocket)
- AI Agent (12 endpoints)
- Analytics (6 endpoints)

**Interactive Docs**: http://localhost:8000/api/docs

---

## 🧪 **TESTING**

### **Test Voice AI Flow**

```bash
# 1. Check provider
curl http://localhost:8000/api/v1/voice/provider

# 2. Test complete flow (text input)
curl -X POST http://localhost:8000/api/v1/voice/test-flow \
  -F "test_text=Hello! I want to learn programming."

# 3. Test with audio
curl -X POST http://localhost:8000/api/v1/voice/voice-conversation \
  -F "audio=@recording.m4a"
```

### **Unit Tests**

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## 🚀 **DEPLOYMENT**

### **Option 1: Docker**

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### **Option 2: VPS (DigitalOcean, AWS, etc.)**

```bash
# On server
git clone <repo>
cd backend

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env with production values

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Option 3: Heroku**

```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create soosh-backend
git push heroku main
```

---

## 📈 **PERFORMANCE**

### **Optimization**

- Redis caching for recommendations (30 min TTL)
- Database connection pooling (10 connections)
- Vector search indexes (IVFFlat, HNSW)
- Background tasks with Celery
- API rate limiting (60 req/min per user)

### **Monitoring**

```bash
# Health check
curl http://localhost:8000/health

# Metrics (if enabled)
curl http://localhost:8000/metrics
```

---

## 🔒 **SECURITY**

- JWT authentication with refresh tokens
- Password hashing (bcrypt)
- OAuth2 flows (Google, Apple, LinkedIn)
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (per user, per IP)
- CORS configuration
- HTTPS only in production

---

## 🐛 **TROUBLESHOOTING**

### **"Module not found" errors**

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### **"Database connection failed"**

```bash
# Check PostgreSQL is running
psql -l

# Check connection string in .env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/soosh
```

### **"Ollama not responding"**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama && ollama serve
```

### **"TTS server not responding"**

```bash
# Check if TTS server is running
curl http://localhost:5002/health

# Restart TTS server
python tts_server.py
```

---

## 📚 **DOCUMENTATION**

- **API Reference**: `API_ENDPOINTS.md`
- **Database Schema**: `database_schema.sql`
- **AI Architecture**: `AI_INTEGRATION_STRATEGY.md`
- **Implementation Plan**: `IMPLEMENTATION_ROADMAP.md`
- **Local AI Setup**: `LOCAL_AI_SETUP_GUIDE.md`

---

## 🔧 **DEVELOPMENT**

### **Code Quality**

```bash
# Format code
black .

# Lint
flake8 app/

# Type checking
mypy app/
```

### **Database Migrations**

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🎯 **NEXT STEPS**

1. **Test locally** - Make sure everything works
2. **Implement endpoints** - Start with authentication
3. **Connect frontend** - Integrate with React Native app
4. **Add features** - Follow IMPLEMENTATION_ROADMAP.md
5. **Deploy** - When ready for production

---

## 📞 **SUPPORT**

- **Docs**: See markdown files in this directory
- **API Docs**: http://localhost:8000/api/docs
- **Issues**: Create GitHub issue

---

**Backend is ready to power your AI learning platform!** 🚀
