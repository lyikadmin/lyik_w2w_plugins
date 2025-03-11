import apluggy as pluggy
from datetime import datetime
from typing import Optional, Annotated, Dict
from pydantic import (
    BaseModel,
    model_validator,
    ConfigDict,
    ValidationError,
    field_validator,
)
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing_extensions import Annotated, Doc
import re

impl = pluggy.HookimplMarker(getProjectName())


class DetailsOfDealings(BaseModel):
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
        if value is None:
            raise ValueError(
                "Website cannot be empty if provided. Enter a valid domain."
            )

        # Regex pattern to allow the required formats
        pattern = r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+$"

        if not re.match(pattern, value):
            raise ValueError("Invalid website format. Use a valid domain.")

        return value

    @model_validator(mode="after")
    def check_all_or_none(cls, values):
        values_dict = vars(values)
        non_empty_fields = [v for v in values_dict.values() if v not in [None, ""]]

        # If at least one field is filled, all must be filled
        if non_empty_fields and len(non_empty_fields) != len(values_dict):
            raise ValueError("Please fill all the details")

        return values


class SubBrokerVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            Dict,
            Doc(
                "Data related to Details of Dealing through Sub-brokers and other Stock Brokers"
            ),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status.")]:
        try:
            validated_payload = DetailsOfDealings(**payload)

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
