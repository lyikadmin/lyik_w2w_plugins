import logging
import os
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated, Doc
import apluggy as pluggy
import pymssql
from datetime import date
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)
from lyikpluginmanager.annotation import RequiredEnv

impl = pluggy.HookimplMarker(getProjectName())
logger = logging.getLogger(__name__)


class TradingAccountPayloadModel(BaseModel):
    trading_id: str | None = Field(
        None,
        description="Trading ID",
    )
    account_holder_name: str = Field(
        None,
        description="Account holder name ",
    )
    account_creation_date: date | None = (
        Field(
            None,
            description="Date of A/c creation",
        ),
    )
    trading_account_pan_number: str = Field(
        ...,
        description="PAN Number to be verified",
    )
    model_config = ConfigDict(extra="allow")


class AccountDetailsVerification(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            TradingAccountPayloadModel,
            Doc("Data related to Trading account having PAN number to be verified"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredEnv(["DB_SERVER", "DB_PORT", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]),
        Doc("success or failure status and account details"),
    ]:

        db_config = {
            "server": os.getenv("DB_SERVER"),
            "port": os.getenv("DB_PORT"),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USERNAME"),
            "password": os.getenv("DB_PASSWORD"),
        }

        if not db_config["server"]:
            raise PluginException("Server configuration not set")

        try:
            with pymssql.connect(**db_config) as conn:
                cursor = conn.cursor(as_dict=True)
                try:
                    cursor.execute(
                        "SELECT TOP 1 * FROM LYIKACCESS WHERE PAN_NO = %s",
                        (payload.trading_account_pan_number.upper(),),
                    )
                    row = cursor.fetchone()
                except Exception as e:
                    logger.error(f"[DB Query Error] Failed executing PAN lookup: {e}")
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.SUCCESS,
                        message=f"Database query failed while fetching PAN details: {e}",
                        actor="system",
                        response={},
                    )
        except Exception as e:
            logger.error(f"[DB Connection Error] Could not connect to database: {e}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                message=f"Database connection failed: {e}",
                actor="system",
                response={},
            )

        if not row:
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                message=f"Account details not found for PAN: {payload.trading_account_pan_number}",
                actor="system",
                response={},
            )

        data = {k: row.get(k, "") for k in ["CLIENT_ID", "CLIENT_NAME"]}
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message=f"Verified successfully by the system on {datetime.now()}. Account details: {data}",
            actor="system",
            response=data,
        )
