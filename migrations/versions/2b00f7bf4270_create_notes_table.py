"""create notes table

Revision ID: 2b00f7bf4270
Revises: 10d2d9383f96
Create Date: 2026-01-05 16:44:24.578464

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b00f7bf4270"
down_revision: Union[str, Sequence[str], None] = "10d2d9383f96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String, nullable=False, unique=True, index=True),
        sa.Column("content", sa.String, nullable=False),
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
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("notes")
