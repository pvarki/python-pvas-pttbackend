"""PTTInstance related endpoints"""
from typing import List
import logging

import pendulum
from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status
from arkia11napi.helpers import get_or_404
from arkia11napi.security import JWTBearer, check_acl


from ..schemas.instance import DBInstance, InstanceCreate, InstancePager
from ..models import PTTInstance


LOGGER = logging.getLogger(__name__)
INSTANCE_ROUTER = APIRouter(dependencies=[Depends(JWTBearer(auto_error=True))])


@INSTANCE_ROUTER.post(
    "/api/v1/ptt/instances", tags=["ptt-instances"], response_model=DBInstance, status_code=status.HTTP_201_CREATED
)
async def create_instance(request: Request, pdinstance: InstanceCreate) -> DBInstance:
    """Create a new PTTInstance"""
    check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:create")
    pttinstance = PTTInstance(**pdinstance.dict())
    await pttinstance.create()
    refresh = await PTTInstance.get(pttinstance.pk)
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.tfdata:read", auto_error=False):
        refresh.tfinputs = None
        refresh.tfoutputs = None
    # FIXME: Trigger pipeline for terraform apply
    return DBInstance.parse_obj(refresh.to_dict())


@INSTANCE_ROUTER.get("/api/v1/ptt/instances", tags=["ptt-instances"], response_model=InstancePager)
async def list_instances(request: Request) -> InstancePager:
    """List PTTInstance"""
    query = PTTInstance.query.where(
        PTTInstance.deleted == None  # pylint: disable=C0121 ; # "is None" will create invalid query
    )
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:read", auto_error=False):
        query = query.where(PTTInstance.ownerid == request.state.jwt["userid"])

    instances = await query.gino.all()
    if not instances:
        return InstancePager(items=[], count=0)

    pdinstances: List[DBInstance] = []
    for instance in instances:
        instance.tfinputs = None
        instance.tfoutputs = None
        pdinstances.append(DBInstance.parse_obj(instance.to_dict()))

    return InstancePager(
        count=len(pdinstances),
        items=pdinstances,
    )


@INSTANCE_ROUTER.get("/api/v1/ptt/instances/{pkstr}", tags=["ptt-instances"], response_model=DBInstance)
async def get_instance(request: Request, pkstr: str) -> DBInstance:
    """Get a single instance"""
    instance = await get_or_404(PTTInstance, pkstr)
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:read", auto_error=False):
        if instance.ownerid != request.state.jwt["userid"]:
            raise HTTPException(status_code=403, detail="Required privilege not granted.")

    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.tfdata:read", auto_error=False):
        instance.tfinputs = None
        instance.tfoutputs = None
    return DBInstance.parse_obj(instance.to_dict())


@INSTANCE_ROUTER.delete("/api/v1/ptt/instances/{pkstr}", tags=["ptt-instances"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(request: Request, pkstr: str) -> None:
    """Delete a single instance"""
    instance = await get_or_404(PTTInstance, pkstr)
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:read", auto_error=False):
        if instance.ownerid != request.state.jwt["userid"]:
            raise HTTPException(status_code=403, detail="Required privilege not granted.")
    # FIXME: Trigger pipeline for terraform destroy
    await instance.update(deleted=pendulum.now("UTC")).apply()
