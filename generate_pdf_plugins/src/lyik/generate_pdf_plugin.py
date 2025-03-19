import apluggy as pluggy
import os
import importlib
from datetime import datetime
from .pdf_generator.pdf_generator import PdfGenerator
from .pdf_utilities.utility import get_geo_location
from .pdf_utilities.pdf_core import PdfCore
from .models.document_plugin_config import DocPluginConfig
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    GeneratePdfSpec,
    DocumentModel,
    DBDocumentModel,
    DocMeta,
    Esign,
    EsignState,
    EsignStatus,
    EsignMeta,
    OperationPluginSpec,
    OperationResponseModel,
    OperationStatus,
    GenericFormRecordModel,
    DocQueryGenericModel,
    GenerateAllDocsResponseModel,
    GenerateAllDocsStatus,
)
from lyikpluginmanager.annotation import RequiredVars, RequiredEnv
from typing import List
import json
import io
import string
import random
from pymongo import MongoClient
import hashlib
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from typing_extensions import Doc, Annotated

logger = logging.getLogger(__name__)

PDF_DB_NAME = "pdfs_db"
PDF_COLLECTION_NAME = "pdfs"
impl = pluggy.HookimplMarker(getProjectName())


class GeneratePdf(OperationPluginSpec, GeneratePdfSpec):

    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc("record id of the form record")],
        status: Annotated[str, Doc("status of the form record")],
        form_record: Annotated[GenericFormRecordModel, Doc("form record data")],
    ) -> Annotated[
        OperationResponseModel,
        RequiredEnv(["API_DOMAIN"]),
        RequiredVars(
            [
                "DB_CONN_URL",
                "DOWNLOAD_DOC_API_ENDPOINT",
                "PDF_GARBLE_KEY",
            ]
        ),
        Doc(
            "Returns the operation response having status and message. If status is success, then return the pdf link within the message."
        ),
    ]:
        """
        Pdf operation to generate and store the pdf.
        """

        if context is None:
            raise ValueError("context must be provided")
        if context.config is None:
            raise ValueError("config must be provided in the context")
        if record_id is None:
            raise ValueError("recordid must be provided")
        pdf_core = PdfCore()
        try:
            generate_all_docs_res = await pdf_core.generate_all_docs(
                context=context,
                form_record=form_record,
                record_id=record_id,
            )
            if not isinstance(generate_all_docs_res, GenerateAllDocsResponseModel):
                logger.debug("Pdf generation failed!")
                raise Exception("Pdf generation failed!")

            return OperationResponseModel(
                status=(
                    OperationStatus.SUCCESS
                    if generate_all_docs_res.status
                    else OperationStatus.FAILED
                ),
                message=f"Pdf generated successfully. Here's the link to downlaod: {generate_all_docs_res.zip_docs_link}",
            )
        except Exception as e:
            return OperationResponseModel(status=OperationStatus.FAILED, message=f"{e}")

    @impl
    async def generate_all_docs(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("form record for which the pdf need to be generated"),
        ],
        record_id: Annotated[
            int, Doc("record id of the form record which is saved in db")
        ],
    ) -> Annotated[
        GenerateAllDocsResponseModel,
        RequiredEnv(["API_DOMAIN"]),
        RequiredVars(
            [
                "DB_CONN_URL",
                "DOWNLOAD_DOC_API_ENDPOINT",
                "PDF_GARBLE_KEY",
            ]
        ),
        Doc(
            "Returns the operation response having status and message. If status is success, then return the pdf link within the message."
        ),
    ]:
        """
        This function will generate and store the pdf(s).
        """
        if context is None:
            raise ValueError("context must be provided")
        if context.config is None:
            raise ValueError("config must be provided in the context")
        if record_id is None:
            raise ValueError("recordid must be provided")
        pdf_core = PdfCore()

        return await pdf_core.generate_all_docs(
            context=context,
            form_record=form_record,
            record_id=record_id,
        )

    @impl
    async def generate_main_doc(
        self,
        context: ContextModel,
        record: Annotated[
            GenericFormRecordModel,
            Doc("form record fow which the pdf need to be generated"),
        ],
        record_id: Annotated[
            int | None, Doc("record id of the form record daved in db")
        ],
        pdf_name: Annotated[str | None, Doc("name to be assigned to generated pdf")],
    ) -> Annotated[
        io.BytesIO,
        RequiredVars(
            [
                "DB_CONN_URL",
            ]
        ),
        Doc("pdf file buffer"),
    ]:
        """
        Generates and return the pdf(StreamResponse) as BytesIO object.
        """
        # return super().generate_pdf(context, form_name, data)

        if context is None:
            raise ValueError("context must be provided")
        if context.config is None:
            raise ValueError("config must be provided in the context")

        pdf_core = PdfCore()
        return await pdf_core.generate_main_doc(
            context=context, record=record, record_id=record_id, pdf_name=pdf_name
        )
