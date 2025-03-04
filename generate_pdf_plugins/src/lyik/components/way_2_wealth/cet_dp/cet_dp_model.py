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
from ...way_2_wealth.aof.aof_text_consts import AOFConstantTexts  # This should be from its own module, not from aof.
from ...components import PdfComponents, HorizontalLine

class CET_and_DP():
    def __init__(self) -> None:
        # self.constant_texts = ConstantTexts()
        pass
    def get_page1(self,doc):
        # constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        col = colors.black
        company_name = f'Way2Wealth Brokers Private Limited'
        address_text = 'Reg. Off: Rukmini Towers, 3rd & 4th Floor, # 3/1,Platform Road, Sheshadripuram<br/>Bangalore – 560020 | Ph: 080 - 43676869 &#9 Fax No.: 080 - 43676899'

        company_header_table = Table([[Paragraph(company_name,pdf_styles.bold_text_style(fontsize=14,alignment=0))],[Paragraph(text=address_text,style=pdf_styles.normal_text_style(alignment=0,fontsize=10))]])
        company_header_table.setStyle(pdf_styles.padded_table_style())

        small_logo = load_logo(width=2.5*inch)

        header = Table([[company_header_table,small_logo],[pdf_components.create_bordered_input_box(doc=doc,width=doc.width-doc.rightMargin*2,height=16,text_value='Application for Closure of Demat Account - NSDL / CDSL',text_style=pdf_styles.bold_text_style(alignment=1,fontsize=12))]], colWidths=[None,doc.width/3],style=pdf_styles.padded_justified_table_style())
        header.setStyle(pdf_styles.bordered_table_style(h_margin=8,v_margin=4))


        date = pdf_components.get_date_field(date='          ',display_name='Date:',font_size=9)
        client_id = pdf_components.get_tabular_field(display_name='Client id:',field_value=[c for c in '       '],font_size=9,text_style= pdf_styles.bold_text_style(alignment=0,fontsize=9))
        date_client_id = pdf_tables.create_composite_table(table1=date,table2=client_id,col_widths=[None,1,None])

        nsdl = pdf_components.get_tabular_field(display_name='NSDL',field_value=['IN','3','0','3','0','7','7'],cell_widths=[0.25*inch])
        cdsl = pdf_components.get_tabular_field(display_name='CDSL',field_value=['1','2','0','6','2','9','0','0'])
        tabular_field = pdf_tables.create_table(data=[['1','2','0','3','1','5','0','0']],col_widths=[0.2*inch],style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid for visibility
        ]))

        nsdl_cdsl_row = Table([[nsdl,Spacer(1,5),pdf_components.create_bordered_input_box(doc=doc,width=0.2*inch,height=0.2*inch),Spacer(1,5),cdsl,Spacer(1,5),pdf_components.create_bordered_input_box(doc=doc,width=0.2*inch,height=0.2*inch),Spacer(1,5),tabular_field,Spacer(1,5),pdf_components.create_bordered_input_box(doc=doc,width=0.2*inch,height=0.2*inch)]],style=pdf_styles.padded_justified_table_style())

        closure_checkbox_field = pdf_components.checkbox_field(doc=doc,field_name_text='Closure Initiated by',options=['BO','DP','Depository'],field_width=(doc.width-doc.rightMargin)*0.6)
        tradind_code = pdf_components.get_text_field(doc=doc,field_name='Trading Code',width=(doc.width-doc.rightMargin)*0.4)
        closure_trading_row = pdf_tables.create_composite_table(table1=closure_checkbox_field,table2=tradind_code,col_widths=[None,1,(doc.width-doc.rightMargin)*0.4])

        first_holder = pdf_components.get_text_field(doc=doc,field_name='Sole/ First Holder:',size=9,width= (doc.width - doc.rightMargin))
        second_holder = pdf_components.get_text_field(doc=doc,field_name='Second Holder:',size=9,width= (doc.width - doc.rightMargin))
        third_holder = pdf_components.get_text_field(doc=doc,field_name='Third Holder:',size=9,width= (doc.width - doc.rightMargin))
        address_for_correspondence = pdf_components.get_text_field(doc=doc,field_name='Address for Correspondence:',size=9,width= (doc.width - doc.rightMargin))

        consolidation_checkbox = pdf_components.checkbox_field(doc=doc,field_name_text='',options=['Consolidation of Accounts','Stopped trading','Relocation to abroad','Others (Please specify):'],field_width=(doc.width-doc.rightMargin)*0.75)
        other_text = pdf_components.create_u_shaped_input_box(width=(doc.width-doc.rightMargin)*0.25,height=0.2*inch,text='')
        consolidation_checkbox_row = pdf_tables.create_composite_table(table1=consolidation_checkbox,table2=other_text,col_widths=[None,1,(doc.width-doc.rightMargin)*0.25])

        options_table_row1 = pdf_components.get_checkbox_option(doc=doc,option_text='Option A(There are no balances/holdings in this account)')
        options_table_row2_cell1 = pdf_components.get_checkbox_option(doc=doc,option_text='Option B(Transfer the balances/holdings in this account as per details given)',width=1*inch)
        options_table_row2_cell2 = pdf_components.checkbox_field(doc=doc,field_name_text='',options=['Transfer to my/our own account (Provide target account details and enclode Client Master Report of Target Account)','Transfer to any other account (submit duly filled delivery Instruction Slipsigned by all holders)','Partly remateriliased and partly transferred'],field_width=(doc.width-doc.rightMargin*2)/3)

        cell3_data = [
            ['Target Account Details', '', '', '', '', '', '', '', '', '', '', ''],  # First 2 rows spanned
            ['', '', '', '', '', '', '', '', '', '', '', ''],
            ['NSDL','','DP ID', '', '', '', '', '', '', '', '', ''],  # 3rd row with first 2 cells spanned
            ['CDSL','', 'Client ID', '', '', '', '', '', '', '', '', ''],  # 4th row with first 2 cells spanned
            ['', '', '', '', '', '', '', '', '', '', '', '']  # Last row spanned
        ]
        options_table_row2_cell3 = Table(cell3_data,colWidths=[0.25*inch])
        options_table_row2_cell3.setStyle(TableStyle([
            ('SPAN', (0, 0), (-1, 1)),  # Span first 2 rows into one cell
            ('SPAN', (0, 2), (1, 2)),  # Span first 2 cells of 3rd row
            ('SPAN', (2, 2), (3, 2)),  # Span 3rd-4th cells of 3rd row
            ('SPAN', (0, 3), (1, 3)),  # Span first 2 cells of 4th row
            ('SPAN', (2, 3), (3, 3)),  # Span first 3rd-4th cells of 4th row
            ('SPAN', (0, 4), (-1, 4)),  # Span the entire last row
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),  # Add inner grid (optional)
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Middle vertical align text
        ]))
        row2 = Table([[options_table_row2_cell1,options_table_row2_cell2,options_table_row2_cell3]],colWidths=[1.2*inch,3*inch,None])
        row2.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('TOPPADDING', (1, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (1, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white), # Clear all borders first 
            ('LINEBEFORE', (1, 0), (-1, -1), 1, colors.black), # Add vertical lines 
            ('LINEAFTER', (0, 0), (-2, -1), 1, colors.black),
        ]))
        options_table_row3 = pdf_components.get_checkbox_option(doc=doc,option_text='Option C(Remateriliased/ ReconvertSubmit duly filled Remat/ Reconversion Request Form - for Mutual Funds Units))')


        options_table = Table([[options_table_row1],[row2],[options_table_row3]])
        options_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('TOPPADDING', (1, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (1, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        kindly_block_delivery_option = pdf_components.get_checkbox_option(doc=doc,option_text='Kindly block the Delivery Instruction book issued to me / us. I/we wish to confirm the same is misplaced.',bold=True,width=(doc.width-doc.rightMargin))


        middle_section = Table([
            [date_client_id],
            [nsdl_cdsl_row],
            [closure_trading_row],
            [Paragraph('I / We hereby request you to close my/our account with you as per following details:',style=pdf_styles.bold_text_style(fontsize=9,alignment=0))],
            [first_holder],
            [second_holder],
            [third_holder],
            [address_for_correspondence],
            [Paragraph('* Please tick the reason for closing the Demat Account :',style=pdf_styles.normal_text_style(fontsize=9,alignment=0))],
            [consolidation_checkbox_row],
            [Paragraph('* Please tick the applicable option(s): (*Marked is a Mandatory Field)',style=pdf_styles.normal_text_style(fontsize=9,alignment=0))],
            [options_table],
            [kindly_block_delivery_option],
            [Paragraph('Declaration: I / We declare and confirm that all the transactions in my/our demat account are true /authentic',style=pdf_styles.bold_text_style(fontsize=9,alignment=0))],

            
        ])
        middle_section.setStyle(pdf_styles.bordered_table_style(h_margin=8,v_margin=2))
        signature_section = Table([
            [pdf_components.signature_field(display_name='SIGNATURE OF SOLE/FIRST HOLDER',width=2*inch,alignment=1,fontsize=9),
            pdf_components.signature_field(display_name='SIGNATURE OF SECOND HOLDER',width=2*inch,alignment=1,fontsize=9),
            pdf_components.signature_field(display_name='SIGNATURE OF THIRD HOLDER',width=2*inch,alignment=1,fontsize=9),
            ]
        ])
        signature_section.setStyle(pdf_styles.bordered_table_style(h_margin=10,v_margin=10))

        
        branch_details_text = Paragraph('Branch Details:', style=pdf_styles.bold_text_style(fontsize=9,alignment=0))
        branch_name_field = pdf_components.get_text_field(doc=doc,field_name='Branch Name',width=(doc.width-doc.rightMargin)/3)
        branch_name_row = pdf_tables.create_composite_table(table1=branch_details_text,table2=branch_name_field,col_widths=[None,1,(doc.width-doc.rightMargin)/3])

        reg_no_row = pdf_tables.create_composite_table(table1=pdf_components.get_text_field(doc=doc,field_name='R M Name Reg No:',width=(doc.width-doc.rightMargin)/3),table2=pdf_components.get_text_field(doc=doc,field_name='Contact No.:',width=(doc.width-doc.rightMargin)*0.25),col_widths=[(doc.width-doc.rightMargin)/3,1,None])
        clousure_approved_by_cell = Table([[Paragraph('Closure Approved By:',style=pdf_styles.normal_text_style(alignment=0,fontsize=9)),Paragraph('Name:',style=pdf_styles.normal_text_style(alignment=0,fontsize=9),)],['',pdf_components.get_text_field(doc=doc,field_name='Signature:',width=(doc.width-doc.rightMargin)*0.25)]],colWidths=[None,(doc.width-doc.rightMargin)*0.3])
        clousure_approved_by_cell.setStyle(
            [
                ('SPAN', (0, 0), (0, 1)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (1,0), (1, 0), 1, colors.white),
            ]
        )

        branch_details_section = Table([[branch_name_row,clousure_approved_by_cell],[reg_no_row,'']])
        branch_details_section.setStyle([
            ('SPAN', (1, 0), (1, 1)),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ])

        data = [
            ['Processed By:', '', 'Verified By:', '', 'DPM Ref No.', 'SI Code:      ', 'Ledger Balances', 'Trading A/C:       '],
            ['', '', '', '', '', 'CI Code       ', '', 'Demat A/C:       ']
        ]
        processed_by_table = Table([[Paragraph(cell, pdf_styles.normal_text_style(fontsize=9)) if cell else '' for cell in row] for row in data])
        # Define a style with cell spanning and grid lines
        style = TableStyle([
            ('SPAN', (0, 0), (0, 1)),
            ('SPAN', (1, 0), (1, 1)),  
            ('SPAN', (2, 0), (2, 1)),  
            ('SPAN', (3, 0), (3, 1)),  
            ('SPAN', (4, 0), (4, 1)), 
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Apply grid lines to all cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle vertical align text
        ])

        # Apply the style to the table
        processed_by_table.setStyle(style)

        for_office_table = Table([[
            Paragraph('For Office Use:',style=pdf_styles.bold_text_style(fontsize=9,alignment=0)), 
            Table([[
                Paragraph('Balance Present in account for (To be filled by DP, if applicable)',style=pdf_styles.normal_text_style(fontsize=9))
                ],
                [
                    pdf_components.checkbox_field(doc=doc,field_name_text='',options=['Ear-Marked','Pledged', 'Frozen','Pendinf for Demat', 'Pending for Remat', 'Lock-in'],field_width=doc.width-doc.rightMargin)
                ]
            ])
        ]],colWidths=[1.2*inch,None])
        for_office_table.setStyle(
            pdf_styles.padded_justified_table_style()
        )

        for_office_use_section = Table([[for_office_table],[processed_by_table]])
        for_office_use_section.setStyle(
            pdf_styles.bordered_table_style(h_margin=10,v_margin=5)
        )

        ack_dp_id = pdf_components.get_tabular_field(display_name='DP ID',field_value=[c for c in '        '],font_size=9,text_style= pdf_styles.bold_text_style(alignment=0,fontsize=9))
        ack_cleint_id = pdf_components.get_tabular_field(display_name='Client id',field_value=[c for c in '        '],font_size=9,text_style= pdf_styles.bold_text_style(alignment=0,fontsize=9))

        ack_dp_client_id = pdf_tables.create_composite_table(table1=ack_dp_id,table2=ack_cleint_id,col_widths=[None,1,None])

        ack_first_holder = pdf_components.get_text_field(doc=doc,field_name='Sole/ First Holder:',size=9,width= (doc.width - doc.rightMargin))
        ack_second_holder = pdf_components.get_text_field(doc=doc,field_name='Second Holder:',size=9,width= (doc.width - doc.rightMargin))
        ack_third_holder = pdf_components.get_text_field(doc=doc,field_name='Third Holder:',size=9,width= (doc.width - doc.rightMargin))

        date_seal_row = Table([
            [
                Paragraph('Date',style=pdf_styles.bold_text_style(alignment=0,fontsize=9)),
                '',
                Paragraph('Seal/ Stamp of Participant',style=pdf_styles.bold_text_style(alignment=0,fontsize=9)),
                ''
            ]
        ],
        colWidths=[inch,(doc.width-doc.rightMargin)*0.5,2*inch,None],
        style=pdf_styles.padded_justified_table_style())

        note_text = '''Note:<br/>
        Please submit latest self attested holding statement in case of closure-cum-transfer along with the form.
        If Unused DIS is misplaced/lost, please tick the above declaration and submit self attested ID proof  along with the form.'''
        note_section = pdf_components.create_bordered_input_box(doc=doc,width=(doc.width-doc.rightMargin),text_value=note_text,text_size=7,height=0.5*inch)

        acknowledgement_section = Table([
            [Paragraph('Acknowledgement',style=pdf_styles.bold_text_style(fontsize=9))],
            [Paragraph('We hereby acknowledge the receipt of your request for closing the following Account subject to verification',style=pdf_styles.normal_text_style(fontsize=9,alignment=0))],
            [ack_dp_client_id],
            [ack_first_holder],
            [ack_second_holder],
            [ack_third_holder],
            [Paragraph('Signature of the Authorised Signatory',style=pdf_styles.bold_text_style(fontsize=9,alignment=1))],
            [Spacer(0,10)],
            [date_seal_row]
        ],style=pdf_styles.bordered_table_style(h_margin=10,v_margin=2))
        



        
        return [header,middle_section,signature_section,branch_details_section,for_office_use_section,note_section,PageBreak(),acknowledgement_section,PageBreak()]
    

    def get_page2(self,doc):
        constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        
        logo = Table([[Spacer(doc.width-doc.rightMargin*2-2.5*inch,0),load_logo(width=2.5*inch)]],colWidths=[None,2.5*inch])
        logo.setStyle(
            [
                 ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ]
        )
        heading = Paragraph('Request for Closure of Trading Account',pdf_styles.bold_text_style(fontsize=9,alignment=1))
        date = '____/____/________'
        branch = '______________________________'
        letter_head = '''<br/>
        Date: {date}<br/><br/>
        Branch: {branch}<br/><br/>
        To,<br/>
        The Manager,<br/>
        Client Registration Department,<br/>
        Way2wealth Brokers Private Limited,<br/>
        Reg. Off: Rukmini Towers, 3rd & 4th Floor,<br/>
        # 3/1,Platform Road, Sheshadripuram<br/>
        Bangalore – 560020<br/><br/>
        Dear Sir,<br/><br/>
        I/We hereby request you to close my/our Trading account with you with following account details. <br/><br/>
        '''.format(date=date, branch=branch)
        head = Paragraph(letter_head,style=pdf_styles.normal_text_style(fontsize=9,alignment=0))

        client_name = pdf_components.get_boxed_field(doc,display_name="Client Name")

        tradinf_ac_no = pdf_components.get_boxed_field(doc,display_name="Trading A/C No",total_width=(doc.width-doc.rightMargin)/2)

        reason_of_closure = pdf_components.get_boxed_field(doc,display_name="Reason Of Closure:",field_height=inch)

        body_declaration = '''<br/>
        I declare and confirm that all the transactions in my trading account are true /authentic and I do
        not have any grievances / complaints with Way2wealth Brokers Private Limited with regard to
        transactions in my trading account”<br/><br/>
        Yours truly,
        '''
        body_dec = Paragraph(body_declaration,style=pdf_styles.normal_text_style(alignment=0,fontsize=9))

        sign_field = pdf_components.boxed_sign_field(doc=doc,display_name='Client Signature',box_width=2*inch,alignment=0,alpha=0.5,fontsize=9)

        data = [
            ['Branch Stamp:', 'Particulars of Employee accepting the request', '', 'Entered By:'],
            ['', 'Name:', '', ''],
            ['', 'Emp id:', '', ''],
            ['', 'Designation:', '', 'Verified By:'],
            ['', 'Signature:', '', '']
        ]

        bottom_section_heading = pdf_tables.create_composite_table(table1=Paragraph('To Be filled by Branch',style=pdf_styles.bold_text_style(alignment=0,fontsize=8)),table2=Paragraph('For Head office',style=pdf_styles.normal_text_style(alignment=0,fontsize=8)),col_widths=[2*inch,None,1.2*inch])        
        bottom_section = Table([[Paragraph(cell, pdf_styles.normal_text_style(alignment=0,fontsize=9)) if cell else '' for cell in row] for row in data], colWidths=[1.5*inch, None, None, 1.5*inch],rowHeights=[None,None,None,None,0.5*inch]) 

        # Define a style with cell spanning and grid lines
        bottom_table_style = TableStyle([
            ('SPAN', (0, 0), (0, 4)),
            ('SPAN', (3, 0), (3, 2)), 
            ('SPAN', (3, 3), (3, 4)),  
            ('SPAN', (1, 0), (2, 0)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Apply grid lines to all cells
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])

        # Apply the style to the table
        bottom_section.setStyle(bottom_table_style)

        page_table = Table([[logo],[heading],[head],[client_name],[tradinf_ac_no],[reason_of_closure],[body_dec],[sign_field],[HorizontalLine(width=doc.width-doc.rightMargin*2,thickness=2)],[bottom_section_heading],[bottom_section]])
        page_table.setStyle(pdf_styles.padded_table_style(top=5,bottom=5,left=20,right=20))

        return [page_table]

