# Photo Maestro — 아키텍처 설계 문서

> 이 문서는 기술 선택의 **이유**를 포함한 설계 결정 기록이다.  
> 코드보다 먼저 읽어야 할 문서. 코드가 바뀌면 이 문서도 함께 갱신한다.

---

## 1. 서비스 개요

사진을 찍거나 업로드하면 AI가 시각 패턴을 분석해 악보와 음악을 생성하는 모바일 앱.

**두 가지 입력 경로를 지원한다:**

| 입력 유형 | 처리 방식 | 예시 |
|-----------|-----------|------|
| 일반 사진 | Claude Vision으로 색감·구조·반복 패턴 추출 → 음악으로 변환 | 꽃밭, 건물, 추상화 |
| 악보 사진 | Oemer(OMR)로 음표를 직접 인식 → 그 악보를 연주 | 손으로 쓴 악보, 인쇄된 악보 |

---

## 2. 팀 구성 (4인)

### 역할 분담

| 담당 | 영역 | 소유 디렉토리 |
|------|------|---------------|
| **A — Mobile** | React Native 앱 전체 | `mobile/` |
| **B — Backend Infra** | FastAPI, Celery, Supabase, Docker, 배포 | `backend/api/`, `backend/services/storage.py`, `backend/worker.py`, `docker-compose.yml` |
| **C — AI Pipeline** | LangGraph 그래프 설계, Claude Vision 노드 | `backend/graph/workflow.py`, `backend/graph/nodes/classifier.py`, `analyzer.py`, `validator.py`, `preprocessor.py` |
| **D — Music Domain** | 패턴 매핑, music21, Oemer, FluidSynth | `backend/graph/nodes/mapper.py`, `score_gen.py`, `score_render.py`, `audio_gen.py`, `omr.py` |

### 분담 기준과 이유

**기술 레이어가 아닌 도메인으로 나눈 이유**

4인을 "프론트/백/인프라/QA" 같은 레이어로 나누면 병렬 개발이 어렵다. 백엔드 한 명이 막히면 프론트가 테스트할 API가 없고, 인프라 담당자는 초반에 할 일이 없다가 배포 때만 바빠진다.

이 프로젝트의 자연스러운 경계는 **데이터 흐름**에 있다. `이미지 → AI 분석 → 음악 파라미터 → 악보·오디오` 흐름에서 각 단계가 명확히 분리된다. C(AI)와 D(Music)는 LangGraph `GraphState`라는 계약서 하나로 연결되고, A(Mobile)와 B(Backend)는 API 스펙으로 연결된다. 이 계약서 두 개만 초반에 확정되면 네 사람이 거의 독립적으로 작업할 수 있다.

### 협업 인터페이스 (병렬 개발의 핵심)

**계약서 1 — GraphState** (`backend/graph/state.py`, C와 D가 공동 정의)

```python
class GraphState(TypedDict):
    job_id: str
    image_bytes: bytes

    # 분류 (C가 쓴다)
    image_type: Literal["sheet_music", "general"]

    # 일반 사진 경로 (C가 쓴다)
    raw_analysis: dict
    analysis_attempts: int

    # 일반 사진 경로 (D가 읽는다)
    music_params: dict          # scale, tempo, octave, dynamics, note_count

    # 악보 경로 (D가 쓴다)
    omr_musicxml: str

    # 최종 출력 (D가 쓴다, B가 Supabase에 업로드한다)
    final_musicxml: str
    score_png_path: str
    midi_path: str
    audio_path: str

    current_step: str
    error: str | None
```

GraphState는 스프린트 첫날 C와 D가 합의해서 확정한다. 이후 필드를 추가할 때는 반드시 상대방과 협의한다. 이 파일이 C와 D의 유일한 충돌 지점이다.

**계약서 2 — API 스펙** (B가 정의, A가 소비)

