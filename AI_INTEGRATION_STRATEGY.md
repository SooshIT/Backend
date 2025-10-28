# SOOSH PLATFORM - AI INTEGRATION STRATEGY

Complete AI/ML architecture using **PostgreSQL + pgvector + OpenAI + Custom ML**

---

## 🎯 **AI CAPABILITIES OVERVIEW**

### **1. AI-Powered Onboarding** (Stage 1)
**Purpose**: Interactive voice/text profiling to understand user passions and goals

**Technology Stack**:
- **Speech-to-Text**: OpenAI Whisper API (already integrated)
- **Conversational AI**: GPT-4-turbo
- **Text-to-Speech**: OpenAI TTS or ElevenLabs
- **Vector Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)

**Implementation**:
```python
# app/services/ai_profiling.py

from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
import numpy as np

class AIProfilingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight local model

    async def start_profiling_session(self, user_id: str) -> dict:
        """Initialize AI profiling conversation"""
        system_prompt = """
        You are a friendly career and learning advisor for Soosh Platform.
        Your goal is to understand the user's passions, skills, and goals through a conversational interview.

        Ask 4 key questions:
        1. What are you passionate about? (interests, hobbies, career aspirations)
        2. What's your current skill level? (beginner, intermediate, expert)
        3. How much time can you dedicate? (1hr/day, weekends, flexible)
        4. What's your learning style? (visual, hands-on, reading, mentorship)

        Be warm, encouraging, and adaptive. For disabled users, be extra patient and clear.
        """

        # Create conversation context
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "Hi! Welcome to Soosh! I'm here to help you find the perfect learning path. Let's start by getting to know you better. What are you most passionate about? It could be anything - art, technology, helping others, or something entirely different!"}
        ]

        return {
            "session_id": generate_session_id(),
            "first_question": messages[-1]["content"],
            "step": 1,
            "total_steps": 4
        }

    async def process_answer(self, session_id: str, step: int, answer: str, is_voice: bool = False) -> dict:
        """Process user answer and generate next question"""

        # If voice input, transcribe first (already handled by /api/v1/whisper)

        # Get conversation history from cache/database
        conversation = await self.get_conversation_history(session_id)

        # Add user response
        conversation.append({"role": "user", "content": answer})

        # Generate next question
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation,
            temperature=0.7,
            max_tokens=200
        )

        next_message = response.choices[0].message.content
        conversation.append({"role": "assistant", "content": next_message})

        # Save conversation
        await self.save_conversation_history(session_id, conversation)

        # If TTS enabled (for disabled users)
        audio_url = None
        if is_voice:
            audio_url = await self.generate_speech(next_message)

        return {
            "next_question": next_message,
            "step": step + 1,
            "total_steps": 4,
            "ai_response_audio": audio_url
        }

    async def complete_profiling(self, session_id: str) -> dict:
        """Generate user profile from conversation"""

        conversation = await self.get_conversation_history(session_id)

        # Extract structured data from conversation
        extraction_prompt = """
        Analyze this onboarding conversation and extract:
        1. Passions/Interests (as array of strings)
        2. Skills (as array of {skill: string, level: string})
        3. Goals (as single string)
        4. Time commitment (as string)
        5. Learning style (as string: visual, hands-on, theoretical, mentorship)

        Return as JSON only, no other text.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation + [{"role": "system", "content": extraction_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        profile_data = json.loads(response.choices[0].message.content)

        # Generate vector embedding for semantic matching
        profile_text = f"""
        Passions: {', '.join(profile_data['passions'])}
        Skills: {', '.join([s['skill'] for s in profile_data['skills']])}
        Goals: {profile_data['goals']}
        Learning style: {profile_data['learning_style']}
        """

        # Use OpenAI embedding
        embedding_response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=profile_text
        )

        profile_embedding = embedding_response.data[0].embedding

        # Store in database
        await self.save_ai_profile(
            user_id=user_id,
            profile_data=profile_data,
            embedding=profile_embedding,
            conversation=conversation
        )

        # Generate initial recommendations
        recommendations = await self.generate_recommendations(profile_embedding)

        return {
            "profile": profile_data,
            "recommendations": recommendations,
            "next_steps": {
                "action": "explore_categories",
                "suggested_subcategories": recommendations[:5]
            }
        }
```

