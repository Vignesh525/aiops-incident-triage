# aiops-triage Helm Chart

This chart packages the AIOps Incident Triage Crew application for Kubernetes.

## What it deploys

- FastAPI API deployment
- Worker deployment
- ClusterIP service for the API
- ConfigMap for runtime settings
- Optional Secret for the OpenAI-compatible API key
- Optional Ingress
- Optional HPA for API and worker
- Optional PodDisruptionBudgets

## Important assumptions

This chart assumes Kafka and Redis are already available as external or separately managed services.

Set these values before deployment:
- `config.kafkaBootstrapServers`
- `config.redisHost`
- `config.redisPort`
- `config.openaiBaseUrl`
- `config.modelName`

## Install example

```powershell
helm install aiops-triage ./helm/aiops-triage `
  --namespace aiops-triage `
  --create-namespace `
  --set image.repository=ghcr.io/your-org/aiops-incident-triage `
  --set image.tag=latest `
  --set config.kafkaBootstrapServers=kafka-bootstrap.kafka.svc.cluster.local:9092 `
  --set config.redisHost=redis-master.redis.svc.cluster.local `
  --set secret.openaiApiKey=your-real-key
```

## Use an existing secret

```powershell
helm install aiops-triage ./helm/aiops-triage `
  --namespace aiops-triage `
  --create-namespace `
  --set existingSecret=aiops-triage-secrets `
  --set secret.create=false
```

That secret must contain:
- `OPENAI_API_KEY`

## Render templates locally

```powershell
helm template aiops-triage ./helm/aiops-triage
```

## Upgrade

```powershell
helm upgrade aiops-triage ./helm/aiops-triage --namespace aiops-triage
```
