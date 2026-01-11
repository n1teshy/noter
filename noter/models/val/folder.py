from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

import noter.utils.constants as c
from noter.models.db.folder import Folder as FolderModel
from noter.models.val.meta import TimestampedJSON
from noter.models.val.user import UserJSON
from noter.utils.exceptions import AppException


class FolderBase(BaseModel):
    name: str = Field(description="The name of the folder")


class FolderCreate(FolderBase):
    model_config = ConfigDict(extra="forbid")


class FolderJSON(TimestampedJSON, FolderBase):
    author: UserJSON


async def ensure_constraints(
    folder: FolderCreate,
    session: AsyncSession,
    user_id: int,
    id: Optional[int] = None,
) -> None:
    stmt = select(
        exists().where(
            FolderModel.name == folder.name,
            FolderModel.author_id == user_id,
            True if id is None else FolderModel.id != id,
        )
    )
    if await session.scalar(stmt):
        raise RequestValidationError(
            errors=[
                {
                    c.FA_FLD_LOC: (c.FA_FLD_BODY, c.WORD_NAME),
                    c.FA_FLD_MSG: "A folder with this name already exists.",
                    c.FA_FLD_TYPE: "value_error.folder.name.exists",
                }
            ]
        )


async def ensure_exists(session: AsyncSession, id: int):
    stmt = select(exists().where(FolderModel.id == id))
    if not await session.scalar(stmt):
        raise AppException(
            status=404, payload={c.WORD_MESSAGE: "Folder doesn't exist"}
        )


async def ensure_ownership(
    session: AsyncSession, user_id: int, folder_id: int
) -> bool:
    stmt = select(
        exists().where(
            FolderModel.author_id == user_id,
            FolderModel.id == folder_id,
        )
    )
    if not session.scalar(stmt):
        raise AppException(status=403)
