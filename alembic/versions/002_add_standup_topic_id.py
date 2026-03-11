"""add standup_topic_id to settings

Revision ID: 002
Revises: 001
Create Date: 2025-03-11

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("standup_topic_id", sa.BIGINT(), nullable=True))


def downgrade() -> None:
    op.drop_column("settings", "standup_topic_id")
