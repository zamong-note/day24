import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from google.genai import types
from google.adk.tools.tool_context import ToolContext

# Windows에 기본 내장된 한글 폰트. 없으면 PIL 기본 폰트로 대체한다 (한글은 깨져 보일 수 있음).
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
]
TEXT_AREA_HEIGHT = 260
PAGE_PADDING = 48
FONT_SIZE = 42
BACKGROUND_COLOR = "#FFFDF5"
TEXT_COLOR = "#3A2E1F"


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


async def _compose_page(page: dict, tool_context: ToolContext) -> dict:
    page_number = page.get("page_number")
    text = page.get("text", "")
    image_filename = f"page_{page_number}.png"
    output_filename = f"storybook_page_{page_number}.png"

    existing_artifacts = await tool_context.list_artifacts()
    if image_filename not in existing_artifacts:
        return {
            "page_number": page_number,
            "status": "error",
            "message": f"{image_filename} 삽화를 찾을 수 없습니다. IllustratorTeam을 먼저 실행하세요.",
        }

    illustration_artifact = await tool_context.load_artifact(filename=image_filename)
    illustration = Image.open(
        io.BytesIO(illustration_artifact.inline_data.data)
    ).convert("RGB")

    canvas_width = illustration.width
    canvas_height = illustration.height + TEXT_AREA_HEIGHT
    canvas = Image.new("RGB", (canvas_width, canvas_height), BACKGROUND_COLOR)
    canvas.paste(illustration, (0, 0))

    draw = ImageDraw.Draw(canvas)
    font = _load_font(FONT_SIZE)
    max_text_width = canvas_width - PAGE_PADDING * 2
    lines = _wrap_text(draw, text, font, max_text_width)

    line_height = font.getbbox("가")[3] + 18
    total_text_height = line_height * len(lines)
    start_y = illustration.height + max(
        (TEXT_AREA_HEIGHT - total_text_height) // 2, PAGE_PADDING // 2
    )

    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        x = (canvas_width - line_width) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")

    composed_artifact = types.Part(
        inline_data=types.Blob(mime_type="image/png", data=buffer.getvalue())
    )
    await tool_context.save_artifact(filename=output_filename, artifact=composed_artifact)

    return {
        "page_number": page_number,
        "filename": output_filename,
        "status": "complete",
    }


def _find_page(story_data: dict, page_number: int) -> dict | None:
    for page in story_data.get("pages", []):
        if page.get("page_number") == page_number:
            return page
    return None


def make_page_composer_tool(page_number: int):
    """지정된 page_number 하나만 담당하는 페이지 합성 도구를 만든다.

    PageComposerTeam의 각 서브 에이전트가 서로 다른 페이지를 동시에 처리할 수 있도록
    page_number를 클로저로 고정한 전용 도구를 생성한다.
    """

    async def compose_page(tool_context: ToolContext):
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

        return await _compose_page(page, tool_context)

    compose_page.__name__ = f"compose_storybook_page_{page_number}"
    compose_page.__doc__ = (
        f"{page_number}페이지의 삽화(page_{page_number}.png)와 본문을 합쳐 텍스트가 포함된 "
        f"최종 동화책 페이지(storybook_page_{page_number}.png)를 만든다."
    )
    return compose_page
