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
        if "kyc_holders" not in payload or not payload["kyc_holders"]:
            logger.info(
                "Payload not as expected. Passing through ClientInformation.pre_save_processor_pipeline."
            )
            return payload

        # Extract the first kyc_holder object
        first_kyc_holder = payload["kyc_holders"][0].get("kyc_holder", {})

        if not first_kyc_holder:
            logger.info(
                "No valid 'kyc_holder' found in payload. Passing through ClientInformation.pre_save_processor_pipeline."
            )
            return payload

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

        # Create a dbClient instance with extracted IDs
        db_client = dbClient(
            email=email_contact_id or "anonymous",
            phone=mobile_contact_id or "anonymous",
        )

        # Update the payload with the db_client information
        payload.update({"_client": db_client.dict()})

        return payload




#  Example of expected data structures.
# payload_new = {
#   "kyc_holders": [
#     {
#       "kyc_holder": {
#         "mobile_email_verification": {
#           "mobile_verification": {
#             "dependency_relationship_mobile": null,
#             "contact_id": null,
#             "verified_contact_id": null
#           },
#           "email_verification": {
#             "dependency_relationship_email": null,
#             "contact_id": null,
#             "verified_contact_id": null
#           }
#         },
#         "pan_verification": {
#           "pan_card_image": null,
#           "pan_details": {
#             "name_in_pan": null,
#             "dob_pan": null,
#             "pan_number": null,
#             "parent_guardian_spouse_name": null
#           }
#         },
#         "identity_address_verification": {
#           "identity_address_info": {
#             "pin": null,
#             "state": null,
#             "city": null,
#             "district": null,
#             "country": null,
#             "name_in_aadhaar": null,
#             "gender_aadhaar": null,
#             "aadhaar_number": null,
#             "permanent_address": null
#           },
#           "other_info": {
#             "father_name": null,
#             "marital_status": null,
#             "country_of_birth": null,
#             "mother_name": null,
#             "place_of_birth": null
#           },
#           "same_as_permanent_address": null,
#           "correspondence_address": {
#             "pin_1": null,
#             "state_1": null,
#             "city_1": null,
#             "district_1": null,
#             "country_1": null,
#             "correspondence_address_proof": null,
#             "type_of_address": null,
#             "correspondence_address_1": null
#           }
#         },
#         "signature_validation": {
#           "upload_images": {
#             "wet_signature_image": null,
#             "proof_of_signature": null
#           }
#         },
#         "liveness_check": {
#           "photo_capture": {
#             "liveness_photo": null
#           },
#           "video_capture": {
#             "liveness_video": null
#           },
#           "liveness_captcha": null,
#           "liveness_geo_loc": null
#         },
#         "declarations": {
#           "income_info": {
#             "gross_annual_income": null,
#             "networth": null,
#             "occupation": null,
#             "date": null
#           },
#           "fatca_crs_declaration": {
#             "is_client_tax_resident": null,
#             "place_of_birth_1": null,
#             "country_of_origin": null,
#             "country_code": null
#           },
#           "fatca_crs_declaration_1": {
#             "country_of_residency_1": null,
#             "tin_no_1": null,
#             "id_type_1": null,
#             "reason_if_no_tin_1": null
#           },
#           "fatca_crs_declaration_2": {
#             "country_of_residency_2": null,
#             "tin_no_2": null,
#             "id_type_2": null,
#             "reason_if_no_tin_2": null
#           },
#           "fatca_crs_declaration_3": {
#             "country_of_residency_3": null,
#             "tin_no_3": null,
#             "id_type_3": null,
#             "reason_if_no_tin_3": null
#           },
#           "politically_exposed_person_card": {
#             "politically_exposed_person": null
#           }
#         }
#       }
#     }
#   ]
# }
# test_new = {
#   "onboarding": {
#     "type_of_client": null
#   },
#   "application_details": {
#     "kyc_digilocker": null,
#     "general": {
#       "application_type": null,
#       "residential_status": null
#     },
#     "cash_fut_como_card": {
#       "cash_minimum_paisa": null,
#       "cash_in_percentage": null
#     },
#     "cash_jobbing_card": {
#       "cash_jobbing_minimum_paisa": null,
#       "cash_jobbing_in_percentage": null
#     },
#     "futures_card": {
#       "futures_minimum_paisa": null,
#       "futures_in_percentage": null
#     },
#     "options_card": {
#       "options_standard_rate": null
#     },
#     "currency_futures_card": {
#       "currency_futures_minimum_paisa": null,
#       "currency_futures_in_percentage": null
#     },
#     "currency_options_card": {
#       "currency_options_rate": null
#     },
#     "commodity_futures_card": {
#       "commodity_futures_minimum_paisa": null,
#       "commodity_futures_in_percentage": null
#     },
#     "commodity_options_card": {
#       "commodity_options_rate": null
#     },
#     "slb_card": {
#       "slb_rate": null
#     },
#     "flat_per_order_card": {
#       "flat_per_order_rate": null
#     },
#     "online_exe_card": {
#       "online_exe": null
#     },
#     "gst_details_card": {
#       "gst_number": null
#     }
#   },
#   "kyc_holders": [
#     {
#       "kyc_holder": {
#         "mobile_email_verification": {
#           "mobile_verification": {
#             "dependency_relationship_mobile": null,
#             "contact_id": null,
#             "verified_contact_id": null
#           },
#           "email_verification": {
#             "dependency_relationship_email": null,
#             "contact_id": null,
#             "verified_contact_id": null
#           }
#         },
#         "pan_verification": {
#           "pan_card_image": null,
#           "pan_details": {
#             "name_in_pan": null,
#             "dob_pan": null,
#             "pan_number": null,
#             "parent_guardian_spouse_name": null
#           }
#         },
#         "identity_address_verification": {
#           "identity_address_info": {
#             "pin": null,
#             "state": null,
#             "city": null,
#             "district": null,
#             "country": null,
#             "name_in_aadhaar": null,
#             "gender_aadhaar": null,
#             "aadhaar_number": null,
#             "permanent_address": null
#           },
#           "other_info": {
#             "father_name": null,
#             "marital_status": null,
#             "country_of_birth": null,
#             "mother_name": null,
#             "place_of_birth": null
#           },
#           "same_as_permanent_address": null,
#           "correspondence_address": {
#             "pin_1": null,
#             "state_1": null,
#             "city_1": null,
#             "district_1": null,
#             "country_1": null,
#             "correspondence_address_proof": null,
#             "type_of_address": null,
#             "correspondence_address_1": null
#           }
#         },
#         "signature_validation": {
#           "upload_images": {
#             "wet_signature_image": null,
#             "proof_of_signature": null
#           }
#         },
#         "liveness_check": {
#           "photo_capture": {
#             "liveness_photo": null
#           },
#           "video_capture": {
#             "liveness_video": null
#           },
#           "liveness_captcha": null,
#           "liveness_geo_loc": null
#         },
#         "declarations": {
#           "income_info": {
#             "gross_annual_income": null,
#             "networth": null,
#             "occupation": null,
#             "date": null
#           },
#           "fatca_crs_declaration": {
#             "is_client_tax_resident": null,
#             "place_of_birth_1": null,
#             "country_of_origin": null,
#             "country_code": null
#           },
#           "fatca_crs_declaration_1": {
#             "country_of_residency_1": null,
#             "tin_no_1": null,
#             "id_type_1": null,
#             "reason_if_no_tin_1": null
#           },
#           "fatca_crs_declaration_2": {
#             "country_of_residency_2": null,
#             "tin_no_2": null,
#             "id_type_2": null,
#             "reason_if_no_tin_2": null
#           },
#           "fatca_crs_declaration_3": {
#             "country_of_residency_3": null,
#             "tin_no_3": null,
#             "id_type_3": null,
#             "reason_if_no_tin_3": null
#           },
#           "politically_exposed_person_card": {
#             "politically_exposed_person": null
#           }
#         }
#       }
#     }
#   ],
#   "bank_verification": {
#     "bank_details": {
#       "bank_account_number": null,
#       "account_holder_name": null,
#       "branch_code": null,
#       "ifsc_code": null
#     },
#     "cancelled_cheque": {
#       "cancelled_cheque_image": null
#     }
#   },
#   "nomination_details": {
#     "general": {
#       "client_nominee_appointment_status": null
#     },
#     "nominees": [
#       {
#         "nominee": {
#           "nominee_data": {
#             "minor_nominee": null,
#             "nominee_type_of_id": null,
#             "name_of_nominee": null,
#             "percentage_of_allocation": null,
#             "nominee_id_proof": null,
#             "id_number": null,
#             "dob_nominee": null,
#             "nominee_address": null
#           },
#           "guardian_data": {
#             "guardian_id_proof": null,
#             "guardian_type_of_id": null,
#             "guardian_name": null,
#             "guardian_address": null,
#             "guardian_signature": null,
#             "guardian_id_number": null,
#             "relationship_with_nominee": null
#           }
#         }
#       }
#     ]
#   },
#   "trading_information": {
#     "check_pan_for_trading_account": {
#       "trading_id": null,
#       "account_holder_name": null,
#       "account_creation_date": null
#     },
#     "trading_account_information": {
#       "segment_pref_1": null,
#       "segment_pref_2": null,
#       "segment_pref_3": null,
#       "segment_pref_4": null,
#       "segment_pref_5": null,
#       "segment_pref_6": null,
#       "type_of_document": null,
#       "contract_format_1": null,
#       "contract_format_2": null,
#       "proof_of_income": null,
#       "client_facility_choice": null,
#       "kit_format_1": null,
#       "kit_format_2": null,
#       "holder_trading_experience": null,
#       "state": null
#     },
#     "employer_details": {
#       "employer_name": null,
#       "mobile_number": null,
#       "approval_date": null,
#       "employer_address": null
#     },
#     "details_of_dealings": {
#       "broker_name": null,
#       "telephone": null,
#       "client_codes": null,
#       "broker_address": null,
#       "sub_broker_name": null,
#       "website": null,
#       "detail_of_disputes": null
#     },
#     "introducer_details": {
#       "introducer_name": null,
#       "introducer_broker_address": null,
#       "introducer_status": null,
#       "remisire_code": null
#     }
#   },
#   "dp_information": {
#     "dp_Account_information": {
#       "dp_tariff_plan": null,
#       "name_of_dp": null,
#       "depository": null,
#       "dp_id_no": null,
#       "client_id_no": null,
#       "cmr_file": null
#     },
#     "standing_info_from_client": {
#       "receive_credit_auth_status": null,
#       "first_holder_sms_alert": null,
#       "joint_holder_sms_alert": null,
#       "account_statement_requirement": null,
#       "electronic_transaction_holding_statement": null,
#       "dividend_interest_receive_option": null,
#       "auto_pledge_confirmation": null,
#       "did_booklet_issuance": null,
#       "bsda": null,
#       "joint_account_operation_mode": null,
#       "consent_for_communication": null,
#       "share_email_id_with_rta": null,
#       "receive_annual_report": null,
#       "aadhaar_pan_seed_status": null,
#       "trust": null
#     },
#     "trust_information": {
#       "stack_exchange_name": null,
#       "clearing_member_name": null,
#       "clearing_member_id": null
#     },
#     "ucc_mapping_1": {
#       "ucc_code_1": null,
#       "exchange_id_1": null,
#       "segment_id_1": null,
#       "cm_id_1": null,
#       "tm_id_1": null
#     },
#     "ucc_mapping_2": {
#       "ucc_code_2": null,
#       "exchange_id_2": null,
#       "segment_id_2": null,
#       "cm_id_2": null,
#       "tm_id_2": null
#     }
#   },
#   "tnc_info_pane": {
#     "declaration": {
#       "sms_alert": null,
#       "policy": null,
#       "processing_time": null
#     }
#   }
# }

