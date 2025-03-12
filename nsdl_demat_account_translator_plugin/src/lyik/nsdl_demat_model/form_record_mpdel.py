from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List, Dict, Any
from datetime import datetime
from lyikpluginmanager import DBDocumentModel


class TimeLog(BaseModel):
    created_on: str
    last_updated_on: str


class Submitter(BaseModel):
    id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    time: Optional[datetime] = None


class Metadata(BaseModel):
    org_id: Optional[str] = None
    form_id: Optional[str] = None
    record_id: Optional[str] = None
    doc_type: Optional[str] = None
    digest: Optional[str] = None
    esign: Optional[str] = None


class AddressInfo(BaseModel):
    state: str
    city: str
    country: str
    pin: str
    aadhaar_xml: Optional[str] = None
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
    proof: DBDocumentModel
    type_of_address: str
    full_address: str
    city: str
    state: str
    pin: str
    country: str


class VerificationStatus(BaseModel):
    status: str
    message: str
    id: Optional[str] = None
    actor: str
    user_id: Optional[str] = None
    weight: Optional[Any] = None
    isMandatoryFilled: Optional[bool] = None


class OVD(BaseModel):
    ovd_type: Optional[str] = None
    ovd_front: Optional[DBDocumentModel] = None
    ovd_back: Optional[DBDocumentModel] = None


class IdentityAddressVerification(BaseModel):
    identity_address_info: AddressInfo
    other_info: OtherInfo
    correspondence_address: CorrespondenceAddress
    same_as_permanent_address: Optional[str] = None
    _ver_status: Optional[VerificationStatus] = None
    ovd: Optional[OVD] = None


class UploadImages(BaseModel):
    wet_signature_image: Optional[DBDocumentModel] = None
    proof_of_signature: Optional[DBDocumentModel] = None
    _ver_status: Optional[Optional[VerificationStatus]] = None


class SignatureValidation(BaseModel):
    upload_images: UploadImages
    _ver_status: Optional[VerificationStatus] = None


class IncomeInfo(BaseModel):
    networth: str
    gross_annual_income: str
    occupation: str
    date: datetime


class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: str
    place_of_birth: Optional[str] = None
    country_of_origin: Optional[str] = None
    country_code: Optional[str] = None


class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: Optional[str] = None


class Declarations(BaseModel):
    income_info: IncomeInfo
    fatca_crs_declaration: FATCACRSDeclaration
    politically_exposed_person_card: PoliticallyExposedPersonCard
    _ver_status: Optional[VerificationStatus] = None


class PanDetails(BaseModel):
    name_in_pan: str
    dob_pan: str
    pan_number: str
    parent_guardian_spouse_name: str


class PanVerification(BaseModel):
    pan_details: PanDetails
    pan_card_image: DBDocumentModel
    _ver_status: Optional[VerificationStatus] = None


class MobileVerification(BaseModel):
    dependency_relationship_mobile: str
    contact_id: str
    _ver_status: Optional[VerificationStatus] = None
    verified_contact_id: str


class EmailVerification(BaseModel):
    dependency_relationship_email: str
    contact_id: str
    _ver_status: Optional[VerificationStatus] = None
    verified_contact_id: str


class MobileEmailVerification(BaseModel):
    mobile_verification: MobileVerification
    email_verification: EmailVerification
    _ver_status: Optional[VerificationStatus] = None


class KYCHolderData(BaseModel):
    mobile_email_verification: MobileEmailVerification
    identity_address_verification: IdentityAddressVerification
    signature_validation: SignatureValidation
    declarations: Declarations
    pan_verification: PanVerification


class KYCHolder(BaseModel):
    kyc_holder: KYCHolderData


class BankDetails(BaseModel):
    bank_account_number: str
    account_holder_name: str
    account_holder_name_pan: str
    account_holder_name_id: str
    ifsc_code: str
    type_of_application: str
    _ver_status: Optional[Optional[VerificationStatus]] = None


