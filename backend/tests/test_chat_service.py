from __future__ import annotations

import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.attraction import Attraction
from app.schemas.chat import ChatResponse
from app.services.chat_service import (
    MAX_CHAT_ANSWER_LENGTH,
    ChatResult,
    ChatSource,
    _extract_web_response,
    _is_place_search,
    _openai_chat_answer,
    _openai_web_search,
    answer_chat,
    summarize_chat_answer,
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

    def test_web_response_removes_inline_links_and_tracking_parameters(self):
        payload = {
            'output': [
                {
                    'type': 'message',
                    'content': [
                        {
                            'type': 'output_text',
                            'text': (
                                '이번 주 서울 행사를 찾아봤어요.\n\n'
                                '1. 식물원은 미술관\n'
                                '기간·장소: 7월 15일~8월 17일 · 서울식물원\n'
                                '한 문장: 식물과 미술을 함께 즐겨요. '
                                '([서울문화포털](https://culture.seoul.go.kr/event?utm_source=openai))\n'
                                '출처: https://culture.seoul.go.kr/event?utm_source=openai\n'
                                '요약: 이번 주에는 서울식물원을 추천합니다.'
                            ),
                            'annotations': [
                                {
                                    'type': 'url_citation',
                                    'title': '서울문화포털',
                                    'url': 'https://culture.seoul.go.kr/event?id=1&utm_source=openai',
                                },
                            ],
                        }
                    ],
                }
            ]
        }

        answer, sources = _extract_web_response(payload)

        self.assertIn('식물원은 미술관', answer)
        self.assertNotIn('http', answer)
        self.assertNotIn('[서울문화포털]', answer)
        self.assertNotIn('출처:', answer)
        self.assertNotIn('기간·장소:', answer)
        self.assertNotIn('한 문장:', answer)
        self.assertNotIn('요약:', answer)
        self.assertEqual(sources[0].url, 'https://culture.seoul.go.kr/event?id=1')

    def test_web_search_requests_user_facing_answer_without_inline_sources(self):
        response_payload = {
            'output': [
                {
                    'type': 'message',
                    'content': [
                        {
                            'type': 'output_text',
                            'text': '이번 주 서울 행사를 찾아봤어요.',
                            'annotations': [],
                        }
                    ],
                }
            ]
        }
        with patch(
            'app.services.chat_service._post_json',
            return_value=response_payload,
        ) as post_json:
            _openai_web_search(
                question='이번 주 서울 축제 알려줘',
                history=[],
                api_key='test-key',
                model='gpt-5-mini',
                timeout_sec=1,
            )

        instructions = post_json.call_args.args[1]['instructions']
        self.assertIn('각 항목은 반드시 다음 예시처럼 꼬리표 없이 세 줄', instructions)
        self.assertIn('본문에는 URL, 출처명, 마크다운 링크, 인용 표식을 절대 넣지 마라', instructions)
        self.assertIn('그 뒤 요약이나 결론을 추가하지 마라', instructions)
        self.assertIn('이번 주는', instructions)

    def test_openai_chat_omits_unsupported_temperature(self):
        with patch(
            'app.services.chat_service._post_json',
            return_value={'choices': [{'message': {'content': '안녕하세요!'}}]},
        ) as post_json:
            answer = _openai_chat_answer(
                question='안녕',
                history=[],
                context_lines=[],
                api_key='test-key',
                model='gpt-5-mini',
                timeout_sec=1,
            )

        payload = post_json.call_args.args[1]
        self.assertNotIn('temperature', payload)
        self.assertEqual(answer, '안녕하세요!')

    def test_long_api_answer_is_summarized_before_response(self):
        long_answer = ('첫 번째 핵심 문장입니다. ' * 80).strip()

        result = ChatResult(
            answer=long_answer,
            sources=[],
            provider='openai',
            mode='conversation',
            used_openai=True,
            fallback=False,
        )

        self.assertLessEqual(len(result.answer), MAX_CHAT_ANSWER_LENGTH)
        self.assertTrue(result.answer.endswith('…'))
        self.assertEqual(result.answer, summarize_chat_answer(long_answer))


class DataEncodingTestCase(unittest.TestCase):
    def test_repairs_utf8_and_euc_kr_mojibake(self):
        utf8_broken = '경복궁'.encode('utf-8').decode('latin1')
        euc_kr_broken = '양화한강공원'.encode('euc-kr').decode('latin1')

        self.assertEqual(repair_mojibake(utf8_broken), '경복궁')
        self.assertEqual(repair_mojibake(euc_kr_broken), '양화한강공원')


if __name__ == '__main__':
    unittest.main()
