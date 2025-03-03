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
from ...way_2_wealth.aof.aof_text_consts import AOFConstantTexts # This should be from its own module, not from aof.
from ...components import PdfComponents, HorizontalLine

class DDPI():
    def __init__(self) -> None:
        # self.constant_texts = ConstantTexts()
        pass
    def get_page1(self,doc):
        # constant_texts = self.constant_texts
        pdf_styles = PdfStyles()
        pdf_tables = PdfTables()
        pdf_components = PdfComponents()

        col = colors.black

        date = '____/____/________'
        account_num = "_________________________________"


        letter_text = '''
        Date: {date}<br/><br/>
        To<br/><br/>
        DP Operations<br/>
        Way2Wealth Brokers Private Limited<br/>
        Reg. office: Rukmini Towers,<br/>
        3rd & 4th Floor, # 3/1, Platform Road,<br/>
        Sheshadripuram, Bangalore - 560 020<br/><br/>
        Dear Sir,<br/><br/>
        {tab}Sub: Updation of DDPI<br/><br/>
        {tab}Ref: DP-Client Account No. {account_num}<br/><br/>
        With reference to the above, please find enclosed the DDPI document duly signed. Kindly update the same in your records and request you to execute the instructions given by me/us.<br/><br/>
        Thanking you.<br/>
        Yours truly,
        '''.format(account_num=account_num,date=date,tab='&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')

        let = Paragraph(letter_text,style=pdf_styles.normal_text_style(fontsize=9,alignment=0))

        sign_table = Table([['Name:','Name:','Name:'],[]])

        data = [
            [Paragraph('Name:', pdf_styles.normal_text_style(alignment=0,fontsize=9)), Paragraph('Name:', pdf_styles.normal_text_style(alignment=0,fontsize=9)), Paragraph('Name:', pdf_styles.normal_text_style(alignment=0,fontsize=9))],
            [Paragraph('1st Holder Signature', pdf_styles.normal_text_style(alignment=1,fontsize=9)), Paragraph('2nd Holder Signature', pdf_styles.normal_text_style(alignment=1,fontsize=9)), Paragraph('3rd Holder Signature', pdf_styles.normal_text_style(alignment=1,fontsize=9))]
        ]

        # Create a table with the specified row heights and column widths
        table = Table(data, rowHeights=[0.5*inch, 1.2*inch])

        # Define a style with grid lines
        table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Apply grid lines to all cells
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),  # Top vertical align for the first row
            ('VALIGN', (0, 1), (-1, 1), 'BOTTOM'),  # Bottom vertical align for the second row
        ])

        # Apply the style to the table
        table.setStyle(table_style)

        return [let,Spacer(0,30),table]
    
