from google.adk.agents import Agent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm

from ...callbacks import progress_callback
from .prompt import PAGE_COMPOSER_DESCRIPTION, PAGE_COMPOSER_PAGE_PROMPT
from .tools import make_page_composer_tool

MODEL = LiteLlm(model="openai/gpt-4o")
NUM_PAGES = 5


def _build_page_composer(page_number: int) -> Agent:
    return Agent(
        name=f"PageComposerPage{page_number}",
        model=MODEL,
        description=f"동화책 {page_number}페이지의 삽화와 텍스트를 합성합니다.",
        instruction=PAGE_COMPOSER_PAGE_PROMPT.format(page_number=page_number),
        tools=[make_page_composer_tool(page_number)],
        output_key=f"storybook_page_{page_number}_status",
        before_agent_callback=progress_callback(f"📚 {page_number}페이지 합성 중..."),
        after_agent_callback=progress_callback(f"✅ {page_number}페이지 합성 완료!"),
    )


page_composer_team = ParallelAgent(
    name="PageComposerTeam",
    description=PAGE_COMPOSER_DESCRIPTION,
    sub_agents=[_build_page_composer(n) for n in range(1, NUM_PAGES + 1)],
    before_agent_callback=progress_callback("📖 삽화와 텍스트를 합쳐 동화책 페이지 5장을 동시에 만듭니다..."),
    after_agent_callback=progress_callback("🎉 모든 동화책 페이지가 완성되었습니다!"),
)
