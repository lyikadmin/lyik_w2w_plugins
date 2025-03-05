from datetime import datetime

class BSEUtility:
    def __init__(self, form_record:dict):
        '''
        # Todo: 
        -   Add form_identifier logic based on form_record data.
            This will decide how to get values of record json!
            
        '''
        self.form_record = form_record
        # todo: kyc data based on form-identifier!
        self.kyc_data = form_record.get('kyc_holders', [])[0].get('kyc_holder',{}) if 0< len(form_record.get('kyc_holders', [])) else {}

    def transaction_code_value(self):
        # Values: N=NEW, M=MODIFY
        return 'N'
    
    def client_type_value(self):
        # Values: I - individual, NI - Non-Individual, INS - Institution
        return 'I'
    
    def client_status_value(self):
        # Values:  OW/CL/ER if client type is I or NI, else IN
        return 'CL'
    
    def client_category_value(self):
        # Values as per `**Table showing list of Client Categories as per their Client Status and Client Type.`
        # but currently handling just Individual category i.e no NRI, no Firm, etc..., just Individual.
        # Note: based on this, different other attributes are dicided!
        return 'I'
    
    def pan_num_value(self):
        pan = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('pan_number','')
        return pan or ''

    
    def politically_exposed_value(self):
        politicallY_exposed = self.kyc_data.get('declarations',{}).get('politically_exposed_person_card',{}).get('politically_exposed_person','')
        if politicallY_exposed == 'PEP':
            return 'Y'
        else:
            return 'N'
        
    def permanent_address_value(self):
        address = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('permanent_address','')
        return address or ''
        
    def same_as_permanent_address_value(self):
        is_permanent_address = self.kyc_data.get('identity_address_verification',{}).get('same_as_permanent_address','')
        if is_permanent_address == 'SAME_AS_PERMANENT_ADDRESS':
            return 'Y'
        return 'N'
    
    def corr_address_value(self):
        address = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('correspondence_address','')
        return address
    
    def corr_address_city_value(self):
        city = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('city','')
        return city
    
    def permanent_address_city_value(self):
        city = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('city','')
        return city
    
    def permanent_address_state_value(self):
        return self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('state','')
    
    def corr_address_state_value(self):
        return self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('state','')

    def permanent_address_country_value(self):
        return 'INDIA'#self._country_value(country=self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('country',''))

    def corr_address_country_value(self):
        return 'INDIA'#self._country_value(country=self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('country',''))
    
    def corr_address_pincode_value(self):
        # Todo: pincode only when country selected is India
        pincode = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('pin','')
        return pincode
    
    def permanent_address_pincode_value(self):
        # Todo: pincode only when country selected is India
        pincode = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('pin','')
        return pincode or ''
    
    def contact_details_value(self):
        # Values: 1 = TELEPHONE, 2 = MOBILE, 3 = BOTH
        return '2'
    
    def mobile_no_value(self):
        mobile = self.kyc_data.get('mobile_email_verification',{}).get('mobile_verification',{}).get('contact_id','')
        return mobile or ''
    
    def email_value(self):
        email = self.kyc_data.get('mobile_email_verification',{}).get('email_verification',{}).get('contact_id','')
        return email or ''
    
    def depository_name_value(self):
        depos_name = self.form_record.get('dp_information',{}).get('dp_Account_information',{}).get('depository','')
        if depos_name.lower() == 'nsdl':
            return 'NSDL'
        if depos_name.lower() == 'cdsl':
            return 'CDSL'
        return None
    
    def depository_id_value(self):
        '''
        This field will have length of 8 Alphanumeric characters. 
            a. IN case Depository Name is selected as NSDL - this field will start with “IN” followed by 6 digits number. 
            b. In case Depository Name is selected as CDSL - No input. 

        '''
        # But as per NSE docs - Values: NSDL, CDSL, but their sample imput follows bse doc description!
        return 'IN302164' # todo: source unknown!
    
    def depository_participant_value(self):
        dp = self.form_record.get('dp_information',{}).get('dp_Account_information',{}).get('name_of_dp','')
        return dp
    
    def bank_name_value(self):
         # Todo: Field not exist in form. Optional just for INSTITUTIONS.
        bank_name = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('bank_name','')
        return 'Bank of India'#bank_name
    
    def last_name_value(self):
        name = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('dob_pan','')
        return name
 
    def provide_income_networth_details_value(self):
        income=self.kyc_data.get('declarations',{}).get('income_info',{}).get('gross_annual_income','')
        netoworth=self.kyc_data.get('declarations',{}).get('income_info',{}).get('networth','')
        if income and netoworth:
            return '3'
        if income:
            return '1'
        return ''
    
    def income_value(self):
        income=self.kyc_data.get('declarations',{}).get('income_info',{}).get('gross_annual_income','')
        if income == 'UPTO_1L':
            return '1'
        if income == '1_TO_5L':
            return '2'
        if income == '5_TO_10L':
            return '3'
        if income == '10_TO_25L':
            return '4'
        if income == '25L_TO_1CR':
            return '5'
        if income == '1CR_TO_5CR':
            return '5'
        return None

    
    def gross_income_date_value(self):
        date = self.kyc_data.get('declarations',{}).get('income_info',{}).get('date','')
        return self.format_date(date=date)
    
    def networth_value(self):
        # Optional field
        networth = self.kyc_data.get('declarations',{}).get('income_info',{}).get('networth',None)
        return networth
    
    def networth_date_value(self):
        # mandatory only of networth is specified!
        if not self.networth_value():
            return None
        date = self.kyc_data.get('declarations',{}).get('income_info',{}).get('date','')
        return self.format_date(date=date)
    
    def is_active_value(self):
        # Values: Y = YES, N = NO, C = CLOSE
        return 'Y' # Todo: fix this, source unknown!
    
    def dob_value(self):
        '''
        Gives DoB as in PAN
        '''
        pan_dob = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('dob_pan','')
        return self.format_date(date=pan_dob)
    
    def cash_value(self):
        # Values: Yes (Y) / No (N)
        return None
    
    def equity_derivatives_value(self):
        # for FNO segment
        # Values: Yes (Y) / No (N)
        fno = self.form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_2')
        return 'Y' if fno else 'N'
    
    def slb_value(self):
        # Values: Yes (Y) / No (N)
        slb = self.form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_6')
        return 'Y' if slb else 'N'
    
    def currency_value(self):
        # Values: Yes (Y) / No (N)
        cur = self.form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_2')
        return 'Y' if cur else 'N'
    
    def debt_value(self):
        # Values: Yes (Y) / No (N)
        return None
    
    def commodity_value(self):
        # Values: Yes (Y) / No (N)
        com = self.form_record.get('trading_information',{}).get('trading_account_information',{}).get('segment_pref_4')
        return 'Y' if com else 'N'
    
    def poa_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def poa_for_fund_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def poa_for_security_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    
    def opted_for_nomination_value(self):
        # Values: Opted for Nomination (Y) / Opted out of Nomination (N)
        return None
    
    def bank_ifsc_value(self):
        bank_ifsc = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('ifsc_code','')
        return bank_ifsc
    
    def bank_acc_no_value(self):
        acc_num = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('bank_account_number','')
        return acc_num
    
    def is_primary_or_secondary_bank(self):
        """
        method to check if bank a/c number{index} is Primary or not!
        """
        # Values: P/S.
        return 'P'
    
    def is_primary_or_secondary_dp(self):
        """
        method to check if dp{index} is Primary or not!
        """
        # Values: P/S.
        return 'P'
    
    def type_of_service(self):
        # Todo: values could be 1(SMS), 2(EMAIL), 3(Both), 4(None)
        # Unknown source
        return None
    def opted_for_upi_value(self):
        # Values: Registered - Y, Not opted - N, Not applicable - NA, Deregistered - D
        # Todo: field not available in form. Mandatory, but could be 'N/A' for some categories!
        return 'N'
    

    def format_date(self, date: str) -> str | None:
        """
        returns date in DD-MM-YYYY format
        """
        if not date:
            return None
        try:
            # Parse the input string into a datetime object
            dt = datetime.strptime(date, '%d/%m/%Y')
            # Format the datetime object into the desired format
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            # logger.debug(f"Error in formatting date {date}")
            return None