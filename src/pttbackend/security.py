"""Security stuff"""
from typing import Optional, Any
import logging

from libadvian.binpackers import ensure_utf8
from arkia11napi.security import JWTBearer, JWTPayload, check_acl, JWTHandler as _JWTHandler
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

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

# re-export some helpers
__all__ = ["JWTHandler", "JWTBearer", "JWTPayload", "check_acl"]
