from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payment_links" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "payment_link_id" VARCHAR(32) NOT NULL UNIQUE,
    "user_id_list" JSONB NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "limit" INT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_payment_lin_payment_d776a2" ON "payment_links" ("payment_link_id");
COMMENT ON TABLE "payment_links" IS 'PaymentLinks';;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "payment_links";"""
