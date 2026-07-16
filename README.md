# LocalHub Seoul MVP

AGENTS.md 기준으로 Vue 3 프론트엔드와 FastAPI 백엔드의 초기 실행 구조를 구성한 저장소입니다.

## 구조

```text
frontend/
	src/
		components/
		router/
		services/
		views/
backend/
	app/
		models/
		routers/
		schemas/
		services/
data/
docs/
```

## 빠른 시작

1. 루트의 `.env.example`을 복사해 `.env`를 만듭니다.
2. 프론트엔드 의존성을 설치합니다.
3. Python 가상환경을 만들고 백엔드 의존성을 설치합니다.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

`VITE_API_BASE_URL` is optional. If it is unset, the frontend calls the same origin it was deployed from,
which is the safer default for production deployments behind a single domain or reverse proxy.

### Backend

```bash
python -m venv .venv
.venv/Scripts/pip install -r backend/requirements.txt
cd backend
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

`DATABASE_URL=sqlite:///./backend/localhub.db` is resolved relative to the repository root by the app,
so the backend can be started from either the repo root or the `backend/` directory without breaking
data loading.

For production, set `CHAT_AI_PROVIDER=openai` unless you intentionally run a local Ollama service in the same
environment. `local` should be treated as an explicit opt-in deployment mode.

The chatbot supports normal multi-turn conversation and automatically detects place-search questions. Place
searches use the local attraction/community database first. Only when no local match exists and
`CHAT_WEB_SEARCH_ENABLED=true` does the backend call the OpenAI Responses API web search tool. Configure the
search-capable model separately with `OPENAI_WEB_SEARCH_MODEL`.

## PWA 설치

프로덕션 빌드는 웹 앱 매니페스트와 서비스 워커를 포함하며, HTTPS로 배포하면 홈 화면이나 데스크톱에
`서울잇다` 앱으로 설치할 수 있습니다.

- Chrome·Edge 등 Chromium 브라우저에서는 설치 조건을 만족하면 헤더에 `앱 설치` 버튼이 표시됩니다.
- iPhone·iPad에서는 브라우저 공유 메뉴의 `홈 화면에 추가`를 사용합니다.
- 설치 후에는 주소 표시줄이 없는 독립 창으로 실행됩니다.
- 한 번 불러온 정적 화면은 기본 캐시에 저장되며, 네트워크 연결이 없으면 오프라인 안내 화면을 제공합니다.
- 서비스 워커는 캐시 혼선을 피하기 위해 `npm run dev`에서는 등록하지 않고 프로덕션 빌드에서만 등록합니다.

PWA 주요 파일은 `frontend/public/manifest.webmanifest`, `frontend/public/sw.js`,
`frontend/public/icons/`에 있습니다.

## 기본 엔드포인트

- `GET /` : 앱 메타 정보
- `GET /api/health` : 서버 및 DB 설정 상태 확인

## 다음 단계

- 서울 공공데이터 적재
- 게시판 모델/스키마/CRUD 추가
- 챗봇 서비스와 `POST /api/chat` 구현
