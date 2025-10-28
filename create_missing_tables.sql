-- Create missing essential tables for Soosh platform

-- Subcategories table
CREATE TABLE IF NOT EXISTS subcategories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id);
CREATE INDEX IF NOT EXISTS idx_subcategories_slug ON subcategories(slug);
CREATE INDEX IF NOT EXISTS idx_subcategories_active ON subcategories(is_active) WHERE is_active = true;

-- Opportunity types enum
DO $$ BEGIN
    CREATE TYPE opportunity_type_enum AS ENUM ('COURSE', 'JOB', 'MENTORSHIP', 'WORKSHOP', 'GIG');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Difficulty level enum
DO $$ BEGIN
    CREATE TYPE difficulty_level_enum AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Opportunities table (simplified without pgvector)
CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    subcategory_id UUID REFERENCES subcategories(id),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    opportunity_type opportunity_type_enum NOT NULL DEFAULT 'COURSE',
    difficulty_level difficulty_level_enum DEFAULT 'BEGINNER',

    -- Duration and schedule
    duration_hours INTEGER DEFAULT 0,
    duration_weeks INTEGER,
    start_date TIMESTAMP,
    end_date TIMESTAMP,

    -- Pricing
    price DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    is_free BOOLEAN DEFAULT false,

    -- Media
    thumbnail_url VARCHAR(1000),
    video_url VARCHAR(1000),
    images TEXT[],

    -- Skills and requirements
    skills_required TEXT[],
    skills_gained TEXT[],
    prerequisites TEXT[],

    -- Location
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT true,
    is_onsite BOOLEAN DEFAULT false,

    -- Status and metrics
    is_active BOOLEAN DEFAULT true,
    is_published BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    views_count INTEGER DEFAULT 0,
    enrollments_count INTEGER DEFAULT 0,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,

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

-- Bookings table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bookings_mentee ON bookings(mentee_user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_mentor ON bookings(mentor_user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_opportunity ON bookings(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_bookings_scheduled ON bookings(scheduled_at);

-- User progress table
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

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
DROP TRIGGER IF EXISTS update_subcategories_updated_at ON subcategories;
CREATE TRIGGER update_subcategories_updated_at
    BEFORE UPDATE ON subcategories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_opportunities_updated_at ON opportunities;
CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings;
CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_progress_updated_at ON user_progress;
CREATE TRIGGER update_user_progress_updated_at
    BEFORE UPDATE ON user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$ BEGIN
    RAISE NOTICE 'Tables created successfully!';
END $$;
