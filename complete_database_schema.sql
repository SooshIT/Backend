-- ============================================================================
-- SOOSH PLATFORM - COMPLETE POSTGRESQL DATABASE SCHEMA
-- Version: 1.0 - Merged and Complete
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

DO $$ BEGIN
    CREATE TYPE user_type_enum AS ENUM (
        'beginner',
        'mid_level',
        'experienced',
        'stay_at_home',
        'disabled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_status_enum AS ENUM (
        'pending_verification',
        'active',
        'suspended',
        'inactive'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE mentor_tier_enum AS ENUM (
        'basic',
        'premium',
        'expert'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE session_status_enum AS ENUM (
        'scheduled',
        'in_progress',
        'completed',
        'cancelled',
        'no_show'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE opportunity_type_enum AS ENUM (
        'COURSE',
        'JOB',
        'MENTORSHIP',
        'WORKSHOP',
        'GIG',
        'course',
        'job',
        'mentorship',
        'workshop',
        'group'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE difficulty_level_enum AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status_enum AS ENUM (
        'pending',
        'processing',
        'completed',
        'failed',
        'refunded'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_type_enum AS ENUM (
        'like',
        'comment',
        'reply',
        'mention',
        'follow',
        'opportunity',
        'booking',
        'message',
        'achievement',
        'system',
        'session_reminder',
        'booking_confirmed',
        'payment_success',
        'message_received',
        'achievement_unlocked',
        'course_update',
        'system_alert'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE post_type_enum AS ENUM (
        'achievement',
        'project',
        'article',
        'question',
        'discussion',
        'resource'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE post_visibility_enum AS ENUM (
        'public',
        'connections',
        'private'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ai_automation_level_enum AS ENUM (
        'none',
        'partial',
        'full'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users Table (All 5 types)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255),

    -- User Classification
    user_type user_type_enum NOT NULL DEFAULT 'beginner',
    user_status user_status_enum NOT NULL DEFAULT 'pending_verification',

    -- Profile Information
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    date_of_birth DATE,
    gender VARCHAR(20),

    -- Location
    country VARCHAR(100),
    city VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Mentor-specific fields
    is_mentor_enabled BOOLEAN DEFAULT FALSE,
    mentor_tier mentor_tier_enum,
    is_verified_mentor BOOLEAN DEFAULT FALSE,
    hourly_rate DECIMAL(10, 2),
    mentor_bio TEXT,
    years_of_experience INTEGER,

    -- Dual-mode
    dual_mode_enabled BOOLEAN DEFAULT FALSE,

    -- AI & Accessibility
    ai_automation_level ai_automation_level_enum DEFAULT 'none',
    accessibility_preferences JSONB,
    ai_agent_id UUID,

    -- Authentication & Security
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    onboarding_completed BOOLEAN DEFAULT FALSE,

    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_mentor_enabled ON users(is_mentor_enabled) WHERE is_mentor_enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_location ON users USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================================================
-- AI PROFILING & EMBEDDINGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_ai_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    passions JSONB,
    skills JSONB,
    goals TEXT,
    time_commitment VARCHAR(50),
    learning_style VARCHAR(50),

    profile_embedding VECTOR(1536),
    interests_embedding VECTOR(1536),

    onboarding_transcript JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_profiles_embedding ON user_ai_profiles
    USING ivfflat (profile_embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- CATEGORIES & OPPORTUNITIES
-- ============================================================================

CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subcategories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    embedding VECTOR(1536),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(category_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id);
CREATE INDEX IF NOT EXISTS idx_subcategories_slug ON subcategories(slug);
CREATE INDEX IF NOT EXISTS idx_subcategories_active ON subcategories(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_subcategories_embedding ON subcategories
    USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subcategory_id UUID REFERENCES subcategories(id),
    category_id UUID REFERENCES categories(id),

    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    opportunity_type opportunity_type_enum NOT NULL DEFAULT 'COURSE',
    difficulty_level difficulty_level_enum DEFAULT 'BEGINNER',

    -- Duration and schedule
    duration_hours INTEGER DEFAULT 0,
    duration_minutes INTEGER,
    duration_weeks INTEGER,
    start_date TIMESTAMP,
    end_date TIMESTAMP,

    -- Pricing
    price DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    is_free BOOLEAN DEFAULT false,
    is_paid BOOLEAN DEFAULT FALSE,

    -- Media
    thumbnail_url VARCHAR(1000),
    video_url VARCHAR(1000),
    content_url TEXT,
    images TEXT[],

    -- Skills and requirements
    skills_required TEXT[],
    skills_gained TEXT[],
    prerequisites TEXT[],
    tags JSONB,
    requirements JSONB,
    learning_outcomes JSONB,

    -- Location
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT true,
    is_onsite BOOLEAN DEFAULT false,

    -- Status and metrics
    is_active BOOLEAN DEFAULT TRUE,
    is_published BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT false,
    featured BOOLEAN DEFAULT FALSE,
    views_count INTEGER DEFAULT 0,
    enrollments_count INTEGER DEFAULT 0,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,

    -- Vector embedding
    embedding VECTOR(1536),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_opportunities_creator ON opportunities(creator_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities(category_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_subcategory ON opportunities(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_type ON opportunities(opportunity_type);
CREATE INDEX IF NOT EXISTS idx_opportunities_active ON opportunities(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_opportunities_published ON opportunities(is_published) WHERE is_published = true;
CREATE INDEX IF NOT EXISTS idx_opportunities_featured ON opportunities(is_featured) WHERE is_featured = true;
CREATE INDEX IF NOT EXISTS idx_opportunities_embedding ON opportunities
    USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- SOCIAL POSTS SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    post_type post_type_enum NOT NULL DEFAULT 'discussion',
    title VARCHAR(500),
    content TEXT NOT NULL,
    media_urls TEXT[],
    tags TEXT[],

    category_id UUID REFERENCES categories(id),
    subcategory_id UUID REFERENCES subcategories(id),

    visibility post_visibility_enum NOT NULL DEFAULT 'public',
    is_pinned BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,

    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,

    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_posts_type ON posts(post_type) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published_at DESC) WHERE is_deleted = false AND published_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_visibility ON posts(visibility) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_posts_tags ON posts USING GIN(tags) WHERE is_deleted = false;

CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(post_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_post_likes_post ON post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_user ON post_likes(user_id);

CREATE TABLE IF NOT EXISTS post_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_comment_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,

    content TEXT NOT NULL,
    media_urls TEXT[],

    likes_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_post_comments_post ON post_comments(post_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_post_comments_author ON post_comments(author_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_post_comments_parent ON post_comments(parent_comment_id) WHERE is_deleted = false;

-- ============================================================================
-- MENTORSHIP SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS mentor_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    expertise_categories JSONB,
    skills_offered JSONB,

    available_hours JSONB,
    timezone VARCHAR(50),
    max_sessions_per_week INTEGER DEFAULT 10,

    average_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    total_sessions_completed INTEGER DEFAULT 0,

    portfolio_url TEXT,
    linkedin_url TEXT,
    verification_documents JSONB,
    verified_at TIMESTAMP WITH TIME ZONE,

    auto_accept_bookings BOOLEAN DEFAULT FALSE,
    session_buffer_minutes INTEGER DEFAULT 15,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_mentor_profiles_rating ON mentor_profiles(average_rating DESC);
CREATE INDEX IF NOT EXISTS idx_mentor_profiles_user ON mentor_profiles(user_id);

-- ============================================================================
-- BOOKING & SESSIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    mentee_user_id UUID NOT NULL REFERENCES users(id),
    mentor_user_id UUID NOT NULL REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id),

    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    timezone VARCHAR(50),

    status VARCHAR(50) DEFAULT 'PENDING',

    meeting_url VARCHAR(500),
    meeting_id VARCHAR(255),
    meeting_password VARCHAR(255),

    ai_scheduled BOOLEAN DEFAULT FALSE,
    ai_reminder_sent BOOLEAN DEFAULT FALSE,

    mentee_notes TEXT,
    mentor_notes TEXT,

    payment_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,

    CHECK (mentee_user_id != mentor_user_id)
);

CREATE INDEX IF NOT EXISTS idx_bookings_mentee ON bookings(mentee_user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_mentor ON bookings(mentor_user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_opportunity ON bookings(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_bookings_scheduled ON bookings(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);

CREATE TABLE IF NOT EXISTS session_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_user_id UUID NOT NULL REFERENCES users(id),
    reviewed_user_id UUID NOT NULL REFERENCES users(id),

    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    skills_learned JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(booking_id, reviewer_user_id)
);

CREATE INDEX IF NOT EXISTS idx_session_reviews_reviewed_user ON session_reviews(reviewed_user_id);

-- ============================================================================
-- PAYMENTS & TRANSACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    payer_user_id UUID NOT NULL REFERENCES users(id),
    payee_user_id UUID REFERENCES users(id),

    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    platform_fee DECIMAL(10, 2),
    mentor_payout DECIMAL(10, 2),

    payment_provider VARCHAR(50),
    payment_intent_id VARCHAR(255),
    status payment_status_enum DEFAULT 'pending',

    booking_id UUID REFERENCES bookings(id),
    opportunity_id UUID REFERENCES opportunities(id),

    payment_method VARCHAR(50),
    receipt_url TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_payments_payer ON payments(payer_user_id);
CREATE INDEX IF NOT EXISTS idx_payments_payee ON payments(payee_user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- ============================================================================
-- LEARNING PATHS & PROGRESS
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subcategory_id UUID NOT NULL REFERENCES subcategories(id),

    current_step INTEGER DEFAULT 1,
    total_steps INTEGER,
    completion_percentage DECIMAL(5, 2) DEFAULT 0.00,

    milestones_completed JSONB,
    recommended_opportunities JSONB,

    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_learning_paths_user ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_subcategory ON learning_paths(subcategory_id);

CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,

    status VARCHAR(50) DEFAULT 'NOT_STARTED',
    completion_percentage INTEGER DEFAULT 0,
    total_time_spent_minutes INTEGER DEFAULT 0,

    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_accessed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, opportunity_id)
);

CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_opportunity ON user_progress(opportunity_id);

-- ============================================================================
-- NOTIFICATIONS SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    notification_type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_name VARCHAR(255),
    actor_avatar_url VARCHAR(500),

    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    reference_id UUID,

    metadata JSONB,

    is_read BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    is_push_sent BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    is_voice_sent BOOLEAN DEFAULT FALSE,

    action_url VARCHAR(500),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,

    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_deleted = false AND is_read = false;
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_notifications_actor ON notifications(actor_id) WHERE is_deleted = false AND actor_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    likes_enabled BOOLEAN DEFAULT true,
    comments_enabled BOOLEAN DEFAULT true,
    replies_enabled BOOLEAN DEFAULT true,
    mentions_enabled BOOLEAN DEFAULT true,
    follows_enabled BOOLEAN DEFAULT true,
    opportunities_enabled BOOLEAN DEFAULT true,
    bookings_enabled BOOLEAN DEFAULT true,
    messages_enabled BOOLEAN DEFAULT true,
    achievements_enabled BOOLEAN DEFAULT true,
    system_enabled BOOLEAN DEFAULT true,

    push_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,

    quiet_hours_enabled BOOLEAN DEFAULT false,
    quiet_hours_start TIME,
    quiet_hours_end TIME,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);

CREATE TABLE IF NOT EXISTS device_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    token TEXT NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    device_name VARCHAR(255),

    is_active BOOLEAN DEFAULT true,

    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, token)
);

CREATE INDEX IF NOT EXISTS idx_device_tokens_user ON device_tokens(user_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_device_tokens_type ON device_tokens(device_type) WHERE is_active = true;

-- ============================================================================
-- GAMIFICATION SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20),
    criteria JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id),

    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS user_points (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMMUNICATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    sender_user_id UUID NOT NULL REFERENCES users(id),
    recipient_user_id UUID NOT NULL REFERENCES users(id),

    message_text TEXT NOT NULL,

    ai_generated BOOLEAN DEFAULT FALSE,

    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CHECK (sender_user_id != recipient_user_id)
);

CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_user_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- ============================================================================
-- AI AGENT SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    agent_name VARCHAR(100) DEFAULT 'Soosh Assistant',
    agent_personality JSONB,

    auto_schedule_enabled BOOLEAN DEFAULT TRUE,
    auto_respond_messages BOOLEAN DEFAULT TRUE,
    auto_manage_calendar BOOLEAN DEFAULT TRUE,

    voice_id VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en-US',

    conversation_history JSONB,
    user_preferences JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS ai_actions_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ai_agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),

    action_type VARCHAR(50),
    action_details JSONB,
    success BOOLEAN,
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_actions_agent ON ai_actions_log(ai_agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_actions_created_at ON ai_actions_log(created_at DESC);

-- ============================================================================
-- ANALYTICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    activity_type VARCHAR(100),
    activity_data JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_time ON user_activity_logs(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    recommendation_type VARCHAR(50),
    recommended_items JSONB,

    query_embedding VECTOR(1536),

    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(user_id, recommendation_type)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user ON ai_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_expires ON ai_recommendations(expires_at);

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

CREATE TRIGGER update_subcategories_updated_at BEFORE UPDATE ON subcategories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_timestamp BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_post_comments_timestamp BEFORE UPDATE ON post_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_timestamp BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION mark_notification_read(notification_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE notifications
    SET is_read = true, read_at = CURRENT_TIMESTAMP
    WHERE id = notification_id AND is_read = false;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION mark_all_notifications_read(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE notifications
    SET is_read = true, read_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id AND is_read = false AND is_deleted = false;
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_unread_notification_count(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    unread_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO unread_count
    FROM notifications
    WHERE user_id = p_user_id AND is_read = false AND is_deleted = false;
    RETURN unread_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW active_mentors AS
SELECT
    u.id,
    u.username,
    u.full_name,
    u.avatar_url,
    mp.average_rating,
    mp.total_reviews,
    u.hourly_rate,
    mp.expertise_categories,
    u.location,
    u.user_type
FROM users u
JOIN mentor_profiles mp ON u.id = mp.user_id
WHERE u.is_mentor_enabled = TRUE
    AND u.user_status = 'active'
    AND u.deleted_at IS NULL;

CREATE OR REPLACE VIEW user_learning_summary AS
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
-- SEED DATA
-- ============================================================================

INSERT INTO categories (name, slug, description, display_order) VALUES
('Creativity & Arts', 'creativity-arts', 'Explore visual arts, music, writing and design', 1),
('Education & Tutoring', 'education-tutoring', 'Academic subjects, test prep and language learning', 2),
('Tech & Digital Innovation', 'tech-innovation', 'Programming, AI, data science and digital skills', 3),
('Lifestyle & Wellness', 'lifestyle-wellness', 'Fitness, mental health, nutrition and wellbeing', 4),
('Entrepreneurship & Side Hustles', 'entrepreneurship', 'Freelancing, startups and business opportunities', 5)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$ BEGIN
    RAISE NOTICE '✅ Complete database schema created successfully!';
    RAISE NOTICE '✅ All tables, indexes, triggers, and functions are in place.';
    RAISE NOTICE '✅ Ready for production use.';
END $$;
