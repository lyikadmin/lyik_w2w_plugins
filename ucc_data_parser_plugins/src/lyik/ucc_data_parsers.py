import apluggy as pluggy
from datetime import datetime
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    UCCDataParserSpec,
    GenericFormRecordModel,
    NSEPayload,
    NSEEntry,
    BSEPayload,
)
# from enum import Enum

from typing import List, Dict
from typing_extensions import Doc, Annotated

# import importlib
import logging
from .ucc_data_parser_utilities.bse_utility import BSEUtility
from .ucc_data_parser_utilities.nse_utility import NSEUtility
logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

class UCCDataParser(UCCDataParserSpec):

    @impl
    async def ucc_data_parse(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("form record data"),
        ],
    ) -> Annotated[NSEPayload | BSEPayload, Doc('Data required for UCC/UCI api')]:
        """
        This method formulates form record payload into NSEPayload or BSEPayload based on NSDL or CDSL selection.
        """
        _form_record = form_record.model_dump()
        # Todo: find out the form structure/type based on certain field availability in form-record.
        depository = _form_record.get('dp_information',{}).get('dp_Account_information',{}).get('depository','')
        if depository == 'NSDL':
            return await self.ucc_nse_data_parse(context=context,form_record=form_record)
        elif depository == 'CDSL':
            return await self.ucc_bse_data_parse(context=context,form_record=form_record)
        else:
            raise Exception('Depository value not found, cannot proceed!')
    
        
    async def ucc_bse_data_parse(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("form record fow which the pdf need to be generated"),
        ],
    ) -> Annotated[BSEPayload, Doc('Data required for BSE UCC/UCI')]:
        """
        This method formulates form record payload into BSEPayload 
        """
        # Note: 
        # 1. for BSE api invokation, optional fields to be filled with None(null in json)
        # 2. Date format: dd/mm/yyyy
        _form_record = form_record.model_dump()
        bse_utility = BSEUtility(form_record=_form_record)
        kyc_data = _form_record.get('kyc_holders', [])[0].get('kyc_holder',{}) if 0< len(_form_record.get('kyc_holders', [])) else {}
        # Todo: All values to be coming from utility functions baased on form record structure and conditions!
        bse_data = BSEPayload(
            TRANSACTIONCODE=bse_utility.transaction_code_value(), # N - New, M - Modify
            BATUSER=None, # optional
            CLIENTTYPE=bse_utility.client_type_value(), # I - individual, NI - Non-Individual, INS - Institution
            STATUS=bse_utility.client_status_value(), # Client Status: OW/CL/ER if client type is I or NI, else IN
            CATEGORY=bse_utility.client_category_value(), # Todo: This should come from form record?, as there are multiple categories for each client type
            CLIENTCODE="ABC123", # Todo: client code, source unknown. Is it to be a Generated code?
            PANNO=bse_utility.pan_num_value(),
            POLITICALEXPERSON=bse_utility.politically_exposed_value(),
            ADDRESS1=bse_utility.permanent_address_value(), # Permanent address?
            PERMNEQUALCORP=bse_utility.same_as_permanent_address_value(),
            ADDRESS2=bse_utility.corr_address_value(), # correpondence address
            
            COUNTRY=bse_utility.corr_address_country_value(),
            STATE=bse_utility.corr_address_state_value(),
            CITY=bse_utility.corr_address_city_value(),
            PINCODE=bse_utility.corr_address_pincode_value(),
            
            TYPEOFSERVICE=bse_utility.type_of_service(), # Todo: unknown source
            CONTACTDETAILS=bse_utility.contact_details_value(), # putting mobile for now!

            EMAIL=bse_utility.email_value(),
            MOBILENUMBER=bse_utility.mobile_no_value(),
            
            STDCODE=None, # No telephone field -> it's optional
            PHONENO=None, # No telephone field -> it's optional
            EQ_CPCODE=None, # optional
            EQCMID=None, # optional
            FNOCPCODE=None, # optional
            FNOCMID=None, # optional

            DEPOSITORYNAME1=bse_utility.depository_name_value(),
            DEMANTID1=bse_utility.depository_id_value(), # Todo: is it depository/dp id? unknown # form_record.get('dp_information',{}).get('dp_Account_information',{}).get('dp_id_no','')
            DEPOSITORYPARTICIPANT1=bse_utility.depository_participant_value(),
            DEPOSITORYNAME2=None, # optional
            DEMANTID2=None, # optional
            DEPOSITORYPARTICIPANT2=None, # optional
            DEPOSITORYNAME3=None, # optional
            DEMANTID3=None, # optional
            DEPOSITORYPARTICIPANT3=None, # optional

            BANKNAME1=bse_utility.bank_name_value(), # Todo: Field not exist in form. Optional just for INSTITUTIONS.
            ACCOUNTNO1=bse_utility.bank_acc_no_value(),
            BANKNAME2=None, # optional
            ACCOUNTNO2=None, # optional
            BANKNAME3=None, # optional
            ACCOUNTNO3=None, # optional
            CLIENTAGGREMENTDATE=None, # Or account opening date, # optional
            PROVIDEDETAILS=bse_utility.provide_income_networth_details_value(),
            INCOME=bse_utility.income_value(),
            INCOMEDATE=bse_utility.gross_income_date_value(),
            NETWORTH=bse_utility.networth_value(),
            NETWORTHDATE=bse_utility.networth_date_value(),
            ISACTIVE=bse_utility.is_active_value(),
            UPDATEREASON=None, # Mandatory if the users modify Client Status/Client Category, else Optional.
            FIRSTNAME=None, # Todo: unknown field
            MIDDLENAME=None, # Todo: unknown field
            LASTNAME=bse_utility.last_name_value(), # filling fullname as name fields are distributed!
            AADHARCARDNO=None, # Todo: can be filled from form record data but optional

            DATEOFBIRTH=bse_utility.dob_value(), # PAN DoB
            CLIENTNAME=None, # optional for client type Individual
            REGISTRATIONNO=None, # Mandatory for FPI
            REGISTERINGAUTHORITY=None, # Mandatory for FPI
            DATEOFREGISTRATION=None, # Mandatory for FPI
            PLACEOFREGISTRATION=None, # Optional
            WHETHERCORPORATE=None, # optional for client type Individual
            CINNO=None, # optional for client category BCO or WHETHERCORPORATE = 'Y'
            NUMBEROFDIRECTORS=None,# Mandatory for client category ‘BCO’ or if user selects ‘Whether Corporate CIN?
            PARTNERS_KARTAUID=None, # Optional, can be filled if client category is HUF/PF
            PARTNERS_COPARCENERUID=None, # Optional, can be filled if client category is HUF/PF
            CONTACTPERSONNAME1=None, # optional for client type Individual
            CONTACTPERSONDESIGNATION1=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONADDRESS1=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONEMAIL1=None, # optional
            CONTACTPERSONPAN1=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONMOBILE1=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONNAME2=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONDESIGNATION2=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONADDRESS2=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONEMAIL2=None, # Optional
            CONTACTPERSONPAN2=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CONTACTPERSONMOBILE2=None, # Mandatory if Client Type is NON-INDIVIDUAL
            CASH=bse_utility.cash_value(), # for CASH segment, # no option of this option in segments
            EQUITY_DERIVATIVE=bse_utility.equity_derivatives_value(), # for FNO segment
            SLB=bse_utility.slb_value(), # for SLB segment
            CURRENCY=bse_utility.currency_value(), # for CURRENCY segment
            DEBT=bse_utility.debt_value(), # for DEBT segment
            ISPOA=bse_utility.poa_value(),
            POAFORFUND=bse_utility.poa_for_fund_value(),
            POAFORSECURITY=bse_utility.poa_for_security_value(),
            DATEOFPOAFORFUND=None, # optional
            DATEOFPOAFORSECURITY=None, # optional
            PERCITY=bse_utility.permanent_address_city_value(),
            PERSTATE=bse_utility.permanent_address_state_value(), 
            PERCOUNTRY=bse_utility.permanent_address_country_value(), # Todo: Is it address country or Select India or USA field value
            PERPINCODE=bse_utility.permanent_address_pincode_value() ,
            CURRENCYCPCODE=None, # optional
            CURRENCYCMID=None, # optional
            ENROLLMENTNUMBER=None, # optional
            COMMDERIVATIVES=bse_utility.commodity_value(), # for Commodity segment
            OPTEDFORNOMINATION=bse_utility.opted_for_nomination_value(), # optional
            CUSTPANNO=None, # Mandatory for client type Institution
            CUSTNAME=None, # Mandatory for client type Institution
            CUSTADDRESS=None, # Mandatory for client type Institution
            CUSTCOUNTRY=None, # Mandatory for client type Institution
            CUSTSTATE=None, # Mandatory for client type Institution
            CUSTCITY=None, # Mandatory for client type Institution
            CUSTPINCODE=None, # Mandatory for client type Institution
            CUSTMOBILENUMBER=None, # Mandatory for client type Institution
            CUSTSTDCODE=None, # Mandatory for client type Institution
            CUSTPHONENO=None, # Mandatory for client type Institution
            CUSTEMAIL=None, # Mandatory for client type Institution
            EGR=None, # for EGR egment, optional
            BENEFICIALOWNACNTNO1="", #Todo: unknown source/formfield, Mandatory for INDIVIDUAL/NON-INDIVIDUALS
            BENEFICIALOWNACNTNO2=None, # optional
            BENEFICIALOWNACNTNO3=None, # optional
            OPTED_FOR_UPI=bse_utility.opted_for_upi_value(), # Todo: field not available in form. Mandatory, but could be 'N/A' for some categories!

            BANKBRANCHIFSCCODE1=bse_utility.bank_ifsc_value(), # Optional for INSTITUTIONS.
            PRIMARYORSECONDARYBANK1=bse_utility.is_primary_or_secondary_bank(), # Todo: form doesn't have more than 1 bank details? Optional for INSTITUTIONS.
            BANKBRANCHIFSCCODE2=None, # optional
            PRIMARYORSECONDARYBANK2=None, # optional
            BANKBRANCHIFSCCODE3=None, # optional
            PRIMARYORSECONDARYBANK3=None, # optional
            BANKBRANCHIFSCCODE4=None, # optional
            BANKNAME4=None, # optional
            ACCOUNTNO4=None, # optional
            PRIMARYORSECONDARYBANK4=None, # optional
            BANKBRANCHIFSCCODE5=None, # optional
            BANKNAME5=None, # optional
            ACCOUNTNO5=None, # optional
            PRIMARYORSECONDARYBANK5=None, # optional
            PRIMARYORSECONDARYDP1=bse_utility.is_primary_or_secondary_dp(), # Optional just for INSTITUTIONS.
            PRIMARYORSECONDARYDP2=None, # Todo: form doesn't have more than 1 dp?
            PRIMARYORSECONDARYDP3 = None, # optional
            DEMANTID4 = None, # optional
            BENEFICIALOWNACNTNO4 = None, # optional
            PRIMARYORSECONDARYDP4 = None, # optional
            DEPOSITORYNAME4 = None, # optional
            DEMANTID5 = None, # optional
            BENEFICIALOWNACNTNO5 = None, # optional
            PRIMARYORSECONDARYDP5 = None, # optional
            DEPOSITORYNAME5 = None, # optional

            CLIENTNAMEDESCRIPTION = None, # optional
            DIRECTORDETAILS = None, # optional
            SERVERIP=None, # optional
                
        )

        return bse_data


    async def ucc_nse_data_parse(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("form record data"),
        ],
    ) -> Annotated[NSEPayload, Doc('Data required for NSE UCC/UCI')]:
        """
        This method formulates form record payload into NSEPayload 
        """
        # Note: 
        # 1. for NSE api invokation, optional fields to be filled with ''

        ### TODO:
        # 1. PREPARE A GENERIC/COMMON NSEEntry() instance.
        # 2. based on selected segments, take a copy and modify the relevent attributes and add that [nse_entries]
        
        _form_record = form_record.model_dump()
        nse_utility = NSEUtility(form_record=_form_record)
        kyc_data = _form_record.get('kyc_holders', [])[0].get('kyc_holder') if 0< len(_form_record.get('kyc_holders', [])) else {}
        is_permanent_address_same = nse_utility.same_as_permanent_address_value()
        _aadhaar_uid = ''
        if (
            str(_form_record.get('application_details',{}).get('kyc_digilocker','')).lower()!='no'
            or
            str(kyc_data.get('identity_address_verification',{}).get('ovd',{}).get('ovd_type','')).lower() == 'aadhaar'
        ):
            _aadhaar_uid = kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('uid','')

        NSE_MEMERCODE = "11502" # todo: this should come from env! same value as username
        base_nse_data = NSEEntry(
            ccdMemCd=NSE_MEMERCODE,
            ccdAcctType=nse_utility.account_type_value(),
            ccdOptForUpi=nse_utility.opted_for_upi_value(),
            ccdCd='ABC123', # Todo: client code, source unknown. Is it to be a Generated code?
            ccdName=nse_utility.client_name_value(),
            ccdCategory=nse_utility.client_category_value(), # Todo: decide client category based on form record data!
            ccdTelNo='', # optional
            ccdAgrDt='', # optional
            ccdPanNo=nse_utility.pan_num_value(),
            
            ccdBankName=nse_utility.bank_name_value(),  # Todo: Field not exist in form. Optional just for INSTITUTIONS.
            
            ccdBankIfsc=nse_utility.bank_ifsc_value(), # Optional for INSTITUTIONS.
            ccdBankAcctNo=nse_utility.bank_acc_no_value(),
            ccdPriSecBnk=nse_utility.is_primary_or_secondary_bank(), # Todo: form doesn't have more than 1 bank details? Optional for INSTITUTIONS.
            ccdDeposName=nse_utility.depository_name_value(),
            ccdBenAcctNo=nse_utility.beneficial_acc_num_value(), # Todo: Beneficial A/c Number - Unknown field, unknown source, is Mandatory!
            ccdDeposId=nse_utility.depository_id_value(),
            ccdPriSecDp=nse_utility.is_primary_or_secondary_dp(),
            ccdRegNo='', # unknown source, mandatory for certain categories 
            ccdRegAuth='', # unknown source, mandatory for certain categories 
            ccdPlcReg='', # unknown source, mandatory for certain categories 
            ccdDtReg='', # unknown source, mandatory for certain categories 
            ccdSegInd= '', #nse_utility.segment_indicator_value(),
            ccdDob=nse_utility.dob_value(),
            ccdAddLine1=nse_utility.corr_address_value(), # correpondence address
            ccdAddLine2='', # optional
            ccdAddLine3='', # optional
            ccdAddCity=nse_utility.corr_address_city_value(), 
            ccdAddState=nse_utility.corr_address_state_value(),
            ccdAddCountry=nse_utility.corr_address_country_value(), 
            ccdPinCode=nse_utility.corr_address_pincode_value(), # Todo: pincode only when country selected is India
            ccdTelIsd='', # optional and No telephone field
            ccdTelStd='', # optional and No telephone field
            ccdMobile=nse_utility.mobile_no_value(),
            ccdEmail=nse_utility.email_value(),
            ccdProofType='', # mandatory only for PAN_EXEMPT
            ccdProofNo='', # mandatory only for PAN_EXEMPT
            ccdIssPlcProof='', # mandatory only for PAN_EXEMPT
            ccdIssDtProof='', # mandatory only for PAN_EXEMPT
            ccdDir1Name='', # optional just for category type Individual(1)
            ccdDir2Name='', # optional just for category type Individual(1)
            ccdDir3Name='', # optional just for category type Individual(1)
            ccdDir1Desig='', # optional just for category type Individual(1)
            ccdDir2Desig='', # optional just for category type Individual(1)
            ccdDir3Desig='', # optional just for category type Individual(1)
            ccdDir1Pan='', # optional just for category type Individual(1)
            ccdDir2Pan='', # optional just for category type Individual(1)
            ccdDir3Pan='', # optional just for category type Individual(1)
            ccdDir1Add='', # optional just for category type Individual(1)
            ccdDir2Add='', # optional just for category type Individual(1)
            ccdDir3Add='', # optional just for category type Individual(1)
            ccdDir1TelNo='', # optional just for category type Individual(1)
            ccdDir2TelNo='', # optional just for category type Individual(1)
            ccdDir3TelNo='', # optional just for category type Individual(1)
            ccdDir1Email='', # optional just for category type Individual(1)
            ccdDir2Email='', # optional just for category type Individual(1)
            ccdDir3Email='', # optional just for category type Individual(1)
            ccdIpv=nse_utility.inperson_verification_value(), # Todo: field not well defined!
            ccdUccCd='', # Mandatory only for SLB Segment and certain client categories
            ccdRelationship='', # optional, require in members having alpha relationship only(annexure 4), i.e apart from spouse, dependent parent, dependent child.
            ccdTvFlag='', # optional
            ccdFacilityType='', # optional
            ccdCin='', # CIN is mandatory for client category 4 & 32.
            ccdCltStatus=nse_utility.client_status_value(), # Todo: Unknown field source
            ccdCltStatusReason='', # optional
            ccdGender=nse_utility.gender_value(),
            ccdGuardianName=nse_utility.guardian_name_value(), # Todo: We're putting Father/Spouse name instead of Guardian Name!
            ccdMaritlStatus=nse_utility.marital_status_value(),
            ccdNationality=nse_utility.nationality_value(), # Todo: Nationality field missing in form
            ccdPermantAddFlg=is_permanent_address_same,
            ccdPermAddLine1= nse_utility.permanent_address_value() if is_permanent_address_same != 'Y' else '',
            ccdPermAddLine2='', # optional
            ccdPermAddLine3='', # optional
            ccdPermAddCity=nse_utility.permanent_address_city_value() if is_permanent_address_same != 'Y' else '',
            ccdPermAddState=nse_utility.permanent_address_state_value() if is_permanent_address_same != 'Y' else '',
            ccdPermAddCountry=nse_utility.permanent_address_country_value() if is_permanent_address_same != 'Y' else '',
            ccdPermPin= nse_utility.permanent_address_pincode_value() if is_permanent_address_same != 'Y' else '',
            ccdOffcIsd='', # optional
            ccdOffcStd='', # optional
            ccdTelOffice='', # optional
            ccdUid='',#_aadhaar_uid, # Todo: if aadhaar not applicable for client, then '999999999999'
            ccdBankName2='', # optional
            ccdBankIfsc2='',# optional
            ccdBankAcctNo2='', # optional
            ccdPriSecBnk2='', # optional
            ccdBankName3='', # optional
            ccdBankAcctNo3='', # optional
            ccdPriSecBnk3='', # optional
            ccdBankIfsc3='', # optional
            ccdBankName4='', # optional
            ccdBankAcctNo4='', # optional
            ccdPriSecBnk4='', # optional
            ccdBankIfsc4='', # optional
            ccdBankName5='', # optional
            ccdBankAcctNo5='', # optional
            ccdPriSecBnk5='', # optional
            ccdBankIfsc5='', # optional
            ccdDeposName2='', # optional
            ccdDeposId2='', # optional
            ccdBenAcctNo2='', # optional
            ccdPriSecDp2='', # optional
            ccdDeposName3='', # optional
            ccdDeposId3='', # optional
            ccdBenAcctNo3='', # optional
            ccdPriSecDp3='', # optional
            ccdDeposName4='', # optional
            ccdDeposId4='', # optional
            ccdBenAcctNo4='', # optional
            ccdPriSecDp4='', # optional
            ccdDeposName5='', # optional
            ccdDeposId5='', # optional
            ccdBenAcctNo5='', # optional
            ccdPriSecDp5='', # optional
            ccdGrosAnnlRnge=nse_utility.gross_income_value(),
            ccdGrosAnnlAsdate=nse_utility.gross_income_date_value(),
            ccdNetWorth= '', #nse_utility.networth_value(), # optional
            ccdNetWorthAsdate='', #nse_utility.networth_date_value(), # mandatory only of networth is specified!
            ccdPep=nse_utility.polotically_exposed_value(),
            ccdPoi='', # Applicable for category other than 1, 11, 18, 25, 26, 27 & 31
            ccdOccupation=nse_utility.occupation_value(),
            ccdOccupationDtls=nse_utility.occupation_details_value(), # Todo: field not available in form
            ccdBusComDt='', # optional
            ccdCpCd='', # CP code is mandatory for categories 6,7,8,9,12,16,22,23 & 24
            ccdClntTyp='', # Mandatory for category other than 1, 11, 18 , 25, 26, 27, 2, 3, 5, 31 & 36
            ccdDinCntrctPerson1='', # optoinal for category 1, unknown field!
            ccdUidCntrctPerson1='', #  optional
            ccdDinCntrctPerson2='', # optional
            ccdUidCntrctPerson2='', # optional
            ccdDinCntrctPerson3='', # optional
            ccdUidCntrctPerson3='', # optional
            ccdDir4Name='', # optional
            ccdDir4Desig='', # optional
            ccdDir4Pan='', # optional
            ccdDir4Add='', # optional
            ccdDir4TelNo='', # optional
            ccdDinCntrctPerson4 = '', # optional
            ccdUidCntrctPerson4 = '', # optional
            ccdDir4Email='', # optional
            ccdDir5Name='', # optional
            ccdDir5Desig='', # optional
            ccdDir5Pan='', # optional
            ccdDir5Add='', # optional
            ccdDir5TelNo='', # optional
            ccdDinCntrctPerson5='', # optional
            ccdUidCntrctPerson5='', # optional
            ccdDir5Email='', # optional
            ccdNationalityOth = '', # Todo: APPLICABLE FOR CATEGORY 1, 11, 18, 25, 26, 27, 31 & 36 and Mandatory if Nationality is '2'
            ccdPermAddStateOth = '', # Mandatory if State Code is '99', In case of No State: "NOT APPLICABLE"
            ccdAddStateOth = '', # Mandatory if State Code is '99', In case of No State: "NOT APPLICABLE"
            
            ccdPoaFunds = nse_utility.poa_funds_value(), # Todo: Power of Attorney (POA) for funds - unknown and mandatory
            ccdPoaSecurities = nse_utility.pos_securities_value(), # Todo: Power of Attorney (POA) for Securities - unknown and mandatory
            ccdCpName = '', # optional
            ccdCpPan = '', # optional
            ccdCpEmail = '', # optional
            ccdCpStd = '', # optional
            ccdCpIsd = '', # optional
            ccdCpTel = '', # optional
            ccdCpMob = '', # optional
            ccdCpAdd = '', # optional
            ccdCpAddCity='', # optional
            ccdCpAddState = '', # optional
            ccdCpAddStateOth = '', # optional
            ccdCpAddCountry = '', # optional
            ccdCpAddPin = '', # optional
            ccdNomFlag = '' # optional
        )

        segment_pref_1= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_1',''))
        segment_pref_2= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_2',''))
        segment_pref_3= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_3',''))
        segment_pref_4= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_4',''))
        segment_pref_5= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_5',''))
        segment_pref_6= nse_utility.segment_indicator_value(segment=_form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_6',''))
        nse_entries = []

        # TODO: update other values too which are depending on segment!
        if segment_pref_1: # EQUITY
            equity_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_1
                }
            )
            nse_entries.append(equity_nse_entry)

        if segment_pref_2: # FNO
            fno_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_2
                }
            )
            nse_entries.append(fno_nse_entry)

        if segment_pref_3: # CURRENCY
            currency_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_3
                }
            )
            nse_entries.append(currency_nse_entry)

        if segment_pref_4: # COMMODITY
            commodity_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_4
                }
            )
            nse_entries.append(commodity_nse_entry)

        if segment_pref_5: # MUTUAL_FUND
            mf_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_5
                }
            )
            nse_entries.append(mf_nse_entry)

        if segment_pref_6: # SLB
            # Todo: ccdUccCd: it's mandatory for SLB segment
            slb_nse_entry = base_nse_data.model_copy(
                update={
                    'ccdSegInd': segment_pref_6
                }
            )
            nse_entries.append(slb_nse_entry)

        return NSEPayload(
            nse_entries=nse_entries
        )

    
    
    # def _get_enum_value_from_key(self,key): 
    #     if not key:
    #         return ""
    #     # Prepend '_' if the key starts with a number 
    #     if key[0].isdigit(): 
    #         key = f"_{key}"
    #     try: 
    #         return FieldMapHelper[key].value 
    #     except KeyError: 
    #         logger.debug(f"{key} - not matched with any of the options")
    #         return ""
    
    # def _get_bse_formatted_date(self,date:str):
    #     """
    #     returns date in dd/mm/yyyy format
    #     """
    #     if not date:
    #         return ""
    #     try:
    #         # Parse the input string into a datetime object 
    #         dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') 
    #         # Format the datetime object into the desired format 
    #         return dt.strftime('%d/%m/%Y')
    #     except ValueError:
    #         logger.debug(f"Error in formatting date {date}")
    #         return None
        
    # moved to nse_utility :)
    # def _get_nse_formatted_date(self, date: str) -> str:
    #     """
    #     returns date in DD-MM-YYYY format
    #     """

    #     if not date:
    #         return ""
    #     try:
    #         # Parse the input string into a datetime object
    #         dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    #         # Format the datetime object into the desired format
    #         return dt.strftime('%d-%m-%Y')
    #     except ValueError:
    #         logger.debug(f"Error in formatting date {date}")
    #         return ''
        
# class FieldMapHelper(Enum):
#     # PEP 
#     PEP = "Politically Exposed Person"
#     RELATED = "Related to Politically Exposed Person"
#     NA = "Not Applicable"
    
#     SAME_AS_PERMANENT_ADDRESS = "Same as Permanent Address"

#     # Genders
#     M = "Male"
#     F = "Female"
#     T = "Transgender"

#     # Marital Status
#     MARRIED = "Married"
#     SINGLE = "Single"

    # Occupation
    # PRIVATE_SECTOR = "Private Sector"
    # PUBLIC_SECTOR = "Public Sector"
    # GOVT_SERVICE = "Govt. Service"
    # PROFESSIONAL = "Professional"
    # HOUSE_WIFE = "Housewife"
    # STUDENT = "Student"
    # SALARIED = "Salaried"
    # SELF_EMPLOYED = "Self employed"
    # BUSINESS = "Business"
    # AGRICULTURIST = "Agranulturist"
    # RETIRED = "Retired Person"
    # OTHERS = "Others"
