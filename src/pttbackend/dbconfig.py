"""Read database configuration from ENV or .env -file"""
from typing import Optional
import logging

from sqlalchemy.engine.url import URL, make_url
from starlette.config import Config
from starlette.datastructures import Secret

LOGGER = logging.getLogger(__name__)


config = Config(".env")

DRIVER = config("DB_DRIVER", default="postgresql")
HOST: Optional[str] = config("DB_HOST", default=None)
PORT = config("DB_PORT", cast=int, default=None)
USER: Optional[str] = config("DB_USER", default=None)
PASSWORD = config("DB_PASSWORD", cast=Secret, default=None)
DATABASE: Optional[str] = config("DB_DATABASE", default=None)
DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername=DRIVER,
        username=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DATABASE,
    ),
)
POOL_MIN_SIZE = config("DB_POOL_MIN_SIZE", cast=int, default=1)
POOL_MAX_SIZE = config("DB_POOL_MAX_SIZE", cast=int, default=16)
ECHO = config("DB_ECHO", cast=bool, default=False)
SSL = config("DB_SSL", cast=str, default="prefer")  # see asyncpg.connect()
USE_CONNECTION_FOR_REQUEST = config("DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True)
RETRY_LIMIT = config("DB_RETRY_LIMIT", cast=int, default=1)
RETRY_INTERVAL = config("DB_RETRY_INTERVAL", cast=int, default=1)

LOGGER.debug("DSN={}".format(DSN))
LOGGER.debug("HOST={}".format(HOST))
LOGGER.debug("DATABASE={}".format(DATABASE))