```
POST /api/analyze
  request:  { image: File }
  response: { job_id: str }

GET /api/jobs/{job_id}
  response: {
    status: "queued" | "running" | "done" | "failed",
    current_step: str,
    progress: int,          # 0~100
    result?: {
      score_url: str,       # Supabase Public URL → PNG
      audio_url: str,       # Supabase Public URL → MP3
      image_type: "sheet_music" | "general",
      music_params?: dict
    },
    error?: str
  }
```

B는 스프린트 첫날 이 스펙을 `backend/main.py`에 목업(stub)으로 구현해 놓는다. A는 실제 로직이 없어도 이 목업을 보고 모바일 개발을 시작할 수 있다.

### 브랜치 전략

```
main (보호, PR 필수)
├── feat/mobile          ← A
├── feat/backend-infra   ← B
├── feat/ai-pipeline     ← C
└── feat/music-domain    ← D
```

`main`에 머지할 때 상대방 계약서 파일(`state.py`, `schemas.py`)이 변경됐으면 반드시 리뷰어로 지정한다.

### 충돌이 예상되는 파일과 대응

| 파일 | 충돌 위험 | 대응 |
|------|-----------|------|
| `backend/graph/state.py` | C, D 모두 수정 | 첫날 확정 후 변경 시 PR 리뷰 필수 |
| `backend/requirements.txt` | 모두 추가 가능 | `requirements-base.txt`(B), `requirements-worker.txt`(C+D)로 분리 |
| `.env.example` | 모두 변수 추가 | B가 소유, 다른 팀원은 PR로 추가 요청 |
| `docker-compose.yml` | B가 소유하지만 모두 영향받음 | 변경 시 전체 공유 |

---

## 3. 기술 결정과 이유

### 3-1. 모바일: React Native + Expo

- **React Native**: iOS·Android 단일 코드베이스. ML 연산이 서버에 있어 네이티브 성능 차이는 무의미하다. Flutter와 비교했을 때 JS 생태계 친숙도가 높다면 학습 곡선이 낮다.
- **Expo**: `expo-camera`(촬영), `expo-image-picker`(갤러리), `expo-av`(MP3 재생)가 이 앱의 핵심 기능을 플랫폼 차이 없이 처리한다. 네이티브 코드 없이도 충분하다.
- **Expo Router**: 파일 기반 라우팅. `app/result/[jobId].tsx` 파일이 곧 화면이다. A가 혼자 작업하기 좋은 구조다.
- **EAS Build + EAS Update**: Xcode 없이 iOS 빌드, JS 번들 변경 시 OTA 업데이트.
- **Zustand**: Redux보다 보일러플레이트가 적다. 잡 상태(job_id, polling, result)를 전역으로 관리하는 데 충분하다.

---

### 3-2. 백엔드: FastAPI

- **async-native**: 이미지 업로드·Claude API 호출·Supabase 업로드가 전부 IO-bound. Flask sync WSGI는 동시 요청마다 스레드를 소비하지만 FastAPI는 asyncio로 처리한다.
- **Pydantic**: 요청/응답 타입이 런타임에 검증된다. A가 API를 소비할 때 타입 오류가 앱이 아니라 서버에서 잡힌다.
- **자동 OpenAPI (`/docs`)**: B가 목업을 올려두면 A가 실제 구현 없이도 API 구조를 확인하고 모바일 코드를 작성할 수 있다.

---

### 3-3. AI 오케스트레이션: LangGraph

이 파이프라인은 **조건부 분기와 재시도 루프**가 있어서 순차 함수 호출로는 관리가 어렵다.

```
[preprocess] → [classify]
                   ↓ 일반 사진          ↓ 악보 사진
           [Claude Vision 분석]     [Oemer OMR]
                   ↓
           [신뢰도 검사]
           낮으면 최대 3회 재시도 ↩
                   ↓
           [music_params 매핑]  ←── (OMR 경로는 여기서 합류)
                   ↓
           [music21 악보 생성]
                   ↓
           [MuseScore3 PNG 렌더링]
                   ↓
           [FluidSynth MP3 변환]
                   ↓
           [Supabase 업로드]
```

