from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .prompt import STORY_WRITER_DESCRIPTION, STORY_WRITER_PROMPT
from .schemas import Story

MODEL = LiteLlm(model="openai/gpt-4o")

writer_agent = Agent(
    name="StoryWriterAgent",
    model=MODEL,
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_PROMPT,
    output_schema=Story,
    output_key="story_data",
)
