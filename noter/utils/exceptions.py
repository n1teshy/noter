from fastapi import HTTPException
from starlette import status


def unprocessable_entities(errors: list):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=errors,
    )