**LangGraph가 적합한 이유**

- **GraphState**: 모든 노드가 공유하는 단일 딕셔너리. C와 D 사이에 데이터를 "함수 인자로 넘기는" 대신 상태에서 읽고 쓴다. 노드 시그니처가 단순해진다.
- **조건부 엣지**: 재시도 로직을 if/else 대신 그래프 엣지로 선언한다. `validator` 노드가 `"retry"` 또는 `"continue"`를 반환하면 그래프가 경로를 선택한다.
- **Redis 체크포인트**: 각 노드 완료 후 상태를 Redis에 저장한다. 워커가 재시작되어도 완료된 노드부터 재개한다.
- **스트리밍**: `graph.astream()`으로 노드 완료 이벤트를 실시간 emit한다. 모바일에서 "분석 중… 악보 생성 중…" 진행 표시가 가능하다.
- **확장성**: 나중에 "더 빠르게", "단조로 바꿔줘" 같은 사용자 피드백 루프를 추가할 때 LangGraph의 human-in-the-loop 패턴을 그대로 쓴다.

---

### 3-4. 비동기 처리: Celery + Redis

전체 파이프라인은 15~30초 소요된다 (Claude Vision 5~10초 + music21 2~5초 + FluidSynth 3~8초, Oemer는 최대 20초). 모바일이 30초 HTTP를 기다릴 수 없다.

```
POST /analyze  →  즉시 { job_id } 반환
Celery Worker  →  백그라운드에서 LangGraph 실행
GET /jobs/{id} →  2초마다 폴링 → 완료 시 결과 URL
```

**FastAPI BackgroundTasks 대신 Celery를 선택한 이유**

`BackgroundTasks`는 서버 프로세스가 살아있는 동안만 동작한다. Docker 컨테이너 재시작 시 진행 중 작업이 사라진다. Celery는 작업을 Redis에 영속화하므로 워커가 재시작되어도 큐에서 다시 가져온다.

---

### 3-5. OMR: Oemer

| 도구 | 언어 | 추가 학습 | Docker 통합 |
|------|------|-----------|-------------|
| **Oemer** | Python | 불필요 (사전학습 포함) | 쉬움 |
| Audiveris | Java | 불필요 | 복잡 |
| 상용 (PhotoScore 등) | - | - | 불가 |

Oemer는 `pip install oemer`로 설치하고 사전학습된 U-Net + Transformer 모델이 포함되어 있다. Python 환경에서 바로 쓸 수 있고 MusicXML을 직접 출력해 music21과 바로 연결된다.

**Oemer의 PyTorch 의존성 문제 대응**

Oemer는 PyTorch를 의존해 이미지 크기가 ~2GB 증가한다. FastAPI 서버는 Celery 큐에 작업을 등록하기만 하고 추론을 직접 하지 않는다. 따라서 `Dockerfile`(FastAPI, 경량)과 `Dockerfile.worker`(Celery + Oemer, 무거움)를 분리한다. 두 컨테이너는 같은 소스 코드를 공유하되 진입점과 Dockerfile만 다르다.

---

### 3-6. 파일 저장: Supabase Storage

**Supabase를 선택한 이유**

| 항목 | 내용 |
|------|------|
| 무료 티어 | 1GB 스토리지 + 2GB 대역폭 (개발~초기 운영 커버) |
| CDN | Supabase Storage의 Public URL이 곧 CDN URL. 모바일이 직접 다운로드 |
| 팀 공유 | 하나의 프로젝트 URL + 키로 4명이 공유. MinIO처럼 Docker 서비스 추가 불필요 |
| 확장성 | 나중에 사용자 계정·히스토리가 필요해지면 Supabase PostgreSQL + Auth를 같은 대시보드에서 추가. 별도 서비스 없음 |
| SDK | `supabase-py`가 깔끔. `boto3`처럼 인증 설정이 복잡하지 않음 |

