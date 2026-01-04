from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

import noter.utils.constants as c
from noter.models.db.user import User as UserModel
from noter.models.val.meta import TimestampedJSON


class UserBase(BaseModel):
    username: str = Field(description="The username of the user")


class UserCreate(UserBase):
    password: str = Field(description="The password of the user")
    model_config = ConfigDict(extra="forbid")


class UserJSON(TimestampedJSON, UserBase):
    pass


async def ensure_constraints(
    data: UserCreate, session: AsyncSession, id: Optional[int] = None
) -> None:
    stmt = select(exists().where(UserModel.username == data.username))
    if id is not None:
        stmt = stmt.where(UserModel.id != id)

    invalid = (await session.execute(stmt)).scalar()
    if invalid:
        raise RequestValidationError(
            errors=[
                {
                    c.FA_FLD_LOC: (c.FA_FLD_BODY, c.WORD_USERNAME),
                    c.FA_FLD_MSG: f"{data.username} already exists.",
                    c.FA_FLD_TYPE: "value_error.user.username.exists",
                }
            ]
        )
