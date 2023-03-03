"""General configuration variables"""
from typing import Optional
from pathlib import Path

from starlette.config import Config

cfg = Config(".env")

STATIC_PATH: Path = cfg("STATIC_PATH", cast=Path, default=Path(__file__).parent / "staticfiles")
TEMPLATES_PATH: Path = cfg("TEMPLATES_PATH", cast=Path, default=Path(__file__).parent / "templates")
LOG_LEVEL: int = cfg("LOG_LEVEL", default=20, cast=int)
PIPELINE_URL: str = cfg(
    "PIPELINE_URL", default="https://dev.azure.com/pvarki/PVARKI/_apis/pipelines/8/runs?api-version=7.0"
)
PIPELINE_REF: str = cfg("PIPELINE_REF", default="refs/heads/init_azure_pipeline")
PIPELINE_TOKEN_KEYVAULT: str = cfg("PIPELINE_TOKEN_KEYVAULT", default="pvarki-shared-kv001")
PIPELINE_TOKEN_SECRETNAME: str = cfg("PIPELINE_TOKEN_SECRETNAME", default="base64encodedsecret")
PIPELINE_SSHKEY_SECRETNAME: str = cfg("PIPELINE_SSHKEY_SECRETNAME", default="sshkeypub")
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
PIPELINE_SSHKEY_OVERRIDE: Optional[str] = cfg("PIPELINE_SSHKEY_OVERRIDE", default=None)
PIPELINE_TOKEN_OVERRIDE: Optional[str] = cfg("PIPELINE_TOKEN_OVERRIDE", default=None)
PIPELINE_SUPPRESS: bool = cfg("PIPELINE_SUPPRESS", default=False, cast=bool)
