import apluggy as pluggy
from typing import Dict, Any
from lyikpluginmanager import (
    getProjectName,
    VerifyHandlerSpec,
    ContextModel,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    SingleFieldModel,
)
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Doc
import random

from datetime import datetime

impl = pluggy.HookimplMarker(getProjectName())


class BankVerificationPaylod(BaseModel):
    bank_account_number: str = Field(..., description="Bank account number")
    account_holder_name: str = Field(..., description="Account holder name")
    branch_code: str = Field(..., description="Branch code")
    ifsc_code: str = Field(..., description="IFSC code")
    model_config = ConfigDict(extra="allow")


class BankAccount(VerifyHandlerSpec):
    """
    Implementation of the VerifyHandlerSpec interface to verify bank account.
    """

    DEFAULT_KEY = "defaults"

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            BankVerificationPaylod,
            Doc("Payload containint bank details to be verified"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel, Doc("success or failure response with message")
    ]:
        """
        This will verify If the bank account exists.
        """

        ifsc_code = payload.ifsc_code
        payload.ifsc_code = ifsc_code.upper()
        payload_dict = payload.model_dump()
        old_ver_status = payload_dict.pop("_ver_status")
        payload_dict.update({"address": f"new_address-{random.randint(0,1000)}"})

        response = VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            actor="system",
            id=1,
            response=payload_dict,
        )

        return response
