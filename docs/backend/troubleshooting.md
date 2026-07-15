# Backend Troubleshooting

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
