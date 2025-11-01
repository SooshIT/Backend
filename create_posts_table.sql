-- Social Posts Table for User Updates, Achievements, and Content Sharing
-- This table stores user-generated content like work achievements, skill updates, project showcases, etc.

-- First, create enum for post types
CREATE TYPE post_type_enum AS ENUM (
    'achievement',      -- Skills learned, milestones reached
    'project',          -- Work/project showcase
    'article',          -- Written content, blog posts
    'question',         -- Questions to community
    'discussion',       -- General discussions
    'resource'          -- Shared resources, links, materials
);

-- Create enum for post visibility
CREATE TYPE post_visibility_enum AS ENUM (
    'public',           -- Visible to everyone
    'connections',      -- Only visible to connections
    'private'           -- Only visible to author
);

-- Create the posts table
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Post content
    post_type post_type_enum NOT NULL DEFAULT 'discussion',
    title VARCHAR(500),
    content TEXT NOT NULL,
    media_urls TEXT[],                      -- Array of image/video URLs
    tags TEXT[],                            -- Hashtags and keywords

    -- Categorization (optional - links to existing categories)
    category_id UUID REFERENCES categories(id),
    subcategory_id UUID REFERENCES subcategories(id),

    -- Metadata
    visibility post_visibility_enum NOT NULL DEFAULT 'public',
    is_pinned BOOLEAN DEFAULT false,        -- Pin to user's profile
    is_featured BOOLEAN DEFAULT false,      -- Featured by admin

    -- Engagement metrics
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,                 -- NULL if draft

    -- Soft delete
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_posts_author ON posts(author_id) WHERE is_deleted = false;
CREATE INDEX idx_posts_type ON posts(post_type) WHERE is_deleted = false;
CREATE INDEX idx_posts_category ON posts(category_id) WHERE is_deleted = false;
CREATE INDEX idx_posts_published ON posts(published_at DESC) WHERE is_deleted = false AND published_at IS NOT NULL;
CREATE INDEX idx_posts_visibility ON posts(visibility) WHERE is_deleted = false;
CREATE INDEX idx_posts_tags ON posts USING GIN(tags) WHERE is_deleted = false;

-- Create likes table for tracking who liked what
CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(post_id, user_id)
);

CREATE INDEX idx_post_likes_post ON post_likes(post_id);
CREATE INDEX idx_post_likes_user ON post_likes(user_id);

-- Create comments table
CREATE TABLE IF NOT EXISTS post_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_comment_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,  -- For nested replies

    content TEXT NOT NULL,
    media_urls TEXT[],

    likes_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_post_comments_post ON post_comments(post_id) WHERE is_deleted = false;
CREATE INDEX idx_post_comments_author ON post_comments(author_id) WHERE is_deleted = false;
CREATE INDEX idx_post_comments_parent ON post_comments(parent_comment_id) WHERE is_deleted = false;

-- Add 'gig' to opportunities enum
ALTER TYPE opportunity_type_enum ADD VALUE IF NOT EXISTS 'gig';

-- Update trigger function for updated_at
CREATE OR REPLACE FUNCTION update_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_posts_timestamp
    BEFORE UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION update_posts_updated_at();

CREATE TRIGGER update_post_comments_timestamp
    BEFORE UPDATE ON post_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_posts_updated_at();

-- Comments
COMMENT ON TABLE posts IS 'User-generated content including achievements, projects, articles, and discussions';
COMMENT ON TABLE post_likes IS 'Tracks which users liked which posts';
COMMENT ON TABLE post_comments IS 'Comments and replies on posts';
COMMENT ON COLUMN posts.post_type IS 'Type of post: achievement, project, article, question, discussion, resource';
COMMENT ON COLUMN posts.visibility IS 'Who can see this post: public, connections, private';
COMMENT ON COLUMN posts.is_pinned IS 'Whether post is pinned to user profile';
COMMENT ON COLUMN posts.is_featured IS 'Whether post is featured by admin/platform';
