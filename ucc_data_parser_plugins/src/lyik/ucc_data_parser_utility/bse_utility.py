class BSEUtility:
    def __init__(self, form_record:dict):
        '''
        # Todo: 
        -   Add form_identifier logic based on form_record data.
            This will decide how to get values of record json!
            
        '''
        self.form_record = form_record
        # todo: kyc data based on form-identifier!
        self.kyc_data = form_record.get('kyc_holders', [])[0] if 0< len(form_record.get('kyc_holders', [])) else {}

    def politically_exposed_value(self):
        politicallY_exposed = self.kyc_data.get('declarations',{}).get('politically_exposed_person_card',{}).get('politically_exposed_person','')
        if politicallY_exposed == 'PEP':
            return 'Y'
        else:
            return 'N'
        
    def same_as_permanent_address_value(self):
        is_permanent_address = self.kyc_data.get('identity_address_verification',{}).get('same_as_permanent_address','')
        if is_permanent_address == 'SAME_AS_PERMANENT_ADDRESS':
            return 'Y'
        return 'N'
    
    def contact_details_value(self):
        # Values: 1 = TELEPHONE, 2 = MOBILE, 3 = BOTH
        return '2'
    
    def depository_name_value(self):
        depos_name = self.form_record.get('dp_information',{}).get('dp_Account_information',{}).get('depository','')
        if depos_name.lower() == 'nsdl':
            return 'NSDL'
        if depos_name.lower() == 'cdsl':
            return 'CDSL'
        return None
    
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
    
    def is_active_value(self):
        # Values: Y = YES, N = NO, C = CLOSE
        return 'Y' # Todo: fix this
    
    def cash_value(self, value:str):
        # Values: Yes (Y) / No (N)
        return None
    
    def equity_derivatives_value(self):
        # Values: Yes (Y) / No (N)
        return None
    
    def slb_value(self, value:str):
        # Values: Yes (Y) / No (N)
        return None
    
    def currency_value(self):
        # Values: Yes (Y) / No (N)
        return None
    
    def debt_value(self):
        # Values: Yes (Y) / No (N)
        return None
    
    def poa_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def poa_for_fund_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def poa_for_security_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def commodity_derivatives_value(self):
        # Values: Yes (Y) / No (N)
        return 'N'
    
    def opted_for_nomination_value(self):
        # Values: Opted for Nomination (Y) / Opted out of Nomination (N)
        return None
    
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