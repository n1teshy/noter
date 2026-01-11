"""delete folder-note mapping on delete of either

Revision ID: f8a7c716dbcf
Revises: 65fb34504919
Create Date: 2026-01-11 23:26:18.528236

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8a7c716dbcf"
down_revision: Union[str, Sequence[str], None] = "65fb34504919"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "folder_notes_folder_id_fkey",
        "folder_notes",
        type_="foreignkey",
    )
    op.drop_constraint(
        "folder_notes_note_id_fkey",
        "folder_notes",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "folder_notes_folder_id_fkey",
        "folder_notes",
        "folders",
        ["folder_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "folder_notes_note_id_fkey",
        "folder_notes",
        "notes",
        ["note_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "folder_notes_folder_id_fkey",
        "folder_notes",
        type_="foreignkey",
    )
    op.drop_constraint(
        "folder_notes_note_id_fkey",
        "folder_notes",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "folder_notes_folder_id_fkey",
        "folder_notes",
        "folders",
        ["folder_id"],
        ["id"],
    )
    op.create_foreign_key(
        "folder_notes_note_id_fkey",
        "folder_notes",
        "notes",
        ["note_id"],
        ["id"],
    )
