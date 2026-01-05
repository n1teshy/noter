from sqlalchemy import ARRAY, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

import noter.utils.constants as c
from noter.models.db.meta import BaseModel


class Note(BaseModel):
    __tablename__ = c.TBL_NOTES
    basic_json_map = {
        **{
            wd: wd
            for wd in [c.WORD_ID, c.WORD_TITLE, c.WORD_CONTENT, c.WORD_TAGS]
        },
        c.FLD_IS_PUBLIC: c.COL_IS_PUBLIC,
        c.FLD_AUTHOR: lambda note: note.author.to_json(),
        c.FLD_CREATED_AT: lambda note: note.created_at.isoformat(),
        c.FLD_UPDATED_AT: lambda note: note.updated_at.isoformat(),
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    content: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey(f"{c.TBL_USERS}.{c.WORD_ID}"), nullable=False
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    author = relationship("User", back_populates="notes")

    @staticmethod
    def from_data(data: dict, author_id: int) -> "Note":
        return Note(**data, author_id=author_id)
