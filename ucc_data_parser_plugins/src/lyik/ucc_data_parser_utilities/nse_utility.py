from datetime import datetime

class NSEUtility:

    def __init__(self, form_record:dict):
        '''
        # Todo: 
        -   Add form_identifier logic based on form_record data.
            This will decide how to get values of record json!
            
        '''
        self.form_record = form_record
        # todo: kyc data based on form-identifier!
        self.kyc_data = form_record.get('kyc_holders', [])[0].get('kyc_holder',{}) if 0< len(form_record.get('kyc_holders', [])) else {}

    def polotically_exposed_value(self):
        val = self.kyc_data.get('declarations',{}).get('politically_exposed_person_card',{}).get('politically_exposed_person','')
        if val == 'PEP':
            return '1'
        elif val == 'RELATED':
            return '2'
        elif val == 'NA':
            return '0'
        return ''
    
    def account_type_value(self):
        # Values: OWN, ERROR, CLIENT
        return 'CLIENT'
    
    def opted_for_upi_value(self):
        # Values: Registered - Y, Not opted - N, Not applicable - NA, Deregistered - D

        ## -- on trying, found that: ccdOptForUpi should be NA for other than C(cash) segment
        return 'NA'
    
    def client_name_value(self):
        # Name of the Client must be in full- first name, middle name, surname.
        # fname = ''
        # mname = ''
        # lname = ''
        # fullname = ''
        # if fname:
        #     fullname = fname
        # if mname:
        #     fullname = f'{fullname} {mname}'
        # if lname:
        #     fullname = f'{fullname} {lname}'

        fullname = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')
        return fullname or ''
    
    def client_category_value(self):
        # Todo: decide client category based on form record data!
        # Values: '1','2'....,'36' for different categories
        return '1'
    
    def pan_num_value(self):
        pan = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('pan_number','')
        return pan or ''
    
    def bank_name_value(self):
         # Todo: Field not exist in form. Optional just for INSTITUTIONS.
        bank_name = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('bank_name','')
        return 'Bank of India' or '' #bank_name
    
    def bank_ifsc_value(self):
        bank_ifsc = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('ifsc_code','')
        return bank_ifsc or ''
    
    def bank_acc_no_value(self):
        acc_num = self.form_record.get('bank_verification',{}).get('bank_details',{}).get('bank_account_number','')
        return acc_num or ''
    
    def is_primary_or_secondary_bank(self):
        """
        method to check if bank a/c number{index} is Primary or not!
        """
        # Values: P/S.
        return 'P'
    
    def depository_name_value(self):
        # Values: NSDL, CDSL
        val=self.form_record.get('dp_information',{}).get('dp_Account_information',{}).get('depository','')
        if val.lower() == 'nsdl':
            return 'NSDL'
        if val.lower() == 'cdsl':
            return 'CDSL'
        return ''

    def depository_id_value(self):
        '''
        This field will have length of 8 Alphanumeric characters. 
            a. IN case Depository Name is selected as NSDL - this field will start with “IN” followed by 6 digits number. 
            b. In case Depository Name is selected as CDSL - No input. 

        '''
        # But as per NSE docs - Values: NSDL, CDSL, but their sample imput follows bse doc description!
        return 'IN302164' # todo: source unknown!
    
    def is_primary_or_secondary_dp(self):
        """
        method to check if dp{index} is Primary or not!
        """
        # Values: P/S.
        return 'P'
    
    def beneficial_acc_num_value(self):
        '''
        # Todo: Beneficial A/c Number - Unknown field, unknown source, is Mandatory!
        '''
        return '12344405'
    
    def segment_indicator_value(self, segment:str|None):
        '''
        Valid values are:
            C- Cash
            F- Future and Option
            S- Securities Lending and Borrowing
            X- Currency Derivatives
            D- Debt Market
            O- Commodity
        '''
        if not segment:
            return ''
        if segment.lower() == 'cash':
            return 'C'
        if segment.lower() == 'fno':
            return 'F'
        if segment.lower() == 'currency':
            return 'X'
        if segment.lower() == 'slb':
            return 'S'
        if segment.lower() == 'Commodity':
            return 'O'
        # if value.lower() == 'debt':
        #     return 'C'
        return ''
    
    def dob_value(self):
        '''
        Gives DoB as in PAN
        '''
        pan_dob = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('dob_pan','')
        return self.format_date(date=pan_dob)
    
    def corr_address_value(self):
        address = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('correspondence_address','')
        return address or ''
    
    def permanent_address_value(self):
        address = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('permanent_address','')
        return address or ''
    
    def corr_address_city_value(self):
        city = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('city','')
        return city or ''
    
    def permanent_address_city_value(self):
        city = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('city','')
        return city or ''
    
    def permanent_address_state_value(self):
        return self._state_value(state_name=self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('state',''))
    
    def corr_address_state_value(self):
        return self._state_value(state_name=self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('state',''))


    def corr_address_pincode_value(self):
        # Todo: pincode only when country selected is India
        pincode = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('pin','')
        return pincode or ''
    
    def permanent_address_pincode_value(self):
        # Todo: pincode only when country selected is India
        pincode = self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('pin','')
        return pincode or ''
    
    def mobile_no_value(self):
        mobile = self.kyc_data.get('mobile_email_verification',{}).get('mobile_verification',{}).get('contact_id','')
        return mobile or ''
    
    def email_value(self):
        email = self.kyc_data.get('mobile_email_verification',{}).get('email_verification',{}).get('contact_id','')
        return email or ''
    
    def _state_value(self, state_name:str):
        """
        returns state number code based state list annexure
        """
        state_code = STATES.get(state_name,'') # Todo: return 99 and based on this specify state name in next field
        return f'{state_code}'
    
    def permanent_address_country_value(self):
        return self._country_value(country=self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('country',''))

    def corr_address_country_value(self):
        return self._country_value(country=self.kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('country','')
)
    def _country_value(self,country:str):
        """
        returns country number code based country list annexure
        """
        country_code = COUNTRIES.get(country,'')
        return f'{country_code}'
    
    def inperson_verification_value(self):
        # Todo: field not well defined!
        #Valid Values are "Y" / "N" or Null
        return 'N'
    
    def client_status_value(self):
        # Values: A = Active, I = Inactive, C = CLOSED
        return 'A' # Todo: Unknown field source, field not well defined!
    
    def gender_value(self):
        # Todo: Mandatory for Individuals (APPLICABLE FOR CATEGORY 1, 11, 18, 25, 26, 27, 31 & 36) and should be NULL in case of other categories.
        # M - Male, F - Female, U - Unisex, NA - Not Applicable
        gender = self.kyc_data.get('identity_address_verification',{}).get('identity_address_info',{}).get('gender_aadhaar','')
        if gender == 'M':
            return 'M'
        if gender == 'F':
            return 'F'
        if gender == 'T':
            return 'U'
        return 'NA'
    
    def guardian_name_value(self):
        # Todo: We're putting Father/Spouse name instead of Guardian Name!
        g_name = self.kyc_data.get('pan_verification',{}).get('pan_details',{}).get('parent_guardian_spouse_name','')
        return g_name or ''
    
    def marital_status_value(self):
        # Todo: Form need to include W, D and NA options too!
        # S - Single, M - Married, W - Widow/widower, D - Divorce, NA - Not Applicable
        marital_status=self.kyc_data.get('identity_address_verification',{}).get('other_info',{}).get('marital_status','')
        if marital_status == 'MARRIED':
            return 'M'
        if marital_status == 'SINGLE':
            return 'S'
        return 'NA'
    
    def nationality_value(self):
        # Todo: Nationality field missing in form
        # 1 - Indian, 2 - Other(please specify)
        # If Indian state is selected, nationality has to be 1.
        return '1'
    
    def same_as_permanent_address_value(self):
        is_same_as_permanent_address = self.kyc_data.get('identity_address_verification',{}).get('same_as_permanent_address','')
        if is_same_as_permanent_address == 'SAME_AS_PERMANENT_ADDRESS':
            return 'Y'
        return 'N'
    
    def gross_income_value(self):
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
        return '0' # for Not Applicabele 
    
    def gross_income_date_value(self):
        date = self.kyc_data.get('declarations',{}).get('income_info',{}).get('date','')
        return self.format_date(date=date)
    
    def networth_value(self):
        # Optional field
        networth = self.kyc_data.get('declarations',{}).get('income_info',{}).get('networth',None)
        return networth or ''
    
    def networth_date_value(self):
        # mandatory only of networth is specified!
        if not self.networth_value():
            return ''
        date = self.kyc_data.get('declarations',{}).get('income_info',{}).get('date','')
        return self.format_date(date=date) or ''
    
    def occupation_value(self):
        # Mandatory for category 1, 11, 18, 25, 26, 27 & 31.
        # Valid values are: 1- Public Sector, 2- Private Sector, 3- Government Service, 4- Business, 5- Professional, 6- Agriculturist, 7- Retired, 8- Housewife, 9- Student, 99- Others (please specify)
        occupation=self.kyc_data.get('declarations',{}).get('income_info',{}).get('occupation','')
        if occupation == 'PUBLIC_SECTOR':
            return '1'
        if occupation == 'PRIVATE_SECTOR':
            return '2'
        if occupation == 'GOVT_SERVICE':
            return '3'
        if occupation == 'BUSINESS':
            return '4'
        if occupation == 'PROFESSIONAL':
            return '5'
        if occupation == 'AGRICULTURIST':
            return '6'
        if occupation == 'RETIRED':
            return '7'
        if occupation == 'HOUSE_WIFE':
            return '8'
        if occupation == 'STUDENT':
            return '9'
        if occupation == 'OTHERS':
            return '99'
        return ''
    
    def occupation_details_value(self):
        # Mandatory if occupation is 'others/99' # Todo: field not available in form
        return ''
    
    def poa_funds_value(self):
         # Todo: Power of Attorney (POA) for funds - unknown and mandatory!
        # Valid values are Y or N
        return 'N'
    
    def pos_securities_value(self):
         # Todo: Power of Attorney (POA) for Securities - unknown and mandatory
        # Valid values are Y or N
        return 'N'
    
    def format_date(self, date: str) -> str:
        """
        returns date in DD-MM-YYYY format
        """
        

        if not date:
            return ""
        try:
            # Parse the input string into a datetime object
            dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            # Format the datetime object into the desired format
            return dt.strftime('%d-%m-%Y')
        except ValueError:
            # logger.debug(f"Error in formatting date {date}")
            return ''
        

