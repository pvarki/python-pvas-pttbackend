"""PTTInstance related endpoints"""
from typing import List
import logging
import uuid

import pendulum
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from arkia11napi.helpers import get_or_404
from arkia11napi.security import JWTBearer, check_acl


from ..config import TEMPLATES_PATH
from ..schemas.instance import DBInstance, InstanceCreate, InstancePager
from ..models import PTTInstance
from ..pipelineclient import PipeLineClient
from .. import config


LOGGER = logging.getLogger(__name__)
TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_PATH))
INSTANCE_ROUTER = APIRouter(dependencies=[Depends(JWTBearer(auto_error=True))])


@INSTANCE_ROUTER.post(
    "/api/v1/ptt/instances", tags=["ptt-instances"], response_model=DBInstance, status_code=status.HTTP_201_CREATED
)
async def create_instance(request: Request, pdinstance: InstanceCreate) -> DBInstance:
    """Create a new PTTInstance"""
    check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:create")
    data = pdinstance.dict()
    max_users = data.pop("max_users")
    pttinstance = PTTInstance(**data)
    pttinstance.tfinputs = {
        "mumble_users": max_users,
    }
    if not pttinstance.pk:
        pttinstance.pk = uuid.uuid4()  # type: ignore
    callback_url = request.url_for("tf_callback", pkstr=str(pttinstance.pk))
    await pttinstance.create()
    refresh = await PTTInstance.get(pttinstance.pk)
    client = PipeLineClient()
    try:
        await client.create(pttinstance, callback_url)
    except Exception as exc:
        LOGGER.exception("Could not trigger pipeline {}".format(exc))
        # Do not leave stuff laying around
        await refresh.delete()
        raise
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.tfdata:read", auto_error=False):
        refresh.tfinputs = None
        refresh.tfoutputs = None
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
    ret = DBInstance.parse_obj(instance.to_dict())
    ret.max_users = instance.tfinputs.get("mumble_users", None)
    return ret


@INSTANCE_ROUTER.delete("/api/v1/ptt/instances/{pkstr}", tags=["ptt-instances"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(request: Request, pkstr: str) -> None:
    """Delete a single instance"""
    instance = await get_or_404(PTTInstance, pkstr)
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:read", auto_error=False):
        if instance.ownerid != request.state.jwt["userid"]:
            raise HTTPException(status_code=403, detail="Required privilege not granted.")
    client = PipeLineClient()
    try:
        await client.delete(instance)
    except Exception as exc:
        LOGGER.exception("Could not trigger pipeline {}".format(exc))
        raise
    await instance.update(deleted=pendulum.now("UTC")).apply()


@INSTANCE_ROUTER.get("/api/v1/ptt/instances/{pkstr}/instructions", tags=["ptt-instances"], response_class=HTMLResponse)
async def get_instructions(request: Request, pkstr: str) -> Response:
    """Show instructions HTML with server address etc"""
    instance = await get_or_404(PTTInstance, pkstr)
    if not check_acl(request.state.jwt, "fi.pvarki.pttbackend.instance:read", auto_error=False):
        if instance.ownerid != request.state.jwt["userid"]:
            raise HTTPException(status_code=403, detail="Required privilege not granted.")
    return TEMPLATES.TemplateResponse(
        "instructions.html",
        {
            "request": request,
            "instructions_pdf": config.INSTRUCTIONS_URL,
            "taisteluajatus_pdf": config.TAKORTTI_URL,
            "templates_zip": config.DOCTEMPLATE_URL,
            "dns_name": instance.tfoutputs["dns_name"],
            "mumble_server_password": instance.tfoutputs["mumble_server_password"],
            "mumble_superuser_password": instance.tfoutputs["mumble_superuser_password"],
        },
    )
