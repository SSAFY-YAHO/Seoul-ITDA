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
