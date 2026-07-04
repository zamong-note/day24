import json
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, Context, InvocationContext
from google.adk.events.event import Event
from google.genai import types

from ...callbacks import progress_callback

STORYBOOK_REVEAL_DESCRIPTION = (
    "PageComposerTeam이 만든 storybook_page_N.png들을 1페이지부터 5페이지까지 정해진 순서로 "
    "하나씩 공개합니다. IllustratorTeam과 PageComposerTeam은 속도를 위해 5페이지를 동시에 "
    "처리하므로 완료 순서가 뒤섞일 수 있는데, 이 에이전트가 항상 페이지 번호 순서로 최종 결과를 "
    "보여준다."
)


class StorybookRevealAgent(BaseAgent):
    """제목과 5개 페이지(텍스트+이미지)를 페이지 번호 순서대로 하나씩 이벤트로 내보내는 에이전트."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        callback_context = Context(ctx)

        story_data = callback_context.state.get("story_data")
        if not story_data:
            return
        if isinstance(story_data, str):
            story_data = json.loads(story_data)

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"# {story_data.get('title', '')}")],
            ),
        )

        pages = sorted(
            story_data.get("pages", []), key=lambda page: page.get("page_number", 0)
        )
        for page in pages:
            page_number = page.get("page_number")
            filename = f"storybook_page_{page_number}.png"

            parts = [
                types.Part(text=f"## {page_number}페이지\n{page.get('text', '')}")
            ]
            image_artifact = await callback_context.load_artifact(filename=filename)
            if image_artifact is not None:
                parts.append(image_artifact)

            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(role="model", parts=parts),
            )


storybook_reveal_agent = StorybookRevealAgent(
    name="StorybookRevealAgent",
    description=STORYBOOK_REVEAL_DESCRIPTION,
    before_agent_callback=progress_callback("📖 완성된 동화책을 1페이지부터 순서대로 보여드릴게요..."),
)
