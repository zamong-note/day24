from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from ...callbacks import progress_callback
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
    before_agent_callback=progress_callback("📝 스토리 작성 중..."),
    after_agent_callback=progress_callback("✅ 스토리 작성 완료!"),
)
