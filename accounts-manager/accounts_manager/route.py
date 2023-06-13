import logging
import time
from time import sleep

import requests
from fastapi import APIRouter
from fastapi import Response
from structlog import get_logger

from settings import Settings

logger = get_logger()


def get_router(settings: Settings) -> APIRouter:
    """Generated a bunch of example routes on a router, and returns the resulting router"""
    router = APIRouter()

    @router.get('/long')
    def long_request() -> str:
        logger.info(f'This is a long request, it will take {settings.long_request_sleep_seconds} seconds')
        start_time = time.perf_counter()
        while time.perf_counter() < start_time + settings.long_request_sleep_seconds:
            logger.debug('Not done sleeping yet...')
            logging.getLogger(__name__).debug('Not done sleeping yet.. (log from stdlib)')
            sleep(0.5)
        return f'request done after sleeping for {settings.long_request_sleep_seconds} seconds'

    @router.get('/status-code/{status_code}')
    def return_status_code(status_code: int, response: Response) -> str:
        logger.info(f'This request will return the status code: {status_code}')
        response.status_code = status_code

        return f'This request returned the status code: {status_code}'

    @router.get('/bug')
    def bug_in_code():
        logger.info('This code segment will rais an error')
        result = 10 / 0

    @router.get('/http-request')
    def send_http_request():
        url = 'http://example.com'
        method = 'GET'
        logger.info('starting outbound http request', method=method, url=url)
        response = requests.request(method=method, url=url)
        logger.info('completed outbound http request', response={
            "status_code": response.status_code,
            "body": response.content
        })

    return router
