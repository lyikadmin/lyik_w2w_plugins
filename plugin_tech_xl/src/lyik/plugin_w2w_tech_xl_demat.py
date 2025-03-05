import logging
import os

import requests
from typing_extensions import Annotated, Doc

import apluggy as pluggy

from lyikpluginmanager import (
    ContextModel,
    getProjectName, GenericFormRecordModel, TeachXLSpec
)

impl = pluggy.HookimplMarker(getProjectName())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TechXLPlugin(TeachXLSpec):
    @impl
    async def create_demat(
            self,
            context: ContextModel,
            form_record: Annotated[
                GenericFormRecordModel,
                Doc("form record to be submitted to TechXL"),
            ],
    ) -> Annotated[str, Doc('response text')]:
        # todo: 1. parse form record to create TechXL object

        # 3. prepare multipart request
        payload = {}
        files = {

        }
        try:
            endpoint = os.getenv("TECH_XL_ENDPOINT")
            response = requests.post(endpoint, data=payload, files=files)
            print(response.status_code)
            print(response.text)
            return response.text

        except Exception as e:
            logger.error(f"Error tech xl submission : {str(e)}")
            return str(e)
