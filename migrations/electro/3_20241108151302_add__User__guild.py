from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "guild_id" BIGINT;
        ALTER TABLE "user" DROP COLUMN "is_staff_member";
        ALTER TABLE "user" ADD CONSTRAINT "fk_user_guild_b2421aae" FOREIGN KEY ("guild_id") REFERENCES "guild" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP CONSTRAINT "fk_user_guild_b2421aae";
        ALTER TABLE "user" ADD "is_staff_member" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "user" DROP COLUMN "guild_id";"""
