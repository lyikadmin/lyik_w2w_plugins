from ....way_2_wealth.aof.aof_individual.aof_ind_text_consts import AOFINDConstantsTexts
from ....components import PdfStyles, PdfTables, PdfComponents, PdfColors
from reportlab.platypus import BaseDocTemplate, Paragraph, PageBreak, Spacer, TableStyle, Table
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from html import escape
from ....images import load_logo
from .....pdf_utilities.utility import format_date, format_xml, split_into_chunks
from .....models.digi_aadhaar_data import Aadhaar, extract_aadhaar_data
from .....models.geocode_location import GeocodeLocation

class AOF_IND:
    def __init__(self,data:dict, date_of_submission:str,application_no:str,is_digilocker:bool=True):
        self.constant_texts = AOFINDConstantsTexts(json_data=data,application_no=application_no,is_digilocker=is_digilocker)
        self.date_of_form_submission = format_date(date_str=date_of_submission)


    async def get_pages(self,doc):

        pdf_components = PdfComponents()
        pdf_styles = PdfStyles()

        form_header = self._get_kyc_form_header(doc=doc)
        section1 = await self._get_kyc_section1(doc=doc)
        section2A = self._get_kyc_section2A(doc=doc)
        section2B = self._get_kyc_section2B(doc=doc)
        section_proof_of_address = self._get_proof_of_address(doc=doc)
        applicants_sign_section = await self._get_kyc_applicant_sign_section(doc=doc)
        section3 = self._get_kyc_section3(doc=doc)
        section4 = self._get_kyc_section4(doc=doc)
        section5_6_7 = self._get_kyc_section5_6_7(doc=doc)
        section8 = await self._get_kyc_section8(doc=doc)
        kyc_bottom_section = self._get_kyc_verification_details_section(doc=doc)

        # Geo Location data
        constant_texts = self.constant_texts
        geoloc_table = None
        if constant_texts.data.geocode_location and isinstance(constant_texts.data.geocode_location,GeocodeLocation):
            geoloc_details = pdf_components.create_bordered_input_box(doc=doc,text_value=f'Liveness taken at ({constant_texts.data.geocode_location.longitude}, {constant_texts.data.geocode_location.latitude}): {constant_texts.data.geocode_location.formatted_address}',height=0.6*inch,width=doc.width-doc.rightMargin,text_size=11,text_style=pdf_styles.normal_text_style(alignment=4,fontsize=9,indent=5)),
            geoloc_table = PdfTables().create_table(data=[[geoloc_details]],col_widths=[None],style=pdf_styles.padded_table_style())


        return [form_header,section1,section2A,section2B,section_proof_of_address,applicants_sign_section,PageBreak(),section3,section4,section5_6_7,section8,kyc_bottom_section, Spacer(1, 0.1 * inch), geoloc_table if geoloc_table else Spacer(1, 1)]
    
    async def _get_kyc_section1(self,doc:BaseDocTemplate):
    
        constant_texts = self.constant_texts
        
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        identity_details_heading = Paragraph(constant_texts.data.identity_details_title, style=pdf_styles.bold_text_style(alignment=0,fontsize=8))
        pan_help_text = Paragraph(constant_texts.data.pan_help_text, style=pdf_styles.normal_text_style(fontsize=8))
        photo_box_width = 1.5*inch
        pan = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_pan_label,value=constant_texts.data.identity_pan_value,width=(doc.width-doc.leftMargin*2-photo_box_width)/2,size=8)
        pan_field_with_help_text = pdf_tables.create_composite_table(table1=pan,table2=pan_help_text,col_widths=[(doc.width-doc.leftMargin*2-photo_box_width)/2,1,None])
        name = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_name_label,size=8,value=constant_texts.data.identity_name_value,width=doc.width- doc.rightMargin*2-photo_box_width )
        maiden_name = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_maiden_name_label,size=8,value=constant_texts.data.identity_maiden_name_value,width=doc.width- doc.leftMargin*2-photo_box_width )
        
        father_spouse_name = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_father_spouse_name_label,value=constant_texts.data.identity_father_spouse_name_value,width=doc.width-photo_box_width- doc.leftMargin*2,size=8)
        mother_name = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_mother_name_label,value=constant_texts.data.identity_mother_name_value,width=doc.width-photo_box_width- doc.leftMargin*2,size=8)


        gender = pdf_components.checkbox_field(doc,options=constant_texts.data.identity_gender_options,field_name_text=constant_texts.data.identity_gender_label,selected_options=constant_texts.data.identity_gender_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*0.5,size=8)
        marital_status = pdf_components.checkbox_field(doc,options=constant_texts.data.identity_marital_status_options,field_name_text=constant_texts.data.identity_marital_status_label,selected_options=constant_texts.data.identity_marital_status_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*0.5,size=8)

        gender_marital_status = pdf_tables.create_composite_table(table1=gender,table2=marital_status,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*0.5,1,(doc.width-photo_box_width- doc.leftMargin*2)*0.5])

        nationality = pdf_components.checkbox_field(doc,options=constant_texts.data.identity_nationality_options,field_name_text=constant_texts.data.identity_nationality_label,selected_options=constant_texts.data.identity_nationality_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*2/3,size=8)
        country_iso_code = pdf_components.get_text_field(doc=doc,field_name=constant_texts.data.identity_iso_country_code_label,value=constant_texts.data.identity_iso_country_code_value,width=(doc.width-photo_box_width- doc.leftMargin*2)/3,size=8)
        nationality_country_code_composite = pdf_tables.create_composite_table(table1=nationality,table2=country_iso_code,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*2/3,1,(doc.width-photo_box_width- doc.leftMargin*2)/3])

        residential_status = pdf_components.checkbox_field(doc,options=constant_texts.data.identity_residential_status_options,field_name_text=constant_texts.data.identity_residential_status_label,selected_options=constant_texts.data.identity_residential_status_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*2/3,size=8)
        residential_help_text = Paragraph(constant_texts.data.identity_residential_status_help_text, style=pdf_styles.normal_text_style(fontsize=8))
        residential_full_field = pdf_tables.create_composite_table(table1=residential_status,table2=residential_help_text,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*2/3,1,None])

        aadhaar = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_aadhar_label,value=constant_texts.data.identity_aadhar_value if constant_texts.data.is_digilocker else '',width=(doc.width-doc.leftMargin*2-photo_box_width)/2-10,size=8)
        dob = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_date_of_birth_label,value=constant_texts.data.identity_date_of_birth_value,width=(doc.width-photo_box_width- doc.leftMargin*2)/2,size=8)

        aadhar_dob = pdf_tables.create_composite_table(table1=aadhaar,table2=dob,col_widths=[(doc.width-doc.leftMargin*2-photo_box_width)/2,1,(doc.width-doc.leftMargin*2-photo_box_width)/2])
        # poi_field = pdf_components.get_text_field(doc,field_name=constant_texts.data.identity_poi_label,value=constant_texts.data.identity_poi_value,width=(doc.width-doc.leftMargin*2-photo_box_width),size=8)


        left = Table([[identity_details_heading],[pan_field_with_help_text],[name],[maiden_name],[father_spouse_name],[mother_name],[gender_marital_status], [nationality_country_code_composite],[residential_full_field],[aadhar_dob]])
        left.setStyle(pdf_styles.padded_table_style(top=1))

        _file_id =constant_texts.data.identity_passport_size_photo
        image_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        photo_box = pdf_components.create_bordered_input_box(doc,image_bytes=image_bytes,text_value=constant_texts.data.identity_passport_size_alt_text,text_style=pdf_styles.normal_text_style(alignment=1,fontsize=9),width=photo_box_width-10,height=photo_box_width,text_size=8)
        right = Table([[photo_box],[Paragraph(constant_texts.data.identity_passport_size_help_text,style=pdf_styles.bold_text_style(alignment=1,fontsize=7))]],style=pdf_styles.padded_table_style())
        # sectionA = pdf_tables.create_composite_table(table1=left,table2=right,col_widths=[(doc.width-doc.leftMargin-photo_box_width),1,photo_box_width])
        sectionA = Table([[left,right]],style=pdf_styles.bordered_table_style(h_margin=5,v_margin=5))
        # sectionA.setStyle(pdf_styles.bordered_table_style(h_margin=5,v_margin=5))

        return sectionA

    
    def _get_kyc_section2A(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        
        address_details_title = Paragraph(constant_texts.data.address_details_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        correspondence_address_field_title = Paragraph(constant_texts.data.address_correspondence_title,style=pdf_styles.bold_text_style(alignment=0,fontsize=8))
        address_lines = pdf_components.get_multiline_text(doc,width=doc.width - doc.leftMargin*2,lines=2,text=constant_texts.data.address_correspondence_value)
        city = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_city_label,value=constant_texts.data.address_city_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pincode = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_pincode_label,value=constant_texts.data.address_pincode_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        district = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_district_label,value=constant_texts.data.address_district_value,width=(doc.width-doc.rightMargin*2)/3,size=8)

        city_district_pincode = Table([[city,district,pincode]],style=pdf_styles.padded_justified_table_style())

        state = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_state_label,value=constant_texts.data.address_state_value,width=(doc.width-doc.rightMargin)*2/3-10,size=8)
        country = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_country_label,value=constant_texts.data.address_country_value,width=(doc.width-doc.rightMargin)/3-10,size=8)
        state_country = pdf_tables.create_composite_table(table1=state,table2=country,col_widths=[(doc.width-doc.rightMargin-10)*2/3,1,(doc.width-doc.rightMargin-10)/3])
        address_type = pdf_components.checkbox_field(doc,options=constant_texts.data.address_type_options,field_name_text=constant_texts.data.address_type_label,selected_options=constant_texts.data.address_type_selected_options,field_width=doc.width - doc.rightMargin*2,size=8)

        
        # proof_of_address = Paragraph('3. Proof of address to be provided by Applicant. Please submit ANY ONE of the following valid documents & tick against the document attached)', style=pdf_styles.normal_text_style(fontsize=8))
        # address_type = pdf_components.checkbox_field(doc,options=["Passport","Driving License", "Voter Id", "Telephone Bill(only LL)*", "Electricity Bill*","Registered Lease/Sale Agreement","Gas Bill*","UID","Bank Statement/Passbook","Others"],field_name_text='',field_width=doc.width - doc.rightMargin*2-20,size=8)
        # validity = pdf_components.get_text_field(doc,field_name='Validity/Expiry date of proof of address submitted',width=(doc.width-doc.rightMargin),size=8)
        # proof_num = pdf_components.get_text_field(doc,field_name='Proof No.',width=(doc.width-doc.rightMargin)*0.5-10,size=8)
        # condition_proof_num = pdf_tables.create_composite_table(table1=Paragraph('* Not more than 2 months old.', style=pdf_styles.normal_text_style(fontsize=8)),table2=proof_num,col_widths=[None,10,(doc.width-doc.rightMargin-10)*0.5])

        # permanent_address = Paragraph('4. Permanent Address of Resident Applicant if different from B1 abovee OR Overseas Address (Mandatory) for Non-Resident Applicant)', style=pdf_styles.normal_text_style(fontsize=8))
        # permanent_proof_of_address = Paragraph('5. Proof of address to be provided by Applicant. Please submit ANY ONE of the following valid documents & tick against the document attached)', style=pdf_styles.normal_text_style(fontsize=8))

        section2A = Table([[address_details_title],[correspondence_address_field_title],[address_lines],[city_district_pincode],[state_country],[address_type]])
        section2A.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return section2A

    def _get_kyc_section2B(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        permanent_address_details_title = Paragraph(constant_texts.data.address_permanent_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        address_lines = pdf_components.get_multiline_text(doc,width=doc.width - doc.leftMargin*2,lines=2,text=constant_texts.data.address_permanent_value)
        city = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_permanent_city_label,value=constant_texts.data.address_permanent_city_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pincode = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_permanent_pincode_label,value=constant_texts.data.address_permanent_pincode_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        district = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_permanent_district_label,value=constant_texts.data.address_permanent_district_value,width=(doc.width-doc.rightMargin*2)/3,size=8)

        city_district_pincode = Table([[city,district,pincode]],style=pdf_styles.padded_justified_table_style())

        state = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_permanent_state_label,value=constant_texts.data.address_permanent_state_value,width=(doc.width-doc.rightMargin)*2/3-10,size=8)
        country = pdf_components.get_text_field(doc,field_name=constant_texts.data.address_permanent_country_label,value=constant_texts.data.address_permanent_country_value,width=(doc.width-doc.rightMargin)/3-10,size=8)
        state_country = pdf_tables.create_composite_table(table1=state,table2=country,col_widths=[(doc.width-doc.rightMargin-10)*2/3,1,(doc.width-doc.rightMargin-10)/3])
        address_type = pdf_components.checkbox_field(doc,options=constant_texts.data.address_permanent_type_options,field_name_text=constant_texts.data.address_permanent_type_label,selected_options=constant_texts.data.address_permanent_type_selected_options,field_width=doc.width - doc.rightMargin*2,size=8)

        section2B = Table([[permanent_address_details_title],[address_lines],[city_district_pincode],[state_country],[address_type]])
        section2B.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return section2B
    
    def _get_proof_of_address(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()
        proof_of_address_section_title = Paragraph(constant_texts.data.proof_of_address_label, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        proof_of_address_section_title_help_text = Paragraph(constant_texts.data.proof_of_address_label_help_text, style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        proof_of_address_section_heading = pdf_tables.create_table(data=[[proof_of_address_section_title,Spacer(10,0),proof_of_address_section_title_help_text]],
                                                                   col_widths=[1.5*inch,10,None],style=pdf_styles.padded_table_style())
        poa_table_data = [[Paragraph(cell, style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=colors.black)) for cell in row] for row in constant_texts.data.proof_of_address_table_data]
        
        
        for i in range(1, 8): 
            poa_table_data[i][0] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=''
                )
            
        for i in range(1, 8): 
            poa_table_data[i][1] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=''
                )

        perm_address_type_index = 0
        _address_type = constant_texts.data.ovd_type.lower()
        if _address_type == 'aadhaar':
            perm_address_type_index = 1
        elif _address_type == 'passport':
            perm_address_type_index = 2
        elif _address_type == 'voter':
            perm_address_type_index = 3
        elif _address_type == 'dl':
            perm_address_type_index = 4
        else:
            perm_address_type_index = 7
        poa_table_data[perm_address_type_index][1] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>' if constant_texts.data.address_permanent_value else ''
                )
        
        poa_table_data[perm_address_type_index][3]= Paragraph(f'{constant_texts.data.identity_aadhar_value}'.upper(),style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=pdf_colors.filled_data_color))
        if constant_texts.data.is_address_correspondence_same_as_permanent:
            poa_table_data[perm_address_type_index][0] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>'  if constant_texts.data.address_correspondence_value else '' 
                )
        else:
            poa_table_data[7][0] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>' if constant_texts.data.address_correspondence_value else ''
                )

        if perm_address_type_index == 2 or perm_address_type_index == 4:
            if constant_texts.data.proof_of_address_expiry_date:
                poa_table_data[perm_address_type_index][5] = Paragraph(constant_texts.data.proof_of_address_expiry_date,style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=pdf_colors.filled_data_color))

        poa_fields_table = pdf_tables.create_table(
            data=poa_table_data,
            col_widths=[(doc.width-doc.rightMargin*2)/6]*6,
            style=pdf_styles.padded_justified_table_style(right=10,top=2,bottom=2)
        )

        table = Table([[proof_of_address_section_heading],[poa_fields_table]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return table

    def _get_kyc_form_header(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        kyc_text = Paragraph(constant_texts.data.page_title, style=pdf_styles.bold_text_style(alignment=0, fontsize=9))
        small_logo = load_logo(width=1.8*inch)

        company_name = constant_texts.data.company_name
        address_text = constant_texts.data.company_address

        table = Table([[Paragraph(company_name,pdf_styles.bold_text_style(fontsize=10))],[Paragraph(text=address_text,style=pdf_styles.normal_text_style(alignment=1,fontsize=7))]])
        table.setStyle(pdf_styles.padded_table_style())
        
        header = Table([[kyc_text,table,small_logo]], colWidths=[None,doc.width/2,None])
        header.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (1, -1), 'TOP'),
            ('VALIGN', (-1, -1), (1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        left_cell_first_table = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.data.form_title,field_width=(doc.width-doc.rightMargin)*0.5,options=constant_texts.data.form_type_options,selected_options=constant_texts.data.application_type_selected_options)
        left_cell_first_table.setStyle(
            TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ])
        )
        left_cell_kyc_mode = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.data.kyc_mode,field_width=(doc.width-doc.rightMargin)*0.75,options=constant_texts.data.kyc_mode_options,selected_options=constant_texts.data.kyc_mode_selected_options)
        left_cell_bottom_table = Paragraph(constant_texts.data.kyc_instructions_text,style=pdf_styles.normal_text_style(fontsize=8))
        left_cell = Table([[left_cell_first_table],[left_cell_kyc_mode],[left_cell_bottom_table]])
        left_cell.setStyle(
            TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ])
        )

        right_cell = Table([[Paragraph(constant_texts.data.application_no_label,style=pdf_styles.bold_text_style(fontsize=8,alignment=1))],[Paragraph(constant_texts.data.application_no_value,style=pdf_styles.normal_text_style(alignment=1, fontsize=8,text_color=pdf_colors.filled_data_color))]], colWidths=[2*inch],rowHeights=[None,16])
        right_cell.setStyle(
            TableStyle([
            ('ALIGN', (0, 0), (-1,-1), 'CENTER'),
            ('GRID', (0, 1), (-1, -1), 1, colors.black)
        ])
        )

        form_instruction = Table([[left_cell,right_cell]])
        form_instruction.setStyle(pdf_styles.padded_justified_table_style())

        form_header = Table([[header],[form_instruction]])
        form_header.setStyle(pdf_styles.bordered_table_style(h_margin=5,v_margin=5))

        return form_header

    async def _get_kyc_applicant_sign_section(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        _file_id = constant_texts.data.applicant_wet_sign_value
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None

        _wetsign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''

        table = pdf_tables.create_table(data=[['',Paragraph(constant_texts.data.applicant_esign_title,style=pdf_styles.normal_text_style(alignment=1,fontsize=9)),Paragraph(constant_texts.data.applicant_wet_sign_title,style=pdf_styles.normal_text_style(alignment=1,fontsize=9))],
                                              ['',constant_texts.data.applicant_esign_value,_wetsign]],
                                              row_heights=[None,0.5*inch],style=pdf_styles.bordered_table_style(styling_list=[('LINEAFTER', (0, 0), (-1,-1), 1, colors.black),('ALIGN', (0, 0), (-1, -1),'CENTER')]),
                                              col_widths=[(doc.width-doc.rightMargin*2)/2,None,None])
        return table
    
    def _get_kyc_section3(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        contact_details = Paragraph(constant_texts.data.contact_details_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))

        telephone_office = pdf_components.get_text_field(doc,field_name=constant_texts.data.contact_tel_off_label,value=constant_texts.data.contact_tel_off_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        telephone_res = pdf_components.get_text_field(doc,field_name=constant_texts.data.contact_tel_res_label,value=constant_texts.data.contact_tel_res_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        mob_num = pdf_components.get_text_field(doc,field_name=constant_texts.data.contact_mobile_label,value=constant_texts.data.contact_mobile_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        telephones_off_and_res = pdf_tables.create_composite_table(table1=telephone_office,table2=telephone_res,col_widths=[(doc.width-doc.rightMargin*2)*0.5,10,(doc.width-doc.rightMargin*2)*0.5])
        mobile_referer = pdf_components.checkbox_field(doc,options=constant_texts.data.contact_mobile_dependent_relationship_options,selected_options=constant_texts.data.contact_mobile_dependent_relationship_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        mob_and_referrer = pdf_tables.create_composite_table(table1=mob_num,table2=mobile_referer,col_widths=[None,1,None])

        email = pdf_components.get_text_field(doc,field_name=constant_texts.data.contact_email_label,value=constant_texts.data.contact_email_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)


        email_referrer = pdf_components.checkbox_field(doc,options=constant_texts.data.contact_email_dependent_relationship_options,selected_options=constant_texts.data.contact_email_dependent_relationship_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        email_and_referrer = pdf_tables.create_composite_table(table1=email,table2=email_referrer,col_widths=[None,1,None])

        table = Table([[contact_details],[email_and_referrer],[mob_and_referrer],[telephones_off_and_res]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))

        return table
    
    def _get_kyc_section4(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        section4_heading = Paragraph(constant_texts.data.fatca_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        resident_field = pdf_components.checkbox_field(doc,options=constant_texts.data.tax_resident_options,selected_options=constant_texts.data.tax_resident_selected_options,field_name_text=constant_texts.data.tax_resident_label,field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        pob = pdf_components.get_text_field(doc,field_name=constant_texts.data.place_of_birth_label,value=constant_texts.data.place_of_birth_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        country_of_origin = pdf_components.get_text_field(doc,field_name=constant_texts.data.country_of_origin_label,value=constant_texts.data.country_of_origin_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        iso_country_code = pdf_components.get_text_field(doc,field_name=constant_texts.data.iso_3166_country_code_label,value=constant_texts.data.iso_3166_country_code_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pob_country_iso_code = Table([[pob,country_of_origin,iso_country_code]],style=pdf_styles.padded_justified_table_style())

        fatca_tin_table_data = []
        row_hts = []
        for row_index, row in enumerate(constant_texts.data.fatca_table_data):
            if row_index == 0:  # First row (header)
                fatca_tin_table_data.append([Paragraph(cell, style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
            else:  # Subsequent rows - data in upper case
                fatca_tin_table_data.append([Paragraph(f'{cell}'.upper(), style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color))for cell in row])
            row_hts.append(10 if not row[3] else None)

        fatca_tin_table = pdf_tables.create_table(data= fatca_tin_table_data,style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2,styling_list=[('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),]),col_widths=[None,None,None,None],row_heights=row_hts)

        note_1 = Paragraph(constant_texts.data.fatca_note_1,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_2 = Paragraph(constant_texts.data.fatca_note_2,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_3 = Paragraph(constant_texts.data.fatca_note_3,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_a = Paragraph(constant_texts.data.fatca_note_a,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_b = Paragraph(constant_texts.data.fatca_note_b,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_c = Paragraph(constant_texts.data.fatca_note_c,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))

        certification_table = Table([[Paragraph(constant_texts.data.certification_heading,style=pdf_styles.normal_text_style(alignment=1,fontsize=8))],[Paragraph(constant_texts.data.certification_content,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))]],
                                    style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2))
        
        table = Table([[section4_heading],[resident_field],[pob_country_iso_code],[fatca_tin_table],[note_1],[note_2],[note_3],[note_a],[note_b],[note_c],[certification_table]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return table
    
    def _get_kyc_section5_6_7(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        gross_annual_income = pdf_components.checkbox_field(doc,options=constant_texts.data.gross_income_range_options,selected_options=constant_texts.data.gross_income_selected_options,field_name_text=constant_texts.data.gross_annual_income_label,field_width=(doc.width-doc.rightMargin*2)*0.75,size=8)
        gross_income_date = pdf_components.get_text_field(doc,field_name=constant_texts.data.gross_income_date_label,value=constant_texts.data.gross_income_date_value,width=(doc.width-doc.rightMargin*2)*0.25,size=8)
        gross_income_and_date = pdf_tables.create_composite_table(table1=gross_annual_income,table2=gross_income_date,col_widths=[(doc.width-doc.rightMargin*2)*0.75,1,(doc.width-doc.rightMargin*2)*0.25])
        networth = pdf_components.get_text_field(doc,field_name=constant_texts.data.gross_networth_label,value=constant_texts.data.gross_networth_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        networth_date = pdf_components.get_text_field(doc,field_name=constant_texts.data.gross_networth_date_label,value=constant_texts.data.gross_networth_date_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        networth_and_date = pdf_tables.create_composite_table(table1=networth,table2=networth_date,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])

        occupation = pdf_components.checkbox_field(doc,options=constant_texts.data.occupation_options,selected_options=constant_texts.data.occupation_selected_options,field_name_text=constant_texts.data.occupation_label,field_width=(doc.width-doc.rightMargin*2),size=8)
        pep = pdf_components.checkbox_field(doc,options=constant_texts.data.pep_options,selected_options=constant_texts.data.pep_selected_options,field_name_text=constant_texts.data.pep_label,field_width=(doc.width-doc.rightMargin*2),size=8)
        
        table = Table([[gross_income_and_date],[networth_and_date],[occupation],[pep]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))

        return table
    
    async def _get_kyc_section8(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        section8_heading = Paragraph(constant_texts.data.applicant_declaration_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        section4_declaration = Paragraph(constant_texts.data.applicant_declaration_content, style=pdf_styles.normal_text_style(fontsize=8,alignment=0))
        date = pdf_components.get_text_field(doc,field_name=constant_texts.data.declaration_date_label,value=self.date_of_form_submission,width=(doc.width-doc.rightMargin*2)*0.3,size=8)
        place = pdf_components.get_text_field(doc,field_name=constant_texts.data.declaration_place_label,value=constant_texts.data.declaration_place_value,width=(doc.width-doc.rightMargin*2)*0.3,size=8)
        date_place = pdf_tables.create_composite_table(table1=date,table2=place,col_widths=[(doc.width-doc.rightMargin*2)*0.3,1,(doc.width-doc.rightMargin*2)*0.3])

        _file_id = constant_texts.data.applicant_wet_sign_value
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None

        _wetsign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=1*inch) if _wetsign_bytes else ''

        table = Table([[section8_heading,Paragraph(constant_texts.data.applicant_esign_label,style=pdf_styles.normal_text_style(alignment=1,fontsize=8)),Paragraph(constant_texts.data.applicant_wet_sign_label,style=pdf_styles.normal_text_style(alignment=1,fontsize=8))],
                       [Table([[section4_declaration],[date_place]]),'',_wetsign]
                       ])
        
        table.setStyle(pdf_styles.bordered_table_style(h_margin=2,v_margin=2,styling_list=[('GRID', (1, 0), (-1, 1), 1, colors.black),('VALIGN',(1, 0),(-1,1),'MIDDLE'),('ALIGN',(1, 0),(-1,1),'CENTER'),]))
        return table

    def _get_kyc_verification_details_section(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        section_heading = Paragraph(constant_texts.data.kyc_verification_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=1))
        date = pdf_components.get_text_field(doc,field_name=constant_texts.data.ipv_carried_out_on_date_label,value=constant_texts.data.ipv_carried_out_on_date_value,width=(doc.width-doc.rightMargin*2)*0.75/2,size=8)
        place = pdf_components.get_text_field(doc,field_name=constant_texts.data.ipv_place_label,value=constant_texts.data.ipv_place_value,width=(doc.width-doc.rightMargin*2)*0.75/2,size=8)
        date_place = pdf_tables.create_composite_table(table1=date,table2=place,col_widths=[(doc.width-doc.rightMargin*2)*0.75/2,1,(doc.width-doc.rightMargin*2)*0.75/2])
        
        name = pdf_components.get_text_field(doc,field_name=constant_texts.data.official_name_label,value=constant_texts.data.official_name_value,width=(doc.width-doc.rightMargin*2)*0.75,size=8)
        designation = pdf_components.get_text_field(doc,field_name=constant_texts.data.official_designation_label,value=constant_texts.data.official_designation_value,width=(doc.width-doc.rightMargin*2)*0.55,size=8)
        employee_code = pdf_components.get_text_field(doc,field_name=constant_texts.data.employee_ap_code_label,value=constant_texts.data.employee_ap_code_value,width=(doc.width-doc.rightMargin*2)*0.2,size=8)
        designation_emp_code = pdf_tables.create_composite_table(table1=designation,table2=employee_code,col_widths=[(doc.width-doc.rightMargin*2)*0.55,1,(doc.width-doc.rightMargin*2)*0.2])
        document_recieved_field = pdf_components.checkbox_field(doc,options=constant_texts.data.documents_received_options,selected_options=constant_texts.data.documents_received_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.75,size=8)

        signature = pdf_components.boxed_sign_field(doc=doc,display_name=constant_texts.data.signature_branch_ap_seal_label,alignment=1,fontsize=8,alpha=0.5,box_width=(doc.width-doc.rightMargin*2)*0.25,box_height=0.6*inch)

        left_table = Table([[section_heading],[date_place],[name],[designation_emp_code],[document_recieved_field]],style=pdf_styles.padded_table_style())
        table = Table([[left_table,signature]])
        table.setStyle(pdf_styles.bordered_table_style(h_margin=2,v_margin=2))
        return table

    # def get_aadhaar_xml_pages(self, doc):
    #     constant_texts = self.constant_texts
    #     pdf_styles = PdfStyles()

    #     # Todo: Either handle the <Ldata> tag(data in local lang) with specific font, or remove it from xml itself.
    #     formatted_xml = format_xml(constant_texts.data.aadhaar_xml)

    #     # Extract XML data and split into chunks
    #     xml_chunks = list(split_into_chunks(escape(formatted_xml), lines_per_chunk=1))
    #     # Create the header row and the initial table structure
    #     table_data = [[
    #         Paragraph(f'Digilocker Aadhaar XML for {constant_texts.data.identity_aadhar_value}',
    #                 style=pdf_styles.bold_text_style(alignment=1, fontsize=9)),

    #     ]]

    #     # Create additional rows for the XML chunks
    #     for chunk in xml_chunks:
    #         table_data.append([Paragraph(f'<pre>{chunk}</pre>', style=pdf_styles.normal_text_style(alignment=0, fontsize=8))])

    #     table = Table(table_data)

    #     # Apply styles: Grid only for the first cell in the first row
    #     table.setStyle(pdf_styles.bordered_table_style(h_margin=2, v_margin=0, styling_list=[
    #         ('TOPPADDING', (0, 0), (0, 0), 4),
    #         ('TOPPADDING', (-1, -1), (-1, -1), 4),
    #         ('BOTTOMPADDING', (0, 0), (0, 0), 4),
    #         ('GRID', (0, 0), (1, 0), 1, colors.black),  # Grid for the first cell only
    #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),     # Vertical alignment for all cells
    #     ]))

    #     return table

    def get_aadhaar_xml_pages(self, doc):
        constant_texts = self.constant_texts.data
        pdf_styles = PdfStyles()
        pdf_components = PdfComponents()
        pdf_tables = PdfTables()

        aadhaar_data = extract_aadhaar_data(xml_data=constant_texts.aadhaar_xml)
        if not aadhaar_data:
            return None
        # Create the header row and the initial table structure
        table_header = Paragraph(f'Aadhaar data as in Digilocker for {constant_texts.identity_aadhar_value}', 
                    style=pdf_styles.bold_text_style(alignment=1, fontsize=9)),
            
        photo_box_width = 1.5*inch

        name_field = pdf_components.get_text_field(doc=doc,field_name='Name:', value=aadhaar_data.name, width=(doc.width - doc.leftMargin*2)*3/4, size=8)
        dob_field = pdf_components.get_text_field(doc=doc,field_name='Date of Birth:', value=aadhaar_data.dob, width=(doc.width - doc.leftMargin*2)*3/4, size=8)
        gender_field = pdf_components.get_text_field(doc=doc,field_name='Gender:', value=aadhaar_data.gender, width=(doc.width - doc.leftMargin*2)*3/4, size=8)
        co_field = pdf_components.get_text_field(doc=doc,field_name='Care of(co):', value=aadhaar_data.co, width=(doc.width - doc.leftMargin*2)*3/4, size=8)
        address_field_title = Paragraph('Address:', style=pdf_styles.normal_text_style(fontsize=8))
        address_field = pdf_components.get_multiline_text(doc=doc, lines=2,text=aadhaar_data.address,width=(doc.width - doc.leftMargin*2)*3/4)

        left = Table([[name_field],[dob_field],[gender_field],[co_field],[address_field_title],[address_field]])
        left.setStyle(pdf_styles.padded_table_style(top=1))

        photo_box = pdf_components.create_bordered_input_box(doc,image_bytes=aadhaar_data.photo,text_value='Aadhaar Photo N/A',text_style=pdf_styles.normal_text_style(alignment=1,fontsize=9),width=photo_box_width-10,height=photo_box_width,text_size=8)
        right = pdf_tables.create_table(data=[[photo_box]],style=pdf_styles.padded_table_style(top=2,bottom=2, left=10),col_widths=[(doc.width - doc.leftMargin*2)/4])

        # bottom = Table([[address_field]],style=pdf_styles.padded_table_style(top=4))

        # table = Table([[table_header,''],[left,right],[bottom,'']],style=pdf_styles.bordered_table_style(h_margin=5,v_margin=5))
        table = Table([[table_header,''],[left,right]])

        # Apply styles: Grid only for the first cell in the first row
        table.setStyle(pdf_styles.bordered_table_style(h_margin=5, v_margin=5, styling_list=[
            ('TOPPADDING', (0, 0), (0, 0), 4),
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 2), (-1, 2)),
            ('TOPPADDING', (-1, -1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('GRID', (0, 0), (1, 0), 1, colors.black),  # Grid for the first cell only
        ]))

        return table