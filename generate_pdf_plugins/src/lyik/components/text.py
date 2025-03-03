from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageTemplate, Frame, Paragraph, PageBreak, Spacer, TableStyle, Table, BaseDocTemplate
from .styles import PdfStyles



def get_text(text:str,text_style:ParagraphStyle=None):
    return Paragraph(text,text_style if text_style else PdfStyles().normal_text_style())

