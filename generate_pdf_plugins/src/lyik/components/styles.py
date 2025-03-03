import importlib.resources
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import importlib

# TEXT and TABLE STYLES
class PdfStyles:

    styleSheet = getSampleStyleSheet() 
   
    with importlib.resources.path('lyik.components','lato_bold.ttf') as lato_bold_path:
        pdfmetrics.registerFont(TTFont('LatoBold', lato_bold_path))

    with importlib.resources.path('lyik.components','lato_regular.ttf') as lato_regular_path:
        pdfmetrics.registerFont(TTFont('Lato', lato_regular_path))
    
    # Modify the default 'BodyText' style to use a different font and size 
    defaultStyle = styleSheet['BodyText']
    defaultStyle.fontName = 'Lato' 
    defaultStyle.fontSize = 12

    def get_preformatted_style(self):
        return ParagraphStyle(name='Preformatted', fontSize=10, leading=12, parent=self.defaultStyle)

    def bold_text_style(self,alignment=1, fontsize=12,text_color=colors.black, leading=12,indent=0):
        return ParagraphStyle(parent=self.defaultStyle,name='bold_text', fontName='LatoBold', alignment=alignment, fontSize=fontsize,textColor=text_color, leading=fontsize,spaceAfter=0,spaceBefore=0,leftIndent=indent,rightIndent=indent,firstLineIndent=0)

    def normal_text_style(self,fontsize=12, alignment=0,indent=0,text_color=colors.black):
        return ParagraphStyle(parent=self.defaultStyle,name='normal',textColor=text_color, alignment=alignment, fontSize=fontsize,spaceAfter=0,spaceBefore=0,leading=fontsize,leftIndent=indent,rightIndent=indent,firstLineIndent=0)   



    # TABLE STYLES
    def padded_table_style(self,top=0,bottom=0,right=0,left=0):
        return TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), top),
            ('BOTTOMPADDING', (0, 0), (-1, -1), bottom),
            ('LEFTPADDING', (0, 0), (-1, -1), left),
            ('RIGHTPADDING', (0, 0), (-1, -1), right),
        ]) 

    def padded_justified_table_style(self,top=0,bottom=0,right=0,left=0):
        return TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), top),
            ('BOTTOMPADDING', (0, 0), (-1, -1), bottom),
            ('LEFTPADDING', (0, 0), (-1, -1), left),
            ('RIGHTPADDING', (0, 0), (-1, -1), right),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, 0), 'TOP'),
        ]) 
    
    def headered_table_style(self,header_color=colors.white):
        return TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), header_color),

        ]) 
    
    def bordered_table_style(self, h_margin=0, v_margin=0,styling_list=[],alpha=1):
        list= [
            ('TOPPADDING', (0, 0), (-1, -1), v_margin),
            ('BOTTOMPADDING', (0, 0), (-1, -1), v_margin),
            ('LEFTPADDING', (0, 0), (-1, -1), h_margin),
            ('RIGHTPADDING', (0, 0), (-1, -1), h_margin),
            ('BOX', (0, 0), (-1, -1), alpha, colors.black),
        ]
        list.extend(styling_list)
        return TableStyle(list)
    
    def bordered_grid_table_style(self, h_margin=0, v_margin=0,styling_list = [],alpha=1):
        list = [
            ('TOPPADDING', (0, 0), (-1, -1), v_margin),
            ('BOTTOMPADDING', (0, 0), (-1, -1), v_margin),
            ('LEFTPADDING', (0, 0), (-1, -1), h_margin),
            ('RIGHTPADDING', (0, 0), (-1, -1), h_margin),
            ('BOX', (0, 0), (-1, -1), alpha, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), alpha, colors.black)
            
        ]
        list.extend(styling_list)
        return TableStyle(list)


