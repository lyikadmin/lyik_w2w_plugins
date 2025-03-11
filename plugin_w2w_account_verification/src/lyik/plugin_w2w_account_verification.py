import logging
import os
from datetime import datetime
from typing_extensions import Annotated, Doc
import apluggy as pluggy
import pymssql
from lyikpluginmanager import (
    ContextModel, getProjectName, VerifyHandlerSpec,
    VerifyHandlerResponseModel, VERIFY_RESPONSE_STATUS
)

impl = pluggy.HookimplMarker(getProjectName())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AccountDetailsVerification(VerifyHandlerSpec):
    async def verify_handler(
            self,
            context: ContextModel,
            payload: Annotated[str, Doc("PAN number to be verified")]
    ) -> Annotated[VerifyHandlerResponseModel, Doc("success or failure status and account details")]:
        try:
            db_config = {
                "server": os.getenv("DB_SERVER"),
                "port": os.getenv("DB_PORT"),
                "database": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USERNAME"),
                "password": os.getenv("DB_PASSWORD")
            }

            if not db_config["server"]:
                raise ValueError("Server configuration not set")

            with pymssql.connect(**db_config) as conn:
                cursor = conn.cursor(as_dict=True)
                cursor.execute("SELECT TOP 1 * FROM LYIKACCESS WHERE PAN_NO = %s", (payload,))
                row = cursor.fetchone()

            if not row:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    message=f"Account details not found for PAN: {payload}",
                    actor="system"
                )

            data = {k: row.get(k, "") for k in ["NAME", "TRADING_ACCOUNT", "CUSTOMER_ID"]}
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                message=f"Verified successfully by the system on {datetime.now()}. Account details: {data}",
                actor="system",
                response=data
            )

        except Exception as e:
            logger.error(f"Error during account verification: {str(e)}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=f"{e}",
                actor="system"
            )
