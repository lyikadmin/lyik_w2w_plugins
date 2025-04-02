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
    logging.debug(f"Type of form: {type(form)}")
    logging.debug(f"Form data: {value}")
    logging.debug(
        f"Onboarding data: {form.onboarding} and type of onboarding: {type(form.onboarding)}"
    )

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
    logging.debug(f"Onboarding data: {value}")
    logging.debug(f"Type of value :{type(value)}")
    if not value:
        return {}
    return {
        "CATEGORY": value.type_of_client.value if value.type_of_client else None,
    }


def _translate_application_details(value: RootApplicationDetails) -> Dict[str, Any]:
    application = getattr(value, "general_application_details", None)
    if not application:
        return {}

    return {
        "RESIDENTIAL_STATUS": getattr(application, "residential_status", None),
    }


def _translate_kyc_holders(value: List[FieldGrpRootKycHolders]) -> Dict[str, Any]:

    def _title(marital_status: W2WMARITALSTATUS, gender: GENDER) -> str:
        if gender == GENDER.M:
            return "MR"
        elif gender == GENDER.F:
            return "MRS" if marital_status == W2WMARITALSTATUS.MARRIED else "MISS"
        else:
            return "MR"  # Default for other genders

    def _first_name(name: str) -> str:
        if not name:
            return ""
        return name.split()[0] if name else ""

    def _last_name(name: str) -> str:
        if not name:
            return ""
        return name.split()[-1] if name else ""

    def _middle_name(name: str) -> str:
        if not name:
            return ""
        parts = name.split()
        return " ".join(parts[1:-1]) if len(parts) > 2 else ""

    if not value:
        return {}

    result = {}
    for i, holder in enumerate(value, 1):
        kyc_holder = getattr(holder, "kyc_holder", None)
        pan_verification = (
            getattr(kyc_holder, "pan_verification", None) if kyc_holder else None
        )
        pan_details = (
            getattr(pan_verification, "pan_details", None) if pan_verification else None
        )
        identity_address_verification = (
            getattr(kyc_holder, "identity_address_verification", None)
            if kyc_holder
            else None
        )
        other_info = (
            getattr(identity_address_verification, "other_info", None)
            if identity_address_verification
            else None
        )
        identity_address_info = (
            getattr(identity_address_verification, "identity_address_info", None)
            if identity_address_verification
            else None
        )
        mobile_email_verification = (
            getattr(kyc_holder, "mobile_email_verification", None)
            if kyc_holder
            else None
        )
        mobile_verification = (
            getattr(mobile_email_verification, "mobile_verification", None)
            if mobile_email_verification
            else None
        )
        email_verification = (
            getattr(mobile_email_verification, "email_verification", None)
            if mobile_email_verification
            else None
        )

        if i == 1 and pan_details:
            result["PAN_NO"] = getattr(pan_details, "pan_number", None)
        if pan_details:
            result.update(
                {
                    "PAN_NAME": getattr(pan_details, "name_in_pan", None),
                    "FIRST_NAME": _first_name(getattr(pan_details, "name_in_pan", "")),
                    "MIDDLE_NAME": _middle_name(
                        getattr(pan_details, "name_in_pan", "")
                    ),
                    "LAST_NAME": _last_name(getattr(pan_details, "name_in_pan", "")),
                    "FATHER_HUSBAND_NAME": getattr(
                        pan_details, "parent_guardian_spouse_name", None
                    ),
                    "MOTHER_NAME": (
                        getattr(other_info, "mother_name", None) if other_info else None
                    ),
                    "BIRTH_DATE": getattr(pan_details, "dob_pan", None),
                    "TITLE": _title(
                        (
                            getattr(other_info, "marital_status", None)
                            if other_info
                            else None
                        ),
                        (
                            getattr(identity_address_info, "gender", None)
                            if identity_address_info
                            else None
                        ),
                    ),
                    "MARITAL_STATUS": (
                        getattr(
                            getattr(other_info, "marital_status", None), "value", None
                        )
                        if other_info and getattr(other_info, "marital_status", None)
                        else None
                    ),
                    "SEX": (
                        getattr(
                            getattr(identity_address_info, "gender", None),
                            "value",
                            None,
                        )
                        if identity_address_info
                        and getattr(identity_address_info, "gender", None)
                        else None
                    ),
                    "PIN_CODE": (
                        getattr(identity_address_info, "pin", None)
                        if identity_address_info
                        else None
                    ),
                    "CITY": (
                        getattr(identity_address_info, "city", None)
                        if identity_address_info
                        else None
                    ),
                    "STATE": (
                        getattr(identity_address_info, "state", None)
                        if identity_address_info
                        else None
                    ),
                    "COUNTRY": (
                        getattr(identity_address_info, "country", None)
                        if identity_address_info
                        else None
                    ),
                    "MOBILE_NO": (
                        getattr(mobile_verification, "contact_id", None)
                        if mobile_verification
                        else None
                    ),
                    "EMAIL_ID": (
                        getattr(email_verification, "contact_id", None)
                        if email_verification
                        else None
                    ),
                }
            )

    return result


def _translate_bank_verification(value: RootBankVerification) -> Dict[str, Any]:
    return {}


def _translate_nomination_details(value: RootNominationDetails) -> Dict[str, Any]:
    general = getattr(value, "general", None)
    nominees = getattr(value, "nominees", None)
    result = {
        "NOMINEEOPTOUT": (
            getattr(general, "client_nominee_appointment_status", None).value
            if general
            and getattr(general, "client_nominee_appointment_status", None) is not None
            else None
        ),
        "NO_OF_NOMINEES": len(nominees) if nominees else 0,
    }

    if nominees:
        for i, nominee in enumerate(nominees, 1):
            nominee_data = (
                getattr(nominee.nominee, "nominee_data", None)
                if nominee.nominee
                else None
            )
            guardian_data = (
                getattr(nominee.nominee, "guardian_data", None)
                if nominee.nominee
                else None
            )
            minor_nominee = (
                getattr(nominee_data, "minor_nominee", None) if nominee_data else None
            )

            result[f"NOMINATION_NAME_{i}"] = (
                getattr(nominee_data, "name_of_nominee", None) if nominee_data else None
            )
            result[f"NOM_ADDRESS_{i}"] = (
                getattr(nominee_data, "nominee_address", None) if nominee_data else None
            )
            result[f"NOM_DOB_{i}"] = (
                getattr(nominee_data, "dob_nominee", None) if nominee_data else None
            )

            if (
                minor_nominee
                and minor_nominee.NOMINEE_IS_A_MINOR == MINORNOMINEE.NOMINEE_IS_A_MINOR
            ):
                result[f"GUARDIAN_NAME_{i}"] = (
                    getattr(guardian_data, "guardian_name", None)
                    if guardian_data
                    else None
                )
                result[f"GUARDIAN_RELATION_{i}"] = (
                    getattr(minor_nominee, "guardian_relation", None).value
                    if minor_nominee
                    and getattr(minor_nominee, "guardian_relation", None)
                    else None
                )
                result[f"GUARDIAN_ADDRESS_{i}"] = (
                    getattr(minor_nominee, "guardian_address", None)
                    if minor_nominee
                    else None
                )

    return result


def _translate_trading_information(value: RootTradingInformation) -> Dict[str, Any]:
    return {"EXCHANGELIST": ""}


def _translate_dp_information(value: RootDpInformation) -> Dict[str, Any]:
    return {}


def _translate_tnc(value: RootTnc) -> Dict[str, Any]:
    return {}