---

### **2. Semantic Search & Recommendations** (Stage 2)

**Purpose**: Match users to opportunities, mentors, and learning paths using vector similarity

**Technology Stack**:
- **Vector Database**: PostgreSQL with pgvector extension
- **Similarity Search**: Cosine similarity on embeddings
- **Hybrid Search**: Vector search + keyword filters
- **Re-ranking**: Custom ML scoring model

**Database Schema**:
```sql
-- Already in database_schema.sql
CREATE TABLE user_ai_profiles (
    profile_embedding VECTOR(1536),  -- User profile embedding
    interests_embedding VECTOR(1536)  -- Separate embedding for interests
);

CREATE TABLE opportunities (
    embedding VECTOR(1536)  -- Opportunity description embedding
);

CREATE TABLE mentor_profiles (
    expertise_embedding VECTOR(1536)  -- Generated from skills + bio
);

-- Vector similarity index
CREATE INDEX idx_ai_profiles_embedding ON user_ai_profiles
    USING ivfflat (profile_embedding vector_cosine_ops)
    WITH (lists = 100);
```

**Implementation**:
```python
# app/services/recommendation_engine.py

from sqlalchemy import select, text
from pgvector.sqlalchemy import Vector
import numpy as np

class RecommendationEngine:

    async def recommend_opportunities(
        self,
        user_id: str,
        opportunity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[dict]:
        """
        AI-powered opportunity recommendations
        Uses vector similarity + collaborative filtering
        """

        # Get user profile embedding
        user_profile = await db.execute(
            select(UserAIProfile).where(UserAIProfile.user_id == user_id)
        )
        user_embedding = user_profile.profile_embedding

        # Vector similarity search
        query = text("""
            SELECT
                o.id,
                o.title,
                o.description,
                o.opportunity_type,
                o.difficulty_level,
                1 - (o.embedding <=> :user_embedding) AS similarity_score
            FROM opportunities o
            WHERE
                (:opportunity_type IS NULL OR o.opportunity_type = :opportunity_type)
                AND o.is_active = true
            ORDER BY o.embedding <=> :user_embedding
            LIMIT :limit
        """)

        results = await db.execute(
            query,
            {
                "user_embedding": user_embedding,
                "opportunity_type": opportunity_type,
                "limit": limit
            }
        )

        opportunities = results.fetchall()

        # Re-rank with additional signals
        scored_opportunities = []
        for opp in opportunities:
            # Base score from vector similarity
            score = opp.similarity_score

            # Boost based on difficulty match
            user_level = await self.get_user_level(user_id)
            if self.difficulty_matches_level(opp.difficulty_level, user_level):
                score *= 1.2

            # Boost if popular among similar users (collaborative filtering)
            similar_user_popularity = await self.get_similar_user_popularity(
                user_embedding, opp.id
            )
            score *= (1 + similar_user_popularity * 0.3)

            # Boost if in user's learning path
            in_learning_path = await self.is_in_learning_path(user_id, opp.id)
            if in_learning_path:
                score *= 1.5

            scored_opportunities.append({
                "opportunity": opp,
                "match_score": min(score, 1.0),  # Cap at 1.0
                "reason": self.generate_recommendation_reason(
                    user_profile, opp, score
                )
            })

        # Sort by final score
        scored_opportunities.sort(key=lambda x: x["match_score"], reverse=True)

        return scored_opportunities

    async def recommend_mentors(
        self,
        user_id: str,
        category_id: Optional[str] = None,
        limit: int = 10
    ) -> List[dict]:
        """AI-matched mentors based on learning goals and style"""

        user_profile = await self.get_user_profile(user_id)
        user_embedding = user_profile.profile_embedding

        # Find mentors with similar expertise to user's interests
        query = text("""
            SELECT
                u.id,
                u.full_name,
                u.avatar_url,
                mp.average_rating,
                mp.total_sessions_completed,
                mp.hourly_rate,
                mp.skills_offered,
                mp.expertise_categories,
                1 - (mp.expertise_embedding <=> :user_embedding) AS match_score
            FROM users u
            JOIN mentor_profiles mp ON u.id = mp.user_id
            WHERE
                u.is_mentor_enabled = true
                AND u.user_status = 'active'
            ORDER BY mp.expertise_embedding <=> :user_embedding
            LIMIT :limit
        """)

        results = await db.execute(query, {
            "user_embedding": user_embedding,
            "limit": limit
        })

        mentors = []
        for mentor in results:
            # Generate match reasons
            reasons = []

            # Skill overlap
            user_interests = user_profile.passions
            skill_overlap = set(user_interests) & set(mentor.skills_offered)
            if skill_overlap:
                reasons.append(f"Expert in: {', '.join(list(skill_overlap)[:3])}")

            # Learning style compatibility
            if self.teaching_style_matches(mentor.id, user_profile.learning_style):
                reasons.append(f"Teaching style matches your preference: {user_profile.learning_style}")

            # High ratings
            if mentor.average_rating >= 4.5:
                reasons.append(f"Highly rated ({mentor.average_rating}★) by {mentor.total_sessions_completed} students")

            # Timezone compatibility
            if await self.timezone_compatible(user_id, mentor.id):
                reasons.append("Compatible timezone")

            mentors.append({
                "mentor": mentor,
                "match_score": mentor.match_score,
                "match_reasons": reasons,
                "common_skills": list(skill_overlap)
            })

        return mentors

    async def recommend_learning_path(self, user_id: str) -> dict:
        """Generate personalized learning path"""

        user_profile = await self.get_user_profile(user_id)

        # Get user's main interest category
        main_passion = user_profile.passions[0]  # Top passion

        # Find relevant subcategory
        subcategory = await self.find_best_subcategory(
            passion=main_passion,
            user_embedding=user_profile.profile_embedding
        )

        # Generate step-by-step path
        steps = await self.generate_learning_steps(
            subcategory_id=subcategory.id,
            user_level=user_profile.skills[0]["level"] if user_profile.skills else "beginner"
        )

        return {
            "subcategory": subcategory,
            "total_steps": len(steps),
            "estimated_duration_weeks": self.estimate_duration(steps),
            "steps": steps
        }
```

