# Backend API Documentation

## 커뮤니티 게시글 이미지

- 게시글 작성·수정 요청에 `image_urls` 배열을 선택적으로 전달합니다.
- 최대 5개이며, 생략하면 빈 배열로 처리합니다.
- 게시글 목록·상세 응답에도 `image_urls`가 포함됩니다.

```json
{
  "title": "서울 산책 후기",
  "content": "사진과 함께 기록합니다.",
  "edit_password": "demo1234",
  "image_urls": [
    "https://res.cloudinary.com/example/image/upload/sample-1.webp",
    "https://res.cloudinary.com/example/image/upload/sample-2.webp"
  ]
}
```

- 6개 이상 전달하면 `422 Unprocessable Entity`를 반환합니다.
- 이미지 파일은 Cloudinary에 저장하고 백엔드는 URL 배열만 SQLite에 저장합니다.

## 게시글 좋아요

- Method: `POST`
- Path: `/api/posts/{post_id}/like`
- Description: 지정한 익명 게시글의 좋아요 수를 1 증가시킵니다.
- Request body: 없음
- Success: `200 OK`, `PostResponse`에 `likes` 포함
- Error: 게시글이 없으면 `404 Not Found`와 `{"detail":"Post not found"}` 반환

로그인 없는 MVP이므로 API는 사용자별 중복 여부를 식별하지 않습니다. 프론트엔드는 같은 브라우저의 중복 클릭을 로컬 저장소로 제한합니다.

## 1) Create Post
- Method: `POST`
- Path: `/api/posts`
- Description: 익명 게시글을 생성합니다.

### Request Body
```json
{
  "title": "서울 나들이 추천",
  "content": "한강 근처 코스 추천 부탁해요.",
  "edit_password": "1234"
}
```

### Success Response
- Status: `201 Created`
```json
{
  "id": 1,
  "title": "서울 나들이 추천",
  "content": "한강 근처 코스 추천 부탁해요.",
  "views": 0,
  "created_at": "2026-07-14T10:00:00",
  "updated_at": "2026-07-14T10:00:00"
}
```

### Validation Rules
- `title`: 1~200자
- `content`: 1자 이상
- `edit_password`: 1~100자

## 2) List Posts
- Method: `GET`
- Path: `/api/posts`
- Description: 게시글 목록을 최신순으로 조회합니다.

### Query Parameters
- `q` (optional): 제목/내용 키워드 검색어

### Success Response
- Status: `200 OK`
```json
{
  "items": [
    {
      "id": 2,
      "title": "한강 산책",
      "content": "저녁 코스 추천",
      "views": 0,
      "created_at": "2026-07-14T10:00:00",
      "updated_at": "2026-07-14T10:00:00"
    }
  ],
  "total": 1
}
```

## 3) Get Post Detail
- Method: `GET`
- Path: `/api/posts/{post_id}`
- Description: 게시글 상세를 조회하고 조회수를 1 증가시킵니다.

### Path Parameters
- `post_id`: 게시글 ID

### Success Response
- Status: `200 OK`
```json
{
  "id": 2,
  "title": "한강 산책",
  "content": "저녁 코스 추천",
  "views": 1,
  "created_at": "2026-07-14T10:00:00",
  "updated_at": "2026-07-14T10:00:00"
}
```

## 4) Update Post
- Method: `PUT`
- Path: `/api/posts/{post_id}`
- Description: 수정용 비밀번호를 검증한 뒤 게시글을 수정합니다.

### Request Body
```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "edit_password": "1234"
}
```

## 5) Delete Post
- Method: `DELETE`
- Path: `/api/posts/{post_id}`
- Description: 수정용 비밀번호를 검증한 뒤 게시글을 삭제합니다.

### Request Body
```json
{
  "edit_password": "1234"
}
```

### Success Response
- Status: `200 OK`
```json
{
  "message": "Post deleted"
}
```

### Error Responses
- Status: `400 Bad Request`
```json
{
  "detail": "Edit password is required"
}
```
- Status: `403 Forbidden`
```json
{
  "detail": "Edit password mismatch"
}
```
- Status: `404 Not Found`
```json
{
  "detail": "Post not found"
}
```

### Success Response
- Status: `200 OK`
```json
{
  "id": 2,
  "title": "수정된 제목",
  "content": "수정된 내용",
  "views": 2,
  "created_at": "2026-07-14T10:00:00",
  "updated_at": "2026-07-14T10:10:00"
}
```

### Error Responses
- Status: `400 Bad Request`
```json
{
  "detail": "Edit password is required"
}
```
- Status: `403 Forbidden`
```json
{
  "detail": "Edit password mismatch"
}
```
- Status: `404 Not Found`
```json
{
  "detail": "Post not found"
}
```

### Error Response
- Status: `404 Not Found`
```json
{
  "detail": "Post not found"
}
```

