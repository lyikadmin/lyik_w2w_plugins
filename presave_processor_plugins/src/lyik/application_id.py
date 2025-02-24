import logging
from typing import Dict
from pydantic import Field, BaseModel
from typing_extensions import Doc, Annotated
from datetime import datetime
import random
import string


import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreSaveProcessorPipelineSpec,
    ContextModel,
    GenericFormRecordModel,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())


def generate_unique_application_id() -> str:
    prefix = "APPLICATION"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{timestamp}-{random_str}"


class ApplicationId(PreSaveProcessorPipelineSpec):
    @impl
    async def pre_save_processor_pipeline(
        self,
        context: ContextModel | None,
        payload: Annotated[
            GenericFormRecordModel,
            Doc("The form record "),
        ],
    ) -> Annotated[
        GenericFormRecordModel, Doc("The updated form record with application_id")
    ]:
        """
        This presave processor adds application_id field to the form record if not already present.
        """
        payload_dict = payload.model_dump()

        # Fetch existing created_on if already exists, else use current_time
        application_id = payload_dict.get("_application_id", {})

        if not application_id:
            application_id = generate_unique_application_id()
            payload_dict.update({"_application_id": application_id})

        return GenericFormRecordModel.model_validate(payload_dict)
