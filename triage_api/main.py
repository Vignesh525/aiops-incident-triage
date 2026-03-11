from uuid import uuid4

from fastapi import FastAPI, HTTPException
from kafka.errors import KafkaError, NoBrokersAvailable
from redis.exceptions import RedisError

from messaging.kafka_producer import kafka_ready, send_alert
from messaging.result_store import get_incident_result, redis_ready
from triage_api.models import IncidentAcceptedResponse, IncidentAlertIn

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    checks = {
        "kafka": kafka_ready(),
        "redis": redis_ready(),
    }
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks})
    return {"status": "ready", "checks": checks}


@app.post("/incident", response_model=IncidentAcceptedResponse)
def receive_incident(alert: IncidentAlertIn):
    incident_id = str(uuid4())
    alert_with_id = {"incident_id": incident_id, **alert.as_payload()}

    try:
        send_alert(alert_with_id)
    except NoBrokersAvailable as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Kafka broker is unreachable. Check KAFKA_BOOTSTRAP_SERVERS for the runtime environment. "
                "If the API is running in Docker and Kafka is on the host, use host.docker.internal:9092 instead of localhost:9092."
            ),
        ) from exc
    except KafkaError as exc:
        raise HTTPException(status_code=503, detail=f"Kafka publish failed: {exc}") from exc

    return IncidentAcceptedResponse(status="alert received and queued", incident_id=incident_id)


@app.get("/incident/{incident_id}")
def get_incident(incident_id: str):
    try:
        result = get_incident_result(incident_id)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail=f"Result store unavailable: {exc}") from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Incident result not found")

    return result
