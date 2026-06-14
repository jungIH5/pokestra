from typing import TypedDict, Literal, Optional


class GraphState(TypedDict):
    job_id: str
    image_bytes: bytes
    mood_input: str  # 사용자 자연어 분위기 입력

    # 분류 단계
    image_type: Optional[Literal["sheet_music", "general"]]

    # 일반 사진 경로 — OpenCV 구조 추출 결과
    structural_data: Optional[dict]  # pitch_contour, edge_density, brightness_profile, n_slices

    # 음악 파라미터 (mood_parser + map_params 노드가 채운다)
    music_params: Optional[dict]  # scale, tempo, base_dynamic, note_count

    # 악보 사진 경로
    omr_musicxml: Optional[str]

    # 공통 출력
    final_musicxml: Optional[str]
    midi_path: Optional[str]
    score_png_path: Optional[str]
    audio_path: Optional[str]

    # Supabase 업로드 후 공개 URL
    score_url: Optional[str]
    audio_url: Optional[str]

    # 진행 상태
    current_step: str
    error: Optional[str]
