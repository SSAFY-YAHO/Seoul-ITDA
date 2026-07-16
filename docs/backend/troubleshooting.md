# Backend Troubleshooting

## 2026-07-15: 백엔드 구문 검사 가상환경 경로 오류

- 증상: 저장소 루트에서 `..\.venv\Scripts\python.exe`를 찾지 못함
- 원인: 백엔드 디렉터리 기준 상대경로를 저장소 루트에서 사용함
- 조치: 루트에서는 `.\.venv\Scripts\python.exe`로 실행
- 결과: 실행 위치별 가상환경 상대경로를 구분함

## 2026-07-15: 커뮤니티 이미지 저장과 배포 영속성

- 증상: Render 무료 파일 시스템에 직접 저장한 업로드 파일은 재배포 시 사라질 수 있음
- 원인: 무료 인스턴스 로컬 디스크가 영속 저장소가 아님
- 조치: 파일은 Cloudinary에 업로드하고 SQLite에는 HTTPS URL만 저장
- 설정: Netlify에 `VITE_CLOUDINARY_CLOUD_NAME`, `VITE_CLOUDINARY_UPLOAD_PRESET` 등록
- 제한: Unsigned Upload Preset에서 허용 형식, 최대 파일 크기, 저장 폴더를 제한해야 함

## 2026-07-15: 기존 게시글 테이블의 이미지 컬럼 호환

- 증상: 기존 SQLite `posts` 테이블에 이미지 URL 저장 컬럼이 없음
- 원인: `create_all()`은 기존 테이블 컬럼을 자동 변경하지 않음
- 조치: 서버 시작 시 `images_json` 존재 여부를 확인하고 없을 때만 기본값 `[]` 컬럼 추가
- 결과: 기존 게시글을 유지하면서 이미지 첨부 응답 정상 동작

## 2026-07-15: Render 배포 전환 중 게시글 좋아요 404

- 증상: 목록에서 받은 게시글 ID로 좋아요 요청 시 일시적으로 404 반환
- 원인: 무료 Render 인스턴스 교체 시 영구 디스크가 없는 SQLite DB가 초기화되어 기존 게시글 ID가 사라짐
- 조치: 새 배포 완료 후 목록과 상세의 현재 ID를 다시 확인하고 좋아요 API 재검증
- 결과: 현재 게시글 ID의 상세 조회와 좋아요 요청 모두 200 응답 확인
- 참고: 배포 간 게시글 보존이 필요하면 Persistent Disk 또는 외부 영속 DB가 필요함

## 2026-07-15: 프론트 빌드 작업 디렉터리 오류

- 증상: `npm run build` 실행 시 `backend/package.json`을 찾을 수 없다는 ENOENT 발생
- 원인: 백엔드 구문 검사와 프론트 빌드를 `backend` 작업 디렉터리에서 연속 실행함
- 조치: 프론트 빌드는 `frontend` 디렉터리에서 별도로 실행
- 결과: 코드나 의존성 문제가 아닌 실행 위치 문제로 확인

## 2026-07-15: 기존 SQLite 게시글 테이블의 좋아요 컬럼 호환

- 증상: 모델에 `likes`를 추가해도 기존 SQLite 테이블에는 컬럼이 자동 추가되지 않음
- 원인: `Base.metadata.create_all()`은 기존 테이블의 컬럼 변경을 수행하지 않음
- 조치: 시작 시 스키마를 확인하고 `likes`가 없을 때만 기본값 0 컬럼을 추가
- 결과: 기존 게시글과 DB를 유지하면서 좋아요 API가 정상 동작함

## 2026-07-14: DB 경로 이슈
- 증상: `sqlite3.OperationalError: unable to open database file`
- 원인: 작업 디렉토리와 `DATABASE_URL` 상대 경로 불일치
- 조치: 실행 시 `DATABASE_URL=sqlite:///./localhub.db` 지정 또는 기본 경로를 실행 위치와 일치하도록 조정
- 상태: 재현 및 정상 기동 확인 완료

