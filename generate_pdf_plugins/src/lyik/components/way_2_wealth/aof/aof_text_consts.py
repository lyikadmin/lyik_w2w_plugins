from ...colors import PdfColors
from ....pdf_utilities.utility import get_geo_location
import logging
# from aof_nominee_details_model import NomineeDetails
logger = logging.getLogger(__name__)


class NomineeDetails:
    def __init__(self,nominee_data:dict):
        

        self.data =  nominee_data
        self.nominee_details_heading = 'Nominee Details:'
        self.nominee_name_field_label = 'Nominee Name'
        self.nominee_name_field_value = nominee_data.get('nominee_data',{}).get('name_of_nominee','')
        self.nominee_percentage_of_allocation_field_label = f'''% of allocation:'''
        self.nominee_percentage_of_allocation_field_value = nominee_data.get('nominee_data',{}).get('percentage_of_allocation','')
        self.nominee_relationship_field_label = 'Relationship:'
        self.nominee_relationship_field_value = ''
        self.nominee_odd_lot_text = 'Any odd lot after division shall be transferred to the first nominee mentioned in the form.'
        self.nominee_address_field_label = 'Address:'
        self.nominee_address_field_value = nominee_data.get('nominee_data',{}).get('nominee_address','')
        self.nominee_telephone_field_label = 'Tele/Mobile No:'
        self.nominee_telephone_field_value = ''
        self.nominee_email_field_label = 'Email ID:'
        self.nominee_email_field_value = ''
        self.nominee_identification_details_text = 'Nominee Identification details: [Proof of Identity :PAN/ Aadhaar/ Voter ID/ Passport/ Driving Licence/ Savings Bank account/ DP&BO ID/ Photo & Signature]'
        self.nominee_proof_of_identity_field_label = 'Proof of Identity'
        self.nominee_proof_of_identity_field_value = nominee_data.get('nominee_data',{}).get('nominee_type_of_id','') #''
        self.nominee_identitification_no_field_label = 'Indentification No:'
        self.nominee_identitification_no_field_value = nominee_data.get('nominee_data',{}).get('id_number','')
        self.nominee_dob_field_label = 'Date of birth*:'
        self.nominee_dob_field_value = get_formatted_date(nominee_data.get('nominee_data',{}).get('dob_nominee',''))
        self.is_nominee_minor = nominee_data.get('nominee_data',{}).get('minor_nominee','')
        self.nominee_guardian_details_heading = 'Guardian Details * (Mandatory if Nominee is a Minor)'
        self.nominee_guardian_name_field_label = 'Guradian Name'
        self.nominee_guardian_name_field_value = nominee_data.get('guardian_data',{}).get('guardian_name','') if self.is_nominee_minor else ''
        self.nominee_guardian_address_field_label = 'Address:'
        self.nominee_guardian_address_field_value = nominee_data.get('guardian_data',{}).get('guardian_address','') if self.is_nominee_minor else ''
        self.nominee_guardian_telephone_field_label = 'Tele/Mobile No:'
        self.nominee_guardian_telephone_field_value = ''
        self.nominee_guardian_email_field_label = 'Email ID:'
        self.nominee_guardian_email_field_value = ''
        self.nominee_guardian_relationship_field_label = 'Relationship:'
        self.nominee_guardian_relationship_field_value = nominee_data.get('guardian_data',{}).get('relationship_with_nominee','') if self.is_nominee_minor else ''
        self.nominee_guardian_details_text = '''
        <b>Guardian Identification details -</b> [Proof of Identity :PAN/ Aadhaar/ Voter ID/ Passport/ Driving Licence/ Savings Bank account/ DP ID & BO ID/ Photo & Signature]
        '''
        self.nominee_guardian_proof_of_identity_field_label = 'Proof of Identity'
        self.nominee_guardian_proof_of_identity_field_value = nominee_data.get('guardian_data',{}).get('guardian_type_of_id','') if self.is_nominee_minor else ''
        self.nominee_guardian_identitification_no_field_label = 'Indentification No:'
        self.nominee_guardian_identitification_no_field_value = nominee_data.get('guardian_data',{}).get('guardian_id_number','') if self.is_nominee_minor else ''
        

