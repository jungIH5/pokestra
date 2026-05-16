import tempfile
from pathlib import Path
from graph.state import GraphState


def omr_node(state: GraphState) -> dict:
    """
    Oemer OMR로 악보 사진에서 MusicXML을 추출한다.
    Oemer와 PyTorch는 worker 컨테이너에만 설치되어 있다.
    """
    try:
        from oemer.ete import end2end
    except ImportError as e:
        return {
            "error": f"Oemer 미설치 (worker 컨테이너에서만 실행 가능): {e}",
            "current_step": "OMR 실패",
        }

    job_dir = _job_dir(state["job_id"])
    img_path = job_dir / "input.jpg"
    img_path.write_bytes(state["image_bytes"])

    output_dir = job_dir / "omr_output"
    output_dir.mkdir(exist_ok=True)

    try:
        end2end(str(img_path), str(output_dir))
    except Exception as e:
        return {
            "error": f"OMR 처리 실패: {e}",
            "current_step": "OMR 실패",
        }

    # Oemer는 output_dir 아래에 MusicXML 파일을 생성한다
    xml_files = list(output_dir.glob("*.xml"))
    if not xml_files:
        return {
            "error": "OMR이 MusicXML을 생성하지 못했습니다. 더 선명한 사진을 사용해주세요.",
            "current_step": "OMR 실패",
        }

    musicxml = xml_files[0].read_text(encoding="utf-8")
    return {
        "omr_musicxml": musicxml,
        "final_musicxml": musicxml,
        "current_step": "악보 인식(OMR) 완료",
    }


def _job_dir(job_id: str) -> Path:
    job_dir = Path(tempfile.gettempdir()) / "photo-maestro" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
