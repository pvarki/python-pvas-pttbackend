"""Security stuff"""
from typing import Optional, Any
import logging
from dataclasses import dataclass, field


from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from libadvian.binpackers import ensure_utf8
from arkia11napi.security import JWTBearer, JWTPayload, check_acl, JWTHandler as _JWTHandler
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from .config import PIPELINE_TOKEN_KEYVAULT, PIPELINE_TOKEN_SECRETNAME


LOGGER = logging.getLogger(__name__)


class JWTHandler(_JWTHandler):
    """JWT handler that is meant only for decode"""

    def __post_init__(self) -> None:
        """Read the keys"""
        if self.privkeypath and self.privkeypath.exists():
            with self.privkeypath.open("rb") as fpntr:
                passphrase: Optional[bytes] = None
                if self.keypasswd:
                    passphrase = ensure_utf8(str(self.keypasswd))
                self._privkey = serialization.load_pem_private_key(
                    fpntr.read(), password=passphrase, backend=default_backend()
                )
        with self.pubkeypath.open("rb") as fpntr:
            self.pubkey = serialization.load_pem_public_key(fpntr.read(), backend=default_backend())

    @classmethod
    def singleton(cls, **kwargs: Any) -> "JWTHandler":
        """Get a singleton"""
        global HDL_SINGLETON  # pylint: disable=W0603
        if HDL_SINGLETON is None:
            HDL_SINGLETON = JWTHandler(**kwargs)
        assert HDL_SINGLETON is not None
        return HDL_SINGLETON


HDL_SINGLETON: Optional[JWTHandler] = None


@dataclass
class PipelineTokens:
    """Wrap the secret fetch to a singleton pattern"""

    bearer: Optional[str] = field(default=None, repr=False)

    kvuri: str = field(default=f"https://{PIPELINE_TOKEN_KEYVAULT}.vault.azure.net")
    _credentials: DefaultAzureCredential = field(default_factory=DefaultAzureCredential)
    _client: SecretClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Fetch the keys here"""
        self._client = SecretClient(vault_url=self.kvuri, credential=self._credentials)
        secret = self._client.get_secret(PIPELINE_TOKEN_SECRETNAME)
        self.bearer = secret.value

    @classmethod
    def singleton(cls, **kwargs: Any) -> "PipelineTokens":
        """Get a singleton"""
        global KVTOKEN_SINGLETON  # pylint: disable=W0603
        if KVTOKEN_SINGLETON is None:
            KVTOKEN_SINGLETON = PipelineTokens(**kwargs)
        assert KVTOKEN_SINGLETON is not None
        return KVTOKEN_SINGLETON


KVTOKEN_SINGLETON: Optional[PipelineTokens] = None


# re-export some helpers
__all__ = ["JWTHandler", "JWTBearer", "JWTPayload", "check_acl"]
