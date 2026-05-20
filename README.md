# Photo Maestro

사진을 찍으면 AI가 시각 패턴을 분석해 악보와 음악을 생성하는 모바일 앱.

## 핵심 기능

| 입력 유형 | 처리 방식 |
|-----------|-----------|
| **일반 사진** | Claude Vision으로 색감·구조·반복 패턴 추출 → 음악 생성 |
| **악보 사진** | Oemer(OMR)로 음표 직접 인식 → 그 악보를 연주 |

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 모바일 | React Native + Expo (expo-router, expo-camera, expo-av, zustand) |
| 백엔드 | Python 3.12 + FastAPI |
| AI 오케스트레이션 | LangGraph (StateGraph, 조건부 엣지) |
| 비동기 처리 | Celery + Redis |
| AI 분석 | Claude Vision API |
| OMR | Oemer (악보 사진 경로) |
| 악보 렌더링 | music21 + MuseScore3 → PNG |
| 오디오 | FluidSynth + ffmpeg → MP3 |
| 파일 저장 | Supabase Storage |
| 배포 | Railway (백엔드), Expo EAS (모바일) |

## 프로젝트 구조

```
photo-maestro/
├── backend/
│   ├── graph/
│   │   ├── state.py             # C+D 공동 계약서 (GraphState)
│   │   ├── workflow.py          # LangGraph 그래프 정의
│   │   └── nodes/
│   │       ├── preprocessor.py  # 이미지 리사이즈·정규화
│   │       ├── classifier.py    # 악보 vs 일반 사진 판별
│   │       ├── analyzer.py      # Claude Vision 패턴 분석
│   │       ├── validator.py     # 분석 검증·재시도 판단
│   │       ├── mapper.py        # 패턴 → 음악 파라미터
│   │       ├── score_gen.py     # music21 MusicXML + MIDI
│   │       ├── omr.py           # Oemer OMR (악보 경로)
│   │       ├── score_render.py  # MuseScore3 PNG
│   │       ├── audio_gen.py     # FluidSynth MP3
│   │       └── uploader.py      # Supabase 업로드
│   ├── api/routes/
│   │   ├── analyze.py           # POST /api/analyze
│   │   ├── jobs.py              # GET /api/jobs/{id}
│   │   └── music.py             # GET /api/music/{id}/score|audio
│   ├── services/
│   │   └── storage.py           # Supabase Storage 추상화
│   ├── models/schemas.py        # Pydantic API 스키마
│   ├── worker.py                # Celery task + LangGraph 실행
│   ├── celery_app.py            # Celery 앱 설정
│   ├── main.py                  # FastAPI 진입점
│   ├── requirements.txt         # FastAPI + Celery + Supabase
│   ├── requirements-worker.txt  # + LangGraph + Oemer + music21
│   ├── Dockerfile               # 경량 (API 서버)
│   └── Dockerfile.worker        # 무거움 (ML + MuseScore3)
│
├── mobile/
│   ├── app/
│   │   ├── _layout.tsx          # 네비게이션 레이아웃
│   │   ├── index.tsx            # 업로드 화면
│   │   ├── result/[jobId].tsx   # 결과 화면 (폴링 → 악보+재생)
│   │   └── history.tsx          # 생성 히스토리
│   ├── components/
│   │   ├── SheetMusicView.tsx
│   │   ├── AudioPlayer.tsx
│   │   └── ProgressBar.tsx
│   ├── store/jobStore.ts        # Zustand 전역 상태
│   └── package.json
│
├── docker-compose.yml
└── ARCHITECTURE.md              # 기술 선택 근거 문서
```

## 실행 방법

### 백엔드

```bash
# .env 파일 준비
cp backend/.env.example backend/.env
# ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_BUCKET 입력

# 전체 실행 (API + Worker + Redis)
docker compose up --build

# 개발 모드 (Flower 모니터링 포함)
docker compose --profile dev up --build
```

API 문서: http://localhost:8000/docs

### 모바일

```bash
cd mobile
cp .env.example .env          # EXPO_PUBLIC_API_URL 설정
npm install
npx expo start
```

## API 엔드포인트

```
POST /api/analyze/           이미지 업로드 → job_id 반환
GET  /api/jobs/{job_id}      작업 상태 조회 (진행률 + 결과 URL)
GET  /api/music/{job_id}/score    악보 PNG 리다이렉트
GET  /api/music/{job_id}/audio    MP3 리다이렉트
```

## 팀 분담

| 담당 | 영역 |
|------|------|
| A | `mobile/` 전담 |
| B | `backend/api/`, `worker.py`, `docker-compose.yml`, Supabase |
| C | `graph/workflow.py`, `nodes/classifier|analyzer|validator|preprocessor.py` |
| D | `graph/nodes/mapper|score_gen|score_render|audio_gen|omr.py` |

자세한 기술 결정 근거는 [ARCHITECTURE.md](ARCHITECTURE.md) 참조.
