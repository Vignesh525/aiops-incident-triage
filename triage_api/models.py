from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IncidentAlertIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    servicenow_sys_id: str = Field(..., description="ServiceNow sys_id of the incident to update")
    servicenow_number: str = Field(..., description="Human-readable ServiceNow incident number")
    severity: Literal["critical", "high", "medium", "low"]
    alert: str | None = None
    alert_name: str | None = None
    service: str | None = None
    host: str | None = None
    metric: str | None = None
    value: str | None = None
    filesystem: str | None = None
    timestamp: str | None = None

    @field_validator("servicenow_sys_id", "servicenow_number")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    def as_payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class IncidentAcceptedResponse(BaseModel):
    status: str
    incident_id: str