## 2026-07-14: TestClient 실행 오류
- 증상: `RuntimeError: The starlette.testclient module requires the httpx package`
- 원인: 테스트 전용 의존성 `httpx`가 현재 requirements에 미포함
- 조치: 운영 의존성 최소화를 위해 `uvicorn + urllib` 방식으로 API 검증 전환
- 상태: `POST /api/posts` 201 응답 확인 완료

## 2026-07-14: curl JSON 파싱 오류 (Git Bash)
- 증상: `{"detail":"There was an error parsing the body"}`
- 원인: Git Bash 환경에서 JSON 인용부호 이스케이프가 깨짐
- 조치: Python `urllib.request`로 JSON 직렬화 후 요청
- 상태: 정상 요청/응답 확인 완료

## 2026-07-14: 라우터 확장 중 import 누락
- 증상: 신규 delete 엔드포인트 연결 시 함수 참조 오류 가능성 확인
- 원인: `delete_post` 서비스 import 누락
- 조치: `backend/app/routers/posts.py`에 `delete_post` import 추가
- 상태: 삭제 API 정상 호출 확인 완료

## 2026-07-14: 챗봇 문장형 질의 매칭 실패
- 증상: `종로구 관광지 추천해줘` 질의에서 데이터 매칭 실패
- 원인: 질문 전체 문자열 단일 LIKE 검색으로 매칭률 저하
- 조치: 질문을 키워드 단위로 분해해 OR 조건 검색으로 개선
- 상태: 키워드 기반 근거 응답 정상 확인

## 2026-07-14: 변경 코드 미반영 검증 이슈
- 증상: 코드 수정 직후 테스트 결과가 이전과 동일
- 원인: `uvicorn` 재시작 없이 기존 프로세스에 요청
- 조치: 서버 재시작 후 동일 시나리오 재검증
- 상태: 개선 로직 반영 및 응답 정상 확인

## 2026-07-15: 장소 DB 한글 인코딩 손상
- 증상: 한글 장소 질문이 DB의 기존 장소명·주소와 일치하지 않아 웹 검색으로 넘어갈 수 있음
- 원인: 원본 JSON에 UTF-8 또는 EUC-KR 바이트가 Latin-1 문자열로 잘못 저장된 항목이 혼재
- 조치: 데이터 적재 시 문자열 품질을 비교해 한글을 복구하고, 서버 시작 시 손상된 기존 DB를 감지해 재동기화
- 상태: 대표 UTF-8/EUC-KR 손상 문자열 복구 테스트 통과

## 2026-07-15: OpenAI 대화·웹 검색 fallback 동작
- 증상: 일반 대화와 웹 검색이 `fallback=true`로 반환됨
- 원인: 설정된 OpenAI API 키의 계정에서 `429 insufficient_quota` 응답 반환
- 조치: API 오류 시 서비스 전체가 실패하지 않도록 유형별 안내 응답 유지, OpenAI 사용 한도 충전 후 동일 설정으로 재시도
- 상태: OpenAI 엔드포인트 도달 및 오류 처리 확인, 내부 DB 장소 응답은 정상 동작

## 2026-07-15: API 프로젝트 모델 접근 권한 불일치
- 증상: 새 API 키 적용 후 일반 대화가 `403 model_not_found`로 fallback 처리됨
- 원인: API 프로젝트는 `gpt-5-mini`만 사용할 수 있지만 환경변수가 `gpt-4o-mini`, `gpt-5.4-mini`로 설정됨
- 조치: 일반 대화와 웹 검색 모델을 `gpt-5-mini`로 통일하고 지원하지 않는 `temperature` 옵션 제거
- 상태: `gpt-5-mini` 일반 대화와 웹 검색 실호출 성공, 웹 검색 출처 4개 반환 확인

