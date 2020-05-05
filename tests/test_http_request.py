"""Test for http helper module"""
import time
import requests
from requests import Request
import requests_mock  # type: ignore

from pcg.network.http_request import HTTPRequest, HTTPRequestEvents


def test_http_request():
    """Testing HTTPRequest object interface"""
    with requests_mock.Mocker() as req_mock:
        req_mock.get(
            'http://somedummydomain.com',
            text='Hi!'
        )

        http = HTTPRequest()
        req = Request('GET', 'http://somedummydomain.com',
                      headers={'user-agent': 'dummy'})
        res = http.repeat_request(req)
        assert res is not None
        assert res.status_code == 200
        assert res.text == 'Hi!'
        assert res.request.headers['user-agent'] == 'dummy'


def test_http_fails_with_backoff():
    """Test http request fails"""
    with requests_mock.Mocker() as req_mock:
        req_mock.get(
            'http://somedummydomain.com',
            status_code=404,
        )

        http = HTTPRequest(
            config={'request_backoff_timeout': 0.1,
                    'change_ua_on_retry': True},
            headers={'user-agent': 'dummy'}
        )
        req = Request('GET', 'http://somedummydomain.com')
        current_time = time.time()
        res = http.repeat_request(req)
        execution_time = time.time() - current_time

        assert res.ok is False
        assert res.status_code == 404
        assert res.text == ''
        assert execution_time > 0.1
        assert res.request.headers['user-agent'] != 'dummy'


def test_http_events():
    """Test http request events system"""

    class Events(HTTPRequestEvents):
        sended = 0
        failed = 0
        succeed = 0

        def on_send(self):
            self.sended += 1

        def on_success(self, res):
            self.succeed += 1

        def on_fail(self, req, res):
            self.failed += 1

    http = HTTPRequest(
        config={
            'request_backoff_timeout': 0.1,
            'request_retries': 3,
            'change_ua_on_retry': False
        },
        headers={'user-agent': 'dummy1'},
        events=Events()
    )

    with requests_mock.Mocker() as req_mock:
        req_mock.register_uri(
            'GET', 'http://somedummydomain.com',
            [
                {'text': 'nf', 'status_code': 404},
                {'text': 'Hi!', 'status_code': 200}
            ])

        res = http.repeat_request(
            Request('GET', 'http://somedummydomain.com'))

        assert res.ok is True
        assert http.events.sended == 2
        assert http.events.failed == 1
        assert http.events.succeed == 1


def test_http_events_on_exceptions():

    class Events(HTTPRequestEvents):
        sended = 0
        exception = 0
        succeed = 0

        def on_send(self):
            self.sended += 1

        def on_success(self, res):
            self.succeed += 1

        def on_exception(self, req, exc):
            self.exception += 1

    http = HTTPRequest(
        config={
            'request_backoff_timeout': 0.1,
            'request_retries': 3,
            'change_ua_on_retry': False
        },
        headers={'user-agent': 'dummy1'},
        events=Events()
    )

    with requests_mock.Mocker() as req_mock:
        req_mock.register_uri(
            'GET', 'http://somedummydomain.com',
            exc=requests.exceptions.ConnectTimeout)

        res = http.repeat_request(
            Request('GET', 'http://somedummydomain.com'))

        assert res is None
        assert http.events.sended == http.config['request_retries']
        assert http.events.exception == 3
        assert http.events.succeed == 0


def test_no_user_agent():
    """Test http request events system"""

    http = HTTPRequest(
        config={
            'request_backoff_timeout': 0.1,
            'request_retries': 3,
            'change_ua_on_retry': False
        },
        headers={'user-agent': 'dummy1'},
    )

    with requests_mock.Mocker() as req_mock:
        req_mock.register_uri(
            'GET', 'http://somedummydomain.com',
            [
                {'text': 'nf', 'status_code': 404},
                {'text': 'Hi!', 'status_code': 200}
            ])

        res = http.repeat_request(
            Request('GET', 'http://somedummydomain.com'))

        assert res.ok is True
        assert res.request.headers['user-agent'] == 'dummy1'


def test_user_agent():
    http = HTTPRequest(
        config={
            'request_backoff_timeout': 0.1,
            'request_retries': 3,
            'change_ua_on_retry': False
        },
    )

    with requests_mock.Mocker() as req_mock:
        req_mock.register_uri(
            'GET', 'http://somedummydomain.com',
            [
                {'text': 'nf', 'status_code': 404},
                {'text': 'Hi!', 'status_code': 200}
            ])

        res = http.repeat_request(
            Request('GET', 'http://somedummydomain.com'))

        assert res.ok is True
        assert res.request.headers['user-agent'].startswith('python-requests')


def test_errors():
    http = HTTPRequest(
        config={
            'request_backoff_timeout': 0.1,
            'request_retries': 3,
            'change_ua_on_retry': False
        },
    )

    with requests_mock.Mocker() as req_mock:
        req_mock.register_uri(
            'GET', 'http://somedummydomain.com',
            exc=requests.exceptions.ConnectTimeout)

        res = http.repeat_request(
            Request('GET', 'http://somedummydomain.com'))

        assert res is None
        assert len(http.errors) == 3
        assert http.last_error()['__type'] == 'exception'
        assert http.last_error()['exception'].response is None
