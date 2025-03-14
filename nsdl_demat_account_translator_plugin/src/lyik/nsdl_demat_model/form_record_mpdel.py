from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from lyikpluginmanager import DBDocumentModel
class TimeLog(BaseModel):
    created_on: str | None = None
    last_updated_on: str


class Submitter(BaseModel):
    id: str | None = None
    phone: str | None = None
    email: str | None = None
    time: datetime | None = None


class Metadata(BaseModel):
    org_id: str | None = None
    form_id: str | None = None
    record_id: str | None = None
    doc_type: str | None = None
    digest: str | None = None
    esign: str | None = None


class AddressInfo(BaseModel):
    state: str
    city: str
    country: str
    pin: str
    aadhaar_xml: str | None = None
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
    id: str | None = None
    actor: str
    user_id: str | None = None
    weight: Any | None = None
    isMandatoryFilled: bool | None = None


class OVD(BaseModel):
    ovd_type: str | None = None
    ovd_front: DBDocumentModel | None = None
    ovd_back: DBDocumentModel | None = None


class IdentityAddressVerification(BaseModel):
    identity_address_info: AddressInfo
    other_info: OtherInfo
    correspondence_address: CorrespondenceAddress
    same_as_permanent_address: str | None = None
    _ver_status: VerificationStatus | None = None
    ovd: OVD | None = None


class UploadImages(BaseModel):
    wet_signature_image: DBDocumentModel
    proof_of_signature: DBDocumentModel | None = None
    _ver_status: VerificationStatus | None = None


class SignatureValidation(BaseModel):
    upload_images: UploadImages
    _ver_status: VerificationStatus | None = None


class IncomeInfo(BaseModel):
    networth: str
    gross_annual_income: str
    occupation: str
    date: datetime


class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: str
    place_of_birth: str | None = None
    country_of_origin: str | None = None
    country_code: str | None = None


class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: str | None = None


class Declarations(BaseModel):
    income_info: IncomeInfo
    fatca_crs_declaration: FATCACRSDeclaration
    politically_exposed_person_card: PoliticallyExposedPersonCard
    _ver_status: VerificationStatus | None = None


class PanDetails(BaseModel):
    name_in_pan: str
    dob_pan: str
    pan_number: str
    parent_guardian_spouse_name: str


class PanVerification(BaseModel):
    pan_details: PanDetails
    pan_card_image: DBDocumentModel
    _ver_status: VerificationStatus | None = None


class MobileVerification(BaseModel):
    dependency_relationship_mobile: str
    contact_id: str
    _ver_status: VerificationStatus | None = None


class EmailVerification(BaseModel):
    dependency_relationship_email: str
    contact_id: str
    _ver_status: VerificationStatus | None = None


class MobileEmailVerification(BaseModel):
    mobile_verification: MobileVerification
    email_verification: EmailVerification
    _ver_status: VerificationStatus | None = None


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
    _ver_status: VerificationStatus | None = None


class CancelledCheque(BaseModel):
    cancelled_cheque_image: Any = None


class BankVerification(BaseModel):
    cancelled_cheque: CancelledCheque
    bank_details: BankDetails
    _ver_status: VerificationStatus | None = None


class NomineeData(BaseModel):
    minor_nominee: str | None = None
    nominee_type_of_id: str | None = None
    name_of_nominee: str
    percentage_of_allocation: str | None = None
    nominee_id_proof: DBDocumentModel | None = None
    id_number: str | None = None
    nominee_address: str
    dob_nominee: str


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
    nominees: List[Nominee] = Field(default_factory=list)
    general: GeneralNomination
    _ver_status: VerificationStatus | None = None


class IntroducerDetails(BaseModel):
    introducer_name: str | None = None
    introducer_broker_address: str | None = None
    introducer_status: str | None = None
    remisire_code: str | None = None


class TradingAccountInformation(BaseModel):
    segment_pref_1: str | None = None
    segment_pref_2: str | None = None
    segment_pref_3: str | None = None
    segment_pref_4: str | None = None
    segment_pref_5: str | None = None
    segment_pref_6: str | None = None
    type_of_document: str | None = None
    contract_format_1: str | None = None
    contract_format_2: str | None = None
    proof_of_income: DBDocumentModel | None = None
    client_facility_choice: str | None = None
    client_facility_choice: str
    kit_format_1: str | None = None
    kit_format_2: str | None = None
    holder_trading_experience: str | None = None


class CheckPanForTrading(BaseModel):
    trading_id: str | None = None
    account_holder_name: str | None = None
    account_creation_date: str | None = None
    _ver_status: VerificationStatus | None = None


class EmployerDetails(BaseModel):
    employer_name: str
    mobile_number: str
    approval_date: str
    employer_address: str


class DetailsOfDealings(BaseModel):
    broker_name: str | None = None
    telephone: str | None = None
    client_codes: str | None = None
    broker_address: str | None = None
    sub_broker_name: str | None = None
    website: str | None = None
    detail_of_disputes: str | None = None


class IntroducerDetails(BaseModel):
    introducer_name: str | None = None
    introducer_broker_address: str | None = None
    introducer_status: str | None = None
    remisire_code: str | None = None


class TradingInformation(BaseModel):
    introducer_details: IntroducerDetails
    check_pan_for_trading_account: CheckPanForTrading
    trading_account_information: TradingAccountInformation
    employer_details: EmployerDetails
    details_of_dealings: DetailsOfDealings
    introducer_details: IntroducerDetails


class Onboarding(BaseModel):
    type_of_client: str
    _ver_status: VerificationStatus | None


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
    flat_per_order_rate: Any = None


class OnlineExeCard(BaseModel):
    online_exe: str


class GSTDetailsCard(BaseModel):
    gst_number: Any = None
    gst_number_1: Any = None


class ClientContactDetails(BaseModel):
    client_mobile: str


class ApplicationDetails(BaseModel):
    defaults: Any = None
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
    display_field: Any = None
    _ver_status: VerificationStatus | None = None


class DPAccountInformation(BaseModel):
    dp_tariff_plan: str | None = None
    name_of_dp: str | None = None
    depository: str | None = "NSDL"
    dp_id_no: str | None = None
    client_id_no: str | None = None
    cmr_file: DBDocumentModel | None = None


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
    stack_exchange_name: str | None = None
    clearing_member_name: str | None = None
    clearing_member_id: str | None = None


class UCCMapping(BaseModel):
    ucc_code: str | None = None
    exchange_id: str | None = None
    segment_id: str | None = None
    cm_id: str | None = None
    tm_id: str | None = None


class DPInformation(BaseModel):
    dp_Account_information: DPAccountInformation
    standing_info_from_client: StandingInfoFromClient
    trust_information: TrustInformation
    ucc_mapping_1: UCCMapping
    ucc_mapping_2: UCCMapping
    _ver_status: VerificationStatus | None = None


class FormRecordModel(BaseModel):
    # payment: Any | None = None
    # submitter: Submitter | None = None
    # state: str | None = None
    onboarding: Onboarding | None = None
    application_details: ApplicationDetails | None = None
    kyc_holders: List[KYCHolder]
    # _time_log: TimeLog | None = None
    # _application_id: str | None = None
    # _owner: List[str] | None = None
    bank_verification: BankVerification | None = None
    nomination_details: NominationDetails | None = None
    trading_information: TradingInformation | None = None
    dp_information: DPInformation | None = None
