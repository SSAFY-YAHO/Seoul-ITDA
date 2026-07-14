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

### API: POST /api/data/load
- 구현 파일
  - `backend/app/models/attraction.py`
  - `backend/app/services/data_service.py`
  - `backend/app/schemas/data.py`
  - `backend/app/routers/data.py`
  - `data/seoul_places.json`
- 작업 내용
  - 서울 관광 데이터 테이블(`attractions`) 추가
  - JSON 파일 적재 API 추가(신규/갱신/스킵 집계)
  - 파일 미존재/적재 실패 예외 처리
- 검증
  - 기본 파일 적재 호출로 `loaded=3` 확인
  - DB 테이블 생성 및 건수 확인

### API: POST /api/chat
- 구현 파일
  - `backend/app/services/chat_service.py`
  - `backend/app/schemas/chat.py`
  - `backend/app/routers/chat.py`
  - `backend/app/config.py`
- 작업 내용
  - 관광 데이터/게시글 기반 질의 응답 API 추가
  - OpenAI 호출 경로 + 로컬 fallback 경로 구성
  - 문장형 질문 대응을 위한 키워드 기반 검색 개선
- 검증
  - `종로구 관광지 추천해줘` 질의에 데이터 근거 응답 확인
  - `OPENAI_API_KEY` 미설정 상태 fallback 응답 확인
