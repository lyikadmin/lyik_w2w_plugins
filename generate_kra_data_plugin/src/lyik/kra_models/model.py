from pydantic import BaseModel
from typing import Optional, Any
from lyikpluginmanager import DBDocumentModel
from datetime import datetime


class PanDetails(BaseModel):
    name_in_pan: str
    dob_pan: str
    pan_number: str
    parent_guardian_spouse_name: str


class VerificationStatus(BaseModel):
    status: str
    message: str
    id: str | None = None
    actor: str
    user_id: str | None = None
    weight: Any | None = None
    isMandatoryFilled: bool | None = None


class PanVerification(BaseModel):
    pan_details: PanDetails
    pan_card_image: DBDocumentModel
    _ver_status: VerificationStatus | None = None


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


class OVD(BaseModel):
    ovd_type: str | None = None
    ovd_front: DBDocumentModel | None = None
    ovd_back: DBDocumentModel | None = None


class IdentityAddressInfo(BaseModel):
    state: str
    city: str
    country: str
    pin: str
    aadhaar_xml: str | None = None
    name: str
    gender: str
    uid: str
    full_address: str


class IdentityAddressVerification(BaseModel):
    identity_address_info: IdentityAddressInfo
    other_info: OtherInfo
    correspondence_address: CorrespondenceAddress
    same_as_permanent_address: str | None = None
    _ver_status: VerificationStatus | None = None
    ovd: OVD | None = None


class IncomeInfo(BaseModel):
    networth: str
    gross_annual_income: str
    occupation: str
    date: datetime


class FatcaResidencyInfo(BaseModel):
    country_of_residency_1: Optional[str] = None
    tin_no_1: Optional[str] = None
    id_type_1: Optional[str] = None
    reason_if_no_tin_1: Optional[str] = None


class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: str
    place_of_birth: str | None = None
    country_of_origin: str | None = None
    country_code: str | None = None


class FATCACRSDeclaration1(BaseModel):
    country_of_residency_1: str
    tin_no_1: str | None = None
    id_type_1: str | None = None
    reason_if_no_tin_1: str | None = None


class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: str | None = None


class Declarations(BaseModel):
    income_info: IncomeInfo
    fatca_crs_declaration: FATCACRSDeclaration
    politically_exposed_person_card: PoliticallyExposedPersonCard
    _ver_status: VerificationStatus | None = None
    fatca_crs_declaration_1: FATCACRSDeclaration1 | None = None


class MobileVerification(BaseModel):
    dependency_relationship_mobile: str
    contact_id: str
    _ver_status: VerificationStatus | None = None
    verified_contact_id: str


class EmailVerification(BaseModel):
    dependency_relationship_email: str
    contact_id: str
    _ver_status: VerificationStatus | None = None
    verified_contact_id: str


class MobileEmailVerification(BaseModel):
    mobile_verification: MobileVerification
    email_verification: EmailVerification
    _ver_status: VerificationStatus | None = None


class UploadImages(BaseModel):
    wet_signature_image: DBDocumentModel
    proof_of_signature: DBDocumentModel | None = None
    _ver_status: VerificationStatus | None = None


class SignatureValidation(BaseModel):
    upload_images: UploadImages
    _ver_status: VerificationStatus | None = None


class KYCHolder(BaseModel):
    mobile_email_verification: MobileEmailVerification
    identity_address_verification: IdentityAddressVerification
    signature_validation: SignatureValidation
    declarations: Declarations
    pan_verification: PanVerification


class KYCDataModel(BaseModel):
    kyc_holder: Optional[KYCHolder] = None
