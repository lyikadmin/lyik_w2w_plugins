import logging
from typing import Dict
from pydantic import Field, BaseModel

import apluggy as pluggy
import jwt
import jwt.exceptions
from lyikpluginmanager import (
    getProjectName,
    PreSaveProcessorPipelineSpec,
    ContextModel,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())


class dbClient(BaseModel):
    """
    Data model storing the details of a records client
    """

    phone: str = Field(None, description="Phone number of the client")
    email: str = Field(None, description="Email id of the client")


class ClientInformation(PreSaveProcessorPipelineSpec):
    @impl
    async def pre_save_processor_pipeline(
        self, context: ContextModel | None, payload: Dict
    ) -> Dict:
        # Check existence and validity of 'kyc_holders'
        if "kyc_holders" not in payload or not payload["kyc_holders"].get("kyc_holder"):
            logger.info(
                "Payload not as expected. Passing through ClientInformation.pre_save_processor_pipeline."
            )
            return payload

        # Extract the first element of the kyc_holder list
        first_kyc_holder = payload["kyc_holders"]["kyc_holder"][0]

        # Retrieve email and mobile contact IDs
        email_contact_id = (
            first_kyc_holder.get("mobile_email_verification", {})
            .get("email_verification", {})
            .get("contact_id")
        )
        mobile_contact_id = (
            first_kyc_holder.get("mobile_email_verification", {})
            .get("mobile_verification", {})
            .get("contact_id")
        )

        db_client = dbClient(
            email=email_contact_id or "anonymous",
            phone=mobile_contact_id or "anonymous",
        )

        payload.update({"_client": db_client.dict()})

        return payload


payload = {
    "kyc_holders": {
        "kyc_holder": [
            {
                "mobile_email_verification": {
                    "mobile_verification": {
                        "dependency_relationship_mobile": "",
                        "contact_id": "12345612345123",
                        "verified_contact_id": "",
                    },
                    "email_verification": {
                        "dependency_relationship_email": "",
                        "contact_id": "test_email@gmai.com",
                        "verified_contact_id": "",
                    },
                }
            }
        ]
    }
}

