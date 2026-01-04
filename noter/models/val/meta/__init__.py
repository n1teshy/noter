from pydantic import BaseModel


class IdentifiedJSON(BaseModel):
    id: int


class TimestampedJSON(IdentifiedJSON):
    createdAt: str
    updatedAt: str
