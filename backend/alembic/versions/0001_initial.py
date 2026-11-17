"""Initial archive schema, search infrastructure and audit trail.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-17
"""

from collections.abc import Sequence

from alembic import op

from app.core.db import Base
from app.models import *  # noqa: F401,F403

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# asyncpg cannot run multi-statement SQL, so each statement is executed alone.
SEARCH_STATEMENTS = [
    """
    CREATE OR REPLACE FUNCTION cabinet_artwork_search_vector(artwork_uuid uuid)
    RETURNS tsvector
    LANGUAGE sql
    STABLE
    AS $$
      SELECT
          setweight(to_tsvector('simple', coalesce(a.title, '')), 'A')
          || setweight(to_tsvector('simple', coalesce(a.description, '')), 'B')
          || setweight(to_tsvector('simple', coalesce(a.external_creator_name, '')), 'C')
          || setweight(to_tsvector('simple', coalesce(string_agg(t.name, ' '), '')), 'C')
      FROM artworks a
      LEFT JOIN artwork_tags at ON at.artwork_id = a.id
      LEFT JOIN tags t ON t.id = at.tag_id
      WHERE a.id = artwork_uuid
      GROUP BY a.id, a.title, a.description, a.external_creator_name;
    $$;
    """,
    """
    CREATE OR REPLACE FUNCTION cabinet_artworks_search_refresh()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      UPDATE artworks
         SET search_vector = cabinet_artwork_search_vector(NEW.id)
       WHERE id = NEW.id;
      RETURN NEW;
    END;
    $$;
    """,
    """
    CREATE TRIGGER trg_artworks_search
    AFTER INSERT OR UPDATE OF title, description, external_creator_name ON artworks
    FOR EACH ROW EXECUTE FUNCTION cabinet_artworks_search_refresh();
    """,
    """
    CREATE OR REPLACE FUNCTION cabinet_artwork_tags_search_refresh()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
      target uuid;
    BEGIN
      IF TG_OP = 'DELETE' THEN
        target := OLD.artwork_id;
      ELSE
        target := NEW.artwork_id;
      END IF;
      UPDATE artworks
         SET search_vector = cabinet_artwork_search_vector(target)
       WHERE id = target;
      RETURN NULL;
    END;
    $$;
    """,
    """
    CREATE TRIGGER trg_artwork_tags_search
    AFTER INSERT OR DELETE ON artwork_tags
    FOR EACH ROW EXECUTE FUNCTION cabinet_artwork_tags_search_refresh();
    """,
    """
    CREATE OR REPLACE FUNCTION cabinet_tags_search_refresh()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      UPDATE artworks a
         SET search_vector = cabinet_artwork_search_vector(a.id)
       WHERE a.id IN (SELECT at.artwork_id FROM artwork_tags at WHERE at.tag_id = NEW.id);
      RETURN NEW;
    END;
    $$;
    """,
    """
    CREATE TRIGGER trg_tags_search
    AFTER UPDATE OF name ON tags
    FOR EACH ROW EXECUTE FUNCTION cabinet_tags_search_refresh();
    """,
]

DROP_STATEMENTS = [
    "DROP TRIGGER IF EXISTS trg_tags_search ON tags",
    "DROP TRIGGER IF EXISTS trg_artwork_tags_search ON artwork_tags",
    "DROP TRIGGER IF EXISTS trg_artworks_search ON artworks",
    "DROP FUNCTION IF EXISTS cabinet_tags_search_refresh()",
    "DROP FUNCTION IF EXISTS cabinet_artwork_tags_search_refresh()",
    "DROP FUNCTION IF EXISTS cabinet_artworks_search_refresh()",
    "DROP FUNCTION IF EXISTS cabinet_artwork_search_vector(uuid)",
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    Base.metadata.create_all(bind=op.get_bind())
    for statement in SEARCH_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DROP_STATEMENTS:
        op.execute(statement)
    Base.metadata.drop_all(bind=op.get_bind())
