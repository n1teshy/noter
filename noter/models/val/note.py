from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

import noter.utils.constants as c
from noter.models.db.note import Note as NoteModel
from noter.models.val.meta import TimestampedJSON


class NoteBase(BaseModel):
    title: str = Field(description="The title of the note")
    content: str = Field(description="The content of the note")
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tags associated with the note",
    )


class NoteCreate(NoteBase):
    model_config = ConfigDict(extra="forbid")


class NoteJSON(TimestampedJSON, NoteBase):
    pass


async def ensure_constraints(
    note: NoteCreate, session: AsyncSession, id: Optional[int] = None
) -> None:
    stmt = select(exists().where(NoteModel.title == note.title))
    if id is not None:
        stmt = stmt.where(NoteModel.id != id)

    invalid = (await session.execute(stmt)).scalar()
    if invalid:
        raise RequestValidationError(
            errors=[
                {
                    c.FA_FLD_LOC: (c.FA_FLD_BODY, c.WORD_TITLE),
                    c.FA_FLD_MSG: "A note with this title already exists.",
                    c.FA_FLD_TYPE: "value_error.note.title.exists",
                }
            ]
        )
