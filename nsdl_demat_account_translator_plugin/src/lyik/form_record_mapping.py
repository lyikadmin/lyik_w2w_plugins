from lyikpluginmanager import (
    getProjectName,
    NSDLDematSpec,
    NSDLRquestModel,
    Instr,
    BankDetails,
    BankAddress,
    BeneficiaryDetails,
    PrimaryBeneficiary,
    JointHolder,
    AdditionalBeneficiaryDetails,
    Nominee,
    NomineeIdentificationDetails,
    Address,
    GenericFormRecordModel,
    DBDocumentModel,
)
from .nsdl_demat_model.form_record_mpdel import (
    FormRecordModel,
    TradingInformation,
    KYCHolder,
)
import json
from importlib import resources
import base64
from typing import List


def map_form_record(form_record_model: FormRecordModel) -> NSDLRquestModel:
    """
    This function maps the form record model to the NSDL root model and returns.
    """

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
                    modeOfOperation=getModeOfOperation(),
                    communicationToBeSend=getCoomunicationSend(),
                    beneficiaryCoresAddress=Address(
                        addressType="1",
                        addressLine1=correspondence_address.full_address,
                        addressLine2="",
                        addressLine3="",
                        addressLine4="",
                        zipcode=correspondence_address.pin,
                        city=correspondence_address.city,
                        statecode=get_state_code(correspondence_address.state),
                        countrycode=get_country_code(correspondence_address.country),
                    ),
                    beneficiaryPermAddress=Address(
                        addressType="4",
                        addressLine1=permanent_address.full_address,
                        addressLine2="",
                        addressLine3="",
                        addressLine4="",
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
                    familyMobileFlag="",
                    familyEmailFlag="",
                    nominationOption="",
                    occupation=None,
                    fatherOrHusbandName="",
                    dpId="",
                    clientId="",
                    sharePercentEqually="",
                    numOfNominees="",
                    listOfNominees=[
                        Nominee(
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
                    ],
                ),
            ),
            bankDetails=BankDetails(
                accountNumber="",
                bankName="",
                ifsc="",
                micr="",
                accountType="",
                bankAddress=BankAddress(
                    addressType="",
                    addressLine1="",
                    addressLine2="",
                    addressLine3="",
                    addressLine4="",
                    zipcode="",
                ),
            ),
        )
    )
    return nsdl_model


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


def getCoomunicationSend(comm: str | None) -> str | None:
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
    return state_mapping.get(state)


def get_country_code(country_name: str) -> str:
    """Returns the country code"""
    country_mapping = None
    if country_mapping is None:
        country_mapping = load_mapping_file(file_name="country.json")
    return country_mapping.get(country_name, "")


def load_mapping_file(self, file_name: str) -> dict:
    with resources.path("lyik.nsdl_mapping_json_file", file_name) as file_path:
        with open(file_path, "r") as file:
            return json.load(file)


def get_wet_signature(wet_signature: DBDocumentModel) -> str:
    """Returns the wet signature value as base64 encoded string"""
    # ToDO: Get the image bytes from the document plugin
    image_bytes = []
    encoded_image = base64.b64encode(image_bytes).decode()
    return encoded_image


def get_number_of_holders(kyc_holders=List[KYCHolder]) -> int:
    """Returns the number of holders"""
    return len(kyc_holders)


def get_list_of_joint_holders(kyc_holders=List[KYCHolder]) -> List[JointHolder]:
    """Returns the list of jointholders"""
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
