import apluggy as pluggy
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
import asyncio
from typing_extensions import Annotated, Doc
from lyikpluginmanager.annotation import InputModel, OutputModel, RequiredVars

impl = pluggy.HookimplMarker(getProjectName())


class NomineePayloadModel(BaseModel):
    general: Dict = Field(
        ...,
        description="A dictionary having a value for key <client_nominee_appointment_status> ",
    )
    nominees: List[Dict[str, Any]] = Field(
        ...,
        description="List of nominees",
    )
    model_config = ConfigDict(extra="allow")



class NomineeAllocationVerification(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            NomineePayloadModel,
            Doc("data related to nominees and their percentage of allocations"),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status.")]:
        """
        Given the nomination details, it verifies the sum of percentage of allocation for the nominees, whoch has to be 100%.
        """
        try:
            # Check if nomination is selected
            if (
                payload.general.get("client_nominee_appointment_status", "").lower()
                == "no"
            ):
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.SUCCESS,
                    message=f"Verified successfully by the system on {datetime.now()}",
                    actor="system",
                )

            # Extract the nominee_data list
            nominee_data = payload.nominees

            # Validate the total percentage_of_allocation
            try:
                total_allocation = sum(
                    nominee["nominee"]["nominee_data"].get(
                        "percentage_of_allocation", 0
                    )
                    for nominee in nominee_data
                )
            except Exception as ex:
                raise Exception("Invalid entry for 'Percentage of Allocation'(s)")

            if total_allocation != 100:
                raise Exception(
                    f"Total percentage of allocation is {total_allocation}, which does not equal to 100."
                )

            # If successful, return a success response
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                message=f"Verified successfully by the system on {datetime.now()}",
                actor="system",
            )
        except Exception as e:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=f"{e}",
                actor="system",
            )
