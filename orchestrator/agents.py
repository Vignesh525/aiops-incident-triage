from crewai import Agent
from llm.llm_config import llm

qualification_agent = Agent(
    role="Incident Qualification Engineer",
    goal="Determine if monitoring alert is real or noise",
    backstory="Expert in alert analysis",
    llm=llm,
    verbose=True
)

enrichment_agent = Agent(
    role="Incident Enrichment Engineer",
    goal="Collect additional context",
    backstory="Monitoring and observability specialist",
    llm=llm,
    verbose=True
)

impact_agent = Agent(
    role="Impact Analysis Engineer",
    goal="Determine service impact",
    backstory="Expert in service dependency mapping",
    llm=llm,
    verbose=True
)

routing_agent = Agent(
    role="Incident Routing Engineer",
    goal="Determine which team should receive incident",
    backstory="IT operations routing expert",
    llm=llm,
    verbose=True
)