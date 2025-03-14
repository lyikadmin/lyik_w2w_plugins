from lyikpluginmanager import (
    NSDLRquestModel,
    Instr,
    BankDetails,
    BankAddress,
    BeneficiaryDetails,
    PrimaryBeneficiary,
    JointHolder,
    AdditionalBeneficiaryDetails,
    NSDLNominee,
    NomineeIdentificationDetails,
    Address,
    DBDocumentModel,
    invoke,
    ContextModel,
)
from .nsdl_demat_model.form_record_mpdel import (
    FormRecordModel,
    KYCHolder,
    KYCHolderData,
    Nominee,
)
import json
from importlib import resources
import base64
from typing import List
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def map_form_record(
    form_record_model: FormRecordModel, context: ContextModel
) -> NSDLRquestModel:
    """
    This function maps the form record model to the NSDL root model and returns.
    """
    REQUESTOR_ID = os.getenv("NSDL_REQUESTOR_ID")
    first_holder = form_record_model.kyc_holders[0].kyc_holder
    correspondence_address = (
        first_holder.identity_address_verification.correspondence_address
    )
    permanent_address = first_holder.identity_address_verification.identity_address_info
    nsdl_model = NSDLRquestModel(
        instr=Instr(
            beneficiaryDetails=BeneficiaryDetails(
                primaryBeneficiary=PrimaryBeneficiary(
                    name=first_holder.identity_address_verification.identity_address_info.name,
                    shortName=first_holder.identity_address_verification.identity_address_info.name,
                    pan=first_holder.pan_verification.pan_details.pan_number,
                    panFlag="Y",
                    grossAnnualIncome=first_holder.declarations.income_info.gross_annual_income,
                    dob=get_NSDL_formatted_date(
                        first_holder.pan_verification.pan_details.dob_pan
                    ),
                    gender=first_holder.identity_address_verification.identity_address_info.gender,
                    aadhar=get_aadhaar_from_uid(
                        first_holder.identity_address_verification.identity_address_info.uid,
                        form_record_model.application_details.kyc_digilocker,
                        first_holder.identity_address_verification.ovd.ovd_type,
                    ),
                    mobile=first_holder.mobile_email_verification.mobile_verification.contact_id,
                    email=first_holder.mobile_email_verification.email_verification.contact_id,
                    ddpiid="12345",  # ??? Source unknown
                    eStatement=getEstatement(
                        kit1=form_record_model.trading_information.trading_account_information.kit_format_1,
                        kit2=form_record_model.trading_information.trading_account_information.kit_format_2,
                    ),
                    dematAccType="04",  # ??? Source is not known yet
                    dematAccSubType="01",  # ??? Source is not known yet
                    rbiRefNo="12345",  # ??? Source is not known yet
                    rbiApprovalDate="20201222",  # ??? Source is not known yet
                    modeOfOperation=getModeOfOperation(
                        form_record_model.dp_information.standing_info_from_client.joint_account_operation_mode,
                        form_record_model.kyc_holders,
                    ),
                    communicationToBeSend=getComunicationSend(
                        form_record_model.dp_information.standing_info_from_client.consent_for_communication,
                        form_record_model.kyc_holders,
                    ),
                    beneficiaryCoresAddress=Address(
                        addressType="1",  # Coresponding Address is 1
                        addressLine1=correspondence_address.full_address,
                        addressLine2="",  # Optional
                        addressLine3="",  # Optional
                        addressLine4="",  # Optional
                        zipcode=correspondence_address.pin,
                        city=correspondence_address.city,
                        statecode=get_state_code(correspondence_address.state),
                        countrycode=get_country_code(correspondence_address.country),
                    ),
                    beneficiaryPermAddress=Address(
                        addressType="4",  # Permanent Address is 4
                        addressLine1=permanent_address.full_address,
                        addressLine2="",  # Optional
                        addressLine3="",  # Optional
                        addressLine4="",  # Optional
                        zipcode=permanent_address.pin,
                        city=permanent_address.city,
                        statecode=get_state_code(permanent_address.state),
                        countrycode=get_country_code(permanent_address.country),
                    ),
                    signature=await get_wet_signature(
                        first_holder.signature_validation.upload_images.wet_signature_image,
                        context=context,
                    ),
                ),
                numOfJointHolders=get_number_of_holders(form_record_model.kyc_holders),
                listOfJointHolders=get_list_of_joint_holders(
                    form_record_model.dp_information.standing_info_from_client.first_holder_sms_alert,
                    form_record_model.kyc_holders,
                ),
                additionalBeneDetails=AdditionalBeneficiaryDetails(
                    familyMobileFlag="N",  # ??? Need more information
                    familyEmailFlag="N",  # ??? Need more information
                    nominationOption=get_nomination_option(
                        form_record_model.nomination_details.general.client_nominee_appointment_status
                    ),
                    occupation=get_occupation(
                        first_holder.declarations.income_info.occupation
                    ),
                    fatherOrHusbandName=first_holder.identity_address_verification.other_info.father_name,
                    dpId=REQUESTOR_ID,
                    clientId=0,  # ??? Don't know
                    sharePercentEqually="N",  # ‘Y’ – indicates system will equally distribute share across all nominees, any decimal factor would be added on to the first nominee. ‘N’ – indicates manual share allocation to all nominees. Total should be 100%.
                    numOfNominees=get_number_of_nominees(
                        form_record_model.nomination_details.nominees
                    ),
                    listOfNominees=get_nominees(
                        form_record_model.nomination_details.nominees,
                        form_record_model.nomination_details.general.client_nominee_appointment_status,
                    ),
                ),
            ),
            bankDetails=BankDetails(
                accountNumber=form_record_model.bank_verification.bank_details.bank_account_number,
                bankName="",  # Don't have the Bank Name one way is to get the bank name from ifsc code
                ifsc=form_record_model.bank_verification.bank_details.ifsc_code,
                micr="",  # Don't have the MICR code
                accountType="",  # Don't have the Account
                bankAddress=BankAddress(
                    addressType="2",  # Bank address is 2
                    addressLine1="",  # Don't have the Bank Address one way is to get the Bank Address from ifsc code
                    addressLine2="",  # Optional
                    addressLine3="",  # Optional
                    addressLine4="",  # Optional
                    zipcode="",  # Not available
                ),
            ),
        )
    )
    return nsdl_model


