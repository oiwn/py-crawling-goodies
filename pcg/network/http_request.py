"""Requests lib wrapper to provide general error handling and
request repeating pattern. I use it inside celery tasks."""
import time
import logging
from typing import Optional, List, Dict

import requests
from user_agent import generate_user_agent  # type: ignore


logger = logging.getLogger(__name__)
DEFAULT_CONFIG = {
    "request_timeout": 10,
    "request_backoff_timeout": 1,
    "request_retries": 3,
    "request_sleep_on_error_time": 1,
    "change_proxy_on_retry": True,
    "change_ua_on_retry": True,
}


class HTTPRequestEvents:
    """Implement events handling for requests

    >> on_send()  # just before send request
    >> on_success()  # if request succeed
    >> on_fail()  # if request fail
    """

    def on_send(self):
        """Just before send each request"""

    def on_success(self, res):
        """On request success"""

    def on_fail(self, req, res):
        """On request fail (on server side)"""

    def on_exception(self, req, exc):
        """On request exception"""


class HTTPRequest:
    """Wrapper around requests library provides shortcuts
    for common functions to work with HTTP requests
    """

    def __init__(self, config=None, headers=None, events=None):
        # create session according to config
        self.session = requests.Session()

        # load conf
        self.config = DEFAULT_CONFIG
        if config is not None:
            self.config.update(config)

        if headers is not None:
            self.session.headers.update(headers)

        if events is not None:
            self.events = events
        else:
            self.events = HTTPRequestEvents()

        self.errors = []

    def last_error(self):
        """Retrun last error"""
        return self.errors[-1] if len(self.errors) > 0 else None

    def backoff_timeout(self, timeout):
        """Return new timeout with added backoff time.
        """
        new_timeout = timeout + self.config['request_backoff_timeout']
        return new_timeout

    def repeat_request(self, req: requests.Request, proxies=None):
        """Repeat request according to request config.

        NOTE: out of the box solution
        >> session.mount('https://', HTTPAdapter(max_retries=...))
        only covers failed DNS lookups, socket connections and
        connection timeouts.
        It doesnt work when server terminate connection while
        response is downloaded.
        """

        backoff_timer = 0  # increase sleep time after each fail
        self.errors = []  # drop errors from previous call

        prepped = self.session.prepare_request(req)

        res = None
        for idx, _ in enumerate(range(self.config['request_retries'])):
            if idx > 0:  # if not first request
                # change user agent
                if self.config['change_ua_on_retry']:
                    prepped.headers['user-agent'] = generate_user_agent()

            self.events.on_send()
            try:
                res = self.session.send(prepped, proxies=proxies)
            except requests.exceptions.RequestException as exc:
                self.errors.append({'__type': 'exception',
                                    'exception': exc,
                                    'request': req,
                                    'response': res})
                self.events.on_exception(req, exc)
                continue
            else:
                if not res.ok:
                    self.errors.append({'__type': 'http',
                                        'exception': None,
                                        'response': res,
                                        'request': None})
                    self.events.on_fail(req, res)

                    backoff_timer = self.backoff_timeout(backoff_timer)
                    time.sleep(backoff_timer)
                    continue
                else:
                    self.events.on_success(res)
                    return res

        return res
