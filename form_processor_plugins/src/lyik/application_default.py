import logging
import pandas as pd
import jwt  # PyJWT for decoding JWT tokens
from typing import List, Dict, Any, Annotated
from pydantic import BaseModel, Field
import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    FormProcessorPipelineSpec,
    ContextModel,
    GenericFormRecordModel,
)
from typing_extensions import Doc

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())

CSV_URL = "https://raw.githubusercontent.com/lyikadmin/defaults/refs/heads/main/franchise_application_default_values.csv"

APPLICATION_DETAILS_FIELD_NAME = "application_details"
DEFAULT = "default"
FRANCHISE_ID = "franchise_id"


class FinancialRates(BaseModel):
    cash_minimum_paisa: float = Field(..., description="Cash minimum paisa")
    cash_in_percentage: float = Field(..., description="Cash in percentage")
    cash_jobbing_minimum_paisa: float = Field(
        ..., description="Cash jobbing minimum paisa"
    )
    cash_jobbing_in_percentage: float = Field(
        ..., description="Cash jobbing in percentage"
    )
    futures_minimum_paisa: float = Field(..., description="Futures minimum paisa")
    futures_in_percentage: float = Field(..., description="Futures in percentage")
    options_standard_rate: float = Field(..., description="Options standard rate")
    currency_futures_minimum_paisa: float = Field(
        ..., description="Currency futures minimum paisa"
    )
    currency_futures_in_percentage: float = Field(
        ..., description="Currency futures in percentage"
    )
    currency_options_rate: float = Field(..., description="Currency options rate")
    commodity_futures_minimum_paisa: float = Field(
        ..., description="Commodity futures minimum paisa"
    )
    commodity_futures_in_percentage: float = Field(
        ..., description="Commodity futures in percentage"
    )
    commodity_options_rate: float = Field(..., description="Commodity options rate")
    slb_rate: float = Field(..., description="SLB rate")


class ApplicationDefaults(FormProcessorPipelineSpec):
    @impl
    async def form_definition_processor_pipeline(
        self,
        context: ContextModel | None,
        bform: Annotated[
            GenericFormRecordModel,
            Doc(
                "The Business form in its entirety. for this plugin, we need 'application_details' field in the businessform, to update the default options."
            ),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        Doc(
            "the updated business form with updated options for default in application_details"
        ),
    ]:
        """
        This method updates the 'application_details' field with default options based on the users franchise_id.
        The Defaults are fetched from a csv file hosted on github.
        """
        # Step 1: Check if 'application_details' exists in form_fields
        if not self.contains_application_details(bform.form_fields):
            # logger.info("No 'application_details' field found. Skipping CSV fetch.")
            return bform  # Skip processing if 'application_details' is absent

        # Step 2: Extract franchise_id from JWT token
        encoded_token = context.token
        franchise_id = self.get_franchise_id(encoded_token)

        try:
            # Step 3: Attempt to Load CSV Data
            df = self.load_csv()
            if df is None:
                return bform  # If CSV is missing/unreadable, return the form as-is

            # Lookup Franchise Data
            row = (
                df[df[FRANCHISE_ID] == franchise_id]
                if franchise_id
                else pd.DataFrame()
            )
            if row.empty:
                row = df[
                    df[FRANCHISE_ID] == DEFAULT
                ]  # Fallback to DEFAULT if not found

            if not row.empty:
                row_dict = row.iloc[0].to_dict()
                new_options = FinancialRates.model_validate(row_dict).model_dump()

                # Step 4: Update 'defaults' options
                self.update_defaults(bform.form_fields, new_options)

        except Exception as e:
            logger.error(f"Unexpected error processing form: {e}", exc_info=True)
            return bform  # Return unchanged form on error

        return bform

    def load_csv(self) -> pd.DataFrame | None:
        """Loads the CSV file. Returns None if the CSV is missing or unreadable."""
        try:
            df = pd.read_csv(CSV_URL)
            df.columns = df.columns.str.strip()
            df[FRANCHISE_ID] = df[FRANCHISE_ID].astype(str).str.strip()
            return df
        except FileNotFoundError:
            logger.error("CSV file not found. Skipping updates.")
        except pd.errors.ParserError:
            logger.error("Error parsing CSV file. Skipping updates.")
        except Exception as e:
            logger.error(f"Unexpected error reading CSV: {e}")
        return None  # Return None if an error occurs

    def get_franchise_id(self, encoded_token: str) -> str:
        """Decodes JWT token and extracts `franchise_id`, returning 'DEFAULT' if missing."""
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

        return (
            DEFAULT  # Default fallback if franchise_id is missing or decoding fails
        )

    def contains_application_details(self, fields: List[Dict[str, Any]]) -> bool:
        """Recursively searches for 'application_details' in the form fields."""
        for field in fields:
            if field["field_name"] == APPLICATION_DETAILS_FIELD_NAME:
                return True
            if "fields" in field and isinstance(field["fields"], list):
                if self.contains_application_details(field["fields"]):
                    return True
        return False

    def update_defaults(
        self, fields: List[Dict[str, Any]], new_options: Dict[str, Any]
    ) -> None:
        """Recursively searches for 'application_details' and updates its 'defaults' field options."""
        for field in fields:
            if field["field_name"] == APPLICATION_DETAILS_FIELD_NAME:
                for subfield in field.get("fields", []):
                    if subfield["field_name"] == "defaults":
                        subfield["options"] = new_options  # Update the options
                        # logger.info(f"Updated 'defaults' options: {new_options}")
                        return  # Stop after updating
            if "fields" in field and isinstance(field["fields"], list):
                self.update_defaults(field["fields"], new_options)
