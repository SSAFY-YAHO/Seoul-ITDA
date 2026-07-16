from __future__ import annotations

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Comment, Post
from app.schemas.comment import CommentCreateRequest
from app.services.comment_service import (
    CommentNotFoundError,
    CommentPostNotFoundError,
    ParentCommentNotFoundError,
    create_comment,
    like_comment,
    list_comments,
)


class CommentServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.post = Post(title='테스트', content='내용', edit_password='1234')
        self.db.add(self.post)
        self.db.commit()
        self.db.refresh(self.post)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_create_and_list_comments(self):
        comment = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='여행자', content='좋은 정보네요!'),
        )

        comments = list_comments(self.db, self.post.id)
        self.assertEqual([item.id for item in comments], [comment.id])
        self.assertEqual(comments[0].author, '여행자')

    def test_create_comment_for_missing_post_fails(self):
        with self.assertRaises(CommentPostNotFoundError):
            create_comment(
                self.db,
                999,
                CommentCreateRequest(author='여행자', content='댓글'),
            )

    def test_like_comment(self):
        comment = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='여행자', content='댓글'),
        )

        liked = like_comment(self.db, self.post.id, comment.id)
        self.assertEqual(liked.likes, 1)

    def test_like_missing_comment_fails(self):
        with self.assertRaises(CommentNotFoundError):
            like_comment(self.db, self.post.id, 999)

    def test_create_reply_for_top_level_comment(self):
        parent = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='여행자', content='부모 댓글'),
        )

        reply = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='서울친구', content='대댓글', parent_id=parent.id),
        )

        self.assertEqual(reply.parent_id, parent.id)
        self.assertEqual(list_comments(self.db, self.post.id)[1].content, '대댓글')

    def test_reply_parent_must_be_top_level_comment_in_same_post(self):
        parent = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='여행자', content='부모 댓글'),
        )
        reply = create_comment(
            self.db,
            self.post.id,
            CommentCreateRequest(author='서울친구', content='대댓글', parent_id=parent.id),
        )

        with self.assertRaises(ParentCommentNotFoundError):
            create_comment(
                self.db,
                self.post.id,
                CommentCreateRequest(author='세 번째', content='3단 댓글', parent_id=reply.id),
            )


if __name__ == '__main__':
    unittest.main()
