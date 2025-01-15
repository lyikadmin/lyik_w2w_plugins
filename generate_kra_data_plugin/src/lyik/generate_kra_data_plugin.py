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
)
import json
import os
import importlib


impl = pluggy.HookimplMarker(getProjectName())


class GenerateKRADataPlugin(KRATranslatorSpec):

    @impl
    async def translate_to_kra(self, context, kyc_holder):
        POS_CODE = os.getenv("POSCODE")
        # Iterate over each KYC holder in the list
        now = datetime.now().strftime("%d/%m/%Y")
        kyc_holder = kyc_holder.get("kyc_holder")
        pan_verification = kyc_holder.get("pan_verification", {}).get(
            "pan_details", {}
        )
        identity_verification = kyc_holder.get("identity_address_verification", {})
        declarations = kyc_holder.get("declarations", {})

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
            APP_PAN_NO=pan_verification.get("pan_number"),
            APP_PAN_COPY="Y",
            APP_EXMT="N",
            APP_EXMT_CAT="",
            APP_EXMT_ID_PROOF="1",
            APP_IPV_FLAG="Y",
            APP_IPV_DATE=now,
            APP_GEN=identity_verification.get("identity_address_info", {}).get(
                "gender_aadhaar"
            ),
            APP_NAME=identity_verification.get("identity_address_info", {}).get(
                "name_in_aadhaar"
            ),
            APP_F_NAME=identity_verification.get("other_info", {}).get(
                "father_name"
            ),
            APP_REGNO="",
            APP_DOB_INCORP=pan_verification.get("dob_pan"),
            APP_COMMENCE_DT="",
            APP_NATIONALITY=self.get_nationality_code(
                identity_verification.get("identity_address_info", {}).get(
                    "country"
                )
            ),
            APP_OTH_NATIONALITY="",
            APP_COMP_STATUS="",
            APP_OTH_COMP_STATUS="",
            APP_RES_STATUS=self.get_residential_status(
                declarations.get("fatca_crs_declaration", {}).get(
                    "is_client_tax_resident"
                )
            ),  ##
            APP_RES_STATUS_PROOF=None,
            APP_UID_NO=None,
            APP_COR_ADD1=identity_verification.get(
                "correspondence_address", {}
            ).get("correspondence_address"),
            APP_COR_ADD2="",
            APP_COR_ADD3="",
            APP_COR_CITY=identity_verification.get(
                "correspondence_address", {}
            ).get("city"),
            APP_COR_PINCD=identity_verification.get(
                "correspondence_address", {}
            ).get("pin"),
            APP_COR_STATE=self.get_state_code(
                identity_verification.get("correspondence_address", {}).get("state")
            ),
            APP_COR_CTRY=self.get_country_code(
                identity_verification.get("correspondence_address", {}).get(
                    "country"
                )
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
            APP_COR_ADD_REF=self.get_aadhaar_last_4_digit(
                identity_verification.get("identity_address_info", {}).get(
                    "aadhaar_number"
                )
            ),
            APP_COR_ADD_DT="",
            APP_PER_ADD_FLAG=self.get_per_add_flag_code(
                identity_verification.get("same_as_permanent_address")
            ),
            APP_PER_ADD1=identity_verification.get("identity_address_info", {}).get(
                "permanent_address"
            ),
            APP_PER_ADD2="",
            APP_PER_ADD3="",
            APP_PER_CITY=identity_verification.get("identity_address_info", {}).get(
                "city"
            ),
            APP_PER_PINCD=identity_verification.get(
                "identity_address_info", {}
            ).get("pin"),
            APP_PER_STATE=self.get_state_code(
                identity_verification.get("identity_address_info", {}).get("state")
            ),
            APP_PER_CTRY=self.get_country_code(
                identity_verification.get("identity_address_info", {}).get(
                    "country"
                )
            ),
            APP_PER_ADD_PROOF=self.get_corr_addr_proof_code("AADHAAR"),
            APP_PER_ADD_REF=self.get_aadhaar_last_4_digit(
                identity_verification.get("identity_address_info", {}).get(
                    "aadhaar_number"
                )
            ),
            APP_PER_ADD_DT="",
            APP_INCOME="",
            APP_OCC="",
            APP_OTH_OCC="",
            APP_POL_CONN="",
            APP_DOC_PROOF="S",  ##
            APP_INTERNAL_REF="",
            APP_BRANCH_CODE="",
            APP_MAR_STATUS=self.get_marital_status_code(
                identity_verification.get("other_info", {}).get("marital_status")
            ),
            APP_NETWRTH=None,
            APP_NETWORTH_DT="",
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
            APP_FATCA_APPLICABLE_FLAG="N",
            APP_FATCA_BIRTH_PLACE="",
            APP_FATCA_BIRTH_COUNTRY="",
            APP_FATCA_COUNTRY_RES=None,
            APP_FATCA_COUNTRY_CITYZENSHIP="",
            APP_FATCA_DATE_DECLARATION=now,
        )

        fatca_details = FATCAAddlDtls(
            APP_FATCA_ENTITY_PAN="",
            APP_FATCA_COUNTRY_RESIDENCY=None,
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
        return {"ROOT": root.model_dump()}

    def get_nationality_code(self, country_name: str) -> str:
        if country_name.lower() == "India".lower():
            return "01"
        else:
            return "02"

    def get_residential_status(self, is_tax_resident: str) -> str:
        if is_tax_resident.lower() == "Yes".lower():
            return "R"
        else:
            return "N"

    def get_country_code(self, country_name: str) -> str:
        with importlib.resources.path("lyik", "country.json") as file_path:
            country_mapping = self.load_mapping_file(file_path)
            return country_mapping.get(country_name)

    def get_state_code(self, state: str) -> str:
        with importlib.resources.path("lyik", "states.json") as file_path:
            state_mapping = self.load_mapping_file(file_path)
            return state_mapping.get(state)

    def get_corr_addr_proof_code(self, addr_proof: str) -> str:
        with importlib.resources.path("lyik", "corr_address_proof.json") as file_path:
            addr_proof_mapping = self.load_mapping_file(file_path)
            return addr_proof_mapping.get(addr_proof)

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

    def load_mapping_file(self, file_path: str) -> dict:
        with open(file_path, "r") as file:
            return json.load(file)
