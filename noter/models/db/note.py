from sqlalchemy import ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column

import noter.utils.constants as c
from noter.models.db.meta import BaseModel


class Note(BaseModel):
    __tablename__ = c.TBL_NOTES
    basic_json_map = {
        **{
            wd: wd
            for wd in [c.WORD_ID, c.WORD_TITLE, c.WORD_CONTENT, c.WORD_TAGS]
        },
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

    @staticmethod
    def from_data(data: dict) -> "Note":
        return Note(**data)
