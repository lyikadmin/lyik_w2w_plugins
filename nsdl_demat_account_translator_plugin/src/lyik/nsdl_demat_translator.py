import apluggy as pluggy
import requests
from datetime import datetime
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
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
from .nsdl_demat_model.form_record_mpdel import FormRecordModel
from .form_record_mapping import map_form_record
from typing import Annotated
from typing_extensions import Doc
import json

impl = pluggy.HookimplMarker(getProjectName())


class NSDLDemat(NSDLDematSpec):
    """"""

    @impl
    async def translate_to_nsdl_demat(
        self,
        context: ContextModel,
        form_record: Annotated[GenericFormRecordModel, Doc("Form Record")],
    ) -> Annotated[NSDLRquestModel, Doc("The Desired output for NSDL Demat")]:
        """
        This function is to translate form record into NSDL demat request model
        """
        # Validating the form record

        form_record_model = FormRecordModel.model_validate(form_record.model_dump())

        # Map the form record to NSDL demat request model
        nsdl_model = map_form_record(form_record_model=form_record_model, context = context)

        return nsdl_model
