"""
Migration: module_links surrogate PK + user_module_links restructure

Run once against your database:
    python -m app.scripts.migrate_module_links

What this does
--------------
1. Adds a surrogate `id` PK to module_links.
2. Drops the old user_module_links table and recreates it with:
     - user_id          (FK → users.id)
     - module_link_id   (FK → module_links.id)   ← replaces module_id
     - link_id          (FK → links.id)
     - completed        bool
     - completed_at     timestamp
   PK: (user_id, module_link_id)

WARNING: this drops and recreates user_module_links, losing any existing
data in that table. Back up first if you need it.
"""

from app.core.database import engine
from sqlalchemy import text


def run():
    with engine.begin() as conn:

        # ----------------------------------------------------------------
        # 1. module_links — add surrogate id
        # ----------------------------------------------------------------

        # Drop the old composite PK
        conn.execute(text("""
            ALTER TABLE module_links
                DROP CONSTRAINT IF EXISTS module_links_pkey
        """))

        # Add the surrogate id (BIGSERIAL creates the sequence automatically)
        conn.execute(text("""
            ALTER TABLE module_links
                ADD COLUMN IF NOT EXISTS id BIGSERIAL PRIMARY KEY
        """))

        # Ensure the unique constraints still exist (idempotent)
        conn.execute(text("""
            ALTER TABLE module_links
                DROP CONSTRAINT IF EXISTS uq_module_links_module_link
        """))
        conn.execute(text("""
            ALTER TABLE module_links
                ADD CONSTRAINT uq_module_links_module_link
                    UNIQUE (module_id, link_id)
        """))

        # uq_module_links_order should already exist; recreate to be safe
        conn.execute(text("""
            ALTER TABLE module_links
                DROP CONSTRAINT IF EXISTS uq_module_links_order
        """))
        conn.execute(text("""
            ALTER TABLE module_links
                ADD CONSTRAINT uq_module_links_order
                    UNIQUE (module_id, order_index)
        """))

        # ----------------------------------------------------------------
        # 2. user_module_links — drop and recreate
        # ----------------------------------------------------------------

        conn.execute(text("DROP TABLE IF EXISTS user_module_links CASCADE"))

        conn.execute(text("""
            CREATE TABLE user_module_links (
                user_id         BIGINT      NOT NULL REFERENCES users(id),
                module_link_id  BIGINT      NOT NULL REFERENCES module_links(id),
                link_id         BIGINT      NOT NULL REFERENCES links(id),
                completed       BOOLEAN     NOT NULL DEFAULT false,
                completed_at    TIMESTAMP,
                PRIMARY KEY (user_id, module_link_id)
            )
        """))

        conn.execute(text("""
            CREATE INDEX ix_user_module_links_user_id
                ON user_module_links (user_id)
        """))
        conn.execute(text("""
            CREATE INDEX ix_user_module_links_module_link_id
                ON user_module_links (module_link_id)
        """))
        conn.execute(text("""
            CREATE INDEX ix_user_module_links_link_id
                ON user_module_links (link_id)
        """))

        print("Migration complete.")


if __name__ == "__main__":
    run()