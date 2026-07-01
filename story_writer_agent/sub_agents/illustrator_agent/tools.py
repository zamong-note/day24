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


async def generate_illustrations(tool_context: ToolContext):
    """StoryWriterAgent가 State에 남긴 story_data를 읽어 페이지별 삽화를 생성한다."""

    story_data = tool_context.state.get("story_data")
    if not story_data:
        return {
            "status": "error",
            "message": "story_data가 State에 없습니다. StoryWriterAgent를 먼저 실행하세요.",
        }

    if isinstance(story_data, str):
        story_data = json.loads(story_data)

    pages = story_data.get("pages", [])
    existing_artifacts = await tool_context.list_artifacts()

    illustrated_pages = []

    for page in pages:
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

        if filename not in existing_artifacts:
            image = None
            last_error = None
            for attempt in range(MAX_ATTEMPTS):
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
                illustrated_pages.append(page_result)
                continue

            image_bytes = base64.b64decode(image.data[0].b64_json)

            artifact = types.Part(
                inline_data=types.Blob(
                    mime_type="image/png",
                    data=image_bytes,
                )
            )

            await tool_context.save_artifact(filename=filename, artifact=artifact)

        illustrated_pages.append(page_result)

    return {
        "title": story_data.get("title"),
        "total_pages": len(illustrated_pages),
        "pages": illustrated_pages,
        "status": "complete",
    }