**S3/R2 대비 Supabase Storage가 불리한 점**

- 1GB 초과 시 유료 (Pro 플랜 $25/월, 100GB). S3는 GB 단위 과금이라 소량이면 더 저렴할 수 있다.
- S3 호환 API가 있지만 `supabase-py` 사용이 더 자연스럽다.

초기 트래픽이 작은 이 프로젝트에서는 Supabase의 단순함과 무료 티어가 S3의 세밀한 과금보다 낫다.

**스토리지 추상화**

```python
# backend/services/storage.py
class SupabaseStorage:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.bucket = "photo-maestro"

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        self.client.storage.from_(self.bucket).upload(path, data,
            {"content-type": content_type, "upsert": "true"})
        return self.public_url(path)

    def public_url(self, path: str) -> str:
        return self.client.storage.from_(self.bucket).get_public_url(path)
```

나중에 스토리지 백엔드를 바꾸어야 한다면 이 클래스만 교체한다.

---

### 3-7. 악보 표시: 서버 PNG 렌더링 (MuseScore3)

모바일에서 MusicXML을 직접 렌더링하는 방법을 검토했다.

| 방법 | 장점 | 단점 |
|------|------|------|
| WebView + OSMD | 렌더링 품질 좋음, 인터랙티브 가능 | WebView 메모리 부담, 초기 로딩 느림, 복잡한 세팅 |
| AlphaTab RN 바인딩 | 네이티브 렌더링 | 라이브러리 미성숙 |
| **서버 PNG (MuseScore3)** | 모바일 부담 없음, 기기 무관 | 파일 다운로드 필요 |

현재 단계에서 악보 표시는 조회 전용이다. `<Image source={{ uri }} />`로 해결된다. 인터랙션(마디 클릭, 편집)이 필요해지면 그때 WebView + OSMD로 전환한다.

MuseScore3는 이미 Dockerfile에 설치되어 있다.

---

### 3-8. 오디오: FluidSynth → MP3 (서버 생성)

```
music21 → MIDI → FluidSynth + soundfont → WAV → lame → MP3
```

React Native에서 MIDI를 직접 합성하려면 iOS/Android 각각의 오디오 API를 다뤄야 하고 앱 번들에 soundfont(~100MB)를 포함해야 한다. 서버에서 MP3를 만들어 Supabase에 올리면 모바일은 `expo-av`로 URL을 재생하기만 한다.

FluidSynth는 이미 Dockerfile에 설치되어 있다.

---

### 3-9. 배포: Railway + Expo EAS

**백엔드 → Railway**

- `docker-compose.yml`을 그대로 배포할 수 있다. AWS ECS처럼 IAM, Task Definition, ALB 설정이 없다.
- Redis 서비스가 플러그인으로 기본 제공된다.
- GitHub `main` 브랜치 푸시 → 자동 재배포.
- 월 $5~20 수준.

**모바일 → Expo EAS**

- `eas build`: 클라우드 iOS/Android 빌드 (Xcode 불필요).
- `eas submit`: App Store/Google Play 제출 자동화.
- `eas update`: JS 번들만 변경 시 OTA 업데이트.

---

## 4. 전체 시스템 구성도