def get_NSDL_formatted_date(date: str) -> str:
    """
    Converts the date of birth from DD/MM/YYYY to YYYYMMDD format.
    """
    formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y%m%d")
    return formatted_date


def load_mapping_file(file_name: str) -> dict:
    with resources.path("lyik.nsdl_mapping_json_files", file_name) as file_path:
        with open(file_path, "r") as file:
            return json.load(file)


def get_aadhaar_from_uid(
    uid: str, kyc_digilocker: str, ovd_type: str | None
) -> str | None:
    """
    Returns the Aadhaar number from the UID.
    """
    if kyc_digilocker == "YES":
        return uid
    elif kyc_digilocker == "NO" and ovd_type and ovd_type == "AADHAAR":
        return uid
    else:
        return None


def getEstatement(kit1: str | None, kit2: str | None) -> str:
    """
    Returns the Estatement value
    """
    if kit2:
        return "E"
    elif kit1:
        return "P"


def getModeOfOperation(mode: str | None, holders: List[KYCHolder]) -> int | None:
    """
    Returns the mode of operation value
    """
    if mode is None:
        return None
    # Optional in case of single account holder. Mandatory in case of joint account holders.
    if len(holders) == 0:
        return None
    elif mode.upper() == "JOINTLY":
        return 1
    elif mode.upper() == "ANY_ONE_HOLDER_OR_SURVIVORS":
        return 2


def getComunicationSend(comm: str | None, holders: List[KYCHolder]) -> str | None:
    """
    Returns the communication to be send value
    """
    if comm is None:
        return None
    # Optional in case of single account holder. Mandatory in case of joint account holders.
    if len(holders) <= 1:
        return None
    elif comm.lower() == "FIRST_HOLDER":
        return 1
    elif comm.lower() == "ALL_HOLDERS":
        return 2


def get_state_code(state: str) -> str:
    state_mapping = None
    if state_mapping is None:
        state_mapping = load_mapping_file(file_name="states.json")
    return state_mapping.get(state.upper())


def get_country_code(country_name: str) -> str:
    """Returns the country code"""
    country_mapping = None
    if country_mapping is None:
        country_mapping = load_mapping_file(file_name="country.json")
    return country_mapping.get(country_name.upper(), "")


async def get_wet_signature(
    wet_signature: DBDocumentModel, context: ContextModel
) -> str:
    """Returns the wet signature value as base64 encoded string"""
    # Invoke the doc_mgmt plugin to fetch a document
    documents = await invoke.fetchDocument(
        config=context.config,
        org_id=context.org_id,
        file_id=wet_signature.doc_id,
        coll_name=context.form_id,
        metadata_params=None,
    )
    document_model: DBDocumentModel = (
        documents[0]
        if isinstance(documents, list)
        and all(isinstance(item, DBDocumentModel) for item in documents)
        else None
    )
    encoded_image = base64.b64encode(document_model.doc_content).decode()
    return encoded_image


def get_number_of_holders(kyc_holders: List[KYCHolder]) -> int:
    """Returns the number of holders"""
    if len(kyc_holders) == 1:
        return 0
    return len(kyc_holders)


