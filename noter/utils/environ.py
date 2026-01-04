import os
from typing import Any, Callable, Optional

from dotenv import load_dotenv

load_dotenv()


def check_env(
    key: str, convert: Optional[Callable] = None, optional: bool = False
) -> Any:
    value = os.getenv(key)
    if value is None:
        if optional:
            return None
        raise EnvironmentError(f"Environment variable '{key}' is not set.")
    return convert(value) if convert else value


DB_URI = check_env("DB_URI")
JWT_SECRET = check_env("JWT_SECRET")
JWT_ALGORITHM = check_env("JWT_ALGORITHM", optional=True) or "HS256"
