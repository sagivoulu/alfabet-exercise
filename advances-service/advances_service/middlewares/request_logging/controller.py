from typing import Dict

from structlog.contextvars import get_contextvars, bind_contextvars, clear_contextvars
from fastapi import Request

LOG_REQUEST_HEADERS = ['user-agent']
MAX_HEADER_VALUE_LEN = 150


class ContextVars:

    __original_context_vars: Dict

    def __init__(self, **kwargs):
        self.__original_context_vars = {}
        self.__context_vars = kwargs

    def __enter__(self):
        self.__original_context_vars = get_contextvars()
        bind_contextvars(**self.__context_vars)

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_contextvars()
        bind_contextvars(**self.__original_context_vars)


def extract_request_metadata(request: Request) -> Dict:
    client = request.client.host
    request_url = str(request.url)
    request_uri = request.url.path
    request_method = request.method

    all_headers = dict(request.headers)
    headers = {}
    for key, value in all_headers.items():
        if key.lower() in LOG_REQUEST_HEADERS:
            _value = value
            if not isinstance(_value, str):
                _value = str(_value)

            if len(_value) > MAX_HEADER_VALUE_LEN:
                _value = f'{_value[:MAX_HEADER_VALUE_LEN]}...'
            headers[key.lower()] = _value

    request_metadata = {
        'client': client,
        'url': request_url,
        'uri': request_uri,
        'method': request_method,
        'headers': headers,
    }

    return request_metadata
