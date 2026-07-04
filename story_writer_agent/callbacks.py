"""SequentialAgent/ParallelAgent 파이프라인의 진행 상황을 콘솔에 출력하는 콜백 모음."""

import json
import sys

from google.genai import types

# Windows 콘솔의 기본 코드페이지(cp949 등)는 이모지를 인코딩하지 못해 print()가
# UnicodeEncodeError로 전체 파이프라인을 중단시킬 수 있다. utf-8로 재설정해 방지한다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def progress_callback(message: str):
    """단순 진행 상황 메시지를 콘솔에 출력하는 before/after_agent_callback을 생성한다."""

    def _callback(callback_context) -> None:
        print(f"[진행 상황] ({callback_context.agent_name}) {message}")
        return None

    return _callback


def page_progress_callbacks(page_number: int, total_pages: int):
    """페이지별 삽화 생성 진행 상황을 표시하는 (before, after) 콜백 쌍을 생성한다."""

    before = progress_callback(f"🖌️ 이미지 {page_number}/{total_pages} 생성 중...")
    after = progress_callback(f"✨ 이미지 {page_number}/{total_pages} 생성 완료!")
    return before, after


def build_final_storybook_callback():
    """모든 페이지와 삽화가 준비된 뒤, 완성된 동화책의 제목과 본문을 정리하는 after_agent_callback.

    페이지별 이미지는 PageComposerTeam의 각 서브 에이전트가 자신의 메시지에 개별적으로 첨부하므로
    (ADK Web UI는 메시지 하나당 이미지 하나만 표시한다), 여기서는 텍스트 요약만 정리한다.
    """

    def _callback(callback_context):
        print(f"[진행 상황] ({callback_context.agent_name}) 📖 동화책이 완성되었습니다!")

        story_data = callback_context.state.get("story_data")
        if not story_data:
            return None
        if isinstance(story_data, str):
            story_data = json.loads(story_data)

        lines = [f"# {story_data.get('title', '')}", ""]
        for page in story_data.get("pages", []):
            page_number = page.get("page_number")
            lines.append(f"## {page_number}페이지")
            lines.append(page.get("text", ""))
            lines.append("")

        return types.Content(role="model", parts=[types.Part(text="\n".join(lines))])

    return _callback
