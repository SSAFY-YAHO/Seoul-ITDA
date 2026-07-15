from __future__ import annotations

import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.attraction import Attraction
from app.schemas.chat import ChatResponse
from app.services.chat_service import (
    ChatSource,
    _extract_web_response,
    _is_place_search,
    answer_chat,
)
from app.services.data_service import repair_mojibake


class ChatServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine('sqlite:///:memory:')
        self.engine = engine
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(bind=engine)()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def answer(self, question: str, **overrides):
        options = {
            'db': self.db,
            'question': question,
            'history': [],
            'ai_provider': 'disabled',
            'local_ai_base_url': 'http://localhost:11434',
            'local_ai_model': '',
            'local_ai_timeout_sec': 1,
            'openai_api_key': '',
            'openai_model': 'test-model',
            'openai_web_search_model': 'test-web-model',
            'openai_timeout_sec': 1,
            'openai_web_search_timeout_sec': 1,
            'web_search_enabled': True,
        }
        options.update(overrides)
        return answer_chat(**options)

    def test_general_conversation_does_not_become_place_search(self):
        result = self.answer('안녕! 오늘 기분은 어때?')

        self.assertEqual(result.mode, 'conversation')
        self.assertEqual(result.sources, [])
        self.assertTrue(result.fallback)

    def test_place_search_uses_database_before_web(self):
        self.db.add(
            Attraction(
                source_id='test:1',
                name='경복궁',
                category='관광지',
                district='종로구',
                description='조선 시대 궁궐',
                address='서울 종로구 사직로 161',
                tags='역사,궁궐',
            )
        )
        self.db.commit()

        with patch(
            'app.services.chat_service._openai_web_search',
            side_effect=AssertionError('DB 결과가 있으면 웹 검색을 호출하면 안 됩니다.'),
        ):
            result = self.answer(
                '종로구 관광지 추천해줘',
                openai_api_key='test-key',
            )

        self.assertEqual(result.mode, 'database')
        self.assertEqual(result.sources[0].title, '경복궁')
        response = ChatResponse(
            answer=result.answer,
            sources=[
                {'type': source.type, 'title': source.title, 'url': source.url}
                for source in result.sources
            ],
            provider=result.provider,
            mode=result.mode,
            used_openai=result.used_openai,
            fallback=result.fallback,
        )
        self.assertEqual(response.sources[0].title, '경복궁')

    def test_place_search_without_database_uses_web_search(self):
        self.db.add(
            Attraction(
                source_id='test:unrelated',
                name='망원동 일반 카페',
                category='카페',
                district='마포구',
                description='일반 카페',
                address='서울 마포구 망원동',
                tags='카페',
            )
        )
        self.db.commit()
        expected_sources = [ChatSource(type='web', title='공식 장소', url='https://example.com')]
        with patch(
            'app.services.chat_service._openai_web_search',
            return_value=('웹에서 장소를 찾았어요.', expected_sources),
        ) as web_search:
            result = self.answer(
                '망원동의 새로운 카페 찾아줘',
                openai_api_key='test-key',
            )

        web_search.assert_called_once()
        self.assertEqual(result.mode, 'web')
        self.assertFalse(result.fallback)
        self.assertEqual(result.sources, expected_sources)

    def test_place_followup_uses_previous_user_context(self):
        history = [
            {'role': 'user', 'content': '성수동 데이트 장소 추천해줘'},
            {'role': 'assistant', 'content': '후보를 알려드릴게요.'},
        ]
        self.assertTrue(_is_place_search('그중 조용한 곳은?', history))

    def test_web_response_extracts_text_and_unique_citations(self):
        payload = {
            'output': [
                {
                    'type': 'message',
                    'content': [
                        {
                            'type': 'output_text',
                            'text': '검색 결과입니다.',
                            'annotations': [
                                {
                                    'type': 'url_citation',
                                    'title': '서울시 공식 페이지',
                                    'url': 'https://seoul.go.kr/example',
                                },
                                {
                                    'type': 'url_citation',
                                    'title': '중복 출처',
                                    'url': 'https://seoul.go.kr/example',
                                },
                            ],
                        }
                    ],
                }
            ]
        }

        answer, sources = _extract_web_response(payload)

        self.assertEqual(answer, '검색 결과입니다.')
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].title, '서울시 공식 페이지')


class DataEncodingTestCase(unittest.TestCase):
    def test_repairs_utf8_and_euc_kr_mojibake(self):
        utf8_broken = '경복궁'.encode('utf-8').decode('latin1')
        euc_kr_broken = '양화한강공원'.encode('euc-kr').decode('latin1')

        self.assertEqual(repair_mojibake(utf8_broken), '경복궁')
        self.assertEqual(repair_mojibake(euc_kr_broken), '양화한강공원')


if __name__ == '__main__':
    unittest.main()