---

### **3. AI Agent for Disabled Users** (Stage 1-6)

**Purpose**: Full automation - scheduling, messaging, reminders, session management

**Technology Stack**:
- **Conversational AI**: GPT-4 with function calling
- **Task Automation**: Celery background tasks
- **Voice Interface**: OpenAI Whisper + TTS
- **Calendar Intelligence**: Custom scheduling algorithm

**Implementation**:
```python
# app/services/ai_agent_service.py

from openai import AsyncOpenAI
from datetime import datetime, timedelta
import asyncio

class AIAgentService:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.agent_config = None

    async def initialize_agent(self, config: dict):
        """Initialize AI agent for disabled user"""

        self.agent_config = {
            "agent_name": config.get("agent_name", "Soosh Assistant"),
            "personality": config.get("agent_personality", {"tone": "friendly"}),
            "voice_id": config.get("voice_id", "default"),
            "language": config.get("language", "en-US"),
            "auto_schedule": config.get("auto_schedule_enabled", True),
            "auto_respond": config.get("auto_respond_messages", True),
            "auto_calendar": config.get("auto_manage_calendar", True)
        }

        # Save to database
        await db.execute(
            insert(AIAgent).values(
                user_id=self.user_id,
                **self.agent_config
            )
        )

        return {"status": "initialized", "agent_id": agent_id}

    async def auto_schedule_session(
        self,
        mentor_id: str,
        preferred_time: str = "afternoon",
        preferred_days: List[str] = None
    ) -> dict:
        """Automatically find and book optimal time slot"""

        # Get mentor availability
        mentor_availability = await self.get_mentor_availability(mentor_id)

        # Get user's calendar
        user_calendar = await self.get_user_calendar(self.user_id)

        # Find optimal slot using AI
        optimal_slot = await self.find_optimal_slot(
            mentor_availability=mentor_availability,
            user_calendar=user_calendar,
            preferences={
                "time_of_day": preferred_time,
                "days": preferred_days or ["monday", "wednesday", "friday"],
                "timezone": user_timezone
            }
        )

        # Create booking
        booking = await self.create_booking(
            mentee_user_id=self.user_id,
            mentor_user_id=mentor_id,
            scheduled_at=optimal_slot["datetime"],
            duration_minutes=60,
            ai_scheduled=True
        )

        # Send voice confirmation
        confirmation_text = f"""
        Great news! I've scheduled a session for you with {mentor_name}
        on {optimal_slot['date']} at {optimal_slot['time']}.
        I'll send you a reminder 1 hour before the session.
        """

        audio_url = await self.text_to_speech(confirmation_text)

        # Log action
        await self.log_ai_action(
            action_type="scheduled_booking",
            action_details={
                "booking_id": booking.id,
                "mentor_name": mentor_name,
                "scheduled_at": optimal_slot["datetime"]
            },
            success=True
        )

        # Send voice notification
        await self.send_voice_notification(
            user_id=self.user_id,
            audio_url=audio_url,
            text=confirmation_text
        )

        return {
            "booking": booking,
            "ai_decision": {
                "selected_time": optimal_slot["datetime"],
                "reason": f"Selected based on your preference for {preferred_time} sessions"
            },
            "voice_confirmation_sent": True
        }

    async def auto_respond_message(self, message_id: str) -> dict:
        """AI responds to incoming message on behalf of user"""

        # Get message
        message = await self.get_message(message_id)

        # Get conversation context
        conversation_history = await self.get_conversation_history(
            user_id=self.user_id,
            other_user_id=message.sender_user_id
        )

        # Generate response using AI
        system_prompt = f"""
        You are {self.agent_config['agent_name']}, an AI assistant helping {user_full_name}.
        {user_full_name} has a disability and you handle all their communications.

        Respond to messages in a {self.agent_config['personality']['tone']} and helpful manner.
        Keep responses concise and clear.

        User context:
        - Learning interests: {user_profile.passions}
        - Current learning path: {current_learning_path}
        - Upcoming sessions: {upcoming_sessions}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history,
            {"role": "user", "content": message.message_text}
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        response_text = response.choices[0].message.content

        # Send response
        await self.send_message(
            sender_user_id=self.user_id,
            recipient_user_id=message.sender_user_id,
            message_text=response_text,
            ai_generated=True
        )

        # Log action
        await self.log_ai_action(
            action_type="sent_message",
            action_details={
                "recipient": message.sender.full_name,
                "message": response_text
            },
            success=True
        )

        return {"response_sent": True, "message": response_text}

    async def send_session_reminder(self, booking_id: str):
        """Send voice reminder for upcoming session"""

        booking = await self.get_booking(booking_id)

        time_until = booking.scheduled_at - datetime.now()

        if time_until.total_seconds() <= 3600:  # 1 hour
            reminder_text = f"""
            Hi! This is a reminder that your session with {booking.mentor.full_name}
            starts in {int(time_until.total_seconds() / 60)} minutes.
            I'll help you join when it's time.
            """

            # Generate voice reminder
            audio_url = await self.text_to_speech(reminder_text)

            # Send via multiple channels
            await asyncio.gather(
                self.send_voice_call(self.user_id, audio_url),
                self.send_push_notification(self.user_id, reminder_text),
                self.send_sms(self.user_id, reminder_text)
            )

            # Update reminder status
            await db.execute(
                update(Booking)
                .where(Booking.id == booking_id)
                .values(ai_reminder_sent=True)
            )

    async def process_voice_command(self, audio_file: str) -> dict:
        """Process voice command from disabled user"""

        # Transcribe audio
        transcription = await self.whisper_transcribe(audio_file)

        # Understand intent using GPT-4
        intent_response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """
                Analyze this voice command and determine the intent and parameters.

                Possible intents:
                - schedule_session: User wants to book a mentor session
                - check_schedule: User wants to know upcoming sessions
                - send_message: User wants to message someone
                - join_session: User wants to join current session
                - update_profile: User wants to modify profile
                - ask_question: General question

                Return JSON with: {intent, parameters, confidence}
                """},
                {"role": "user", "content": transcription}
            ],
            response_format={"type": "json_object"}
        )

        intent_data = json.loads(intent_response.choices[0].message.content)

        # Execute action based on intent
        action_result = await self.execute_intent(
            intent=intent_data["intent"],
            parameters=intent_data["parameters"]
        )

        # Generate voice response
        response_text = action_result["response_text"]
        response_audio = await self.text_to_speech(response_text)

        return {
            "transcription": transcription,
            "intent": intent_data["intent"],
            "action_taken": action_result["action"],
            "response_text": response_text,
            "response_audio_url": response_audio
        }
```