test_original = {
    "onboarding": {"type_of_client": ""},
    "application_details": {
        "kyc_digilocker": "",
        "general": {"application_type": "", "residential_status": ""},
        "cash_fut_como_card": {"cash_minimum_paisa": "", "cash_in_percentage": ""},
        "cash_jobbing_card": {
            "cash_jobbing_minimum_paisa": "",
            "cash_jobbing_in_percentage": "",
        },
        "futures_card": {"futures_minimum_paisa": "", "futures_in_percentage": ""},
        "options_card": {"options_standard_rate": ""},
        "currency_futures_card": {
            "currency_futures_minimum_paisa": "",
            "currency_futures_in_percentage": "",
        },
        "currency_options_card": {"currency_options_rate": ""},
        "commodity_futures_card": {
            "commodity_futures_minimum_paisa": "",
            "commodity_futures_in_percentage": "",
        },
        "commodity_options_card": {"commodity_options_rate": ""},
        "slb_card": {"slb_rate": ""},
        "flat_per_order_card": {"flat_per_order_rate": ""},
        "online_exe_card": {"online_exe": ""},
    },
    "kyc_holders": {
        "kyc_holder": [
            {
                "mobile_email_verification": {
                    "mobile_verification": {
                        "dependency_relationship_mobile": "",
                        "contact_id": "",
                        "verified_contact_id": "",
                    },
                    "email_verification": {
                        "dependency_relationship_email": "",
                        "contact_id": "",
                        "verified_contact_id": "",
                    },
                },
                "pan_verification": {
                    "pan_card_image": "",
                    "pan_details": {
                        "name_in_pan": "",
                        "dob_pan": "",
                        "pan_number": "",
                        "parent_guardian_spouse_name": "",
                    },
                },
                "identity_address_verification": {
                    "identity_address_info": {
                        "pin": "",
                        "state": "",
                        "city": "",
                        "district": "",
                        "country": "",
                        "name_in_aadhaar": "",
                        "gender_aadhaar": "",
                        "aadhaar_number": "",
                        "permanent_address": "",
                    },
                    "other_info": {
                        "father_name": "",
                        "marital_status": "",
                        "country_of_birth": "",
                        "mother_name": "",
                        "place_of_birth": "",
                    },
                    "same_as_permanent_address": "",
                    "correspondence_address": {
                        "pin_1": "",
                        "state_1": "",
                        "city_1": "",
                        "district_1": "",
                        "country_1": "",
                        "correspondence_address_proof": "",
                        "type_of_address": "",
                        "correspondence_address_1": "",
                    },
                },
                "signature_validation": {
                    "upload_images": {
                        "wet_signature_image": "",
                        "proof_of_signature": "",
                    }
                },
                "liveness_check": {
                    "photo_capture": {"liveness_photo": ""},
                    "video_capture": {"liveness_video": ""},
                    "liveness_captcha": "",
                    "liveness_geo_loc": "",
                },
                "declarations": {
                    "income_info": {
                        "gross_annual_income": "",
                        "networth": "",
                        "occupation": "",
                        "date": "",
                    },
                    "fatca_crs_declaration": {"is_client_tax_resident": ""},
                    "fatca_crs_declaration_1": {
                        "country_of_residency_1": "",
                        "tin_no_1": "",
                        "id_type_1": "",
                        "reason_if_no_tin_1": "",
                    },
                    "fatca_crs_declaration_2": {
                        "country_of_residency_2": "",
                        "tin_no_2": "",
                        "id_type_2": "",
                        "reason_if_no_tin_2": "",
                    },
                    "fatca_crs_declaration_3": {
                        "country_of_residency_3": "",
                        "tin_no_3": "",
                        "id_type_3": "",
                        "reason_if_no_tin_3": "",
                    },
                    "politically_exposed_person_card": {
                        "politically_exposed_person": ""
                    },
                },
            }
        ]
    },
    "bank_verification": {
        "bank_details": {
            "bank_account_number": "",
            "account_holder_name": "",
            "branch_code": "",
            "ifsc_code": "",
        },
        "cancelled_cheque": {"cancelled_cheque_image": ""},
    },
    "nomination_details": {
        "general": {"client_nominee_appointment_status": ""},
        "nominees": {
            "nominee": [
                {
                    "nominee_data": {
                        "minor_nominee": "",
                        "nominee_type_of_id": "",
                        "name_of_nominee": "",
                        "percentage_of_allocation": "",
                        "nominee_id_proof": "",
                        "id_number": "",
                        "dob_nominee": "",
                        "nominee_address": "",
                    },
                    "guardian_data": {
                        "guardian_id_proof": "",
                        "guardian_type_of_id": "",
                        "guardian_name": "",
                        "guardian_address": "",
                        "guardian_signature": "",
                        "guardian_id_number": "",
                        "relationship_with_nominee": "",
                    },
                }
            ]
        },
    },
    "trading_information": {
        "check_pan_for_trading_account": {
            "trading_id": "",
            "account_holder_name": "",
            "account_creation_date": "",
        },
        "trading_account_information": {
            "segment_pref_1": "",
            "segment_pref_2": "",
            "segment_pref_3": "",
            "segment_pref_4": "",
            "segment_pref_5": "",
            "segment_pref_6": "",
            "type_of_document": "",
            "contract_format_1": "",
            "contract_format_2": "",
            "proof_of_income": "",
            "client_facility_choice": "",
            "kit_format_1": "",
            "kit_format_2": "",
            "holder_trading_experience": "",
            "state": "",
        },
        "employer_details": {
            "employer_name": "",
            "mobile_number": "",
            "approval_date": "",
            "employer_address": "",
        },
        "details_of_dealings": {
            "broker_name": "",
            "telephone": "",
            "client_codes": "",
            "broker_address": "",
            "sub_broker_name": "",
            "website": "",
            "detail_of_disputes": "",
        },
        "introducer_details": {
            "introducer_name": "",
            "introducer_broker_address": "",
            "introducer_status": "",
            "remisire_code": "",
        },
    },
    "dp_information": {
        "dp_Account_information": {
            "dp_tariff_plan": "",
            "name_of_dp": "",
            "depository": "",
            "dp_id_no": "",
            "client_id_no": "",
            "cmr_file": "",
        },
        "standing_info_from_client": {
            "receive_credit_auth_status": "",
            "first_holder_sms_alert": "",
            "joint_holder_sms_alert": "",
            "account_statement_requirement": "",
            "electronic_transaction_holding_statement": "",
            "dividend_interest_receive_option": "",
            "auto_pledge_confirmation": "",
            "did_booklet_issuance": "",
            "bsda": "",
            "joint_account_operation_mode": "",
            "consent_for_communication": "",
            "share_email_id_with_rta": "",
            "receive_annual_report": "",
            "aadhaar_pan_seed_status": "",
            "trust": "",
        },
        "trust_information": {
            "stack_exchange_name": "",
            "clearing_member_name": "",
            "clearing_member_id": "",
        },
        "ucc_mapping_1": {
            "ucc_code_1": "",
            "exchange_id_1": "",
            "segment_id_1": "",
            "cm_id_1": "",
            "tm_id_1": "",
        },
        "ucc_mapping_2": {
            "ucc_code_2": "",
            "exchange_id_2": "",
            "segment_id_2": "",
            "cm_id_2": "",
            "tm_id_2": "",
        },
    },
    "tnc_info_pane": {
        "declaration": {"sms_alert": "", "policy": "", "processing_time": ""}
    },
}
