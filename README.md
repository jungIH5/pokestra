# photo-maestro

사진에서 패턴을 분석해 악보를 자동 생성하고 연주하는 AI 앱.

## 핵심 기능

1. **이미지 입력** — 카메라 촬영 또는 갤러리에서 사진 선택
2. **패턴 분석** — AI(Claude Vision)가 색상·형태·반복 구조 등 시각 패턴 추출
3. **음악 매핑** — 패턴을 음계·리듬·템포로 변환
4. **악보 생성** — MusicXML / LilyPond 기반 악보 렌더링
5. **연주** — MIDI 합성으로 즉시 재생

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 모바일 | React Native (Expo) |
| 백엔드 | Python 3.12 + FastAPI |
| AI 분석 | Claude API (Vision) |
| 음악 생성 | music21 |
| 오디오 출력 | FluidSynth / MIDI |
| 인프라 | Docker Compose |

## 프로젝트 구조

```
photo-maestro/
├── backend/
│   ├── api/routes/       # FastAPI 라우터
│   ├── services/         # 핵심 비즈니스 로직
│   │   ├── image_analyzer.py   # 이미지 패턴 분석
│   │   ├── pattern_mapper.py   # 패턴 → 음악 변환
│   │   ├── music_generator.py  # 악보/MIDI 생성
│   │   └── audio_renderer.py   # 오디오 합성
│   ├── models/           # Pydantic 스키마
│   ├── main.py
│   └── requirements.txt
├── mobile/
│   ├── app/              # Expo Router 페이지
│   ├── components/       # 공용 컴포넌트
│   └── store/            # Zustand 상태관리
├── docker-compose.yml
└── README.md
```

## 개발 단계

- [ ] Phase 1: 프로젝트 초기 세팅
- [ ] Phase 2: 이미지 업로드 + Claude Vision 패턴 분석
- [ ] Phase 3: 패턴 → 음악 매핑 알고리즘
- [ ] Phase 4: 악보 생성 및 모바일 렌더링
- [ ] Phase 5: MIDI 재생
- [ ] Phase 6: UI 완성 및 히스토리 기능

## 실행 방법

```bash
docker-compose up --build
```
