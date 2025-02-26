import logging
import pandas as pd
import jwt
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    VerifyHandlerSpec,
    ContextModel,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    generate_hash_id_from_dict,
)
from pydantic import BaseModel, ConfigDict
from typing_extensions import Annotated, Doc

from datetime import datetime

impl = pluggy.HookimplMarker(getProjectName())

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CSV_URL = "https://raw.githubusercontent.com/lyikadmin/defaults/refs/heads/main/franchise_application_default_values.csv"
FRANCHISE_ID = "franchise_id"
DEFAULT = "DEFAULT"


class GeneralApplicationDetails(BaseModel):
    application_type: str = Field(...)
    residential_status: str = Field(...)


class CashFutComoCard(BaseModel):
    cash_minimum_paisa: float = Field(...)
    cash_in_percentage: float = Field(...)


class CashJobbingCard(BaseModel):
    cash_jobbing_minimum_paisa: float = Field(...)
    cash_jobbing_in_percentage: float = Field(...)


class FuturesCard(BaseModel):
    futures_minimum_paisa: float = Field(...)
    futures_in_percentage: float = Field(...)


class OptionsCard(BaseModel):
    options_standard_rate: float = Field(...)


class CurrencyFuturesCard(BaseModel):
    currency_futures_minimum_paisa: float = Field(...)
    currency_futures_in_percentage: float = Field(...)


class CurrencyOptionsCard(BaseModel):
    currency_options_rate: float = Field(...)


class CommodityFuturesCard(BaseModel):
    commodity_futures_minimum_paisa: float = Field(...)
    commodity_futures_in_percentage: float = Field(...)


class CommodityOptionsCard(BaseModel):
    commodity_options_rate: float = Field(...)


class SlbCard(BaseModel):
    slb_rate: float = Field(...)


class FlatPerOrderCard(BaseModel):
    flat_per_order_rate: Optional[float] = Field(None)


class OnlineExeCard(BaseModel):
    online_exe: Optional[float] = Field(None)


class GstDetailsCard(BaseModel):
    gst_number: Optional[str] = Field(None)
    gst_number_1: Optional[str] = Field(None)


class ClientContactDetails(BaseModel):
    client_mobile: Optional[str] = Field(None)


class SegmentRates(BaseModel):
    pass


class ApplicationDetailsModel(BaseModel):
    defaults: Optional[dict] = Field(None)
    kyc_digilocker: str = Field(...)
    general_application_details: GeneralApplicationDetails = Field(...)
    cash_fut_como_card: CashFutComoCard = Field(...)
    cash_jobbing_card: CashJobbingCard = Field(...)
    futures_card: FuturesCard = Field(...)
    options_card: OptionsCard = Field(...)
    currency_futures_card: CurrencyFuturesCard = Field(...)
    currency_options_card: CurrencyOptionsCard = Field(...)
    commodity_futures_card: CommodityFuturesCard = Field(...)
    commodity_options_card: CommodityOptionsCard = Field(...)
    slb_card: SlbCard = Field(...)
    flat_per_order_card: FlatPerOrderCard = Field(...)
    online_exe_card: OnlineExeCard = Field(...)
    gst_details_card: GstDetailsCard = Field(...)
    client_contact_details: ClientContactDetails = Field(...)
    segment_rates: SegmentRates = Field(...)
    model_config = ConfigDict(extra="allow")


