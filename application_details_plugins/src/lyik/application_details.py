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
from pydantic import BaseModel, ConfigDict
from typing_extensions import Annotated, Doc

from datetime import datetime

impl = pluggy.HookimplMarker(getProjectName())


class ApplicationDetailsPayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApplicationDetails(VerifyHandlerSpec):
    """
    Implementation of the VerifyHandlerSpec interface for Application Details verification.
    """

    DEFAULT_KEY = "defaults"

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            ApplicationDetailsPayload,
            Doc("Payload data to be verified against default range of values"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel, Doc("success or failure response with message")
    ]:
        """
        This will verify whether the values in the fields are in the limit of default values.
        """

        fileds_def: Dict[str, Any] = context.field_definition

        return self._compare_defaults_with_payload(
            field_def=fileds_def, payload=payload.model_dump()
        )

    def _compare_defaults_with_payload(
        self, field_def: Dict[str, Any], payload: Dict[str, Any]
    ) -> VerifyHandlerResponseModel:

        _default = self._find_defaults_field(field_def=field_def)
        try:
            options_defaults = _default["options"]
            for key, default_value in options_defaults.items():
                payload_value = self._find_payload_value(payload, key)
                if payload_value is not None:
                    if float(default_value) <= float(payload_value):
                        pass
                    else:
                        title = self.find_field_title_by_derived_name(
                            derived_field_name=key, field_def=field_def
                        )
                        return VerifyHandlerResponseModel(
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                            actor="system",
                            message=f"Value for \n{title} is not in desired range {default_value}",
                        )
                else:
                    print(f"Key '{key}' not found in payload.")
        except Exception as e:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message="Fatal Error please contact the admin",
            )
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            actor="system",
            message=f"Verified by the system on {datetime.now()}",
        )

    def _find_defaults_field(self, field_def: Dict[str, Any]) -> Dict[str, Any]:
        if field_def.get("derived_field_name") == self.DEFAULT_KEY:
            return field_def
        for field in field_def.get("fields", []):
            result = self._find_defaults_field(field)
            if result:
                return result
        return None

    def find_field_title_by_derived_name(
        self, field_def: Dict[str, Any], derived_field_name: str
    ):
        """
        Recursively search for a field with the specified derived_field_name in a nested dictionary or list.

        Args:
            data (dict or list): The data structure to search.
            derived_field_name (str): The derived_field_name to search for.

        Returns:
            dict or None: The field dictionary if found, otherwise None.
        """
        if isinstance(field_def, dict):
            # Check if the current dictionary has the desired derived_field_name
            if field_def.get("derived_field_name") == derived_field_name:
                return field_def.get("title")
            # Recursively search in the 'fields' key if present
            if "fields" in field_def:
                for sub_field in field_def["fields"]:
                    result = self.find_field_title_by_derived_name(
                        sub_field, derived_field_name
                    )
                    if result:
                        return result

        elif isinstance(field_def, list):
            # If the data is a list, search each element
            for item in field_def:
                result = self.find_field_title_by_derived_name(item, derived_field_name)
                if result:
                    return result

        return None

    def _find_payload_value(self, payload_data, options_key):
        if options_key in payload_data:
            return payload_data[options_key]
        for k, v in payload_data.items():
            if isinstance(v, dict):
                result = self._find_payload_value(v, options_key)
                if result is not None:
                    return result
        return None
