from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from lyikpluginmanager import DBDocumentModel


class PanDetails(BaseModel):
    name_in_pan: Optional[str] = None
    dob_pan: Optional[str] = None
    pan_number: Optional[str] = None
    parent_guardian_spouse_name: Optional[str] = None


class PanVerification(BaseModel):
    pan_card_image: Optional[DBDocumentModel] = None
    pan_details: Optional[PanDetails] = None


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


class IdentityAddressInfo(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    country: Optional[str] = None
    pin: Optional[str] = None
    aadhaar_xml: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    uid: Optional[str] = None
    full_address: Optional[str] = None


class IdentityAddressVerification(BaseModel):
    other_info: Optional[OtherInfo] = None
    correspondence_address: Optional[CorrespondenceAddress] = None
    identity_address_info: Optional[IdentityAddressInfo] = None
    same_as_permanent_address: Optional[str] = None


class IncomeInfo(BaseModel):
    gross_annual_income: Optional[str] = None
    networth: Optional[str] = None
    occupation: Optional[str] = None
    date: Optional[str] = None


class FatcaResidencyInfo(BaseModel):
    country_of_residency_1: Optional[str] = None
    tin_no_1: Optional[str] = None
    id_type_1: Optional[str] = None
    reason_if_no_tin_1: Optional[str] = None


class FATCACRSDeclaration(BaseModel):
    is_client_tax_resident: Optional[str] = None
    place_of_birth: Optional[str] = None
    country_of_origin: Optional[str] = None
    country_code: Optional[str] = None


class PoliticallyExposedPersonCard(BaseModel):
    politically_exposed_person: Optional[str] = None


class Declarations(BaseModel):
    income_info: Optional[IncomeInfo] = None
    fatca_crs_declaration: Optional[FATCACRSDeclaration] = None
    politically_exposed_person_card: Optional[PoliticallyExposedPersonCard] = None
    fatca_crs_declaration_1: Optional[FatcaResidencyInfo] = None


class KYCHolder(BaseModel):
    pan_verification: Optional[PanVerification] = None
    identity_address_verification: Optional[IdentityAddressVerification] = None
    declarations: Optional[Declarations] = None


class KYCDataModel(BaseModel):
    kyc_holder: Optional[KYCHolder] = None
