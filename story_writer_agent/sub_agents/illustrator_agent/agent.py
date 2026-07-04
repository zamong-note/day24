from google.adk.agents import Agent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm

from ...callbacks import page_progress_callbacks, progress_callback
from .prompt import ILLUSTRATOR_DESCRIPTION, ILLUSTRATOR_PAGE_PROMPT
from .tools import make_page_illustration_tool

MODEL = LiteLlm(model="openai/gpt-4o")
NUM_PAGES = 5


def _build_page_illustrator(page_number: int) -> Agent:
    before_cb, after_cb = page_progress_callbacks(page_number, NUM_PAGES)
    return Agent(
        name=f"IllustratorPage{page_number}",
        model=MODEL,
        description=f"동화책 {page_number}페이지의 삽화만 담당하는 삽화가입니다.",
        instruction=ILLUSTRATOR_PAGE_PROMPT.format(page_number=page_number),
        tools=[make_page_illustration_tool(page_number)],
        output_key=f"illustration_page_{page_number}",
        before_agent_callback=before_cb,
        after_agent_callback=after_cb,
    )


illustrator_team = ParallelAgent(
    name="IllustratorTeam",
    description=ILLUSTRATOR_DESCRIPTION,
    sub_agents=[_build_page_illustrator(n) for n in range(1, NUM_PAGES + 1)],
    before_agent_callback=progress_callback("🖼️ 삽화 5개를 동시에 생성합니다..."),
    after_agent_callback=progress_callback("🎉 모든 삽화 생성이 끝났습니다!"),
)
