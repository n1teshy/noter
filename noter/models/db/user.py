from sqlalchemy.orm import Mapped, mapped_column, relationship

import noter.utils.constants as c
from noter.models.db.meta import BaseModel


class User(BaseModel):
    __tablename__ = c.TBL_USERS
    basic_json_map = {
        **{wd: wd for wd in [c.WORD_ID, c.WORD_USERNAME]},
        c.FLD_CREATED_AT: lambda user: user.created_at.isoformat(),
        c.FLD_UPDATED_AT: lambda user: user.updated_at.isoformat(),
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        nullable=False, unique=True, index=True
    )
    passwd_hash: Mapped[str] = mapped_column(nullable=False)

    notes = relationship("Note", back_populates="author", lazy="selectin")

    @staticmethod
    def from_data(data: dict) -> "User":
        return User(**data)
