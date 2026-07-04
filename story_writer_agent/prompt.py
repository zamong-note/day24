STORY_BOOK_DESCRIPTION = (
    "테마(제목)를 입력받아 5페이지 분량의 어린이 동화를 작성(StoryWriterAgent)한 뒤, "
    "5개의 페이지별 삽화가 서브 에이전트(IllustratorTeam)를 ParallelAgent로 동시에 실행해 "
    "삽화를 생성하고, 마지막으로 PageComposerAgent가 삽화와 본문 텍스트를 하나의 이미지로 합쳐 "
    "텍스트가 포함된 최종 동화책 페이지를 만드는 SequentialAgent 파이프라인입니다. "
    "모든 에이전트는 Session State의 story_data를 통해 데이터를 공유하며, "
    "Callback을 통해 각 단계의 진행 상황이 콘솔에 표시됩니다."
)
