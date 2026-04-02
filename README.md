# AIOps Incident Triage Crew

An event-driven AI incident triage system that accepts monitoring alerts, queues them through Kafka, processes them with a CrewAI multi-agent workflow, stores the result in Redis, and exposes the final outcome through a FastAPI endpoint.

## Overview


This project is an AI-assisted incident triage platform.

Instead of sending every monitoring alert directly to an engineer for manual review, the system:
- receives the alert through an API
- queues it through Kafka
- processes it asynchronously using a multi-agent AI workflow
- determines likely validity, impact, and routing
- stores the result for retrieval
- can now attempt to push the triage decision back to the same ServiceNow incident automatically

In practical terms, it acts as an intelligent first-line incident analyst.

Technical  flow is:

1. A client sends an alert to the API.
2. The API generates an `incident_id` and publishes the alert to Kafka.
3. A worker consumes the alert and runs a CrewAI workflow.
4. The workflow evaluates the alert across multiple agent roles.
5. The worker stores the result in Redis.
6. The worker also publishes the final result to a Kafka results topic.
7. The API exposes the result through a lookup endpoint.

## Architecture

### Runtime components

- `api`
  FastAPI service that accepts alerts and returns triage results.

- `worker`
  Kafka consumer that executes the CrewAI triage workflow.

- `kafka`
  Message broker used to decouple ingestion from processing.

- `redis`
  Result store used for incident lookup by `incident_id`.

### Code structure

- `app_env.py`
  Shared environment loading and validation.

- `llm/`
  LLM configuration for CrewAI.

- `triage_api/`
  HTTP API entrypoints.

- `messaging/`
  Kafka publishing and Redis result persistence.

- `workers/`
  Background worker logic.

- `orchestrator/`
  Agent, task, and crew definitions.

- `integrations/`
  Placeholder adapters for monitoring and ITSM integrations.

- `docker-compose.yml`
  Local distributed runtime with API, worker, Kafka, and Redis.

- `k8s/`
  Production-oriented Kubernetes manifests, autoscaling, probes, disruption budgets, and ingress baseline.

## Agent Workflow

The CrewAI orchestration currently models triage as four agent roles:

- `Incident Qualification Engineer`
  Determines whether the alert looks valid or likely noise.

- `Incident Enrichment Engineer`
  Adds supporting context around the incident.

- `Impact Analysis Engineer`
  Assesses severity and possible customer or service impact.

- `Incident Routing Engineer`
  Determines the team that should handle the incident.

These agents are defined in `orchestrator/agents.py`, and their task definitions live in `orchestrator/tasks.py`.

## Technology Stack

### Python
Used as the implementation language for the entire system. It fits well for API development, messaging, and AI orchestration.

### FastAPI
Used for the HTTP layer. It provides the `POST /incident` and `GET /incident/{incident_id}` endpoints.

### Uvicorn
Runs the FastAPI application inside the API container.

### CrewAI
Provides the multi-agent orchestration model that drives alert qualification, enrichment, impact assessment, and routing.

### OpenAI-compatible LLM endpoint
Provides the reasoning backend for CrewAI agents. The project currently uses values from `.env` for model name, base URL, and API key.

### Kafka
Acts as the event backbone of the system.

Topics currently used:
- `incident-alerts`
- `incident-triage-results`

### Redis
Stores incident result payloads so they can be fetched later through the API.

### Docker
Packages the Python application into a reusable container image.

### Docker Compose
Runs the full local stack so the distributed workflow can be tested end to end.

### Kubernetes
A production-oriented baseline now exists under `k8s/`, including namespace, config, secret template, API and worker deployments, HPA, PDB, service, ingress, and deployment guidance.

## API Endpoints

### `GET /healthz`
Simple liveness endpoint for container and Kubernetes health checks.

### `GET /readyz`
Readiness endpoint that checks Kafka and Redis connectivity.

### `POST /incident`
Accepts an alert payload, assigns an `incident_id`, and queues it for processing.

Example request:

```json
{
  "alert_name": "Disk Saturation",
  "service": "orders",
  "severity": "high"
}
```

