# Kubernetes Deployment Guide

## What this directory contains

This directory provides a production-oriented baseline for deploying the project on Kubernetes.

Included resources:
- `00-namespace.yaml`
- `01-configmap.yaml`
- `02-secret.example.yaml`
- `03-api-service.yaml`
- `04-api-deployment.yaml`
- `05-worker-deployment.yaml`
- `06-api-hpa.yaml`
- `07-worker-hpa.yaml`
- `08-api-pdb.yaml`
- `09-worker-pdb.yaml`
- `10-ingress.yaml`
- `kustomization.yaml`

## Deployment model

These manifests assume:
- Kafka is already available in the cluster or through a managed service
- Redis is already available in the cluster or through a managed service
- You will push the application image to a real container registry
- You will provide the OpenAI-compatible API key as a Kubernetes Secret

The manifests do not deploy Kafka or Redis themselves. For production scale, managed or dedicated stateful infrastructure is the safer default.

## 1. Build and push the image

Example:

```powershell
docker build -t ghcr.io/your-org/aiops-incident-triage:latest .
docker push ghcr.io/your-org/aiops-incident-triage:latest
```

Then update both deployment files to use your real image reference.

## 2. Configure external service endpoints

Edit `01-configmap.yaml` and set:
- `KAFKA_BOOTSTRAP_SERVERS`
- `REDIS_HOST`
- `REDIS_PORT`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

## 3. Create the runtime secret

You can either copy `02-secret.example.yaml` and apply it after replacing the placeholder value, or create the secret directly:

```powershell
kubectl create namespace aiops-triage
kubectl -n aiops-triage create secret generic aiops-triage-secrets --from-literal=OPENAI_API_KEY=your-real-key
```

## 4. Apply the manifests

```powershell
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/03-api-service.yaml
kubectl apply -f k8s/04-api-deployment.yaml
kubectl apply -f k8s/05-worker-deployment.yaml
kubectl apply -f k8s/06-api-hpa.yaml
kubectl apply -f k8s/07-worker-hpa.yaml
kubectl apply -f k8s/08-api-pdb.yaml
kubectl apply -f k8s/09-worker-pdb.yaml
kubectl apply -f k8s/10-ingress.yaml
```

Or use kustomize-compatible apply:

```powershell
kubectl apply -k k8s
```

Note: `02-secret.example.yaml` is intentionally not referenced by `kustomization.yaml` because it contains a placeholder secret.

## 5. Verify the rollout

```powershell
kubectl -n aiops-triage get pods
kubectl -n aiops-triage get svc
kubectl -n aiops-triage get ingress
kubectl -n aiops-triage get hpa
```

## 6. Probe behavior

The API deployment uses:
- `/healthz` for liveness
- `/readyz` for readiness

Readiness checks confirm both Kafka and Redis are reachable before the pod is marked ready.

## 7. Scaling behavior

- API starts at 3 replicas and autoscale can increase it to 10.
- Worker starts at 2 replicas and autoscale can increase it to 10.
- PodDisruptionBudgets reduce the risk of voluntary disruption during node maintenance.

## 8. Production follow-ups still recommended

This manifest set is a strong baseline, but a real production rollout should also consider:
- registry credentials and imagePullSecrets
- TLS certificates for ingress
- network policies
- centralized logging and metrics
- secret rotation
- external-dns or ingress automation
- Kafka topic management and retention policies
- Redis persistence and high availability
- node affinity / taints if workloads must be isolated