class ApplicationDetails(VerifyHandlerSpec):
    """
    Implementation of the VerifyHandlerSpec interface for Application Details verification.
    """

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            ApplicationDetailsModel,
            Doc("Payload data to be verified against default range of values"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc(
            "Succeeds if all values are equal to, or above the desired minimums. Fails otherwise."
        ),
    ]:
        """
        This verifies whether the payload values are above the desired minimum values, which is tied to the users franchise_id
        """

        payload_dict = payload.model_dump()

        # NOTE: Handling re-verification
        ret = check_if_verified(payload_dict=payload_dict)
        if ret:
            return ret

        client_mobile = payload_dict["client_contact_details"]["client_mobile"]
        validated_phone = validate_phone(client_mobile)
        payload_dict["client_contact_details"]["client_mobile"] = validated_phone

        # Step 1: Extract franchise_id from JWT token
        encoded_token = context.token
        franchise_id = self.get_franchise_id(encoded_token)

        # Step 2: Load CSV Defaults (return success if CSV cannot be read)
        options_defaults = self.load_csv_defaults(franchise_id)
        if options_defaults is None:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message="Verification skipped as CSV could not be read.",
            )

        # Step 3: Compare Payload with CSV Defaults
        ver_status = self._compare_defaults_with_payload(options_defaults, payload_dict)

        old_ver_status = payload_dict.pop("_ver_status", None)

        ver_status.response = payload_dict
        return ver_status

    def get_franchise_id(self, encoded_token: str) -> str:
        """Decodes JWT token and extracts `franchise_id` safely, returning 'DEFAULT' if missing."""
        # return "FR_006"
        try:
            decoded_token = jwt.decode(
                encoded_token, options={"verify_signature": False}
            )
            franchise_id = (
                decoded_token.get("user_metadata", {})
                .get("user_info", {})
                .get(FRANCHISE_ID)
            )
            if franchise_id:
                # logger.info(f"Extracted franchise_id: {franchise_id}")
                return franchise_id
        except jwt.DecodeError:
            logger.error("Failed to decode JWT token. Using DEFAULT.")
        except Exception as e:
            logger.error(f"Unexpected error decoding JWT: {e}")

        return DEFAULT  # Default fallback if franchise_id is missing or decoding fails

    def load_csv_defaults(self, franchise_id: str) -> Dict[str, Any] | None:
        """Safely loads the CSV file and fetches defaults for the given franchise_id."""
        try:
            df = pd.read_csv(CSV_URL)
            df.columns = df.columns.str.strip()
            df[FRANCHISE_ID] = df[FRANCHISE_ID].astype(str).str.strip()

            # Lookup Franchise Data
            row = (
                df[df[FRANCHISE_ID] == franchise_id] if franchise_id else pd.DataFrame()
            )
            if row.empty:
                row = df[
                    df[FRANCHISE_ID] == DEFAULT
                ]  # Fallback to DEFAULT if not found

            if not row.empty:
                # logger.info(f"Using defaults for franchise_id: {franchise_id}")
                return row.iloc[0].to_dict()

        except FileNotFoundError:
            logger.error("CSV file not found. Skipping verification.")
        except pd.errors.ParserError:
            logger.error("Error parsing CSV file. Skipping verification.")
        except Exception as e:
            logger.error(f"Unexpected error reading CSV: {e}")

        return None  # Return None if an error occurs

    def _compare_defaults_with_payload(
        self, options_defaults: Dict[str, Any], payload: Dict[str, Any]
    ) -> VerifyHandlerResponseModel:
        """
        Compares payload values against CSV default values, searching nested fields.
        """
        try:
            for key, minimum_default_value in options_defaults.items():
                payload_value = self._find_nested_value(payload, key)

                if payload_value is not None:
                    if float(minimum_default_value) > float(
                        payload_value
                    ):  # Check limit
                        return VerifyHandlerResponseModel(
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                            actor="system",
                            message=f"Value for {key} is not in desired range >={minimum_default_value}",
                        )

        except Exception as e:
            logger.error(f"Fatal error during verification: {e}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message="Fatal error. Please contact the admin.",
            )

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            actor="system",
            message="Verified successfully.",
            id=generate_hash_id_from_dict(payload),
        )

    def _find_nested_value(self, payload: Dict[str, Any], target_key: str) -> Any:
        """
        Recursively searches for a key in a nested dictionary and returns its value.
        """
        if target_key in payload:
            return payload[target_key]  # Found at the current level

        for _, value in payload.items():
            if isinstance(value, dict):  # Dive into nested dicts
                result = self._find_nested_value(value, target_key)
                if result is not None:
                    return result

        return None  # Key not found


def check_if_verified(payload_dict: dict) -> VerifyHandlerResponseModel | None:
    """
    Handle the flow is payload if already verified. (Re-verification)
    Check if ver_Status already exists. If it does, check if values have changed.
    If it has, return failure status as values are inconsistent.
    """

    if payload_dict.get("_ver_status"):
        ver_Status = VerifyHandlerResponseModel.model_validate(
            payload_dict.get("_ver_status")
        )
        if ver_Status.status == VERIFY_RESPONSE_STATUS.SUCCESS:
            current_id = ver_Status.id
            generated_id = generate_hash_id_from_dict(payload_dict)
            if str(current_id) == str(generated_id):
                return ver_Status
            else:
                ver_Status.status = VERIFY_RESPONSE_STATUS.FAILURE
                ver_Status.message = "Values have changed. Please Re-verify"
                return ver_Status

    return None


import phonenumbers


def validate_phone(value: str) -> str:
    phone = phonenumbers.parse(
        number=value,
        region=phonenumbers.region_code_for_country_code(int(91)),
    )
    if not phonenumbers.is_valid_number(phone):
        raise ValueError(f"{value} does not seem like a valid phone number")

    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
