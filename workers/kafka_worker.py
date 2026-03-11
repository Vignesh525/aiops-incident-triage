import json

from kafka import KafkaConsumer

from app_env import required_env
from messaging.kafka_producer import publish_triage_result
from messaging.result_store import save_incident_result
from orchestrator.crew import run_triage


def build_consumer():
    return KafkaConsumer(
        "incident-alerts",
        bootstrap_servers=required_env("KAFKA_BOOTSTRAP_SERVERS"),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )


def _serialize_triage_result(result):
    if hasattr(result, "raw"):
        return result.raw
    if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
        return result
    return str(result)


def main():
    consumer = build_consumer()

    for message in consumer:
        alert = message.value
        incident_id = alert.get("incident_id", "unknown")
        print("Received alert:", alert)

        try:
            triage_result = run_triage(alert)
            result_payload = {
                "incident_id": incident_id,
                "status": "completed",
                "alert": alert,
                "triage_result": _serialize_triage_result(triage_result),
            }
        except Exception as exc:
            result_payload = {
                "incident_id": incident_id,
                "status": "failed",
                "alert": alert,
                "error": str(exc),
            }

        save_incident_result(incident_id, result_payload)
        publish_triage_result(result_payload)
        print("Triage Result:", result_payload)


if __name__ == "__main__":
    main()
