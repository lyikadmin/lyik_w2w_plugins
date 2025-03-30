from reportlab.platypus import Table, Paragraph, Flowable,TableStyle, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, A4
from .styles import PdfStyles
from .tables import PdfTables
from reportlab.pdfbase import pdfmetrics
import os
from reportlab.lib.utils import ImageReader
import importlib
from io import BytesIO
from .colors import PdfColors
import logging
logger = logging.getLogger(__name__)



class HorizontalLine(Flowable):
    def __init__(self, width=400, thickness=1, color=colors.black, alignment='left', margin=1*inch):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.alignment = alignment
        self.margin = margin

    def draw(self):
        # Determine x-coordinate based on alignment
        if self.alignment == 'center':
            x_start = (self.canv._pagesize[0] - self.width - self.margin) / 2
        elif self.alignment == 'right':
            x_start = self.canv._pagesize[0] - self.width
        else:  # default to left
            x_start = 0

        # Draw the line
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(x_start, 0, x_start + self.width, 0)


class HintText(Flowable):
    def __init__(self, text, hint_text_color=colors.lightgrey):
        Flowable.__init__(self)
        self.text = text
        self.hint_text_color = hint_text_color

    def draw(self):
        if self.text.isdigit():
            self.canv.setFillColor(colors.black)
        else:
            self.canv.setFillColor(self.hint_text_color)
        self.canv.drawString(0, 0, self.text)

class BorderedInputBox(Flowable):
    def __init__(self, width, text, height=0.3*inch,image_bytes:str | bytes=None,text_size:int=8,text_style=None,box_color=colors.white,alpha=1):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.text = text
        self.image_bytes = image_bytes
        self.alpha = alpha
        self.text_size=text_size
        self.text_style = text_style
        self.box_color = box_color

    def draw(self):
        # Save current canvas state
        self.canv.saveState()

        # Set the fill and stroke color for the box
        self.canv.setFillColor(self.box_color)
        self.canv.setStrokeColor(colors.black, alpha=self.alpha)
        
        # Draw the rectangle (bordered box)
        self.canv.rect(0, 0, self.width, self.height, fill=1)

        img = PdfComponents().get_image_from_bytes(file_bytes=self.image_bytes,width=self.width-2,height=self.height-2) if self.image_bytes else None
        if img:
            img.drawOn(self.canv, 1, 1)
        else:
            # Create a Paragraph object for the text
            text_paragraph = Paragraph(self.text, 
                                    self.text_style if self.text_style else PdfStyles().normal_text_style(fontsize=self.text_size))
            
            # Wrap the text to fit within the box width
            text_width, text_height = text_paragraph.wrap(self.width - 2, self.height - 2)

            # Calculate vertical center offset for the text
            y_offset = (self.height - text_height) / 2

            # Draw the text inside the box
            text_paragraph.drawOn(self.canv, 2, y_offset)

        # Restore the canvas state
        self.canv.restoreState()


