from fastapi import FastAPI
from fastapi_pagination import add_pagination
import uvicorn
from structlog import get_logger

from settings import Settings
from configure_logging import configure_logging
from middlewares.request_logging.middleware import add_log_context
from routes.advances import get_router as get_transactions_router
from dal.dal import Dal

logger = get_logger()


def get_app() -> FastAPI:
    """
    Generates the FastAPI app, loaded with all the required routes

    :return: (FastAPI) app
    """
    settings = Settings()
    app = FastAPI(title=settings.title)

    configure_logging(settings)

    logger.info('Connecting to database')
    dal = Dal()

    # Required for paths that return a paginated list of results
    add_pagination(app)

    app.middleware("http")(add_log_context)

    app.include_router(get_transactions_router(dal=dal))

    @app.on_event("startup")
    def on_startup():
        dal.initiate_connection(settings.db_connection_string.get_secret_value())

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
        port=9000,

        # We set this so that uvicorn does not try to configure logging. we are doing that instead
        log_config=None)
