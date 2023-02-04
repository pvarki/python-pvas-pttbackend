"""General configuration variables"""
from pathlib import Path

from starlette.config import Config

cfg = Config(".env")

STATIC_PATH: Path = cfg("STATIC_PATH", cast=Path, default=Path(__file__).parent / "staticfiles")
TEMPLATES_PATH: Path = cfg("TEMPLATES_PATH", cast=Path, default=Path(__file__).parent / "templates")
LOG_LEVEL: int = cfg("LOG_LEVEL", default=20, cast=int)
SPINUP_PIPELINE_URL: str = cfg("SPINUP_PIPELINE_URL", default="https://up.example.com")
SPINDOWN_PIPELINE_URL: str = cfg("SPINDOWN_PIPELINE_URL", default="https://down.example.com")
PIPELINE_TOKEN_KEYVAULT: str = cfg("PIPELINE_TOKEN_KEYVAULT", default="pvarki-shared-kv001")
PIPELINE_TOKEN_SECRETNAME: str = cfg("PIPELINE_TOKEN_SECRETNAME", default="base64encodedsecret")
INSTRUCTIONS_URL: str = cfg(
    "INSTRUCTIONS_URL", default="https://arkipublic.blob.core.windows.net/ohjeet/Kayttoohje-Mumble.pdf"
)
TAKORTTI_URL: str = cfg(
    "TAKORTTI_URL", default="https://arkipublic.blob.core.windows.net/ohjeet/Taisteluajatuskortti_Mumble.pdf"
)
DOCTEMPLATE_URL: str = cfg(
    "DOCTEMPLATE_URL",
    default="https://arkipublic.blob.core.windows.net/dokumentointi/F02_PVARKI-tuotteen_dokumentointi_MUMBLE.zip",
)
