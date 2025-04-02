from pydantic import BaseModel
from typing import Any
from lyikpluginmanager import DBDocumentModel
from datetime import datetime


class PanDetails(BaseModel):
    name_in_pan: str | None = None
    dob_pan: str | None = None
    pan_number: str | None = None
    parent_guardian_spouse_name: str | None = None


class VerificationStatus(BaseModel):
    status: str | None = None
    message: str | None = None
    id: str | None = None
    actor: str | None = None
    user_id: str | None = None
    weight: Any | None = None
    isMandatoryFilled: bool | None = None


class PanVerification(BaseModel):
    pan_details: PanDetails | None = None
    pan_card_image: DBDocumentModel | None = None
    _ver_status: VerificationStatus | None = None


class OtherInfo(BaseModel):
    father_name: str | None = None
    marital_status: str | None = None
    country_of_birth: str | None = None
    mother_name: str | None = None
    place_of_birth: str | None = None


class CorrespondenceAddress(BaseModel):
    proof: DBDocumentModel | None = None
    type_of_address: str | None = None
    full_address: str | None = None
    city: str | None = None
    state: str | None = None
    pin: str | None = None
    country: str | None = None


class OVD(BaseModel):
    ovd_type: str | None = None
    ovd_front: DBDocumentModel | None = None
    ovd_back: DBDocumentModel | None = None


class IdentityAddressInfo(BaseModel):
    state: str | None = None
    city: str | None = None
    country: str | None = None
    pin: str | None = None
    aadhaar_xml: str | None = None
    name: str | None = None
    gender: str | None = None
    uid: str | None = None
    full_address: str | None = None


class IdentityAddressVerification(BaseModel):
    identity_address_info: IdentityAddressInfo | None = None
    other_info: OtherInfo | None = None
    correspondence_address: CorrespondenceAddress | None = None
    same_as_permanent_address: str | None = None
    _ver_status: VerificationStatus | None = None
    ovd: OVD | None = None


class IncomeInfo(BaseModel):
    networth: str | None = None
    gross_annual_income: str | None = None
    occupation: str | None = None
    date: datetime | None = None


class FatcaResidencyInfo(BaseModel):
    country_of_residency_1: str | None = None
    tin_no_1: str | None = None
    id_type_1: str | None = None
    reason_if_no_tin_1: str | None = None


class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: str | None = None
    place_of_birth: str | None = None
    country_of_origin: str | None = None
    country_code: str | None = None


class FATCACRSDeclaration1(BaseModel):
    country_of_residency_1: str | None = None
    tin_no_1: str | None = None
    id_type_1: str | None = None
    reason_if_no_tin_1: str | None = None


class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: str | None = None


class Declarations(BaseModel):
    income_info: IncomeInfo | None = None
    fatca_crs_declaration: FATCACRSDeclaration | None = None
    politically_exposed_person_card: PoliticallyExposedPersonCard | None = None
    _ver_status: VerificationStatus | None = None
    fatca_crs_declaration_1: FATCACRSDeclaration1 | None = None


class MobileVerification(BaseModel):
    dependency_relationship_mobile: str | None = None
    contact_id: str | None = None
    _ver_status: VerificationStatus | None = None


class EmailVerification(BaseModel):
    dependency_relationship_email: str | None = None
    contact_id: str | None = None
    _ver_status: VerificationStatus | None = None


class MobileEmailVerification(BaseModel):
    mobile_verification: MobileVerification | None = None
    email_verification: EmailVerification | None = None
    _ver_status: VerificationStatus | None = None


class UploadImages(BaseModel):
    wet_signature_image: DBDocumentModel | None = None
    proof_of_signature: DBDocumentModel | None = None
    _ver_status: VerificationStatus | None = None


class SignatureValidation(BaseModel):
    upload_images: UploadImages | None = None
    _ver_status: VerificationStatus | None = None


class KYCHolder(BaseModel):
    mobile_email_verification: MobileEmailVerification | None = None
    identity_address_verification: IdentityAddressVerification | None = None
    signature_validation: SignatureValidation | None = None
    declarations: Declarations | None = None
    pan_verification: PanVerification | None = None


class KYCDataModel(BaseModel):
    kyc_holder: KYCHolder | None = None
