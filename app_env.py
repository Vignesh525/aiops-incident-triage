import json
import os
from pathlib import Path

from dotenv import load_dotenv


_ROOT_DOTENV = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ROOT_DOTENV, override=False)


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def required_env(name: str) -> str:
    value = get_env(name)
    if not value:
        raise ValueError(f"{name} is missing. Set it in .env or pass it as an environment variable.")
    return value


def get_bool_env(name: str, default: bool = False) -> bool:
    value = get_env(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def get_json_env(name: str, default=None):
    value = get_env(name)
    if value is None:
        return default
    return json.loads(value)
