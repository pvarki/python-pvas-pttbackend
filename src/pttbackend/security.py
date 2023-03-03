"""Security stuff"""
from typing import Optional, Any
import logging
from dataclasses import dataclass, field


from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


from .config import (
    PIPELINE_TOKEN_KEYVAULT,
    PIPELINE_TOKEN_SECRETNAME,
    PIPELINE_SSHKEY_SECRETNAME,
    PIPELINE_SSHKEY_OVERRIDE,
    PIPELINE_TOKEN_OVERRIDE,
)


LOGGER = logging.getLogger(__name__)


@dataclass
class PipelineTokens:
    """Wrap the secret fetch to a singleton pattern"""

    bearer: Optional[str] = field(default=None, repr=False)
    ssh_pub: Optional[str] = field(default=None, repr=False)

    kvuri: str = field(default=f"https://{PIPELINE_TOKEN_KEYVAULT}.vault.azure.net")
    _credentials: DefaultAzureCredential = field(init=False, repr=False)
    _client: SecretClient = field(init=False, repr=False)

    @property
    def client(self) -> SecretClient:
        """Init the client or return"""
        try:
            return self._client
        except AttributeError:
            pass
        self._credentials = DefaultAzureCredential()
        self._client = SecretClient(vault_url=self.kvuri, credential=self._credentials)
        return self._client

    def __post_init__(self) -> None:
        """Fetch the keys here"""
        if PIPELINE_TOKEN_OVERRIDE:
            self.bearer = PIPELINE_TOKEN_OVERRIDE
        else:
            secret = self.client.get_secret(PIPELINE_TOKEN_SECRETNAME)
            self.bearer = secret.value
        if PIPELINE_SSHKEY_OVERRIDE:
            self.ssh_pub = PIPELINE_SSHKEY_OVERRIDE
        else:
            secret = self.client.get_secret(PIPELINE_SSHKEY_SECRETNAME)
            self.ssh_pub = secret.value

    @classmethod
    def singleton(cls, **kwargs: Any) -> "PipelineTokens":
        """Get a singleton"""
        global KVTOKEN_SINGLETON  # pylint: disable=W0603
        if KVTOKEN_SINGLETON is None:
            KVTOKEN_SINGLETON = PipelineTokens(**kwargs)
        assert KVTOKEN_SINGLETON is not None
        return KVTOKEN_SINGLETON


KVTOKEN_SINGLETON: Optional[PipelineTokens] = None
