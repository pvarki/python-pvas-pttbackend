"""Pager schemas"""
from typing import Optional, Sequence
import uuid

from libadvian.binpackers import uuid_to_b64, ensure_str
from pydantic.main import BaseModel  # pylint: disable=E0611 # false positive
from pydantic import Field

# pylint: disable=R0903

# FIXME: this should probably we in some common library of Ours
class PagerBase(BaseModel):
    """Base schema for pagers"""

    count: int = Field(description="Total number of matched items")
    items: Sequence[BaseModel] = Field(default_factory=list, description="The items")
    prev: Optional[str] = Field(default=None, is_nullable=True, description="URL of previous page")
    next: Optional[str] = Field(default=None, is_nullable=True, description="URL of next page")

    class Config:
        """Pydantic configs"""

        extra = "forbid"
        json_encoders = {uuid.UUID: lambda val: ensure_str(uuid_to_b64(val))}
