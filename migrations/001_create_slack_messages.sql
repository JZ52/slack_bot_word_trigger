CREATE TABLE IF NOT EXISTS public.slack_messages (
    id BIGSERIAL PRIMARY KEY,
    channel_id VARCHAR(32) NOT NULL,
    channel_name VARCHAR(100),
    message_ts VARCHAR(32) NOT NULL,
    original_message TEXT NOT NULL,
    has_image BOOLEAN NOT NULL DEFAULT FALSE,
    original_user_id VARCHAR(32),
    original_user_name VARCHAR(100),
    resolved_by_user_id VARCHAR(32) NOT NULL,
    resolved_by_user_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ NOT NULL,
    UNIQUE (channel_id, message_ts)
);