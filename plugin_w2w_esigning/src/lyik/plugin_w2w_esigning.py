import logging
from typing_extensions import Annotated, Doc
import apluggy as pluggy
from datetime import date
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    OperationPluginSpec,
    DBDocumentModel,
    PluginException,
    GenericFormRecordModel,
    OperationResponseModel,
    OperationStatus,
    DocQueryGenericModel,
    invoke,
    EsignState,
    DocMeta,
    DocumentModel
)
import os
from lyikpluginmanager.annotation import RequiredEnv, RequiredVars
from typing import List
from .w2w_esigning_utility.utility import stamp_pdf, digitally_sign_pdf, obfuscate_string
impl = pluggy.HookimplMarker(getProjectName())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class W2WEsigning(OperationPluginSpec):
    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc('record id of the form record')],
        status: Annotated[str, Doc('status of the form record')],
        form_record: Annotated[GenericFormRecordModel, Doc('form record')],
        params: Annotated[dict | None, Doc('additonal parameters require for the operation. N/A, pass None')],
    ) -> Annotated[OperationResponseModel,
                   RequiredEnv(["API_DOMAIN"]),
                    RequiredVars(
                        [
                            "DB_CONN_URL",
                            "DOWNLOAD_DOC_API_ENDPOINT",
                            "PDF_GARBLE_KEY",
                            "CRED_FILES_MOUNT_PATH",
                            "W2W_DIGITAL_SIGN_STAMP_IMAGE"
                            "PROTEAN_ESIGN_PFX",
                            "PROTEAN_ESIGN_PFX_PASSWORD"
                        ]
                    ),
                    Doc('Returns the operation response')]:
        """
        This will put a way2wealth stamp and digitally esign(using protean pfx certificate) the main pdf if it is fullly esigned!
        """
        
        if context is None:
            raise PluginException("context must be provided")
        if context.config is None:
            raise PluginException("config must be provided in the context")
        if record_id is None:
            raise PluginException("recordid must be provided")
        
        try:
            # 1. Get the main doc from db
            # 2. Check if the doc is fully esigned i.e. all esigners have signed
            # 3. If yes, proceed for way2wealth stamping and esigning and replace the new pdf in db.
            # 4. If no, return the response with message "Document is not fully esigned yet!"
            # 5. Succesfull response will include link to download pdfs.

            pdf_query_data = DocQueryGenericModel(
                record_id=record_id,
                org_id=context.org_id,
                form_id=context.form_id,
                doc_type="application/pdf",
                tag="main_doc",
            )

            main_docs = await self._get_main_docs(context=context,record_id=record_id, query_params=pdf_query_data)
            if not main_docs:
                return OperationResponseModel(
                    status=OperationStatus.FAILED,
                    message='Pdf not not found. Please generate and esign the pdf first!' if main_docs is None else 'Pdf(s) not present or not esinged yet!'
                )
            for doc in main_docs:
                # Todo: check if file is not already signed by way2wealth, if yes, skip the file.
                esigned_doc = self.perform_stamping_and_esigning(pdf_bytes=doc.doc_content)
                await self._update_file_in_db(
                    context=context,
                    filename=doc.doc_name,
                    file_bytes=esigned_doc,
                    doc_id=doc.doc_id,
                    # meta_data=doc.metaadata # todo: update metadat with org_signed = true
                )

            obfus_str = obfuscate_string(
                    data_str=f"{pdf_query_data.model_dump_json()}",
                    static_key=context.config.PDF_GARBLE_KEY,
                )

            api_domain = os.getenv("API_DOMAIN")
            download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
            pdf_link = api_domain + download_doc_endpoint + f"{obfus_str}.zip"
            return OperationResponseModel(
                message=f"Pdf(s) are digitally signed by Way2Wealth. Here\'s the link to download: {pdf_link}",
                status=OperationStatus.SUCCESS
            )
            
        except Exception as e:
            raise PluginException(f"An error occurred during esiging the document: {e}")
        

    async def _get_main_docs(self, context: ContextModel, record_id: int, query_params:DocQueryGenericModel) -> List[DBDocumentModel] | None:
        """
        Get the main pdf(s) which are fully esigned.
        """
        
        
        try:
            docs: List[DBDocumentModel] = await invoke.fetchDocument(
                config=context.config,
                org_id=context.org_id,
                file_id=None,
                coll_name=context.form_id,
                metadata_params=query_params,
            )
            if not docs:
                return None
            
            # pdf_docs = [doc for doc in docs if "pdf" in doc.metadata.doc_type]
            fully_signed_docs = []
            for doc in docs:
                if doc.metadata.esign:
                    # Check if all esigners have signed
                    if all(
                        em.sign_status.status == EsignState.DONE
                        for em in doc.metadata.esign.esign_meta
                    ):
                        
                        fully_signed_docs.append(doc)
            
            return fully_signed_docs

        except Exception as e:
            logger.debug(f"Error finding existing pdfs: {e}.")
            return None
        
    def perform_stamping_and_esigning(self, pdf_bytes:bytes)->bytes:
        """
        This function will stamp the pdf and esign it using the way2wealth certificate.
        """
        try:
            # 1. Stamp the pdf
            stamped_pdf = stamp_pdf(pdf_bytes=pdf_bytes)
            # 2. Esign the pdf
            esigned_pdf = digitally_sign_pdf(pdf_bytes=stamped_pdf)
            return esigned_pdf
        except Exception as e:
            logger.error(f"Error occurred during stamping and esigning: {e}")
            raise PluginException(f'Error occurred during stamping and esigning.', detailed_message=f'Error occurred during stamping and esigning: {e}')

    async def _update_file_in_db(
        self,
        context: ContextModel,
        filename: str,
        file_bytes: bytes,
        doc_id: str,
        meta_data: DocMeta | None = None,
    ) -> DBDocumentModel:
        """
        Uses doc management plugin to update the pdf file in the database given a doc_id
        """

        doc_model = DocumentModel(
            doc_name=filename,
            doc_type='application/pdf',
            doc_size=len(file_bytes),
            doc_content=file_bytes,
        )

        document_models: List[DBDocumentModel] = await invoke.updateDocument(
            config=context.config,
            org_id=context.org_id,
            document=doc_model,
            file_id=doc_id,
            coll_name=context.form_id,
            new_metadata=meta_data,
            metadata_params=None,
        )
        return document_models[0]

