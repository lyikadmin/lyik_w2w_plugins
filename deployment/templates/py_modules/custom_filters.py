from __future__ import annotations

import logging
from typing import Any, Dict, List
from datetime import datetime

from aof import (
    AofModel,
    RootOnboarding,
    RootApplicationDetails,
    FieldGrpRootKycHolders,
    W2WMARITALSTATUS,
    RootBankVerification,
    RootNominationDetails,
    RootTradingInformation,
    RootDpInformation,
    RootTnc,
    GENDER,
    MINORNOMINEE,
)
import jwt


def current_date():
    #     return date in DD/MM/YYYY format
    from datetime import datetime

    return datetime.now().strftime("%d/%m/%Y")


def exchange_list(form: AofModel) -> str:
    exchanges = set()
    if (
        form.trading_information
        and form.trading_information.trading_account_information
    ):
        tai = form.trading_information.trading_account_information
        segments = [
            segment.value
            for segment in [
                tai.segment_pref_1,
                tai.segment_pref_2,
                tai.segment_pref_3,
                tai.segment_pref_4,
                tai.segment_pref_5,
                tai.segment_pref_6,
            ]
            if segment is not None
        ]

        # If Equity => NSE_CASH, BSE_CASH
        if "EQUITY" in segments:
            exchanges.update(["NSE_CASH", "BSE_CASH"])

        # If FNO => NSE_FNO, BSE_FNO, plus NSE_DLY (since FNO is a derivative)
        if "FNO" in segments:
            exchanges.update(["NSE_FNO", "BSE_FNO", "NSE_DLY"])

        # If Currency => CD_NSE, CD_BSE, plus NSE_DLY (since Currency is a derivative)
        if "CURRENCY" in segments:
            exchanges.update(["CD_NSE", "CD_BSE", "NSE_DLY"])

        # If Commodity => MCX, but only if Commodity is the *only* segment
        if "COMMODITY" in segments:
            if segments == ["COMMODITY"]:
                exchanges.add("MCX")

        # If Mutual Fund => MF_NSE
        if "MUTUAL_FUND" in segments:
            exchanges.add("MF_NSE")

        # If SLB => NSE_SLBM
        if "SLB" in segments:
            exchanges.add("NSE_SLBM")

    # Return as a list (set helps avoid duplicates if multiple conditions overlap)
    ret = ",".join(list(exchanges))
    return ret


def is_digilocker_selected(value: RootApplicationDetails) -> bool:
    if value.kyc_digilocker.value == "YES":
        return True
    return False


def extract_branch_from_token(token: str) -> str:
    # Decode the JWT token without verification
    decoded_token = jwt.decode(token, options={"verify_signature": False})

    # Extract branch from extra_fields
    branch = (
        decoded_token.get("user_metadata", {})
        .get("user_info", {})
        .get("extra_fields", {})
        # .get("branch", "")
    )

    return branch


def translate_form_to_techxl(value: Dict[str, Any], user_token: str) -> Dict[str, Any]:
    form = AofModel.model_validate(value)

    logging.debug(f"Form data: {value}")
    try:
        return {
            # todo: field need to be added in the form
            "NOT_BOID": "DUMMY_BO_ID",
            # todo: need to be extracted from the user token, "branch_token" need to be added to user token.
            "BRANCH_CODE": extract_branch_from_token(token=user_token),
            "ExchangeList": exchange_list(form),
            "Client_Nature": "C",
            "SMS_SEND": "Y",
            "FATCA_COUNTRY": "India",
            "Agreement_Date": current_date(),
            "NOT_EFT": "Y",
            "NOT_POA": "N",
            "CL_OP_CHGS_DEBITED": "C",
            "CLIENT_WEBXID": "Y",
            "FATCA_DECLARATION": "Yes",
            **_translate_onboarding(form.onboarding),
            **_translate_application_details(form.application_details),
            **_translate_kyc_holders(form.kyc_holders, form.application_details),
            **_translate_bank_verification(form.bank_verification),
            **_translate_nomination_details(form.nomination_details),
            **_translate_trading_information(form.trading_information),
            **_translate_dp_information(form.dp_information),
            **_translate_tnc(form.tnc),
        }
    except Exception as e:
        logging.exception(f"Error in translate_form_to_techxl: {e}")
        return {}


def _translate_onboarding(value: RootOnboarding) -> Dict[str, Any]:
    result = {"Category": ""}

    if not value:
        return result

    if value.type_of_client:
        # result["CATEGORY"] = value.type_of_client.value
        result["Category"] = "I"

    return result


