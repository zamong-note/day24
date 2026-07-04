import base64
import json

from google.genai import types
from openai import OpenAI, BadRequestError
from google.adk.tools.tool_context import ToolContext

client = OpenAI()

STYLE_SUFFIX = (
    ", children's picture book illustration, soft colors, simple shapes, "
    "warm and friendly style"
)

# gpt-image-1's moderation system occasionally rejects innocuous prompts with a
# false positive; a retry with the same prompt usually succeeds.
MAX_ATTEMPTS = 2


def _find_page(story_data: dict, page_number: int) -> dict | None:
    for page in story_data.get("pages", []):
        if page.get("page_number") == page_number:
            return page
    return None


async def _generate_and_save_page(page: dict, tool_context: ToolContext) -> dict:
    page_number = page.get("page_number")
    text = page.get("text")
    visual_description = page.get("visual_description")
    filename = f"page_{page_number}.png"

    page_result = {
        "page_number": page_number,
        "text": text,
        "visual_description": visual_description,
        "filename": filename,
        "status": "complete",
    }

    existing_artifacts = await tool_context.list_artifacts()
    if filename in existing_artifacts:
        return page_result

    image = None
    last_error = None
    for _ in range(MAX_ATTEMPTS):
        try:
            image = client.images.generate(
                model="gpt-image-1",
                prompt=f"{visual_description}{STYLE_SUFFIX}",
                n=1,
                quality="low",
                output_format="png",
                size="1024x1024",
            )
            break
        except BadRequestError as error:
            last_error = error

    if image is None:
        page_result["status"] = "failed"
        page_result["filename"] = None
        page_result["error"] = str(last_error)
        return page_result

    image_bytes = base64.b64decode(image.data[0].b64_json)

    artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes,
        )
    )

    await tool_context.save_artifact(filename=filename, artifact=artifact)

    return page_result


def make_page_illustration_tool(page_number: int):
    """지정된 page_number 하나만 담당하는 삽화 생성 도구를 만든다.

    ParallelAgent의 각 서브 에이전트가 서로 다른 페이지를 동시에 처리할 수 있도록
    page_number를 클로저로 고정한 전용 도구를 생성한다.
    """

    async def generate_illustration(tool_context: ToolContext):
        story_data = tool_context.state.get("story_data")
        if not story_data:
            return {
                "status": "error",
                "message": "story_data가 State에 없습니다. StoryWriterAgent를 먼저 실행하세요.",
            }

        if isinstance(story_data, str):
            story_data = json.loads(story_data)

        page = _find_page(story_data, page_number)
        if page is None:
            return {
                "status": "error",
                "message": f"{page_number}페이지 데이터를 story_data에서 찾을 수 없습니다.",
            }

        return await _generate_and_save_page(page, tool_context)

    generate_illustration.__name__ = f"generate_illustration_page_{page_number}"
    generate_illustration.__doc__ = (
        f"story_data에 저장된 {page_number}페이지 정보를 읽어 삽화를 생성하고 Artifact로 저장한다."
    )
    return generate_illustration
