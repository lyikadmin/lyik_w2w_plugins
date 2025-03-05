import logging
import os

from typing_extensions import Annotated, Doc

import apluggy as pluggy
import pymssql
from lyikpluginmanager import (
    ContextModel,
    getProjectName, PanVerificationSpec, PanVerificationResponseModel,
)

impl = pluggy.HookimplMarker(getProjectName())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PanVerification(PanVerificationSpec):
    @impl
    async def verify_pan(self,
                         context: ContextModel,
                         payload: Annotated[str, Doc("PAN number to be verified")]) -> Annotated[
        PanVerificationResponseModel, Doc("success or failure status and PAN holder's name")]:

        # 1. todo: read from env

        server = os.getenv("DB_SERVER")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")

        if not server:
            raise ValueError("Server configuration not set")

        # 2. execute sql query
        pan_number = payload
        query = "SELECT TOP 1 * FROM LYIKACCESS WHERE PAN_NO = %s"

        try:
            # Connect to the database using pymssql
            conn = pymssql.connect(
                server=server,
                port=port,
                user=username,
                password=password,
                database=database
            )

            cursor = conn.cursor(as_dict=True)  # Get results as dictionaries

            # Execute the query with parameter
            cursor.execute(query, (pan_number,))
            row = cursor.fetchone()

            # Close the connection
            conn.close()
            print("Connection closed successfully.")

            if not row:
                # Return the output model with appropriate values
                return PanVerificationResponseModel(
                    status=False,
                )

            # Assuming the columns in LYIKACCESS include first_name and last_name
            # Adjust the column names based on your actual database schema
            return PanVerificationResponseModel(
                status=True,
                name=row.get("NAME", ""),
                trading_account=row.get("TRADING_ACCOUNT", ""),
                customer_id=row.get("CUSTOMER_ID", "")
            )

        except Exception as e:
            logger.error(f"Error during PAN verification: {str(e)}")
            return PanVerificationResponseModel(
                status=False,
            )
