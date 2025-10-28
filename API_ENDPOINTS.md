# SOOSH PLATFORM - API ENDPOINTS DOCUMENTATION

Complete REST API specification for all 6 user journey stages

**Base URL**: `http://localhost:8000/api/v1`

---

## 📋 TABLE OF CONTENTS

1. [Authentication & Onboarding](#1-authentication--onboarding-stage-1)
2. [AI Profiling](#2-ai-profiling-stage-1)
3. [Categories & Exploration](#3-categories--exploration-stage-2)
4. [Opportunities](#4-opportunities-stage-2)
5. [Mentors & Matching](#5-mentors--matching-stage-2)
6. [Bookings & Sessions](#6-bookings--sessions-stage-3)
7. [Payments](#7-payments-stage-3)
8. [Learning Paths & Progress](#8-learning-paths--progress-stage-4)
9. [Notifications](#9-notifications-stage-4)
10. [Messages & Communication](#10-messages--communication-stage-4)
11. [AI Agent (Disabled Users)](#11-ai-agent-stage-1-6)
12. [Portfolio & Resume](#12-portfolio--resume-stage-5)
13. [Community & Social](#13-community--social-stage-6)
14. [Analytics & Insights](#14-analytics--insights-stage-6)

---

## 1. AUTHENTICATION & ONBOARDING (Stage 1)

### `POST /api/v1/auth/register`
**Purpose**: Register new user (email/password)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "username": "johndoe",
  "user_type": "beginner"  // or mid_level, experienced, stay_at_home, disabled
}
```

**Response** (201):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "user_type": "beginner",
    "onboarding_completed": false
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

---

### `POST /api/v1/auth/login`
**Purpose**: Login with email/password

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "user": { /* user object */ },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

---

### `POST /api/v1/auth/google`
**Purpose**: OAuth login with Google

**Request Body**:
```json
{
  "token": "google_oauth_token"
}
```

---

### `POST /api/v1/auth/apple`
**Purpose**: OAuth login with Apple

---

### `POST /api/v1/auth/linkedin`
**Purpose**: OAuth login with LinkedIn

---

### `POST /api/v1/auth/verify-email`
**Purpose**: Verify email address

**Request Body**:
```json
{
  "token": "verification_token_from_email"
}
```

---

### `POST /api/v1/auth/resend-verification`
**Purpose**: Resend email verification link

---

### `POST /api/v1/auth/refresh-token`
**Purpose**: Refresh access token

**Request Body**:
```json
{
  "refresh_token": "current_refresh_token"
}
```

---

## 2. AI PROFILING (Stage 1)

### `POST /api/v1/ai-profiling/start`
**Purpose**: Start AI onboarding session

**Response**:
```json
{
  "session_id": "uuid",
  "first_question": "What are you most passionate about?",
  "ai_agent_id": "uuid"  // For disabled users
}
```

---

### `POST /api/v1/ai-profiling/submit-answer`
**Purpose**: Submit answer to AI question (text or voice)

**Request Body (Text)**:
```json
{
  "session_id": "uuid",
  "step": 1,
  "answer_text": "I'm passionate about design and technology",
  "answer_type": "text"
}
```

**Request Body (Voice)**:
```json
{
  "session_id": "uuid",
  "step": 1,
  "audio_file": "base64_encoded_audio",
  "answer_type": "voice"
}
```

**Response**:
```json
{
  "next_question": "What's your current skill level in design?",
  "step": 2,
  "total_steps": 4,
  "ai_response_audio": "url_to_tts_audio"  // For disabled users
}
```

---

### `POST /api/v1/ai-profiling/complete`
**Purpose**: Complete AI profiling and generate profile

**Request Body**:
```json
{
  "session_id": "uuid"
}
```

**Response**:
```json
{
  "profile": {
    "passions": ["Design", "Technology"],
    "skills": [
      {"skill": "UI Design", "level": "intermediate"}
    ],
    "goals": "Become a UX designer",
    "time_commitment": "2-3 hours/day",
    "learning_style": "visual",
    "recommended_categories": ["Creativity & Arts", "Tech & Digital Innovation"]
  },
  "profile_embedding": [0.123, 0.456, ...],  // Vector embedding
  "next_steps": {
    "action": "explore_categories",
    "suggested_subcategories": [...]
  }
}
```

---

### `GET /api/v1/ai-profiling/profile`
**Purpose**: Get user's AI profile

**Response**:
```json
{
  "user_id": "uuid",
  "passions": [...],
  "skills": [...],
  "goals": "...",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

### `PUT /api/v1/ai-profiling/profile`
**Purpose**: Update AI profile (for re-profiling - Stage 6)

---

## 3. CATEGORIES & EXPLORATION (Stage 2)

### `GET /api/v1/categories`
**Purpose**: Get all main categories (22 categories)

**Response**:
```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "Creativity & Arts",
      "slug": "creativity-arts",
      "description": "...",
      "icon": "palette",
      "subcategory_count": 4
    },
    // ... 21 more categories
  ],
  "total": 22
}
```

---

### `GET /api/v1/categories/{category_id}/subcategories`
**Purpose**: Get subcategories for a main category

**Response**:
```json
{
  "category": {
    "id": "uuid",
    "name": "Creativity & Arts"
  },
  "subcategories": [
    {
      "id": "uuid",
      "name": "Visual Arts",
      "slug": "visual-arts",
      "description": "..."
    },
    // ... more subcategories
  ]
}
```

---

### `GET /api/v1/categories/search`
**Purpose**: Semantic search across categories using AI embeddings

**Query Parameters**:
- `q`: Search query
- `limit`: Number of results (default: 10)

**Example**: `GET /api/v1/categories/search?q=learn mobile design&limit=5`

**Response**:
```json
{
  "query": "learn mobile design",
  "results": [
    {
      "category": "Creativity & Arts",
      "subcategory": "Design & Media",
      "relevance_score": 0.89,
      "why_relevant": "Matches your interest in mobile and design"
    },
    // ... more results
  ]
}
```

---

## 4. OPPORTUNITIES (Stage 2)

### `GET /api/v1/opportunities`
**Purpose**: Get opportunities (courses, jobs, mentorships, workshops, groups)

**Query Parameters**:
- `type`: course | job | mentorship | workshop | group
- `subcategory_id`: Filter by subcategory
- `difficulty`: beginner | intermediate | advanced
- `is_paid`: true | false
- `page`: Page number
- `limit`: Results per page

**Example**: `GET /api/v1/opportunities?type=course&subcategory_id=uuid&difficulty=beginner`

**Response**:
```json
{
  "opportunities": [
    {
      "id": "uuid",
      "title": "UI Design Fundamentals",
      "description": "...",
      "opportunity_type": "course",
      "is_paid": true,
      "price": 49.99,
      "currency": "USD",
      "duration_minutes": 360,
      "difficulty_level": "beginner",
      "tags": ["figma", "ui-design", "mobile"],
      "rating": 4.7,
      "enrollment_count": 1523
    },
    // ... more opportunities
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "pages": 8
  }
}
```

---

### `GET /api/v1/opportunities/{opportunity_id}`
**Purpose**: Get opportunity details

---

### `GET /api/v1/opportunities/recommended`
**Purpose**: AI-powered opportunity recommendations based on user profile

**Response**:
```json
{
  "recommendations": [
    {
      "opportunity": { /* opportunity object */ },
      "match_score": 0.92,
      "reason": "Matches your interest in UI design and beginner skill level",
      "learning_path_fit": true
    },
    // ... more recommendations
  ]
}
```

---

### `POST /api/v1/opportunities/{opportunity_id}/enroll`
**Purpose**: Enroll in an opportunity (course/workshop/group)

**Response**:
```json
{
  "enrollment": {
    "id": "uuid",
    "opportunity_id": "uuid",
    "status": "enrolled",
    "enrolled_at": "2025-01-15T10:30:00Z"
  },
  "payment_required": true,
  "payment_url": "https://..." // For paid opportunities
}
```

---

## 5. MENTORS & MATCHING (Stage 2)

### `GET /api/v1/mentors`
**Purpose**: Browse mentors

**Query Parameters**:
- `category_id`: Filter by category
- `subcategory_id`: Filter by subcategory
- `skill`: Filter by skill
- `min_rating`: Minimum rating
- `max_hourly_rate`: Maximum rate
- `available_now`: true (mentors available today)
- `sort`: rating | rate | experience

**Response**:
```json
{
  "mentors": [
    {
      "id": "uuid",
      "user": {
        "full_name": "Sarah Johnson",
        "avatar_url": "...",
        "username": "sarahj"
      },
      "mentor_tier": "premium",
      "average_rating": 4.9,
      "total_reviews": 127,
      "total_sessions_completed": 340,
      "hourly_rate": 75.00,
      "skills_offered": ["UI Design", "Figma", "Design Systems"],
      "bio": "10+ years in product design at tech companies",
      "years_of_experience": 10,
      "is_verified": true,
      "next_available_slot": "2025-01-16T14:00:00Z"
    },
    // ... more mentors
  ]
}
```

---

### `GET /api/v1/mentors/{mentor_id}`
**Purpose**: Get mentor profile details

**Response**:
```json
{
  "mentor": { /* full mentor profile */ },
  "availability": {
    "timezone": "America/New_York",
    "slots": [
      {
        "date": "2025-01-16",
        "times": ["09:00", "10:00", "14:00", "15:00"]
      },
      // ... next 7 days
    ]
  },
  "reviews": [
    {
      "id": "uuid",
      "reviewer": {
        "username": "john_doe",
        "avatar_url": "..."
      },
      "rating": 5,
      "review_text": "Amazing session! Learned so much about Figma.",
      "created_at": "2025-01-10T15:30:00Z"
    },
    // ... more reviews
  ]
}
```

---

### `GET /api/v1/mentors/recommended`
**Purpose**: AI-matched mentors based on user profile

**Response**:
```json
{
  "matches": [
    {
      "mentor": { /* mentor object */ },
      "match_score": 0.94,
      "match_reasons": [
        "Expert in your passions: UI Design, Figma",
        "Teaching style matches your learning preference: Visual",
        "Compatible timezone",
        "High ratings from similar students"
      ],
      "common_skills": ["UI Design", "Prototyping"]
    },
    // ... more matches
  ]
}
```

---

### `GET /api/v1/mentors/proximity`
**Purpose**: Find mentors nearby (location-based - Stage 2 + Stage 6)

**Query Parameters**:
- `lat`: Latitude
- `lng`: Longitude
- `radius_km`: Search radius in kilometers

---

## 6. BOOKINGS & SESSIONS (Stage 3)

### `POST /api/v1/bookings/create`
**Purpose**: Book a mentorship session

**Request Body**:
```json
{
  "mentor_user_id": "uuid",
  "scheduled_at": "2025-01-16T14:00:00Z",
  "duration_minutes": 60,
  "timezone": "America/New_York",
  "mentee_notes": "I want to learn about design systems",
  "opportunity_id": "uuid"  // Optional: if booking for specific course
}
```

**Response**:
```json
{
  "booking": {
    "id": "uuid",
    "status": "pending_payment",
    "scheduled_at": "2025-01-16T14:00:00Z",
    "duration_minutes": 60,
    "amount": 75.00,
    "currency": "USD"
  },
  "payment": {
    "payment_intent_id": "pi_stripe_id",
    "client_secret": "secret_for_frontend",
    "amount": 75.00
  }
}
```

---

### `GET /api/v1/bookings`
**Purpose**: Get user's bookings

**Query Parameters**:
- `status`: scheduled | completed | cancelled
- `role`: mentee | mentor (filter by role)
- `upcoming`: true (only future sessions)

**Response**:
```json
{
  "bookings": [
    {
      "id": "uuid",
      "mentor": {
        "full_name": "Sarah Johnson",
        "avatar_url": "..."
      },
      "mentee": {
        "full_name": "John Doe",
        "avatar_url": "..."
      },
      "scheduled_at": "2025-01-16T14:00:00Z",
      "duration_minutes": 60,
      "status": "scheduled",
      "meeting_url": "https://daily.co/soosh-session-uuid",
      "meeting_id": "soosh-session-uuid"
    },
    // ... more bookings
  ]
}
```

---

### `GET /api/v1/bookings/{booking_id}`
**Purpose**: Get booking details

---

### `POST /api/v1/bookings/{booking_id}/join`
**Purpose**: Join video session (generates/returns meeting URL)

**Response**:
```json
{
  "meeting_url": "https://daily.co/soosh-session-uuid",
  "meeting_token": "token_for_auth",
  "starts_at": "2025-01-16T14:00:00Z",
  "can_join": true,
  "time_until_start_minutes": 5
}
```

---

### `POST /api/v1/bookings/{booking_id}/cancel`
**Purpose**: Cancel a booking

**Request Body**:
```json
{
  "cancellation_reason": "Schedule conflict"
}
```

**Response**:
```json
{
  "booking": {
    "id": "uuid",
    "status": "cancelled",
    "cancelled_at": "2025-01-15T10:30:00Z"
  },
  "refund": {
    "amount": 75.00,
    "status": "processing",
    "refund_id": "re_stripe_id"
  }
}
```

---

### `POST /api/v1/bookings/{booking_id}/complete`
**Purpose**: Mark session as completed (auto-called after session ends)

---

### `POST /api/v1/bookings/{booking_id}/review`
**Purpose**: Submit session review

**Request Body**:
```json
{
  "rating": 5,
  "review_text": "Excellent session! Very helpful.",
  "skills_learned": ["Design systems", "Figma components"]
}
```

---

## 7. PAYMENTS (Stage 3)

### `POST /api/v1/payments/create-intent`
**Purpose**: Create Stripe payment intent

**Request Body**:
```json
{
  "booking_id": "uuid",
  "amount": 75.00,
  "currency": "USD"
}
```

**Response**:
```json
{
  "payment_id": "uuid",
  "client_secret": "pi_secret_for_stripe",
  "amount": 75.00,
  "platform_fee": 11.25,
  "mentor_payout": 63.75
}
```

---

### `POST /api/v1/payments/confirm`
**Purpose**: Confirm payment completion

---

### `POST /api/v1/payments/webhook`
**Purpose**: Stripe webhook handler (internal)

---

### `GET /api/v1/payments/history`
**Purpose**: Get payment history

**Response**:
```json
{
  "payments": [
    {
      "id": "uuid",
      "amount": 75.00,
      "currency": "USD",
      "status": "completed",
      "booking": {
        "id": "uuid",
        "mentor_name": "Sarah Johnson"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "receipt_url": "https://..."
    },
    // ... more payments
  ]
}
```

---

### `GET /api/v1/payments/earnings`
**Purpose**: Get mentor earnings (Mid-Level, Experienced only)

**Response**:
```json
{
  "total_earnings": 2450.00,
  "pending_payout": 315.50,
  "lifetime_earnings": 18750.00,
  "this_month": 450.00,
  "earnings_by_month": [
    {"month": "2025-01", "amount": 450.00},
    // ... more months
  ]
}
```

---

## 8. LEARNING PATHS & PROGRESS (Stage 4)

### `GET /api/v1/learning/paths`
**Purpose**: Get user's learning paths

**Response**:
```json
{
  "learning_paths": [
    {
      "id": "uuid",
      "subcategory": {
        "id": "uuid",
        "name": "UI/UX Design",
        "category_name": "Creativity & Arts"
      },
      "current_step": 3,
      "total_steps": 8,
      "completion_percentage": 37.5,
      "milestones_completed": [
        {
          "step": 1,
          "title": "Design Fundamentals",
          "completed_at": "2025-01-10T10:00:00Z"
        },
        {
          "step": 2,
          "title": "Figma Basics",
          "completed_at": "2025-01-12T14:30:00Z"
        }
      ],
      "next_milestone": {
        "step": 3,
        "title": "Color Theory",
        "estimated_duration_hours": 4
      }
    },
    // ... more paths
  ]
}
```

---

### `POST /api/v1/learning/paths/create`
**Purpose**: Create new learning path

**Request Body**:
```json
{
  "subcategory_id": "uuid"
}
```

---

### `POST /api/v1/learning/paths/{path_id}/complete-milestone`
**Purpose**: Mark milestone as completed

**Request Body**:
```json
{
  "step": 3
}
```

**Response**:
```json
{
  "milestone": {
    "step": 3,
    "title": "Color Theory",
    "completed_at": "2025-01-15T10:30:00Z"
  },
  "points_earned": 50,
  "achievements_unlocked": [
    {
      "id": "uuid",
      "name": "Design Explorer",
      "description": "Complete 3 design milestones"
    }
  ],
  "next_milestone": { /* step 4 */ }
}
```

---

### `GET /api/v1/learning/progress`
**Purpose**: Get progress for all enrolled opportunities

**Response**:
```json
{
  "enrolled_courses": [
    {
      "opportunity": {
        "id": "uuid",
        "title": "UI Design Fundamentals"
      },
      "status": "in_progress",
      "completion_percentage": 45.0,
      "total_time_spent_minutes": 180,
      "last_accessed_at": "2025-01-15T09:00:00Z"
    },
    // ... more courses
  ]
}
```

---

### `GET /api/v1/learning/achievements`
**Purpose**: Get user achievements

**Response**:
```json
{
  "achievements": [
    {
      "id": "uuid",
      "name": "First Steps",
      "description": "Complete your first session",
      "icon_url": "...",
      "rarity": "common",
      "earned_at": "2025-01-10T15:00:00Z"
    },
    // ... more achievements
  ],
  "total_points": 1250,
  "level": 7,
  "next_level_points": 1500,
  "current_streak_days": 12,
  "longest_streak_days": 23
}
```

---

### `GET /api/v1/learning/certificates`
**Purpose**: Get earned certificates

**Response**:
```json
{
  "certificates": [
    {
      "id": "uuid",
      "opportunity_title": "UI Design Fundamentals",
      "issued_at": "2025-01-14T10:00:00Z",
      "certificate_url": "https://...",
      "verification_code": "SOOSH-2025-ABC123"
    },
    // ... more certificates
  ]
}
```

---

## 9. NOTIFICATIONS (Stage 4)

### `GET /api/v1/notifications`
**Purpose**: Get user notifications

**Query Parameters**:
- `unread`: true (only unread)
- `type`: session_reminder | booking_confirmed | payment_success | etc.
- `limit`: Number of results

**Response**:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "session_reminder",
      "title": "Session in 1 hour",
      "message": "Your session with Sarah Johnson starts at 2:00 PM",
      "action_url": "soosh://booking/uuid",
      "is_read": false,
      "created_at": "2025-01-16T13:00:00Z"
    },
    // ... more notifications
  ],
  "unread_count": 5
}
```

---

### `PUT /api/v1/notifications/{notification_id}/read`
**Purpose**: Mark notification as read

---

### `PUT /api/v1/notifications/read-all`
**Purpose**: Mark all notifications as read

---

### `GET /api/v1/notifications/settings`
**Purpose**: Get notification preferences

**Response**:
```json
{
  "push_enabled": true,
  "email_enabled": true,
  "sms_enabled": false,
  "notification_types": {
    "session_reminder": true,
    "booking_confirmed": true,
    "payment_success": true,
    "message_received": true,
    "achievement_unlocked": true,
    "course_update": false
  }
}
```

---

### `PUT /api/v1/notifications/settings`
**Purpose**: Update notification preferences

---

## 10. MESSAGES & COMMUNICATION (Stage 4 + Stage 6)

### `GET /api/v1/messages/conversations`
**Purpose**: Get message conversations

**Response**:
```json
{
  "conversations": [
    {
      "participant": {
        "id": "uuid",
        "full_name": "Sarah Johnson",
        "avatar_url": "...",
        "user_type": "experienced"
      },
      "last_message": {
        "message_text": "Looking forward to our session!",
        "created_at": "2025-01-15T10:30:00Z",
        "is_read": true
      },
      "unread_count": 2
    },
    // ... more conversations
  ]
}
```

---

### `GET /api/v1/messages/conversation/{user_id}`
**Purpose**: Get messages with specific user

**Response**:
```json
{
  "participant": {
    "id": "uuid",
    "full_name": "Sarah Johnson"
  },
  "messages": [
    {
      "id": "uuid",
      "sender_user_id": "uuid",
      "recipient_user_id": "uuid",
      "message_text": "Hi! Can we discuss design systems in our session?",
      "ai_generated": false,
      "is_read": true,
      "created_at": "2025-01-15T09:00:00Z"
    },
    // ... more messages
  ]
}
```

---

### `POST /api/v1/messages/send`
**Purpose**: Send message

**Request Body**:
```json
{
  "recipient_user_id": "uuid",
  "message_text": "Looking forward to our session!"
}
```

**Response**:
```json
{
  "message": {
    "id": "uuid",
    "created_at": "2025-01-15T10:30:00Z",
    "is_delivered": true
  }
}
```

---

### `WebSocket /api/v1/messages/ws/{user_id}`
**Purpose**: Real-time messaging WebSocket connection

**Messages**:
```json
// Receive new message
{
  "type": "new_message",
  "message": { /* message object */ }
}

// Typing indicator
{
  "type": "typing",
  "user_id": "uuid",
  "username": "sarah_j"
}
```

---

## 11. AI AGENT (Stage 1-6 - Disabled Users)

### `POST /api/v1/ai-agent/create`
**Purpose**: Create AI agent for disabled user

**Request Body**:
```json
{
  "agent_name": "Soosh Assistant",
  "agent_personality": {
    "tone": "friendly",
    "verbosity": "concise"
  },
  "voice_id": "default",
  "language": "en-US",
  "auto_schedule_enabled": true,
  "auto_respond_messages": true,
  "auto_manage_calendar": true
}
```

---

### `GET /api/v1/ai-agent/profile`
**Purpose**: Get AI agent profile

---

### `PUT /api/v1/ai-agent/profile`
**Purpose**: Update AI agent settings

---

### `POST /api/v1/ai-agent/schedule-session`
**Purpose**: AI auto-schedules mentorship session

**Request Body**:
```json
{
  "mentor_id": "uuid",
  "preferred_time_range": "afternoon",  // morning, afternoon, evening
  "preferred_days": ["monday", "wednesday", "friday"],
  "duration_minutes": 60
}
```

**Response**:
```json
{
  "booking": { /* booking object */ },
  "ai_decision": {
    "selected_time": "2025-01-16T14:00:00Z",
    "reason": "Based on your preferences for afternoon sessions and mentor availability"
  },
  "voice_confirmation_sent": true
}
```

---

### `POST /api/v1/ai-agent/respond-message`
**Purpose**: AI responds to message on behalf of user

**Request Body**:
```json
{
  "message_id": "uuid",
  "auto_respond": true
}
```

---

### `GET /api/v1/ai-agent/actions-log`
**Purpose**: Get AI agent action history

**Response**:
```json
{
  "actions": [
    {
      "id": "uuid",
      "action_type": "scheduled_booking",
      "action_details": {
        "mentor_name": "Sarah Johnson",
        "scheduled_at": "2025-01-16T14:00:00Z"
      },
      "success": true,
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": "uuid",
      "action_type": "sent_message",
      "action_details": {
        "recipient": "John Mentor",
        "message": "Thank you for your help!"
      },
      "success": true,
      "created_at": "2025-01-15T09:00:00Z"
    },
    // ... more actions
  ]
}
```

---

### `POST /api/v1/ai-agent/voice-command`
**Purpose**: Process voice command from disabled user

**Request Body**:
```json
{
  "audio_file": "base64_encoded_audio"
}
```

**Response**:
```json
{
  "transcription": "Schedule a session with Sarah next week",
  "intent": "schedule_session",
  "action_taken": {
    "type": "scheduled_booking",
    "booking_id": "uuid"
  },
  "response_text": "I've scheduled a session with Sarah for Tuesday at 2 PM",
  "response_audio_url": "https://..."  // TTS audio
}
```

---

## 12. PORTFOLIO & RESUME (Stage 5)

### `POST /api/v1/users/resume/generate`
**Purpose**: AI-generate resume from profile

**Response**:
```json
{
  "resume": {
    "id": "uuid",
    "pdf_url": "https://...",
    "json_data": {
      "summary": "Aspiring UI/UX designer with...",
      "skills": ["Figma", "UI Design", "Prototyping"],
      "experience": [
        {
          "title": "Completed UI Design Fundamentals",
          "type": "course",
          "duration": "2 months"
        }
      ],
      "achievements": [...]
    },
    "generated_at": "2025-01-15T10:30:00Z"
  }
}
```

---

### `POST /api/v1/users/portfolio/create`
**Purpose**: Create portfolio page

**Request Body**:
```json
{
  "bio": "...",
  "featured_projects": ["project_id_1", "project_id_2"],
  "custom_url": "johndoe"
}
```

---

### `GET /api/v1/users/portfolio/{username}`
**Purpose**: Get public portfolio

---

### `POST /api/v1/users/portfolio/share`
**Purpose**: Share portfolio on social media (AI-generated posts)

**Request Body**:
```json
{
  "platforms": ["linkedin", "twitter"],
  "auto_generate_caption": true
}
```

**Response**:
```json
{
  "linkedin": {
    "post_text": "Excited to share my learning journey...",
    "post_url": "https://linkedin.com/...",
    "posted": true
  },
  "twitter": {
    "post_text": "Just completed UI Design course! 🎨",
    "post_url": "https://twitter.com/...",
    "posted": true
  }
}
```

---

## 13. COMMUNITY & SOCIAL (Stage 6)

### `GET /api/v1/community/groups`
**Purpose**: Get community groups

**Response**:
```json
{
  "groups": [
    {
      "id": "uuid",
      "name": "UI Design Enthusiasts",
      "description": "...",
      "member_count": 1250,
      "category": "Creativity & Arts",
      "is_member": false
    },
    // ... more groups
  ]
}
```

---

### `POST /api/v1/community/groups/{group_id}/join`
**Purpose**: Join community group

---

### `GET /api/v1/community/groups/{group_id}/posts`
**Purpose**: Get group posts/discussions

---

### `POST /api/v1/community/groups/{group_id}/posts`
**Purpose**: Create post in group

---

### `GET /api/v1/community/events`
**Purpose**: Get community events (workshops, meetups)

---

## 14. ANALYTICS & INSIGHTS (Stage 6)

### `GET /api/v1/analytics/dashboard`
**Purpose**: Get user analytics dashboard

**Response**:
```json
{
  "overview": {
    "total_sessions": 12,
    "total_hours_learned": 24,
    "courses_completed": 3,
    "current_streak_days": 12,
    "total_points": 1250,
    "level": 7
  },
  "learning_progress": {
    "active_paths": 2,
    "completion_rate": 45.5,
    "average_session_rating": 4.8
  },
  "earnings": {  // For mentors
    "this_month": 450.00,
    "total_sessions_given": 28,
    "average_rating": 4.9
  },
  "recommendations": {
    "next_steps": [
      "Complete Color Theory milestone",
      "Book session with Sarah Johnson",
      "Join UI Design community group"
    ]
  }
}
```

---

### `GET /api/v1/analytics/activity`
**Purpose**: Get activity timeline

**Response**:
```json
{
  "activities": [
    {
      "type": "session_completed",
      "data": {
        "mentor_name": "Sarah Johnson",
        "topic": "Design Systems"
      },
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "type": "milestone_completed",
      "data": {
        "milestone": "Figma Basics",
        "points_earned": 50
      },
      "timestamp": "2025-01-14T14:00:00Z"
    },
    // ... more activities
  ]
}
```

---

### `GET /api/v1/analytics/mentor-stats`
**Purpose**: Mentor performance analytics (Experienced users)

---

## 15. USERS & PROFILE MANAGEMENT

### `GET /api/v1/users/me`
**Purpose**: Get current user profile

---

### `PUT /api/v1/users/me`
**Purpose**: Update user profile

**Request Body**:
```json
{
  "full_name": "John Doe",
  "bio": "Aspiring UI designer",
  "location": {
    "city": "San Francisco",
    "country": "USA",
    "lat": 37.7749,
    "lng": -122.4194
  },
  "timezone": "America/Los_Angeles"
}
```

---

### `POST /api/v1/users/me/avatar`
**Purpose**: Upload profile picture

**Request**: Multipart form data with image file

---

### `POST /api/v1/users/upgrade-to-mentor`
**Purpose**: Upgrade account to mentor (Mid-Level/Experienced)

**Request Body**:
```json
{
  "user_type": "mid_level",  // or experienced
  "mentor_bio": "...",
  "skills_offered": ["UI Design", "Figma"],
  "expertise_categories": [
    {
      "category_id": "uuid",
      "subcategory_ids": ["uuid1", "uuid2"]
    }
  ],
  "hourly_rate": 50.00,
  "portfolio_url": "...",
  "linkedin_url": "..."
}
```

---

### `PUT /api/v1/users/switch-mode`
**Purpose**: Switch between learner/mentor mode (Experienced users)

**Request Body**:
```json
{
  "mode": "mentor"  // or "learner"
}
```

---

## WEBSOCKET ENDPOINTS

### `WebSocket /api/v1/ws/notifications`
**Purpose**: Real-time notifications

---

### `WebSocket /api/v1/ws/messages/{user_id}`
**Purpose**: Real-time messaging

---

### `WebSocket /api/v1/ws/session/{booking_id}`
**Purpose**: Real-time session updates (session started, ended, etc.)

---

## ERROR RESPONSES

All endpoints follow consistent error format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "specific error details"
  }
}
```

**Common Error Codes**:
- `AUTH_ERROR` (401)
- `FORBIDDEN` (403)
- `USER_NOT_FOUND` (404)
- `VALIDATION_ERROR` (422)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_SERVER_ERROR` (500)

---

## AUTHENTICATION

All endpoints (except `/auth/*` and public endpoints) require JWT token:

**Header**:
```
Authorization: Bearer <access_token>
```

**Token Refresh**:
When access token expires, use `/auth/refresh-token` endpoint.

---

## PAGINATION

List endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response Headers**:
- `X-Total-Count`: Total number of items
- `X-Page`: Current page
- `X-Page-Size`: Items per page

---

## RATE LIMITING

**Limits**:
- 60 requests per minute
- 1000 requests per hour

**Headers**:
- `X-RateLimit-Limit`: Requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time until limit resets (Unix timestamp)

---

## VERSIONING

Current version: **v1**

Base URL: `/api/v1`

Future versions will use `/api/v2`, etc.

---

**End of API Documentation**
