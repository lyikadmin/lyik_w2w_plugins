from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List, Dict, Any
from datetime import datetime

class TimeLog(BaseModel):
    created_on: datetime
    last_updated_on: datetime

class Submitter(BaseModel):
    id: str
    phone: str
    email: EmailStr
    time: datetime

class Metadata(BaseModel):
    org_id: Optional[str]
    form_id: Optional[str]
    record_id: Optional[str]
    doc_type: Optional[str]
    digest: Optional[str]
    esign: Optional[str]

class Document(BaseModel):
    doc_id: str
    doc_name: str
    doc_size: int
    doc_content: Optional[Any]
    metadata: Metadata

class AddressInfo(BaseModel):
    state: str
    city: str
    district: str
    country: str
    pin: str
    aadhaar_xml: str
    name: str
    gender: str
    uid: str
    full_address: str

class OtherInfo(BaseModel):
    father_name: str
    marital_status: str
    country_of_birth: str
    mother_name: str
    place_of_birth: str

class CorrespondenceAddress(BaseModel):
    proof: Document
    type_of_address: str
    full_address: str

class VerificationStatus(BaseModel):
    isMandatoryFilled: bool

class IdentityAddressVerification(BaseModel):
    identity_address_info: AddressInfo
    other_info: OtherInfo
    correspondence_address: CorrespondenceAddress
    _ver_status: VerificationStatus

class UploadImages(BaseModel):
    wet_signature_image: Optional[Any]
    proof_of_signature: Optional[Any]
    _ver_status: Optional[VerificationStatus]

class SignatureValidation(BaseModel):
    upload_images: UploadImages
    _ver_status: VerificationStatus

class IncomeInfo(BaseModel):
    networth: str
    gross_annual_income: str
    occupation: str
    date: datetime

class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: str
    place_of_birth: str
    country_of_origin: str
    country_code: str

class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: Optional[str]

class Declarations(BaseModel):
    income_info: IncomeInfo
    fatca_crs_declaration: FATCACRSDeclaration
    politically_exposed_person_card: PoliticallyExposedPersonCard
    _ver_status: VerificationStatus

class PanDetails(BaseModel):
    name_in_pan: str
    dob_pan: str
    pan_number: str
    parent_guardian_spouse_name: str

class PanVerification(BaseModel):
    pan_details: PanDetails
    pan_card_image: Document
    _ver_status: VerificationStatus

class KYCHolderData(BaseModel):
    identity_address_verification: IdentityAddressVerification
    signature_validation: SignatureValidation
    declarations: Declarations
    pan_verification: PanVerification

class KYCHolder(BaseModel):
    kyc_holder: KYCHolderData

class BankDetails(BaseModel):
    bank_account_number: str
    account_holder_name: str
    branch_code: str
    ifsc_code: str
    _ver_status: Optional[VerificationStatus]

class CancelledCheque(BaseModel):
    cancelled_cheque_image: Optional[Any]

class BankVerification(BaseModel):
    cancelled_cheque: CancelledCheque
    bank_details: BankDetails
    _ver_status: VerificationStatus

class NomineeData(BaseModel):
    minor_nominee: Optional[str]
    nominee_type_of_id: Optional[str]
    name_of_nominee: Optional[str]
    percentage_of_allocation: Optional[str]
    nominee_id_proof: Optional[str]
    id_number: Optional[str]
    nominee_address: Optional[str]

class Nominee(BaseModel):
    nominee_data: NomineeData

class GeneralNomination(BaseModel):
    client_nominee_appointment_status: str

class NominationDetails(BaseModel):
    nominees: List[Nominee]
    general: GeneralNomination
    _ver_status: VerificationStatus

class IntroducerDetails(BaseModel):
    introducer_name: Optional[str]
    introducer_broker_address: Optional[str]
    introducer_status: Optional[str]
    remisire_code: Optional[str]

class TradingAccountInformation(BaseModel):
    segment_pref_1: Optional[str]
    segment_pref_2: Optional[str]
    segment_pref_3: Optional[str]
    segment_pref_4: Optional[str]
    segment_pref_5: Optional[str]
    segment_pref_6: Optional[str]
    type_of_document: Optional[str]
    contract_format_1: Optional[str]
    contract_format_2: Optional[str]
    proof_of_income: Optional[str]
    client_facility_choice: Optional[str]
    kit_format_1: Optional[str]
    kit_format_2: Optional[str]
    holder_trading_experience: Optional[str]

class CheckPanForTrading(BaseModel):
    trading_id: Optional[str]
    account_holder_name: Optional[str]
    account_creation_date: Optional[Dict[str, Any]]
    _ver_status: Optional[VerificationStatus]

class TradingInformation(BaseModel):
    introducer_details: IntroducerDetails
    check_pan_for_trading_account: CheckPanForTrading
    trading_account_information: TradingAccountInformation

class OperationCard(BaseModel):
    operation_type: str

class Operations(BaseModel):
    operation_card: OperationCard

class ApplicationData(BaseModel):
    _id: int
    payment: Optional[Any]
    submitter: Submitter
    state: str
    kyc_holders: List[KYCHolder]
    _time_log: TimeLog
    _application_id: str
    _owner: List[str]
    bank_verification: BankVerification
    nomination_details: NominationDetails
    trading_information: TradingInformation
    operations: Operations

class FormRecordModel(BaseModel):
    form_record: ApplicationData