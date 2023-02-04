"""schema baseclasses"""
from typing import Optional
import uuid
import datetime
import logging

from libadvian.binpackers import uuid_to_b64, ensure_str
from pydantic import Field
from pydantic.main import BaseModel  # pylint: disable=E0611 # false positive

# pylint: disable=R0903
LOGGER = logging.getLogger(__name__)


class SchemaBase(BaseModel):
    """Common encoders and validators"""

    class Config:
        """Pydantic configs"""

        extra = "forbid"
        json_encoders = {uuid.UUID: lambda val: ensure_str(uuid_to_b64(val))}


class CreateBase(SchemaBase):
    """Creation baseclass"""


class DBBase(SchemaBase):
    """Base for object that came from database"""

    pk: uuid.UUID = Field(description="Primary-key, UUID")
    created: datetime.datetime = Field(description="Timestamp of creation")
    updated: datetime.datetime = Field(description="Timestamp of last update")
    deleted: Optional[datetime.datetime] = Field(
        default=None, nullable=True, description="None, or timestamp when marked deleted"
    )
