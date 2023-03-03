"""Client for calling the pipelines"""
from typing import Dict, Any, cast
from dataclasses import dataclass
import logging

import aiohttp

from .models import PTTInstance
from .security import PipelineTokens
from .config import PIPELINE_REF, PIPELINE_URL, PIPELINE_SUPPRESS

LOGGER = logging.getLogger(__name__)


@dataclass
class PipeLineClient:
    """Wrap the pipeline calls to something nicer"""

    @property
    def default_headers(self) -> Dict[str, Any]:
        """Default headers"""
        headers = {"Authorization": f"Basic {PipelineTokens.singleton().bearer}"}
        return headers

    async def create(self, for_instance: PTTInstance, callback_url: str) -> None:
        """Call pipeline to spin up a new service"""
        post_data: Dict[str, Any] = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": PIPELINE_REF,
                    },
                },
            },
            "templateParameters": {
                "SSH_PUBLIC_KEY": PipelineTokens.singleton().ssh_pub,
                "WORKSPACE_NAME": str(for_instance.pk),
                "CREATE": True,
                "CALLBACK_URL": callback_url,
            },
        }
        # Keys must be given as uppercase (ENV variables)
        for_instance.tfinputs = cast(Dict[str, Any], for_instance.tfinputs)
        for param in for_instance.tfinputs.keys():
            post_data["templateParameters"][param.upper()] = for_instance.tfinputs[param]
        await self.do_post(post_data)

    async def do_post(self, post_data: Dict[str, Any]) -> None:
        """Do the POST"""
        if PIPELINE_SUPPRESS:
            LOGGER.warning("Pipeline runs supressed by config")
            return
        async with aiohttp.ClientSession(headers=self.default_headers) as session:
            LOGGER.debug("session.headers {}".format(session.headers))
            LOGGER.debug("POSTing {}".format(post_data))
            LOGGER.debug("to {}".format(PIPELINE_URL))
            async with session.post(PIPELINE_URL, json=post_data) as resp:
                if resp.status != 200:
                    LOGGER.error("Failure response {}".format(resp))
                    if resp.status == 400:
                        json_body = await resp.json()
                        LOGGER.info("Got response {}".format(json_body))
                    raise RuntimeError("Pipeline returned failure")
                json_body = await resp.json()
                LOGGER.debug("Got response {}".format(json_body))

    async def delete(self, from_instance: PTTInstance) -> None:
        """Call pipeline to spin down existing service"""
        post_data = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": PIPELINE_REF,
                    },
                },
            },
            "templateParameters": {
                "SSH_PUBLIC_KEY": PipelineTokens.singleton().ssh_pub,
                "WORKSPACE_NAME": str(from_instance.pk),
                "CREATE": False,
            },
        }
        await self.do_post(post_data)
