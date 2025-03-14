import apluggy as pluggy
import requests
from lyikpluginmanager import (
    getProjectName,
    VerifyHandlerSpec,
    ContextModel,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    invoke,
)
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Doc

impl = pluggy.HookimplMarker(getProjectName())
from thefuzz import fuzz

NAME_MATCHING_THRESHOLD = 80


class BankVerificationPayload(BaseModel):
    bank_account_number: str = Field(..., description="Bank account number")
    account_holder_name_pan: str | None = Field(
        None, description="Account holder name as per PAN"
    )
    account_holder_name_id: str | None = Field(
        None, description="Account holder name as per ID proof"
    )
    ifsc_code: str = Field(..., description="IFSC code")
    account_holder_name: str = Field(..., description="Account holder name")
    mobile_number: str = Field(..., description="Mobile number")
    type_of_application: str = Field(..., description="Type of application")
    micr_code: str | None = Field(None, description="MICR code")
    bank_address: str | None = Field(None, description="Bank address")
    bank_name: str | None = Field(None, description="Bank name")
    type_of_account: str | None = Field(None, description="Bank a/c type")

    model_config = ConfigDict(extra="allow")


def shallow_match_name(customer_name, account_holder_name) -> bool:
    similarity = fuzz.token_set_ratio(account_holder_name, customer_name)
    return similarity > NAME_MATCHING_THRESHOLD


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

        # remove +91 from mobile number
        mobile_number = payload.mobile_number.replace("+91", "")

        try:
            response = await invoke.verify_bank(
                context=context,
                ifsc_code=payload.ifsc_code,
                account_number=payload.bank_account_number,
                name=payload.account_holder_name,
                mobile_number=mobile_number,
            )

            success = response.status == VERIFY_RESPONSE_STATUS.SUCCESS

            if not success:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    id="1",
                    message=f"Failed to verify bank account",
                )

            name_matched = shallow_match_name(
                response.customer_name, payload.account_holder_name
            )

            if not name_matched:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    id="1",
                    message=f"Account holder name mismatch",
                )

            # update payload
            payload.account_holder_name = response.customer_name
            payload.bank_name = ifsc_details.get("BANK")
            payload.micr_code = ifsc_details.get("MICR")
            payload.bank_address = ifsc_details.get("ADDRESS")

            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                actor="system",
                id="1",
                response=payload.model_dump(),
            )

        except Exception as e:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                id="1",
                message=f"Failed to verify bank account: {str(e)}",
            )
