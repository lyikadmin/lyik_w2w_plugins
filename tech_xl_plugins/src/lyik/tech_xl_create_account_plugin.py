import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    OperationPluginSpec,
    GenericFormRecordModel,
    OperationResponseModel,
    OperationStatus,
    PluginException,
)
from typing import Dict
from typing_extensions import Doc, Annotated
from lyikpluginmanager.annotation import RequiredEnv
import logging
from .tech_xl_utils.utils import TechXLUtils

logging.basicConfig(level=logging.debug)
logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class TechXLCreateAccount(OperationPluginSpec):

    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc("record id of the form record")],
        status: Annotated[str, Doc("status of the form record")],
        form_record: Annotated[GenericFormRecordModel, Doc("form record")],
    ) -> Annotated[
        OperationResponseModel,
        RequiredEnv(["TECH_XL_ENDPOINT"]),
        Doc("TechXL create account upload data"),
    ]:
        """
        Uploads the data to TechXL to create account.
        """
        try:
            # Get transformed data
            data: Dict = await TechXLUtils.getTechxlTransformedData(
                context=context, form_record=form_record
            )
            if not data:
                raise PluginException("Unable to get TechXL transformed data")

            # Upload data
            response_data = TechXLUtils.upload_to_techxl(data)

            return OperationResponseModel(
                status=OperationStatus.SUCCESS,
                message=f"Account created successfully: {response_data}",
            )

        except PluginException as e:
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message=str(e),
            )
