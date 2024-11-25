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
from datetime import datetime

impl = pluggy.HookimplMarker(getProjectName())


class ApplicationDetails(VerifyHandlerSpec):
    """
    This will verify the application detail values with the default values
    """

    DEFAULT_KEY = "defaults"

    @impl
    async def verify_handler(
        self, context: ContextModel, payload: SingleFieldModel
    ) -> VerifyHandlerResponseModel:

        fileds_def: Dict[str, Any] = context.field_definition

        return self._compare_defaults_with_payload(
            field_def=fileds_def, payload=payload.payload
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
                        return VerifyHandlerResponseModel(
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                            actor="system",
                            message=f"Value for {key} is not in desired range {default_value}",
                        )
                else:
                    print(f"Key '{key}' not found in payload.")
        except Exception as e:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE, actor="system", message=str(e)
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

    def _find_payload_value(self, payload_data, options_key):
        if options_key in payload_data:
            return payload_data[options_key]
        for k, v in payload_data.items():
            if isinstance(v, dict):
                result = self._find_payload_value(v, options_key)
                if result is not None:
                    return result
        return None