def _translate_application_details(value: RootApplicationDetails) -> Dict[str, Any]:
    result = {}
    if not value:
        return {}

    if value.gst_details_card:
        result["GSTIN_C"] = value.gst_details_card.gst_number or ""
    # if value.general_application_details:
    #     result["Residential_Status"] = (
    #         value.general_application_details.residential_status.value
    #     )

    return result


def _translate_kyc_holders(
    value: List[FieldGrpRootKycHolders], application_details: RootApplicationDetails
) -> Dict[str, Any]:
    def _title(marital_status: W2WMARITALSTATUS, gender: GENDER) -> str:
        if gender is None:
            return "MR"
        elif gender == GENDER.M:
            return "MR"
        elif gender == GENDER.F:
            if marital_status is None:
                return "MISS"
            return "MRS" if marital_status == W2WMARITALSTATUS.MARRIED else "MISS"
        else:
            return "MR"

    def _first_name(name: str) -> str:
        return name.split()[0] if name else ""

    def _last_name(name: str) -> str:
        return name.split()[-1] if name else ""

    def _middle_name(name: str) -> str:
        parts = name.split()
        return " ".join(parts[1:-1]) if len(parts) > 2 else ""

    result = {
        "Client_Name": "",
        "PAN_NO": "",
        "Pan_Name": "",
        "FIRST_NAME": "",
        "MIDDLE_NAME": "",
        "LAST_NAME": "",
        "Father_Husband_Name": "",
        "Mother_Name": "",
        "BIRTH_DATE": "",
        "TITLE": "",
        "MARITAL_STATUS": "",
        "SEX": "",
        "Pin_Code": "",
        "City": "",
        "State": "",
        "Country": "",
        "MOBILE_NO": "",
        "EMAIL_ID": "",
        "Residential_Status": "",
    }

    if not value:
        return result

    for i, holder in enumerate(value, 1):
        if holder is None or holder.kyc_holder is None:
            continue

        kyc_holder = holder.kyc_holder

        if kyc_holder.pan_verification and kyc_holder.pan_verification.pan_details:
            pan = kyc_holder.pan_verification.pan_details
            result.update(
                {
                    "Client_Name": pan.name_in_pan or "",
                    "PAN_NO": pan.pan_number or "" if i == 1 else result["PAN_NO"],
                    "Pan_Name": pan.name_in_pan or "",
                    "FIRST_NAME": _first_name(pan.name_in_pan or ""),
                    "MIDDLE_NAME": _middle_name(pan.name_in_pan or ""),
                    "LAST_NAME": _last_name(pan.name_in_pan or ""),
                    "Father_Husband_Name": pan.parent_guardian_spouse_name or "",
                    "BIRTH_DATE": pan.dob_pan or "",
                }
            )

        marital_status = None

        if kyc_holder.identity_address_verification:
            identity_info = kyc_holder.identity_address_verification

            digilocker_selected: bool = is_digilocker_selected(
                value=application_details
            )
            if digilocker_selected:
                result["Pan_Proof"] = "02"
            else:
                id_proof_mapping = {
                    "VOTER": "05",
                    "DL": "04",
                    "PASSPORT": "03",
                    "AADHAAR": "02",
                }

                result["Pan_Proof"] = id_proof_mapping.get(
                    identity_info.ovd.ovd_type.value, ""
                )

            if identity_info.other_info:
                result["Mother_Name"] = identity_info.other_info.mother_name or ""
                marital_status = identity_info.other_info.marital_status
                if marital_status:
                    result["MARITAL_STATUS"] = (
                        "S" if marital_status.value == "SINGLE" else "M"
                    )
                result["Residential_Status"] = (
                    identity_info.other_info.residential_status.value or ""
                )
                result["NATIONALITY"] = (
                    "I"
                    if identity_info.other_info.residential_status.value == "RI"
                    else "O"
                )

            # Mapping dictionary for Address proofs
            address_proof_mapping = {
                "VOTER": "06",
                "DL": "02",
                "PASSPORT": "02",
                "AADHAAR": "31",
            }

            # Determine Address_Proof1 value based on is_digilocker_selected()
            if is_digilocker_selected(value=application_details):
                address_proof1 = "31"
            else:
                address_proof1 = address_proof_mapping.get(
                    identity_info.ovd.ovd_type.value, ""
                )

            # Determine Correspondance_Address_Proof based on same_as_permanent_address condition
            if (
                identity_info.same_as_permanent_address.value
                == "SAME_AS_PERMANENT_ADDRESS"
            ):
                correspondance_address_proof = address_proof1
            else:
                correspondance_address_proof = address_proof_mapping.get(
                    identity_info.ovd_corr.ovd_type.value, ""
                )

            if identity_info.identity_address_info:
                identity_address = identity_info.identity_address_info
                gender = identity_address.gender
                if gender and marital_status:
                    result["TITLE"] = _title(marital_status, gender)
                    result["SEX"] = ""
                    if gender.value in ("M", "F"):
                        result["SEX"] = gender.value
                    elif gender.value in ("T", "O"):
                        result["SEX"] = "U"

                result.update(
                    {
                        "RESI_ADDRESS1": identity_address.full_address or "",
                        "Pin_Code": identity_address.pin or "",
                        "City": identity_address.city or "",
                        "State": (
                            "TELANGANA"
                            if identity_address.state.lower() == "telangana"
                            else identity_address.state.title() or ""
                        ),
                        "Country": identity_address.country.title() or "",
                        "Address_Proof1": address_proof1,
                    }
                )

            if identity_info.correspondence_address:
                correspondence_address = identity_info.correspondence_address
                result.update(
                    {
                        "Correspondance_Address_Proof": correspondance_address_proof,
                        "REG_ADDR1": correspondence_address.full_address or "",
                        "R_PIN_CODE": correspondence_address.pin or "",
                        "R_CITY": correspondence_address.city or "",
                        "R_STATE": (
                            "TELANGANA"
                            if correspondence_address.state.lower() == "telangana"
                            else identity_address.state.title() or ""
                        ),
                        "R_COUNTRY": correspondence_address.country.title() or "",
                    }
                )

        if kyc_holder.mobile_email_verification:
            mobile_email = kyc_holder.mobile_email_verification
            mobile_contact_id = (
                mobile_email.mobile_verification.contact_id
                if mobile_email.mobile_verification
                else None
            )
            email_contact_id = (
                mobile_email.email_verification.contact_id
                if mobile_email.email_verification
                else None
            )

            result["MOBILE_NO"] = mobile_contact_id or ""
            result["EMAIL_ID"] = email_contact_id or ""
            relationship_mapping = {
                "SELF": "SELF",
                "SPOUSE": "SPOUSE",
                "DEPENDENT_PARENT": "DEPENDENT PARENTS",
                "DEPENDENT_CHILD": "DEPENDENT CHILDREN",
            }
            result["RelationshipMobile"] = relationship_mapping.get(
                mobile_email.mobile_verification.dependency_relationship_mobile.value,
                "",
            )

            result["RelationshipEmailId"] = relationship_mapping.get(
                mobile_email.email_verification.dependency_relationship_email.value,
                "",
            )

            # Determining TypeOfFacility based on presence of contact IDs
            if email_contact_id and not mobile_contact_id:
                result["TypeOfFacility"] = 1
            elif mobile_contact_id and not email_contact_id:
                result["TypeOfFacility"] = 2
            elif mobile_contact_id and email_contact_id:
                result["TypeOfFacility"] = 3
            else:
                result["TypeOfFacility"] = 4

        # Declaration
        if kyc_holder.declarations:
            declarations = kyc_holder.declarations
            result["Political_Affilication"] = "03"  # Default value

            if declarations.politically_exposed_person_card.politically_exposed_person:
                pep_value = (
                    declarations.politically_exposed_person_card.politically_exposed_person
                )

                if pep_value == "PEP":
                    result["Political_Affilication"] = "01"
                elif pep_value == "RELATED":
                    result["Political_Affilication"] = "02"

            if declarations.income_info:
                income_info = declarations.income_info

                # Mapping dictionary for occupation values
                occupation_mapping = {
                    "PRIVATE_SECTOR": "Private Sector Service",
                    "PUBLIC_SECTOR": "Public Sector Service",
                    "GOVT_SERVICE": "Government Service",
                    "BUSINESS": "Business",
                    "HOUSEWIFE": "Housewife",
                    "STUDENT": "Student",
                    "PROFESSIONAL": "Self Employed",
                    "AGRICULTURIST": "Agriculturist",
                    "RETIRED": "Retired",
                    "FARMER": "Farmer",
                    "OTHERS": "Others",
                }

                # Assigning mapped occupation to result
                result["OCCUPATION"] = occupation_mapping.get(
                    income_info.occupation.value, ""
                )
                # Mapping dictionary for income values
                income_mapping = {
                    "UPTO_1L": "Less Than One Lakhs",
                    "1_TO_5L": "One To Five Lakhs",
                    "5_TO_10L": "Five To Ten Lakhs",
                    "10_TO_25L": "Ten To TwentyFive Lakhs",
                    "25L_TO_1CR": "TwentyFive Lakhs To One Crore",
                    "1CR_TO_5CR": "One Crore To Five Crores",
                    "GT_5CR": "Above Five Crore",
                }

                # Assigning mapped income value to result
                result["ANNUAL_INCOME"] = income_mapping.get(
                    income_info.gross_annual_income.value,
                    "",
                )
                result["PORTFOLIO_MKT_VALUE"] = income_info.networth or ""

                parsed_date = datetime.strptime(
                    income_info.date[:10], "%Y-%m-%d"
                ).date()
                result["GrossAnnualIncomeDate"] = (
                    parsed_date.strftime("%d/%m/%Y") if parsed_date else ""
                )

    return result


