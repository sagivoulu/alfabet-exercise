from sqlalchemy import create_engine, Engine
import structlog

logger = structlog.get_logger()


def get_sqlalchemy_engine(connection_string: str) -> Engine:
    logger.debug('Creating database engine')
    engine = create_engine(connection_string, echo=True)
    logger.debug('Database engine created', engine=engine)

    return engine
