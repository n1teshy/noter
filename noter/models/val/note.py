from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

import noter.utils.constants as c
from noter.models.db.note import Note as NoteModel
from noter.models.val.meta import TimestampedJSON
from noter.models.val.user import UserJSON
from noter.utils.exceptions import AppException


class NoteBase(BaseModel):
    title: str = Field(description="The title of the note")
    content: str = Field(description="The content of the note")
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tags associated with the note",
    )
    is_public: bool = Field(
        description="Whether the note is public or private", alias="isPublic"
    )

    model_config = ConfigDict(populate_by_name=False)


class NoteCreate(NoteBase):
    model_config = ConfigDict(extra="forbid")


class NoteJSON(TimestampedJSON, NoteBase):
    author: UserJSON


async def ensure_constraints(
    note: NoteCreate,
    session: AsyncSession,
    user_id: int,
    id: Optional[int] = None,
) -> None:
    stmt = select(
        exists().where(
            NoteModel.title == note.title,
            NoteModel.author_id == user_id,
            True if id is None else NoteModel.id != id,
        )
    )
    if await session.scalar(stmt):
        raise RequestValidationError(
            errors=[
                {
                    c.FA_FLD_LOC: (c.FA_FLD_BODY, c.WORD_TITLE),
                    c.FA_FLD_MSG: "A note with this title already exists.",
                    c.FA_FLD_TYPE: "value_error.note.title.exists",
                }
            ]
        )


async def ensure_exists(session: AsyncSession, id: int):
    stmt = select(exists().where(NoteModel.id == id))
    if not await session.scalar(stmt):
        raise AppException(
            status=404, payload={c.WORD_MESSAGE: "Note doesn't exist"}
        )


async def ensure_viewership(
    session: AsyncSession, user_id: int, note_id: int
) -> bool:
    stmt = select(
        exists().where(
            NoteModel.id == note_id,
            or_(NoteModel.is_public.is_(True), NoteModel.author_id == user_id),
        )
    )
    if not session.scalar(stmt):
        raise AppException(status=403)


async def ensure_ownership(
    session: AsyncSession, user_id: int, note_id: int
) -> bool:
    stmt = select(
        exists().where(
            NoteModel.author_id == user_id,
            NoteModel.id == note_id,
        )
    )
    if not await session.scalar(stmt):
        raise AppException(status=403)