def _translate_bank_verification(value: RootBankVerification) -> Dict[str, Any]:
    result = {"NOT_BANKCCOUNTNNO": "", "NOT_IFSC": ""}

    if not value:
        return result

    if value.bank_details:
        bank_details = value.bank_details
        result["NOT_BANKCCOUNTNNO"] = bank_details.bank_account_number or ""
        result["NOT_IFSC"] = bank_details.ifsc_code or ""
        result["Not_BankAcType"] = (
            "Saving" if bank_details.account_type.value == "SAVINGS" else "Current"
        )
        result["Not_MicrNo"] = bank_details.micr_code or ""

    return result


def _translate_nomination_details(value: RootNominationDetails) -> Dict[str, Any]:
    # Initialize all possible keys with empty values
    result = {
        "NomineeOptOut": "",
        "NO_OF_NOMINEES": 0,
    }

    # Add nominee-specific empty fields for up to 3 nominees

    if not value:
        return result

    # Update general nomination fields if they exist
    if value.general and value.general.client_nominee_appointment_status:
        _val = value.general.client_nominee_appointment_status.value
        if _val == "YES":
            result["NomineeOptOut"] = "Y"
        elif _val == "NO":
            result["NomineeOptOut"] = "N"
        else:
            result["NomineeOptOut"] = "D"

    if value.nominees:
        result["NO_OF_NOMINEES"] = len(value.nominees)

        # Update nominee-specific fields
        for i, nominee in enumerate(value.nominees, 1):
            if nominee and nominee.nominee and nominee.nominee.nominee_data:
                nominee_data = nominee.nominee.nominee_data
                if nominee_data:
                    if nominee_data.name_of_nominee:
                        result[f"NOMINATION_NAME_{i}"] = nominee_data.name_of_nominee
                    if nominee_data.nominee_address:
                        result[f"NOM_ADDRESS_{i}"] = nominee_data.nominee_address
                    if nominee_data.dob_nominee:
                        result[f"NOM_DOB_{i}"] = nominee_data.dob_nominee

                    if nominee_data.percentage_of_allocation:
                        result[f"SHARE_PERCENTAGE_{i}"] = (
                            nominee_data.percentage_of_allocation
                        )

                    # Check for minor nominee details
                    if (
                        nominee_data.minor_nominee
                        and nominee_data.minor_nominee.NOMINEE_IS_A_MINOR
                        == MINORNOMINEE.NOMINEE_IS_A_MINOR
                        and nominee.nominee.guardian_data
                    ):
                        guardian_data = nominee.nominee.guardian_data
                        if guardian_data.guardian_name:
                            result[f"GUARDIAN_NAME_{i}"] = guardian_data.guardian_name
                        if guardian_data.relationship_with_nominee:
                            result[f"GUARDIAN_RELATION_{i}"] = (
                                guardian_data.relationship_with_nominee
                            )
                        if guardian_data.guardian_address:
                            result[f"GUARDIAN_ADDRESS_{i}"] = (
                                guardian_data.guardian_address
                            )

    return result


def _translate_trading_information(value: RootTradingInformation) -> Dict[str, Any]:
    return {}


def _translate_dp_information(value: RootDpInformation) -> Dict[str, Any]:
    if not value:
        return {}
    if value.dp_Account_information:
        dp_info = value.dp_Account_information
        return {
            "NOT_DPID": dp_info.dp_id_no or "",
            "Client_id": dp_info.client_id_no or "TEST0001",
        }


def _translate_tnc(value: RootTnc) -> Dict[str, Any]:
    return {}
