# Backend Development Log

## 2026-07-15: 커뮤니티 다중 이미지 첨부

- 게시글 작성·수정·목록·상세 스키마에 최대 5개의 `image_urls` 추가
- SQLite에는 JSON 문자열로 저장하고 응답에서는 URL 배열로 변환
- 기존 DB에 `images_json` 컬럼을 시작 시 안전하게 추가
- Cloudinary 직접 업로드, 파일 형식·5MB 용량·5장 제한, 미리보기와 삭제 구현
- 상세 이미지 갤러리와 목록 대표 썸네일 구현
- 검증: URL 2개 저장 201, URL 6개 요청 422, 테스트 게시글 삭제 확인

## 2026-07-15: 게시글 좋아요 API

- 게시글 `likes` 컬럼과 좋아요 증가 서비스 추가
- 게시글 상세 응답에 `likes` 포함
- 기존 SQLite DB에 시작 시 컬럼을 안전하게 추가하는 호환 처리
- 상세 화면 좋아요 버튼 및 같은 브라우저 중복 클릭 방지
- 검증: 게시글 1번의 좋아요가 0에서 1로 증가하며 200 응답
- 오류 검증: 존재하지 않는 게시글 좋아요 요청에 404 응답

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

### 2026-07-15: 대화형 챗봇과 DB 우선 장소 탐색
- 구현 파일
  - `backend/app/services/chat_service.py`
  - `backend/app/schemas/chat.py`
  - `backend/app/routers/chat.py`
  - `frontend/src/components/chatbot/ChatbotWidget.vue`
- 작업 내용
  - 일반 대화에서는 장소 DB를 조회하지 않는 대화형 응답 경로 추가
  - 장소 탐색 질문은 서울잇다 DB와 커뮤니티를 우선 검색
  - 내부 결과가 없을 때만 OpenAI Responses API의 웹 검색 도구 호출
  - 최근 대화 10건 전달 및 DB/웹 출처 링크 표시
  - 적재 원본의 UTF-8/EUC-KR 깨짐 문자열을 DB 저장 전에 복구
- 검증
  - 일반 대화, DB 우선, DB 미검색 시 웹 검색, 후속 질문, 웹 출처 파싱 테스트 6건 통과
  - 프론트엔드 프로덕션 빌드 통과

### 2026-07-15: AI 응답 백엔드 요약
- 작업 내용
  - 일반 대화·내부 DB·웹 검색 프롬프트에 핵심 요약과 길이 제한 적용
  - AI 응답을 백엔드에서 최대 800자로 정리한 뒤 프론트에 반환
  - 기존 로컬 저장소의 긴 메시지는 히스토리 전송 시 1,000자로 제한
- 검증
  - 긴 AI 응답 요약 및 응답 길이 회귀 테스트 추가

### 2026-07-16: 웹 검색 답변 안내 형식 개선
- 작업 내용
  - 웹 검색 결과를 따뜻한 도입과 `행사명 → 날짜·장소 → 한 줄 설명` 형식으로 생성하도록 프롬프트 개선
  - 확인된 결과가 부족할 때 항목 수를 억지로 채우지 않고, 같은 장소의 유사 프로그램을 합치도록 제한
  - 답변 본문의 URL·마크다운 인용·출처 줄·보고서형 필드명·중복 요약 제거
  - 웹 출처를 기존 `sources` 버튼 영역으로 분리하고 `utm_*` 추적 파라미터 제거
  - 한국 표준시 기준 현재 날짜와 월요일~일요일 범위를 웹 검색에 전달
- 검증
  - 웹 응답 정제·출처 중복 제거·프롬프트 형식 회귀 테스트 포함 백엔드 테스트 10건 통과
  - 실제 웹 검색 응답에서 본문 URL·마크다운 링크 제거 및 별도 출처 반환 확인

### 2026-07-16: 서울잇다 PWA 설치 지원
- 작업 내용
  - 기존 해치 SVG 브랜드를 바탕으로 180px·192px·512px·마스커블 앱 아이콘 제작
  - 웹 앱 매니페스트와 Android·Chromium·iOS 설치 메타데이터 연결
  - 지원 브라우저에서만 표시되는 `앱 설치` 버튼 추가
  - 프로덕션 전용 서비스 워커와 오프라인 안내 화면 추가
  - 동일 출처의 정적 자산만 캐시하고 API 및 외부 요청은 서비스 워커에서 제외
- 검증
  - 프론트엔드 프로덕션 빌드 통과
  - 미리보기 서버에서 홈·매니페스트·서비스 워커·아이콘 HTTP 200 확인
  - 매니페스트 및 Apple Touch 아이콘 링크, 180/192/512px 이미지 크기 확인
# Android 앱 CORS 허용

- Capacitor Android WebView의 기본 출처인 `https://localhost`와 호환 출처 `http://localhost`를 백엔드 기본 허용 목록에 추가했다.
- Render의 `CORS_ORIGINS` 환경변수에 값이 누락되어도 Android 앱의 API 요청과 preflight 요청이 허용된다.
- GET 및 OPTIONS 요청에 대한 자동 테스트를 추가했다.
# 게시글 댓글과 댓글 좋아요

- 게시글별 댓글을 저장하는 `comments` 테이블과 SQLAlchemy 모델을 추가했다.
- 댓글 목록, 작성, 댓글 좋아요 API를 추가했다.
- 게시글 삭제 시 연결된 댓글을 함께 삭제하도록 처리했다.
- 댓글 작성·조회·좋아요와 누락 게시글·댓글 오류 테스트를 추가했고 전체 백엔드 테스트 16개가 통과했다.
# 한 단계 대댓글

- 댓글에 선택적 `parent_id`를 추가해 최상위 댓글 아래 한 단계 대댓글을 지원한다.
- 부모 댓글은 같은 게시글의 최상위 댓글이어야 하며, 대댓글에 다시 답글을 작성하는 3단 구조는 차단한다.
- 기존 Render SQLite의 `comments` 테이블에는 앱 시작 시 `parent_id` 컬럼을 호환 방식으로 추가한다.
