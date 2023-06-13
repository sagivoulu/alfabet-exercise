from fastapi import FastAPI
import uvicorn
from structlog import get_logger

from settings import Settings
from configure_logging import configure_logging
from middlewares.request_logging.middleware import add_log_context
from routes.transactions import get_router as get_transactions_router

logger = get_logger()


def get_app() -> FastAPI:
    """
    Generates the FastAPI app, loaded with all the required routes

    :return: (FastAPI) app
    """
    settings = Settings()
    app = FastAPI(title=settings.title)

    configure_logging(settings)

    app.middleware("http")(add_log_context)

    app.include_router(get_transactions_router())

    @app.get('/')
    def root() -> str:
        logger.info('Serving the root welcome page')
        return f'Welcome to AlfaBet Exercise: {app.title}'

    return app


app = get_app()
if __name__ == '__main__':
    uvicorn.run(
        app,

        host='0.0.0.0',

        # We set this so that uvicorn does not try to configure logging. we are doing that instead
        log_config=None)