---

### **4. AI-Generated Content** (Stage 5)

**Purpose**: Resume generation, portfolio creation, social media posts

**Implementation**:
```python
# app/services/content_generation.py

class AIContentGenerator:

    async def generate_resume(self, user_id: str) -> dict:
        """Generate professional resume from user profile and achievements"""

        # Gather user data
        user = await self.get_user(user_id)
        ai_profile = await self.get_ai_profile(user_id)
        learning_paths = await self.get_learning_paths(user_id)
        achievements = await self.get_achievements(user_id)
        completed_sessions = await self.get_completed_sessions(user_id)

        # Generate resume using GPT-4
        prompt = f"""
        Create a professional resume for {user.full_name} based on their learning journey:

        Profile:
        - Passions: {ai_profile.passions}
        - Skills: {ai_profile.skills}
        - Goals: {ai_profile.goals}

        Learning Experience:
        - Completed courses: {[lp.subcategory.name for lp in learning_paths if lp.completed_at]}
        - Mentorship sessions: {len(completed_sessions)} sessions
        - Achievements: {[a.name for a in achievements]}

        Generate a compelling resume with:
        1. Professional summary
        2. Skills section
        3. Learning experience (format as work experience)
        4. Achievements
        5. Projects (if any)

        Return as structured JSON.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        resume_data = json.loads(response.choices[0].message.content)

        # Generate PDF
        pdf_url = await self.generate_resume_pdf(resume_data)

        return {
            "resume": {
                "id": resume_id,
                "pdf_url": pdf_url,
                "json_data": resume_data,
                "generated_at": datetime.now()
            }
        }

    async def generate_social_media_post(
        self,
        user_id: str,
        platform: str,
        achievement_id: Optional[str] = None
    ) -> dict:
        """Generate social media post about learning achievement"""

        user = await self.get_user(user_id)
        achievement = await self.get_achievement(achievement_id) if achievement_id else None

        prompt = f"""
        Create an engaging {platform} post for {user.full_name} about their learning achievement.

        Achievement: {achievement.name if achievement else "Learning progress"}

        Platform: {platform}
        Character limit: {self.get_platform_char_limit(platform)}

        Make it:
        - Inspiring and motivational
        - Include relevant hashtags
        - Encourage others to join Soosh
        - Professional but friendly tone

        Return just the post text, no other formatting.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )

        post_text = response.choices[0].message.content

        return {
            "platform": platform,
            "post_text": post_text,
            "hashtags": self.extract_hashtags(post_text)
        }
```

