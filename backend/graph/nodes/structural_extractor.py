import cv2
import numpy as np
from graph.state import GraphState

N_SLICES = 16


def structural_extract_node(state: GraphState) -> dict:
    """OpenCV로 이미지를 N_SLICES 구간으로 분할해 구조적 특징을 추출한다."""
    nparr = np.frombuffer(state["image_bytes"], np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    height, width = gray.shape
    slice_w = max(width // N_SLICES, 1)

    pitch_contour = []
    edge_density = []
    brightness_profile = []

    for i in range(N_SLICES):
        x0 = i * slice_w
        x1 = x0 + slice_w if i < N_SLICES - 1 else width

        s_gray = gray[:, x0:x1].astype(float)
        s_edges = edges[:, x0:x1]

        # 수직 무게중심 → 음고 (이미지 위쪽 = 높은 음)
        total = s_gray.sum()
        if total > 0:
            y_idx = np.arange(height).reshape(-1, 1)
            cy = float((s_gray * y_idx).sum() / total)
            pitch_norm = 1.0 - cy / height
        else:
            pitch_norm = 0.5

        pitch_contour.append(round(pitch_norm, 4))
        edge_density.append(round(float(s_edges.mean()) / 255.0, 4))
        brightness_profile.append(round(float(s_gray.mean()) / 255.0, 4))

    return {
        "structural_data": {
            "pitch_contour": pitch_contour,
            "edge_density": edge_density,
            "brightness_profile": brightness_profile,
            "n_slices": N_SLICES,
        },
        "current_step": "구조적 특징 추출 완료",
    }