def get_list_of_joint_holders(
    sms_alert: str, kyc_holders: List[KYCHolder]
) -> List[JointHolder]:
    """Returns the list of jointholders"""
    if len(kyc_holders) <= 1:
        return []
    joint_holders: list[JointHolder] = []
    for index, holder in enumerate(kyc_holders[1:], start=1):
        holder = kyc_holders[index]
        holder_data: KYCHolderData = holder.kyc_holder
        joint_holder = JointHolder(
            seq=index + 1,  # Because the sequence no is starting from 2
            name=holder_data.identity_address_verification.identity_address_info.name,
            pan=holder_data.pan_verification.pan_details.pan_number,
            panFlag="Y",
            dob=get_NSDL_formatted_date(
                holder_data.pan_verification.pan_details.dob_pan
            ),
            mobileNo=holder_data.mobile_email_verification.mobile_verification.contact_id,
            emailId=holder_data.mobile_email_verification.email_verification.contact_id,
            smsfacility=get_join_holder_sms_facility(
                holder_data.mobile_email_verification.mobile_verification.contact_id,
                sms_alert,
                index,
            ),
        )
        joint_holders.append(joint_holder)
    return joint_holders


def get_join_holder_sms_facility(
    mobile_number: str | None, sms_alert: str, index: int
) -> str:
    """Returns the join holder sms_facility tag"""
    if mobile_number is None:
        return "N"
    elif sms_alert == "NO":
        return "N"
    elif sms_alert == "ALL_JOINT_HOLDER":
        return "Y"
    elif sms_alert == "FIRST_HOLDER":
        if index == 0:
            return "Y"
        else:
            return "N"


def get_occupation(occupation_name) -> str:
    """Returns the occupation"""
    occupation_mapping = None
    if occupation_mapping is None:
        occupation_mapping = load_mapping_file(file_name="occupation.json")
    return occupation_mapping.get(occupation_name, "8")  # Because 8 is for other


def get_number_of_nominees(nominees_list: List[Nominee]) -> int:
    return len(nominees_list)


def get_nominees(nominees_list: List[Nominee], nominee_flag: str) -> List[NSDLNominee]:
    if nominee_flag == "NO":
        return []
    nominees: List[NSDLNominee] = []
    for index, nominee in enumerate(nominees_list):
        nominee = NSDLNominee(
            seqNo=index + 1,
            nomineeName=nominee.nominee_data.name_of_nominee,
            relationWithNominee="",  # Relation is not in the form
            nomineeAddress=Address(
                addressType="",  # Not sure how to get the code for nominee address type
                addressLine1=nominee.nominee_data.nominee_address,
                addressLine2="",  # Optional
                addressLine3="",  # Optional
                addressLine4="",  # Optional
                zipcode="",  # PIN is not available for nominee in form
                city="",  # City is not available for nominee in form
                statecode="",  # State is not available for nominee in form
                countrycode="",  # Country is not available for nominee in form
            ),
            nomineeMobileNum="",  # Optional
            nomineeEmailId="",  # Optional
            nomineeShare=get_nominee_share(
                nominee.nominee_data.percentage_of_allocation
            ),
            nomineeIdentificationDtls=NomineeIdentificationDetails(
                pan="",  # Optional
                aadhar="",  # Optional
                savingBankAccNo="",  # Optional
                dematAccId="",  # Optional
            ),
            minor=nominee.nominee_data.minor_nominee,
            dob=get_NSDL_formatted_date(nominee.nominee_data.dob_nominee),
            guardianName=nominee.guardina_data.guardian_name,  # if nominee is minor then only
            guardianAddress=Address(
                addressType="",  # Need for more information on this
                addressLine1=nominee.guardina_data.guardian_address,
                addressLine2="",  # Optional
                addressLine3="",  # Optional
                addressLine4="",  # Optional
                zipcode="",  # Not available in the form
                city="",  # Not available in the form
                statecode="",  # Not available in the form
                countrycode="",  # Not available in the form
            ),
            guardianMobileNum="",  # Optional
            guardianEmailId="",  # Optional
            guardianRelationship=nominee.guardina_data.relationship_with_nominee,
            guardianIdentificationDtls=NomineeIdentificationDetails(
                pan="",  # Optional
                aadhar="",  # Optional
                savingBankAccNo="",  # Optional
                dematAccId="",  # Optional
            ),
        )
        nominees.append(nominee)
    return nominees


def get_nomination_option(nomination_option: str) -> str:
    """Returns the nomination option"""
    nomination_mapping = {
        "YES": "Y",
        "NO": "N",
    }
    return nomination_mapping.get(nomination_option, "N")


def get_nominee_share(allocation_percentage: str) -> int | None:
    """Returns the number of shares"""
    if allocation_percentage is None:
        return None
    return int(allocation_percentage)
