-- Notifications System for Real-Time User Updates
-- Handles likes, comments, mentions, opportunities, bookings, etc.

-- Create enum for notification types
CREATE TYPE notification_type_enum AS ENUM (
    'like',                 -- Someone liked your post/opportunity
    'comment',              -- Someone commented on your post/opportunity
    'reply',                -- Someone replied to your comment
    'mention',              -- Someone mentioned you in a post/comment
    'follow',               -- Someone followed you
    'opportunity',          -- New opportunity matching your interests
    'booking',              -- Booking request/confirmation/cancellation
    'message',              -- New direct message
    'achievement',          -- Milestone or achievement unlocked
    'system'                -- System announcements
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Recipient
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Type and content
    notification_type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Actor (who triggered the notification)
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_name VARCHAR(255),           -- Cached name for deleted users
    actor_avatar_url VARCHAR(500),     -- Cached avatar

    -- Related entities (for navigation)
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,

    -- Additional data (JSON for flexibility)
    metadata JSONB,                    -- Extra data specific to notification type

    -- State
    is_read BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,

    -- Action URL (deeplink for mobile)
    action_url VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,

    -- Soft delete
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_notifications_user ON notifications(user_id) WHERE is_deleted = false;
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_deleted = false AND is_read = false;
CREATE INDEX idx_notifications_type ON notifications(notification_type) WHERE is_deleted = false;
CREATE INDEX idx_notifications_created ON notifications(created_at DESC) WHERE is_deleted = false;
CREATE INDEX idx_notifications_actor ON notifications(actor_id) WHERE is_deleted = false AND actor_id IS NOT NULL;

-- Notification preferences table (what notifications users want to receive)
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Per-type preferences
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

    -- Delivery channels
    push_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,

    -- Quiet hours
    quiet_hours_enabled BOOLEAN DEFAULT false,
    quiet_hours_start TIME,
    quiet_hours_end TIME,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

CREATE INDEX idx_notification_preferences_user ON notification_preferences(user_id);

-- Device tokens for push notifications
CREATE TABLE IF NOT EXISTS device_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    token TEXT NOT NULL,
    device_type VARCHAR(50) NOT NULL,  -- 'ios', 'android', 'web'
    device_name VARCHAR(255),

    is_active BOOLEAN DEFAULT true,

    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, token)
);

CREATE INDEX idx_device_tokens_user ON device_tokens(user_id) WHERE is_active = true;
CREATE INDEX idx_device_tokens_type ON device_tokens(device_type) WHERE is_active = true;

-- Update trigger for notification preferences
CREATE OR REPLACE FUNCTION update_notification_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_notification_preferences_timestamp
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_preferences_updated_at();

-- Function to mark notification as read
CREATE OR REPLACE FUNCTION mark_notification_read(notification_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE notifications
    SET is_read = true, read_at = CURRENT_TIMESTAMP
    WHERE id = notification_id AND is_read = false;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to mark all notifications as read for a user
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

-- Function to get unread count for a user
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

-- Comments
COMMENT ON TABLE notifications IS 'System-wide notifications for user activities and updates';
COMMENT ON TABLE notification_preferences IS 'User preferences for notification delivery';
COMMENT ON TABLE device_tokens IS 'Device tokens for push notifications';
COMMENT ON COLUMN notifications.notification_type IS 'Type of notification: like, comment, reply, mention, follow, opportunity, booking, message, achievement, system';
COMMENT ON COLUMN notifications.actor_id IS 'User who triggered the notification (null for system notifications)';
COMMENT ON COLUMN notifications.metadata IS 'Additional JSON data specific to notification type';
COMMENT ON COLUMN notifications.action_url IS 'Deep link or URL to navigate when notification is tapped';
