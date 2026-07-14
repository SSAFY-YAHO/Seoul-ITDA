# Backend Development Log

## 2026-07-14

### API: POST /api/posts
- 구현 파일
  - `backend/app/models/post.py`
  - `backend/app/schemas/post.py`
  - `backend/app/services/post_service.py`
  - `backend/app/routers/posts.py`
  - `backend/app/main.py`
- 작업 내용
  - 게시글 SQLAlchemy 모델 추가
  - 게시글 생성 요청/응답 스키마 추가
  - 생성 서비스 및 라우터 구현
- 검증
  - `uvicorn` 실행 후 Python `urllib` 요청으로 201 응답 및 필드 생성 확인

### API: GET /api/posts
- 구현 파일
  - `backend/app/routers/posts.py`
  - `backend/app/services/post_service.py`
  - `backend/app/schemas/post.py`
  - `docs/backend/api.md`
- 작업 내용
  - 게시글 목록 조회 API 추가
  - `q` 파라미터 기반 제목/내용 부분 일치 검색 추가
  - 최신 생성 순 정렬 반환
- 검증
  - 전체 목록 응답(`total=2`) 확인
  - 키워드 `한강` 검색 응답(`total=1`) 확인
