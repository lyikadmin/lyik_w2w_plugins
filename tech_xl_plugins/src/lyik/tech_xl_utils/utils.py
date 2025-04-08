import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    invoke,
    GenericFormRecordModel,
    TransformerResponseModel,
    TRANSFORMER_RESPONSE_STATUS,
    PluginException,
)
import logging
import requests
import json
from typing import Dict
import os

logging.basicConfig(level=logging.INFO)

TECHXL_TRANFORMER = "techxl.j2"

logger = logging.getLogger(__name__)
class TechXLUtils:
    @staticmethod
    async def getTechxlTransformedData(
        context: ContextModel, form_record: GenericFormRecordModel
    ):
        # Invoke transformer to get data
        res: TransformerResponseModel = await invoke.transform_data(
            config=context.config,
            record=form_record,
            form_id=context.form_id,
            org_id=context.org_id,
            form_name=context.form_name,
            transformer=TECHXL_TRANFORMER,
        )

        # Check if transformer response status indicates failure
        if res.status == TRANSFORMER_RESPONSE_STATUS.FAILURE:
            raise PluginException(
                f"Couldn't get transformed data for Techxl: {TECHXL_TRANFORMER}"
            )
        return res.response

    @staticmethod
    def upload_to_techxl(data: Dict) -> Dict:
        """
        Uploads JSON data to the TechXL API using a multipart request.

        :param data: The JSON data to be uploaded
        :return: The JSON response from the API on success.
        :raises PluginException: If there is a failure (missing env variable, request error, etc.).
        """
        techxl_endpoint = os.getenv("TECH_XL_ENDPOINT")
        if not techxl_endpoint:
            raise PluginException("TechXL API environment variable is not set")

        # Convert data to JSON string and prepare multipart form data
        files = {key: (None, value) for key, value in data.items()}

        try:
            response = requests.post(techxl_endpoint, files=files)
            response.raise_for_status()
            response_txt = response.text
            logger.info(f"TechXL API response is {response_txt}")
            return response_txt
        except requests.RequestException as e:
            raise PluginException(f"TechXL API request failed: {str(e)}")
