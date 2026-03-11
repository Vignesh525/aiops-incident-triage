# Sample Payloads

This folder contains reusable JSON payloads for testing the FastAPI incident endpoint.

## Files

- `servicenow_incident_payload.json`
  Critical database disk usage incident.

- `servicenow_incident_payload_low.json`
  Lower-severity incident that can be used to test a likely-noise or lower-priority path.

## Submit a sample payload

### Critical example

```powershell
$body = Get-Content samples\servicenow_incident_payload.json -Raw
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/incident -ContentType "application/json" -Body $body
$response
```

### Lower-severity example

```powershell
$body = Get-Content samples\servicenow_incident_payload_low.json -Raw
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/incident -ContentType "application/json" -Body $body
$response
```

## Fetch the result

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/incident/$($response.incident_id)"
```

## Watch worker logs

```powershell
docker compose logs -f worker
```