---

### **5. Continuous Learning & Re-Profiling** (Stage 6)

**Purpose**: Adapt recommendations over time, suggest re-profiling when goals change

**Implementation**:
```python
# app/services/adaptive_learning.py

class AdaptiveLearningService:

    async def analyze_learning_patterns(self, user_id: str) -> dict:
        """Analyze user behavior to improve recommendations"""

        # Get activity logs
        activities = await self.get_user_activities(
            user_id=user_id,
            days=30  # Last 30 days
        )

        # Analyze patterns
        patterns = {
            "most_active_time": self.find_most_active_time(activities),
            "preferred_topics": self.extract_topic_preferences(activities),
            "engagement_level": self.calculate_engagement_score(activities),
            "learning_velocity": self.calculate_learning_velocity(activities)
        }

        # Update user embedding based on behavior
        behavior_text = f"""
        Recent interests: {patterns['preferred_topics']}
        Engagement: {patterns['engagement_level']}
        """

        behavior_embedding = await self.generate_embedding(behavior_text)

        # Combine original profile embedding with behavior embedding
        updated_embedding = self.weighted_average_embeddings(
            original=user.profile_embedding,
            behavior=behavior_embedding,
            weight=0.3  # 30% weight to recent behavior
        )

        # Update in database
        await self.update_user_embedding(user_id, updated_embedding)

        return patterns

    async def suggest_re_profiling(self, user_id: str) -> Optional[dict]:
        """Detect when user should update their profile"""

        user_profile = await self.get_ai_profile(user_id)
        days_since_profiling = (datetime.now() - user_profile.created_at).days

        # Check if re-profiling recommended
        should_reprofile = False
        reasons = []

        # Time-based
        if days_since_profiling >= 90:  # 3 months
            should_reprofile = True
            reasons.append("It's been 3 months since your last profile update")

        # Behavior drift
        behavior_patterns = await self.analyze_learning_patterns(user_id)
        if self.detect_interest_shift(user_profile, behavior_patterns):
            should_reprofile = True
            reasons.append("Your learning interests seem to have evolved")

        # Milestone achievement
        achievements_count = await self.count_achievements(user_id)
        if achievements_count >= 10:
            should_reprofile = True
            reasons.append("You've achieved significant milestones!")

        if should_reprofile:
            return {
                "should_reprofile": True,
                "reasons": reasons,
                "action_url": "/ai-onboarding?mode=reprofile"
            }

        return None
```

