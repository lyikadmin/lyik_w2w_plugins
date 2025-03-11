import apluggy as pluggy
from datetime import datetime
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    KRATranslatorSpec,
    ROOT,
    KYCData,
    Header,
    Footer,
    FATCAAddlDtls,
    ROOTDataModel,
    GenericKYCData,
)
import json
import os
from importlib import resources
from .model import KYCDataModel, Declarations
from typing import Dict, Any, List, Annotated
from typing_extensions import Doc

import re
from dotenv import load_dotenv

load_dotenv()


impl = pluggy.HookimplMarker(getProjectName())


class GenerateKRADataPlugin(KRATranslatorSpec):
    """
    Plugin for translating KYC holder data to the KRA format.
    This class implements the KRATranslatorSpec interface and provides
    structured mapping of input data to the required KRA format.
    """

    # class attribute (cache) for storing mapping files data
    country_mapping = None
    fatca_country_mapping = None
    state_mapping = None
    addr_proof_mapping = None

    @impl
    async def translate_to_kra(
        self,
        context: ContextModel,
        kyc_holder: Annotated[GenericKYCData, Doc("Kyc holder data")],
    ) -> Annotated[ROOTDataModel, Doc("ROOT model will be returned")]:
        """
        Translates KYC holder data to the KRA format.

        Args:
            context (ContextModel): The execution context.
            kyc_holder (dict): Dictionary containing KYC holder data.

        Returns:
            dict: Translated data in KRA format.
        """
        POS_CODE = os.getenv("POSCODE")
        # Iterate over each KYC holder in the list
        now = datetime.now().strftime("%d/%m/%Y")

        # Parse the data into the Pydantic model
        # parsed_data = KYCDataModel(**kyc_holder)
        parsed_data: KYCDataModel = KYCDataModel(**kyc_holder.model_dump())

        # kyc_holder = parsed_data
        pan_details = parsed_data.kyc_holder.pan_verification.pan_details
        identity_address__verification = (
            parsed_data.kyc_holder.identity_address_verification
        )
        declarations = parsed_data.kyc_holder.declarations

        header = Header(
            COMPANY_CODE=POS_CODE,
            BATCH_DATE=now,
        )

        kyc_data = KYCData(
            APP_UPDTFLG="01",
            APP_KRA_CODE="CVLKRA",
            APP_POS_CODE=POS_CODE,
            APP_TYPE="I",
            APP_NO="",
            APP_DATE=now,
            APP_PAN_NO=pan_details.pan_number,
            APP_PAN_COPY="Y",
            APP_EXMT="N",
            APP_EXMT_CAT="",
            APP_EXMT_ID_PROOF="1",
            APP_IPV_FLAG="Y",
            APP_IPV_DATE=now,
            APP_GEN=identity_address__verification.identity_address_info.gender,
            APP_NAME=identity_address__verification.identity_address_info.name,
            APP_F_NAME=identity_address__verification.other_info.father_name,
            APP_REGNO="",
            APP_DOB_INCORP=pan_details.dob_pan,
            APP_COMMENCE_DT="",
            APP_NATIONALITY=self.get_nationality_code(
                identity_address__verification.identity_address_info.country
            ),
            APP_OTH_NATIONALITY="",
            APP_COMP_STATUS="",
            APP_OTH_COMP_STATUS="",
            APP_RES_STATUS=self.get_residential_status(
                declarations.fatca_crs_declaration.is_client_tax_resident
            ),  ##
            APP_RES_STATUS_PROOF=None,
            APP_UID_NO=None,
            APP_COR_ADD1=identity_address__verification.correspondence_address.full_address,
            APP_COR_ADD2="",
            APP_COR_ADD3="",
            APP_COR_CITY=identity_address__verification.identity_address_info.city,
            APP_COR_PINCD=identity_address__verification.identity_address_info.pin,
            APP_COR_STATE=self.get_state_code(
                identity_address__verification.identity_address_info.state
            ),
            APP_COR_CTRY=self.get_country_code(
                identity_address__verification.identity_address_info.country
            ),
            APP_OFF_ISD=None,
            APP_OFF_STD=None,
            APP_OFF_NO=None,
            APP_RES_ISD=None,
            APP_RES_STD=None,
            APP_RES_NO=None,
            APP_MOB_ISD=None,
            APP_MOB_NO=None,
            APP_FAX_ISD=None,
            APP_FAX_STD=None,
            APP_FAX_NO=None,
            APP_EMAIL=None,
            APP_COR_ADD_PROOF=self.get_corr_addr_proof_code(
                # identity_verification.get("correspondence_address", {}).get(
                #     "correspondence_address_proof"
                # )
                "AADHAAR"
            ),
            APP_COR_ADD_REF="",
            APP_COR_ADD_DT="",
            APP_PER_ADD_FLAG=self.get_per_add_flag_code(
                identity_address__verification.same_as_permanent_address
            ),
            APP_PER_ADD1=identity_address__verification.identity_address_info.full_address,
            APP_PER_ADD2="",
            APP_PER_ADD3="",
            APP_PER_CITY=identity_address__verification.identity_address_info.city,
            APP_PER_PINCD=identity_address__verification.identity_address_info.pin,
            APP_PER_STATE=self.get_state_code(
                identity_address__verification.identity_address_info.state
            ),
            APP_PER_CTRY=self.get_country_code(
                identity_address__verification.identity_address_info.country
            ),
            APP_PER_ADD_PROOF=self.get_corr_addr_proof_code("AADHAAR"),
            APP_PER_ADD_REF="",
            APP_PER_ADD_DT="",
            APP_INCOME="",  ##
            APP_OCC="",  ##
            APP_OTH_OCC="",  ##
            APP_POL_CONN="",  ##
            APP_DOC_PROOF="S",  ##
            APP_INTERNAL_REF="",
            APP_BRANCH_CODE="",
            APP_MAR_STATUS=self.get_marital_status_code(
                identity_address__verification.other_info.marital_status
            ),
            APP_NETWRTH=None,  ##
            APP_NETWORTH_DT="",  ##
            APP_INCORP_PLC="",
            APP_OTHERINFO="",
            APP_FILLER1="",
            APP_FILLER2="",
            APP_FILLER3="",
            APP_IPV_NAME="",
            APP_IPV_DESG="",
            APP_IPV_ORGAN="",
            APP_KYC_MODE=self.get_app_kyc_mode("Digilocker"),
            APP_VER_NO="",
            APP_VID_NO="",
            APP_UID_TOKEN="",
            APP_AUTH_NAME="",
            APP_AUTH_EMAIL="",
            APP_AUTH_EMAIL1="",
            APP_AUTH_EMAIL2="",
            APP_AUTH_MOBILE="",
            APP_AUTH_FPICONSENT="",
            APP_AUTH_UBOCONSENT="",
            APP_FATCA_APPLICABLE_FLAG=self.get_fatca_applicable_flag(
                is_tax_resident=declarations.fatca_crs_declaration.is_client_tax_resident
            ),
            APP_FATCA_BIRTH_PLACE=declarations.fatca_crs_declaration.place_of_birth,
            APP_FATCA_BIRTH_COUNTRY=self.get_fatca_country_code(
                identity_address__verification.other_info.country_of_birth
            ),
            APP_FATCA_COUNTRY_CITYZENSHIP=self.get_fatca_country_origin(
                is_indian_citizen=declarations.fatca_crs_declaration.is_client_tax_resident,
                declarations= declarations
            ),
            APP_FATCA_COUNTRY_RES=None,
            APP_FATCA_DATE_DECLARATION=now,
        )

        fatca_details = FATCAAddlDtls(
            APP_FATCA_ENTITY_PAN="",
            APP_FATCA_COUNTRY_RESIDENCY="",
            APP_FATCA_TAX_IDENTIFICATION_NO="",
            APP_FATCA_TAX_EXEMPT_FLAG="",
            APP_FATCA_TAX_EXEMPT_REASON="",
        )

        footer = Footer(
            NO_OF_KYC_RECORDS="1",
            NO_OF_ADDLDATA_RECORDS="0",
            NO_OF_FATCA_ADDL_DTLS_RECORDS="0",
        )

        root = ROOT(
            HEADER=header,
            KYCDATA=kyc_data,
            FATCA_ADDL_DTLS=fatca_details,
            FOOTER=footer,
        )
        return ROOTDataModel(root_data=root)

    def get_nationality_code(self, country_name: str) -> str:
        if country_name:
            if country_name.lower() == "India".lower():
                return "01"
            else:
                return "02"

    def get_residential_status(self, is_tax_resident: str) -> str:
        if is_tax_resident.lower() == "Yes".lower():
            return "R"
        else:
            return "N"

    def get_fatca_applicable_flag(self, is_tax_resident: str):
        if is_tax_resident.lower() == "yes":
            return "N"
        else:
            return "Y"

    def get_country_code(self, country_name: str) -> str:
        if self.country_mapping is None:
            self.country_mapping = self.load_mapping_file(file_name="country.json")
        return self.country_mapping.get(country_name)

    def get_state_code(self, state: str) -> str:
        if self.state_mapping is None:
            self.state_mapping = self.load_mapping_file(file_name="states.json")
        return self.state_mapping.get(state)

    def get_corr_addr_proof_code(self, addr_proof: str) -> str:
        if self.addr_proof_mapping is None:
            self.addr_proof_mapping = self.load_mapping_file(
                file_name="corr_address_proof.json"
            )
        return self.addr_proof_mapping.get(addr_proof)

    def get_aadhaar_last_4_digit(self, aadhaar_number: str) -> str:
        if aadhaar_number[-4:].isdigit():
            return aadhaar_number[-4:]
        else:
            raise ValueError(
                "Invalid Aadhaar number. The last 4 characters must be digits."
            )

    def get_per_add_flag_code(self, same_as_permanent_add: str) -> str:
        if same_as_permanent_add.lower() == "SAME_AS_PERMANENT_ADDRESS".lower():
            return "Y"
        else:
            return "N"

    def get_marital_status_code(self, status: str) -> str:
        marital_status_mapping = {"MARRIED": "1", "SINGLE": "2"}
        return marital_status_mapping.get(status)

    def get_app_kyc_mode(self, mode=str) -> str:
        kyc_mode_mapping = {
            "Normal KYC": "0",
            "e-KYC with OTP": "1",
            "e-KYC with Biometric": "2",
            "Online Data Entry and IPV": "3",
            "Offline KYC - Aadhaar": "4",
            "Digilocker": "5",
            "SARAL": "6",
        }

        return kyc_mode_mapping.get(mode)

    def load_mapping_file(self, file_name: str) -> dict:
        with resources.path("lyik", file_name) as file_path:
            with open(file_path, "r") as file:
                return json.load(file)

    def get_fatca_country_code(self, country_name: str) -> str:
        """Match user input with the correct FATCA country code and display the normalized value."""
        normalized_input = country_name.upper().strip()
        normalized_input = re.sub(r"[^A-Z\s]", "", normalized_input)
        if self.fatca_country_mapping is None:
            self.fatca_country_mapping = self.load_mapping_file(
                file_name="fatca_country_code.json"
            )

        # Direct match
        if normalized_input in self.fatca_country_mapping:
            return self.fatca_country_mapping[normalized_input]

        # Try fuzzy matching by checking substrings
        for country_name, code in self.fatca_country_mapping.items():
            if normalized_input in country_name or country_name in normalized_input:
                return code
        return ""

    def get_fatca_country_origin(
        self, is_indian_citizen: str, declarations: Declarations
    ):
        """"""
        try:
            country = None
            if is_indian_citizen.lower() == "yes":
                country = "India"
            else:
                if declarations.fatca_crs_declaration_1 is not None and declarations.fatca_crs_declaration_1.country_of_residency_1 is not None:
                    country = declarations.fatca_crs_declaration_1.country_of_residency_1
            if country is not None:
                return self.get_fatca_country_code(country_name=country)
            else:
                raise ValueError("Country is not available")        
        except Exception as e:
            print(f"Error in getting FATCA country origin: {e}")
            return ""
