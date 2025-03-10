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
)
from .nsdl_demat_model.form_record_mpdel import (
    FormRecordModel,
    ApplicationData,
    TradingInformation,
)
import json


def map_form_record(form_record_model: FormRecordModel) -> NSDLRquestModel:
    """
    This function maps the form record model to the NSDL root model and returns.
    """
    
    nsdl_model = NSDLRquestModel() #ToDo: Map the form record to NSDLRrquestModel
    return nsdl_model
