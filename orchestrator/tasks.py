from crewai import Task
from orchestrator.agents import (
    qualification_agent,
    enrichment_agent,
    impact_agent,
    routing_agent,
)


def qualification_task(alert):
    return Task(
        description=f"""
Determine if this alert is valid:

{alert}
""",
        expected_output="A short assessment stating whether the alert is valid or likely noise, with supporting reasoning.",
        agent=qualification_agent,
    )


def enrichment_task():
    return Task(
        description="""
Gather additional context:
host
metrics
related alerts
""",
        expected_output="A concise summary of additional incident context including host details, metrics, and related alerts.",
        agent=enrichment_agent,
    )


def impact_task():
    return Task(
        description="""
Determine severity and customer impact
""",
        expected_output="A severity assessment and a summary of likely customer impact.",
        agent=impact_agent,
    )


def routing_task():
    return Task(
        description="""
Determine responsible team
""",
        expected_output="The team that should receive the incident, with a brief justification.",
        agent=routing_agent,
    )
