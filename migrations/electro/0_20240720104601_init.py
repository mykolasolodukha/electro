from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "guild" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "name" VARCHAR(255) NOT NULL,
    "icon" VARCHAR(255),
    "banner" VARCHAR(255),
    "description" TEXT,
    "preferred_locale" VARCHAR(255),
    "afk_channel_id" BIGINT,
    "afk_timeout" INT,
    "owner_id" BIGINT
);
COMMENT ON TABLE "guild" IS 'The model for Discord Guild.';
CREATE TABLE IF NOT EXISTS "channel" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "name" VARCHAR(255),
    "type" VARCHAR(255) NOT NULL,
    "used_for" VARCHAR(255),
    "guild_id" BIGINT REFERENCES "guild" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "channel" IS 'The model for Discord Channel.';
CREATE TABLE IF NOT EXISTS "role" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "name" VARCHAR(255) NOT NULL,
    "color" INT,
    "position" INT,
    "permissions" INT,
    "is_hoisted" BOOL NOT NULL  DEFAULT FALSE,
    "is_mentionable" BOOL NOT NULL  DEFAULT FALSE,
    "guild_id" BIGINT NOT NULL REFERENCES "guild" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "role" IS 'The model for Discord Role.';
CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "username" VARCHAR(255) NOT NULL,
    "discriminator" INT NOT NULL,
    "avatar" VARCHAR(255),
    "locale" VARCHAR(255),
    "is_bot" BOOL NOT NULL  DEFAULT FALSE,
    "is_admin" BOOL NOT NULL  DEFAULT FALSE
);
COMMENT ON TABLE "user" IS 'The model for Discord User.';
CREATE TABLE IF NOT EXISTS "guild_member" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "nickname" VARCHAR(255),
    "joined_at" TIMESTAMPTZ,
    "premium_since" TIMESTAMPTZ,
    "deaf" BOOL NOT NULL  DEFAULT FALSE,
    "mute" BOOL NOT NULL  DEFAULT FALSE,
    "guild_id" BIGINT NOT NULL REFERENCES "guild" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "guild_member" IS 'The model for Discord Guild Member.';
CREATE TABLE IF NOT EXISTS "message" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "edited_at" TIMESTAMPTZ,
    "is_pinned" BOOL,
    "is_tts" BOOL,
    "is_bot_message" BOOL,
    "is_command" BOOL,
    "author_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "channel_id" BIGINT NOT NULL REFERENCES "channel" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "message" IS 'The model for Message.';
CREATE TABLE IF NOT EXISTS "interaction" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "custom_id" VARCHAR(255) NOT NULL,
    "channel_id" BIGINT NOT NULL REFERENCES "channel" ("id") ON DELETE CASCADE,
    "message_id" BIGINT NOT NULL REFERENCES "message" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "interaction" IS 'The model for Interaction.';
CREATE TABLE IF NOT EXISTS "user_state_changed" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT TRUE,
    "is_deleted" BOOL NOT NULL  DEFAULT FALSE,
    "date_deleted" TIMESTAMPTZ,
    "previous_state" TEXT,
    "new_state" TEXT NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "user_state_changed" IS 'The model for User State Changed.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