STATES={
  "Andaman & Nicobar Islands": 1,
  "Andhra Pradesh": 2,
  "Arunachal Pradesh": 3,
  "Assam": 4,
  "Bihar": 5,
  "Chandigarh": 6,
  "Dadra & Nagar Haveli": 7, # Updated name: Dadra and Nagar Haveli and Daman and Diu
  "Dadra and Nagar Haveli and Daman and Diu": 7, # Added by us
  "Daman & Diu": 8, # Updated name: Dadra and Nagar Haveli and Daman and Diu
  "Delhi": 9,
  "Goa": 10,
  "Gujarat": 11,
  "Haryana": 12,
  "Himachal Pradesh": 13,
  "Jammu & Kashmir": 14,
  "Karnataka": 15,
  "Kerala": 16,
  "Lakhswadeep": 17,
  "Madhya Pradesh": 18,
  "Maharashtra": 19,
  "Manipur": 20,
  "Meghalaya": 21,
  "Mizoram": 22,
  "Nagaland": 23,
  "Orissa": 24, # Odisha after 2011
  "Odisha": 24, # Added by us
  "Pondicherry": 25, # Puducherry after 2006
  "Puducherry": 25,
  "Punjab": 26,
  "Rajasthan": 27,
  "Sikkim": 28,
  "Tamil Nadu": 29,
  "Tripura": 30,
  "Uttar Pradesh": 31,
  "West Bengal": 32,
  "Chhattisgarh": 33,
  "Uttaranchal": 34, # Uttarakhand after 2007
  "Uttarakhand": 34, # Added by us
  "Jharkhand": 35,
  "Telangana": 37,
  "Ladakh": 38,
  "APO": 98,
  "Others (please specify)": 99
}

