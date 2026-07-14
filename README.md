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

### Backend

```bash
python -m venv .venv
.venv/Scripts/pip install -r backend/requirements.txt
cd backend
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

## 기본 엔드포인트

- `GET /` : 앱 메타 정보
- `GET /api/health` : 서버 및 DB 설정 상태 확인

## 다음 단계

- 서울 공공데이터 적재
- 게시판 모델/스키마/CRUD 추가
- 챗봇 서비스와 `POST /api/chat` 구현