```
┌───────────────────────────────────────────────────────┐
│  모바일 (React Native + Expo)             [담당: A]    │
│                                                        │
│  [카메라/갤러리] → [업로드] → [진행 표시] → [결과 화면]│
│                        │                    ↑          │
│                    job_id 반환         폴링 (2초)       │
└────────────────────────┼────────────────────┼──────────┘
                         │                    │
               POST /analyze        GET /jobs/{id}
                         │                    │
┌────────────────────────▼────────────────────┼──────────┐
│  FastAPI (backend 컨테이너)        [담당: B] │          │
│                                             │          │
│  /analyze → Celery 큐 등록 → job_id 반환    │          │
│  /jobs/{id} → Redis 상태 조회              │          │
└─────────────────────────────────────────────┼──────────┘
                                              │
┌─────────────────────────────────────────────┼──────────┐
│  Celery Worker (worker 컨테이너)   [담당: C+D]          │
│                                                        │
│  LangGraph StateGraph                                  │
│                                                        │
│  [preprocess]──[classify]                              │
│  [담당: C]          ↓ 일반 사진   ↓ 악보 사진           │
│              [Claude Vision]  [Oemer OMR]  [담당: C/D] │
│                    ↓                                   │
│              [validate/retry]              [담당: C]   │
│                    ↓                                   │
│              [map_to_params] ←── (OMR 합류) [담당: D]  │
│                    ↓                                   │
│              [music21 생성]                [담당: D]   │
│                    ↓                                   │
│              [MuseScore3 PNG]              [담당: D]   │
│                    ↓                                   │
│              [FluidSynth MP3]              [담당: D]   │
│                    ↓                                   │
│              [Supabase 업로드]             [담당: B]   │
└────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────────────────┐
│  Redis           │    │  Supabase Storage            │
│  Celery 브로커   │    │  PNG / MP3 / MusicXML        │
│  LangGraph 체크  │    │  Public CDN URL 제공         │
│  Job 상태        │    │                              │
└──────────────────┘    └──────────────────────────────┘
```

---

## 5. 디렉토리 구조 (담당자 포함)

```
photo-maestro/
│
├── backend/                              [B가 설정, 전체 공유]
│   │
│   ├── graph/
│   │   ├── state.py                      [C+D 공동 정의, 초반 확정 필수]
│   │   ├── workflow.py                   [C]
│   │   └── nodes/
│   │       ├── preprocessor.py           [C] 이미지 리사이즈·인코딩
│   │       ├── classifier.py             [C] 악보 vs 일반 사진 판별
│   │       ├── analyzer.py               [C] Claude Vision 패턴 분석
│   │       ├── validator.py              [C] 신뢰도 검사·재시도 판단
│   │       ├── omr.py                    [D] Oemer OMR 호출
│   │       ├── mapper.py                 [D] 패턴 → 음악 파라미터
│   │       ├── score_gen.py              [D] music21 MusicXML + MIDI
│   │       ├── score_render.py           [D] MuseScore3 PNG
│   │       └── audio_gen.py              [D] FluidSynth MP3
│   │
│   ├── api/                              [B]
│   │   └── routes/
│   │       ├── analyze.py                [B] POST /analyze
│   │       ├── jobs.py                   [B] GET /jobs/{id}
│   │       └── music.py                  [B] 파일 URL 반환
│   │
│   ├── services/
│   │   ├── storage.py                    [B] Supabase 업로드 추상화
│   │   ├── image_analyzer.py             [C로 이전 예정, 현재 유지]
│   │   ├── pattern_mapper.py             [D로 이전 예정, 현재 유지]
│   │   └── music_generator.py            [D로 이전 예정, 현재 유지]
│   │
│   ├── models/
│   │   └── schemas.py                    [B가 API 스키마 정의]
│   │
│   ├── worker.py                         [B] Celery app + task 등록
│   ├── main.py                           [B] FastAPI 진입점
│   │
│   ├── requirements.txt                  [B] FastAPI, Celery, Supabase 등
│   ├── requirements-worker.txt           [C+D] torch, oemer, music21 등
│   │
│   ├── Dockerfile                        [B] FastAPI 경량 이미지
│   └── Dockerfile.worker                 [B] Celery + ML 무거운 이미지
│
├── mobile/                               [A 전담]
│   ├── app/
│   │   ├── index.tsx                     카메라/갤러리 업로드 화면
│   │   ├── result/
│   │   │   └── [jobId].tsx              결과 화면 (악보 + 재생)
│   │   └── history.tsx                  생성 히스토리
│   │
│   ├── components/
│   │   ├── SheetMusicView.tsx            Supabase URL → Image 표시
│   │   ├── AudioPlayer.tsx               expo-av 재생 래퍼
│   │   └── ProgressBar.tsx              폴링 기반 진행 표시
│   │
│   └── store/
│       └── jobStore.ts                  Zustand 전역 상태
│
├── docker-compose.yml                    [B]
├── .env.example                          [B 관리, 전체 기여]
├── ARCHITECTURE.md                       [전체]
└── README.md                             [전체]
```

