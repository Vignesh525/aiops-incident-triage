from crewai import Crew
from orchestrator.tasks import (
    qualification_task,
    enrichment_task,
    impact_task,
    routing_task
)

def run_triage(alert):

    tasks = [
        qualification_task(alert),
        enrichment_task(),
        impact_task(),
        routing_task()
    ]

    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        verbose=True
    )

    return crew.kickoff()