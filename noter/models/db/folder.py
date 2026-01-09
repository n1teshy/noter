from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

import noter.utils.constants as c
from noter.models.db.meta import BaseModel


class Folder(BaseModel):
    __tablename__ = c.TBL_FOLDERS
    __table_args__ = (
        UniqueConstraint(
            c.COL_AUHTOR_ID,
            c.WORD_NAME,
            name="uq_folder_name_author",
        ),
    )

    basic_json_map = {
        **{wd: wd for wd in [c.WORD_ID, c.WORD_NAME]},
        c.FLD_AUTHOR: lambda folder: folder.author.to_json(),
        c.FLD_CREATED_AT: lambda folder: folder.created_at.isoformat(),
        c.FLD_UPDATED_AT: lambda folder: folder.updated_at.isoformat(),
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey(f"{c.TBL_USERS}.{c.WORD_ID}"), nullable=False
    )

    author = relationship("User", back_populates="folders")

    @staticmethod
    def from_data(data: dict, author_id: int) -> "Folder":
        return Folder(**data, author_id=author_id)
