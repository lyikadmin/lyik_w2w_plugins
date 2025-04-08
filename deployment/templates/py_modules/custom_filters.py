from __future__ import annotations

import logging
from typing import Any, Dict, List

from model import (
    Org82418635Frm5244590Model,
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


def current_date():
    #     return date in DD/MM/YYYY format
    from datetime import datetime

    return datetime.now().strftime("%d/%m/%Y")


def exchange_list(form: Org82418635Frm5244590Model) -> str:
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


def translate_form_to_techxl(value: Dict[str, Any]) -> Dict[str, Any]:
    form = Org82418635Frm5244590Model.model_validate(value)

    logging.debug(f"Form data: {value}")
    try:
        return {
            # todo: field need to be added in the form
            "NOTBO_ID": "DUMMY_BO_ID",
            # todo: need to be extracted from the user token, "branch_token" need to be added to user token.
            "BRANCH_CODE": "DUMMY_BRANCH_CODE",
            "EXCHANGELIST": exchange_list(form),
            "PAN_PROOF": "01",
            "CLIENT_NATURE": "C",
            "SMS_SEND": "Y",
            "FATCA_COUNTRY": "India",
            "AGREEMENT_DATE": current_date(),
            "NOT_EFT": "Y",
            "NOT_POA": "N",
            "TYPEOFFACILITY": 3,
            **_translate_onboarding(form.onboarding),
            **_translate_application_details(form.application_details),
            **_translate_kyc_holders(form.kyc_holders),
            **_translate_bank_verification(form.bank_verification),
            **_translate_nomination_details(form.nomination_details),
            **_translate_trading_information(form.trading_information),
            **_translate_dp_information(form.dp_information),
            **_translate_tnc(form.tnc),
        }
    except Exception as e:
        logging.error(f"Error in translate_form_to_techxl: {e}")
        return {}


def _translate_onboarding(value: RootOnboarding) -> Dict[str, Any]:
    result = {"CATEGORY": ""}

    if not value:
        return result

    if value.type_of_client:
        result["CATEGORY"] = value.type_of_client.value

    return result


def _translate_application_details(value: RootApplicationDetails) -> Dict[str, Any]:
    result = {}
    if not value:
        return {}

    if value.gst_details_card:
        result["GSTIN_C"] = value.gst_details_card.gst_number or ""

    return result


def _translate_kyc_holders(value: List[FieldGrpRootKycHolders]) -> Dict[str, Any]:
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
        "CLIENT_NAME": "",
        "PAN_NO": "",
        "PAN_NAME": "",
        "FIRST_NAME": "",
        "MIDDLE_NAME": "",
        "LAST_NAME": "",
        "FATHER_HUSBAND_NAME": "",
        "MOTHER_NAME": "",
        "BIRTH_DATE": "",
        "TITLE": "",
        "MARITAL_STATUS": "",
        "SEX": "",
        "PIN_CODE": "",
        "CITY": "",
        "STATE": "",
        "COUNTRY": "",
        "MOBILE_NO": "",
        "EMAIL_ID": "",
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
                    "CLIENT_NAME": pan.name_in_pan or "",
                    "PAN_NO": pan.pan_number or "" if i == 1 else result["PAN_NO"],
                    "PAN_NAME": pan.name_in_pan or "",
                    "FIRST_NAME": _first_name(pan.name_in_pan or ""),
                    "MIDDLE_NAME": _middle_name(pan.name_in_pan or ""),
                    "LAST_NAME": _last_name(pan.name_in_pan or ""),
                    "FATHER_HUSBAND_NAME": pan.parent_guardian_spouse_name or "",
                    "BIRTH_DATE": pan.dob_pan or "",
                }
            )

        marital_status = None

        if kyc_holder.identity_address_verification:
            identity_info = kyc_holder.identity_address_verification
            if identity_info.other_info:
                result["MOTHER_NAME"] = identity_info.other_info.mother_name or ""
                marital_status = identity_info.other_info.marital_status
                result["MARITAL_STATUS"] = (
                    marital_status.value if marital_status else ""
                )

            if identity_info.identity_address_info:
                identity_address = identity_info.identity_address_info
                gender = identity_address.gender
                result.update(
                    {
                        "SEX": gender.value if gender else "",
                        "RESI_ADDRESS1": identity_address.full_address or "",
                        "PIN_CODE": identity_address.pin or "",
                        "CITY": identity_address.city or "",
                        "STATE": identity_address.state or "",
                        "COUNTRY": identity_address.country or "",
                        "ADDRESS_PROOF1": "",
                        "CORRESPONDANCE_ADDRESS_PROOF": "",
                    }
                )
                result["TITLE"] = _title(marital_status, gender)
            if identity_info.correspondence_address:
                correspondence_address = identity_info.correspondence_address
                result.update(
                    {
                        "REG_ADDRESS1": correspondence_address.full_address or "",
                        "R_PIN_CODE": correspondence_address.pin or "",
                        "R_CITY": correspondence_address.city or "",
                        "R_STATE": correspondence_address.state or "",
                        "R_COUNTRY": correspondence_address.country or "",
                    }
                )

        if kyc_holder.mobile_email_verification:
            mobile_email = kyc_holder.mobile_email_verification
            if mobile_email.mobile_verification:
                result["MOBILE_NO"] = mobile_email.mobile_verification.contact_id or ""
            if mobile_email.email_verification:
                result["EMAIL_ID"] = mobile_email.email_verification.contact_id or ""

        # Declaration
        if kyc_holder.declarations:
            declarations = kyc_holder.declarations
            if declarations.politically_exposed_person_card:
                result["POLITICAL_AFFILICATION"] = (
                    declarations.politically_exposed_person_card.politically_exposed_person
                    or ""
                )

            if declarations.income_info:
                income_info = declarations.income_info
                result["OCCUPATION"] = income_info.occupation.value or ""
                result["ANNUAL_INCOME"] = income_info.gross_annual_income.value or ""
                result["PORTFOLIO_MKT_VALUE"] = income_info.networth or ""
                # todo change date field name
                # result["NETWORTHDATE"] = income_info.date or ""

    return result


def _translate_bank_verification(value: RootBankVerification) -> Dict[str, Any]:
    result = {"NOT_BANKCCOUNTNNO": "", "NOT_IFSC": ""}

    if not value:
        return result

    if value.bank_details:
        bank_details = value.bank_details
        result["NOT_BANKCCOUNTNNO"] = bank_details.bank_account_number or ""
        result["NOT_IFSC"] = bank_details.ifsc_code or ""
        result["NOT_BANKACTYPE"] = bank_details.account_type.value
        result["NOT_MICRNO"] = bank_details.micr_code or ""

    return result


def _translate_nomination_details(value: RootNominationDetails) -> Dict[str, Any]:
    # Initialize all possible keys with empty values
    result = {
        "NOMINEEOPTOUT": "",
        "NO_OF_NOMINEES": 0,
    }

    # Add nominee-specific empty fields for up to 3 nominees

    if not value:
        return result

    # Update general nomination fields if they exist
    if value.general and value.general.client_nominee_appointment_status:
        result["NOMINEEOPTOUT"] = value.general.client_nominee_appointment_status.value

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
            "DP_ID": dp_info.dp_id_no or "",
            "CLIENT_ID": dp_info.client_id_no or "TEST0001",
        }


def _translate_tnc(value: RootTnc) -> Dict[str, Any]:
    return {}