class KYC:
    def __init__(self,kyc_data:dict, is_digilocker:bool=True):
        self.data = kyc_data
        self.is_digilocker = is_digilocker

        # General Section
        self.page_title = 'Know Your Client (KYC)'
        self.company_name = 'Way2Wealth Brokers Private Limited'
        self.company_address = '''
        Reg. off.: Rukmini Towers, 3rd & 4th Floor # 3/1, Platform Road, Sheshadripuram Bangalore - 560020. www.way2wealth.com, Tele: 080-43676869'''
        self.form_title = 'Application form for Individual'
        self.form_type_options = ['NEW','Modification']
        self.application_type_selected_options = ['New']#[self.data.get('application_details',{}).get('general',{}).get('application_type','')]

        self.application_no_label = 'Application No:'
        self.application_no_value = []#self.data.get('FLD', {}).get('application_details', {}).get('application_no', '')

        self.kyc_mode = 'KYC Mode:'
        self.kyc_mode_options = ['Normal','DigiLocker'] #,[]'EKYC OTP', 'Online KYC', 'Offline','EKYC','EKYC Biometric']
        self.kyc_mode_selected_options = ['DigiLocker' if is_digilocker else 'Normal']
        self.kyc_instructions_text = 'Please fill the Application in <font name="LatoBold">English</font> and in <font name="LatoBold">BLOCK Letters</font> with <b>Black Ink</b>:'      

        # Identity Details Section
        self.identity_passport_size_alt_text = 'Please affix a recent passport Size Photo and sign across it'

        self.identity_passport_size_photo = self.data.get('liveness_check',{}).get('photo_capture',{}).get('liveness_photo',{}).get('doc_id','') if isinstance(self.data.get('liveness_check',{}).get('photo_capture',{}).get('liveness_photo'),dict) else ''
        self.identity_passport_size_help_text ='Cross Signature across Photograph'
        self.identity_details_title = '1. Identity Details: (Please See the Guidelines over Leaf)'
        self.identity_pan_label = 'PAN:'
        self.pan_help_text = '(Please enclose a duly attested copy of your PAN Card)'
        self.identity_pan_value = self.data.get('pan_verification',{}).get('pan_details',{}).get('pan_number','')
        self.identity_name_label = 'Name (same as ID proof):'
        self.identity_name_value = self.data.get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')
        self.identity_maiden_name_label = 'Maiden Name (if any):'
        self.identity_maiden_name_value = ''
        self.identity_father_spouse_name_label = 'Father/Spouse Name:'
        self.identity_father_spouse_name_value = self.data.get('pan_verification',{}).get('pan_details',{}).get('parent_guardian_spouse_name','')
        self.identity_mother_name_label = 'Mother Name:'
        self.identity_mother_name_value = self.data.get('identity_address_verification',{}).get('other_info',{}).get('mother_name','')
        self.identity_gender_label = 'Gender:'
        self.identity_gender_options = ['Male', 'Female', 'Transgender']
        self.identity_gender_selected_options = [get_enum_value_from_key(self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('gender_aadhaar',''))]
        self.identity_marital_status_label = 'Marital Status:'
        self.identity_marital_status_options = ['Married', 'Single']
        self.identity_marital_status_selected_options = [get_enum_value_from_key(self.data.get('identity_address_verification',{}).get('other_info',{}).get('marital_status',''))]
        self.identity_nationality_label = 'Nationality:'
        self.identity_nationality_options = ['Indian', 'Others']
        self.identity_nationality_selected_options = []
        self.identity_iso_country_code_label = 'ISO 3166 Country Code'
        self.identity_iso_country_code_value = ''
        self.identity_residential_status_label = 'Residential Status:'
        self.identity_residential_status_options = [
            'RI', 'NRI',
            'PIO', 'Foreign National'
        ]
        self.identity_residential_status_help_text = '(Passport is mandatory for NRI/PIO/FN)'
        self.identity_residential_status_selected_options = []
        self.identity_aadhar_label = 'Aadhaar No. (UID):'
        self.identity_aadhar_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('aadhaar_number','') # This is not necessarily the aadhaar number, it could be any ovd id number too!
        self.identity_date_of_birth_label = 'Date of Birth:'
        self.identity_date_of_birth_value = get_formatted_date(self.data.get('pan_verification',{}).get('pan_details',{}).get('dob_pan',''))
        self.identity_poi_label = 'POI Submitted for PAN exempted Case:'
        self.identity_poi_value = ''
        # self.page3_identity_poi_options = [
        #     'Aadhaar', 'Passport', 'Voter ID', 'Driving License', 'NREGA Card', 'NPR', 'Other'
        # ]
        # self.page3_identity_poi_selected_options = []
        self.aadhaar_xml = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('aadhaar_xml','') if is_digilocker else ''
        self.ovd_type = self.data.get('identity_address_verification',{}).get('ovd_ocr_card',{}).get('ovd_type','') if not self.is_digilocker else 'AADHAAR'
        # Address Details Section
        # 1. Correspondence Address section
        self.address_details_title = '2. Address Details:'
        self.address_correspondence_title = 'A. Correspondence/Local Address'
        self.address_correspondence_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('correspondence_address','')
        self.address_city_label = 'City/Town/Village:'
        self.address_city_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('city','')
        self.address_district_label = 'District:'
        self.address_district_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('district','')
        self.address_pincode_label = 'Pincode:'
        self.address_pincode_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('pin','')
        self.address_state_label = 'State:'
        self.address_state_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('state','')
        self.address_country_label = 'Country:'
        self.address_country_value = self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('country','')
        self.address_type_label = 'Address Type:'
        self.address_type_options = [
            'Residential/Business', 'Residential', 'Business', 'Registered Office', 'Unspecified'
        ]
        self.address_type_selected_options = [get_enum_value_from_key(self.data.get('identity_address_verification',{}).get('correspondence_address',{}).get('type_of_address',''))]

        # 2. Permanent Address section
        self.address_permanent_title = '''
        B. Permanent Resident Address of Applicant, if different from above A / OR Overseas Address
        (Mandatory for Non-Resident Applicant)
        '''
        self.address_permanent_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('permanent_address','')
        self.address_permanent_city_label = 'City/Town/Village:'
        self.address_permanent_city_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('city','')
        self.address_permanent_district_label = 'District:'
        self.address_permanent_district_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('district','')
        self.address_permanent_pincode_label = 'Pincode:'
        self.address_permanent_pincode_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('pin','')
        self.address_permanent_state_label = 'State:'
        self.address_permanent_state_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('state','')
        self.address_permanent_country_label = 'Country:'
        self.address_permanent_country_value = self.data.get('identity_address_verification',{}).get('identity_address_info',{}).get('country','')
        self.address_permanent_type_label = 'Address Type:'
        self.address_permanent_type_options = [
            'Residential/Business', 'Residential', 'Business', 'Registered Office', 'Unspecified'
        ]
        self.address_permanent_type_selected_options = []
        
        # Proof of Address section
        self.proof_of_address_label = 'Proof of Address*:'
        self.proof_of_address_label_help_text = '(attested copy of POA for correspondance and permanent address each to be submitted)'
        # self.proof_of_address_options = [
        #     'Aadhaar Card', 'Passport Number', 'Voter ID Card', 'Driving License',
        #     'NREGA Job Card', 'NPR Letter', 'Others'
        # ]
        # self.proof_of_address_options_types = ['Corr. Add','Perm. Add']
        # self.proof_of_address_expiry_date = ''
        # self.proof_of_address_zid_number = ''
        self.is_address_correspondence_same_as_permanent = self.data.get('identity_address_verification',{}).get('same_as_permanent_address','')
        self.proof_of_address_table_data = [
            ['Corr. Add','Perm. Add','','','',''],
            ['','','A Aadhaar Card','','',''],
            ['','','B Passport Number','__________','Expiry Date','__________'],
            ['','','C Voter ID Card','__________','',''],
            ['','','D Driving License','__________','Expiry Date','__________'],
            ['','','E NREGA Job Card','__________','',''],
            ['','','F NPR Letter','__________','',''],
            ['','','Z Others','__________','Z. Id Number','__________']
        ]
        self.applicant_esign_title = 'Applicant e-Sign'
        self.applicant_esign_value = ''
        self.applicant_wet_sign_title = 'Applicant Wet Sign'

        # Todo: Handle empty value which is "", not {}
        self.applicant_wet_sign_value = self.data.get('signature_validation',{}).get('upload_images',{}).get('wet_signature_image',{}).get('doc_id','') if isinstance(self.data.get('signature_validation',{}).get('upload_images',{}).get('wet_signature_image'),dict) else ''

        # Page 4
        # Contact Details Section
        self.contact_details_title = '3. Contact Details:'
        self.contact_email_label = 'Email ID:'
        self.contact_email_value = self.data.get('mobile_email_verification',{}).get('email_verification',{}).get('contact_id','')
        self.contact_mobile_label = 'Mobile:'
        self.contact_mobile_value = self.data.get('mobile_email_verification',{}).get('mobile_verification',{}).get('contact_id','')
        self.contact_mobile_dependent_relationship_options = ['Self', 'Spouse', 'Dependent Parent', 'Dependent Child']
        self.contact_mobile_dependent_relationship_selected_options = [get_enum_value_from_key(self.data.get('mobile_email_verification',{}).get('mobile_verification',{}).get('dependency_relationship_mobile',''))]
        self.contact_email_dependent_relationship_options = ['Self', 'Spouse', 'Dependent Parent', 'Dependent Child']
        self.contact_email_dependent_relationship_selected_options = [get_enum_value_from_key(self.data.get('mobile_email_verification',{}).get('email_verification',{}).get('dependency_relationship_email',''))]
        self.contact_tel_off_label = 'Tel. (off) with STD Code:'
        self.contact_tel_off_value = ''
        self.contact_tel_res_label = 'Tel. (Resi) with STD Code:'
        self.contact_tel_res_value = ''


        # FATCA - CRS Declaration - Individuals (Trading & DP)
        self.fatca_heading = '4. FATCA - CRS Declaration - Individuals (Trading & DP)'
        self.tax_resident_label = 'Are you a tax resident of any country other than India?'
        self.tax_resident_options = ['Yes','No']
        self.tax_resident_selected_options = [get_enum_value_from_key(self.data.get('declarations',{}).get('fatca_crs_declaration',{}).get('is_client_tax_resident',''))]
        self.place_of_birth_label = 'Place of Birth :'
        self.place_of_birth_value = self.data.get('declarations',{}).get('fatca_crs_declaration',{}).get('place_of_birth_1','')
        self.country_of_origin_label = 'Country of Origin :'
        self.country_of_origin_value = self.data.get('declarations',{}).get('fatca_crs_declaration',{}).get('country_of_origin','')
        self.iso_3166_country_code_label = 'ISO 3166 Country Code'
        self.iso_3166_country_code_value = self.data.get('declarations',{}).get('fatca_crs_declaration',{}).get('country_code','')

        self.fatca_table_data = [
            ['<font color = "#000000">Country Of Tax Residency #</font>','<font color = "#000000">TAX Identification No. (TIN) %</font>','<font color = "#000000">Identification Type (TIN or Other, Please Specify)</font>','<font color = "#000000">If TIN not available *</font>'],
            [self.data.get('declarations',{}).get('fatca_crs_declaration_1',{}).get('country_of_residency_1',''),self.data.get('declarations',{}).get('fatca_crs_declaration_1',{}).get('tin_no_1',''),self.data.get('declarations',{}).get('fatca_crs_declaration_1',{}).get('id_type_1',''),self.data.get('declarations',{}).get('fatca_crs_declaration_1',{}).get('reason_if_no_tin_1','')],
            [self.data.get('declarations',{}).get('fatca_crs_declaration_2',{}).get('country_of_residency_2',''),self.data.get('declarations',{}).get('fatca_crs_declaration_2',{}).get('tin_no_2',''),self.data.get('declarations',{}).get('fatca_crs_declaration_2',{}).get('id_type_2',''),self.data.get('declarations',{}).get('fatca_crs_declaration_2',{}).get('reason_if_no_tin_2','')],
            [self.data.get('declarations',{}).get('fatca_crs_declaration_3',{}).get('country_of_residency_3',''),self.data.get('declarations',{}).get('fatca_crs_declaration_3',{}).get('tin_no_3',''),self.data.get('declarations',{}).get('fatca_crs_declaration_3',{}).get('id_type_3',''),self.data.get('declarations',{}).get('fatca_crs_declaration_3',{}).get('reason_if_no_tin_3','')],
        ]

        self.fatca_note_1 = '# To also include USA, where the individual is a citizen/Green card holder of the USA'
        self.fatca_note_2 = '$ In case Tax identification number is not available, kindly provide its functional equivalent'
        self.fatca_note_3 = '*If Tin not available, Reason:'
        self.fatca_note_a = 'A - The country where the account holder is liable to pay tax and does not issue tax identification number to its residents'
        self.fatca_note_b = 'B - No Tin Required (Select this only if the authorities of respective country of tax residence not require the TIN be collected)'
        self.fatca_note_c = 'C - Others; Please state the thereof'

        # Certification Section
        self.certification_heading = 'Certification'
        self.certification_content = '''I/We have understood the information requirements of this form (read along with the FATCA & CRS instructions) and
            here by confirm that the information provide by me/us on this form is true, correct and complete. I/We also confirm
            that I/We have read and understood the FACTA & CRS terms and conditions and hereby accept the same.'''

        # Gross Annual Income
        self.gross_annual_income_label = '5. Gross Annual Income:'
        self.gross_income_range_options = [
            '0-1Lac',
            '1-5Lac',
            '5-10Lac',
            '10-25Lac',
            '25Lac-1Cr',
            '1Cr-5Cr',
            '>5Cr'
        ]
        self.gross_income_selected_options = [get_enum_value_from_key(self.data.get('declarations',{}).get('income_info',{}).get('gross_annual_income',''))]  # Selected range index(es)

        self.gross_income_date_label = 'Date :'
        self.gross_income_date_value = get_formatted_date(self.data.get('declarations',{}).get('income_info',{}).get('date',''))

        self.gross_networth_label = "Networth:"
        self.gross_networth_value = self.data.get('declarations',{}).get('income_info',{}).get('networth','')
        self.gross_networth_date_label = 'Date :'
        self.gross_networth_date_value = get_formatted_date(self.data.get('declarations',{}).get('income_info',{}).get('date',''))

        # Occupation Details
        self.occupation_label = '6. Occupation:'
        self.occupation_options = [
            'Private Sector',
            'Public Sector',
            'Business',
            'Govt. Service',
            'Professional',
            'Student',
            'House wife',
            'Agriculturist',
            'Retired Person',
            'Others'
        ]
        self.occupation_selected_options = [get_enum_value_from_key(self.data.get('declarations',{}).get('income_info',{}).get('occupation',''))]  # Selected occupation value(s)
        self.occupation_other_label = 'Others (Specify):'
        self.occupation_other_value = ''

        # Politically Exposed Person (PEP)
        self.pep_label = '7. Please Tick if Applicable:'
        self.pep_options = [
            'Politically Exposed Person',
            'Related to Politically Exposed Person',
            'Not Applicable'
        ]
        self.pep_selected_options = [get_enum_value_from_key(self.data.get('declarations',{}).get('politically_exposed_person_card',{}).get('politically_exposed_person',''))] # Selected PEP status index(es)

        # Applicant Declaration
        self.applicant_declaration_heading = '8. Applicant Declaration'
        self.applicant_declaration_content = (
            'I/We hereby declare that the details furnished above are true and correct to the best of my/our knowledge and belief '
            'and I/We under-take to inform you of any changes therein, immediately. In case any of the above information is found '
            'to be false or untrue or misleading or misrepresenting, I am/We are aware that I/We may be held liable for it. I/We '
            'hereby consent to receiving information from KRA & CKYC through SMS/Email on the above registered number/Email address. '
            'I/We are also aware that for Aadhaar OVD based KYC, my KYC request shall be validated against Aadhaar details. I/We hereby '
            'consent to sharing my/our masked Aadhaar card with readable QR code or my Aadhaar XML/Digilocker XML file, along with '
            'passcode and as applicable, with KRA and other Intermediaries with whom I have a business relationship for KYC purposes only.'
        )
        self.declaration_date_label = 'Date :'
        self.declaration_date_value = ''
        self.declaration_place_label = 'Place :'
        self.declaration_place_value = get_geo_location(
            lat=(kyc_data.get('liveness_check', {}).get('liveness_geo_loc') if isinstance(kyc_data.get('liveness_check', {}).get('liveness_geo_loc'), dict) else {}).get('lat', ''),
            long=(kyc_data.get('liveness_check', {}).get('liveness_geo_loc') if isinstance(kyc_data.get('liveness_check', {}).get('liveness_geo_loc'), dict) else {}).get('long', '')
        )

        # Signatures
        self.applicant_esign_label = 'Applicant e-Sign'
        self.applicant_wet_sign_label = 'Applicant Wet Sign'

        # KYC Verification/In Person Verification (IPV)
        self.kyc_verification_heading = 'KYC Verification/In Person Verification (IPV) Carried out by: (For Office Use only)'
        self.ipv_carried_out_on_date_label = 'Inperson Verification Carried Out On Date'
        self.ipv_carried_out_on_date_value = ''
        self.ipv_place_label = 'Place'
        self.ipv_place_value = ''
        self.official_name_label = 'Name of Official:'
        self.official_name_value = ''
        self.official_designation_label = 'Designation:'
        self.official_designation_value = ''
        self.employee_ap_code_label = 'Employee / AP Code:'
        self.employee_ap_code_value = ''
        self.documents_received_options = [
            'Self certified document copies received (OVD)',
            'True Copies of documents received (Attested)'
        ]
        self.documents_received_selected_options = []  # Selected document status index(es)

        self.signature_branch_ap_seal_label = 'Signature & Branch /AP Seal'

