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
)
from .nsdl_demat_model.form_record_mpdel import (
    FormRecordModel,
    KYCHolder,
    Nominee,
)
import json
from importlib import resources
import base64
from typing import List
import os


def map_form_record(form_record_model: FormRecordModel) -> NSDLRquestModel:
    """
    This function maps the form record model to the NSDL root model and returns.
    """
    REQUESTOR_ID = os.getenv("NSDL_REQUESTOR_ID")
    holder = form_record_model.kyc_holders[0].kyc_holder
    correspondence_address = holder.identity_address_verification.correspondence_address
    permanent_address = holder.identity_address_verification.identity_address_info
    nsdl_model = NSDLRquestModel(
        instr=Instr(
            beneficiaryDetails=BeneficiaryDetails(
                primaryBeneficiary=PrimaryBeneficiary(
                    name=holder.identity_address_verification.identity_address_info.name,
                    shortName=holder.identity_address_verification.identity_address_info.name,
                    pan=holder.pan_verification.pan_details.pan_number,
                    panFlag="Y",
                    grossAnnualIncome=holder.declarations.income_info.gross_annual_income,
                    dob=holder.pan_verification.pan_details.dob_pan,  # Client DOB with YYYYMMDD format.
                    aadhar=holder.identity_address_verification.identity_address_info.uid,
                    mobile=holder.mobile_email_verification.mobile_verification.contact_id,
                    email=holder.mobile_email_verification.email_verification.contact_id,
                    ddpiid=None,
                    eStatement=getEstatement(
                        kit1=form_record_model.trading_information.trading_account_information.kit_format_1,
                        kit2=form_record_model.trading_information.trading_account_information.kit_format_2,
                    ),
                    dematAccType="04",  # ??? Source is not known yet
                    dematAccSubType="01",  # ??? Source is not known yet
                    rbiRefNo="12345",  # ??? Source is not known yet
                    rbiApprovalDate="20201222",  # ??? Source is not known yet
                    modeOfOperation=getModeOfOperation(),  # Mode is not known yet
                    communicationToBeSend=getComunicationSend(),
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
                    signature=get_wet_signature(
                        holder.signature_validation.upload_images.wet_signature_image
                    ),
                ),
                numOfJointHolders=get_number_of_holders(form_record_model.kyc_holders),
                listOfJointHolders=get_list_of_joint_holders(
                    form_record_model.kyc_holders
                ),
                additionalBeneDetails=AdditionalBeneficiaryDetails(
                    familyMobileFlag="N",
                    familyEmailFlag="N",
                    nominationOption=get_nomination_option(
                        form_record_model.nomination_details.general.client_nominee_appointment_status
                    ),
                    occupation=get_occupation(
                        holder.declarations.income_info.occupation
                    ),
                    fatherOrHusbandName=holder.identity_address_verification.other_info.father_name,
                    dpId=REQUESTOR_ID,
                    clientId="",  # Don't know
                    sharePercentEqually="",  #
                    numOfNominees=get_number_of_nominees(
                        form_record_model.nomination_details.nominees
                    ),
                    listOfNominees=get_nominees(
                        form_record_model.nomination_details.nominees
                    ),
                ),
            ),
            bankDetails=BankDetails(
                accountNumber=form_record_model.bank_verification.bank_details.bank_account_number,
                bankName="",  # Don't have the Bandk Name one way is to get the bank name from ifsc code
                ifsc=form_record_model.bank_verification.bank_details.ifsc_code,
                micr="",  # Don't have the Micr code
                accountType="",  # Don't have the Account
                bankAddress=BankAddress(  # Don't have the Bank Address one way is to get the Bank Address from ifsc code
                    addressType="",
                    addressLine1="",
                    addressLine2="",  # Optional
                    addressLine3="",  # Optional
                    addressLine4="",  # Optional
                    zipcode="",
                ),
            ),
        )
    )
    return nsdl_model


