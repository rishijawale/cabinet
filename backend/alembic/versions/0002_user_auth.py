"""Supabase identity columns for provisioned accounts.

Revision ID: 0002_user_auth
Revises: 0001_initial
Create Date: 2026-11-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.models import *  # noqa: F401,F403

revision: str = "0002_user_auth"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CONSTRAINT_NAME = "uq_users_supabase_sub"


def _has_sub_column(inspector: sa.Inspector) -> bool:
    return "supabase_sub" in {column["name"] for column in inspector.get_columns("users")}


def _has_sub_uniqueness(inspector: sa.Inspector) -> bool:
    for constraint in inspector.get_unique_constraints("users"):
        if "supabase_sub" in constraint.get("column_names", []):
            return True
    for index in inspector.get_indexes("users"):
        if index.get("unique") and "supabase_sub" in index.get("column_names", []):
            return True
    return False


def upgrade() -> None:
    """Add the column on databases created before it existed.

    0001 builds the schema from the current models, so a fresh database already
    has both the column and its unique constraint; this migration then no-ops.
    """
    inspector = sa.inspect(op.get_bind())
    if not _has_sub_column(inspector):
        op.add_column(
            "users",
            sa.Column("supabase_sub", sa.String(64), nullable=True),
        )
    if not _has_sub_uniqueness(inspector):
        op.create_unique_constraint(CONSTRAINT_NAME, "users", ["supabase_sub"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for constraint in inspector.get_unique_constraints("users"):
        if "supabase_sub" in constraint.get("column_names", []):
            op.drop_constraint(constraint["name"], "users", type_="unique")
    for index in inspector.get_indexes("users"):
        if index.get("unique") and "supabase_sub" in index.get("column_names", []):
            op.drop_index(index["name"], table_name="users")
    if _has_sub_column(inspector):
        op.drop_column("users", "supabase_sub")