class CancelledCheque(BaseModel):
    cancelled_cheque_image: Optional[Any] = None


class BankVerification(BaseModel):
    cancelled_cheque: CancelledCheque
    bank_details: BankDetails
    _ver_status: Optional[VerificationStatus] = None


class NomineeData(BaseModel):
    minor_nominee: Optional[str] = None
    nominee_type_of_id: Optional[str] = None
    name_of_nominee: Optional[str] = None
    percentage_of_allocation: Optional[str] = None
    nominee_id_proof: Optional[DBDocumentModel] = None
    id_number: Optional[str] = None
    nominee_address: Optional[str] = None
    dob_nominee: Optional[str] = None


class GuardianData(BaseModel):
    guardian_id_proof: DBDocumentModel
    guardian_type_of_id: str
    guardian_name: str
    guardian_address: str
    guardian_signature: DBDocumentModel
    guardian_id_number: str
    relationship_with_nominee: str


class Nominee(BaseModel):
    nominee_data: NomineeData | None = None
    guardina_data: GuardianData | None = None


class GeneralNomination(BaseModel):
    client_nominee_appointment_status: str


class NominationDetails(BaseModel):
    nominees: List[Nominee]
    general: GeneralNomination
    _ver_status: Optional[VerificationStatus] = None


class IntroducerDetails(BaseModel):
    introducer_name: Optional[str] = None
    introducer_broker_address: Optional[str] = None
    introducer_status: Optional[str] = None
    remisire_code: Optional[str] = None


class TradingAccountInformation(BaseModel):
    segment_pref_1: Optional[str] = None
    segment_pref_2: Optional[str] = None
    segment_pref_3: Optional[str] = None
    segment_pref_4: Optional[str] = None
    segment_pref_5: Optional[str] = None
    segment_pref_6: Optional[str] = None
    type_of_document: Optional[str] = None
    contract_format_1: Optional[str] = None
    contract_format_2: Optional[str] = None
    proof_of_income: Optional[DBDocumentModel] = None
    client_facility_choice: Optional[str] = None
    client_facility_choice: str
    kit_format_1: Optional[str] = None
    kit_format_2: Optional[str] = None
    holder_trading_experience: Optional[str] = None


class CheckPanForTrading(BaseModel):
    trading_id: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_creation_date: Optional[str] = None
    _ver_status: Optional[Optional[VerificationStatus]]


class EmployerDetails(BaseModel):
    employer_name: str
    mobile_number: str
    approval_date: str
    employer_address: str


class DetailsOfDealings(BaseModel):
    broker_name: Optional[str] = None
    telephone: Optional[str] = None
    client_codes: Optional[str] = None
    broker_address: Optional[str] = None
    sub_broker_name: Optional[str] = None
    website: Optional[str] = None
    detail_of_disputes: Optional[str] = None


class IntroducerDetails(BaseModel):
    introducer_name: Optional[str] = None
    introducer_broker_address: Optional[str] = None
    introducer_status: Optional[str] = None
    remisire_code: Optional[str] = None


class TradingInformation(BaseModel):
    introducer_details: IntroducerDetails
    check_pan_for_trading_account: CheckPanForTrading
    trading_account_information: TradingAccountInformation
    employer_details: EmployerDetails
    details_of_dealings: DetailsOfDealings
    introducer_details: IntroducerDetails


class Onboarding(BaseModel):
    type_of_client: str
    _ver_status: Optional[VerificationStatus]


class GeneralApplicationDetails(BaseModel):
    application_type: str
    residential_status: str


class CashFutComoCard(BaseModel):
    cash_minimum_paisa: int
    cash_in_percentage: float


class CashJobbingCard(BaseModel):
    cash_jobbing_minimum_paisa: int
    cash_jobbing_in_percentage: float


