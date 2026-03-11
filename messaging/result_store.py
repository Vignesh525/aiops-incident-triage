import json
import os

import redis

from app_env import required_env


_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.Redis(
            host=required_env("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
        )
    return _client


def redis_ready() -> bool:
    try:
        return bool(_get_client().ping())
    except Exception:
        return False


def save_incident_result(incident_id: str, payload: dict):
    _get_client().set(f"incident:{incident_id}", json.dumps(payload))


def get_incident_result(incident_id: str):
    value = _get_client().get(f"incident:{incident_id}")
    if value is None:
        return None
    return json.loads(value)