COUNTRIES = {
    "Afghanistan": 1,
    "Albenia": 2,
    "Algeria": 3,
    "Angola": 4,
    "Argentina": 5,
    "Armenia": 6,
    "Aruba": 7,
    "Australia": 8,
    "Austria": 9,
    "Azarbaijan": 10,
    "Bahamas": 11,
    "Bahrain": 12,
    "Bangladesh": 13,
    "Barbados": 14,
    "Belarus": 15,
    "Belgium": 16,
    "Belize": 17,
    "Benin": 18,
    "Bermuda": 19,
    "Bhutan": 20,
    "Bolivian": 21,
    "Bosnia - herzegovina": 22,
    "Botswana": 23,
    "Brazil": 24,
    "Brunei": 25,
    "Bulgaria": 26,
    "Burkina Faso": 27,
    "Burundi": 28,
    "Cameroon Republic": 29,
    "Canada": 30,
    "Cape Verde": 31,
    "Cayman Islands": 32,
    "Central African Republic": 33,
    "Chad": 34,
    "Chile": 35,
    "China": 36,
    "Colombia": 37,
    "Combodia": 38,
    "Comoros": 39,
    "Congo": 40,
    "Cook Islands": 41,
    "Costa Rica": 42,
    "Cote D'ivoire": 43,
    "Croatia": 44,
    "Cuba": 45,
    "Cyprus": 46,
    "Czech Republic": 47,
    "Denmark": 48,
    "Djibouti": 49,
    "Dominica": 50,
    "Dominican Republic": 51,
    "East Timor": 52,
    "Ecuador": 53,
    "Egypt": 54,
    "El Salvador": 55,
    "Equatorial Guinea": 56,
    "Estonia": 57,
    "Ethiopia": 58,
    "Falkland Islands": 59,
    "Fiji": 60,
    "Finland": 61,
    "France": 62,
    "French Guiana": 63,
    "French Polynesia": 64,
    "Gabon": 65,
    "Gambia": 66,
    "Georgia": 67,
    "Germany": 68,
    "Ghana": 69,
    "Gibraltor": 70,
    "Greece": 71,
    "Greenland": 72,
    "Grenada": 73,
    "Guadeloupe": 74,
    "Guam": 75,
    "Guatemala": 76,
    "Guernsey": 77,
    "Guinea": 78,
    "Guinea - bissau": 79,
    "Guyana": 80,
    "Haiti": 81,
    "Honduras": 82,
    "Hongkong": 83,
    "Iceland": 84,
    "India": 85,
    "Indonesia": 86,
    "Iran": 87,
    "Iraq": 88,
    "Ireland": 89,
    "Israel": 90,
    "Italy": 91,
    "Jamaica": 92,
    "Japan": 93,
    "Jordan": 94,
    "Kazakstan": 95,
    "Kenya": 96,
    "Kuwait": 97,
    "Kyrgyzstan": 98,
    "Laos": 99,
    "Latvia": 100,
    "Lebanon": 101,
    "Lesotho": 102,
    "Liberia": 103,
    "Libya": 104,
    "Lithuania": 105,
    "Luxembourg": 106,
    "Macau": 107,
    "Macedonia": 108,
    "Madagascar": 109,
    "Malawi": 110,
    "Malaysia": 111,
    "Maldives": 112,
    "Mali": 113,
    "Malta": 114,
    "Mauritania": 115,
    "Mauritius": 116,
    "Mexico": 117,
    "Moldova": 118,
    "Monetary Authorities": 119,
    "Mongolia": 120,
    "Montserrat": 121,
    "Morocca": 122,
    "Mozambique": 123,
    "Myanmar": 124,
    "Namibia": 125,
    "Nepal": 126,
    "Netherlands": 127,
    "Netherlands Antilles": 128,
    "New Caledonia": 129,
    "New Zealand": 130,
    "Nicaragua": 131,
    "Niger": 132,
    "Nigeria": 133,
    "No Specific Country": 134,
    "North Korea": 135,
    "Norway": 136,
    "Oman": 137,
    "Pakistan": 138,
    "Panama": 139,
    "Papua New Guinea": 140,
    "Paraguay": 141,
    "Peru": 142,
    "Philippines": 143,
    "Poland": 144,
    "Portugal": 145,
    "Qatar": 146,
    "Romania": 147,
    "Russia": 148,
    "Rwanda": 149,
    "San Tome And Principe": 150,
    "Saudi Arabia": 151,
    "Senegal": 152,
    "Seychelles": 153,
    "Singapore": 154,
    "Slovakia": 155,
    "Slovenia": 156,
    "Solomon Islands": 157,
    "Somalia": 158,
    "South Africa": 159,
    "South Korea": 160,
    "Spain": 161,
    "Sri Lanka": 162,
    "St. Helena": 163,
    "St. Kitts And Nevis": 164,
    "St. Vincent And Grenadines": 165,
    "St.lucia": 166,
    "Sudan": 167,
    "Suriname": 168,
    "Swaziland": 169,
    "Sweden": 170,
    "Switzerland": 171,
    "Syria": 172,
    "Taiwan": 173,
    "Tajikisthan": 174,
    "Tanzania": 175,
    "Thailand": 176,
    "Togo Republic": 177,
    "Tokyo": 178,
    "Tonga": 179,
    "Trinidad And Tobago": 180,
    "Tunisia": 181,
    "Turkey": 182,
    "Turkmenistan": 183,
    "U A E": 184,
    "UAE":184, # Added by us
    "Uganda": 185,
    "United Arab Emirates": 186, # UAE is already present!
    "United Kingdom": 187,
    "Uruguay": 188,
    "Usa": 189,
    "Vanuatu": 190,
    "Venezuela": 191,
    "Vietnam": 192,
    "West Africa": 193,
    "Western Samoa": 194,
    "Yemen": 195,
    "Yugoslavian": 196,
    "Zaire": 197,
    "Zambia": 198,
    "Zimbabwe": 199,
    "Aland Islands": 200,
    "American Samoa": 201,
    "Andorra": 202,
    "Anguilla": 203,
    "Antarctica": 204,
    "Antigua And Barbuda": 205,
    "Bouvet Island": 206,
    "British Indian Ocean Territory": 207,
    "Cambodia": 208,
    "Christmas Island": 209,
    "Cocos (Keeling) Islands": 210,
    "Congo, The Democratic Republic Of The": 211,
    "Eritrea": 212,
    "Faroe Islands": 213,
    "French Southern Territories": 214,
    "Heard Island And Mcdonald Islands": 215,
    "Holy See (Vatican City State)": 216,
    "Hungary": 217,
    "Isle Of Man": 218,
    "Jersey": 219,
    "Kiribati": 220,
    "Korea, Democratic People's Republic Of": 221,
    "Korea, Republic Of": 222,
    "Liechtenstein": 223,
    "Marshall Islands": 224,
    "Martinique": 225,
    "Mayotte": 226,
    "Micronesia, Federated States Of": 227,
    "Monaco": 228,
    "Nauru": 229,
    "Niue": 230,
    "Norfolk Island": 231,
    "Northern Mariana Islands": 232,
    "Palau": 233,
    "Palestinian Territory, Occupied": 234,
    "Pitcairn": 235,
    "Puerto Rico": 236,
    "Reunion": 237,
    "Saint Kitts And Nevis": 238,
    "Saint Lucia": 239,
    "Saint Pierre And Miquelon": 240,
    "Saint Vincent And The Grenadines": 241,
    "Samoa": 242,
    "San Marino": 243,
    "Sao Tome And Principe": 244,
    "Serbia And Montenegro": 245,
    "Sierra Leone": 246,
    "Svalbard And Jan Mayen": 247,
    "Timor - Leste": 248,
    "Tokelau": 249,
    "Turks And Caicos Islands": 250,
    "Tuvalu": 251,
    "Ukraine": 252,
    "United States Minor Outlying Islands": 253,
    "Uzbekistan": 254,
    "Virgin Islands, British": 255,
    "Virgin Islands, U.S.": 256,
    "Wallis And Futuna": 257,
    "Western Sahara": 258
}

    
