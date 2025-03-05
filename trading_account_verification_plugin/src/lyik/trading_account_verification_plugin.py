import apluggy as pluggy
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing_extensions import Annotated, Doc

impl = pluggy.HookimplMarker(getProjectName())


class TradingAccountVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            Dict,
            Doc("data related to trading account information"),
        ],
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status.")]:
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message=f"Verified successfully by the system on {datetime.now()}",
            actor="system",
        )
