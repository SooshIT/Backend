-- ============================================================================
-- SOOSH PLATFORM - POSTGRESQL DATABASE SCHEMA
-- Version: 1.0
-- PostgreSQL 16+ with pgvector, PostGIS extensions
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- ENUMS - Type Definitions
-- ============================================================================

CREATE TYPE user_type_enum AS ENUM (
    'beginner',
    'mid_level',
    'experienced',
    'stay_at_home',
    'disabled'
);

CREATE TYPE user_status_enum AS ENUM (
    'pending_verification',
    'active',
    'suspended',
    'inactive'
);

CREATE TYPE mentor_tier_enum AS ENUM (
    'basic',
    'premium',
    'expert'
);

CREATE TYPE session_status_enum AS ENUM (
    'scheduled',
    'in_progress',
    'completed',
    'cancelled',
    'no_show'
);

CREATE TYPE opportunity_type_enum AS ENUM (
    'course',
    'job',
    'mentorship',
    'workshop',
    'group'
);

CREATE TYPE payment_status_enum AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'refunded'
);

CREATE TYPE notification_type_enum AS ENUM (
    'session_reminder',
    'booking_confirmed',
    'payment_success',
    'message_received',
    'achievement_unlocked',
    'course_update',
    'system_alert'
);

CREATE TYPE ai_automation_level_enum AS ENUM (
    'none',
    'partial',
    'full'
);

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users Table (All 5 types)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL for OAuth users

    -- User Classification
    user_type user_type_enum NOT NULL DEFAULT 'beginner',
    user_status user_status_enum NOT NULL DEFAULT 'pending_verification',

    -- Profile Information
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    date_of_birth DATE,
    gender VARCHAR(20),

    -- Location (for proximity features)
    country VARCHAR(100),
    city VARCHAR(100),
    location GEOGRAPHY(POINT, 4326), -- PostGIS for geospatial queries
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Mentor-specific fields
    is_mentor_enabled BOOLEAN DEFAULT FALSE,
    mentor_tier mentor_tier_enum,
    is_verified_mentor BOOLEAN DEFAULT FALSE,
    hourly_rate DECIMAL(10, 2),
    mentor_bio TEXT,
    years_of_experience INTEGER,

    -- Dual-mode (Experienced users can also learn)
    dual_mode_enabled BOOLEAN DEFAULT FALSE,

    -- AI & Accessibility (Disabled users)
    ai_automation_level ai_automation_level_enum DEFAULT 'none',
    accessibility_preferences JSONB, -- {voice_only, screen_reader, font_size, etc}
    ai_agent_id UUID, -- Links to dedicated AI agent

    -- Authentication & Security
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50), -- 'google', 'apple', 'linkedin'
    oauth_id VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    onboarding_completed BOOLEAN DEFAULT FALSE,

    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_mentor_enabled ON users(is_mentor_enabled) WHERE is_mentor_enabled = TRUE;
CREATE INDEX idx_users_location ON users USING GIST(location);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- AI PROFILING & EMBEDDINGS
-- ============================================================================

-- AI Profile Data (from onboarding)
CREATE TABLE user_ai_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Profiling responses
    passions JSONB, -- [{category: "Design", subcategory: "UI/UX", confidence: 0.85}]
    skills JSONB, -- [{skill: "Figma", level: "intermediate", verified: false}]
    goals TEXT,
    time_commitment VARCHAR(50), -- "1-2 hours/day", "weekends only"
    learning_style VARCHAR(50), -- "visual", "hands-on", "theoretical"

    -- Vector embeddings for AI matching
    profile_embedding VECTOR(1536), -- OpenAI embedding dimension
    interests_embedding VECTOR(1536),

    -- AI conversation history
    onboarding_transcript JSONB, -- Full conversation log

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

-- Vector similarity index for fast matching
CREATE INDEX idx_ai_profiles_embedding ON user_ai_profiles
    USING ivfflat (profile_embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- CATEGORIES & OPPORTUNITIES
-- ============================================================================

-- Main Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subcategories
CREATE TABLE subcategories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    embedding VECTOR(1536), -- For semantic search
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(category_id, slug)
);

CREATE INDEX idx_subcategories_category ON subcategories(category_id);
CREATE INDEX idx_subcategories_embedding ON subcategories
    USING ivfflat (embedding vector_cosine_ops);

