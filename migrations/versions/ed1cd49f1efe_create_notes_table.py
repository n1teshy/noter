"""Create notes table

Revision ID: ed1cd49f1efe
Revises:
Create Date: 2026-01-03 22:05:27.469969

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ed1cd49f1efe"
down_revision: Union[str, Sequence[str], None] = None
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
