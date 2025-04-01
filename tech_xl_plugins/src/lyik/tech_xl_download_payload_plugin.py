import apluggy as pluggy
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime
import base64
from lyikpluginmanager import (
    getProjectName,
    invoke,
    ContextModel,
    OperationPluginSpec,
    GenericFormRecordModel,
    OperationResponseModel,
    DocumentModel,
    OperationStatus,
    DocMeta,
    DocQueryGenericModel,
    PluginException,
)
from typing import Dict
from typing_extensions import Doc, Annotated
import json
from lyikpluginmanager.annotation import RequiredVars, RequiredEnv
import logging
import os
from .tech_xl_utils.utils import TechXLUtils

logging.basicConfig(level=logging.debug)
logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class TechXLDownloadPayload(OperationPluginSpec):

    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc("record id of the form record")],
        status: Annotated[str, Doc("status of the form record")],
        form_record: Annotated[GenericFormRecordModel, Doc("form record")],
    ) -> Annotated[
        OperationResponseModel,
        RequiredVars(["DB_CONN_URL", "DOWNLOAD_DOC_API_ENDPOINT", "PDF_GARBLE_KEY"]),
        RequiredEnv(["API_DOMAIN"]),
        Doc("TechXL upload request result"),
    ]:
        """
        Creates a json file having payload for TechXL and stores in db, returns link to download payload files.

        """
        try:
            # Fetch transformed data for TechXL
            data: Dict = await TechXLUtils.getTechxlTransformedData(
                context=context, form_record=form_record
            )
            if not data:
                raise PluginException("Unable to get TechXL transformed data")

            # Store the payload data into the database
            await self.store_payload(context=context, data=data, rec_id=record_id)

            # Create the link for downloading the payload file
            link_data = DocQueryGenericModel(
                org_id=context.org_id, form_id=context.form_id, record_id=record_id
            )
            link_data = link_data.model_copy(
                update={
                    "tag": "techxl"
                }  # Will help in flitering just the files having `techxl` tag in metadata.
            )

            # Obfuscate the data string
            obfus_str = self.obfuscate_string(
                data_str=link_data.model_dump_json(),
                static_key=context.config.PDF_GARBLE_KEY,
            )

            # Build the download URL for the payload
            api_domain = os.getenv("API_DOMAIN")
            download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
            download_url = api_domain + download_doc_endpoint + f"{obfus_str}.zip"

            # Return the successful operation response with the download URL
            return OperationResponseModel(
                status=OperationStatus.SUCCESS,
                message=f"TechXL Payload download URL : {download_url}",
            )
        except PluginException as e:
            # Catch PluginException raised during data transformation or other issues
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message=f"TechXL Payload creation failed: {str(e)}",
            )
        except Exception as e:
            # Catch any other exceptions and log them
            logger.debug(
                f"Failed to create the json file having payload for TechXL and store in db: {str(e)}"
            )
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message=f"Failed to create the json file having payload for TechXL: {str(e)}",
            )

    async def store_payload(self, context: ContextModel, data: Dict, rec_id: int):
        """
        Stores the payload data in the database as a JSON file.

        :param context: The current context containing configuration and other necessary info.
        :param data: The payload data that will be stored.
        :param rec_id: The unique identifier for the record being processed.
        """
        try:
            # Write the dictionary to a JSON file
            file_bytes = json.dumps(data).encode("utf-8")
            file_name = f"tech_xl_upload_{datetime.now().isoformat()}.json"

            # Prepare metadata for storing the document
            meta_data = DocMeta(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=rec_id,
            )
            meta_data = meta_data.model_copy(update={"tag": "techxl"})

            # Invoke document storage process
            plugin_res = await invoke.updateDocument(
                config=context.config,
                org_id=context.org_id,
                file_id=None,
                document=DocumentModel(
                    doc_name=file_name,
                    doc_size=len(file_bytes),
                    doc_content=file_bytes,
                    doc_type="application/json",
                ),
                coll_name=context.form_id,
                new_metadata=meta_data,
                metadata_params=DocQueryGenericModel(
                    **(meta_data.model_dump(exclude_unset=True))
                ),
            )
        except Exception as e:
            raise PluginException(f"Failed to store the payload for TechXL: {str(e)}")

    def obfuscate_string(self, data_str: str, static_key: str) -> str:
        """
        Obfuscates a string using AES encryption with a static key.

        :param data_str: The string that will be encrypted.
        :param static_key: The key used for encryption.
        :return: The obfuscated string in Base64 format.
        """
        try:
            # Ensure the key is exactly 16 bytes long
            key = static_key.encode().ljust(16, b"\0")

            # Data to encrypt
            data = data_str.encode()

            # Create cipher and encrypt the data with padding
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted_data = cipher.encrypt(pad(data, AES.block_size))

            # Encode the encrypted data with Base64
            obfuscated_string = base64.urlsafe_b64encode(encrypted_data).decode()
            return obfuscated_string

        except Exception as e:
            raise PluginException(f"Failed to obfuscate the string: {str(e)}")