-- Opportunities (Courses, Jobs, Mentorships, Workshops)
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subcategory_id UUID NOT NULL REFERENCES subcategories(id),
    created_by_user_id UUID REFERENCES users(id), -- NULL for platform-generated

    title VARCHAR(255) NOT NULL,
    description TEXT,
    opportunity_type opportunity_type_enum NOT NULL,

    -- Pricing
    is_paid BOOLEAN DEFAULT FALSE,
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Content
    content_url TEXT, -- Course link, job posting, etc
    duration_minutes INTEGER,
    difficulty_level VARCHAR(20), -- "beginner", "intermediate", "advanced"

    -- Metadata
    tags JSONB, -- ["python", "data-science", "ml"]
    requirements JSONB, -- Prerequisites
    learning_outcomes JSONB,

    -- Vector embedding for semantic search
    embedding VECTOR(1536),

    -- Visibility
    is_active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_opportunities_subcategory ON opportunities(subcategory_id);
CREATE INDEX idx_opportunities_type ON opportunities(opportunity_type);
CREATE INDEX idx_opportunities_embedding ON opportunities
    USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- MENTORSHIP SYSTEM
-- ============================================================================

-- Mentor Profiles (Extended info for mentors)
CREATE TABLE mentor_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Expertise
    expertise_categories JSONB, -- [{"category_id": "...", "subcategory_ids": [...]}]
    skills_offered JSONB, -- ["UI Design", "Figma", "Prototyping"]

    -- Availability
    available_hours JSONB, -- {"monday": ["09:00-12:00", "14:00-18:00"], ...}
    timezone VARCHAR(50),
    max_sessions_per_week INTEGER DEFAULT 10,

    -- Ratings & Reviews
    average_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    total_sessions_completed INTEGER DEFAULT 0,

    -- Verification
    portfolio_url TEXT,
    linkedin_url TEXT,
    verification_documents JSONB, -- Links to uploaded docs
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Settings
    auto_accept_bookings BOOLEAN DEFAULT FALSE, -- For AI disabled users
    session_buffer_minutes INTEGER DEFAULT 15, -- Gap between sessions

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE INDEX idx_mentor_profiles_rating ON mentor_profiles(average_rating DESC);
CREATE INDEX idx_mentor_profiles_user ON mentor_profiles(user_id);

-- ============================================================================
-- BOOKING & SESSIONS
-- ============================================================================

-- Session Bookings
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Participants
    mentee_user_id UUID NOT NULL REFERENCES users(id),
    mentor_user_id UUID NOT NULL REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id), -- NULL for direct mentorship

    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    timezone VARCHAR(50),

    -- Status
    status session_status_enum DEFAULT 'scheduled',

    -- Meeting Info
    meeting_url TEXT, -- Zoom/Google Meet link
    meeting_id VARCHAR(255),
    meeting_password VARCHAR(255),

    -- AI Assistance (for disabled users)
    ai_scheduled BOOLEAN DEFAULT FALSE, -- Was this auto-scheduled by AI?
    ai_reminder_sent BOOLEAN DEFAULT FALSE,

    -- Notes
    mentee_notes TEXT, -- Questions/topics
    mentor_notes TEXT, -- Session summary

    -- Payment
    payment_id UUID, -- Links to payments table

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,

    CHECK (mentee_user_id != mentor_user_id)
);

CREATE INDEX idx_bookings_mentee ON bookings(mentee_user_id);
CREATE INDEX idx_bookings_mentor ON bookings(mentor_user_id);
CREATE INDEX idx_bookings_scheduled_at ON bookings(scheduled_at);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Session Feedback & Reviews
CREATE TABLE session_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_user_id UUID NOT NULL REFERENCES users(id),
    reviewed_user_id UUID NOT NULL REFERENCES users(id), -- Mentor being reviewed

    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    skills_learned JSONB, -- ["Figma shortcuts", "Design thinking"]

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(booking_id, reviewer_user_id)
);

CREATE INDEX idx_session_reviews_reviewed_user ON session_reviews(reviewed_user_id);