---

## 6. Docker Compose 구성

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile          # 경량 (FastAPI only, PyTorch 없음)
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - ./backend:/app
    env_file: ./backend/.env

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker   # 무거운 이미지 (PyTorch + Oemer ~3GB)
    command: celery -A worker.celery_app worker --loglevel=info --concurrency=2
    depends_on:
      - redis
    volumes:
      - ./backend:/app
    env_file: ./backend/.env

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  flower:                             # 개발 전용 Celery 모니터링
    image: mher/flower:2.0
    command: celery --broker=redis://redis:6379/0 flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    profiles:
      - dev                           # docker compose --profile dev up

volumes:
  redis_data:
```

파일 저장은 Supabase Storage가 담당하므로 `storage` 볼륨이 없다. 모든 생성 파일은 Supabase에 업로드 후 URL을 Redis에 저장한다.

---

## 7. API 엔드포인트

```
POST /api/analyze
  body:     multipart/form-data { image: File }
  response: { job_id: str, status: "queued" }

GET /api/jobs/{job_id}
  response: {
    job_id: str,
    status: "queued" | "running" | "done" | "failed",
    current_step: str,
    progress: int,
    result?: {
      score_url: str,       # Supabase Public URL (PNG)
      audio_url: str,       # Supabase Public URL (MP3)
      image_type: "sheet_music" | "general",
      music_params?: dict   # 일반 사진 경로일 때만
    },
    error?: str
  }
```

---

## 8. 개발 단계

| 단계 | 목표 | 주담당 | 완료 기준 |
|------|------|--------|-----------|
| **0** | `state.py` + API 스펙 확정 | C+D, B | 문서화된 계약서 2개 |
| **1** | Docker Compose + Redis + Supabase 연결 | B | `docker compose up` healthy |
| **2** | LangGraph 그래프 뼈대 (더미 노드) | C | 상태 흐름 검증 |
| **3** | 일반 사진 경로 구현 | C+D | Claude Vision → PNG + MP3 생성 |
| **4** | 악보 사진 경로 구현 | D | Oemer → PNG + MP3 생성 |
| **5** | Celery 비동기 연결 | B | job 폴링 → 완료 결과 |
| **6** | 모바일 업로드 → 결과 화면 | A | 촬영 → 악보 표시 → 재생 |
| **7** | Railway 배포 + EAS Build | B+A | TestFlight/Play 테스트 |

단계 0이 가장 중요하다. 여기서 계약서가 확정되어야 1~6이 병렬로 진행될 수 있다.

---

## 9. 환경 변수

```bash
# Claude API (C가 사용)
ANTHROPIC_API_KEY=

# Redis (B가 설정)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Supabase (B가 설정)
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_KEY=
SUPABASE_BUCKET=photo-maestro
```

---

## 10. 결정 보류 항목

| 항목 | 현재 결정 | 재검토 시점 |
|------|-----------|-------------|
| 악보 인터랙션 | PNG 이미지 표시 | 마디 클릭·편집 필요 시 → WebView + OSMD |
| 사용자 계정·히스토리 | 없음 | 배포 후 반응 보고 → Supabase Auth + PostgreSQL |
| 음악 품질 | 규칙 기반 랜덤 음표 | 패턴 매핑 정교화 후 → Claude로 멜로디 구조 설계 |
| Supabase → 대용량 스토리지 | 1GB 무료 티어 | 1GB 초과 시 → Pro $25/월 또는 R2 이전 |
| Oemer 정확도 | 기본 사전학습 모델 | 인식률 불만족 시 → fine-tuning 검토 |
