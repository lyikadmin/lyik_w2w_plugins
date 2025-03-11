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
        context:ContextModel,
        form_record: Annotated[GenericFormRecordModel, Doc("Form Record")],
    ) -> Annotated[NSDLRquestModel, Doc("The Desired output for NSDL Demat")]:
        """
        This function is to translate form record into NSDL demat request model
        """
        try:
            # Validating the form record

            form_record_model = FormRecordModel.model_validate(form_record.model_dump())

            # Map the form record to NSDL demat request model
            nsdl_model = map_form_record(form_record_model=form_record_model)

            # with open(
            #     "/Users/rahulc/Lyik/lyik_w2w_plugins/nsdl_demat_account_translator_plugin/src/lyik/demat_paload.json",
            #     "r",
            #     encoding="utf-8",
            # ) as file:
            #     json_data = json.load(file)
            #     data = NSDLRquestModel.model_validate(json_data)
            #     return data
            
            return nsdl_model
        except Exception as e:
            # ToDo: handle exception
            print(f"Error occurred during translation: {e}")
            return None

