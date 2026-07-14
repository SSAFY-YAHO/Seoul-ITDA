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
