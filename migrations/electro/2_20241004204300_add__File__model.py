from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "file" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_deleted" BOOL NOT NULL  DEFAULT False,
    "date_deleted" TIMESTAMPTZ,
    "storage_service" VARCHAR(32) NOT NULL,
    "storage_file_object_key" TEXT NOT NULL,
    "file_name" TEXT,
    "discord_attachment_id" TEXT,
    "discord_cdn_url" TEXT,
    "added_by_user_id" BIGINT REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "file"."storage_service" IS 'S3: S3\nAZURE_BLOB_STORAGE: AzureBlobStorage';
COMMENT ON TABLE "file" IS 'The model for the file.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "file";"""
