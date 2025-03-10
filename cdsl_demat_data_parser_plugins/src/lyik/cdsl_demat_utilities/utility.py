from lyikpluginmanager.models.cdsl.helper_enums import *
from lyikpluginmanager.models.cdsl.state_codes import StateCode

class HolderType(str, Enum):
    KYC_HOLDER = 'KYC Holder'
    NOMINEE = 'Nominee'
    NOMINEE_GUARDIAN = 'Nominee Guardian'

class AddressType(str, Enum):
    COR = 'Corresepondence Address'
    PERM = 'Permanent Address'

class CDSLDematUtility:
    def __init__(self, form_record:dict):
        '''
        # Todo: 
        -   Add form_identifier logic based on form_record data.
            This will decide how to get values of record json!
            
        '''
        self.form_record = form_record
        # todo: kyc data based on form-identifier!
        self.kyc_data = [kyc_holder.get('kyc_holder',{}) for kyc_holder in form_record.get('kyc_holders', []) ] #form_record.get('kyc_holders', [])[0].get('kyc_holder',{}) if 0< len(form_record.get('kyc_holders', [])) else {}

    def product_number_value(self):
        # Product Number / Client Type
        return ProductNumber.IND # condidering client type of Individual only!
    
    def beneficiary_subtype_value(self):
        # Todo: why not just Individual(INDVL)?
        return BeneficiarySubType.INRES # Individual-Resident / Ordinary
    
    def purpose_value(self, holder_type:HolderType, index:int):
        # Todo: this method only handles holder(FH,SH,TH), nominee(NM) and Nominee-Guardian(NMG) types, not even guardian(GD) and other types!
        if holder_type==HolderType.KYC_HOLDER:
            if index == 0:
                return Purpose.FH 
            if index == 1:
                return Purpose.SH
            if index == 1:
                return Purpose.TH
            
        if holder_type==HolderType.NOMINEE:
            return Purpose.NM
        
        if holder_type == HolderType.NOMINEE_GUARDIAN:
            return Purpose.NMG
        
        return Purpose.DFT
    
    def first_name_value(self,index):
        # Todo: Putting (full) name as per PAN, as fname, mnane, lname fields are not present in form!
        fullname = self.kyc_data[index].get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')
        return fullname
    
    def father_or_husband_name_value(self, index):
        # Todo: Need clarity for this field, field name and description are seemd to be differnt!
        name = self.kyc_data[index].get('pan_verification',{}).get('pan_details',{}).get('parent_guardian_spouse_name','')
        return name # currently returning spouse/father name
    
    def dob_value(self, index):
        '''
        Gives DoB as in PAN
        '''
        pan_dob = self.kyc_data[index].get('pan_verification',{}).get('pan_details',{}).get('dob_pan','')
        return self.format_date(date=pan_dob)
    
    def gender_value(self, index):
        gender = self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('gender_aadhaar','')
        if not gender:
            return None
        if gender == 'M':
            return Gender.MALE
        if gender == 'F':
            return Gender.FMALE
        if gender == 'T':
            return Gender.TRGEN
        
        return Gender.DFT
    
    def pan_num_value(self,index):
        pan = self.kyc_data[index].get('pan_verification',{}).get('pan_details',{}).get('pan_number','')
        return pan
    
    def pan_verification_flag(self,index):
        # Mandatory only when PAN is present
        pan = self.pan_num_value(index=index)
        if not pan:
            return None
        flag = PANVerificationFlag.PANATC # PAN Verified,Aadhar link to be checked
        return flag
    
    # def aadhaar_uid_value(self, index):
    #     return ''

    def aadhaar_authenticated_value(self, index):
        # Aadhaar Authenticated with UIDAI/ UID VERIFICATION FLAG
        # Todo: if digilocker aadhaar, return 'ADRV', else 'ADRNV'
        return None
    
    def sms_facility_value(self):
        # Todo: value in 2 places: under TnC section and also in dp_information!
        sms_selection = self.form_record.get('dp_information',{}).get('standing_info_from_client',{}).get('first_holder_sms_alert','')
        if not sms_selection:
            return SMSFacility.DFT
        if sms_selection == 'NO': # Todo: need to check whether it's 'NO' or something else
            return SMSFacility.NO
        
        return SMSFacility.YES
    
    def primary_isd_code_value(self,index:int):
        # Currenly setting '91' hard coded!
        return '91'
    
    def mobile_num_value(self, index):
        mobile = self.kyc_data[index].get('mobile_email_verification',{}).get('mobile_verification',{}).get('contact_id','')
        return mobile
    
    def email_value(self, index):
        email = self.kyc_data[index].get('mobile_email_verification',{}).get('email_verification',{}).get('contact_id','')
        return email
    
    def family_flag_email_value(self, index):
        # Todo: unknown source of data
        return FamilyFlagForEmail.DFT
    
    def mode_of_operation_value(self):
        # Mode of Operation: 
        # # todo: need clarity on what the field is? 
        #           whether it is sole holder vs 1+ holder 
        #           or some other field value like field having first holder, all joint holder options!
        #           as one option include any one(ANOSUR) too

        if len(self.kyc_data)==1:
            return ModeOfOperation.SLHLD
        return ModeOfOperation.JTHLDR # why not ANOSUR(any one or survivor)?
        
    def standing_instruction_indicator_value(self):
        # unkown source of data
        return StandingInstructionIndicator.DFT
    
    def gross_income_value(self, index):
        income=self.kyc_data[index].get('declarations',{}).get('income_info',{}).get('gross_annual_income','')
        if income == 'UPTO_1L':
            return GrossAnnualIncomeRange.UPT1L.value
        if income == '1_TO_5L':
            return GrossAnnualIncomeRange._1LT5L.value
        if income == '5_TO_10L':
            return GrossAnnualIncomeRange._5LTXL.value
        if income == '10_TO_25L':
            return GrossAnnualIncomeRange.XLTXXV.value
        if income == '25L_TO_1CR':
            return GrossAnnualIncomeRange._25T1CR.value
        if income == '1CR_TO_5CR':
            return GrossAnnualIncomeRange.GT1CR.value
        return GrossAnnualIncomeRange.DFT.value
    
    def bank_ifsc_value(self):
        bank_ifsc = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('ifsc_code','')
        return bank_ifsc
    
    def bank_micrcd_value(self):
        bank_micrid = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('micr_code','') # Todo: field not present in form!
        return '', #bank_micrid

    def ecs_mandate_value(self):
        # Todo: unknown field source
        return ECSMandate.DFT # Todo: need to be changed as we get more info
    

    def exchange_value(self):
        # Todo: Does CDSL repository means exchange to be filled as BSE, and NSE for NSDL?
        depository = self.form_record.get('dp_information',{}).get('dp_Account_information',{}).get('depository','')
        if depository=='NSDL':
            return Exchange.NSE
        if depository == 'CDSL':
            return Exchange.BSE
        return Exchange.DFT
    
    def nationality_value(self):
        # Todo: Nationality field missing in form
        
        return Nationality.IN
    
    def bank_account_type_value(self):
        # Todo: account type field missing in form
        return BankAccountType.DFT
    
    def bo_category_value(self):
        return BOCategory.NHB # Todo: Need a deciding factor
    
    def bank_acc_no_value(self):
        acc_num = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('bank_account_number','')
        return acc_num 
    
    def tax_deduction_status(self):
        # Currently considering just RI type of clients!
        return BeneficiaryTaxDeductionStatus.RI
    
    def bsda_flag_value(self):
        bsda_flag = self.form_record.get('dp_information',{}).get('standing_info_from_client',{}).get('bsda','')
        if bsda_flag == 'YES':
            return BSDAFlag.BSDA
        if bsda_flag == 'NO':
            return BSDAFlag.NBSD
        return BSDAFlag.DFT
    
    def occupation_value(self, index):
        occupation=self.kyc_data[index].get('declarations',{}).get('income_info',{}).get('occupation','')
        if occupation == 'PUBLIC_SECTOR':
            return Occupation.PUS
        if occupation == 'PRIVATE_SECTOR':
            return Occupation.PRS
        if occupation == 'GOVT_SERVICE':
            return Occupation.GOV
        if occupation == 'BUSINESS':
            return Occupation.BUS
        if occupation == 'PROFESSIONAL':
            return Occupation.PRO
        if occupation == 'AGRICULTURIST':
            return Occupation.FAR
        if occupation == 'RETIRED':
            return Occupation.RET
        if occupation == 'HOUSE_WIFE':
            return Occupation.HOU
        if occupation == 'STUDENT':
            return Occupation.STU
        if occupation == 'OTHERS':
            return Occupation.OTH
        return Occupation.DFT
    
    def communication_pref_value(self):
        com_pref = self.form_record.get('dp_information', {}).get('standing_info_from_client', {}).get('first_holder_sms_alert','')
        if com_pref == 'FIRST_HOLDER':
            return CommunicationPreference.FIH
        if com_pref == 'ALL_HOLDERS':
            return CommunicationPreference.ALH
        return CommunicationPreference.DFT
    

    def account_opening_source_value(self):
        return AccountOpeningSource.OLAO # Todo: Unknown source of data

    def sender_reference_number_value(self, index):
        # Unknown source of data
        return f'AOI781{index}'
    
    def holder_purpose_code_value(self, address_type:AddressType):
        if address_type==AddressType.COR:
            return PurposeCode.CORAD
        if address_type==AddressType.PERM:
            return PurposeCode.PERAD
        return PurposeCode.DFT
    
    def holder_address_value(self, index, address_type:PurposeCode):
        if address_type==PurposeCode.CORAD:
            return self.kyc_data[index].get('identity_address_verification',{}).get('correspondence_address',{}).get('correspondence_address','')
        return self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('permanent_address','')

    def is_permanent_address(self,index):
        return True if self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('permanent_address','') else False

    def is_corr_address(self,index):
        return True if self.kyc_data[index].get('identity_address_verification',{}).get('correspondence_address',{}).get('correspondence_address','') else False

    def holder_country_value(self, index,address_type:PurposeCode ):
        if address_type==PurposeCode.CORAD:
            country=self.kyc_data[index].get('identity_address_verification',{}).get('correspondence_address',{}).get('country','')
        elif address_type==PurposeCode.PERAD:
            country = self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('country','')
        else:
            return None
        return self._country_value(country=str(country).lower())
    
    def holder_address_pincode(self, index, address_type:PurposeCode):
        if address_type==PurposeCode.CORAD:
            return self.kyc_data[index].get('identity_address_verification',{}).get('correspondence_address',{}).get('pin','')
        if address_type==PurposeCode.PERAD:
            return self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('pin','')
        return None
    
    def holder_state_code(self, index, address_type:PurposeCode):
        if address_type==PurposeCode.CORAD:
            state=self.kyc_data[index].get('identity_address_verification',{}).get('correspondence_address',{}).get('country','')
        elif address_type==PurposeCode.PERAD:
            state = self.kyc_data[index].get('identity_address_verification',{}).get('identity_address_info',{}).get('country','')
        else:
            return None
        return StateCode.get(state, 'DFT')

    def _country_value(self,country:str):
        
        country_code = AddressCountryCode.IN if country == 'india' else AddressCountryCode.DFT
        return country_code
    

    def format_date(self, date: str) -> str:
        """
        returns date in YYYY-MM-DD format
        """
        from datetime import datetime

        if not date:
            return None
        try:
            # Parse the input string into a datetime object
            # dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            dt = datetime.strptime(date, '%d/%m/%Y')
            # Format the datetime object into the desired format
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            # logger.debug(f"Error in formatting date {date}")
            return None

