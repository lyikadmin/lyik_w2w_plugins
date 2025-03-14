import apluggy as pluggy
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, ValidationError
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing_extensions import Annotated, Doc

impl = pluggy.HookimplMarker(getProjectName())


class TradingAccountInformationPayload(BaseModel):
    segment_pref_1: Optional[str] = None
    segment_pref_2: Optional[str] = None  # FNO
    segment_pref_3: Optional[str] = None  # CURRENCY
    segment_pref_4: Optional[str] = None  # COMMODITY
    segment_pref_5: Optional[str] = None
    segment_pref_6: Optional[str] = None
    contract_format_1: Optional[str] = None
    contract_format_2: Optional[str] = None
    proof_of_income: Optional[str] = None  #
    type_of_document: Optional[str] = None
    client_facility_choice: Optional[str] = None
    kit_format_1: Optional[str] = None
    kit_format_2: Optional[str] = None
    holder_trading_experience: Optional[str] = None

    model_config = ConfigDict(extra="allow")

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
            raise ValueError(
                "Please select how to send the Client the account opening kit."
            )
        if not contract_formats:
            raise ValueError("Please select how you wish to receive the Contract")
        if not kit_formats:
            raise ValueError("At least one kit format is required.")
        if trading_experience is None:
            raise ValueError("Holder's trading experience is required.")
        # Check if segment_pref_2, segment_pref_3, or segment_pref_4 is filled
        if any(
            values_dict.get(seg)
            for seg in ["segment_pref_2", "segment_pref_3", "segment_pref_4"]
        ):
            if not values_dict.get("proof_of_income"):
                raise ValueError(
                    "Proof of income is required if F & O, Currency, or Commodity is selected."
                )
        return values


class TradingAccountVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            Dict,
            Doc("Payload containing trading account information"),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status.")]:
        try:
            validated_payload = TradingAccountInformationPayload(**payload)

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
