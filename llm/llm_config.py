from crewai import LLM
from app_env import required_env


llm = LLM(
    model=required_env("MODEL_NAME"),
    base_url=required_env("OPENAI_BASE_URL"),
    api_key=required_env("OPENAI_API_KEY"),
)