## 6) Load Seoul Data
- Method: `POST`
- Path: `/api/data/load`
- Description: 서울 관광 JSON 데이터를 DB `attractions` 테이블로 적재합니다.

### Request Body
```json
{
  "file_path": "data"
}
```

- `file_path` 미지정 시 `.env`의 `SEOUL_DATA_PATH`(기본값 `data`)를 사용합니다.
- `data` 디렉토리를 지정하면 `서울_*.json` 파일들을 일괄 적재합니다.

### Success Response
- Status: `200 OK`
```json
{
  "message": "Seoul TourAPI data load completed",
  "loaded": 6518,
  "updated": 0,
  "skipped": 0,
  "processed_files": 7,
  "file_path": "C:\\path\\to\\data"
}
```

### Error Responses
- Status: `404 Not Found` (파일 없음)
- Status: `500 Internal Server Error` (적재 실패)

## 7) Chat
- Method: `POST`
- Path: `/api/chat`
- Description: 서울 관광 데이터와 커뮤니티 게시글을 근거로 답변합니다.

### Request Body
```json
{
  "question": "종로구 관광지 추천해줘"
}
```

### Success Response
- Status: `200 OK`
```json
{
  "answer": "관광 데이터 기준 추천: ...",
  "sources": ["attraction:경복궁"],
  "used_openai": false,
  "fallback": true
}
```

### Rules
- `OPENAI_API_KEY`가 없거나 OpenAI 호출 실패 시 로컬 데이터 기반 fallback 답변을 반환합니다.
- 답변에는 `sources`로 근거 레코드를 함께 반환합니다.

## 8) Chat v2
- Method: `POST`
- Path: `/api/chat`
- Description: 일반 대화를 지원하며, 장소 탐색은 내부 DB를 먼저 검색하고 결과가 없을 때만 웹 검색을 사용합니다.

### Request Body
```json
{
  "question": "그중 조용한 곳은?",
  "history": [
    {"role": "user", "content": "성수동 데이트 장소 추천해줘"},
    {"role": "assistant", "content": "후보를 알려드릴게요."}
  ]
}
```

### Success Response
```json
{
  "answer": "답변 내용",
  "sources": [
    {"type": "attraction", "title": "장소명", "url": "https://map.naver.com/..."}
  ],
  "provider": "openai",
  "mode": "database",
  "used_openai": true,
  "fallback": false
}
```

### Modes
- `conversation`: 일반 대화. 장소 DB를 조회하지 않습니다.
- `database`: 내부 장소·커뮤니티 데이터에 검색 결과가 있습니다.
- `web`: 내부 검색 결과가 없어 웹 검색을 시도했습니다.

### Rules
- `history`는 최근 10건까지 전달합니다.
- AI API 응답은 백엔드에서 핵심 문장 중심으로 정리하고 최대 800자로 제한한 뒤 반환합니다.
- 웹 검색 답변은 따뜻한 도입 문장과 최대 5개의 `이름 → 날짜·장소 → 설명` 항목으로 정리합니다.
- 웹 검색 본문에서는 URL·마크다운 인용·보고서형 필드명을 제거하고, 출처는 `sources`에만 분리해 반환합니다.
- 웹 출처 URL의 `utm_*` 추적 파라미터는 제거합니다.
- 웹 검색은 `CHAT_WEB_SEARCH_ENABLED=true`, 유효한 `OPENAI_API_KEY`, 웹 검색 지원 모델이 모두 필요합니다.
- 내부 DB 결과가 한 건이라도 있으면 웹 검색을 호출하지 않습니다.
# Android 앱 CORS

Capacitor Android 앱은 `https://localhost` 출처에서 API를 호출한다. 모든 `/api/*` 엔드포인트는 이 출처와 `http://localhost` 호환 출처의 CORS 요청을 허용한다.
# 댓글 API

## 댓글 목록

- Method: `GET`
- Path: `/api/posts/{post_id}/comments`
- Success: `200 OK`
- Response: `{ "items": CommentResponse[], "total": number }`
- Error: 게시글이 없으면 `404 Not Found`

## 댓글 작성

- Method: `POST`
- Path: `/api/posts/{post_id}/comments`
- Body: `{ "author": "닉네임", "content": "댓글 내용" }`
- 제한: 닉네임 1~30자, 내용 1~1,000자, 공백만 입력할 수 없음
- Success: `201 Created`, 생성된 `CommentResponse`
- Error: 게시글이 없으면 `404 Not Found`, 입력값이 잘못되면 `422 Unprocessable Entity`

## 댓글 좋아요

- Method: `POST`
- Path: `/api/posts/{post_id}/comments/{comment_id}/like`
- Success: `200 OK`, 좋아요가 증가한 `CommentResponse`
- Error: 해당 게시글의 댓글이 없으면 `404 Not Found`

`CommentResponse` 필드: `id`, `post_id`, `author`, `content`, `likes`, `created_at`
