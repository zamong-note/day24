from google.adk.agents import SequentialAgent

from .prompt import STORY_BOOK_DESCRIPTION
from .sub_agents.writer_agent.agent import writer_agent
from .sub_agents.illustrator_agent.agent import illustrator_agent

story_book_agent = SequentialAgent(
    name="StoryBookAgent",
    description=STORY_BOOK_DESCRIPTION,
    sub_agents=[writer_agent, illustrator_agent],
)

root_agent = story_book_agent
