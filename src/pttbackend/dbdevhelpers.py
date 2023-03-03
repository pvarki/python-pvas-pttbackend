"""DB related helpers for development"""
import sqlalchemy

from . import models


async def create_all() -> None:
    """Create all schemas and tables"""
    await models.db.status(sqlalchemy.schema.CreateSchema("pttbackend"))
    await models.db.gino.create_all()


async def drop_all() -> None:
    """Drop all tables and schemas"""
    await models.db.gino.drop_all()
    await models.db.status(sqlalchemy.schema.DropSchema("pttbackend"))
