from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import noter.utils.constants as c
import noter.utils.environ as env
from noter.utils.datetime import utc_now
from noter.utils.db import add_sql_logging

add_sql_logging()
engine = create_async_engine(env.DB_URI)


class BaseModel(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    def to_json(self, fld_to_col_map: str = c.WORD_BASIC) -> dict:
        mapping: dict = getattr(
            self.__class__, f"{fld_to_col_map}_json_map", None
        )
        assert mapping is not None, f"{fld_to_col_map}_json_map not found"
        return {
            fld: col(self) if callable(col) else getattr(self, col)
            for fld, col in mapping.items()
        }


SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
            if session.new or session.dirty or session.deleted:
                await session.commit()
        except Exception:
            await session.rollback()
            raise
