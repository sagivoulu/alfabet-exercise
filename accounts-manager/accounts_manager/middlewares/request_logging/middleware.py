import time
import uuid
import traceback

from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from structlog import get_logger

from .controller import ContextVars, extract_request_metadata

logger = get_logger()


async def add_log_context(request: Request, call_next: RequestResponseEndpoint):
    request_id = str(uuid.uuid4())

    tracing_params = {
        'request_id': request_id
    }

    request_metadata = {
        **extract_request_metadata(request=request),
        **tracing_params
    }

    logger.info('Starting http request', **request_metadata)

    start_time = end_time = response = e = None
    try:
        # Bind the request logging param, so they appear in every log message of the request.
        with ContextVars(**tracing_params):
            start_time = time.perf_counter()
            response = await call_next(request)
            end_time = time.perf_counter()
    except Exception as _e:
        e = _e
        raise
    finally:
        end_time = end_time if end_time else time.perf_counter()
        duration = end_time - start_time
        response_status_code = response.status_code if response else None

        request_metadata['request_duration'] = duration

        if response_status_code:
            request_metadata['response_status_code'] = response_status_code

        if e:
            request_metadata = {
                **request_metadata,
                'exception_msg': str(e),
                'exception_type': type(e),
                'exception': ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
            }

        logger.info('HTTP request complete', **request_metadata)

    response.headers['X-Request-ID'] = request_id

    return response
