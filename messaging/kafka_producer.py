import json
from kafka import KafkaProducer

from app_env import required_env


_producer = None


def _get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=required_env("KAFKA_BOOTSTRAP_SERVERS"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return _producer


def kafka_ready() -> bool:
    try:
        return bool(_get_producer().bootstrap_connected())
    except Exception:
        return False


def send_message(topic: str, payload: dict):
    producer = _get_producer()
    producer.send(topic, payload)
    producer.flush()


def send_alert(alert: dict):
    send_message("incident-alerts", alert)


def publish_triage_result(result: dict):
    send_message("incident-triage-results", result)
