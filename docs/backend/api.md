# Backend API Documentation

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
  "file_path": "data/seoul_places.json"
}
```

### Success Response
- Status: `200 OK`
```json
{
  "message": "Seoul data load completed",
  "loaded": 3,
  "updated": 0,
  "skipped": 0,
  "file_path": "C:\\path\\to\\data\\seoul_places.json"
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
