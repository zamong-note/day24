from typing import List

from pydantic import BaseModel, Field


class StoryPage(BaseModel):
    page_number: int = Field(description="1부터 시작하는 페이지 번호")
    text: str = Field(description="해당 페이지에 들어갈 동화 본문 (1~3문장, 쉬운 한국어)")
    visual_description: str = Field(
        description="삽화가가 그림을 생성할 때 참고할 장면 묘사 (등장인물 외형, 배경, 분위기 포함)"
    )


class Story(BaseModel):
    title: str = Field(description="동화 제목")
    theme: str = Field(description="입력받은 테마")
    pages: List[StoryPage] = Field(description="5개의 페이지로 구성된 스토리")