class AOFConstantTexts:
    def __init__(self, json_data:dict={}):
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_dir, 'second_json.json')
        # with open(file_path, 'r') as file:
        #     dynamic_data = json.load(file) 
        self.data =  json_data
    
        # Page 1
        self.page1_box_left_text = '''
        <font name="LatoBold">SEBI Reg No:<br/>
        Stock Broker: INZ000178638<br/>
        Depository Participant: IN-DP-472-2020<br/><br/>
        Investor Grievance Details: Exchange</font><br/>
        NSE: ig@nse.co.in Tele: 022-26598100<br/>
        BSE: is@bse.co.in Tele: 022-22728097<br/>
        MCX-SX: investorcomplaints@mcx-sx.com<br/><br/>
        <font name="LatoBold">Depository:</font><br/>
        NSDL: relations@nsdl.co.in (022) 2499 4200<br/>
        CDSL: complaints@cdslIndia.com 1800-200-5533'''

        self.page1_box_right_text = f'''<font name="LatoBold">Details of Compliance Officer</font><br/>
        Name: Sandhya<br/>
        Email: Sandhya@way2wealth.com<br/>
        Telephone: 080- 43676874<br/><br/>
        <font name="LatoBold">Details of CEO</font><br/>
        Name: G S Shridhar<br/>
        Telephone: 080- 43676869,<br/>
        Email:ceo@way2wealth.com<br/><br/>
        SEBI Scores: <font color={PdfColors().filled_data_color}><a href='www.scores.gov.in'>www.scores.gov.in</a></font><br/>
        <font name="LatoBold">Investor Grievance Details: Member</font><br/>
        grievance@way2wealth.com, Tele: 080-43676862'''

        self.page1_bottom_text = '''For any grievance/dispute please contact stock broker at the above address, email id and Phone No. In case not satisfied with the response, please contact the concerned exchange(s) at respective investor grievance, Phone No. given above.'''

        self.page1_address_text = 'Reg. office: Rukmini Towers, 3rd & 4th Floor, # 3/1, Platform Road,<br/>Sheshadripuram, Bangalore -560 020<br/> Tel.: (080) 4367 6869, Fax: (080) 4367 6999'

        self.page1_form_title = 'Client Registration Form<br/>Trading & DP Account'

        self.page1_company_title = f'Way<font color={"#C00000"}>2</font>Wealth Brokers Private Limited'

        self.page1_company_website = f"Website: www.way2wealth.com"

        self.page1_table1_data = [
            ["Application No.", ""],
            ["Branch", ""],
            ["Branch Code", ""],
            ["Region", ""]
        ]

        self.page1_table2_data = [
            ['To be Filled at (HO)'],
            ['Trading Code', ''],
            ['DP Code', '', '', '', '', '', '', '', '']
        ]

        # Page 2
        # Nested table (4 rows x 3 columns)
        self.page2_nested_table_data = [["Particulars", "Employee Code", "Employee Name"],
                            ["Introducer/ Lead Generator", "", ""],
                            ["Relationship Manager / Lead Closer", "", ""],
                            ["Dealer", "", ""]]
        
        self.page2_branch_manager_heading = 'Branch Manager / AP Authorisation'

        self.page2_table1_date_value = ''
        self.page2_table1_place_value = ''
        self.page2_table1_name_value = ''
        self.page2_table1_designation_value = ''
        self.page2_table1_contact_no_value = ''
        self.page2_table1_employee_code_value = ''

        self.page2_table1_header = 'For Branch Office / Authorised Person'

        self.page2_table2_heading = 'Document Verification/Inperson Verification & Client Interviewed by :'
        self.page2_table2_ipv_date = ''
        self.page2_table2_mobile_no = ''
        self.page2_table2_name = ''
        self.page2_table2_designation = ''
        self.page2_table2_signature_heading = 'Signature of Person Doing IPV:'
        self.page2_table2_image_header = 'Branch/Sub-Broker/AP Seal & Signature'

        self.page2_tabel2_undertaking_text = '''I/We undertake that we have made the client aware of \'Policy and Procedures\', tariff sheet and all the non-mandatory documents. I/We
        have also made the client aware of \'Rights and Obligations\' document(s), RDD and Guidance Note. I/We have given/sent him a copy of all
        the KYC documents. I/We undertake that any change in the \'Policy and Procedures\', tariff sheet and all the non-mandatory documents
        would be duly intimated to the clients. I/We also undertake that any change in the \'Rights and Obligations\' and RDD would be made
        available on my/our website, if any, for the information of the clients.
        '''
        self.page2_table2_sign_pretext =  'Authorised Signatory: '
        self.page2_table2_header = 'For office use only (Branch Office)'

        # Page 3,4 - KYCs
        _is_digilocker = str(self.data.get('application_details',{}).get('kyc_digilocker','')).lower()!='no'

        self.page_kyc_details:list[KYC] = [KYC(kyc_data=kyc_data.get('kyc_holder',{}),is_digilocker=_is_digilocker) for kyc_data in self.data.get('kyc_holders', [])]

        # Page 5 is fully textual, scanned page can be added directly to pdf

        # Page 6
        # Additional Details (Part - B) Section
        self.page6_additional_details_part_b_heading = 'ADDITIONAL DETAILS (PART - B)'

        self.page6_additional_details_table_heading = 'Other Details'

        self.page6_rbi_approval_ref_no_label = 'RBI Approval Ref No. (For NRI/FN/POI/Others):'
        self.page6_rbi_approval_ref_no_value = ''

        self.page6_date_of_approval_label = 'Date of Approval:'
        self.page6_date_of_approval_value = get_formatted_date(self.data.get('trading_information',{}).get('employer_details',{}).get('approval_date',''))

        self.page6_name_of_employer_label = 'Name of the Employer:'
        self.page6_name_of_employer_value = self.data.get('trading_information',{}).get('employer_details',{}).get('employer_name','')

        self.page6_address_and_contact_label = 'Address & Contact No:'
        self.page6_address_and_contact_value = self.data.get('trading_information',{}).get('employer_details',{}).get('employer_address','') + " | " + self.data.get('trading_information',{}).get('employer_details',{}).get('mobile_number','')

        # Bank & Depository Account Details (Default) Section
        self.page6_bank_and_depository_table_heading = 'Bank & Depository Account Details (Default)'

        self.page6_bank_name_label = 'Bank Name:'
        self.page6_bank_name_value = ''

        self.page6_bank_address_label = 'Bank Address:'
        self.page6_bank_address_value = ''

        self.page6_bank_account_num_label = 'Bank Account No:'
        self.page6_bank_account_num_value = self.data.get('bank_verification',{}).get('bank_details',{}).get('bank_account_number','')

        self.page6_ifsc_code_label = 'IFSC Code:'
        self.page6_ifsc_code_value = self.data.get('bank_verification',{}).get('bank_details',{}).get('ifsc_code','')

        self.page6_micr_num_label = 'MICR No:'
        self.page6_micr_num_value = ''

        self.page6_bank_ac_type_label = 'Type:'
        self.page6_bank_ac_type_options = [
            'Savings',
            'Current',
            'Others'
        ]
        self.page6_bank_ac_type_selected_options = []

        self.page6_upi_id_label = 'UPI ID:'
        self.page6_upi_id_value = ''

        self.page6_depository_participant_name_label = 'DEPOSITORY PARTICIPANT NAME'
        self.page6_depository_participant_name_value = self.data.get('dp_information',{}).get('dp_Account_information',{}).get('name_of_dp','')

        self.page6_dp_id_num_label = 'DP ID No'
        self.page6_dp_id_num_value = self.data.get('dp_information',{}).get('dp_Account_information',{}).get('dp_id_no','')

        self.page6_client_id_label = 'CLIENT ID No'
        self.page6_client_id_value = self.data.get('dp_information',{}).get('dp_Account_information',{}).get('client_id_no','')

        self.page6_depositry_label = 'DEPOSITORY'
        self.page6_depositry_options = [
            'NSDL',
            'CDSL'
        ]
        self.page6_depositry_selected_options = [get_enum_value_from_key(self.data.get('dp_information',{}).get('dp_Account_information',{}).get('depository',''))]

        # Exchange and Segment Preferences Section
        self.page6_exchange_and_segment_preferences_heading = 'Exchange and Segment Preferences'

        self.page6_exchange_and_segment_preferences_instruction = (
            'Please tick and sign on the relevant boxes where you wish to trade and '
            'segment not selected should be struck off by client.'
        )

        # Exchange, Segments, Client Signature Table
        self.page6_exchange_segment_table_data = [
            ["Exchange", "Segments", "Client Signature"],
            ["National Stock Exchange<br/>Bombay Stock Exchange", "Equity Cash", ""],  # Add as many empty rows as necessary based on the table layout
            ["", "Equity Derivatives", ""],
            ["", "Currency Derivatives", ""],
            ["National Stock Exchange", "SLB", ""],
            ["MCX Commodity Exchange","Commodities Derivatives",""]
        ]

        self.page6_exchange_prefs_note = 'Note: In future if the client want to trade in new segment / Exchange, separate authorisation letter should be given by client'
        self.page6_exchange_prefs_past_action_label = "Past Actions: Details of any action / proceedings initiated / pending / taken by SEBI / Stock exchange / any other authority against the applicant / constituent or its Partners / promoters / whole time directors / authorized persons in charge of dealing in securities during the last 3 years."
        self.page6_exchange_prefs_past_action_value = ''
        self.page6_exchange_prefs_any_other_info_label = 'Any other Information:'
        self.page6_exchange_prefs_any_other_info_value = ''

        # Details of Dealing through Sub-brokers and other Stock Brokers
        self.page6_details_of_dealing_heading = 'Details of Dealing through Sub-brokers and other Stock Brokers'
        self.page6_broker_name_and_address_label = 'Name & Address of Broker / Sub-Broker:'
        self.page6_broker_name_address_value = self.data.get('trading_information',{}).get('details_of_dealings',{}).get('broker_name','') + ' | ' + self.data.get('trading_information',{}).get('details_of_dealings',{}).get('broker_address','')
        self.page6_broker_telephone_label = 'Telephone & Website:'
        self.page6_broker_telephone_value = self.data.get('trading_information',{}).get('details_of_dealings',{}).get('telephone','') + ' | ' + self.data.get('trading_information',{}).get('details_of_dealings',{}).get('website','')
        self.page6_broker_client_code_label = 'Client Codes:'
        self.page6_broker_client_code_value = self.data.get('trading_information',{}).get('details_of_dealings',{}).get('client_codes','')
        self.page6_broker_details_of_dispute_label = 'Details of disputes / dues pending from / to such stock broker / sub-broker'
        self.page6_broker_details_of_dispute_value = self.data.get('trading_information',{}).get('details_of_dealings',{}).get('detail_of_disputes','')

        # Additional Details:
        self.page6_additional_details_section_heading = 'Additional Details:'
        self.page6_additional_details_physcial_contract_field_label = 'Whether you wish to receive'
        self.page6_additional_details_physcial_contract_field_options = ['Physical Contract Note','Electronic contact Note (ECN)']
        self.page6_additional_details_physcial_contract_field_selected_options = [get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('contract_format_1','')),get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('contract_format_2',''))]
        self.page6_additional_details_internet_option_label = 'Whether you wish to avail the facility of Internet / wireless trading / mobile trading / technology (please specify):'
        self.page6_additional_details_internet_option_options = ['Yes','No']
        self.page6_additional_details_internet_option_selected_options = [get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('client_facility_choice',''))]
        self.page6_additional_details_experience_field_label = 'Number of years of Investment / Trading Experience'
        self.page6_additional_details_experience_field_options = ['Nil','1-3 Years','3-6 Years','More than 6 years']
        self.page6_additional_details_experience_field_selected_options = [get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('holder_trading_experience',''))]
        self.page6_additional_details_opt_for_ac_opening_kit_label = 'I would like to receive the account opening kit / standard set of documents in'
        self.page6_additional_details_opt_for_ac_opening_kit_options = ['Physical','Electronic Form']
        self.page6_additional_details_opt_for_ac_opening_kit_selected_options = [get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('kit_format_1','')),get_enum_value_from_key(self.data.get('trading_information',{}).get('trading_account_information',{}).get('kit_format_2',''))]


        # Page 7: Introducer Details
        self.page7_introducer_details_heading = 'Introducer Details'
        self.page7_introducer_name_field_label = 'Name:'
        self.page7_introducer_name_field_value = self.data.get('trading_information',{}).get('introducer_details',{}).get('introducer_name','')
        self.page7_introducer_address_field_label = 'Address:'
        self.page7_introducer_address_field_value = self.data.get('trading_information',{}).get('introducer_details',{}).get('introducer_broker_address','')
        self.page7_introducer_status_of_introducer_field_label = 'Status of Introducer:'
        self.page7_introducer_status_of_introducer_field_options = ['Client','Sub-Broker/AP','Remisier']
        self.page7_introducer_status_of_introducer_field_selected_options = [get_enum_value_from_key(self.data.get('trading_information',{}).get('introducer_details',{}).get('introducer_status',''))]
        self.page7_introducer_singnature_label = 'Signature of Introducer'

        self.page7_declaration_heading = 'Declaration'
        self.page7_declaration_text = '''
        I/We here by declare that the details furnished above are true and correct to the best of my knowledge & belief and I/We undertake to inform you of any changes
        there in, immediately. In case any of the above information is found to be false or untrue or misleading or misrepresenting, I am / we are aware that I / we may be
        held liable for it.<br/>
        I / We confirm having read / been explained and understood the contents of the document on policy and procedures of the stock broker and the tariff sheet.<br/>
        I / We further confirm having read and understood the contents of the 'Rights and Obligations' document(s) and 'Risk Disclosure' Document, additional voluntary
        risks disclosure clauses, Do's and Dont's and Policies &Procedures. I / We do hereby agree to be bound by such provisions as outlined in these documents. I /
        We have also been informed that the standard set of documents has been displayed for Information on stock broker's designated website, www.way2wealth.com.
        I/We do hereby declare that I have not been involved in any unlawful activities and I have not been declared a defaulter or my name is not appearing in defaulter
        database as per SEBI/Various Exchange / Regulatory Bodies, etc. I further declare that the above mentioned declaration / True and correct.<br/>
        I/we have been informed that the KYC data provided by us to you would further be validated by the KRA agencies, which would require me/us to complete certain
        validations thru SMS/email links sent by them and I/we would promptly complete the same as and when received. Further, I/we have been informed that in case
        of KYC data provided herewith is found not to be correct/or validation fails then my transactions may be blocked until the validation process is completed and the
        KRA status changed to KYC Registered /Validated.
        '''
        self.page7_declaration_client_details_table_data = [
            ['Client Name:',self.page_kyc_details[0].identity_name_value if 0 < len(self.page_kyc_details) else '','Client Signature'],
            ['Place:',self.page_kyc_details[0].declaration_place_value if 0 < len(self.page_kyc_details) else '',''],
            ['Date:','','']
        ]
        self.page7_brokerage_tariff_heading = 'Brokerage Tariff for Trading'
        self.page7_brokerage_tariff_segment_standard_rates_table_data = [
            ['Segment','Standard Rate',''],
            ['','Minimum Paisa','In %'],
            ['Cash & FNO Delivery','5 Paisa','0.50%'],
            ['Cash Jobbing','5 Paisa','0.10%'],
            ['Futures','5 Paisa','0.10%'],
            ['Options','Rs.100/-',''],
            ['Currency Futures','5 Paisa','0.10%'],
            ['Currency Options','Rs.25/-',''],
            ['Commodity Futures','5 Paisa','0.03%'],
            ['Commodity Options','Rs.100/-',''],
            ['SLB Fee','20%',''],
        ]

        self.page7_brokerage_tariff_special_rates_table_data = [
            ['<font color = "#000000">Special Rates</font>',''],
            ['<font color = "#000000">Minimum Paisa</font>','<font color = "#000000">In %</font>'],
            [self.data.get('application_details',{}).get('cash_fut_como_card',{}).get('cash_minimum_paisa',''),self.data.get('application_details',{}).get('cash_fut_como_card',{}).get('cash_in_percentage','')],
            [self.data.get('application_details',{}).get('cash_jobbing_card',{}).get('cash_jobbing_minimum_paisa',''),self.data.get('application_details',{}).get('cash_jobbing_card',{}).get('cash_jobbing_in_percentage','')],
            [self.data.get('application_details',{}).get('futures_card',{}).get('futures_minimum_paisa',''),self.data.get('application_details',{}).get('futures_card',{}).get('futures_in_percentage','')],
            [self.data.get('application_details',{}).get('options_card',{}).get('options_standard_rate',''),''],
            [self.data.get('application_details',{}).get('currency_futures_card',{}).get('currency_futures_minimum_paisa',''),self.data.get('application_details',{}).get('currency_futures_card',{}).get('currency_futures_in_percentage','')],
            [self.data.get('application_details',{}).get('currency_options_card',{}).get('currency_options_rate',''),''],
            [self.data.get('application_details',{}).get('commodity_futures_card',{}).get('commodity_futures_minimum_paisa',''),self.data.get('application_details',{}).get('commodity_futures_card',{}).get('commodity_futures_in_percentage','')],
            [self.data.get('application_details',{}).get('commodity_options_card',{}).get('commodity_options_rate',''),''],
            [self.data.get('application_details',{}).get('slb_card',{}).get('slb_rate',''),'']
        ]
        self.page7_brokerage_tariff_flat_per_table_data = [
            ['<font color = "#000000">Flat Per order</font>'],
            [self.data.get('application_details',{}).get('flat_per_order_card',{}).get('flat_per_order_rate','')]
        ]

        self.page7_brokerage_tariff_online_fee_option_text = 'Online EXE (Fee. Rs.750/-)'
        self.page7_brokerage_tariff_online_fee_option_selection = self.data.get('application_details',{}).get('online_exe_card',{}).get('online_exe','')
        self.page7_bottom_declaration_text = '''
        1. The above rates are exclusive of GST and education cess, SEBI/Exchange/Clearing Members Charges, Stamp Duty, Statutory Charges payable to
        exchange /SEBI/Govt. Authorities etc., which will be charged extra at the rate prevailing from time to time.<br/>
        2. In Addition to this DP Annual Maintenance Charges, DP Transaction charges/Pledge/Un-pledge/demat/remat charges, DP Inter settlement charges, Account
        Opening charges, Bank charges towards cheques received unpaid, charges towards customized/special service, which will be charged extra at the rate
        prevailing from time to time.<br/>
        3. The General rates as mentioned here shall be applied unless the special rates as may be agreed by the sub-broker/Authorised Person/ Introducer and client
        and the same are mentioned here.<br/>
        4. I have read and understand the additional risk disclosure clauses given by brokers and agreed to abed by the same.<br/>
        Note : Brokerage will not exceed the rates specified by SEBI and the Exchanges of 2.5%. All statutory and Regulatory charges are will be levied at actuals
        Brokerage is also charged on expired, excercised and assigned option contracts.
        '''
        self.page7_gst_details_text = 'GST Details:'
        self.page7_gst_no_field_label = 'GST No:'
        self.page7_gst_no_field_value = self.data.get('application_details',{}).get('gst_details_card',{}).get('gst_number','')
        self.page7_gst_state_field_label = 'State:'
        self.page7_gst_state_field_value = self.data.get('application_details',{}).get('gst_details_card',{}).get('gst_number_1','')
        self.page7_client_signature_field_label = 'Client Signature'
        self.page7_client_signature_field_value = ''


        # Page 8
        self.page8_table_heading = 'Additional Details for DP account'
        self.page8_cdsl_checkbox_option = 'CDSL DP ID: 12062900'
        self.page8_nsdl_checkbox_option = 'NSDL DP ID: IN 303077'
        self.page8_account_type_field_display_name = 'A/C Type:'
        self.page8_account_type_options = ['Resident Indian','NRI - Repatriable','NRI Non-Repatriable','FN','Promoter']
        self.page8_account_type_selected_options = []
        self.page8_guardian_details_field_display_name = 'Guardian Details (Where Sole holder is a Minor)'
        self.page8_guardian_details_field_options=['Court Appointed']
        self.page8_guardian_details_field_selected_options = []
        self.page8_guardian_pan_field_display_name = 'PAN No of Guardian:'
        self.page8_guardian_pan_field_value = ''
        self.page8_guardian_name_field_display_name = 'Name of the Guardian:'
        self.page8_guardian_name_field_value = ''
        self.page8_guardian_address_field_display_name = 'Address:'
        self.page8_guardian_address_field_display_value = ''
        self.page8_guardian_city_field_display_name = 'City/ Town/Village:'
        self.page8_guardian_city_field_display_value = ''
        self.page8_guardian_pincode_field_display_name = 'Pin Code:'
        self.page8_guardian_pincode_field_display_value = ''
        self.page8_guardian_state_field_display_name = 'State:'
        self.page8_guardian_state_field_display_value = ''
        self.page8_relationship_with_holder_display_name = 'Relationship With Account Holder:'
        self.page8_relationship_with_holder_value = ''
        self.page8_instructions_heading ='Standing Instructions:'     

        self.page8_instruction1_display_name = '1 I/We authorise you to receive credits automatically into my / our account'
        self.page8_instruction1_options = ['Yes','No']
        self.page8_instruction1_selcted_options = [self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('receive_credit_auth_status','')]

        self.page8_instruction2_display_name = '2 SMS Alert Facility'
        self.page8_instruction2_options = ['1st Holder','All Joint Holders','No']
        self.page8_instruction2_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('first_holder_sms_alert',''))]

        self.page8_instruction3_display_name = '3 Account Statement requirment :'
        self.page8_instruction3_options = ['Weekly','Monthly']
        self.page8_instruction3_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('account_statement_requirement',''))]

        self.page8_instruction4_display_name = '4 I/We request you to send Electronic Transaction-Cum-Holding Statements at Sole/ First Holders Email id stated in the account opening form.'
        self.page8_instruction4_options = ['Yes','No','E-CAS']
        self.page8_instruction4_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('electronic_transaction_holding_statement',''))]

        self.page8_instruction5_display_name = '5 Do you wish to receive Dividens/Interest directly into your bank account mentioned in KYC'
        self.page8_instruction5_options = ['Yes','No']
        self.page8_instruction5_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('dividend_interest_receive_option',''))]

        self.page8_instruction6_display_name = '6 Standing Instruction for Auto Pledge Confirmation by Pledgee'
        self.page8_instruction6_options = ['Yes','No']
        self.page8_instruction6_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('auto_pledge_confirmation',''))]

        self.page8_instruction7_display_name = '7 Option for Issuance of Delivery Instruction Slip (DIS) Booklet.'
        self.page8_instruction7_options = ['With A/C Opening','On Request']
        self.page8_instruction7_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('did_booklet_issuance',''))]

        self.page8_instruction8_display_name = '8 Basic Services Demat Account (BSDA)'
        self.page8_instruction8_options = ['Yes','No']
        self.page8_instruction8_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('bsda',''))]
        self.page8_instruction8_declaration_text = '''
        <font name="LatoBold">BSDA Declartion:</font> I/We have read and understood the SEBI guidelines for facility for a BSDA. I/We hereby declare that I/We am/are eligible to open a DP
        account as a BSDA holder and undertake to comply with the requirements specified by SEBI or any such authority for such facility from time to time. I/We
        also understand that in case I/We at any point of time do not meet the eligibility as a BSDA holder, my/our aforesaid DP account is liable to be converted to
        regular account.Further, by choosing "NO" I understand that I dont want to opt for BSDA facility at any point of time. Futher, I understand that to avail the
        facility of BSDA in furure, I have to provide written request.
        '''

        self.page8_instruction9_display_name = '9 Mode of operation for joint accounts'
        self.page8_instruction9_options = ['Jointly','Any one of the holders or survivor(s)']
        self.page8_instruction9_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('joint_account_operation_mode',''))]
        self.page8_instruction9_subinstruction_display_name = '''
        Consent for Communication to be received by first account holder/ all Account holder:<br/>
        (Tick the applicable box. If not marked the default option would be first holder)
        '''
        self.page8_instruction9_subinstruction_options = ['First Holder','All Holder)']
        self.page8_instruction9_subinstruction_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('consent_for_communication',''))]

        self.page8_instruction10_display_name = '10 I/We Would like to share the email id with the RTA'
        self.page8_instruction10_options = ['Yes','No']
        self.page8_instruction10_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('share_email_id_with_rta',''))]

        self.page8_instruction11_display_name = '11 I/We Would like to receive the annual report (If Not selected it will be physical)'
        self.page8_instruction11_options = ['Electronic','Physical']
        # Todo: Define enum value defined for these options, and use get_enum_value_from_key() method
        self.page8_instruction11_selected_options = [self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('receive_annual_report','')]#[get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('receive_annual_report',''))]

        self.page8_instruction12_display_name = '12 PAN is seeded with Adhaar'
        self.page8_instruction12_options = ['Exempted','Yes','No']
        self.page8_instruction12_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('aadhaar_pan_seed_status',''))]

        self.page8_instruction13_display_name = '''13 Transactions Using Secured Texting Facility <font name="LatoBold">(TRUST)</font>'''
        self.page8_instruction13_options = ['Yes','No']
        self.page8_instruction13_selected_options = [get_enum_value_from_key(self.data.get('dp_information', {}).get('standing_info_from_client', {}).get('trust',''))]

        self.page8_instructions_untertaking = '''
        (Refer to terms & Conditions given as Annexure - B)<br/>
        I wish to avail the Trust Facility using the mobile number registered for SMS alert Facility, I have read and understood the terms
        and conditions precribed by CDSL for the same.<br/>
        I /We Wish to register the following clearing member ID under my/our Below mentioed BO ID registered as TRUST
        '''

        self.page8_stock_exchange_table_data = [
            ['<font color = "#000000">Stock Exchange Name/ID</font>','<font color = "#000000">Clearing Member Name</font>','<font color = "#000000">Clearing Member ID</font>'],
            ['','','']
        ]

        self.page8_ucc_mapping_heading = '14 UCC Mapping for DP account'
        self.page8_ucc_mapping_table = [
            ['<font color = "#000000">UCC Code</font>','<font color = "#000000">Exchange ID</font>','<font color = "#000000">Segment ID</font>','<font color = "#000000">CM ID</font>','<font color = "#000000">TM ID</font>'],
            [self.data.get('dp_information', {}).get('ucc_mapping_1', {}).get('ucc_code_1',''),self.data.get('dp_information', {}).get('ucc_mapping_1', {}).get('exchange_id_1',''),self.data.get('dp_information', {}).get('ucc_mapping_1', {}).get('segment_id_1',''),self.data.get('dp_information', {}).get('ucc_mapping_1', {}).get('cm_id_1',''),self.data.get('dp_information', {}).get('ucc_mapping_1', {}).get('tm_id_1','')],
            [self.data.get('dp_information', {}).get('ucc_mapping_2', {}).get('ucc_code_2',''),self.data.get('dp_information', {}).get('ucc_mapping_2', {}).get('exchange_id_2',''),self.data.get('dp_information', {}).get('ucc_mapping_2', {}).get('segment_id_2',''),self.data.get('dp_information', {}).get('ucc_mapping_2', {}).get('cm_id_2',''),self.data.get('dp_information', {}).get('ucc_mapping_2', {}).get('tm_id_2','')],
        ]

        self.page8_holder_sign_heading = 'Signature of Holders'
        self.page8_holder_signature_field_lable = 'Holder Signature'
        self.page8_holder_signature_field_value = ''


        
        # Page 9 - Declaration Section
        self.page9_declaration_heading = 'Declaration'

        self.page9_declaration_content = '''
        The rules and regulations of the Depository and Depository Participants pertaining to an account which are in force now have been read by
        me/us and I/we have understood the same and I/we agree to abide by and to be bound by the rules as are in force from time to time for such
        accounts. I/We hereby declare that the details furnished above are true and correct to the best of my our knowledge and belief and I/we
        undertake to inform you of any changes therein, immediately. In case any of the above information is found to be false or untrue or misleading or
        misrepresenting. I am/We are aware that I/we may be held liable for it. I/We further agree that any false / misleading information given by me/us
        or suppression of any material information will render my account liable for termination and suitable action. In case non resident account, I/we
        also declare that I/we have complied and will continue to comply with FEMA regulations.<br/><br/>

        I/We do hereby declare that I have not been involved in any unlawful activities and I have not been declared a defaulter or my name is not
        appearing in defaulter database as per SEBI/Various Exchange / Regulatory Bodies, etc. I further declare that the above mentioned declaration /
        True and correct.<br/><br/>

        I/we acknowledge the receipt of copy of the document, "Rights and Obligations of the Beneficial Owner and Depository Participant".
        In case of joint account, on death of any of the joint account holders, the surviving account holder(s) has to inform Participant about the death of
        account holder(s) with required documents within one year of the date of demise.
        '''

        # Holders and Signature Table
        _kyc_holders = self.data.get('kyc_holders', [])
        self.page9_holders_signature_table_data = [
            ["Name of the Holders", "", "Signature of Account Holders"],
            ["First Holder", f"<font color={PdfColors().filled_data_color}>{(_kyc_holders[0] if 0 < len(_kyc_holders) else {}).get('kyc_holder', {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""],
            ["Second Holder", f"<font color={PdfColors().filled_data_color}>{(_kyc_holders[1] if 1 < len(_kyc_holders) else {}).get('kyc_holder', {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""],
            ["Third Holder", f"<font color={PdfColors().filled_data_color}>{(_kyc_holders[2] if 2 < len(_kyc_holders) else {}).get('kyc_holder', {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""],
        ]

        # self.page9_holders_signature_table_data = [
        #     ["Name of the Holders", "", "Signature of Account Holders"],
        #     ["First Holder", f"<font color='#0000FF'>{(_kyc_holders[0] if 0 < len(_kyc_holders) else {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""],
        #     ["Second Holder", f"<font color='#0000FF'>{(_kyc_holders[1] if 1 < len(_kyc_holders) else {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""],
        #     ["Third Holder", f"<font color='#0000FF'>{(_kyc_holders[2] if 2 < len(_kyc_holders) else {}).get('pan_verification',{}).get('pan_details',{}).get('name_in_pan','')}</font>", ""]
        # ]

        # Page 10 - Nominee Details
        self.page10_table_heading = 'Annexure - A (Nomination Details (Trading & DP))'
        self.page10_nominate_option1_text = 'I / We do not wish to nominate'
        self.page10_nominate_option1_description = '''I / We hereby confirm that I / We do not wish to appoint any nominee(s) in my / our trading / demat account and understand the issues involved in nonappointment
        of nominee(s) and further are aware that in case of death of all the account holder(s), my / our legal heirs would need to submit all the requisite
        documents / information for claiming of assets held in my / our trading / demat account, which may also include documents issued by Court or other such
        competent authority, based on the value of assets held in the trading / demat account.
        '''
        self.page10_nominate_option2_text = 'I wish to nominate (As per details given Below)'
        self.page10_nominate_option2_description = '''
        I/We wish to make a nomination and do hereby nominate the following person(s) who shall receive all the assets held in my / our account in the event of my
        / our death.
        '''
        self.page10_nomination_selection = self.data.get('nomination_details',{}).get('general',{}).get('client_nominee_appointment_status','')
        ##### Nominee Details Section
        self.page10_nominee_details:list[NomineeDetails] = [NomineeDetails(nominee_data=nominee_data.get('nominee',{})) for nominee_data in self.data.get('nomination_details', {}).get('nominees',[])]

        self.page10_nomination_undertaking_text = 'This nomination shall supersede any prior nomination made by me / us and also any testamentary document executed by me / us.'
        self.page10_nominee_signature_field_label = 'Holder Signature'
        # Page 11
        self.page11_left_header = '''
        Way2Wealth Brokers Pvt. Limited<br/>
        NSDL DP-ID: IN303077 and CDSL DP ID - 12062900, 12031500<br/>
        Schedule 'A' Charges for Depository Services applicable to Individuals/HUF/Corporate
        '''
        self.page11_dp_client_id_field_lable = 'DP ID/CLIENT ID'
        self.page11_dp_client_id_field_value = ''
        self.page11_table_heading = "Schedule 'A' Charges for Depository Services applicable to Individuals/HUF/Corporate"
        self.page11_table_data = [
            ['TRANSACTION TYPE','SCHEME - 1','SCHEME - 2','BSDA / IPO'],
            ['Refundable Deposit *','Nil','2000/- *','Nil'],
            ['Annual Maintenance Charges','Rs.550/- p.a. per account','Nil','AMC Nil Upto Stock Value of Rs.400,000/-, Rs.100/- for Stock Value Rs.400,001/- to Rs.10 Lac'],
            ['Demat & Remat Charges','','',''],
            ['Demat Charges','Rs.2/- per cert. + Rs.150/-','',''],
            ['Remat Charges','Rs.25/- per cert. (for every hundred securities) + Rs.150/-','',''],
            ['Demat Rejection Charges','Rs.150/- per rejection','',''],
            ['Transaction Charges','','',''],
            ['Selling through M/s.Way2Wealth Brokers Pvt. Ltd with POA','Nil','Rs.10/- per Debit transfer','Rs.25/- Per Debit Instruction']
            # Todo: Remaining data ...
        ]
        self.page11_condition_description = '''
        * Deposit amount of Rs.2000/- [ Rs.5000/- in case of corporate accounts] will be payable upfront and will be refunded only on closure of Demat account. AMC of
        600/- will be deducted from the deposit amount if the account is closed within one year of the account opened or within one year of the scheme change. ** In
        case of Corporate Accounts - AMC will be = W2W AMC + AMC charged by Depository
        '''
        self.page11_tnc_heading = 'Terms & Conditions:'
        self.page11_tnc = '''
        1) The Above schedule of charges is based on NSDL and CDSL charges charged on us and is subject to revision at the discretion of Way2Wealth
        Brokers Pvt. Ltd. Any revision in the schedule of charges will be notified by ordinary post/email/electronic mode within 30 days notice.<br/>
        2) All the percentages in the above rates would be applied on the value of the transactions as computed by NSDL, And CDSL.<br/>
        3) Any extra statement would be charged @ Rs.15/- for first 10 pages, thereafter it would be charged a Rs.2/- per page.<br/>
        4) For accounts opened during the year, AMC will be charged on pro-rata basis in the first bill. The AMC is charged for first/one year and will be automatically
        renewed at the end of the financial year at the prevailing rates, unless Way2Wealth Brokers Pvt. Ltd received written communication in the
        prescribed format. AMC once paid will not be refunded on any circumstances. GST as applicable will be levied extra.<br/>
        5) CAS Transaction Statement will be sent monthly, only if there is any transaction in the relevant month. If there is no transaction, statement will be
        provided once in a year. CAS charges will be levied as per actuals.<br/>
        6) Demand Draft in favour of “Way2Wealth Brokers Pvt. Ltd” payable at “Bangalore” only. No outstation cheques will not be accepted other than our
        branches located.<br/>
        7) Cheque Bounce charges will be applied based on charges as determined by the bankers with minimum of Rs.50/- per instance.<br/>
        8) All market instructions for transfer must be received latest by 4.00 p.m. on the previous working day prior to payin day as per SEBI Guidelines. All off market
        instructions for transfer must be received at least 24 hours before the execution date. Late instruction would be accepted at the account holder's sole risk/responsibility.<br/>
        9) Charges quoted above are for the services listed. Any service not quoted above will be charged separately.<br/>
        10) Depository Service charges bills should be paid on or before the due date. Interest @ 2% p.m. will be charged on the outstanding amount for non- payment.
        Notwithstanding this, DP reserves rights to “Freeze depository account for debit transactions” in case client fails to pay charges.<br/>
        11) This rate card supersedes all our earlier rate structures.<br/>
        12) Insurance charges on holding if any, charged by NSDL, will be recovered from the clients at the discretion of the DP, in proportion to their holdings.<br/>
        13) *Stamp duty payable as per local charges. For additional services like Internet agreement, Power of Attorney, Fax Indemnity etc., stamp duty payable at actual.
        '''

        self.page11_tnc_undertaking_text = '''
        I/We have accepted the Schedule 'A' as stated herein above. We have chosen to open our Trading account with Way2Wealth Brokers Pvt. Ltd. for debiting the
        depository service charges. I/We hereby authorize Way2Wealth Brokers Private Limited for debiting amount due towards Scheme-2 to My/Our Trading account.
        '''

        self.page11_holder_signature_field_lable = 'Holder'

        
        # Page 12 - Internet & Wireless Technology Based Trading Facility Section
        self.page12_heading = 'Internet & wireless technology based trading facility provided by stock broker to the client'

        self.page12_subheading = (
            '(All the clauses mentioned in the "Rights and Obligations" document(s) shall be applicable. Additionally, the clauses '
            'mentioned herein shall also be applicable.)'
        )

        self.page12_clauses = '''
        1. Stock broker is eligible for providing Internet Based trading (IBT) and securities trading through the use of wireless
        technology that shall include the use of devices such as mobile phone, laptop with data card, etc. which use Internet
        Protocol (IP). The stock broker shall comply with all requirements applicable to internet based trading/securities trading
        using wireless technology as may be specified by SEBI & the Exchanges from time to time.<br/><br/>
        2. The client is desirous of investing/trading in securities and for this purpose, the client is desirous of using either the internet
        based trading facility or the facility for securities trading through use of wireless technology. The Stock broker shall provide
        the Stock broker's IBT Service to the Client, and the Client shall avail of the Stock broker's IBT Service, on and subject to
        SEBI/Exchanges Provisions and the terms and conditions specified on the Stock broker's IBT website provided that they
        are in line with the norms prescribed by Exchanges/SEBI.<br/><br/>
        3. The stock broker shall bring to the notice of client the features, risks, responsibilities, obligations and liabilities associated
        with securities trading through wireless technology/internet/smart order routing or any other technology should be brought
        to the notice of the client by the stock broker.<br/><br/>
        4. The stock broker shall make the client aware that the Stock Broker's IBT system itself generates the initial password and
        its password policy is as stipulated in line with norms prescribed by Exchanges/SEBI.<br/><br/>
        5. The Client shall be responsible for keeping the Username and Password confidential and secure and shall be solely
        responsible for all orders entered and transactions done by any person whosoever through the Stock broker's IBT System
        using the Client's Username and/or Password whether or not such a person was authorized to do so. Also the client is
        aware that authentication technologies and strict security measures are required for the internet trading/securities trading
        through wireless technology through order routed system and undertakes to ensure that the password of the client and/or
        his authorized representative are not revealed to any third party including employees and dealers of the stock broker.<br/><br/>
        6. The Client shall immediately notify the Stock broker in writing if he forgets his password, discovers security flaw in Stock
        Broker's IBT System, discovers/suspects discrepancies/unauthorized access through his username/password/account with
        full details of such unauthorized use, the date, the manner and the transactions effected pursuant to such unauthorized
        use, etc.<br/><br/>
        7. The Client is fully aware of and understands the risks associated with availing of a service for routing orders over the
        internet/securities trading through wireless technology and Client shall be fully liable and responsible for any and all acts
        done in the Client's Username/password in any manner whatsoever.<br/><br/>
        8. The stock broker shall send the order/trade confirmation through email to the client at his request. The client is aware that
        the order/trade confirmation is also provided on the web portal. In case client is trading using wireless technology, the stock
        broker shall send the order/trade confirmation on the device of the client.<br/><br/>
        9. The client is aware that trading over the internet involves many uncertain factors and complex hardware, software,
        systems, communication lines, peripherals, etc. are susceptible to interruptions and dislocations. The Stock broker and the
        Exchange do not make any representation or warranty that the Stock broker's IBT Service will be available to the Client at
        all times without any interruption.<br/><br/>
        10. The Client shall not have any claim against the Exchange or the Stockbroker on account of any suspension, interruption,
        non-availability or malfunctioning of the Stock broker's IBT System or Service or the Exchange's service or systems or nonexecution
        of his orders due to any link / system failure at the Client/Stock brokers/Exchange end for any reason beyond the
        control of the stockbroker/Exchanges.<br/><br/>
        '''

        # Declaration Section
        self.page12_declaration_heading = 'Declaration'

        self.page12_declaration_content = '''
            1. I/We hereby declare that the details furnished above are true and correct to the best of my/our knowledge and belief,
            and I/We undertake to inform you of any changes therein, immediately. In case any of the above information is found to
            be false, untrue, misleading, or misrepresenting, I/We am/are aware that I/We may be held liable for it.<br/><br/>
            
            2. I/We confirm having read/been explained and understood the contents of the document on policy and procedures of the
            stock broker and the tariff sheet.<br/><br/>
            
            3. I/We further confirm having read and understood the contents of the 'Rights and Obligations' document(s) and 'Risk
            Disclosure Document'. I/We do hereby agree to be bound by such provisions as outlined in these documents. I/We have also
            been informed that the standard set of documents has been displayed for information on the stock broker\'s designated website, if any.
        '''

        # Client Details Section
        self.page12_client_name_label = 'Client Name:'
        self.page12_client_name_value = self.page_kyc_details[0].identity_name_value if 0 < len(self.page_kyc_details) else ''

        self.page12_place_label = 'Place:'
        self.page12_place_value = self.page_kyc_details[0].declaration_place_value if 0 < len(self.page_kyc_details) else ''

        self.page12_date_label = 'Date:'
        self.page12_date_value = ''

        self.page12_signature_label = 'Client Signature'
        self.page12_signature_value = ''
 
        
        # Page 13 - Issuance of Electronic Contract Notes Letter Content

        # Address Section
        self.page13_addressee = '''
        To,<br/>
        Way2Wealth Brokers Private Limited,
        Rukmini Towers, 3rd & 4th Floor, # 3/1,
        Platform Road, Sheshadripuram,
        Bangalore - 560 020<br/>
        Dear Sirs,
        '''

        # Salutation
        self.page13_subject1 = 'Subject: Issuance of Electronic Contract notes, Statements and Communications'

        self.page13_body1 = '''
        I/we understand that digital signed contract notes and other electronic communications is a specialized service offered by the member
        which is optional in nature and this document has been signed by me/us voluntarily without any coercion or force. I/we also understand
        that I/we have a right to terminate this document. However in such an event this facility shall be liable to be terminated. I/we agree and
        permit the Member to provide digitally signed contract notes through internet (web-based) at the registered email id mentioned in the
        KYC which belongs to me/us.<br/><br/>
        I/we shall access the contract notes/ confirmations of the trades executed on my/our behalf on the trade date electronically. I/we
        understand that it is my/our responsibility to review all confirmations, contract notes, statements, notices and other communications including but not limited to margin and
        maintenance calls, etc. All information contained therein shall be binding on me/us, if I/we do not object, either in writing or via
        electronic mail within 24 hours after any such documents are available to me/us.<br/>
        Should I/we experience any difficulty in opening a document electronically delivered by the Member, the Member may, on
        receipt of intimation from the me/us in that behalf, make the required delivery by any other electronic means (e-mail, fax,
        electronic mail attachment, or in the form of an available download from the back-office website) or in paper based format. Failure by
        me/us to advise the Member of such difficulty within twenty four hours after delivery shall serve as an affirmation that I/we
        was/were able to receive and open the said document on the internet.<br/><br/>
        I/we agree not to receive the contract notes in paper form from the Member. Provided however that in case when the Member is not
        able to provide Contract Note to me/us through (web based) electronic medium due to any unforeseen problems, the Member
        would ensure that the contract note reaches me/us in physical form as per the time schedule stipulated in the Bye-Laws, Rules and
        Regulations of the Exchanges.<br/><br/>
        I/we shall take all the necessary steps to ensure confidentiality and secrecy of the login name and password which secure my/our
        email-ID. Unless I/we lodge a complaint with the Member as to my/our inability to access the system, it would be presumed that
        contract notes and all have been properly delivered.<br/><br/>
        I/we agree that the Member fulfils its legal obligation to deliver to the Client any such document if sent via electronic delivery and the
        Member has not received any report indicating bouncing back of such electronic delivery.<br/><br/>
        I/we agree that as an alternative to the e-mail communication and/or in case of non-receipt of the digital contract note through email.
        I/we shall utilize the facility of accessing the website hosted by the Member to access the contract note.<br/><br/>
        I/we agree that in any change in the Email-ID specified above shall be communicated by me/us to the Member in writing or digitally.<br/><br/>
        I/We request you allocate a login and mail the password to me/us for accessing your website to download my contract notes and my statement.
        '''

        self.page13_client_signature_table1 = [
            ['Client Name:',self.page_kyc_details[0].identity_name_value if 0 < len(self.page_kyc_details) else ''],
            ['Client Signature','']
        ]

        self.page13_subject2 = 'Subject: Maintenance of Running Account (Voluntary)'

        self.page13_body2_part1 = '''
        I/We are dealing through you as a client in Capital Market and/or Future & Option segment and/or Currency segment and/or
        Interest Rate future Segment & in order to facilitate ease of operations and upfront requirement of margin for trade.<br/><br/>
        1. I/We request you to maintain running balance in my account & retain the credit balance in my/our account and to use the
        unused funds towards my/our margin/pay-in/other future obligation(s) of any segment(s) of any or all the
        Exchange(s) /Clearing corporation unless I/We instruct you otherwise.<br/><br/>
        2. In case I/We have an outstanding obligation on the settlement date, you may retain the requisite funds towards such
        obligations and may also retain the funds up to the extent of allowed by SEBI/Exchange/relevant regulatory from time to time.<br/><br/>
        3. I/We request you to settle my fund and securities account<br/>
        '''

        self.page13_body2_settlement_field_label = '(choose one option)'
        self.page13_body2_settlement_field_options = ['Once in a calendar Month','Once in every calendar Quarter']
        self.page13_body2_settlement_field_selected_options = []

        self.page13_body2_part2 = '''
        4. I/We confirm you that I will bring to your notice any dispute arising from the statement of account or settlement so made
        in writing preferably within 30 working days from the date of receipt of funds or statement of account or
        statement related to it, as the case may be at your registered office.<br/><br/>
        5. I/We understand that I/We can revoke the above-mentioned authority at any time by submitting such request in writing to
        us and the same would be processed and updated by us within 2 working days from receipt of such written request.<br/><br/>
        6. This running account authorization would continue until it is revoked by me.<br/>
        '''

        self.page13_client_signature_table2 = [
            ['Client Name:',self.page_kyc_details[0].identity_name_value if 0 < len(self.page_kyc_details) else ''],
            ['Client Signature','']
        ]
        

        # Page 14: Staic content page, can be directly added as image into pdf.

        # Page 15 - Acknowledgment Letter Content
        # Address Section
        self.page15_letter_addressee = '''
        To,<br/>
        Way2Wealth Brokers Private Limited<br/>
        Rukmini Towers, 3rd & 4th Floor, # 3/1,<br/>
        Platform Road, Sheshadripuram,<br/>
        Bangalore - 560 020, Karnataka (India)<br/>
        '''

        # Subject
        self.page15_letter_subject = 'Sub: Acknowledgement for receiving the client registration documents'

        # Body Content
        self.page15_body_content = '''
        Dear Sir,<br/><br/>
        This is to acknowledge the receipt of the following listed client registration documents.
        '''

        # Table of Documents
        self.page15_documents_table_data = [
            ["S. No.", "Brief Significance of the Document"],
            ["1", "Client Registration Form (KYC)"],
            ["2", "Rights and Obligation"],
            ["3", "Risk Disclosure Document (RDD)"],
            ["4", "Guidance Note"],
            ["5", "Policies & Procedures"],
            ["6", "Write up on PMLA (Check List)"],
            ["7", "Tariff Sheet"],
            ["8", "Contact Details"],
            ["9", "Rights and obligations of the Beneficial owner and Depository Participants"],
            ["10", "Additional Voluntary clauses supplemental to Account Opening Form"],
            ["11", "Smart Terms & Conditions for receiving SMS alerts from CDSL"],
            ["12", "Most Important Terms and Conditions (MITC)"]
        ]

        # Closing Declaration
        self.page15_closing_declaration = f'''
        I further state and confirm that I have read and understood all the clauses of the aforesaid document. I also confirm that I have
        received the relevant clarifications, wherever required, from the officials of <font name="LatoBold">Way2Wealth Brokers Private Limited</font> to my complete
        understanding and satisfaction.<br/><br/>
        [* All the standard documents, (2-6,9,11-12) may be viewed through
        <font color={PdfColors().filled_data_color}><a href='https://www.way2wealth.com/customer-care/downloads'>https://www.way2wealth.com/customer-care/downloads</a></font> - “Investor Awareness and Compliance”.]<br/><br/>
         Yours Faithfully,<br/>
        '''

        # Applicant Information
        self.page15_applicant_name_label = 'Name of the Applicant:'
        self.page15_applicant_name_value = self.page_kyc_details[0].identity_name_value if 0 < len(self.page_kyc_details) else ''

        self.page15_applicant_signature_label = 'Signature of the Applicant:'
        self.page15_applicant_signature_value = ''

        # Page 16 is empty
        # Page 17,18 and 19,20 are copy of Page 3,4

from enum import Enum
class FieldMapHelper(Enum):
    IND = "Individual"
    CORPORATE = "Corporate Body"
    PARTNERSHIP = "Partnership Firm"
    TRUST = "Trust"
    HUF = "HUF"
    UNINCORPORATED = "Unincorporated Association or a Body of Individuals"
    BANKS = "Banks/Institutional Investors"
    SOCIETY = "Registered Society"
    TRADING = "Trading"
    DP = "DP"
    TRADING_AND_DP = "Trading and DP"
    _1 = "One"
    _2 = "Two"
    _3 = "Three"

    # Residential Status 
    RI = "RI"
    NRI = "NRI"
    PIO = "PIO"
    FOREIGN_NATIONAL = "Foreign National"
    YES = "Yes"
    NO = "No"

    # dependencies
    SELF = "Self"
    SPOUSE = "Spouse"
    DEPENDENT_PARENT = "Dependent Parent"
    DEPENDENT_CHILD = "Dependent Child"
    INDIA = "India"
    USA = "USA"

    SAME_AS_PERMANENT_ADDRESS = "Same as Permanent Address"
    # address type
    RESIDENTIAL = "Residential"
    RESIDENTIAL_BUSINESS = "Residential Business"
    BUSINESS_ADDRESS = "Business"
    REGISTERED_OFFICE = "Registered Office"
    UNSPECIFIED = "Unidentified"

    UPTO_1L = "0-1Lac"
    _1_TO_5L = "1-5Lac"
    _5_TO_10L = "5-10Lac"
    _10_TO_25L = "10-25Lac"
    _25L_TO_1CR = "25Lac-1Cr"
    _1CR_TO_5CR = "1Cr-5Cr"


    # Occupation
    PRIVATE_SECTOR = "Private Sector"
    PUBLIC_SECTOR = "Public Sector"
    GOVT_SERVICE = "Govt. Service"
    PROFESSIONAL = "Professional"
    HOUSE_WIFE = "Housewife"
    STUDENT = "Student"
    SALARIED = "Salaried"
    SELF_EMPLOYED = "Self employed"
    BUSINESS = "Business"
    AGRICULTURIST = "Agranulturist"
    RETIRED = "Retired Person"
    # OTHERS = "Others"

    # PEP 
    PEP = "Politically Exposed Person"
    RELATED = "Related to Politically Exposed Person"
    NA = "Not Applicable"

    NOMINEE_IS_A_MINOR = "Nominee is a minor"
    VOTER = "Voter ID"
    PAN = "PAN"
    EQUITY = "Equity"
    FNO = "F & O"
    CURRENCY = "Currency"
    COMMODITY = "Commodity"
    MUTUAL_FUND = "Mutual Fund"
    SLB = "SLB"
    PHYSICAL = "Physical Contact Note"
    ELECTRONIC = "Electronic Contact Note (ECN)"
    BEGINNER = "1-3"
    INTERMEDIATE = "3-5"
    EXPERT = "5+"

    # Introducer Status
    CLIENT = "Client"
    SUB_BROKER_OR_AP = "Sub-Broker/AP"
    REMISIER = "Remisier"

    DAILY = "Daily"
    MONTHLY = "Monthly"

    # Depositories
    NSDL = "NSDL"
    CDSL = "CDSL"
    TRUST_FACILITY_ON_MOBILE = ("I wish to avail the Trust Facility using the mobile "
                                "number registered for SMS alert Facility. I have read "
                                "and understood the terms and conditions prescribed by CDSL "
                                "for the same.")
    RISK_MANAGEMENT_POLICY = ("The stock broker's Risk Management Policy provides details "
                              "about how the trading limits will be given to you and the "
                              "tariff sheet provides the charges that the stock broker will "
                              "levy on you.")
    SEBI_TNC = ("You have read and understood the rights and obligations of the stock broker; "
                "sub-broker and client as prescribed by SEBI and stock exchanges.")
    WEEKLY = "Weekly"
    WITH_AC_OPENING = "With A/C Opening"
    ON_REQUEST = "On Request"
    JOINTLY = "Jointly"
    ANY_ONE_HOLDER_OR_SURVIVORS = "Any one of the holders or survivor(s)"
    FIRST_HOLDER = "First Holder"
    ALL_HOLDERS = "All Holders"
    EXEMPTED = "Exempted"
    ALL_JOINT_HOLDER = "All Joint Holders"
    #Gender
    M = "Male"
    F = "Female"
    T = "Transgender"

    # Marital Status
    MARRIED = "Married"
    SINGLE = "Single"

    E_CAS = "E-CAS"


    # Nationality
    INDIAN = "Indian"
    OTHERS = "Others"

    # Bank A/c Type
    SAVINGS = 'Savings'
    CURRENT = 'Current'

    # Trading Experience
    NIL = "Nil"
    _1_3YEARS = "1-3 Years"
    _3_6YEARS = "3-6 Years"
    MORE_THAN_6YEARS = "More than 6 years"

    # Kit Options
    PHYSICAL_KIT = "Physical"
    ELECTRONIC_KIT = "Electronic Form"

    # DP A/C Type
    RESIDENT_INDIAN = "Resident Indian"
    NRI_REPATRIABLE = "NRI - Repatriable"
    NRI_NON_REPATRIABLE = "NRI Non-Repatriable"
    FN = "FN"
    PROMOTER = "Promoter"


# Function to get enum value from string key 
def get_enum_value_from_key(key): 
    if not key:
        return ""
    # Prepend '_' if the key starts with a number 
    if key[0].isdigit(): 
        key = f"_{key}"
    try: 
        return FieldMapHelper[key].value 
    except KeyError: 
        logger.debug(f"{key} - not matched with any of the options")
        return ""
    
from datetime import datetime
def get_formatted_date(date:str):
    if not date:
        return ""
    try:
        # Parse the input string into a datetime object 
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') 
        # Format the datetime object into the desired format 
        return dt.strftime('%d/%m/%Y')
    except ValueError:
        logger.debug(f"Error in formatting date {date}")
        return date
    