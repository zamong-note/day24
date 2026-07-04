from google.adk.agents import SequentialAgent

from .callbacks import build_final_storybook_callback, progress_callback
from .prompt import STORY_BOOK_DESCRIPTION
from .sub_agents.writer_agent.agent import writer_agent
from .sub_agents.illustrator_agent.agent import illustrator_team
from .sub_agents.page_composer_agent.agent import page_composer_team

story_book_agent = SequentialAgent(
    name="StoryBookAgent",
    description=STORY_BOOK_DESCRIPTION,
    sub_agents=[writer_agent, illustrator_team, page_composer_team],
    before_agent_callback=progress_callback("🎨 동화책 제작을 시작합니다..."),
    after_agent_callback=build_final_storybook_callback(),
)

root_agent = story_book_agent