-- ============================================================================
-- PAYMENTS & TRANSACTIONS
-- ============================================================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Parties
    payer_user_id UUID NOT NULL REFERENCES users(id),
    payee_user_id UUID REFERENCES users(id), -- Mentor receiving payment

    -- Payment Details
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    platform_fee DECIMAL(10, 2), -- Soosh commission
    mentor_payout DECIMAL(10, 2), -- Amount mentor receives

    -- Payment Gateway
    payment_provider VARCHAR(50), -- 'stripe', 'paypal'
    payment_intent_id VARCHAR(255), -- Stripe/PayPal transaction ID
    status payment_status_enum DEFAULT 'pending',

    -- References
    booking_id UUID REFERENCES bookings(id),
    opportunity_id UUID REFERENCES opportunities(id),

    -- Metadata
    payment_method VARCHAR(50), -- 'card', 'upi', 'wallet'
    receipt_url TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_payments_payer ON payments(payer_user_id);
CREATE INDEX idx_payments_payee ON payments(payee_user_id);
CREATE INDEX idx_payments_status ON payments(status);

-- ============================================================================
-- LEARNING PATHS & PROGRESS
-- ============================================================================

-- Learning Paths (for Beginners & Mid-Level)
CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subcategory_id UUID NOT NULL REFERENCES subcategories(id),

    -- Progress
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER,
    completion_percentage DECIMAL(5, 2) DEFAULT 0.00,

    -- Milestones
    milestones_completed JSONB, -- [{step: 1, completed_at: "...", title: "..."}]

    -- AI-generated recommendations
    recommended_opportunities JSONB, -- AI-suggested next steps

    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_paths_user ON learning_paths(user_id);
CREATE INDEX idx_learning_paths_subcategory ON learning_paths(subcategory_id);

-- User Progress (Course enrollments, completions)
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    opportunity_id UUID NOT NULL REFERENCES opportunities(id),

    -- Progress
    status VARCHAR(50) DEFAULT 'enrolled', -- 'enrolled', 'in_progress', 'completed'
    completion_percentage DECIMAL(5, 2) DEFAULT 0.00,

    -- Time tracking
    total_time_spent_minutes INTEGER DEFAULT 0,

    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, opportunity_id)
);

CREATE INDEX idx_user_progress_user ON user_progress(user_id);

-- ============================================================================
-- GAMIFICATION SYSTEM
-- ============================================================================

-- Achievements & Badges
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20), -- 'common', 'rare', 'epic', 'legendary'
    criteria JSONB, -- {type: "sessions_completed", count: 10}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Achievements
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id),

    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, achievement_id)
);

-- Leaderboard / Points
CREATE TABLE user_points (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NOTIFICATIONS & COMMUNICATIONS
-- ============================================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    notification_type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Links
    action_url TEXT, -- Deep link to relevant screen
    reference_id UUID, -- Booking ID, payment ID, etc

    -- Delivery
    is_read BOOLEAN DEFAULT FALSE,
    is_push_sent BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    is_voice_sent BOOLEAN DEFAULT FALSE, -- For disabled users

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Direct Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    sender_user_id UUID NOT NULL REFERENCES users(id),
    recipient_user_id UUID NOT NULL REFERENCES users(id),

    message_text TEXT NOT NULL,

    -- AI-generated (for disabled users)
    ai_generated BOOLEAN DEFAULT FALSE,

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CHECK (sender_user_id != recipient_user_id)
);

CREATE INDEX idx_messages_sender ON messages(sender_user_id);
CREATE INDEX idx_messages_recipient ON messages(recipient_user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- ============================================================================
-- AI AGENT SYSTEM (For Disabled Users)
-- ============================================================================

CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    agent_name VARCHAR(100) DEFAULT 'Soosh Assistant',
    agent_personality JSONB, -- {tone: "friendly", verbosity: "concise"}

    -- Automation settings
    auto_schedule_enabled BOOLEAN DEFAULT TRUE,
    auto_respond_messages BOOLEAN DEFAULT TRUE,
    auto_manage_calendar BOOLEAN DEFAULT TRUE,

    -- Voice preferences
    voice_id VARCHAR(100), -- TTS voice ID
    language VARCHAR(10) DEFAULT 'en-US',

    -- AI memory/context
    conversation_history JSONB,
    user_preferences JSONB, -- Learned preferences

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

-- AI Actions Log (for transparency)
CREATE TABLE ai_actions_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ai_agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),

    action_type VARCHAR(50), -- 'scheduled_booking', 'sent_message', 'updated_profile'
    action_details JSONB,
    success BOOLEAN,
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_actions_agent ON ai_actions_log(ai_agent_id);
CREATE INDEX idx_ai_actions_created_at ON ai_actions_log(created_at DESC);

