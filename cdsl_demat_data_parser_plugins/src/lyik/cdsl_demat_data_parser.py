import asyncio
import csv
import json

import apluggy as pluggy
from datetime import datetime
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    CDSLPayloadDataParserSpec,
    GenericFormRecordModel,
    CDSLDematPayloadModel,
    HolderRecord,
    NomineeRecord,
    NomineeGuardianRecord,
)
from lyikpluginmanager.models.cdsl.helper_enums import *

# from enum import Enum
# from .cdsl_demat_utilities.utility import CDSLDematUtility, HolderType, AddressType

from cdsl_demat_utilities.utility import CDSLDematUtility, HolderType, AddressType

from typing import List, Dict
from typing_extensions import Doc, Annotated
from datetime import date, datetime

# import importlib
import logging

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class CDSLDematDataParser(CDSLPayloadDataParserSpec):

    @impl
    async def parse_data_to_cdsl_payload(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("The form record for which the data has to be submitted"),
        ],
    ) -> CDSLDematPayloadModel:
        """
        This function is to get the payload(s) for creating a demat account in CDSL
        """
        serial_number = 0
        _form_record = form_record.model_dump()
        date_today = date.today()
        datetime_now = datetime.now()
        cdsl_utility = CDSLDematUtility(form_record=_form_record)
        holders = []
        signatures = []
        for index, holder in enumerate(cdsl_utility.kyc_data):
            # First fill the common attributes for all holders
            # Entry for Permanent Address PurposeCode
            serial_number += 1
            holder_first_purpose = None
            holder_second_purpose = None
            if cdsl_utility.is_permanent_address(
                index=index
            ) and cdsl_utility.is_corr_address(index=index):
                holder_first_purpose = PurposeCode.PERAD
                holder_second_purpose = PurposeCode.CORAD
            elif cdsl_utility.is_corr_address(index=index):
                holder_first_purpose = PurposeCode.CORAD
            else:
                holder_first_purpose = PurposeCode.DFT

            _holder = HolderRecord(
                CntrlSctiesDpstryPtcpt="",  # TODO: unknown source, mandatory!
                BrnchId="000000",  # always 000000 for cdsl-BO upload!
                # BtchId= 100000,# Todo: Unknown source,
                # SndrId='', # Todo: unknown source
                # CntrlSctiesDpstryPtcptRole=DPType.DF, # Not appicable for CDSL
                # SndrDt=date_today, # TODO: unknown source
                # RcvDt=datetime_now, # Todo: Conditional Required, condition unknown!
                RcrdNb=index
                + 1,  # Todo: Will have same value for all lines of single client
                RcdSRNumber=serial_number,  # Todo: this should be filled dynamically while preparing final payload!
                BOTxnTyp=BOTransactionType.BOSET,  # Creation type
                # ClntId = '', # Need 16 digit client id, source unknown!
                PrdNb=cdsl_utility.product_number_value(),  # Considering client type of Individual only for now!
                # BnfcrySubTp=cdsl_utility.beneficiary_subtype_value(), # Todo: Conditional Required, condition unknown!
                Purpse=cdsl_utility.purpose_value(
                    holder_type=HolderType.KYC_HOLDER, index=index
                ),
                # Todo: Conditional Required, condition unknown!
                # Titl= ,# Todo: Conditional Required, condition unknown!
                FrstNm=cdsl_utility.first_name_value(
                    index=index
                ),  # Todo: Conditional Required, condition unknown!
                # MddlNm='', # field not present in form and Conditional Required
                # LastNm='', # field not present in form and Conditional Required
                # FSfx='', # field not present in form and Conditional Required
                # BnfcryShrtNm='', # blank for cdsl, and Conditional Required
                ScndHldrNmOfFthr=cdsl_utility.father_or_husband_name_value(index=index),
                # Todo: Conditional Required, condition unknown! Also need calrity on field.
                BirthDt=cdsl_utility.dob_value(index=index),
                Gndr=cdsl_utility.gender_value(index=index),
                PAN=cdsl_utility.pan_num_value(index=index),
                PANVrfyFlg=cdsl_utility.pan_verification_flag(index=index),
                # PANXmptnCd=PANExemptedCode.DFT, # Todo: unknow field source, not applicable for current state of form!
                # UID='', # Todo: we don't have full aadhaar number. Also it's conditional field, and condition unknown
                # AdhrAuthntcnWthUID=cdsl_utility.aadhaar_authenticated_value(index=index), # Todo: Conditional Required, condition unknown!
                SMSFclty=cdsl_utility.sms_facility_value(),  # Todo: Conditional Required, condition unknown!
                PrmryISDCd=cdsl_utility.primary_isd_code_value(index=index),
                # Mandatory in case of CDSL Account opening optional for others.
                MobNb=cdsl_utility.mobile_num_value(index=index),
                # Mandatory in case of CDSL Account opening optional for others.
                # ScndryISDCd='', # secondary mobile num not present in form
                # SrcCMBPID='', # secondary mobile num not present in form
                EmailAdr=cdsl_utility.email_value(index=index),
                # FmlyFlgForEmailAdr=cdsl_utility.family_flag_email_value(index=index),  # Todo: Conditional Required, condition unknown! Field source also unknown.
                # AltrnEmailAdr=None, # field not available in form,  Conditional Required, condition unknown!
                MdOfOpr=cdsl_utility.mode_of_operation_value(),
                # Todo: Mandatory for BO Upload(Creation), Unknown field source, need clarity!
                # ClrMmbId='',# unknown source, Conditional Required, condition unknown!
                # StgInstr=cdsl_utility.standing_instruction_indicator_value(), # Todo: Conditional Required, condition unknown! Field source also unknown.
                GrssAnlIncmRg=cdsl_utility.gross_income_value(index=index),
                # LEI='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # LEIExp='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # OneTmDclrtnFlgForGSECIDT='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                INIFSC=cdsl_utility.bank_ifsc_value(),
                MICRCd="000110485003",  # cdsl_utility.bank_micrcd_value(), # Todo: Required, and  Field source unknown.
                # DvddCcy='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # DvddBkCcy='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # RBIApprvdDt=None, # Todo: Conditional Required, condition unknown! Field source also unknown.
                # RBIRefNb='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # Mndt= cdsl_utility.ecs_mandate_value(),  # Todo: Conditional Required, condition unknown! Field source also unknown.
                # SEBIRegNb='',  # Todo: Conditional Required, condition unknown! Field source also unknown.
                # EdctnLvl= cdsl_utility.education_level_value(), # Todo: Conditional Required, condition unknown! Field source also unknown.
                AnlRptFlg=cdsl_utility.annual_report_flag(),
                BOStatementCycleCode=cdsl_utility.bo_statement_cycle_code_value(),
                ElctrncConf=cdsl_utility.electronic_confiramtion_value(),
                EmailRTADwnldFlg=cdsl_utility.email_rta_download_value(),
                # GeoCd='', # unknown source of data
                Xchg=cdsl_utility.exchange_value(),  # Todo: need clarity on field
                # MntlDsblty='', # unknown source of data
                Ntlty=cdsl_utility.nationality_value(),
                # Todo: Conditional Required, condition unknown! Field source also unknown.
                PldgStgInstrFlg=cdsl_utility.pledge_instruction_value(),
                BkAcctTp=cdsl_utility.bank_account_type_value(),
                # Todo: Mandatory for BO Upload, field not present in form!
                BnfcryAcctCtgy=cdsl_utility.bo_category_value(),
                # Todo: Mandatory for BO Upload, field not present in form!
                BnfcryBkAcctNb=cdsl_utility.bank_acc_no_value(),
                BnfcryTaxDdctnSts=cdsl_utility.tax_deduction_status_value(),
                # Todo: Conditional Required, condition unknown! Field source also unknown.
                # ClrSysId='', unknown field source
                BSDAFlg=cdsl_utility.bsda_flag_value(),
                Ocptn=cdsl_utility.occupation_value(index=index),
                FrstClntOptnToRcvElctrncStmtFlg=cdsl_utility.first_client_option_to_recieve_statement_value(),
                # Todo: need to confirm data source in form!
                ComToBeSentTo=cdsl_utility.communication_pref_value(),
                # DelFlg='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                # RsnCdDeltn='',# Todo: Field source also unknown.
                # DtOfDeath='', # Todo: Conditional Required, condition unknown! Field source also unknown.
                AccntOpSrc=cdsl_utility.account_opening_source_value(),
                # Mandatory field, hard coded to 'OLAO'(Online Account opening by the BO)
                #### more unknown fields
                SndrRefNb1=cdsl_utility.sender_reference_number_value(index=index),
                # Mandatory for BO Upload, hard coded to 'AOI781'
                PurpCd=holder_first_purpose,
                Adr1=cdsl_utility.holder_address_value(
                    index=index, address_type=holder_first_purpose
                ),
                # Mandatory for BO Upload
                Ctry=cdsl_utility.holder_country_value(
                    index=index, address_type=holder_first_purpose
                ),
                PstCd=cdsl_utility.holder_address_pincode(
                    index=index, address_type=holder_first_purpose
                ),
                CtrySubDvsnCd=cdsl_utility.holder_state_code(
                    index=index, address_type=holder_first_purpose
                ),
            )

            # if index == 0:
            #     # update and Fill first holder specific attributes! DO it here or Outside the loop!
            #     print()

            holders.append(_holder)

            ## todo: Fill it later! Only few fields need to be filled?
            # if holder_second_purpose:
            #     serial_number = serial_number+=1
            #     _holder_entry2 = HolderRecord(

            #     )
            # holders.append(_holder_entry2)

        # SrlNbr(serial number rof nominee), RcdSRNumber(serial_number) also need to be added!

        # nominee and nominee guardian record
        nominees_records: List[NomineeRecord] = []
        nominees_guardians: List[NomineeGuardianRecord] = []

        for index, data in enumerate(cdsl_utility.nominees()):
            nominee = data.nominee_data
            guardian_data = data.guardian_data
            # nominee data
            nominee_record = NomineeRecord(
                BOTxnTyp=BOTransactionType.BOSET,
                Purpse=Purpose.NM,
                FrstNm=cdsl_utility.nominee_first_name(nominee),
                BirthDt=cdsl_utility.nominee_dob(nominee),  # Unknown source
                NmneeMnrInd=cdsl_utility.nominee_minor_indicator(),
                RltshWthBnfclOwnr=None,  # Unknown source
                # Address fields not separately available
                Adr1=None,  #
                Adr2=None,
                Adr3=None,
                Adr4=None,
                NmneePctgOfShr=nominee.percentage_of_allocation,
                SrlNbr=index + 1,  # Not applicable for CDSL
                FlgForShrPctgEqlty=None,  # todo: write method
                RsdlSecFlg=None,  # Unknown source
                PurpCd=cdsl_utility.nominee_purpose_code(),
            )
            nominees_records.append(nominee_record)

            # NOMINEE GUARDIAN RECORD
            if nominee.is_minor:
                guardian_record = NomineeGuardianRecord(
                    BOTxnTyp=BOTransactionType.BOSET,
                    Purpse=Purpose.NMG,
                    # Address fields not separately available
                    Adr1=None,
                    Adr2=None,
                    Adr3=None,
                    Adr4=None,
                    FrstNm=cdsl_utility.nominee_guardian_name(guardian_data),
                    RltshWthBnfclOwnr=None,  # Source unknown
                    PurpCd=cdsl_utility.nominee_guardian_purpose_code(),
                )

                nominees_guardians.append(guardian_record)

        all_entries = []
        for hold in holders:
            all_entries.append(hold)
        for nominee in nominees_records:
            all_entries.append(nominee)
        for nm in nominees_guardians:
            all_entries.append(nm)

        signatures = cdsl_utility.get_all_signature_ids()

        response = CDSLDematPayloadModel(records=all_entries, signatures=signatures)

        return response


async def main():
    cd = CDSLDematDataParser()
    with open(
        "form_with_ovd_1103.json",
        "r",
        encoding="utf-8",
    ) as file:
        jd = json.load(file)
        data = GenericFormRecordModel.model_validate(jd)
    response = await cd.parse_data_to_cdsl_payload(
        context=ContextModel(), form_record=data
    )

    # Serialize each record individually
    records_json = [record.model_dump_json() for record in response.records]

    # Write the JSON data to the file
    with open("test.json", "w+", encoding="utf-8") as f:
        f.write(str(records_json))  # Use json.dump to write JSON to file


if __name__ == "__main__":
    asyncio.run(main())
