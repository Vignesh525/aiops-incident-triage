from crewai import Crew
from orchestrator.tasks import (
    qualification_task,
    enrichment_task,
    impact_task,
    routing_task,
)


def _serialize_result(result):
    if hasattr(result, "raw"):
        return result.raw
    if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
        return result
    return str(result)


def _infer_valid_alert(raw_text: str) -> bool:
    text = raw_text.lower()
    negative_markers = ["likely noise", "false positive", "test alert", "non-production"]
    return not any(marker in text for marker in negative_markers)


def _infer_assignment_group(alert: dict, raw_text: str) -> str:
    text = raw_text.lower()
    if "infrastructure operations" in text:
        return "Infrastructure Operations"
    if "database" in text or alert.get("metric") in {"disk_usage", "disk_iops"}:
        return "Database Operations"
    if "payments" in str(alert.get("service", "")).lower():
        return "Payments Platform"
    if "checkout" in str(alert.get("service", "")).lower():
        return "Commerce Platform"
    if "quality assurance" in text or "development" in text:
        return "Development/Quality Assurance"
    return "Site Reliability Engineering"


def _infer_priority(alert: dict, valid_alert: bool) -> str:
    severity = str(alert.get("severity", "medium")).lower()
    if not valid_alert:
        return "4"
    return {
        "critical": "1",
        "high": "2",
        "medium": "3",
        "low": "4",
    }.get(severity, "3")


def _summarize(raw_text: str, limit: int = 280) -> str:
    clean = " ".join(raw_text.split())
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."


def build_structured_triage_result(alert: dict, triage_result) -> dict:
    raw_output = _serialize_result(triage_result)
    raw_text = raw_output if isinstance(raw_output, str) else str(raw_output)
    valid_alert = _infer_valid_alert(raw_text)
    assignment_group = _infer_assignment_group(alert, raw_text)
    priority = _infer_priority(alert, valid_alert)
    resolution_recommended = not valid_alert
    recommended_action = "resolve" if resolution_recommended else "reassign"

    return {
        "triage_summary": _summarize(raw_text),
        "valid_alert": valid_alert,
        "recommended_assignment_group": assignment_group,
        "recommended_priority": priority,
        "recommended_action": recommended_action,
        "resolution_recommended": resolution_recommended,
        "work_notes": raw_text,
        "raw_model_output": raw_output,
    }


def run_triage(alert):
    tasks = [
        qualification_task(alert),
        enrichment_task(),
        impact_task(),
        routing_task(),
    ]

    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        verbose=True,
    )

    triage_result = crew.kickoff()
    return build_structured_triage_result(alert, triage_result)
