import apluggy as pluggy
from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(extra="allow")


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

        networth, date = payload.networth, payload.date

        # Ensure both fields are provided together or neither
        if bool(networth) ^ bool(date):
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Networth and Date must be provided together.",
                actor="system",
            )

        # Check if networth and date is provided or not
        if not networth or not date:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message="Validation failed. Networth and date are not provided",
                actor="system",
            )

        networth_value = networth.strip()

        # Ensure networth is at least 100000
        if not networth_value.isdigit() or int(networth_value) < 100000:
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
