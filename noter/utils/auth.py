from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import noter.utils.environ as env

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=1,
)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- JWT stuff ---


class AuthUser(BaseModel):
    id: int
    username: str


def create_token(
    data: dict, expire_in: timedelta = timedelta(hours=24)
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_in
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, env.JWT_SECRET, algorithm=env.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, env.JWT_SECRET, algorithms=[env.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401)


async def require_auth(token: str = Depends(oauth_scheme)) -> AuthUser:
    return AuthUser(**verify_token(token))


# --- Password stuff ---


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)
