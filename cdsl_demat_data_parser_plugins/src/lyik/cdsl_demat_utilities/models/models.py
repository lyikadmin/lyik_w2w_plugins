from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    doc_id: str | None = Field(default=None)
    doc_name: str | None = Field(default=None)
    doc_size: int | None = Field(default=None)
    doc_content: str | None = Field(default=None)


class NomineeData(BaseModel):
    minor_nominee: Optional[str] = Field(default=None)
    nominee_type_of_id: Optional[str] = Field(default=None)
    name_of_nominee: Optional[str] = Field(default=None)
    percentage_of_allocation: Optional[str] = Field(default=None)
    nominee_id_proof: Document | None = Field(default=None)
    id_number: Optional[str] = Field(default=None)
    dob_nominee: Optional[str] = Field(default=None)
    nominee_address: Optional[str] = Field(default=None)

    @property
    def is_minor(self) -> bool:
        return self.minor_nominee is not None


class GuardianData(BaseModel):
    guardian_id_proof: Document | None = Field(default=None)
    guardian_type_of_id: Optional[str] = Field(default=None)
    guardian_name: Optional[str] = Field(default=None)
    guardian_address: Optional[str] = Field(default=None)
    guardian_signature: Optional[str] = Field(default=None)
    guardian_id_number: Optional[str] = Field(default=None)
    relationship_with_nominee: Optional[str] = Field(default=None)


class Nominee(BaseModel):
    nominee_data: Optional[NomineeData] = None
    guardian_data: Optional[GuardianData] = None


class General(BaseModel):
    client_nominee_appointment_status: Optional[str] = Field(default=None)


class NominationDetails(BaseModel):
    general: Optional[General] = Field(default=None)
    nominees: List[Nominee] = Field(default_factory=list)

    def __init__(self, payload: Dict[str, Any], **kwargs):
        general_data = payload.get("general")
        if general_data:
            kwargs["general"] = General(**general_data)
        nominees_data = payload.get("nominees", [])
        kwargs["nominees"] = [
            Nominee(
                nominee_data=(
                    NomineeData(**obj["nominee"]["nominee_data"])
                    if obj["nominee"].get("nominee_data")
                    else None
                ),
                guardian_data=(
                    GuardianData(**obj["nominee"]["guardian_data"])
                    if obj["nominee"].get("guardian_data")
                    else None
                ),
            )
            for obj in nominees_data
        ]
        super().__init__(**kwargs)
