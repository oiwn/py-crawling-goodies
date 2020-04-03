import time
import logging

import requests
from celery import Task  # types: ignore
from datadog import statsd
from user_agent import generate_user_agent

from grabscrapers.settings import conf


logger = logging.getLogger(__name__)


class HTTPTask(Task):
    """Template for celery task provides shortcuts for common functions to
    work with HTTP requests

    NOTE: about `repeat_request` out of the box solution
    >> session.mount('https://', HTTPAdapter(max_retries=...))
    only covers failed DNS lookups, socket connections and connection timeouts
    It doesnt work when server terminate connection while response is downloaded
    """

    def repeat_request(self):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError
