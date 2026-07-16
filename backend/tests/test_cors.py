from __future__ import annotations

import asyncio
import unittest

from app.main import app


async def request(method: str, headers: list[tuple[bytes, bytes]]):
    sent = []
    received = False

    async def receive():
        nonlocal received
        if not received:
            received = True
            return {'type': 'http.request', 'body': b'', 'more_body': False}
        return {'type': 'http.disconnect'}

    async def send(message):
        sent.append(message)

    await app(
        {
            'type': 'http',
            'asgi': {'version': '3.0'},
            'http_version': '1.1',
            'method': method,
            'scheme': 'https',
            'path': '/api/health',
            'raw_path': b'/api/health',
            'query_string': b'',
            'headers': headers,
            'client': ('127.0.0.1', 12345),
            'server': ('testserver', 443),
        },
        receive,
        send,
    )
    start = next(message for message in sent if message['type'] == 'http.response.start')
    return start['status'], dict(start['headers'])


class CorsTestCase(unittest.TestCase):
    def test_capacitor_origin_is_allowed_for_health_request(self):
        status, headers = asyncio.run(
            request('GET', [(b'origin', b'https://localhost')])
        )

        self.assertEqual(status, 200)
        self.assertEqual(headers[b'access-control-allow-origin'], b'https://localhost')

    def test_capacitor_origin_preflight_is_allowed(self):
        status, headers = asyncio.run(
            request(
                'OPTIONS',
                [
                    (b'origin', b'https://localhost'),
                    (b'access-control-request-method', b'GET'),
                ],
            )
        )

        self.assertEqual(status, 200)
        self.assertEqual(headers[b'access-control-allow-origin'], b'https://localhost')


if __name__ == '__main__':
    unittest.main()
