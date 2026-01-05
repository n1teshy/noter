"""add notes table

Revision ID: 3313c893d9a3
Revises: ad4c698cda02
Create Date: 2026-01-05 11:21:41.523748

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3313c893d9a3"
down_revision: Union[str, Sequence[str], None] = "ad4c698cda02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "title", sa.String(255), nullable=False, unique=True, index=True
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "tags", sa.ARRAY(sa.String), nullable=False, server_default="{}"
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("notes")
