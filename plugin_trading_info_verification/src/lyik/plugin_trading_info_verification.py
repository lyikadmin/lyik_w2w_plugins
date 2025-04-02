import apluggy as pluggy
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import (
    BaseModel,
    field_validator,
    ConfigDict,
    model_validator,
    ValidationError,
)
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)
from typing_extensions import Annotated, Doc
import re

impl = pluggy.HookimplMarker(getProjectName())


class TradingInformationPayload(BaseModel):
    segment_pref_1: Optional[str] = None
    segment_pref_2: Optional[str] = None
    segment_pref_3: Optional[str] = None
    segment_pref_4: Optional[str] = None
    segment_pref_5: Optional[str] = None
    segment_pref_6: Optional[str] = None
    contract_format_1: Optional[str] = None
    contract_format_2: Optional[str] = None
    proof_of_income: Optional[str] = None
    type_of_document: Optional[str] = None
    client_facility_choice: Optional[str] = None
    kit_format_1: Optional[str] = None
    kit_format_2: Optional[str] = None
    holder_trading_experience: Optional[str] = None

    broker_name: Optional[str] = None
    telephone: Optional[str] = None
    client_codes: Optional[str] = None
    broker_address: Optional[str] = None
    sub_broker_name: Optional[str] = None
    website: Optional[str] = None
    detail_of_disputes: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("website")
    @classmethod
    def validate_website(cls, value):
        pattern = r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+$"
        if value and not re.match(pattern, value):
            raise PluginException("Invalid website format. Use a valid domain.")
        return value

    @model_validator(mode="after")
    def check_mandatory_fields(cls, values):
        values_dict = vars(values)
        segment_prefs = [
            v
            for k, v in values_dict.items()
            if k.startswith("segment_pref_") and v is not None
        ]
        contract_formats = [
            v
            for k, v in values_dict.items()
            if k.startswith("contract_format_") and v is not None
        ]
        kit_formats = [
            v
            for k, v in values_dict.items()
            if k.startswith("kit_format_") and v is not None
        ]
        trading_experience = values_dict.get("holder_trading_experience")

        if not segment_prefs:
            raise PluginException(
                "Please select how to send the Client the account opening kit."
            )
        if not contract_formats:
            raise PluginException("Please select how you wish to receive the Contract")
        if not kit_formats:
            raise PluginException("At least one kit format is required.")
        if trading_experience is None:
            raise PluginException("Holder's trading experience is required.")
        # Check if segment_pref_2, segment_pref_3, or segment_pref_4 is filled
        if any(
            values_dict.get(seg)
            for seg in ["segment_pref_2", "segment_pref_3", "segment_pref_4"]
        ):
            if not values_dict.get("proof_of_income"):
                raise PluginException(
                    "Proof of income is required if F & O, Currency, or Commodity is selected."
                )

        sub_broker_fields = [
            "broker_name",
            "telephone",
            "client_codes",
            "broker_address",
            "sub_broker_name",
            "website",
            "detail_of_disputes",
        ]
        non_empty_fields = [
            k for k in sub_broker_fields if values_dict.get(k) not in [None, ""]
        ]
        if non_empty_fields and len(non_empty_fields) != len(sub_broker_fields):
            raise PluginException(
                "Please fill all the details in Details of Dealing through Sub-brokers and other Stock Brokers if providing any."
            )
        return values


class TradingInformationVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            Dict,
            Doc("Payload containing trading information"),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status.")]:
        try:
            flattened_payload = {
                **payload.get("trading_account_information", {}),
                **payload.get("details_of_dealings", {}),
            }
            validated_payload = TradingInformationPayload(**flattened_payload)

            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                message=f"Verified successfully by the system on {datetime.now()}",
                actor="system",
            )

        except ValidationError as e:
            error_messages = [err["msg"].split(", ", 1)[-1] for err in e.errors()]
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=" ".join(error_messages),
                actor="system",
            )
        except PluginException as e:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=e.message,
                actor="system",
            )
