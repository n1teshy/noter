"""add folder unique constraint

Revision ID: a3928a838c8b
Revises: c74258d9dab4
Create Date: 2026-01-09 15:07:36.488354

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3928a838c8b"
down_revision: Union[str, Sequence[str], None] = "c74258d9dab4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_folder_name_author",
        "folders",
        ["author_id", "name"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_folder_name_author",
        "folders",
        type_="unique",
    )