class PdfComponents:
    def create_bordered_input_box(self,doc,width, height=0.3*inch,image_bytes: str| bytes=None, text_value='',text_size=8,text_style=None,box_color=colors.white,alpha=1):
        """Create an input box with a specified width and height, and optional initial text."""
        
        return BorderedInputBox(width=width,height=height,image_bytes=image_bytes,text=text_value,text_size=text_size,text_style=text_style,box_color=box_color,alpha=alpha)
        


    def create_u_shaped_input_box(self, width, height=0.3*inch, text='', text_style=None, text_size=8):
        """Create an input 'u' shape box with a specified width and height, and optional initial text."""
        # Ensure a style exists
        styles = getSampleStyleSheet()
        text_style = text_style if text_style else PdfStyles().normal_text_style(alignment=0, fontsize=text_size,text_color=PdfColors().filled_data_color)

        # Create a Paragraph object for the text
        text_paragraph = Paragraph(text.upper(), text_style)

        # Create a Table with one cell to contain the Paragraph
        cell_content = [[text_paragraph]]
        table = Table(cell_content, colWidths=[width], rowHeights=[height])

        # Apply styles to create the U-shaped box
        table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
            ('LINEBEFORE', (0, 0), (0, 0), 0.5, colors.black),
            ('TOPPADDING', (0, 0), (0, 0), 2),
            ('BOTTOMPADDING', (0, 0), (0, 0), 2),
            ('LEFTPADDING', (0, 0), (0, 0), 2),
            ('RIGHTPADDING', (0, 0), (0, 0), 2),
        ]))

        return table

    def get_checkbox_option(self,doc,option_text='', filled=False, size=8, bold=False, width=None):
        pdf_styles = PdfStyles()
        text = Paragraph(option_text,style=pdf_styles.bold_text_style(fontsize=size,alignment=0) if bold else pdf_styles.normal_text_style(fontsize=size,alignment=0))
        option_text_size = pdfmetrics.stringWidth(option_text, 'Lato', size) if width is None else width
        _table1 = self.create_bordered_input_box(doc, width=size+1,height=size+1,text_value=f'<font name="ZapfDingbats" color={PdfColors().filled_data_color}>✓</font>' if filled is True else '')

        table = PdfTables().create_composite_table(table1=_table1,table2=text,col_widths=[size,4,option_text_size])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0)
        ]))
        return table

    def get_checkbox_option_with_other(self,doc,option_text='Other', filled=False, size=8, bold=False, other_width=inch, other_value=None):
        other_value_box = self.create_u_shaped_input_box(width=other_width,text='',height=0.2*inch)
        option_text_size = pdfmetrics.stringWidth(option_text, 'Lato', size)

        table = Table([[self.create_bordered_input_box(doc,width=size,height=size,),Paragraph(option_text,style=PdfStyles().bold_text_style(fontsize=size-2) if bold else None),other_value_box]], colWidths=[size+10,option_text_size+10,other_width])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (-1, -1), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0)
        ]))
        return table

    def checkbox_field(self,doc,field_name_text:str, field_width:int, options:list[str],selected_options:list[str]=[],size=8, display_name_width=None):
        """
        TEST AND FIX LOGIC FOR LONG FIELDS AND OUT OF BOUND RENDERING
        """
        field_name = Paragraph(field_name_text,style=PdfStyles().normal_text_style(fontsize=size)) if field_name_text is not None else Spacer(0,0)
        # Calculate width
        field_name_width = display_name_width if display_name_width is not None else (pdfmetrics.stringWidth(field_name_text, 'Lato', size)+5) if field_name_text is not None else 0
        
        rendered_options_table = self.create_dynamic_checkbox_table(doc=doc,max_width=field_width-field_name_width,options=options,size=size,selected_options=selected_options)

        field = Table([[field_name,rendered_options_table]],colWidths=[field_name_width,field_width-field_name_width])
        field = PdfTables().create_composite_table(table1=field_name,table2=rendered_options_table, col_widths=[field_name_width,1,None])
        field.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2)
        ]))

        return field

    def create_dynamic_checkbox_table(self,doc,max_width:int,options:list[str],size=8,selected_options:list[str]=[]): 
        table_data = []
        col_widths = []
        row = []
        current_width = 0

        for option in options:
            option_text_size = pdfmetrics.stringWidth(option, 'Lato', size)
            total_size = option_text_size + 20  # Adding padding and checkbox size

            if total_size > max_width:  # If single option exceeds max width, wrap text within cell
                text_style = ParagraphStyle(
                    name='Normal',
                    parent=getSampleStyleSheet()['Normal'],
                    alignment=4,
                    fontSize=size
                )
                wrapped_text = Paragraph(option, text_style)
                wrapped_text.wrap(max_width-16, 0.3*inch)  # Wrap within cell width
                
                tab = Table([[BorderedInputBox(width=10, height=10,text=f'<font name="ZapfDingbats" color={PdfColors().filled_data_color}>✓</font>' if option.lower() in [opt.lower() for opt in selected_options] else ''), wrapped_text]],colWidths=[16,max_width+10])
                tab.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                row.append(tab)
                table_data.append(row)
                col_widths.append(max_width+26)
                row = []
                current_width = 0
            else:
                if current_width + total_size > max_width:
                    table_data.append(row)
                    row = []
                    current_width = 0
                
                row.append(self.get_checkbox_option(doc,option_text=option,size=size,filled=option.lower() in [opt.lower() for opt in selected_options]))
                col_widths.append(total_size+26)
                current_width += total_size
        
        if row:
            table_data.append(row)
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        return table



    def get_text_field(self,doc,field_name, value=None, size=8, bold=False, width=inch):
        _field_name = Paragraph(field_name,style=PdfStyles().normal_text_style(fontsize=size))
        # Calculate width
        field_name_width = pdfmetrics.stringWidth(field_name, 'Lato', size)

        value_box = self.create_u_shaped_input_box(width=width -field_name_width-10,text=value if value else '',height=0.18*inch)
        field = Table([[_field_name,value_box]],colWidths=[field_name_width+5,width-field_name_width-5])
        field.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]))

        return field
    

    def get_multiline_text(self, doc, lines=1, width=inch, text='',text_style=None,text_size=8):
        table = []
        
        # Split the text into lines that fit within the width of the input box
        words = text.split()
        current_line = ""
        all_lines = []
        
        for word in words:
            temp_line = current_line + word + " "
            if pdfmetrics.stringWidth(temp_line, 'Lato', 10) <= width - 4:
                current_line = temp_line
            else:
                all_lines.append(current_line.strip())
                current_line = word + " "
        
        # Append the last line
        if current_line:
            all_lines.append(current_line.strip())
        
        # Combine remaining text if it exceeds the number of lines 
        if len(all_lines) > lines: 
            combined_text = ' '.join(all_lines[lines-1:lines+1]) +  (' ...' if len(all_lines)>lines+1 else '')
            all_lines = all_lines[:lines-1] 
            all_lines.append(combined_text)
        
        # Fill the lines into the table rows
        for i in range(lines):
            if i < len(all_lines):
                line_text = all_lines[i]
            else:
                line_text = ""
            
            input_box = self.create_u_shaped_input_box(width=width, height=0.2*inch, text=line_text,text_style=text_style,text_size=text_size)
            table.append([input_box])
            table.append([Spacer(1, 1)])
        
        return Table(table, style=PdfStyles().padded_table_style())

    
    def get_date_box(self,date:str="DD/MM/YYYY"):
        data_values = [char if char else "" for char in date]  # Use characters from the string

        # Create a table for the date with hint text
        date_cells = [HintText(data) for data in data_values]  # Create HintText for each character
        date_table = Table([date_cells], colWidths=[0.2*inch] * 10, rowHeights=[0.25*inch])

        # Set table style
        date_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid for visibility
        ]))
        return date_table
    
    def get_date_field(self, date:str="DD/MM/YYYY",display_name:str='Date',font_size=8):
        _field_name = Paragraph(display_name,style=PdfStyles().normal_text_style(fontsize=font_size))
        # Calculate width
        field_name_width = pdfmetrics.stringWidth(display_name, 'Lato', fontSize=font_size)
        date_box = self.get_date_box(date=date)

        field = Table([[_field_name,date_box]],colWidths=[field_name_width+10,None])
        field.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        return field
    
    
    def get_tabular_field(self,display_name,field_value:list[str],font_size=8,text_style=None,cell_widths=[0.2*inch]):
        _field_name = Paragraph(display_name,style=text_style if text_style else PdfStyles().normal_text_style(fontsize=font_size))
        # Calculate width
        field_name_width = pdfmetrics.stringWidth(display_name, 'Lato', fontSize=font_size)
        num_of_boxes = len(field_value)

        # Create a table for the date with hint text
        field_cells = [c for c in field_value]  # Create HintText for each character
        field_table = PdfTables().create_table(data=[field_cells],col_widths=cell_widths,style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Grid for visibility
        ]))

        field = Table([[_field_name,field_table]],colWidths=[field_name_width+10,None])
        field.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        return field
    
    def get_boxed_field(self,doc,display_name,total_width=None,display_box_width=None,field_value='', style=None,font_size=9, field_height = None):

        field_name_width = pdfmetrics.stringWidth(display_name, 'Lato', fontSize=font_size)
        if display_box_width is None:
            display_box_width = field_name_width
        table = Table([[Paragraph(display_name,style=style if style else PdfStyles().normal_text_style(fontsize=font_size)),Paragraph(field_value,style=style if style else PdfStyles().normal_text_style(fontsize=font_size))]],colWidths=[display_box_width+10, total_width-display_box_width-10 if total_width else None],rowHeights=[field_height])
        table.setStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ])
        return table


    
    # Helper function to insert an image from local file
    def load_local_image(self,wt,image_dir, file_name, ht=None):
        """ Insert an image as a full page. """
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # full_path = os.path.join(current_dir, image_path)

        with importlib.resources.path(image_dir,file_name) as img_path:
            img = ImageReader(img_path)
            img_w, img_h = img.getSize()
            # logger.debug(f"A4 height: {A4[1]}, width: {A4[0]}")
            # logger.debug(f"Image height: {img_h}, width: {img_w}")
            return Image(img_path, width=wt, height=ht if ht else img_h * wt / img_w)
    

    def signature_field(self,display_name,width=3*inch, value=None,alignment=0,fontsize = 10):
        filled_value = value if value is not None else Spacer(10,width)
        table = Table([[filled_value],[Paragraph(display_name,style=PdfStyles().normal_text_style(alignment=alignment, fontsize=fontsize))]],colWidths=[width], rowHeights=[0.5*inch, 20])
        table.setStyle([
            ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Clear all borders first
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Horizontal line below the first row
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Middle vertical align text
            
        ])
        return table
    
    def boxed_sign_field(self,doc,display_name, value=None,alignment=0,fontsize = 10,alpha:float=1, box_width=2*inch,box_height=0.5*inch):
        sign_box = Table([[Paragraph('x',style=PdfStyles().bold_text_style(alignment=0,fontsize=9))],[value if value is not None else '']],rowHeights=[None,box_height-5],colWidths=[box_width])
        sign_box.setStyle([
            ('BOX', (0, 0), (-1, -1), alpha, colors.black),

        ])
        sign_text = Paragraph(display_name,style=PdfStyles().normal_text_style(alignment=alignment,fontsize=fontsize))

        table = Table([[sign_box],[sign_text]])
        table.setStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER' if alignment==1 else 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ])
        return table
    
    async def fetch_image_bytes(self,file_id:str):
        from ..pdf_utilities.utility import fetchFileBytes
        return await fetchFileBytes(file_id=file_id)
    
    def get_image_from_bytes(self, file_bytes:bytes,width, height=None):
        """
        Resizes an image to fit within the specified width and height while maintaining its aspect ratio.

        Args:
            file_bytes (bytes): The image in bytes.
            width (float): The available width for the image.
            height (float): The available height for the image.

        Returns:
            Image: A resized ReportLab Image flowable.
        """
        try:
            image_stream = BytesIO(file_bytes)
            ir = ImageReader(image_stream)
            img_w, img_h = ir.getSize()

            # Calculate scaling factors for width and height
            width_scale = width / img_w
            height_scale = (height / img_h) if height else width_scale

            # Use the smaller scale to maintain aspect ratio and fit within the bounds
            scale = min(width_scale, height_scale)

            # Calculate the resized dimensions
            resized_width = img_w * scale
            resized_height = img_h * scale

            # Create and return the Image flowable
            img = Image(image_stream, width=resized_width-2, height=resized_height-2)
            return img
        except Exception as e:
            logger.debug(f"Error creating image: {str(e)}")
            return ''