-- ============================================================================
-- ANALYTICS & RECOMMENDATIONS
-- ============================================================================

-- User Activity Tracking
CREATE TABLE user_activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    activity_type VARCHAR(100), -- 'viewed_opportunity', 'searched', 'booked_session'
    activity_data JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partitioned by month for scalability
CREATE INDEX idx_activity_logs_user_time ON user_activity_logs(user_id, created_at DESC);

-- AI Recommendations Cache
CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    recommendation_type VARCHAR(50), -- 'mentor', 'course', 'opportunity'
    recommended_items JSONB, -- [{id, score, reason}]

    -- Embeddings for similarity
    query_embedding VECTOR(1536),

    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- Cache expiry

    UNIQUE(user_id, recommendation_type)
);

CREATE INDEX idx_recommendations_user ON ai_recommendations(user_id);
CREATE INDEX idx_recommendations_expires ON ai_recommendations(expires_at);

-- ============================================================================
-- TRIGGERS - Auto-update timestamps
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_profiles_updated_at BEFORE UPDATE ON user_ai_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS - Useful queries
-- ============================================================================

-- Active Mentors with availability
CREATE VIEW active_mentors AS
SELECT
    u.id,
    u.username,
    u.full_name,
    u.avatar_url,
    mp.average_rating,
    mp.total_reviews,
    mp.hourly_rate,
    mp.expertise_categories,
    u.location,
    u.user_type
FROM users u
JOIN mentor_profiles mp ON u.id = mp.user_id
WHERE u.is_mentor_enabled = TRUE
    AND u.user_status = 'active'
    AND u.deleted_at IS NULL;

-- User Learning Summary
CREATE VIEW user_learning_summary AS
SELECT
    u.id AS user_id,
    u.full_name,
    u.user_type,
    COUNT(DISTINCT lp.id) AS active_learning_paths,
    COUNT(DISTINCT up.id) AS enrolled_courses,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(points.total_points, 0) AS total_points,
    COALESCE(points.level, 1) AS user_level
FROM users u
LEFT JOIN learning_paths lp ON u.id = lp.user_id AND lp.completed_at IS NULL
LEFT JOIN user_progress up ON u.id = up.user_id
LEFT JOIN bookings b ON u.id = b.mentee_user_id
LEFT JOIN user_points points ON u.id = points.user_id
GROUP BY u.id, u.full_name, u.user_type, points.total_points, points.level;

-- ============================================================================
-- SEED DATA - Initial categories (matches your AppData.ts)
-- ============================================================================

-- Insert main categories (sample)
INSERT INTO categories (name, slug, description, display_order) VALUES
('Creativity & Arts', 'creativity-arts', 'Explore visual arts, music, writing and design', 1),
('Education & Tutoring', 'education-tutoring', 'Academic subjects, test prep and language learning', 2),
('Tech & Digital Innovation', 'tech-innovation', 'Programming, AI, data science and digital skills', 3),
('Lifestyle & Wellness', 'lifestyle-wellness', 'Fitness, mental health, nutrition and wellbeing', 4),
('Entrepreneurship & Side Hustles', 'entrepreneurship', 'Freelancing, startups and business opportunities', 5);

-- ============================================================================
-- PERFORMANCE OPTIMIZATIONS
-- ============================================================================

-- Partitioning for large tables (example for activity logs)
-- CREATE TABLE user_activity_logs_2025_01 PARTITION OF user_activity_logs
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Materialized view for leaderboard (refresh periodically)
-- CREATE MATERIALIZED VIEW leaderboard AS
-- SELECT user_id, total_points, level, ROW_NUMBER() OVER (ORDER BY total_points DESC) as rank
-- FROM user_points
-- ORDER BY total_points DESC
-- LIMIT 100;

-- ============================================================================
-- SECURITY - Row Level Security (RLS) examples
-- ============================================================================

-- Enable RLS on sensitive tables
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY users_select_policy ON users
--     FOR SELECT USING (id = current_user_id() OR is_public_profile(id));

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
