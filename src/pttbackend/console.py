"""CLI entrypoints for pttbackend"""
from typing import Any
import logging
import asyncio

import click

from libadvian.logging import init_logging

from pttbackend import __version__, dbconfig, models
from pttbackend.dbdevhelpers import create_all, drop_all


LOGGER = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("-l", "--loglevel", help="Python log level, 10=DEBUG, 20=INFO, 30=WARNING, 40=CRITICAL", default=30)
@click.option("-v", "--verbose", count=True, help="Shorthand for info/debug loglevel (-v/-vv)")
@click.pass_context
def cligroup(ctx: Any, loglevel: int, verbose: int) -> None:
    """models cli for quick and dirty devel ops, use alembic for actual migrations"""
    if verbose == 1:
        loglevel = 20
    if verbose >= 2:
        loglevel = 10
    logging.getLogger("").setLevel(loglevel)
    LOGGER.setLevel(loglevel)
    ctx.ensure_object(dict)


@cligroup.command()
def create_tables() -> None:
    """Create tables"""

    async def runner() -> None:
        await models.db.set_bind(dbconfig.DSN)
        await create_all()

    asyncio.get_event_loop().run_until_complete(runner())


@cligroup.command()
def drop_tables() -> None:
    """Remove all tables"""

    async def runner() -> None:
        await models.db.set_bind(dbconfig.DSN)
        await drop_all()

    asyncio.get_event_loop().run_until_complete(runner())


def pttbackend_cli() -> None:
    """models cli for quick and dirty devel ops, use alembic for actual migrations"""
    init_logging(logging.WARNING)
    LOGGER.setLevel(logging.WARNING)
    cligroup()  # pylint: disable=E1120