Example response:

```json
{
  "status": "alert received and queued",
  "incident_id": "e7f51fc8-0090-4a84-b993-7b67a2bf58c6"
}
```

### `GET /incident/{incident_id}`
Returns the stored result payload for the incident.

Example response:

```json
{
  "incident_id": "e7f51fc8-0090-4a84-b993-7b67a2bf58c6",
  "status": "completed",
  "alert": {
    "incident_id": "e7f51fc8-0090-4a84-b993-7b67a2bf58c6",
    "alert_name": "Disk Saturation",
    "service": "orders",
    "severity": "high"
  },
  "triage_result": "The team that should receive the incident is the Infrastructure Operations Team ..."
}
```

## Local Setup

### Prerequisites

- Docker Desktop or a compatible Docker runtime
- Docker Compose support
- A valid LLM API key and endpoint in `.env`

### Environment variables

The project reads configuration from `.env`.

Current required values include:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`
- `KAFKA_BOOTSTRAP_SERVERS`
- `REDIS_HOST`

When using Docker Compose, Kafka and Redis hostnames are overridden internally to use service names:
- `kafka:9092`
- `redis`

### Start the stack

```powershell
docker compose up --build -d
```

### Check service status

```powershell
docker compose ps
```

### Follow logs

```powershell
docker compose logs -f api worker kafka redis
```

## End-to-End Validation

### 1. Submit an incident

```powershell
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/incident `
  -ContentType 'application/json' `
  -Body '{"alert_name":"Disk Saturation","service":"orders","severity":"high"}'

$response.incident_id
```

### 2. Fetch the result

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/incident/$($response.incident_id)"
```

If the worker has not finished yet, you may briefly receive `404 Incident result not found`. Retry after a few seconds.

## Kubernetes Deployment

Use the production baseline under `k8s/`.

Key additions there:
- namespace and config separation
- secret template for API credentials
- API deployment with liveness and readiness probes
- worker deployment with separate scaling
- HorizontalPodAutoscalers for API and worker
- PodDisruptionBudgets
- ClusterIP service and ingress
- deployment guide in `k8s/README.md`

Typical flow:

```powershell
docker build -t ghcr.io/your-org/aiops-incident-triage:latest .
docker push ghcr.io/your-org/aiops-incident-triage:latest
kubectl apply -k k8s
```

Before applying, update:
- image references in the deployment manifests
- Kafka and Redis endpoints in `k8s/01-configmap.yaml`
- the real API key secret in the cluster

## Current Implementation Notes

### What works now

- Alert ingestion through FastAPI
- Kafka-backed asynchronous processing
- CrewAI-based multi-agent triage
- Redis-backed result lookup
- Result publishing to a Kafka results topic
- Local multi-container deployment through Docker Compose
- Kubernetes-ready liveness/readiness support in the API
- Production-oriented Kubernetes baseline manifests

### Current limitations

- Input payloads are not yet defined with strict Pydantic models
- Monitoring and ServiceNow integrations are still placeholders
- Result payloads are simple JSON blobs rather than a formal domain schema
- Kubernetes manifests assume external Kafka and Redis rather than deploying them
- No authentication, authorization, or audit-grade persistence layer yet

## Deployment Files

### `dockerfile`
Defines the Python application image used by both the API and worker services.

### `docker-compose.yml`
Defines the local distributed stack:
- Kafka broker
- Redis
- FastAPI API
- Worker consumer

### `k8s/`
Defines the production-oriented Kubernetes baseline for scalable API and worker deployment.

## Future Improvements

Natural next steps for the project include:

- Add request and response models with Pydantic
- Pass richer task outputs between agents
- Connect live integrations for metrics, logs, and ticketing
- Automatically create ITSM incidents after routing
- Add a result listing endpoint or dashboard
- Add structured logging and observability
- Complete production networking, TLS, image pull secrets, and policy hardening

## Detailed Explanation

A longer project document is also available at:

- `PROJECT_DETAILED_EXPLANATION.txt`

That file contains a more exhaustive breakdown of each component, module, and technology choice.
