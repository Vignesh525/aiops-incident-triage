import os
from pathlib import Path

from dotenv import load_dotenv


_ROOT_DOTENV = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ROOT_DOTENV, override=False)


def required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise ValueError(f"{name} is missing. Set it in .env or pass it as an environment variable.")
    return value
