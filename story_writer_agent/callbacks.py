"""SequentialAgent/ParallelAgent 파이프라인의 진행 상황을 콘솔에 출력하는 콜백 모음."""

import sys

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
