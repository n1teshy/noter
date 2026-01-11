"""add note unique constraint

Revision ID: 65fb34504919
Revises: a3928a838c8b
Create Date: 2026-01-11 17:00:56.258851

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "65fb34504919"
down_revision: Union[str, Sequence[str], None] = "a3928a838c8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_notes_title", table_name="notes")
    op.create_unique_constraint(
        "uq_note_title_author",
        "notes",
        ["author_id", "title"],
    )


def downgrade() -> None:
    op.create_index(
        "ix_notes_title",
        "notes",
        ["title"],
        unique=True,
    )
    op.drop_constraint(
        "uq_note_title_author",
        "notes",
        type_="unique",
    )
