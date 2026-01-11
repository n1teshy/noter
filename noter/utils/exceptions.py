from typing import Optional, Union


class AppException(Exception):
    def __init__(
        self, status: int, payload: Optional[Union[list, dict]] = None
    ):
        self.status = status
        self.payload = payload
