"""callbacks for TF etc"""
from typing import Dict, Any
import logging

import pendulum
from fastapi import APIRouter, HTTPException
from starlette import status
from arkia11napi.helpers import get_or_404


from ..models import PTTInstance


LOGGER = logging.getLogger(__name__)
CALLBACKS_ROUTER = APIRouter()


@CALLBACKS_ROUTER.post(
    "/api/v1/ptt/callbacks/{pkstr}", tags=["ptt-instances"], status_code=status.HTTP_204_NO_CONTENT, name="tf_callback"
)
async def terraform_callback(pkstr: str, tfoutputs: Dict[str, Any]) -> None:
    """one-use callback for pipeline to update instance with TF outputs"""
    instance = await get_or_404(PTTInstance, pkstr)
    if instance.tfcompleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="May only be called once per instance")
    LOGGER.debug("called for {}, tfoutputs={}".format(pkstr, tfoutputs))
    await instance.update(tfcompleted=pendulum.now("UTC"), tfoutputs=tfoutputs).apply()