## 2026-07-15: 긴 대화 내역으로 다음 질문 422 오류
- 증상: 긴 웹 검색 답변 다음 질문에서 프론트가 `답변을 불러오지 못했습니다` 표시
- 원인: 1,000자를 넘는 이전 AI 답변이 `history` 스키마의 글자 수 제한을 초과
- 조치: 백엔드 응답을 최대 800자로 요약하고 프론트 히스토리도 메시지당 1,000자로 제한
- 상태: 1,001자 입력의 422 재현 후 길이 제한 회귀 테스트 추가

## 2026-07-16: Windows에서 서울 시간대 데이터 조회 실패
- 증상: 웹 검색 프롬프트의 이번 주 범위 테스트에서 `ZoneInfoNotFoundError: Asia/Seoul` 발생
- 원인: 프로젝트 Python 환경에 IANA 시간대 데이터 패키지 `tzdata`가 설치되어 있지 않음
- 조치: 추가 의존성 없이 동작하도록 서울 시간을 고정 UTC+9 기준으로 계산
- 상태: 전체 백엔드 테스트 10건 통과

## 2026-07-16: 웹 검색 응답 60초 초과
- 증상: 동일한 축제 검색을 연속 호출할 때 `OPENAI_WEB_SEARCH_TIMEOUT_SEC=60`을 넘겨 fallback 응답 반환
- 원인: OpenAI 웹 검색 처리 지연. `Selected model is at capacity` 메시지는 사용량 소진이 아닌 별도의 일시적 모델 용량 부족 상태
- 조치: 서비스 오류 대신 기존 fallback 안내를 유지하며, 일시적 용량 부족은 간격을 두고 재시도
- 상태: 실호출 성공 시 웹 본문 URL 제거와 출처 분리 확인, 연속 재호출 2건은 타임아웃 fallback 확인

## 2026-07-16: PWA 미리보기 검증 스크립트 실행 실패
- 증상: Vite 미리보기 서버가 실행 중인데 준비 확인 단계에서 계속 실패로 판정됨
- 원인: PowerShell은 변수명을 대소문자 구분하지 않아 응답 변수 `$home`이 읽기 전용 예약 변수 `$HOME`과 충돌
- 조치: 응답 변수명을 `$homeResponse`로 변경하고 프로덕션 미리보기 자산을 다시 요청
- 상태: 홈·매니페스트·서비스 워커·아이콘 모두 HTTP 200 확인
# Android 앱에서 API 연결 실패

- 원인: Capacitor WebView의 `Origin`은 `https://localhost`이며, Render CORS 허용 목록에 없으면 브라우저가 응답을 차단한다.
- 조치: 백엔드가 `https://localhost`와 `http://localhost`를 항상 허용하도록 설정하고 Render 백엔드를 재배포한다.
- 확인: `Origin: https://localhost` GET 응답과 OPTIONS preflight 응답에 `access-control-allow-origin` 헤더가 포함되어야 한다.
# 댓글 API가 404를 반환하는 경우

- 댓글 목록·작성에서 404가 발생하면 URL의 게시글 ID가 실제로 존재하는지 확인한다.
- 댓글 좋아요에서 404가 발생하면 댓글이 해당 게시글에 속하는지 확인한다. 다른 게시글의 댓글 ID는 허용하지 않는다.
- Render 배포 후 최초 시작 시 `Base.metadata.create_all()`이 `comments` 테이블을 생성했는지 로그와 DB를 확인한다.
# 대댓글 작성이 404를 반환하는 경우

- `parent_id`가 같은 게시글의 최상위 댓글 ID인지 확인한다.
- 다른 게시글의 댓글이나 이미 대댓글인 항목을 부모로 지정하면 한 단계 구조 규칙에 따라 거부된다.
- 기존 DB에서 오류가 나면 Render 재시작 로그에서 `parent_id` 호환 컬럼 추가가 실행됐는지 확인한다.
