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

### API: GET /api/posts/{post_id}
- 구현 파일
  - `backend/app/routers/posts.py`
  - `backend/app/services/post_service.py`
  - `docs/backend/api.md`
- 작업 내용
  - 게시글 상세 조회 API 추가
  - 상세 조회 시 조회수 1 증가 로직 반영
  - 미존재 게시글 요청 시 404 처리
- 검증
  - 동일 게시글 2회 조회 시 `views`가 1씩 증가하는지 확인
  - 없는 ID 조회 시 404 응답 확인

### API: PUT /api/posts/{post_id}
- 구현 파일
  - `backend/app/routers/posts.py`
  - `backend/app/services/post_service.py`
  - `backend/app/schemas/post.py`
  - `docs/backend/api.md`
- 작업 내용
  - 게시글 수정 API 추가
  - 수정 비밀번호 누락/불일치/게시글 미존재 케이스를 구분 응답
- 검증
  - 올바른 비밀번호 수정 성공(200) 확인
  - 비밀번호 누락(400), 불일치(403), 미존재 ID(404) 확인

### API: DELETE /api/posts/{post_id}
- 구현 파일
  - `backend/app/routers/posts.py`
  - `backend/app/services/post_service.py`
  - `backend/app/schemas/post.py`
  - `docs/backend/api.md`
- 작업 내용
  - 게시글 삭제 API 추가
  - 삭제 비밀번호 누락/불일치/게시글 미존재 케이스 구분 응답
- 검증
  - 올바른 비밀번호 삭제 성공(200) 확인
  - 비밀번호 누락(400), 불일치(403), 미존재 ID(404) 확인
