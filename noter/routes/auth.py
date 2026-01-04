from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import noter.utils.constants as c
from noter.models.db.meta import get_session
from noter.models.db.user import User
from noter.models.val.user import UserCreate, ensure_constraints
from noter.utils.auth import create_token, hash_password, verify_password

router = APIRouter()


@router.post("/sign-up/")
async def sign_up(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    await ensure_constraints(data, session)
    user = User.from_data(
        {
            c.WORD_USERNAME: data.username,
            c.COL_PASSWD_HASH: hash_password(data.password),
        }
    )
    session.add(user)
    await session.commit()
    token = create_token({c.WORD_ID: user.id, c.WORD_USERNAME: user.username})
    return {"token": token}


@router.post("/sign-in/")
async def sign_in(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(User.username == data.username)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None or not verify_password(data.password, user.passwd_hash):
        raise HTTPException(
            status_code=422, detail={c.WORD_MESSAGE: "Invalid credentials"}
        )
    token = create_token({c.WORD_ID: user.id, c.WORD_USERNAME: user.username})
    return {"token": token}
