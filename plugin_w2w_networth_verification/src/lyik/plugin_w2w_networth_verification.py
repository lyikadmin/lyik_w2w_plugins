import apluggy as pluggy
from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing_extensions import Annotated, Doc

impl = pluggy.HookimplMarker(getProjectName())


class IncomeInformationPayload(BaseModel):
    gross_annual_income: Optional[str] = None
    networth: Optional[str] = None
    occupation: Optional[str] = None
    date: Optional[str] = None


class NetworthVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            IncomeInformationPayload,
            Doc("Data related to income information"),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("Success or failure status.")]:
        """
        This plugin is to verify the networth of the user.
        """

        networth = payload.networth

        # Check if networth is missing, empty, or zero
        if not networth or not networth.strip().isdigit():
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Net worth must be a valid value and cannot be empty or zero.",
                actor="system",
            )

        networth_value = int(networth.strip())

        # Ensure networth is at least 100000
        if networth_value < 100000:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Net worth must be at least 100000.",
                actor="system",
            )
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message=f"Verified successfully by the system on {datetime.now()}",
            actor="system",
        )