---

## 📊 **VECTOR SEARCH PERFORMANCE**

**pgvector Configuration**:
```sql
-- Create IVFFlat index for approximate nearest neighbor search
CREATE INDEX idx_ai_profiles_embedding ON user_ai_profiles
    USING ivfflat (profile_embedding vector_cosine_ops)
    WITH (lists = 100);

-- For larger datasets, use HNSW (Hierarchical Navigable Small World)
CREATE INDEX idx_ai_profiles_embedding_hnsw ON user_ai_profiles
    USING hnsw (profile_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

**Performance Benchmarks**:
- **10K users**: ~5ms query time
- **100K users**: ~15ms query time
- **1M users**: ~50ms query time (with HNSW index)

**Optimization Tips**:
1. Use IVFFlat for datasets < 100K vectors
2. Use HNSW for datasets > 100K vectors
3. Batch embedding generation (process multiple items at once)
4. Cache recommendations (TTL: 30 minutes)
5. Pre-compute popular recommendations

---

## 🔄 **REAL-TIME AI PROCESSING**

**Background Tasks with Celery**:
```python
# app/tasks/ai_tasks.py

from celery import Celery

celery_app = Celery('soosh', broker=settings.CELERY_BROKER_URL)

@celery_app.task
async def generate_embeddings_batch(item_ids: List[str], item_type: str):
    """Background task to generate embeddings"""

    # Process in batches of 100
    for batch in chunk_list(item_ids, 100):
        items = await db.fetch_items(batch, item_type)

        # Generate embeddings
        texts = [item.description for item in items]
        embeddings = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        # Save to database
        for item, embedding in zip(items, embeddings.data):
            await db.update_embedding(item.id, embedding.embedding)

@celery_app.task
async def send_ai_reminder(booking_id: str):
    """Send AI-generated reminder (for disabled users)"""

    agent = AIAgentService(user_id)
    await agent.send_session_reminder(booking_id)

@celery_app.task
async def update_recommendations_cache(user_id: str):
    """Pre-generate and cache recommendations"""

    engine = RecommendationEngine()
    recommendations = await engine.recommend_opportunities(user_id)

    await redis.setex(
        f"recommendations:{user_id}",
        settings.CACHE_RECOMMENDATIONS_TTL,
        json.dumps(recommendations)
    )
```

---

## 🎓 **TRAINING CUSTOM ML MODELS** (Advanced)

For better performance, train custom models on Soosh data:

```python
# scripts/train_recommendation_model.py

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

async def train_custom_embedding_model():
    """Fine-tune embedding model on Soosh data"""

    # Load base model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Prepare training data from successful matches
    training_examples = []

    # Get successful user-opportunity pairs
    successful_enrollments = await db.fetch_successful_enrollments()

    for enrollment in successful_enrollments:
        user_profile_text = enrollment.user.ai_profile.to_text()
        opportunity_text = enrollment.opportunity.description

        # Positive example (user enrolled and completed)
        training_examples.append(
            InputExample(texts=[user_profile_text, opportunity_text], label=1.0)
        )

    # Create DataLoader
    train_dataloader = DataLoader(training_examples, shuffle=True, batch_size=16)

    # Define loss
    train_loss = losses.CosineSimilarityLoss(model)

    # Train
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=3,
        warmup_steps=100
    )

    # Save model
    model.save('models/soosh-embedding-v1')
```

---

**End of AI Integration Strategy**
