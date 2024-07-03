from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "countries" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "country_id" INT NOT NULL UNIQUE,
    "name" VARCHAR(128) NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS "idx_countries_country_28588e" ON "countries" ("country_id");
COMMENT ON TABLE "countries" IS 'Countries';
CREATE TABLE IF NOT EXISTS "services" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(128) NOT NULL UNIQUE,
    "name" VARCHAR(128),
    "search_names" TEXT,
    "used_count" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_services_code_97a1b4" ON "services" ("code");
COMMENT ON TABLE "services" IS 'Services';
CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL UNIQUE,
    "full_name" VARCHAR(128) NOT NULL,
    "username" VARCHAR(64),
    "mention" VARCHAR(64),
    "balance" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "ref_balance" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "total_ref_earnings" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "refer_id" BIGINT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "users" IS 'Users';
CREATE TABLE IF NOT EXISTS "activations" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "activation_id" INT NOT NULL UNIQUE,
    "cost" DOUBLE PRECISION NOT NULL,
    "phone_number" VARCHAR(32) NOT NULL,
    "sms_text" TEXT,
    "status" SMALLINT NOT NULL  DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "activation_expire_at" TIMESTAMPTZ,
    "country_id" INT NOT NULL REFERENCES "countries" ("id") ON DELETE CASCADE,
    "service_id" INT NOT NULL REFERENCES "services" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_activations_activat_6307c2" ON "activations" ("activation_id");
COMMENT ON COLUMN "activations"."status" IS 'STATUS_WAIT_CODE: 1\nSTATUS_WAIT_RETRY: 2\nSTATUS_WAIT_RESEND: 3\nSTATUS_CANCEL: 4\nSTATUS_OK: 5';
COMMENT ON TABLE "activations" IS 'Activations';
CREATE TABLE IF NOT EXISTS "mails" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(128) NOT NULL UNIQUE,
    "old_messages_id" JSONB NOT NULL,
    "is_paid_mail" BOOL NOT NULL  DEFAULT False,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "expire_at" TIMESTAMPTZ NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_mails_email_979cc6" ON "mails" ("email");
COMMENT ON TABLE "mails" IS 'Mails';
CREATE TABLE IF NOT EXISTS "payments" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "method" VARCHAR(16) NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "order_id" VARCHAR(128)  UNIQUE,
    "invoice_id" VARCHAR(128)  UNIQUE,
    "is_success" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_payments_order_i_b4a5f9" ON "payments" ("order_id");
CREATE INDEX IF NOT EXISTS "idx_payments_invoice_0e0bbd" ON "payments" ("invoice_id");
COMMENT ON COLUMN "payments"."method" IS 'LAVA: lava\nPAYOK: payok\nFREEKASSA: freekassa';
COMMENT ON TABLE "payments" IS 'Payments';
CREATE TABLE IF NOT EXISTS "withdraws" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "requisites" TEXT NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "is_success" BOOL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "withdraws" IS 'Withdraws';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
