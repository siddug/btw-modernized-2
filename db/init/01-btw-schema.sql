-- Read-only schema for the publisher FastAPI port's local stack.
-- Creates the `btw` schema and only the four tables the service reads:
-- btw.users, btw.custom_domains, btw.notes, btw.memories
-- (column definitions taken from the recorded btw pg_dump).

CREATE SCHEMA IF NOT EXISTS btw;

CREATE SEQUENCE IF NOT EXISTS btw.custom_domains_id_seq;
CREATE SEQUENCE IF NOT EXISTS btw.user_id_seq;

CREATE TABLE IF NOT EXISTS "btw"."custom_domains" (
    "id" int4 NOT NULL DEFAULT nextval('btw.custom_domains_id_seq'::regclass),
    "domain" text NOT NULL,
    "user_id" int4 NOT NULL,
    "umami_site_id" uuid,
    "share_id" text,
    PRIMARY KEY ("domain","user_id")
);

CREATE TABLE IF NOT EXISTS "btw"."users" (
    "id" int4 NOT NULL DEFAULT nextval('btw.user_id_seq'::regclass),
    "email" text NOT NULL,
    "processed_email" text NOT NULL,
    "name" text,
    "slug" text,
    "created_at" timestamptz NOT NULL,
    "bio" text,
    "pic" varchar,
    "twitter" varchar,
    "instagram" varchar,
    "linkedin" varchar,
    "pro" bool,
    "umami_site_id" uuid,
    "share_id" text,
    "settings" json,
    PRIMARY KEY ("processed_email")
);

CREATE TABLE IF NOT EXISTS "btw"."notes" (
    "user_id" int4 NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    "json" json,
    "html" text,
    "title" text,
    "id" uuid NOT NULL,
    "ydoc" bytea,
    "tags" text,
    "published_at" timestamptz,
    "slug" text,
    "publish" bool,
    "archive" bool,
    "delete" bool,
    "deleted_at" timestamptz,
    "md" text,
    "image" text,
    "private" bool,
    PRIMARY KEY ("id","user_id")
);

CREATE TABLE IF NOT EXISTS "btw"."memories" (
    "id" uuid NOT NULL,
    "user_id" int4 NOT NULL,
    "name" text NOT NULL,
    "place_name" text NOT NULL,
    "place_address" text,
    "latitude" float8 NOT NULL,
    "longitude" float8 NOT NULL,
    "place_type" text,
    "city" text NOT NULL,
    "country_code" text NOT NULL,
    "description" text,
    "photo_urls" jsonb,
    "visited_date" timestamptz,
    "private" boolean NOT NULL DEFAULT false,
    "created_at" timestamptz NOT NULL DEFAULT NOW(),
    "updated_at" timestamptz NOT NULL DEFAULT NOW(),
    PRIMARY KEY ("id","user_id")
);
