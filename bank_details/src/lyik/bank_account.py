import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    VerifyHandlerSpec,
    ContextModel,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Doc
import random
import requests

impl = pluggy.HookimplMarker(getProjectName())


class BankVerificationPayload(BaseModel):
    bank_account_number: str = Field(..., description="Bank account number")
    account_holder_name_pan: str | None = Field(
        ..., description="Account holder name as per PAN"
    )
    account_holder_name_id: str | None = Field(
        ..., description="Account holder name as per ID proof"
    )
    ifsc_code: str = Field(..., description="IFSC code")
    account_holder_name: str | None = Field(..., description="Account holder name")
    type_of_application: str = Field(..., description="Type of application")
    model_config = ConfigDict(extra="allow")


class BankAccount(VerifyHandlerSpec):
    """
    Implementation of the VerifyHandlerSpec interface to verify bank account.
    """

    DEFAULT_KEY = "defaults"
    IFSC_API_URL = "https://ifsc.razorpay.com/"

    def validate_ifsc_code(self, ifsc_code: str):
        response = requests.get(f"{self.IFSC_API_URL}{ifsc_code}")
        if response.status_code == 200:
            return response.json()
        return None

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            BankVerificationPayload,
            Doc("Payload containint bank details to be verified"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel, Doc("Success or failure response with message")
    ]:
        """
        This will verify If the bank account exists and validate the IFSC code.
        """

        payload.ifsc_code = payload.ifsc_code.upper()
        ifsc_details = self.validate_ifsc_code(payload.ifsc_code)

        if not ifsc_details:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                id="1",
                message="Invalid IFSC code",
            )

        if payload.type_of_application in [
            "TRADING_KTK",
            "TRADING_AND_DP_KTK",
        ]:
            if ifsc_details.get("BANK") != "Karnataka Bank":
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    id="1",
                    message="IFSC code does not belong to the selected bank",
                )

        payload_dict = payload.model_dump()
        old_ver_status = payload_dict.pop("_ver_status", None)
        # payload_dict.update({"address": f"new_address-{random.randint(0,1000)}"})
        payload_dict.update(
            {
                "account_holder_name_pan": "",
                "account_holder_name_id": "",
                "account_holder_name": "",
            }
        )

        response = VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            actor="system",
            id="1",
            response=payload_dict,
        )

        return response
