from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from .styles import PdfStyles


class PdfTables:
    def create_table(self, data:list,col_widths,style:TableStyle,row_heights=None):
        table = Table(data,colWidths=col_widths,rowHeights=row_heights,style=style)
        return table

    def create_composite_table(self, table1, table2,col_widths):
        return Table([[table1, Spacer(0.1 * inch, 0), table2]], colWidths=col_widths,style=PdfStyles().padded_table_style(), rowHeights=[None])
    
    def create_headered_table(self, table_body:Table, header_text='', header_color=colors.white):
        """
        Create a table of 2 x 1, first rows having header
        """
        
        table = Table([[Paragraph(text=header_text, style=PdfStyles().bold_text_style())],[table_body]])
        table.setStyle(PdfStyles().headered_table_style(header_color=header_color))

        return table