"""pytest automagics"""
from typing import Any, Generator
import asyncio
import logging
from pathlib import Path

import pytest

import sqlalchemy
from asyncpg.exceptions import DuplicateSchemaError
from libadvian.logging import init_logging
from arkia11nmodels.testhelpers import monkeysession  # pylint: disable=W0611 ; # false positive
import arkia11napi.security

from pttbackend.api import WRAPPER
from pttbackend import models
from pttbackend import config

# pylint: disable=W0621
init_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
DATA_PATH = Path(__file__).parent / Path("data")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """return event loop, made session scoped fixture to allow db connections to persists between tests"""
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="session")
def dockerdb(docker_ip: str, docker_services: Any, monkeysession: Any) -> Generator[str, None, None]:
    """start docker container for db"""
    LOGGER.debug("Monkeypatching env")
    _ = docker_services
    from pttbackend import dbconfig  # pylint: disable=C0415

    mp_values = {
        "HOST": docker_ip,
        "PORT": docker_services.port_for("db", 5432),
        "PASSWORD": "apitestpwd",  # pragma: allowlist secret
        "USER": "postgres",
        "DATABASE": "a11napitest",
        "RETRY_LIMIT": "10",
        "RETRY_INTERVAL": "3",
    }
    LOGGER.debug("mp_values={}".format(mp_values))
    for key, value in mp_values.items():
        monkeysession.setenv(f"DB_{key}", str(value))
        monkeysession.setattr(dbconfig, key, value)

    new_dsn = sqlalchemy.engine.url.URL(
        drivername=dbconfig.DRIVER,
        username=dbconfig.USER,
        password=dbconfig.PASSWORD,
        host=dbconfig.HOST,
        port=dbconfig.PORT,
        database=dbconfig.DATABASE,
    )
    monkeysession.setattr(dbconfig, "DSN", new_dsn)

    # Wrapper got already initialized and does not inherit the new values
    monkeysession.setattr(WRAPPER, "dsn", new_dsn)
    monkeysession.setattr(WRAPPER, "retry_limit", int(mp_values["RETRY_LIMIT"]))
    monkeysession.setattr(WRAPPER, "retry_interval", int(mp_values["RETRY_INTERVAL"]))

    LOGGER.debug("yielding {}".format(str(dbconfig.DSN)))
    yield str(dbconfig.DSN)


# FIXME: move the dockerdb and bind_and_create_all helpers to arkia11nmodels testhelpers
#       (and do a bit of refactoring with the old stuff there too)
async def bind_and_create_all() -> None:
    """Create all schemas and tables"""
    try:
        LOGGER.debug("Acquiring connection")
        async with WRAPPER.gino.acquire() as conn:
            LOGGER.debug("Acquiring transaction")
            async with conn.transaction():
                LOGGER.debug("Creating a11n schema")
                await models.db.status(sqlalchemy.schema.CreateSchema("a11n"))
                LOGGER.debug("Creating tables")
                await models.db.gino.create_all()
    except DuplicateSchemaError:
        pass


@pytest.fixture(scope="session", autouse=True)
def jwt_issuer(monkeysession: Any) -> Generator[arkia11napi.security.JWTHandler, None, None]:
    """Monkeypatch env with correct JWT keys and re-init the singleton"""
    monkeysession.setenv("JWT_PRIVKEY_PATH", str(DATA_PATH / "jwtRS256.key"))
    monkeysession.setenv("JWT_PUBKEY_PATH", str(DATA_PATH / "jwtRS256.pub"))
    monkeysession.setenv("JWT_PRIVKEY_PASS", "Disparate-Letdown-Pectin-Natural")  # pragma: allowlist secret
    monkeysession.setenv("JWT_COOKIE_SECURE", "0")
    monkeysession.setenv("JWT_COOKIE_DOMAIN", "")
    monkeysession.setenv("PIPELINE_SUPPRESS", "1")
    monkeysession.setattr(config, "PIPELINE_SUPPRESS", True)
    monkeysession.setattr(arkia11napi.security, "HDL_SINGLETON", arkia11napi.security.JWTHandler())
    singleton = arkia11napi.security.JWTHandler.singleton()
    yield singleton
