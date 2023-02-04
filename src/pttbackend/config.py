"""General configuration variables"""
from pathlib import Path

from starlette.config import Config

cfg = Config(".env")

STATIC_PATH: Path = cfg("STATIC_PATH", cast=Path, default=Path(__file__).parent / "staticfiles")
TEMPLATES_PATH: Path = cfg("TEMPLATES_PATH", cast=Path, default=Path(__file__).parent / "templates")
LOG_LEVEL: int = cfg("LOG_LEVEL", default=20, cast=int)
SPINUP_PIPELINE_URL: str = cfg("SPINUP_PIPELINE_URL", default="https://")
SPINDOWN_PIPELINE_URL: str = cfg("SPINDOWN_PIPELINE_URL", default="https://")
PIPELINE_TOKEN_KEYVAULT: str = cfg("PIPELINE_TOKEN_KEYVAULT", default="pvarki-shared-kv001")
PIPELINE_TOKEN_SECRETNAME: str = cfg("PIPELINE_TOKEN_SECRETNAME", default="changeme")
