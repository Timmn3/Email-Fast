from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "in_channel" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users" ADD "last_check_in" TIMESTAMPTZ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "in_channel";
        ALTER TABLE "users" DROP COLUMN "last_check_in";"""
