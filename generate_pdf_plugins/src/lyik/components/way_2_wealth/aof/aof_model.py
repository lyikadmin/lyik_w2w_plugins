from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Paragraph, PageBreak, Spacer, TableStyle, Table
from ...components import PdfTables
from ...components import PdfStyles
from ...images import load_logo
from ...text import get_text
from reportlab.lib.units import inch
from reportlab.lib.colors import CMYKColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from ...way_2_wealth.aof.aof_text_consts import AOFConstantTexts
from ...components import PdfComponents, HorizontalLine
from ...colors import PdfColors
from ....models.digi_aadhaar_data import Aadhaar, extract_aadhaar_data
from ....models.geocode_location import GeocodeLocation
from ....pdf_utilities.utility import format_xml, split_into_chunks, format_date
from html import escape
from pydantic import BaseModel
import xml.etree.ElementTree as ET
class AOF:
    def __init__(self,data:dict=None) -> None:
        self.constant_texts = AOFConstantTexts(json_data=data)
        self.date_of_form_submission = format_date(date_str=data.get('submitter',{}).get('time',''))
    def get_page1(self,doc):

        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        style1 = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table1 = pdf_tables.create_table(data=constant_texts.page1_table1_data,style=style1,col_widths=[1.2 * inch, 2 * inch],row_heights=[0.4 * inch] * 4)

        style2 = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'LatoBold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (1, 1), (-1, 1)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table2 = pdf_tables.create_table(data=constant_texts.page1_table2_data,style=style2,col_widths=[1 * inch] + [0.3 * inch] * 8,row_heights=[0.8 * inch, 0.4 * inch, 0.4 * inch])
        composite_table = pdf_tables.create_composite_table(table1, table2,col_widths=[3.2 * inch, 10, 3.4 * inch])

        w2w_logo = load_logo()
        ktk_logo = pdf_components.load_local_image(wt=3*inch,image_dir='lyik.components.way_2_wealth.aof.images',file_name='ktk.png') if constant_texts.page1_is_ktk else ''
        logos = pdf_tables.create_table(
            data=[[ktk_logo,w2w_logo]], col_widths=[None, None], style=pdf_styles.padded_table_style()
        )

        info_paras = Table([[get_text(text=constant_texts.page1_box_left_text,text_style=pdf_styles.get_preformatted_style()),get_text(constant_texts.page1_box_right_text,text_style=pdf_styles.get_preformatted_style())]],colWidths=[3.5 * inch, 3.5 * inch])
        info_paras.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        ktk_w2w_banner = pdf_components.load_local_image(wt=doc.width,image_dir='lyik.components.way_2_wealth.aof.images',file_name='ktk_w2w_banner.png') if constant_texts.page1_is_ktk else None

        return [
            composite_table,
            Spacer(1, 0.7 * inch), logos,
            Spacer(1, 0.4 * inch), get_text(text=constant_texts.page1_form_title,text_style=pdf_styles.bold_text_style(fontsize=20,text_color=colors.darkblue,leading=30)),
            Spacer(1, 0.4 * inch), get_text(text=constant_texts.page1_company_title,text_style=pdf_styles.bold_text_style(fontsize=17,alignment=1)),
            Spacer(1, 0.1 * inch), get_text(text=constant_texts.page1_address_text,text_style=pdf_styles.normal_text_style(fontsize=10, alignment=1)),
            Spacer(1, 0.01 * inch), get_text(text = constant_texts.page1_company_website,text_style=pdf_styles.normal_text_style(fontsize=10,alignment=1)),
            Spacer(1,0.2*inch), info_paras,
            Spacer(1,0.2*inch if ktk_w2w_banner else 1), ktk_w2w_banner if ktk_w2w_banner else Spacer(1,1),
            Spacer(1, 0.1 * inch), pdf_components.create_bordered_input_box(doc=doc,text_value=constant_texts.page1_bottom_text,height=0.8*inch,width=doc.width-doc.rightMargin,text_size=11,text_style=pdf_styles.normal_text_style(alignment=4,fontsize=9,indent=5)),
            Spacer(1, 0.2 * inch), PageBreak()
        ]

    def get_page2(self,doc):
        constant_texts = self.constant_texts #ConstantTexts()
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        # Nested content for the second row
        page2_first_headered_table_body = []

        nested_table1 = Table(constant_texts.page2_nested_table_data, colWidths=[(doc.width-1.8* inch)/2,1.5 * inch, (doc.width-1.8* inch)/2])
        nested_table1.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING', (1, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (1, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        page2_first_headered_table_body.append(nested_table1)
        page2_first_headered_table_body.append(Paragraph(constant_texts.page2_branch_manager_heading,style=pdf_styles.normal_text_style(fontsize=9)))

        date_text_field = pdf_components.get_text_field(doc=doc,field_name='Date:',size=9,width=(doc.width - doc.leftMargin)/2,value=constant_texts.page2_table1_date_value)
        place_text_field = pdf_components.get_text_field(doc=doc,field_name='Place:',size=9,width= (doc.width - doc.rightMargin)/2,value=constant_texts.page2_table1_place_value)
        name_text_field = pdf_components.get_text_field(doc=doc,field_name='Name:',size=9,width= (doc.width - doc.rightMargin),value=constant_texts.page2_table1_name_value)
        designation_text_field = pdf_components.get_text_field(doc=doc,field_name='Designation:',size=9,width= (doc.width - doc.rightMargin),value=constant_texts.page2_table1_designation_value)
        contact_num_text_field = pdf_components.get_text_field(doc=doc,field_name='Contact No:',size=9,width= (doc.width - doc.rightMargin),value=constant_texts.page2_table1_contact_no_value)
        employee_code_text_field = pdf_components.get_text_field(doc=doc,field_name='Employee Code/ AP Code:',size=9,width= (doc.width - doc.rightMargin),value=constant_texts.page2_table1_employee_code_value)

        page2_first_headered_table_body.append(pdf_tables.create_composite_table(table1=date_text_field,table2=place_text_field,col_widths=[None,0.1,None]))
        page2_first_headered_table_body.append(name_text_field)
        page2_first_headered_table_body.append(designation_text_field)
        page2_first_headered_table_body.append(contact_num_text_field)
        page2_first_headered_table_body.append(employee_code_text_field)

        page2_first_headered_table_body_table = Table([[item] for item in page2_first_headered_table_body], colWidths=[doc.width])
        page2_first_headered_table_body_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the inner table
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0.2 * inch),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.2 * inch),  
        ]))

        page2_first_headered_table = pdf_tables.create_headered_table(header_text=constant_texts.page2_table1_header,header_color=CMYKColor(0, 0.0590, 0.1180, 0.0235),table_body=page2_first_headered_table_body_table)

        page2_second_headered_table_body = []
        page2_second_headered_table_body.append(Paragraph(constant_texts.page2_table2_heading,style=pdf_styles.normal_text_style(fontsize=9)))

        ipv_date_text_field = pdf_components.get_text_field(doc=doc,field_name='IPV Date:',size=9,width=(doc.width - doc.leftMargin)/3,value=constant_texts.page2_table2_ipv_date)
        mobile_num_text_field = pdf_components.get_text_field(doc=doc,field_name='Mobile No.:',size=9,width= (doc.width - doc.rightMargin)/3,value=constant_texts.page2_table2_mobile_no)
        name2_text_field = pdf_components.get_text_field(doc=doc,field_name='Name:',size=9,width= (doc.width - doc.rightMargin)*2/3,value=constant_texts.page2_table2_name)
        designation2_text_field = pdf_components.get_text_field(doc=doc,field_name='Designation:',size=9,width= (doc.width - doc.rightMargin)*2/3,value=constant_texts.page2_table2_designation)
        employee_subbroker_code_text_field = pdf_components.get_text_field(doc=doc,field_name='Employee Code/AP/Sub-Broker Code:',size=9,width= (doc.width - doc.rightMargin)*2/3)
        signature = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page2_table2_signature_heading,size=9,width=(doc.width - doc.rightMargin)*2/3)
        page2_second_headered_table_body.append(name2_text_field)
        page2_second_headered_table_body.append(designation2_text_field)
        page2_second_headered_table_body.append(employee_subbroker_code_text_field)
        page2_second_headered_table_body.append(pdf_tables.create_composite_table(table1=ipv_date_text_field,table2=mobile_num_text_field,col_widths=[None,0.1,(doc.width - doc.rightMargin)*75/2]))
        page2_second_headered_table_body.append(Spacer(0,20))
        page2_second_headered_table_body.append(signature)

        right_nested_table = Table([[Paragraph(constant_texts.page2_table2_image_header,pdf_styles.normal_text_style(fontsize=7))],[pdf_components.create_bordered_input_box(doc,width=(doc.width - doc.rightMargin)*0.25,height=120)]])
        # Define column widths for 8:3 ratio
        column_widths = [doc.width*2/3-10,10, doc.width/3]


        page2_second_headered_table_body_table = Table([[item] for item in page2_second_headered_table_body], colWidths=[doc.width*2/3],rowHeights=[20]*7)
        page2_second_headered_table_body_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Center the inner table
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),

        ]))
        middle_composite_table = pdf_tables.create_composite_table(table1=page2_second_headered_table_body_table,table2=right_nested_table,col_widths=column_widths)
        
        # Prepare 3rd row

        page2_second_full_body_table = Table([[middle_composite_table],[HorizontalLine(width=500, thickness=1, color=colors.black, alignment='left',margin=0)],[Paragraph(constant_texts.page2_tabel2_undertaking_text,pdf_styles.normal_text_style(alignment=4,fontsize=9))],[Spacer(1,15)],[Paragraph(constant_texts.page2_table2_sign_pretext)]])

        page2_second_headered_table = pdf_tables.create_headered_table(header_text=constant_texts.page2_table2_header,header_color=CMYKColor(0, 0.0590, 0.1180, 0.0235),table_body=page2_second_full_body_table)


        page2_second_headered_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the inner table
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0.2 * inch),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.2 * inch),
        ]))

        # page2_bottom_heading = pdf_components.create_bordered_input_box(doc=doc,width=doc.width,text='For office use only (Head Office)',text_size=12,text_style=pdf_styles.get_bold_text(),box_color=colors.lightgrey)
        # code_alloted = Table([['','','','','','','','','','','']],rowHeights=25, colWidths=25)
        # code_alloted.setStyle(TableStyle([
        #     ('GRID', (0, 0), (-1, -1), 1, colors.black),
        #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # ]))

        # code_alloted_section = pdf_tables.create_composite_table(table1=Table([[Paragraph('CODE ALOTTED', style=pdf_styles.get_bold_text())]]),table2=code_alloted, col_widths=[2 * inch, 1, None])

        # date_string = "19/10/1999"
        # bottom_content = Table([[pdf_components.get_date_field(date=date_string,display_name='Date:',font_size=9),Paragraph("Signature of the Authorised Signatory", style=pdf_styles.normal_text_style(fontsize=9)), Spacer(1*inch,1)]], colWidths=[None, 2.5*inch, 1*inch])
        # bottom_content.setStyle(pdf_styles.padded_justified_table_style())

        return [page2_first_headered_table, Spacer(1,0.1*inch),Spacer(2, 0.3 * inch),page2_second_headered_table,Spacer(1, 0.6 * inch),PageBreak()]


    # def get_aadhaar_xml_pages(self, doc, index):
    #     constant_texts = self.constant_texts.page_kyc_details[index]
    #     pdf_styles = PdfStyles()
        
    #     formatted_xml = format_xml(constant_texts.aadhaar_xml)
        
    #     # Extract XML data and split into chunks
    #     xml_chunks = list(split_into_chunks(escape(formatted_xml), lines_per_chunk=1))
    #     # Create the header row and the initial table structure
    #     table_data = [[
    #         Paragraph(f'Digilocker Aadhaar XML for {constant_texts.identity_aadhar_value}', 
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
    
    def get_aadhaar_xml_pages(self, doc, index):
        constant_texts = self.constant_texts.page_kyc_details[index]
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

        # bottom = Table([[address_field_title],[address_field]],style=pdf_styles.padded_table_style(top=4))

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


    async def get_kyc_pages(self,doc,index):
        pdf_components = PdfComponents()
        pdf_styles = PdfStyles()
        form_header = self._get_kyc_form_header(doc=doc,index=index)
        section1 = await self._get_kyc_section1(doc=doc,index=index)
        section2A = self._get_kyc_section2A(doc=doc,index=index)
        section2B = self._get_kyc_section2B(doc=doc,index=index)
        section_proof_of_address = self._get_proof_of_address(doc=doc,index=index)
        applicants_sign_section = await self._get_kyc_applicant_sign_section(doc=doc,index=index)
        section3 = self._get_kyc_section3(doc=doc,index=index)
        section4 = self._get_kyc_section4(doc=doc,index=index)
        section5_6_7 = self._get_kyc_section5_6_7(doc=doc,index=index)
        section8 = await self._get_kyc_section8(doc=doc,index=index)
        kyc_bottom_section = self._get_kyc_verification_details_section(doc=doc,index=index)

        # Geo Location data
        constant_texts = self.constant_texts.page_kyc_details[index]
        geoloc_table = None
        if constant_texts.geocode_location and isinstance(constant_texts.geocode_location,GeocodeLocation):
            geoloc_details = pdf_components.create_bordered_input_box(doc=doc,text_value=f'Liveness taken at ({constant_texts.geocode_location.longitude}, {constant_texts.geocode_location.latitude}): {constant_texts.geocode_location.formatted_address}',height=0.6*inch,width=doc.width-doc.rightMargin,text_size=11,text_style=pdf_styles.normal_text_style(alignment=4,fontsize=9,indent=5)),
            geoloc_table = PdfTables().create_table(data=[[geoloc_details]],col_widths=[None],style=pdf_styles.padded_table_style())

        return [form_header,section1,section2A,section2B,section_proof_of_address,applicants_sign_section,PageBreak(),section3,section4,section5_6_7,section8,kyc_bottom_section, Spacer(1, 0.1 * inch), geoloc_table if geoloc_table else Spacer(1, 1) ,PageBreak()]
        
    async def _get_kyc_section1(self,doc:BaseDocTemplate,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        identity_details_heading = Paragraph(constant_texts.identity_details_title, style=pdf_styles.bold_text_style(alignment=0,fontsize=8))
        pan_help_text = Paragraph(constant_texts.pan_help_text, style=pdf_styles.normal_text_style(fontsize=8))
        photo_box_width = 1.5*inch
        pan = pdf_components.get_text_field(doc,field_name=constant_texts.identity_pan_label,value=constant_texts.identity_pan_value,width=(doc.width-doc.leftMargin*2-photo_box_width)/2,size=8)
        pan_field_with_help_text = pdf_tables.create_composite_table(table1=pan,table2=pan_help_text,col_widths=[(doc.width-doc.leftMargin*2-photo_box_width)/2,1,None])
        name = pdf_components.get_text_field(doc,field_name=constant_texts.identity_name_label,size=8,value=constant_texts.identity_name_value,width=doc.width- doc.rightMargin*2-photo_box_width )
        maiden_name = pdf_components.get_text_field(doc,field_name=constant_texts.identity_maiden_name_label,size=8,value=constant_texts.identity_maiden_name_value,width=doc.width- doc.leftMargin*2-photo_box_width )
        
        father_spouse_name = pdf_components.get_text_field(doc,field_name=constant_texts.identity_father_spouse_name_label,value=constant_texts.identity_father_spouse_name_value,width=doc.width-photo_box_width- doc.leftMargin*2,size=8)
        mother_name = pdf_components.get_text_field(doc,field_name=constant_texts.identity_mother_name_label,value=constant_texts.identity_mother_name_value,width=doc.width-photo_box_width- doc.leftMargin*2,size=8)


        gender = pdf_components.checkbox_field(doc,options=constant_texts.identity_gender_options,field_name_text=constant_texts.identity_gender_label,selected_options=constant_texts.identity_gender_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*0.5,size=8)
        marital_status = pdf_components.checkbox_field(doc,options=constant_texts.identity_marital_status_options,field_name_text=constant_texts.identity_marital_status_label,selected_options=constant_texts.identity_marital_status_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*0.5,size=8)

        gender_marital_status = pdf_tables.create_composite_table(table1=gender,table2=marital_status,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*0.5,1,(doc.width-photo_box_width- doc.leftMargin*2)*0.5])

        nationality = pdf_components.checkbox_field(doc,options=constant_texts.identity_nationality_options,field_name_text=constant_texts.identity_nationality_label,selected_options=constant_texts.identity_nationality_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*2/3,size=8)
        country_iso_code = pdf_components.get_text_field(doc=doc,field_name=constant_texts.identity_iso_country_code_label,value=constant_texts.identity_iso_country_code_value,width=(doc.width-photo_box_width- doc.leftMargin*2)/3,size=8)
        nationality_country_code_composite = pdf_tables.create_composite_table(table1=nationality,table2=country_iso_code,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*2/3,1,(doc.width-photo_box_width- doc.leftMargin*2)/3])

        residential_status = pdf_components.checkbox_field(doc,options=constant_texts.identity_residential_status_options,field_name_text=constant_texts.identity_residential_status_label,selected_options=constant_texts.identity_residential_status_selected_options,field_width=(doc.width-photo_box_width- doc.leftMargin*2)*2/3,size=8)
        residential_help_text = Paragraph(constant_texts.identity_residential_status_help_text, style=pdf_styles.normal_text_style(fontsize=8))
        residential_full_field = pdf_tables.create_composite_table(table1=residential_status,table2=residential_help_text,col_widths=[(doc.width-photo_box_width- doc.leftMargin*2)*2/3,1,None])

        aadhaar = pdf_components.get_text_field(doc,field_name=constant_texts.identity_aadhar_label,value=constant_texts.identity_aadhar_value if constant_texts.is_digilocker else '',width=(doc.width-doc.leftMargin*2-photo_box_width)/2-10,size=8)
        dob = pdf_components.get_text_field(doc,field_name=constant_texts.identity_date_of_birth_label,value=constant_texts.identity_date_of_birth_value,width=(doc.width-photo_box_width- doc.leftMargin*2)/2,size=8)

        aadhar_dob = pdf_tables.create_composite_table(table1=aadhaar,table2=dob,col_widths=[(doc.width-doc.leftMargin*2-photo_box_width)/2,1,(doc.width-doc.leftMargin*2-photo_box_width)/2])
        # poi_field = pdf_components.get_text_field(doc,field_name=constant_texts.identity_poi_label,value=constant_texts.identity_poi_value,width=(doc.width-doc.leftMargin*2-photo_box_width),size=8)


        left = Table([[identity_details_heading],[pan_field_with_help_text],[name],[maiden_name],[father_spouse_name],[mother_name],[gender_marital_status], [nationality_country_code_composite],[residential_full_field],[aadhar_dob]])
        left.setStyle(pdf_styles.padded_table_style(top=1))

        _file_id =constant_texts.identity_passport_size_photo
        image_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        photo_box = pdf_components.create_bordered_input_box(doc,image_bytes=image_bytes,text_value=constant_texts.identity_passport_size_alt_text,text_style=pdf_styles.normal_text_style(alignment=1,fontsize=9),width=photo_box_width-10,height=photo_box_width,text_size=8)
        right = Table([[photo_box],[Paragraph(constant_texts.identity_passport_size_help_text,style=pdf_styles.bold_text_style(alignment=1,fontsize=7))]],style=pdf_styles.padded_table_style())
        # sectionA = pdf_tables.create_composite_table(table1=left,table2=right,col_widths=[(doc.width-doc.leftMargin-photo_box_width),1,photo_box_width])
        sectionA = Table([[left,right]],style=pdf_styles.bordered_table_style(h_margin=5,v_margin=5))
        # sectionA.setStyle(pdf_styles.bordered_table_style(h_margin=5,v_margin=5))

        return sectionA

    
    def _get_kyc_section2A(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        
        address_details_title = Paragraph(constant_texts.address_details_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        correspondence_address_field_title = Paragraph(constant_texts.address_correspondence_title,style=pdf_styles.bold_text_style(alignment=0,fontsize=8))
        address_lines = pdf_components.get_multiline_text(doc,width=doc.width - doc.leftMargin*2,lines=2,text=constant_texts.address_correspondence_value)
        city = pdf_components.get_text_field(doc,field_name=constant_texts.address_city_label,value=constant_texts.address_city_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pincode = pdf_components.get_text_field(doc,field_name=constant_texts.address_pincode_label,value=constant_texts.address_pincode_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        district = pdf_components.get_text_field(doc,field_name=constant_texts.address_district_label,value=constant_texts.address_district_value,width=(doc.width-doc.rightMargin*2)/3,size=8)

        city_district_pincode = Table([[city,district,pincode]],style=pdf_styles.padded_justified_table_style())

        state = pdf_components.get_text_field(doc,field_name=constant_texts.address_state_label,value=constant_texts.address_state_value,width=(doc.width-doc.rightMargin)*2/3-10,size=8)
        country = pdf_components.get_text_field(doc,field_name=constant_texts.address_country_label,value=constant_texts.address_country_value,width=(doc.width-doc.rightMargin)/3-10,size=8)
        state_country = pdf_tables.create_composite_table(table1=state,table2=country,col_widths=[(doc.width-doc.rightMargin-10)*2/3,1,(doc.width-doc.rightMargin-10)/3])
        address_type = pdf_components.checkbox_field(doc,options=constant_texts.address_type_options,field_name_text=constant_texts.address_type_label,selected_options=constant_texts.address_type_selected_options,field_width=doc.width - doc.rightMargin*2,size=8)

        
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

    def _get_kyc_section2B(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        permanent_address_details_title = Paragraph(constant_texts.address_permanent_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        address_lines = pdf_components.get_multiline_text(doc,width=doc.width - doc.leftMargin*2,lines=2,text=constant_texts.address_permanent_value)
        city = pdf_components.get_text_field(doc,field_name=constant_texts.address_permanent_city_label,value=constant_texts.address_permanent_city_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pincode = pdf_components.get_text_field(doc,field_name=constant_texts.address_permanent_pincode_label,value=constant_texts.address_permanent_pincode_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        district = pdf_components.get_text_field(doc,field_name=constant_texts.address_permanent_district_label,value=constant_texts.address_permanent_district_value,width=(doc.width-doc.rightMargin*2)/3,size=8)

        city_district_pincode = Table([[city,district,pincode]],style=pdf_styles.padded_justified_table_style())

        state = pdf_components.get_text_field(doc,field_name=constant_texts.address_permanent_state_label,value=constant_texts.address_permanent_state_value,width=(doc.width-doc.rightMargin)*2/3-10,size=8)
        country = pdf_components.get_text_field(doc,field_name=constant_texts.address_permanent_country_label,value=constant_texts.address_permanent_country_value,width=(doc.width-doc.rightMargin)/3-10,size=8)
        state_country = pdf_tables.create_composite_table(table1=state,table2=country,col_widths=[(doc.width-doc.rightMargin-10)*2/3,1,(doc.width-doc.rightMargin-10)/3])
        address_type = pdf_components.checkbox_field(doc,options=constant_texts.address_permanent_type_options,field_name_text=constant_texts.address_permanent_type_label,selected_options=constant_texts.address_permanent_type_selected_options,field_width=doc.width - doc.rightMargin*2,size=8)

        section2B = Table([[permanent_address_details_title],[address_lines],[city_district_pincode],[state_country],[address_type]])
        section2B.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return section2B
    
    def _get_proof_of_address(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()
        proof_of_address_section_title = Paragraph(constant_texts.proof_of_address_label, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        proof_of_address_section_title_help_text = Paragraph(constant_texts.proof_of_address_label_help_text, style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        proof_of_address_section_heading = pdf_tables.create_table(data=[[proof_of_address_section_title,Spacer(10,0),proof_of_address_section_title_help_text]],
                                                                   col_widths=[1.5*inch,10,None],style=pdf_styles.padded_table_style())
        poa_table_data = [[Paragraph(cell, style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=colors.black)) for cell in row] for row in constant_texts.proof_of_address_table_data]
        
        
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
        _address_type = constant_texts.ovd_type.lower()
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
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>' if constant_texts.address_permanent_value else ''
                )
        
        poa_table_data[perm_address_type_index][3]= Paragraph(f'{constant_texts.identity_aadhar_value}'.upper(),style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=pdf_colors.filled_data_color))
        if constant_texts.is_address_correspondence_same_as_permanent:
            poa_table_data[perm_address_type_index][0] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>'  if constant_texts.address_correspondence_value else '' 
                )
        else:
            _corr_address_type = constant_texts.address_ovd_corr_type.lower()
            corr_address_type_index = 0
            if _corr_address_type == 'aadhaar':
                corr_address_type_index = 1
            elif _corr_address_type == 'passport':
                corr_address_type_index = 2
            elif _corr_address_type == 'voter':
                corr_address_type_index = 3
            elif _corr_address_type == 'dl':
                corr_address_type_index = 4
            else:
                corr_address_type_index = 7
            poa_table_data[corr_address_type_index][0] = pdf_components.create_bordered_input_box(
                doc, width=9, height=9, 
                text_value=f'<font name="ZapfDingbats" color={pdf_colors.filled_data_color}>✓</font>' if constant_texts.address_correspondence_value else ''
                )
            
        if perm_address_type_index == 2 or perm_address_type_index == 4:
            if constant_texts.proof_of_address_expiry_date:
                poa_table_data[perm_address_type_index][5] = Paragraph(constant_texts.proof_of_address_expiry_date,style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=pdf_colors.filled_data_color))
        
        if corr_address_type_index == 2 or corr_address_type_index == 4:
            if constant_texts.address_corr_expiry_date:
                poa_table_data[corr_address_type_index][5] = Paragraph(constant_texts.address_corr_expiry_date,style=pdf_styles.normal_text_style(alignment=0,fontsize=8,text_color=pdf_colors.filled_data_color))

        
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

    def _get_kyc_form_header(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_components = PdfComponents()

        kyc_text = Paragraph(constant_texts.page_title, style=pdf_styles.bold_text_style(alignment=0, fontsize=9))
        small_logo = load_logo(width=1.8*inch)

        company_name = constant_texts.company_name
        address_text = constant_texts.company_address

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

        left_cell_first_table = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.form_title,field_width=(doc.width-doc.rightMargin)*0.5,options=constant_texts.form_type_options,selected_options=constant_texts.application_type_selected_options)
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
        left_cell_kyc_mode = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.kyc_mode,field_width=(doc.width-doc.rightMargin)*0.75,options=constant_texts.kyc_mode_options,selected_options=constant_texts.kyc_mode_selected_options)
        left_cell_bottom_table = Paragraph(constant_texts.kyc_instructions_text,style=pdf_styles.normal_text_style(fontsize=8))
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
        right_cell = Table([[Paragraph(constant_texts.application_no_label,style=pdf_styles.bold_text_style(fontsize=8,alignment=1))],[Paragraph(f'{constant_texts.application_no_value}',style=pdf_styles.normal_text_style(fontsize=8,alignment=1,text_color=PdfColors().filled_data_color))]], colWidths=[2*inch],rowHeights=[None,16])
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

    async def _get_kyc_applicant_sign_section(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        _file_id = constant_texts.applicant_wet_sign_value
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None

        _wetsign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''

        table = pdf_tables.create_table(data=[['',Paragraph(constant_texts.applicant_esign_title,style=pdf_styles.normal_text_style(alignment=1,fontsize=9)),Paragraph(constant_texts.applicant_wet_sign_title,style=pdf_styles.normal_text_style(alignment=1,fontsize=9))],
                                              ['',constant_texts.applicant_esign_value,_wetsign]],
                                              row_heights=[None,0.5*inch],style=pdf_styles.bordered_table_style(styling_list=[('LINEAFTER', (0, 0), (-1,-1), 1, colors.black),('ALIGN', (0, 0), (-1, -1),'CENTER')]),
                                              col_widths=[(doc.width-doc.rightMargin*2)/2,None,None])
        return table
    
    def _get_kyc_section3(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        contact_details = Paragraph(constant_texts.contact_details_title, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))

        telephone_office = pdf_components.get_text_field(doc,field_name=constant_texts.contact_tel_off_label,value=constant_texts.contact_tel_off_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        telephone_res = pdf_components.get_text_field(doc,field_name=constant_texts.contact_tel_res_label,value=constant_texts.contact_tel_res_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        mob_num = pdf_components.get_text_field(doc,field_name=constant_texts.contact_mobile_label,value=constant_texts.contact_mobile_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        telephones_off_and_res = pdf_tables.create_composite_table(table1=telephone_office,table2=telephone_res,col_widths=[(doc.width-doc.rightMargin*2)*0.5,10,(doc.width-doc.rightMargin*2)*0.5])
        mobile_referer = pdf_components.checkbox_field(doc,options=constant_texts.contact_mobile_dependent_relationship_options,selected_options=constant_texts.contact_mobile_dependent_relationship_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        mob_and_referrer = pdf_tables.create_composite_table(table1=mob_num,table2=mobile_referer,col_widths=[None,1,None])

        email = pdf_components.get_text_field(doc,field_name=constant_texts.contact_email_label,value=constant_texts.contact_email_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)


        email_referrer = pdf_components.checkbox_field(doc,options=constant_texts.contact_email_dependent_relationship_options,selected_options=constant_texts.contact_email_dependent_relationship_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        email_and_referrer = pdf_tables.create_composite_table(table1=email,table2=email_referrer,col_widths=[None,1,None])

        table = Table([[contact_details],[email_and_referrer],[mob_and_referrer],[telephones_off_and_res]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))

        return table
    
    def _get_kyc_section4(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        section4_heading = Paragraph(constant_texts.fatca_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        resident_field = pdf_components.checkbox_field(doc,options=constant_texts.tax_resident_options,selected_options=constant_texts.tax_resident_selected_options,field_name_text=constant_texts.tax_resident_label,field_width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        pob = pdf_components.get_text_field(doc,field_name=constant_texts.place_of_birth_label,value=constant_texts.place_of_birth_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        country_of_origin = pdf_components.get_text_field(doc,field_name=constant_texts.country_of_origin_label,value=constant_texts.country_of_origin_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        iso_country_code = pdf_components.get_text_field(doc,field_name=constant_texts.iso_3166_country_code_label,value=constant_texts.iso_3166_country_code_value,width=(doc.width-doc.rightMargin*2)/3,size=8)
        pob_country_iso_code = Table([[pob,country_of_origin,iso_country_code]],style=pdf_styles.padded_justified_table_style())

        fatca_tin_table_data = []
        row_hts = []
        for row_index, row in enumerate(constant_texts.fatca_table_data):
            if row_index == 0:  # First row (header)
                fatca_tin_table_data.append([Paragraph(cell, style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
            else:  # Subsequent rows - data in upper case
                fatca_tin_table_data.append([Paragraph(f'{cell}'.upper(), style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color))for cell in row])
            row_hts.append(10 if not row[3] else None)
        fatca_tin_table = pdf_tables.create_table(data=fatca_tin_table_data ,style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2,styling_list=[('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),]),col_widths=[None,None,None,None],row_heights=row_hts)

        note_1 = Paragraph(constant_texts.fatca_note_1,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_2 = Paragraph(constant_texts.fatca_note_2,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_3 = Paragraph(constant_texts.fatca_note_3,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_a = Paragraph(constant_texts.fatca_note_a,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_b = Paragraph(constant_texts.fatca_note_b,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        note_c = Paragraph(constant_texts.fatca_note_c,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))

        certification_table = Table([[Paragraph(constant_texts.certification_heading,style=pdf_styles.normal_text_style(alignment=1,fontsize=8))],[Paragraph(constant_texts.certification_content,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))]],
                                    style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2))
        
        table = Table([[section4_heading],[resident_field],[pob_country_iso_code],[fatca_tin_table],[note_1],[note_2],[note_3],[note_a],[note_b],[note_c],[certification_table]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        return table
    
    def _get_kyc_section5_6_7(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        gross_annual_income = pdf_components.checkbox_field(doc,options=constant_texts.gross_income_range_options,selected_options=constant_texts.gross_income_selected_options,field_name_text=constant_texts.gross_annual_income_label,field_width=(doc.width-doc.rightMargin*2)*0.75,size=8)
        gross_income_date = pdf_components.get_text_field(doc,field_name=constant_texts.gross_income_date_label,value=constant_texts.gross_income_date_value,width=(doc.width-doc.rightMargin*2)*0.25,size=8)
        gross_income_and_date = pdf_tables.create_composite_table(table1=gross_annual_income,table2=gross_income_date,col_widths=[(doc.width-doc.rightMargin*2)*0.75,1,(doc.width-doc.rightMargin*2)*0.25])
        networth = pdf_components.get_text_field(doc,field_name=constant_texts.gross_networth_label,value=constant_texts.gross_networth_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        networth_date = pdf_components.get_text_field(doc,field_name=constant_texts.gross_networth_date_label,value=constant_texts.gross_networth_date_value,width=(doc.width-doc.rightMargin*2)*0.5,size=8)
        networth_and_date = pdf_tables.create_composite_table(table1=networth,table2=networth_date,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])

        occupation = pdf_components.checkbox_field(doc,options=constant_texts.occupation_options,selected_options=constant_texts.occupation_selected_options,field_name_text=constant_texts.occupation_label,field_width=(doc.width-doc.rightMargin*2),size=8)
        pep = pdf_components.checkbox_field(doc,options=constant_texts.pep_options,selected_options=constant_texts.pep_selected_options,field_name_text=constant_texts.pep_label,field_width=(doc.width-doc.rightMargin*2),size=8)
        
        table = Table([[gross_income_and_date],[networth_and_date],[occupation],[pep]])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))

        return table
    
    async def _get_kyc_section8(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        section8_heading = Paragraph(constant_texts.applicant_declaration_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=0))
        section4_declaration = Paragraph(constant_texts.applicant_declaration_content, style=pdf_styles.normal_text_style(fontsize=8,alignment=0))
        date = pdf_components.get_text_field(doc,field_name=constant_texts.declaration_date_label,value=self.date_of_form_submission,width=(doc.width-doc.rightMargin*2)*0.3,size=8)
        place = pdf_components.get_text_field(doc,field_name=constant_texts.declaration_place_label,value=constant_texts.declaration_place_value,width=(doc.width-doc.rightMargin*2)*0.3,size=8)
        date_place = pdf_tables.create_composite_table(table1=date,table2=place,col_widths=[(doc.width-doc.rightMargin*2)*0.3,1,(doc.width-doc.rightMargin*2)*0.3])

        _file_id = constant_texts.applicant_wet_sign_value
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None

        _wetsign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=1*inch) if _wetsign_bytes else ''

        table = Table([[section8_heading,Paragraph(constant_texts.applicant_esign_label,style=pdf_styles.normal_text_style(alignment=1,fontsize=8)),Paragraph(constant_texts.applicant_wet_sign_label,style=pdf_styles.normal_text_style(alignment=1,fontsize=8))],
                       [Table([[section4_declaration],[date_place]]),'',_wetsign]
                       ])
        
        table.setStyle(pdf_styles.bordered_table_style(h_margin=2,v_margin=2,styling_list=[('GRID', (1, 0), (-1, 1), 1, colors.black),('VALIGN',(1, 0),(-1,1),'MIDDLE'),('ALIGN',(1, 0),(-1,1),'CENTER'),]))
        return table

    def _get_kyc_verification_details_section(self,doc,index):
        constant_texts = self.constant_texts.page_kyc_details[index]
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        section_heading = Paragraph(constant_texts.kyc_verification_heading, style=pdf_styles.bold_text_style(fontsize=8,alignment=1))
        date = pdf_components.get_text_field(doc,field_name=constant_texts.ipv_carried_out_on_date_label,value=constant_texts.ipv_carried_out_on_date_value,width=(doc.width-doc.rightMargin*2)*0.75/2,size=8)
        place = pdf_components.get_text_field(doc,field_name=constant_texts.ipv_place_label,value=constant_texts.ipv_place_value,width=(doc.width-doc.rightMargin*2)*0.75/2,size=8)
        date_place = pdf_tables.create_composite_table(table1=date,table2=place,col_widths=[(doc.width-doc.rightMargin*2)*0.75/2,1,(doc.width-doc.rightMargin*2)*0.75/2])
        
        name = pdf_components.get_text_field(doc,field_name=constant_texts.official_name_label,value=constant_texts.official_name_value,width=(doc.width-doc.rightMargin*2)*0.75,size=8)
        designation = pdf_components.get_text_field(doc,field_name=constant_texts.official_designation_label,value=constant_texts.official_designation_value,width=(doc.width-doc.rightMargin*2)*0.55,size=8)
        employee_code = pdf_components.get_text_field(doc,field_name=constant_texts.employee_ap_code_label,value=constant_texts.employee_ap_code_value,width=(doc.width-doc.rightMargin*2)*0.2,size=8)
        designation_emp_code = pdf_tables.create_composite_table(table1=designation,table2=employee_code,col_widths=[(doc.width-doc.rightMargin*2)*0.55,1,(doc.width-doc.rightMargin*2)*0.2])
        document_recieved_field = pdf_components.checkbox_field(doc,options=constant_texts.documents_received_options,selected_options=constant_texts.documents_received_selected_options,field_name_text='',field_width=(doc.width-doc.rightMargin*2)*0.75,size=8)

        signature = pdf_components.boxed_sign_field(doc=doc,display_name=constant_texts.signature_branch_ap_seal_label,alignment=1,fontsize=8,alpha=0.5,box_width=(doc.width-doc.rightMargin*2)*0.25,box_height=0.6*inch)

        left_table = Table([[section_heading],[date_place],[name],[designation_emp_code],[document_recieved_field]],style=pdf_styles.padded_table_style())
        table = Table([[left_table,signature]])
        table.setStyle(pdf_styles.bordered_table_style(h_margin=2,v_margin=2))
        return table


    async def get_page6(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        page_table_heading = Paragraph(constant_texts.page6_additional_details_part_b_heading,style=pdf_styles.bold_text_style(alignment=1))
        other_details_heading = Paragraph(constant_texts.page6_additional_details_table_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=8))
        rbi_approval_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_rbi_approval_ref_no_label,value=constant_texts.page6_rbi_approval_ref_no_value,width=(doc.width-doc.rightMargin*2)*2/3,)
        date_approval_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_date_of_approval_label,value=constant_texts.page6_date_of_approval_value,width=(doc.width-doc.rightMargin*2)/3,)
        rbi_approval_and_date = pdf_tables.create_composite_table(table1=rbi_approval_field,table2=date_approval_field,col_widths=[(doc.width-doc.rightMargin*2)*2/3,1,None])
        employer_name_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_name_of_employer_label,value=constant_texts.page6_name_of_employer_value,width=(doc.width-doc.rightMargin*2))
        address_contact_no_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_address_and_contact_label,value=constant_texts.page6_address_and_contact_value,width=(doc.width-doc.rightMargin*2))

        bank_and_depository_heading = Paragraph(constant_texts.page6_bank_and_depository_table_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=8))
        bank_name = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_bank_name_label,value=constant_texts.page6_bank_name_value,width=(doc.width-doc.rightMargin*2))
        bank_address = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_bank_address_label,value=constant_texts.page6_bank_address_value,width=(doc.width-doc.rightMargin*2))
        bank_acc_no = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_bank_account_num_label,value=constant_texts.page6_bank_account_num_value,width=(doc.width-doc.rightMargin*2)*0.4)
        ifsc = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_ifsc_code_label,value=constant_texts.page6_ifsc_code_value,width=(doc.width-doc.rightMargin*2)*0.3)
        micr_no = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_micr_num_label,value=constant_texts.page6_micr_num_value,width=(doc.width-doc.rightMargin*2)*0.3)
        bank_acc_no_ifsc_micr = Table([[bank_acc_no,ifsc,micr_no]],style=pdf_styles.padded_table_style())
        
        type_of_acc = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_bank_ac_type_label,options=constant_texts.page6_bank_ac_type_options,selected_options=constant_texts.page6_bank_ac_type_selected_options,field_width=(doc.width-doc.rightMargin*2)*0.4)
        upi_id = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_upi_id_label,value=constant_texts.page6_upi_id_value,width=(doc.width-doc.rightMargin*2)*0.6)
        type_of_acc_upi_id = pdf_tables.create_composite_table(table1=type_of_acc,table2=upi_id,col_widths=[(doc.width-doc.rightMargin*2)*0.4,1,(doc.width-doc.rightMargin*2)*0.6])

        depository_participant_name = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_depository_participant_name_label,value=constant_texts.page6_depository_participant_name_value,width=(doc.width-doc.rightMargin*2)*0.5)
        dp_id_no = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_dp_id_num_label,value=constant_texts.page6_dp_id_num_value,width=(doc.width-doc.rightMargin*2)*0.5)
        depository_participant_name_dp_id = pdf_tables.create_composite_table(table1=depository_participant_name,table2=dp_id_no,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])

        client_id_no = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_client_id_label,value=constant_texts.page6_client_id_value,width=(doc.width-doc.rightMargin*2)*0.5)
        depository = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_depositry_label,options=constant_texts.page6_depositry_options,selected_options=constant_texts.page6_depositry_selected_options,field_width=(doc.width-doc.rightMargin*2)*0.5)
        client_id_depositiry = pdf_tables.create_composite_table(table1=client_id_no,table2=depository,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])

        exchange_and_segment_heading = Paragraph(constant_texts.page6_exchange_and_segment_preferences_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=8))
        exchange_and_segment_instructions = Paragraph(constant_texts.page6_exchange_and_segment_preferences_instruction,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        
        exchange_and_segment_table_data = [[Paragraph(cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=8)) for cell in row] for row in constant_texts.page6_exchange_segment_table_data]
        _file_id = constant_texts.page_kyc_details[0].applicant_wet_sign_value if 0 < len(self.constant_texts.page_kyc_details) else None
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''

        for index in range(1, len(constant_texts.page6_exchange_segment_table_data)):
            if constant_texts.page6_exchange_segment_selected_options[index-1]:
                exchange_and_segment_table_data[index][2] = _client_sign

        exchange_segment_table = pdf_tables.create_table(data=exchange_and_segment_table_data,
                                                         col_widths=[(doc.width-doc.rightMargin*2)*0.4,(doc.width-doc.rightMargin*2)*0.15,(doc.width-doc.rightMargin*2)*0.45],
                                                         style=pdf_styles.bordered_grid_table_style(styling_list=[('SPAN', (0, 1), (0, 3)),('VALIGN', (0, 0), (-1, -1),'MIDDLE')],v_margin=2),
                                                         row_heights=[None,50,50,50,50,50],)
        
        exchange_pref_note = Paragraph(constant_texts.page6_exchange_prefs_note,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))
        exchange_pref_past_action_label = Paragraph(constant_texts.page6_exchange_prefs_past_action_label,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))
        exchange_pref_past_action_value_field = pdf_components.get_text_field(doc=doc,field_name='',value=constant_texts.page6_exchange_prefs_past_action_value,width=(doc.width-doc.rightMargin*2)*0.5)
        exchange_pref_other_info_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_exchange_prefs_any_other_info_label,value=constant_texts.page6_exchange_prefs_any_other_info_value,width=(doc.width-doc.rightMargin*2)*0.5)
        exchange_pref_past_action_other_info = pdf_tables.create_composite_table(table1=exchange_pref_past_action_value_field,table2=exchange_pref_other_info_field,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])
        
        details_of_dealing_heading = Paragraph(constant_texts.page6_details_of_dealing_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        
        broker_name_address = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_broker_name_and_address_label,value=constant_texts.page6_broker_name_address_value,width=(doc.width-doc.rightMargin*2))
        broker_dispute_details = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_broker_details_of_dispute_label,value=constant_texts.page6_broker_details_of_dispute_value,width=(doc.width-doc.rightMargin*2))
        
        broker_telephone = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_broker_telephone_label,value=constant_texts.page6_broker_telephone_value,width=(doc.width-doc.rightMargin*2)*0.5)
        broker_client_codes = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page6_broker_client_code_label,value=constant_texts.page6_broker_client_code_value,width=(doc.width-doc.rightMargin*2)*0.5)
        broker_telephone_client_code = pdf_tables.create_composite_table(table1=broker_telephone,table2=broker_client_codes,col_widths=[(doc.width-doc.rightMargin*2)*0.5,1,(doc.width-doc.rightMargin*2)*0.5])
        
        additional_details_heading = Paragraph(constant_texts.page6_additional_details_section_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        additional_details_physical_contract_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_additional_details_physcial_contract_field_label,options=constant_texts.page6_additional_details_physcial_contract_field_options,selected_options=constant_texts.page6_additional_details_physcial_contract_field_selected_options,field_width=(doc.width-doc.rightMargin*2))
        additional_details_internet_option_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_additional_details_internet_option_label,options=constant_texts.page6_additional_details_internet_option_options,selected_options=constant_texts.page6_additional_details_internet_option_selected_options,field_width=(doc.width-doc.rightMargin*2))
        additional_details_trading_experience_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_additional_details_experience_field_label,options=constant_texts.page6_additional_details_experience_field_options,selected_options=constant_texts.page6_additional_details_experience_field_selected_options,field_width=(doc.width-doc.rightMargin*2))
        additional_details_acc_opening_kit_opt_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page6_additional_details_opt_for_ac_opening_kit_label,options=constant_texts.page6_additional_details_opt_for_ac_opening_kit_options,selected_options=constant_texts.page6_additional_details_opt_for_ac_opening_kit_selected_options,field_width=(doc.width-doc.rightMargin*2))

        

        table = Table([[page_table_heading],[other_details_heading],
                       [rbi_approval_and_date],[employer_name_field],
                       [address_contact_no_field],[bank_and_depository_heading],
                       [bank_name],[bank_address],[bank_acc_no_ifsc_micr],
                       [type_of_acc_upi_id],[depository_participant_name_dp_id],
                       [client_id_depositiry],[exchange_and_segment_heading],
                       [exchange_and_segment_instructions],
                        [exchange_segment_table],
                        [exchange_pref_note],
                        [exchange_pref_past_action_label],
                        [exchange_pref_past_action_other_info],
                        [details_of_dealing_heading],
                        [broker_name_address],
                        [broker_telephone_client_code],
                        [broker_dispute_details],
                        [additional_details_heading],
                        [additional_details_physical_contract_field],
                        [additional_details_internet_option_field],
                        [additional_details_trading_experience_field],
                        [additional_details_acc_opening_kit_opt_field]
                       ])
        table.setStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, 1), 1, colors.black),
            ('GRID', (0, 5), (-1, 5), 1, colors.black),
            ('GRID', (0, 12), (-1, 13), 1, colors.black),
            ('GRID', (0, 15), (-1, 15), 1, colors.black),
            ('GRID', (0, 18), (-1, 18), 1, colors.black),

            ('GRID', (0, 22), (-1, 22), 1, colors.black),

        ])

        

        return [table,PageBreak()]
    
    async def get_page7(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        intruducer_details_heading = Paragraph(constant_texts.page7_introducer_details_heading,style=pdf_styles.bold_text_style(alignment=1))
        name_field_label = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page7_introducer_name_field_label,value=constant_texts.page7_introducer_name_field_value,width=(doc.width-doc.rightMargin*2)*2/3)

        address_field_label = Paragraph(constant_texts.page7_introducer_address_field_label,style=pdf_styles.normal_text_style(fontsize=8,alignment=0))
        address_field_value = pdf_components.get_multiline_text(doc,width=(doc.width-doc.rightMargin*2)*2/3,lines=2,text=constant_texts.page7_introducer_address_field_value)
        status_of_introducer_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page7_introducer_status_of_introducer_field_label,options=constant_texts.page7_introducer_status_of_introducer_field_options,selected_options=constant_texts.page7_introducer_status_of_introducer_field_selected_options,field_width=(doc.width-doc.rightMargin*2)*2/3)

        sing_of_introducer = pdf_components.boxed_sign_field(doc=doc,fontsize=8,display_name=constant_texts.page7_introducer_singnature_label,box_width=(doc.width-doc.rightMargin*2)/3 -10,box_height=0.4*inch,alignment=1,alpha=0.5)

        introducer_details_section_left = Table([[name_field_label],
            [address_field_label],
            [address_field_value],
            [status_of_introducer_field],
        ],style=pdf_styles.padded_table_style(top=2))
        introducer_details_section = Table([[introducer_details_section_left,sing_of_introducer]],style=pdf_styles.padded_justified_table_style(right=2))

        decalaration_heading = Paragraph(constant_texts.page7_declaration_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        decalaration_content = Paragraph(constant_texts.page7_declaration_text,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))
        
        _client_table_data = [[Paragraph(f'{cell}'.upper() if i==1 else cell,style=pdf_styles.normal_text_style(alignment=0,fontsize=9,text_color=pdf_colors.filled_data_color if i==1 else pdf_colors.text_color)) for i, cell in enumerate(row)] for row in constant_texts.page7_declaration_client_details_table_data]
        
        _file_id = constant_texts.page_kyc_details[0].applicant_wet_sign_value if 0 < len(self.constant_texts.page_kyc_details) else None
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
        _client_table_data[1][2] = _client_sign
        _client_table_data[2][1] = Paragraph(self.date_of_form_submission,style=pdf_styles.normal_text_style(alignment=0,fontsize=9, text_color=pdf_colors.filled_data_color))

        client_details_table = pdf_tables.create_table(data=_client_table_data
                                                       ,style=pdf_styles.bordered_table_style(h_margin=2,v_margin=2,alpha=0.5,styling_list=[
            ('SPAN', (2, 1), (2, 2)),
            ('GRID', (0, 2), (0, 2), 0.5, colors.black),
            ('GRID', (0, 0), (1, 2), 0.5, colors.black),
        ]),col_widths=[inch,(doc.width-doc.rightMargin*2)-4*inch,3*inch])

        brokerage_tariff_heading = Paragraph(constant_texts.page7_brokerage_tariff_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        bottom_declaration = Paragraph(constant_texts.page7_bottom_declaration_text,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))
        gst_details_heading = Paragraph(constant_texts.page7_gst_details_text,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        gst_no_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page7_gst_no_field_label,value=constant_texts.page7_gst_no_field_value,width=(doc.width-doc.rightMargin*2)*0.4)
        gst_state_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page7_gst_state_field_label,value=constant_texts.page7_gst_state_field_value,width=(doc.width-doc.rightMargin*2)*0.4)

        gst_details = pdf_tables.create_table(data=[
            [gst_details_heading,gst_no_field,gst_state_field]
        ],col_widths=[inch,None,None],style=pdf_styles.padded_table_style())

        client_sign = pdf_tables.create_composite_table(table1=pdf_components.boxed_sign_field(doc=doc,fontsize=8,display_name=constant_texts.page7_client_signature_field_label,value=_client_sign,box_width=(doc.width-doc.rightMargin*2)/2,box_height=0.4*inch,alignment=1,alpha=0.5),
                                                        table2=Spacer((doc.width-doc.rightMargin*2)/2,0),
                                                        col_widths=[None,1,None]
                                                        )

        brokerage_segment_rate_table = pdf_tables.create_table(
            data=[[Paragraph(cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=8)) for cell in row] for row in constant_texts.page7_brokerage_tariff_segment_standard_rates_table_data],
            col_widths=[1.2*inch,0.8*inch,0.8*inch],
            row_heights=[12]*11,
            style=pdf_styles.bordered_grid_table_style(v_margin=2,h_margin=2,styling_list=[
                ('VALIGN', (0, 0), (-1, -1),('MIDDLE')),
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (1, 0), (2, 0)),
                ('SPAN', (1, 5), (2, 5)),
                ('SPAN', (1, 7), (2, 7)),
                ('SPAN', (1, 9), (2, 9)),
                ('SPAN', (1, 10), (2, 10)),
            ])
        )

        brokerage_special_rates_table = pdf_tables.create_table(
            data=[[Paragraph(cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row] for row in constant_texts.page7_brokerage_tariff_special_rates_table_data],
            col_widths=[0.8*inch,0.8*inch],
            row_heights=[12]*11,
            style=pdf_styles.bordered_grid_table_style(v_margin=2,h_margin=2,styling_list=[
                ('VALIGN', (0, 0), (-1, -1),('MIDDLE')),
                ('SPAN', (0, 0), (1, 0)),
                ('SPAN', (0, 5), (1, 5)),
                ('SPAN', (0, 7), (1, 7)),
                ('SPAN', (0, 9), (1, 9)),
                ('SPAN', (0, 10), (1, 10)),

            ])
        )

        flat_per_order_table = pdf_tables.create_table(
            data=[[Paragraph(cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row] for row in constant_texts.page7_brokerage_tariff_flat_per_table_data],
            col_widths=1.5*inch,
            row_heights=[12,30],
            style=pdf_styles.bordered_grid_table_style(h_margin=5,v_margin=2,styling_list=[('VALIGN', (0, 0), (-1, -1),('MIDDLE'))])
        )
        online_exe_fee_checkbox = pdf_components.get_checkbox_option(doc=doc,option_text=constant_texts.page7_brokerage_tariff_online_fee_option_text,filled=len(constant_texts.page7_brokerage_tariff_online_fee_option_selection)!=0,width=1.5*inch)
        brokerage_tariff_right_section = pdf_tables.create_table(
            data=[[flat_per_order_table],[Spacer(0,inch)],[online_exe_fee_checkbox]],
            col_widths=[None],
            style=pdf_styles.padded_table_style()
        )
        brokerage_tariff_section = pdf_tables.create_table(data=[
            [brokerage_segment_rate_table,brokerage_special_rates_table,brokerage_tariff_right_section]
        ],
        style=pdf_styles.padded_table_style(left=10),
        col_widths=[None,None,2*inch]
        )

        table = Table(data=[
            [intruducer_details_heading],
            [introducer_details_section],
            [decalaration_heading],
            [decalaration_content],
            [client_details_table],
            [brokerage_tariff_heading],
            [brokerage_tariff_section],
            [bottom_declaration],
            [gst_details],
            [client_sign]
        ])
        table.setStyle(
            pdf_styles.bordered_table_style(h_margin=5,v_margin=5,styling_list=[
                ('GRID', (0, 0), (-1, 1), 1, colors.black),
                ('GRID', (0, 2), (-1, 2), 1, colors.black),
                ('GRID', (0, 5), (-1, 6), 1, colors.black),
            ])
        )
        return [table,PageBreak()]

    async def get_page8(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        table_heading = Paragraph(constant_texts.page8_table_heading,style=pdf_styles.bold_text_style(alignment=1))

        dp_depository_field = pdf_components.checkbox_field(doc=doc, field_name_text='',field_width=doc.width-doc.rightMargin,options=constant_texts.page8_dp_account_depository_options,selected_options=constant_texts.page8_dp_account_depository_selected_options)

        account_type = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_account_type_field_display_name,options=constant_texts.page8_account_type_options,field_width=doc.width-doc.rightMargin,selected_options=constant_texts.page8_account_type_selected_options,)
        guardian_details_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_guardian_details_field_display_name,options=constant_texts.page8_guardian_details_field_options,selected_options=constant_texts.page8_guardian_details_field_selected_options,field_width=(doc.width-doc.rightMargin*2)*0.6)
        guardian_pan_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_guardian_pan_field_display_name,value=constant_texts.page8_guardian_pan_field_value,width=(doc.width-doc.rightMargin*2)*0.3)
        guradian_pan_composite = pdf_tables.create_composite_table(table1=guardian_details_field,table2=guardian_pan_field,col_widths=[(doc.width-doc.rightMargin*2)*0.7,1,(doc.width-doc.rightMargin*2)*0.3])
        guardian_name_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_guardian_name_field_display_name,value=constant_texts.page8_guardian_name_field_value,width=doc.width-doc.rightMargin*2)

        address_field_label = Paragraph(constant_texts.page8_guardian_address_field_display_name,style=pdf_styles.normal_text_style(fontsize=8,alignment=0))
        address_field_value = pdf_components.get_multiline_text(doc,width=(doc.width-doc.rightMargin*2),lines=2,text=constant_texts.page8_guardian_address_field_display_value)
        guardian_city_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_guardian_city_field_display_name,value=constant_texts.page8_guardian_city_field_display_value,width=(doc.width-doc.rightMargin*2)*0.5)
        guardian_pincode_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_guardian_pincode_field_display_name,value=constant_texts.page8_guardian_pincode_field_display_value,width=(doc.width-doc.rightMargin*2)*0.2)
        guardian_state_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_guardian_state_field_display_name,value=constant_texts.page8_guardian_state_field_display_value,width=(doc.width-doc.rightMargin*2)*0.3)
        guardian_city_pincode_state = pdf_tables.create_table(
            data=[[guardian_city_field,guardian_pincode_field,guardian_state_field]],
            col_widths=[(doc.width-doc.rightMargin*2)*0.5,(doc.width-doc.rightMargin*2)*0.2,(doc.width-doc.rightMargin*2)*0.3],
            style=pdf_styles.padded_justified_table_style()
        )

        relationship_with_holder = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page8_relationship_with_holder_display_name,value=constant_texts.page8_relationship_with_holder_value,width=doc.width-doc.rightMargin*2)

        instructions_heading = Paragraph(constant_texts.page8_instructions_heading,style=pdf_styles.bold_text_style(alignment=0,fontsize=9))
        _field_width = doc.width-doc.rightMargin*2
        _field_display_width = (doc.width-doc.rightMargin*2)*0.6
        instruction1 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction1_display_name,options=constant_texts.page8_instruction1_options,selected_options=constant_texts.page8_instruction1_selcted_options,field_width=_field_width,display_name_width=_field_display_width)

        instruction2 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction2_display_name,options=constant_texts.page8_instruction2_options,selected_options=constant_texts.page8_instruction2_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction3 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction3_display_name,options=constant_texts.page8_instruction3_options,selected_options=constant_texts.page8_instruction3_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction4 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction4_display_name,options=constant_texts.page8_instruction4_options,selected_options=constant_texts.page8_instruction4_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction5 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction5_display_name,options=constant_texts.page8_instruction5_options,selected_options=constant_texts.page8_instruction5_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction6 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction6_display_name,options=constant_texts.page8_instruction6_options,selected_options=constant_texts.page8_instruction6_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction7 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction7_display_name,options=constant_texts.page8_instruction7_options,selected_options=constant_texts.page8_instruction7_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction8 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction8_display_name,options=constant_texts.page8_instruction8_options,selected_options=constant_texts.page8_instruction8_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction8_bsda_declaration = Paragraph(constant_texts.page8_instruction8_declaration_text,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))
        instruction9 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction9_display_name,options=constant_texts.page8_instruction9_options,selected_options=constant_texts.page8_instruction9_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction10 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction10_display_name,options=constant_texts.page8_instruction10_options,selected_options=constant_texts.page8_instruction10_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction11 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction11_display_name,options=constant_texts.page8_instruction11_options,selected_options=constant_texts.page8_instruction11_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction12 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction12_display_name,options=constant_texts.page8_instruction12_options,selected_options=constant_texts.page8_instruction12_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        instruction13 = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page8_instruction13_display_name,options=constant_texts.page8_instruction13_options,selected_options=constant_texts.page8_instruction13_selected_options,field_width=_field_width,display_name_width=_field_display_width)
        
        undertaking_text = Paragraph(constant_texts.page8_instructions_untertaking,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        
        stock_exchange_table_data = []
        for row_index, row in enumerate(constant_texts.page8_stock_exchange_table_data):
            if row_index == 0:  # First row (header)
                stock_exchange_table_data.append([Paragraph(cell, style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
            else:  # Subsequent rows - data in upper case
                stock_exchange_table_data.append([Paragraph(f'{cell}'.upper(), style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
        
        stock_exchange_table = pdf_tables.create_table(data=stock_exchange_table_data,style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2),col_widths=[(doc.width-doc.rightMargin*2)/3],row_heights=[None,10])
        ucc_mapping_instruction14 = Paragraph(constant_texts.page8_ucc_mapping_heading,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        
        ucc_mapping_table_data = []
        for row_index, row in enumerate(constant_texts.page8_ucc_mapping_table):
            if row_index == 0:  # First row (header)
                ucc_mapping_table_data.append([Paragraph(cell, style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
            else:  # Subsequent rows - data in upper case
                ucc_mapping_table_data.append([Paragraph(f'{cell}'.upper(), style=pdf_styles.normal_text_style(alignment=1,fontsize=8,text_color=pdf_colors.filled_data_color)) for cell in row])
        
        
        ucc_mapping_table = pdf_tables.create_table(data=ucc_mapping_table_data,style=pdf_styles.bordered_grid_table_style(h_margin=2,v_margin=2),col_widths=[(doc.width-doc.rightMargin*2)/5],row_heights=[None,10,10])

        
        sign_section_data = []
        for i in range(0,3):
            _file_id = constant_texts.page_kyc_details[i].applicant_wet_sign_value if i < len(self.constant_texts.page_kyc_details) else None
            _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
            _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
            sign_section_data.append(pdf_components.signature_field(display_name=f"{i+1}. {constant_texts.page8_holder_signature_field_lable}",value=_client_sign,width=2*inch,alignment=1,fontsize=9))
        
        holders_signature_section = Table([
            sign_section_data
        ])
        holders_signature_section.setStyle(pdf_styles.bordered_grid_table_style(h_margin=10,v_margin=10))

        holder_sign_heading = Paragraph(constant_texts.page8_holder_sign_heading,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        table = Table([[table_heading],[dp_depository_field],
                       [account_type],[guradian_pan_composite],
                       [address_field_label],[address_field_value],[guardian_city_pincode_state],
                       [guardian_name_field],[relationship_with_holder],
                       [instructions_heading],
                       [instruction1],[instruction2],
                       [instruction3],[instruction4],
                       [instruction5],[instruction6],
                       [instruction7],[instruction8],
                       [instruction8_bsda_declaration],[instruction9],
                       [instruction10],[instruction11],
                       [instruction12],[instruction13],
                       [undertaking_text],[stock_exchange_table],
                       [ucc_mapping_instruction14],[ucc_mapping_table],
                       [Spacer(0,5)],[holder_sign_heading],
                       [holders_signature_section]
                       ])
        table.setStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, 1), 1, colors.black),

        ])
        return [table,PageBreak()]
   
    async def get_page9(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        table_heading = Paragraph(constant_texts.page9_declaration_heading,style=pdf_styles.bold_text_style(alignment=1))

        declaration_text = Paragraph(constant_texts.page9_declaration_content,style=pdf_styles.normal_text_style(alignment=4,fontsize=8))

        _sign_table_data = [[Paragraph(f'{cell}'.upper() if i==1 else cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=9)) for i, cell in enumerate(row)] for row in constant_texts.page9_holders_signature_table_data]
        for i in range(0,len(self.constant_texts.page_kyc_details)):
            _file_id = constant_texts.page_kyc_details[i].applicant_wet_sign_value
            _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
            _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
            _sign_table_data[i+1][2] = _client_sign
            
        signature_table = pdf_tables.create_table(data=_sign_table_data,style=pdf_styles.bordered_grid_table_style(styling_list=[('SPAN', (0, 0), (1, 0))],v_margin=20,h_margin=10),col_widths=[(doc.width-doc.rightMargin*2)/3])

        table = Table([[table_heading],[declaration_text],[signature_table]])
        table.setStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, 0), 1, colors.black),

        ])
        return [table,PageBreak()]

    async def get_page10(self,doc,number_of_nominees):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_components = PdfComponents()

        table_heading = Paragraph(constant_texts.page10_table_heading,style=pdf_styles.bold_text_style(alignment=1))
        nominee_checkbox_option1_field = pdf_components.get_checkbox_option(doc=doc,option_text=constant_texts.page10_nominate_option1_text,filled=f'{constant_texts.page10_nomination_selection}'.lower()=="no",width=doc.width-doc.rightMargin*2)
        nominee_checkbox_option1_description = Paragraph(constant_texts.page10_nominate_option1_description,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        nominee_checkbox_option2_field = pdf_components.get_checkbox_option(doc=doc,option_text=constant_texts.page10_nominate_option2_text,filled=f'{constant_texts.page10_nomination_selection}'.lower()=="yes",width=doc.width-doc.rightMargin*2)
        nominee_checkbox_option2_description = Paragraph(constant_texts.page10_nominate_option2_description,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))

        ''' Non - tabular nominee details '''
        nominee_details_sections = [] 
        for i in range (number_of_nominees):
            nominee_details_sections.append(self._page10_nominee_details(doc=doc, index=i)) 
            nominee_details_sections.append(Spacer(1, 10))

        nomination_undertaking_text = Paragraph(constant_texts.page10_nomination_undertaking_text,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        
        sign_section_data = []
        for i in range(0,3):
            _file_id = constant_texts.page_kyc_details[i].applicant_wet_sign_value if i < len(self.constant_texts.page_kyc_details) else None
            _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
            _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
            sign_section_data.append(pdf_components.signature_field(display_name=f"{i+1}. {constant_texts.page10_nominee_signature_field_label}",value=_client_sign,width=2*inch,alignment=1,fontsize=9))
        
        holders_signature_section = Table([
            sign_section_data
        ])
        holders_signature_section.setStyle(pdf_styles.bordered_grid_table_style(h_margin=10,v_margin=10))


        table_data = [[table_heading],
                       [nominee_checkbox_option1_field],
                       [nominee_checkbox_option1_description],
                       [nominee_checkbox_option2_field],
                       [nominee_checkbox_option2_description],
                       [nominee_details_sections],
                       [nomination_undertaking_text],
                        [holders_signature_section]
                       ]
        
        table = Table(table_data)
        

        table.setStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, 0), 1, colors.black),

        ])
        return [table,PageBreak()]
    
    def _page10_nominee_details(self,doc,index):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        nominee_details_heading = Paragraph(f'{constant_texts.page10_nominee_details[index].nominee_details_heading} for Nominee {index+1}',style=pdf_styles.bold_text_style(alignment=0,fontsize=9))
        nominee_name_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_name_field_label,value=constant_texts.page10_nominee_details[index].nominee_name_field_value,width=(doc.width-doc.rightMargin*2)/2)
        percentage_of_allocation_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_percentage_of_allocation_field_label,value=constant_texts.page10_nominee_details[index].nominee_percentage_of_allocation_field_value,width=(doc.width-doc.rightMargin*2)*0.2)
        nominee_relationship_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_relationship_field_label,value=constant_texts.page10_nominee_details[index].nominee_relationship_field_value,width=(doc.width-doc.rightMargin*2)*0.3)
        nominee_name_allocation_relationship = pdf_tables.create_table(
            data=[[nominee_name_field,percentage_of_allocation_field,nominee_relationship_field]],
            col_widths=[(doc.width-doc.rightMargin*2)/2,None,(doc.width-doc.rightMargin*2)*0.3],
            style=pdf_styles.padded_justified_table_style(bottom=2)
            )
        nominee_odd_lot_text = Paragraph(constant_texts.page10_nominee_details[index].nominee_odd_lot_text,pdf_styles.normal_text_style(alignment=0,fontsize=8))
        nominee_address_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_address_field_label,value=constant_texts.page10_nominee_details[index].nominee_address_field_value,width=(doc.width-doc.rightMargin*2))
        nominee_telephone_mobile_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_telephone_field_label,value=constant_texts.page10_nominee_details[index].nominee_telephone_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_email_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_email_field_label,value=constant_texts.page10_nominee_details[index].nominee_email_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_mobile_email_composite = pdf_tables.create_composite_table(table1=nominee_telephone_mobile_field,table2=nominee_email_field,col_widths=[(doc.width-doc.rightMargin*2)/2,1,(doc.width-doc.rightMargin*2)/2])
        nominee_identification_details_text = Paragraph(constant_texts.page10_nominee_details[index].nominee_identification_details_text,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))
        nominee_proof_of_identity = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_proof_of_identity_field_label,value=constant_texts.page10_nominee_details[index].nominee_proof_of_identity_field_value,width=(doc.width-doc.rightMargin*2)/3)
        nominee_identitification_no_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_identitification_no_field_label,value=constant_texts.page10_nominee_details[index].nominee_identitification_no_field_value,width=(doc.width-doc.rightMargin*2)/3)
        nominee_dob_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_dob_field_label,value=constant_texts.page10_nominee_details[index].nominee_dob_field_value,width=(doc.width-doc.rightMargin*2)/3)
        nominee_identity_proof_id_no_dob = pdf_tables.create_table(
            data=[[nominee_proof_of_identity,nominee_identitification_no_field,nominee_dob_field]],
            col_widths=[(doc.width-doc.rightMargin*2)/3,(doc.width-doc.rightMargin*2)/3,(doc.width-doc.rightMargin*2)/3],
            style=pdf_styles.padded_justified_table_style(bottom=2)
            )

        nominee_guardian_details_heading = Paragraph(constant_texts.page10_nominee_details[index].nominee_guardian_details_heading,style=pdf_styles.bold_text_style(alignment=0,fontsize=9))
        nominee_guardian_name_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_name_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_name_field_value,width=(doc.width-doc.rightMargin*2)*0.6)
        nominee_guardian_relationship_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_relationship_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_relationship_field_value,width=(doc.width-doc.rightMargin*2)*0.4)
        nominee_guardian_name_relationship = pdf_tables.create_composite_table(table1=nominee_guardian_name_field,table2=nominee_guardian_relationship_field,col_widths=[(doc.width-doc.rightMargin*2)*0.6,1,(doc.width-doc.rightMargin*2)*0.4])
        
        nominee_guardian_address_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_address_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_address_field_value,width=(doc.width-doc.rightMargin*2))
        nominee_guardian_telephone_mobile_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_telephone_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_telephone_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_guardian_email_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_email_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_email_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_guardian_mobile_email_composite = pdf_tables.create_composite_table(table1=nominee_guardian_telephone_mobile_field,table2=nominee_guardian_email_field,col_widths=[(doc.width-doc.rightMargin*2)/2,1,(doc.width-doc.rightMargin*2)/2])
        nominee_guardian_identification_details_text = Paragraph(constant_texts.page10_nominee_details[index].nominee_guardian_details_text,style=pdf_styles.normal_text_style(alignment=0,fontsize=8))

        nominee_guardian_proof_of_identity = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_proof_of_identity_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_proof_of_identity_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_guardian_identitification_no_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page10_nominee_details[index].nominee_guardian_identitification_no_field_label,value=constant_texts.page10_nominee_details[index].nominee_guardian_identitification_no_field_value,width=(doc.width-doc.rightMargin*2)/2)
        nominee_guardian_identity_proof_id_no = pdf_tables.create_table(
            data=[[nominee_guardian_proof_of_identity,nominee_guardian_identitification_no_field]],
            col_widths=[(doc.width-doc.rightMargin*2)/2,(doc.width-doc.rightMargin*2)/2],
            style=pdf_styles.padded_justified_table_style(bottom=2)
            )

        return [
            nominee_details_heading,
            nominee_name_allocation_relationship,
            nominee_odd_lot_text,
            nominee_address_field,
            nominee_mobile_email_composite,
            Spacer(0,3),
            nominee_identification_details_text,
            nominee_identity_proof_id_no_dob,
            Spacer(0,3),
            nominee_guardian_details_heading,
            nominee_guardian_name_relationship,
            nominee_guardian_address_field,
            nominee_guardian_mobile_email_composite,
            Spacer(0,3),
            nominee_guardian_identification_details_text,
            nominee_guardian_identity_proof_id_no,
            Spacer(0,5),
        ]


    
    async def get_page11(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        left_header_section = Paragraph(constant_texts.page11_left_header,style=pdf_styles.bold_text_style(alignment=0,fontsize=9))
        right_header_section = Table([[load_logo(width=1.5*inch)],[pdf_components.get_text_field(doc=doc,field_name=constant_texts.page11_dp_client_id_field_lable,value=constant_texts.page11_dp_client_id_field_value,bold=True,width=(doc.width-doc.rightMargin*2)*0.3)]])
        page_header = pdf_tables.create_table([[left_header_section,right_header_section]],style=pdf_styles.padded_justified_table_style(),col_widths=[(doc.width-doc.rightMargin*2)*0.7,(doc.width-doc.rightMargin*2)*0.3])

        table_header = Paragraph(constant_texts.page11_table_heading,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))

        table_data = [[Paragraph(cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=9)) for cell in row] for row in constant_texts.page11_table_data]
        table = pdf_tables.create_table(data=table_data,col_widths=[(doc.width-doc.rightMargin*2)*0.25,None,None,(doc.width-doc.rightMargin*2)*0.45],style=pdf_styles.bordered_grid_table_style(
            h_margin=5,v_margin=2,
            styling_list=[
                ('FONTNAME', (0, 0), (-1, 0), 'LatoBold'),
                ('SPAN', (0, 3), (-1, 3)),
                ('SPAN', (1, 4), (-1, 4)),
                ('SPAN', (1, 5), (-1, 5)),
                ('SPAN', (1, 6), (-1, 6)),
                ('SPAN', (0, 7), (-1, 7)),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]
        ))
        astric_description = Paragraph(constant_texts.page11_condition_description,style=pdf_styles.bold_text_style(alignment=4,fontsize=9))
        tnc_heading = Paragraph(constant_texts.page11_tnc_heading,style=pdf_styles.bold_text_style(alignment=0,fontsize=9))
        tnc_content = Paragraph(constant_texts.page11_tnc,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))
        tnc_undertaking_text = Paragraph(constant_texts.page11_tnc_undertaking_text,style=pdf_styles.bold_text_style(alignment=4,fontsize=9))

        sign_section_data = []
        for i in range(0,3):
            _file_id = constant_texts.page_kyc_details[i].applicant_wet_sign_value if i < len(self.constant_texts.page_kyc_details) else None
            _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
            _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
            sign_section_data.append(pdf_components.signature_field(display_name=f"{i+1}. {constant_texts.page11_holder_signature_field_lable}",value=_client_sign,width=2*inch,alignment=1,fontsize=9))
        
        holders_signature_section = Table([
            sign_section_data
        ])
        holders_signature_section.setStyle(pdf_styles.bordered_grid_table_style(h_margin=10,v_margin=10))

        return [page_header,table_header,Spacer(0,5),table,Spacer(0,5),astric_description,Spacer(0,5),tnc_heading,tnc_content,Spacer(0,5),tnc_undertaking_text,Spacer(0,5),holders_signature_section,PageBreak()]
    
    async def get_page12(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        page_heading = Paragraph(constant_texts.page12_heading,style=pdf_styles.bold_text_style(alignment=1))

        page_subheading = Paragraph(constant_texts.page12_subheading,style=pdf_styles.bold_text_style(alignment=1))

        clauses = Paragraph(constant_texts.page12_clauses,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))

        declaration_heading = Paragraph(constant_texts.page12_declaration_heading,style=pdf_styles.bold_text_style(alignment=0))
        declaration_content = Paragraph(constant_texts.page12_declaration_content,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))

        client_name = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page12_client_name_label,value=constant_texts.page12_client_name_value,width=(doc.width-doc.rightMargin*2)/2)
        place = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page12_place_label,value=constant_texts.page12_place_value,width=(doc.width-doc.rightMargin*2)/2)
        date = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page12_date_label,value=self.date_of_form_submission,width=(doc.width-doc.rightMargin*2)/2)

        _file_id = constant_texts.page_kyc_details[0].applicant_wet_sign_value if 0 < len(self.constant_texts.page_kyc_details) else None
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=1*inch) if _wetsign_bytes else ''
        
        signature = pdf_components.boxed_sign_field(doc=doc,display_name=constant_texts.page12_signature_label,value=_client_sign,alpha=0.5,box_width=2.5*inch,box_height=1*inch)

        bottom_content = pdf_tables.create_composite_table(table1=Table([[client_name],[place],[date]]),table2=signature,col_widths=[(doc.width-doc.rightMargin*2)/2,20,None])
        bottom_content.setStyle(pdf_styles.padded_justified_table_style())
        return [page_heading,Spacer(0,10),page_subheading,Spacer(0,10),clauses,declaration_heading,Spacer(0,10),declaration_content,Spacer(0,5),bottom_content,PageBreak()]


    async def get_page13(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()
        pdf_colors = PdfColors()

        addressee = Paragraph(constant_texts.page13_addressee,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))
        subject1 = Paragraph(constant_texts.page13_subject1,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        body1 = Paragraph(constant_texts.page13_body1,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))

        _client_table_data1 = [[Paragraph(f'{cell}'.upper() if i==1 else cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=9, text_color=pdf_colors.filled_data_color if i==1 else pdf_colors.text_color)) for i, cell in enumerate(row)] for row in constant_texts.page13_client_signature_table1]
        
        _file_id = constant_texts.page_kyc_details[0].applicant_wet_sign_value if 0 < len(self.constant_texts.page_kyc_details) else None
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=0.5*inch) if _wetsign_bytes else ''
        _client_table_data1[1][1] = _client_sign

        client_name_signature_table1 = pdf_tables.create_table(data=_client_table_data1,style=pdf_styles.bordered_grid_table_style(alpha=0.5,h_margin=10,v_margin=5,styling_list=[('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),]),col_widths=[None,4*inch],row_heights=[None,50])

        subject2 = Paragraph(constant_texts.page13_subject2,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        body2_part1 = Paragraph(constant_texts.page13_body2_part1,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))

        settle_fund_duration_field = pdf_components.checkbox_field(doc=doc,field_name_text=constant_texts.page13_body2_settlement_field_label,options=constant_texts.page13_body2_settlement_field_options,selected_options=constant_texts.page13_body2_settlement_field_selected_options,field_width=(doc.width-doc.rightMargin*2))
        body2_part2 = Paragraph(constant_texts.page13_body2_part2,style=pdf_styles.normal_text_style(alignment=4,fontsize=9))

        _client_table_data2 = [[Paragraph(f'{cell}'.upper() if i==1 else cell,style=pdf_styles.normal_text_style(alignment=1,fontsize=9, text_color=pdf_colors.filled_data_color if i==1 else pdf_colors.text_color)) for i, cell in enumerate(row)] for row in constant_texts.page13_client_signature_table2]
        
        _client_table_data2[1][1] = _client_sign
        client_name_signature_table2 = pdf_tables.create_table(data=_client_table_data1,style=pdf_styles.bordered_grid_table_style(alpha=0.5,h_margin=10,v_margin=5,styling_list=[('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),]),col_widths=[None,4*inch],row_heights=[None,50])

        return [addressee,Spacer(0,10),subject1,Spacer(0,5),body1,Spacer(0,10),client_name_signature_table1,Spacer(0,10),subject2,Spacer(0,5),body2_part1,Spacer(0,5),settle_fund_duration_field,Spacer(0,5),body2_part2,Spacer(0,5),client_name_signature_table2,PageBreak()]

    async def get_page15(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        addressee = Paragraph(constant_texts.page15_letter_addressee,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))
        subject = Paragraph(constant_texts.page15_letter_subject,style=pdf_styles.bold_text_style(alignment=1,fontsize=9))
        body = Paragraph(constant_texts.page15_body_content,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))

        body_table = pdf_tables.create_table(data=constant_texts.page15_documents_table_data,col_widths=[inch,5*inch],style=pdf_styles.bordered_grid_table_style(h_margin=10,alpha=0.5,styling_list=[('FONTNAME', (0, 0), (-1, -1), 'LatoBold'),('ALIGN', (0, 0), (-1, -1), 'LEFT'),('ALIGN', (1, 0), (1, 0), 'CENTER')]))
        closing_declaration = Paragraph(constant_texts.page15_closing_declaration,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))

        name_field = pdf_components.get_text_field(doc=doc,field_name=constant_texts.page15_applicant_name_label,value=constant_texts.page15_applicant_name_value,width=(doc.width-doc.rightMargin*2))
        
        _file_id = constant_texts.page_kyc_details[0].applicant_wet_sign_value if 0 < len(self.constant_texts.page_kyc_details) else None
        _wetsign_bytes = await pdf_components.fetch_image_bytes(file_id=_file_id) if _file_id else None
        _client_sign = pdf_components.get_image_from_bytes(file_bytes=_wetsign_bytes,width=2*inch,height=1*inch) if _wetsign_bytes else ''
        
        
        signature = pdf_components.boxed_sign_field(doc=doc,display_name=constant_texts.page15_applicant_signature_label,value=_client_sign,alpha=0.5,box_width=2.5*inch,box_height=1*inch)

        return [addressee,Spacer(0,10),subject,Spacer(0,10),body,Spacer(0,10),body_table,Spacer(0,10),closing_declaration,Spacer(0,20),name_field,signature]