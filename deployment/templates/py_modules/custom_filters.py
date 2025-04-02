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


def translate_form_to_techxl(value: Dict[str, Any]) -> Dict[str, Any]:
    form = Org82418635Frm5244590Model.model_validate(value)

    logging.debug(f"Form data: {value}")
    try:
        return {
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
                        "PIN_CODE": identity_address.pin or "",
                        "CITY": identity_address.city or "",
                        "STATE": identity_address.state or "",
                        "COUNTRY": identity_address.country or "",
                    }
                )
                result["TITLE"] = _title(marital_status, gender)

        if kyc_holder.mobile_email_verification:
            mobile_email = kyc_holder.mobile_email_verification
            if mobile_email.mobile_verification:
                result["MOBILE_NO"] = mobile_email.mobile_verification.contact_id or ""
            if mobile_email.email_verification:
                result["EMAIL_ID"] = mobile_email.email_verification.contact_id or ""

    return result


def _translate_bank_verification(value: RootBankVerification) -> Dict[str, Any]:
    result = {}

    return result


def _translate_nomination_details(value: RootNominationDetails) -> Dict[str, Any]:
    result = {"NOMINEEOPTOUT": "", "NO_OF_NOMINEES": 0}

    if not value:
        return result

    result.update(
        {
            "NOMINEEOPTOUT": value.general.client_nominee_appointment_status.value,
            "NO_OF_NOMINEES": len(value.nominees),
        }
    )

    for i, nominee in enumerate(value.nominees, 1):
        result[f"NOMINATION_NAME_{i}"] = nominee.nominee.nominee_data.name_of_nominee
        result[f"NOM_ADDRESS_{i}"] = nominee.nominee.nominee_data.nominee_address
        result[f"NOM_DOB_{i}"] = nominee.nominee.nominee_data.dob_nominee

        if (
            nominee.nominee.nominee_data.minor_nominee.NOMINEE_IS_A_MINOR
            == MINORNOMINEE.NOMINEE_IS_A_MINOR
        ):
            result[f"GUARDIAN_NAME_{i}"] = nominee.nominee.guardian_data.guardian_name
            result[f"GUARDIAN_RELATION_{i}"] = (
                nominee.nominee.guardian_data.guardian_relation.value
            )
            result[f"GUARDIAN_ADDRESS_{i}"] = (
                nominee.nominee.guardian_data.guardian_address
            )

    return result


def _translate_trading_information(value: RootTradingInformation) -> Dict[str, Any]:
    result = {}

    if not value:
        return result

    # update keys

    return result


def _translate_dp_information(value: RootDpInformation) -> Dict[str, Any]:
    result = {}

    if not value:
        return result

    # update keys

    return result


def _translate_tnc(value: RootTnc) -> Dict[str, Any]:
    result = {}

    if not value:
        return result

    # update keys

    return result
