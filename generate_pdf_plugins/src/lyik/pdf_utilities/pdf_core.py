import apluggy as pluggy
import os
import importlib
from datetime import datetime
from ..pdf_generator.pdf_generator import PdfGenerator
from ..pdf_utilities.utility import get_geo_location
from ..models.document_plugin_config import DocPluginConfig
from lyikpluginmanager import (
    invoke,
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
    PluginException,
    TransformerResponseModel,
    TemplateDocumentModel,
    TRANSFORMER_RESPONSE_STATUS,
)
from lyikpluginmanager.annotation import RequiredVars
from typing import List, Any, Dict
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

impl = pluggy.HookimplMarker(getProjectName())


class PdfCore:
    """
    Handles the core functionality of All Docs Generation.
    """

    async def generate_all_docs(
        self, context: ContextModel, form_record: GenericFormRecordModel, record_id: int
    ) -> GenerateAllDocsResponseModel:
        """
        Pdf operation to generate and store the pdf.
        """

        config = context.config

        # TODO : -- ADD METHOD TO DECIDE TEMPLATE NAME BASED ON FORM RECORD STRUCTURE.
        form_temp_name = "aof_form"
        if form_temp_name is None:
            raise ValueError(
                "Form template is required to generated pdf, otherwise form doesn't support pdf."
            )
        logger.debug(
            f"org-id: {context.org_id}\nform-id: {context.form_id}\nrecord id: {record_id}"
        )

        # Initialiazing singleton to use wherever needed later.
        document_plugin_config = DocPluginConfig(context=context)

        logger.debug(
            f"Doc Plugin Config initialized: {document_plugin_config.is_none()}"
        )

        # SET PDF NAME AS FORM_NAME+RECORDID.pdf
        final_name = (
            f"{context.form_name}".replace(" ", "_")
            + f"{record_id}"
            + f'_{datetime.now().strftime("%H%M%S_%d%m%Y")}.pdf'
        )

        current_dir = os.path.dirname(os.path.abspath(__file__))
        generated_pdf_path = os.path.join(current_dir, final_name)

        temp_name = template_dict.get(form_temp_name)
        try:
            author = form_record.model_dump().get("submitter", {}).get("id", "")
            if temp_name:

                # CHECK IF FILES ALREADY PRESENT AND LOCKED.
                # IF YES, DO NOT PROCEED! RETURN success status having message saying existing record found and locked! ALONG WITH EXISING FILES LINK.
                existing_pdfs: List[DBDocumentModel] = await self._get_files_from_db(
                    context=context,
                    query_params=DocQueryGenericModel(
                        org_id=context.org_id,
                        form_id=context.form_id,
                        record_id=record_id,
                    ),
                )
                locked = (
                    False
                    if not existing_pdfs
                    else self._check_locked(docs=existing_pdfs)
                )

                if locked:
                    pdf_query_data = DocQueryGenericModel(
                        org_id=context.org_id,
                        form_id=context.form_id,
                        record_id=record_id,
                        doc_type="application/pdf",
                    )  # doc_type to avoid having other files getting downloaded when fetched!
                    obfus_str = self.obfuscate_string(
                        data_str=f"{pdf_query_data.model_dump_json()}",
                        static_key=config.PDF_GARBLE_KEY,
                    )

                    api_domain = os.getenv("API_DOMAIN")
                    download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
                    pdf_link = api_domain + download_doc_endpoint + f"{obfus_str}.zip"
                    return GenerateAllDocsResponseModel(
                        status=GenerateAllDocsStatus.SUCCESS,
                        message="Pdfs already present and locked i.e. cannot generate new!",
                        zip_docs_link=f"{pdf_link}",
                    )

                # if not locked, replace the newly generated with exisiting one!

                # Todo: We should not generate the pdf everytime, if record data is not changed! CAN BE IMPLEMENTED LATER...
                file_io_bytes = await self._generate_pdf(
                    record_paylod=form_record.model_dump(),
                    template_name=temp_name,
                    file_path=generated_pdf_path,
                    author=author,
                )

                file_bytes = file_io_bytes.getvalue()

                sign_locations: List[EsignMeta] = self._retrieve_esign_meta(
                    form_record=form_record.model_dump(),
                    template_name=temp_name,
                    form_name="Onboarding",
                )  # Todo: replace 'Onboarding' with form name

                # Add `esign` only if sign_locations is not None
                pdf_meta = DocMeta(
                    org_id=context.org_id,
                    form_id=context.form_id,
                    record_id=record_id,
                    # pdf = doc,
                    digest="",  # TODO: add hash of record too.
                )
                if sign_locations:
                    pdf_meta.esign = Esign(esign_meta=sign_locations)

                # DELETE THE EXISITING DOCS IF ANY BEFORE ADING NEW. TRY TO FIND IT, IF FOUND, DELETE IT!
                pdf_query_data = DocQueryGenericModel(
                    org_id=context.org_id,
                    form_id=context.form_id,
                    record_id=record_id,
                    doc_type="application/pdf",
                )  # doc_type to avoid having other files getting downloaded when fetched!
                doc = await self._upsert_pdf_file(
                    context=context,
                    filename=final_name,
                    file_bytes=file_bytes,
                    meta_data=pdf_meta,
                    update_query_params=pdf_query_data,
                )

                logger.debug(f"Added pdf doc:\n{doc.model_dump()}")

                # GENERATE pdfs for kyc holders, and crerate pdf records for them too, based on sign_locations list.
                await self._generate_individual_pdfs(
                    context=context,
                    record=form_record.model_dump(),
                    record_id=record_id,
                    esigners=sign_locations,
                    temp_name="way2wealth_aof_ind_template",
                    parent_pdf_path=generated_pdf_path,
                    author=author,
                )

                obfus_str = self.obfuscate_string(
                    data_str=f"{pdf_query_data.model_dump_json()}",
                    static_key=config.PDF_GARBLE_KEY,
                )
                # obfus_str = self.obfuscate_string(data_str=f'{pdf_meta.form_id}-{pdf_meta.org_id}-{pdf_meta.record_id}',static_key=config.PDF_GARBLE_KEY)

                api_domain = os.getenv("API_DOMAIN")
                download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
                pdf_link = api_domain + download_doc_endpoint + f"{obfus_str}.zip"
                return GenerateAllDocsResponseModel(
                    status=GenerateAllDocsStatus.SUCCESS,
                    message="Pdfs generated and stored successfully.",
                    zip_docs_link=f"{pdf_link}",
                )

            else:
                """Use generic form template"""
                raise Exception(
                    f'Pdf Template not found corresponding to "{form_temp_name}"'
                )
        except Exception as e:
            logger.exception(e)
            raise PluginException(f"An error occurred while generating PDF!")

    async def generate_main_doc(
        self,
        context: ContextModel,
        record: GenericFormRecordModel,
        record_id: int,
        pdf_name: str | None,
    ) -> io.BytesIO:

        config = context.config
        # TODO : -- ADD METHOD TO DECIDE TEMPLATE NAME BASED ON FORM RECORD STRUCTURE.
        form_temp_name = "aof_form"  # context.form_name
        if form_temp_name is None:
            raise ValueError(
                "Form template is required to generated pdf, otherwise form doesn't support pdf."
            )

        # Initialiazing singleton to use wherever needed later.
        document_plugin_config = DocPluginConfig(context=context)

        logger.debug(
            f"Doc Plugin Config initialized: {document_plugin_config.is_none()}"
        )

        # IF pdf_name NOT PASSED, SET FORM_NAME+RECORDID
        final_name = (
            pdf_name
            if pdf_name
            else f"{context.form_name}".replace(" ", "_")
            + f"{record_id}"
            + f'_{datetime.now().strftime("%H%M%S_%d%m%Y")}'
        )
        if not final_name.lower().endswith(".pdf"):
            final_name += ".pdf"

        current_dir = os.path.dirname(os.path.abspath(__file__))
        generated_pdf_name = os.path.join(current_dir, final_name)

        temp_name = template_dict.get(form_temp_name)
        try:
            author = record.model_dump().get("submitter", {}).get("id", "")

            if temp_name:
                file_io_bytes = await self._generate_pdf(
                    record_paylod=record.model_dump(),
                    template_name=temp_name,
                    file_path=generated_pdf_name,
                    author=author,
                )

                # Return the PDF as a response
                file_io_bytes.seek(0)  # Ensure the stream starts from the beginning

                return file_io_bytes

            else:
                """Use generic form template"""
                raise Exception(
                    f'Pdf Template not found corresponding to "{form_temp_name}"'
                )
        except Exception as e:
            raise PluginException(f"An error occurred while generating PDF!")

    async def generate_doc(
        self,
        context: ContextModel,
        record: GenericFormRecordModel,
        record_id: int,
        params: dict,
    ) -> GenerateAllDocsResponseModel:
        config = context.config

        try:
            # CHECK IF FILES ALREADY PRESENT AND LOCKED.
            # IF YES, DO NOT PROCEED! RETURN success status having message saying existing record found and locked! ALONG WITH EXISING FILES LINK.
            existing_pdfs: List[DBDocumentModel] = await self._get_files_from_db(
                context=context,
                query_params=DocQueryGenericModel(
                    org_id=context.org_id,
                    form_id=context.form_id,
                    record_id=record_id,
                ),
            )

            locked = (
                False if not existing_pdfs else self._check_locked(docs=existing_pdfs)
            )

            pdf_query_data = DocQueryGenericModel(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=record_id,
                doc_type="application/pdf",
            )  # doc_type to avoid having other files getting downloaded when fetched!

            if locked:
                obfus_str = self.obfuscate_string(
                    data_str=f"{pdf_query_data.model_dump_json(exclude_unset=True)}",
                    static_key=config.PDF_GARBLE_KEY,
                )

                api_domain = os.getenv("API_DOMAIN")
                download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
                pdf_link = api_domain + download_doc_endpoint + f"{obfus_str}.zip"
                return GenerateAllDocsResponseModel(
                    status=GenerateAllDocsStatus.SUCCESS,
                    message="Pdfs already present and locked i.e. cannot generate new!",
                    zip_docs_link=f"{pdf_link}",
                )

            # GET THE PDF(S) FROM TRANFORMER PLUGIN.
            generate_docs_res = await invoke.template_generate_pdf(
                config=config,
                org_id=context.org_id,
                form_id=context.form_id,
                template_id=params.get("template_id"),
                record=record,
                params=params,
                form_name=context.form_name,
                additional_args={"record_id": record_id},
            )
            if not generate_docs_res or not isinstance(
                generate_docs_res, TransformerResponseModel
            ):
                raise PluginException("Pdf generation failed!")
            if generate_docs_res.status != TRANSFORMER_RESPONSE_STATUS.SUCCESS:
                return GenerateAllDocsResponseModel(
                    message=generate_docs_res.message,
                    status=GenerateAllDocsStatus.FAILED,
                    zip_docs_link=None,
                )

            # DELETE THE EXISITING DOCS IF ANY, BEFORE ADDING NEW!
            if existing_pdfs:
                for pdf in existing_pdfs:
                    await self._delete_file_from_db(context=context, doc_id=pdf.doc_id)

            # STORE THE PDF(S) IN DB.
            pdfs: List[TemplateDocumentModel] = generate_docs_res.response
            for pdf in pdfs:
                doc = await self._upsert_pdf_file(
                    context=context,
                    filename=pdf.doc_name,
                    file_bytes=pdf.doc_content,
                    meta_data=pdf.metadata,
                )
                logger.debug(f"Added pdf doc:\n{doc.model_dump()}")

            # pdfs_dict: Dict[str, bytes] = generate_docs_res.response

            # pdf_meta = DocMeta(
            #     org_id=context.org_id,
            #     form_id=context.form_id,
            #     record_id=record_id,
            # )
            # for key, value in pdfs_dict.items():

            #     doc = await self._upsert_pdf_file(
            #         context=context,
            #         filename=f'{key}.pdf',
            #         file_bytes=value,
            #         meta_data=pdf_meta,
            #     )
            #     logger.debug(f"Added pdf doc:\n{doc.model_dump()}")

            # PREPARE THE LINK TO DOWNLOAD THE FILES!
            obfus_str = self.obfuscate_string(
                data_str=f"{pdf_query_data.model_dump_json(exclude_unset=True)}",
                static_key=config.PDF_GARBLE_KEY,
            )

            api_domain = os.getenv("API_DOMAIN")
            download_doc_endpoint = config.DOWNLOAD_DOC_API_ENDPOINT
            pdf_link = api_domain + download_doc_endpoint + f"{obfus_str}.zip"
            return GenerateAllDocsResponseModel(
                status=GenerateAllDocsStatus.SUCCESS,
                message="Pdfs generated and stored successfully.",
                zip_docs_link=f"{pdf_link}",
            )

        except Exception as e:
            logger.debug(f"Pdf generation failed! Exception: {e}")
            raise PluginException(
                f"An error occurred while generating PDF!", detailed_message=f"{e}"
            )

    async def _generate_pdf(
        self, record_paylod, template_name: str, file_path: str, author: str = ""
    ):
        """
        Generates the pdf corresponding to template name, and returns the file as bytes.
        """

        # Use AOF form template
        if template_name == "way2wealth_aof_template":
            # logger.debug(f"PDF NAME: {generated_pdf_name}")

            # Tranform to desired json structure
            with importlib.resources.path(
                "lyik.components.way_2_wealth.aof", "desired_form_json.json"
            ) as desired_json_path:
                with open(desired_json_path, "r") as desired_json_file:
                    desired_json_structure = json.load(desired_json_file)
            record_paylod = self._prepare_desired_payload(
                desired_json=desired_json_structure, record_json=record_paylod
            )
            _payload = self.transform_values_to_str(payload=record_paylod)
            pdf_generator = PdfGenerator()
            await pdf_generator.generate_aof(
                pdf_path=file_path, data=_payload, author=author
            )
            file_io_bytes = self._get_file_to_bytes(filename=file_path)
            return file_io_bytes
        # elif template_name == "way2wealth_cetdp_template":
        #     # logger.debug(f"PDF NAME: {generated_pdf_name}")
        #     pdf_generator.generate_cetdp(pdf_name=file_name,data=_payload)
        # elif template_name == "way2wealth_ddpi_template":
        #     # logger.debug(f"PDF NAME: {generated_pdf_name}")
        #     pdf_generator.generate_ddpi(pdf_name=file_name,data=_payload)

    async def _generate_individual_pdfs(
        self,
        context: ContextModel,
        record: dict,
        record_id: int,
        esigners: list[EsignMeta],
        temp_name,
        parent_pdf_path: str,
        author: str = "",
    ):
        """
        Generates, and stores the pdf records for the individual kyc holders.
        Since, the individual pdfs are subset of full pdf, storing same esign meta excpet the signer id.
        """
        pdf_generator = PdfGenerator()

        if temp_name == "way2wealth_aof_ind_template":
            # Generate the pdf for the individual kyc holder
            for index, es in enumerate(esigners):
                # Tranform to desired json structure
                with importlib.resources.path(
                    "lyik.components.way_2_wealth.aof", "desired_form_json.json"
                ) as desired_json_path:
                    with open(desired_json_path, "r") as desired_json_file:
                        desired_json_structure = json.load(desired_json_file)
                record_paylod = self._prepare_desired_payload(
                    desired_json=desired_json_structure, record_json=record
                )
                _payload = self.transform_values_to_str(payload=record_paylod)

                _is_digilocker = (
                    str(
                        _payload.get("application_details", {}).get(
                            "kyc_digilocker", ""
                        )
                    ).lower()
                    != "no"
                )
                _kyc_rec = (
                    _payload.get("kyc_holders", [])[index].get("kyc_holder", {})
                    if index < len(_payload.get("kyc_holders", []))
                    else {}
                )
                _date_of_submission = _payload.get("submitter", {}).get("time", "")
                _pan_no = (
                    _kyc_rec.get("pan_verification", {})
                    .get("pan_details", {})
                    .get("pan_number", "")
                )
                _application_no = _payload.get("_application_id", "")

                # Extract the directory path
                directory = os.path.dirname(parent_pdf_path)

                # Define the new file name
                new_file_name = f"{_pan_no}.pdf"

                # Create the new file path
                file_path = os.path.join(directory, new_file_name)
                await pdf_generator.generate_aof_individual(
                    pdf_path=file_path,
                    kyc_data=_kyc_rec,
                    author=author,
                    application_no=_application_no,
                    is_digilocker=_is_digilocker,
                    date_of_submission=_date_of_submission,
                )
                file_io_bytes = self._get_file_to_bytes(filename=file_path)

                # Insert pdf file to db
                # doc = await self._upsert_pdf_file(db_conn_url=context.config.DB_CONN_URL,filename=file_path.split('/')[-1],file_bytes=file_io_bytes.getvalue())

                # change id and sign location(page number)
                es.id = self._generate_id(length=8)
                es.page_no = "1"
                sign_locations: List[EsignMeta] = [es]

                pdf_meta = DocMeta(
                    org_id=context.org_id,
                    form_id=context.form_id,
                    record_id=record_id,
                    # pdf = doc,
                    digest="",  # TODO: add hash of record too.
                    esign=Esign(
                        esign_meta=sign_locations,
                    ),
                )
                pdf_meta = pdf_meta.model_copy(update={"pan_no": _pan_no})
                # self._upsert_pdf_record(db_conn_url=context.config.DB_CONN_URL,pdf_meta=pdf_meta)
                doc = await self._upsert_pdf_file(
                    context=context,
                    filename=file_path.split("/")[-1],
                    file_bytes=file_io_bytes.getvalue(),
                    meta_data=pdf_meta,
                )
                logger.debug(f"added pdf doc:\n{doc.model_dump()}")

    def _retrieve_esign_meta(
        self, form_record: dict, template_name: str, form_name: str
    ) -> List[EsignMeta]:
        """
        Based on template name, defines the esign meta data.
        """
        sign_locations: List[EsignMeta] = []
        if template_name == "way2wealth_aof_template":
            for index, kyc_data in enumerate(form_record.get("kyc_holders", [])):
                esigner_name = (
                    kyc_data.get("kyc_holder", {})
                    .get("pan_verification", {})
                    .get("pan_details", {})
                    .get("name_in_pan", "")
                )
                try:
                    geocode_location = get_geo_location(
                        lat=(
                            kyc_data.get("liveness_check", {}).get("liveness_geo_loc")
                            if isinstance(
                                kyc_data.get("liveness_check", {}).get(
                                    "liveness_geo_loc"
                                ),
                                dict,
                            )
                            else {}
                        ).get("lat", ""),
                        long=(
                            kyc_data.get("liveness_check", {}).get("liveness_geo_loc")
                            if isinstance(
                                kyc_data.get("liveness_check", {}).get(
                                    "liveness_geo_loc"
                                ),
                                dict,
                            )
                            else {}
                        ).get("long", ""),
                    )
                    esigner_location = (
                        (
                            geocode_location.city_or_county
                            or geocode_location.state
                            or geocode_location.country
                            or ""
                        )
                        if geocode_location
                        else ""
                    )
                except Exception as ex:
                    logger.error(f"Error getting geolocation for {esigner_name}: {ex}")
                    esigner_location = ""  # Earlier it was 'Unknown'
                logger.debug(f"esigner_name: {esigner_name}")
                if esigner_name:
                    sign_locations.append(
                        EsignMeta(
                            xy=("175", "130"),
                            hw=("45", "130"),
                            location=esigner_location,
                            page_no=f"{2*index+3}",
                            name=esigner_name,
                            id=self._generate_id(length=8),
                            reason_for_esign=form_name,
                            sign_status=EsignStatus(status=EsignState.PENDING),
                        )
                    )
        # elif template_name == "way2wealth_cetdp_template":

        return sign_locations

    def _generate_id_hash(data) -> str:
        """
        Generate a robust hash for the given form-record data.
        Args:
            data (dict): The input data to be hashed.
        Returns:
            str: A SHA-256 hash of the normalized data.
        """
        # Ensure the data is sorted to avoid hash inconsistencies due to key order
        normalized_data = json.dumps(data, sort_keys=True, separators=(",", ":"))

        # Create a SHA-256 hash of the normalized data
        hash_object = hashlib.sha256(normalized_data.encode("utf-8"))
        return hash_object.hexdigest()

    def _get_file_to_bytes(self, filename):
        """
        Reads and returns the file as bytes. Also deletes the file from the system.
        """
        with open(filename, "rb") as file:
            file_bytes = io.BytesIO(file.read())
        os.remove(filename)
        return file_bytes

    def transform_values_to_str(self, payload: dict):
        """Transforms the values to strings"""
        if isinstance(payload, dict):
            return {
                key: self.transform_values_to_str(value)
                for key, value in payload.items()
            }
        elif isinstance(payload, list):
            return [self.transform_values_to_str(element) for element in payload]
        elif payload is None:
            return ""
        else:
            return str(payload) if not isinstance(payload, str) else payload

    def _prepare_desired_payload(self, desired_json, record_json):
        """
        Prepares a desired json with desired form record structure by Union(DESIRED_JSON, payload) such a way that reduces exceptions of key not found while pre filling in aof_consts.
        """

        try:
            for key, value in record_json.items():
                if isinstance(value, dict):
                    # If the value is a dictionary, recurse
                    if key not in desired_json or not isinstance(
                        desired_json[key], dict
                    ):
                        desired_json[key] = {}
                    self._prepare_desired_payload(desired_json[key], value)
                elif isinstance(value, list):
                    # If the value is a list, ensure all items have the required keys
                    if key not in desired_json or not isinstance(
                        desired_json[key], list
                    ):
                        desired_json[key] = []

                    # Use the first item of the desired_json list as the template
                    template = desired_json[key][0] if desired_json[key] else {}

                    # Merge each item in the list
                    merged_list = []
                    for item in value:
                        merged_item = (
                            self._prepare_desired_payload(template.copy(), item)
                            if isinstance(item, dict)
                            else item
                        )
                        merged_list.append(merged_item)
                    desired_json[key] = merged_list
                else:
                    # Only update if the value is not None
                    if value is not None:
                        desired_json[key] = value
            return desired_json
        except Exception as e:
            logger.error(f"Exception while converting record data to desired data")
            return record_json

    async def _upsert_pdf_file(
        self,
        context: ContextModel,
        filename: str,
        file_bytes: bytes,
        update_query_params: DocQueryGenericModel | None = None,
        meta_data: DocMeta | None = None,
    ) -> DBDocumentModel:
        """
        Uses doc management plugin to add/update the pdf file in the database.
        If existing_doc_id is passed, then updates the file against that doc id.
        O/w adds a new file.
        """

        doc_model = DocumentModel(
            doc_name=filename,
            doc_type="pdf",
            doc_size=len(file_bytes),
            doc_content=file_bytes,
        )

        if update_query_params:
            document_models: List[DBDocumentModel] = await invoke.updateDocument(
                config=context.config,
                org_id=context.org_id,
                document=doc_model,
                file_id=None,
                coll_name=context.form_id,
                new_metadata=meta_data,
                metadata_params=update_query_params,
            )
            # Todo: validate response!
            return document_models[0]
        else:
            document_model: DBDocumentModel = await invoke.addDocument(
                config=context.config,
                org_id=context.org_id,
                document=doc_model,
                coll_name=context.form_id,
                metadata=meta_data,
            )

            return document_model

    def obfuscate_string(self, data_str: str, static_key: str) -> str:
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

    def _generate_id(self, length=16):
        """
        Generates a random string of Alphanumeric characters of given length.
        """
        characters = string.ascii_letters + string.digits

        # Generate a random string
        random_string = "".join(random.choice(characters) for _ in range(length))

        return random_string

    async def _get_files_from_db(
        self,
        context: ContextModel,
        doc_id: str | None = None,
        query_params: DocQueryGenericModel | None = None,
    ) -> List[DBDocumentModel] | None:
        """
        fetches the files based on metadata, and returns the list of pdf files.
        """

        try:
            docs: List[DBDocumentModel] = await invoke.fetchDocument(
                config=context.config,
                org_id=context.org_id,
                file_id=doc_id,
                coll_name=context.form_id,
                metadata_params=query_params,
            )
            logger.debug(f"{len(docs)} Existing pdf(s) found")
            # return just the pdf files!
            return [doc for doc in docs if "pdf" in doc.metadata.doc_type]
        except Exception as e:
            logger.debug(f"Error finding existing pdfs: {e}.")
            return None

    def _check_locked(self, docs: List[DBDocumentModel]) -> bool:
        try:
            if docs and len(docs) > 0:
                # check if locked i.e. any pdf is in state of esign inprogress or done.

                for existing_pdf in docs:
                    if (
                        existing_pdf.metadata.esign
                        and existing_pdf.metadata.esign.esign_meta
                    ):
                        for em in existing_pdf.metadata.esign.esign_meta:
                            if (
                                em.sign_status.status == EsignState.DONE
                                or em.sign_status.status == EsignState.INPROGRESS
                            ):
                                return True
        except Exception as e:
            return False

        return False

    # def _check_locked(self, docs: List[DBDocumentModel]) -> bool:
    #     if not docs:
    #         return False

    #     try:
    #         for pdf in docs:
    #             if any(em.sign_status.status in {EsignState.DONE, EsignState.PENDING}
    #                 for em in getattr(pdf.metadata.esign, 'esign_meta', [])):
    #                 return True
    #     except Exception:
    #         return False

    #     return False

    async def _delete_file_from_db(self, context: ContextModel, doc_id: str):
        """
        Deletes the file against doc id using Document Management Plugin.
        """

        try:
            await invoke.deleteDocument(
                config=context.config,
                org_id=context.org_id,
                file_id=doc_id,
                coll_name=context.form_id,
                metadata_params=None,
            )
            logger.debug(f"Existing pdf file with doc id - {doc_id} deleted!")
        except Exception as e:
            logger.error(f"Exception in deleting pdf file with doc id - {doc_id}: {e}")


template_dict = {
    "aof_form": "way2wealth_aof_template",
    "aof_form_individual": "way2wealth_aof_ind_template",
    "cet_dp": "way2wealth_cetdp_template",
    "ddpi": "way2wealth_ddpi_template",
}
