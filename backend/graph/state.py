from typing import TypedDict, Literal, Optional


class GraphState(TypedDict):
    job_id: str
    image_bytes: bytes

    # 분류 단계 (classifier 노드가 쓴다)
    image_type: Optional[Literal["sheet_music", "general"]]

    # 일반 사진 경로 (analyzer/validator/mapper 노드가 쓴다)
    raw_analysis: Optional[dict]
    analysis_attempts: int
    music_params: Optional[dict]  # scale, tempo, octave, dynamic, note_count, mood

    # 악보 사진 경로 (omr 노드가 쓴다)
    omr_musicxml: Optional[str]

    # 공통 출력 (score_gen / omr 이후 모든 노드가 참조)
    final_musicxml: Optional[str]
    midi_path: Optional[str]
    score_png_path: Optional[str]
    audio_path: Optional[str]

    # Supabase 업로드 후 공개 URL (uploader 노드가 쓴다)
    score_url: Optional[str]
    audio_url: Optional[str]

    # 진행 상태 (worker가 Redis 업데이트에 사용)
    current_step: str
    error: Optional[str]
