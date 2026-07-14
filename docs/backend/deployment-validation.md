# Backend Deployment Validation (Render-ready)

## 2026-07-14 Local Production-like Check

### Goal
- Render 배포 전, 프로덕션 유사 환경변수로 로컬 기동/핵심 API 동작을 검증한다.

### Environment
- `APP_ENV=production`
- `DATABASE_URL=sqlite:///./localhub.db` (backend 작업 디렉토리 기준)
- `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`

### Commands
```bash
cd backend
APP_ENV=production DATABASE_URL=sqlite:///./localhub.db ../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### Validation Scenarios
1. `POST /api/data/load` 호출로 `attractions` 적재
2. `POST /api/chat` 호출로 데이터 기반 답변 반환 확인
3. SQLite 테이블 확인: `posts`, `attractions`

### Result
- 데이터 적재 성공 (`loaded=3`)
- 챗봇 응답 성공 (fallback 경로 포함)
- 테이블 확인 완료: `posts`, `attractions`

### Render Notes
- Render 환경에서는 `DATABASE_URL`을 절대/명시 경로로 지정해야 상대경로 이슈를 피할 수 있다.
- `OPENAI_API_KEY` 미설정 시 챗봇은 로컬 fallback으로 동작한다.
- 운영 환경에서는 `.env` 직접 커밋 금지, Render 환경변수로만 주입한다.