class FuturesCard(BaseModel):
    futures_minimum_paisa: int
    futures_in_percentage: float


class OptionsCard(BaseModel):
    options_standard_rate: int


class CurrencyFuturesCard(BaseModel):
    currency_futures_minimum_paisa: int
    currency_futures_in_percentage: float


class CurrencyOptionsCard(BaseModel):
    currency_options_rate: int


class CommodityFuturesCard(BaseModel):
    commodity_futures_minimum_paisa: int
    commodity_futures_in_percentage: float


class CommodityOptionsCard(BaseModel):
    commodity_options_rate: int


class SLBCard(BaseModel):
    slb_rate: int


class FlatPerOrderCard(BaseModel):
    flat_per_order_rate: Optional[Any] = None


class OnlineExeCard(BaseModel):
    online_exe: str


class GSTDetailsCard(BaseModel):
    gst_number: Optional[Any] = None
    gst_number_1: Optional[Any] = None


class ClientContactDetails(BaseModel):
    client_mobile: str


class ApplicationDetails(BaseModel):
    defaults: Optional[Any] = None
    kyc_digilocker: str
    general_application_details: GeneralApplicationDetails
    cash_fut_como_card: CashFutComoCard
    cash_jobbing_card: CashJobbingCard
    futures_card: FuturesCard
    options_card: OptionsCard
    currency_futures_card: CurrencyFuturesCard
    currency_options_card: CurrencyOptionsCard
    commodity_futures_card: CommodityFuturesCard
    commodity_options_card: CommodityOptionsCard
    slb_card: SLBCard
    flat_per_order_card: FlatPerOrderCard
    online_exe_card: OnlineExeCard
    gst_details_card: GSTDetailsCard
    client_contact_details: ClientContactDetails
    segment_rates: Dict[str, Any]
    display_field: Optional[Any] = None
    _ver_status: Optional[VerificationStatus]


class DPAccountInformation(BaseModel):
    dp_tariff_plan: Optional[str] = None
    name_of_dp: Optional[str] = None
    depository: Optional[str] = "NSDL"
    dp_id_no: Optional[str] = None
    client_id_no: Optional[str] = None
    cmr_file: Optional[DBDocumentModel] = None


class StandingInfoFromClient(BaseModel):
    receive_credit_auth_status: str
    first_holder_sms_alert: str
    account_statement_requirement: str
    electronic_transaction_holding_statement: str
    dividend_interest_receive_option: str
    auto_pledge_confirmation: str
    did_booklet_issuance: str
    bsda: str
    joint_account_operation_mode: str
    consent_for_communication: str
    share_email_id_with_rta: str
    receive_annual_report: str
    aadhaar_pan_seed_status: str
    trust: str


class TrustInformation(BaseModel):
    stack_exchange_name: Optional[str] = None
    clearing_member_name: Optional[str] = None
    clearing_member_id: Optional[str] = None


class UCCMapping(BaseModel):
    ucc_code: Optional[str] = None
    exchange_id: Optional[str] = None
    segment_id: Optional[str] = None
    cm_id: Optional[str] = None
    tm_id: Optional[str] = None


class DPInformation(BaseModel):
    dp_Account_information: DPAccountInformation
    standing_info_from_client: StandingInfoFromClient
    trust_information: TrustInformation
    ucc_mapping_1: UCCMapping
    ucc_mapping_2: UCCMapping
    _ver_status: Optional[VerificationStatus] = None


class FormRecordModel(BaseModel):
    payment: Optional[Any] = None
    submitter: Submitter
    state: str
    onboarding: Onboarding
    application_details: ApplicationDetails
    kyc_holders: List[KYCHolder]
    _time_log: Optional[TimeLog] = None
    _application_id: Optional[str] = None
    _owner: Optional[List[str]] = None
    bank_verification: BankVerification
    nomination_details: NominationDetails
    trading_information: TradingInformation
    dp_information: DPInformation
