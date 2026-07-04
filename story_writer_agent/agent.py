from google.adk.agents import SequentialAgent

from .callbacks import progress_callback
from .prompt import STORY_BOOK_DESCRIPTION
from .sub_agents.writer_agent.agent import writer_agent
from .sub_agents.illustrator_agent.agent import illustrator_team
from .sub_agents.page_composer_agent.agent import page_composer_team
from .sub_agents.storybook_reveal_agent.agent import storybook_reveal_agent

story_book_agent = SequentialAgent(
    name="StoryBookAgent",
    description=STORY_BOOK_DESCRIPTION,
    sub_agents=[
        writer_agent,
        illustrator_team,
        page_composer_team,
        storybook_reveal_agent,
    ],
    before_agent_callback=progress_callback("🎨 동화책 제작을 시작합니다..."),
    after_agent_callback=progress_callback("🎉 동화책이 완성되었습니다!"),
)

root_agent = story_book_agent
