"""Pydantic schemas for deployed instances"""
from typing import Optional, Sequence, Dict, Any
import datetime
import logging

from pydantic import Field

from .base import CreateBase, DBBase
from .pager import PagerBase


# pylint: disable=R0903
LOGGER = logging.getLogger(__name__)


class InstanceCreate(CreateBase):
    """Create PTTInstance objects"""

    ownerid: str = Field(description="Who owns this, usually should point to 'userid' in JWT")
    color: str = Field(description="Color of this deployment, HTML 6-character RGB code #rrggbb, no alpha")
    grouping: Optional[str] = Field(description="Arbitrary string to group deployments by", nullable=True, default=None)
    max_users: int = Field(description="How many max users will the instance be created for", default=500)


class DBInstance(InstanceCreate, DBBase):
    """Display/update PTTInstance objects"""

    tfcompleted: Optional[datetime.datetime] = Field(
        description="When was the TerraForm pipeline completed", nullable=True, default=None
    )
    tfinputs: Optional[Dict[str, Any]] = Field(description="Inputs given to TerraForm, only visible to admins")
    tfoutputs: Optional[Dict[str, Any]] = Field(description="Outpust from TerraForm, only visible to admins")


class InstancePager(PagerBase):
    """List instances (paginated)"""

    items: Sequence[DBInstance] = Field(default_factory=list, description="The instances on this page")
