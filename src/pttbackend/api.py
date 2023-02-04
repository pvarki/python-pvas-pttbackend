"""Main API entrypoint"""
from typing import Mapping
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from libadvian.logging import init_logging
from arkia11napi.middleware import DBWrapper

from .config import TEMPLATES_PATH, STATIC_PATH, LOG_LEVEL
from .views.instances import INSTANCE_ROUTER
from .views.callbacks import CALLBACKS_ROUTER

from . import models


TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_PATH))
LOGGER = logging.getLogger(__name__)

APP = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")
APP.mount("/static", StaticFiles(directory=str(STATIC_PATH)), name="static")
APP.include_router(CALLBACKS_ROUTER)
APP.include_router(INSTANCE_ROUTER)
WRAPPER = DBWrapper(gino=models.db)
WRAPPER.init_app(APP)

init_logging(LOG_LEVEL)


@APP.get("/api/v1", tags=["misc"])
async def hello() -> Mapping[str, str]:
    """Say hello"""
    return {"message": "Hello World"}