def load_mapping_file(self, file_name: str) -> dict:
    with resources.path("lyik.nsdl_mapping_json_file", file_name) as file_path:
        with open(file_path, "r") as file:
            return json.load(file)


def getEstatement(kit1: str | None, kit2: str | None) -> str:
    """
    Returns the Estatement value
    """
    if kit1:
        return "P"
    elif kit2:
        return "E"


def getModeOfOperation(mode: str | None) -> str | None:
    """
    Returns the mode of operation value
    """
    # ToDO: The mode is not known yet
    # Optional in case of single account holder. Mandatory in case of joint account holders.
    if mode is None:
        return None
    elif mode.lower() == "Jointly":
        return "1"
    elif mode.lower() == "Anyone of the holder or survivor":
        return "2"


def getComunicationSend(comm: str | None) -> str | None:
    """
    Returns the communication to be send value
    """
    # ToDO: The communication is not known yet
    # Optional in case of single account holder. Mandatory in case of joint account holders.
    if comm is None:
        return None
    elif comm.lower() == "First holder":
        return "1"
    elif comm.lower() == " All joint account holders":
        return "2"


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


def get_wet_signature(wet_signature: DBDocumentModel) -> str:
    """Returns the wet signature value as base64 encoded string"""
    # ToDO: Get the image bytes from the document plugin
    image_bytes = []
    encoded_image = base64.b64encode(image_bytes).decode()
    return encoded_image


def get_number_of_holders(kyc_holders=List[KYCHolder]) -> int:
    """Returns the number of holders"""
    if len(kyc_holders) is 1:
        return 0
    return len(kyc_holders)


def get_list_of_joint_holders(kyc_holders=List[KYCHolder]) -> List[JointHolder] | None:
    """Returns the list of jointholders"""
    if len(kyc_holders) <= 1:
        return None
    joint_holders: List[JointHolder] = []
    for kyc_holder in kyc_holders:
        # ToDO: prepare the joint holder from kyc holder data
        joint_holder = JointHolder(
            seq="",
            name="",
            pan="",
            panFlag="Y",
            dob="",
            mobileNo="",
            emailId="",
            smsfacility="",
        )
        joint_holders.append(joint_holder)
    return joint_holders


def get_occupation(occupation_name) -> str:
    """Returns the occupation"""
    occupation_mapping = None
    if occupation_mapping is None:
        occupation_mapping = load_mapping_file(file_name="occupation.json")
    return occupation_mapping.get(occupation_name, "8")  # Because 8 is for other


def get_number_of_nominees(nominees_list: List[Nominee]) -> int:
    return len(nominees_list)


def get_nominees(nominees_list: List[Nominee]) -> List[NSDLNominee] | None:
    if len(nominees_list) == 0:
        return None
    nominees: List[NSDLNominee] = []
    for nominee in nominees_list:
        # ToDO: prepare the nominee from nominee data
        nominee = NSDLNominee(
            seqNo="",
            nomineeName="",
            relationWithNominee="",
            nomineeAddress=Address(
                addressType="",
                addressLine1="",
                addressLine2="",
                addressLine3="",
                addressLine4="",
                zipcode="",
                city="",
                statecode="",
                countrycode="",
            ),
            nomineeMobileNum="",
            nomineeEmailId="",
            nomineeShare=None,
            nomineeIdentificationDtls=NomineeIdentificationDetails(
                pan="",
                aadhar="",
                savingBankAccNo="",
                dematAccId="",
            ),
            minor="",
            dob="",
            guardianName="",
            guardianAddress=Address(
                addressType="",
                addressLine1="",
                addressLine2="",
                addressLine3="",
                addressLine4="",
                zipcode="",
                city="",
                statecode="",
                countrycode="",
            ),
            guardianMobileNum="",
            guardianEmailId="",
            guardianRelationship="",
            guardianIdentificationDtls=NomineeIdentificationDetails(
                pan="",
                aadhar="",
                savingBankAccNo="",
                dematAccId="",
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
