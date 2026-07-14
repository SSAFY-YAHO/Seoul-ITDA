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
