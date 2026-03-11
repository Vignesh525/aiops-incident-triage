import json
from typing import Any

import requests

from app_env import get_bool_env, get_json_env, get_env, required_env


_DEF_TIMEOUT = 15


def servicenow_enabled() -> bool:
    return get_bool_env("SERVICENOW_ENABLED", default=False)


def _assignment_group_map() -> dict[str, str]:
    return get_json_env("SERVICENOW_ASSIGNMENT_GROUP_MAP", default={}) or {}


def _build_auth() -> tuple[str, str]:
    return required_env("SERVICENOW_USERNAME"), required_env("SERVICENOW_PASSWORD")


def _base_url() -> str:
    return required_env("SERVICENOW_INSTANCE_URL").rstrip("/")


def _table_name() -> str:
    return get_env("SERVICENOW_TABLE", "incident")


def _incident_url(incident_sys_id: str) -> str:
    return f"{_base_url()}/api/now/table/{_table_name()}/{incident_sys_id}"


def _map_assignment_group(group_name: str | None) -> str | None:
    if not group_name:
        return None
    return _assignment_group_map().get(group_name)


def build_incident_update_payload(alert: dict[str, Any], triage_result: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "work_notes": triage_result.get("work_notes") or triage_result.get("triage_summary") or "AI triage completed.",
        "comments": triage_result.get("triage_summary") or "AI triage completed.",
        "priority": triage_result.get("recommended_priority", "3"),
    }

    assignment_group = _map_assignment_group(triage_result.get("recommended_assignment_group"))
    if assignment_group:
        payload["assignment_group"] = assignment_group

    if triage_result.get("resolution_recommended") and get_bool_env("SERVICENOW_AUTO_RESOLVE", default=False):
        payload["state"] = get_env("SERVICENOW_RESOLVED_STATE", "6")
        payload["close_notes"] = triage_result.get("triage_summary") or "Resolved by AI triage recommendation."
        payload["close_code"] = get_env("SERVICENOW_CLOSE_CODE", "Solved (Permanently)")

    servicenow_number = alert.get("servicenow_number")
    if servicenow_number:
        payload["work_notes"] = f"[AI Triage for {servicenow_number}]\n{payload['work_notes']}"

    return payload


def update_incident(incident_sys_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.patch(
        _incident_url(incident_sys_id),
        auth=_build_auth(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json=payload,
        timeout=_DEF_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def push_triage_update(alert: dict[str, Any], triage_result: dict[str, Any]) -> dict[str, Any] | None:
    if not servicenow_enabled():
        return None

    incident_sys_id = alert.get("servicenow_sys_id")
    if not incident_sys_id:
        return None

    payload = build_incident_update_payload(alert, triage_result)
    return update_incident(incident_sys_id, payload)
