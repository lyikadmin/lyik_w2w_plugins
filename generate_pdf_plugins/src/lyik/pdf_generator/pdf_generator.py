from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate,PageTemplate, Frame, Image, PageBreak,Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import logging
from ..components.way_2_wealth.aof.aof_model import AOF
from ..components.way_2_wealth.aof.aof_individual.aof_ind_model import AOF_IND
from ..components.way_2_wealth.cet_dp.cet_dp_model import CET_and_DP
from ..components.way_2_wealth.ddpi.ddpi_model import DDPI
from ..components.components import PdfComponents, PdfTables, PdfStyles
from ..pdf_utilities.utility import get_all_file_ids, merge_pdf_attachment

logger = logging.getLogger(__name__)
# def create_document(filename, buffer):
#     doc = BaseDocTemplate(buffer, pagesize=A4,
#                           leftMargin=0.5 * inch, rightMargin=0.5 * inch,
#                           topMargin=0.5 * inch, bottomMargin=0.5 * inch)
#     return doc

def create_document(filename:str,author:str=None):
    # Todo: Make filename to filename.split('/')[-1] to get only the filename
    doc = BaseDocTemplate(filename=filename,pagesize=A4,
                          leftMargin=0.25 * inch, rightMargin=0.25 * inch,
                          topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                          title=filename.split('/')[-1],
                          creator='Way2Wealth Brokers Private Limited',
                          subject='',
                          author= author if author else '',
                          producer='LYIK Technologies Pvt Ltd'
                          )
    return doc


class PdfGenerator():

    # def first_page_layout(self,canvas, doc): 
    #     canvas.saveState() # Custom layout or header/footer for the first page 
    #     canvas.restoreState() 
    # def subsequent_page_layout(self,canvas, doc): 
    #     canvas.saveState() # Custom layout or header/footer for subsequent pages 
    #     canvas.restoreState()


    def create_page_template(self,doc):
        # frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame1')
        frame = Frame(0.25*inch, 0.25*inch, doc.width, doc.height+0.25*inch, id='frame1')
        # page_template = PageTemplate(id='FirstPage', frames=[frame],onPage=self.first_page_layout)
        page_template = PageTemplate(id='FirstPage', frames=[frame])

        doc.addPageTemplates([page_template])

    def create_subsequent_page_template(self,doc,margin=0.1*inch):
        """Create the subsequent page of the document."""
        frame = Frame(margin, margin, doc.width - 2 *margin, doc.height - 2 *margin, id='frame2')
        # page_template = PageTemplate(id='SubsequentPages', frames=[frame],onPage=self.subsequent_page_layout)
        page_template = PageTemplate(id='SubsequentPages', frames=[frame])
        doc.addPageTemplates([page_template])
 
    async def generate_aof(self,pdf_path:str, data:dict, author:str=''):

        aof = AOF(data=data)
        pdf_components = PdfComponents()
        pdf_tables = PdfTables()
        pdf_styles = PdfStyles()

        doc = create_document(pdf_path,author=author)
        # doc = create_document(pdf_name,author=data.get('submitter',{}).get('id',''))
        
        # Get default stylesheet and modify the default style 
        styleSheet = getSampleStyleSheet() 
    
        # Modify the default 'BodyText' style to use a different font and size 
        defaultStyle = styleSheet['BodyText'] 
        defaultStyle.fontName = 'Courier' 
        defaultStyle.fontSize = 12

        self.create_page_template(doc)
        self.create_subsequent_page_template(doc)
        self.create_subsequent_page_template(doc,margin=0)

        story = []

        page1 = aof.get_page1(doc=doc)
        for item in page1:
            story.append(item)


        page2 = aof.get_page2(doc=doc)
        for item in page2:
            story.append(item)

        # create KYC(3rd,4th) page(s) - KYC Details
        num_of_kycs = len(data.get('kyc_holders', []))
        for i in range (num_of_kycs):
            kyc_pages = await aof.get_kyc_pages(doc=doc,index=i)
            for item in kyc_pages:
                story.append(item)


        # add image as 5th page 
        story.append(pdf_components.insert_image_as_page(doc,'aof_05.jpg'))

        # create 6th page
        page6 = aof.get_page6(doc=doc)
        for item in page6:
            story.append(item)
     
        
        page7 = await aof.get_page7(doc=doc)
        for item in page7:
            story.append(item) 
     
        # create 8th page
        page8 = await aof.get_page8(doc=doc)
        for item in page8:
            story.append(item)

        # create 9th page
        page9 = await aof.get_page9(doc=doc)
        for item in page9:
            story.append(item)

        # create 10th page - Nominee Details Page
        num_of_nominees = len(data.get('nomination_details', {}).get('nominees',[]))
        page10 = await aof.get_page10(doc=doc,number_of_nominees=num_of_nominees)
        for item in page10:
            story.append(item)
        
        # create 11th page
        page11 = await aof.get_page11(doc=doc)
        for item in page11:
            story.append(item)
        
        # create 12th page
        page12 = await aof.get_page12(doc=doc)
        for item in page12:
            story.append(item)

        # create 13th page
        page13 = await aof.get_page13(doc=doc)
        for item in page13:
            story.append(item)


        # add image as 14th page 
        story.append(pdf_components.insert_image_as_page(doc,'aof_14.jpg'))

        # create 15th page
        page15 = await aof.get_page15(doc=doc)
        for item in page15:
            story.append(item)

        # Add aadhaar xml if aadhaar details are from digilocker
        for i in range (num_of_kycs):
            if data.get('kyc_holders', [])[i].get('kyc_holder', {}).get('identity_address_verification',{}).get('identity_address_info',{}).get('aadhaar_xml',''):
                xml_page = aof.get_aadhaar_xml_pages(doc=doc,index=i)
                story.append(PageBreak())
                story.append(xml_page)
                

        # ADD all the documents to the end of pdf(Todo: except signature and photo)
        exclude_files = ['wet_signature_image','liveness_photo']
        all_files = get_all_file_ids(record=data,exclude_ids=exclude_files)
        images:list[Image] = []
        all_pdf_attachments = []
        for file in all_files:
            
            if not 'pdf' in file.get('doc_type'):
                image_bytes = await pdf_components.fetch_image_bytes(file_id=file.get('doc_id')) if file.get('doc_id') else None
                _image = pdf_components.get_image_from_bytes(file_bytes=image_bytes,width=doc.width-doc.rightMargin*2-50, height=doc.height-doc.topMargin*2-50) if image_bytes else None

                if _image:
                    _table = pdf_tables.create_table([[_image],[Paragraph(file.get('doc_name',''),style=pdf_styles.normal_text_style(fontsize=9))]],col_widths=doc.width-doc.rightMargin*2,
                                                    style=pdf_styles.padded_table_style(top=20))
                    images.append(_table)
            else:
                all_pdf_attachments.append(file)

        
        # Add all IMAGEs to pdf
        for im in images:
            story.append(PageBreak())
            story.append(im)

        doc.build(story)

        # Merge all pdf attachments with generated pdf
        for pdf_attachment in all_pdf_attachments:
            pdf_bytes = await pdf_components.fetch_image_bytes(file_id=pdf_attachment.get('doc_id')) if file.get('doc_id') else None
            try:
                if pdf_bytes:
                    merge_pdf_attachment(original_pdf_path=pdf_path, file_bytes=pdf_bytes, output_file_path=pdf_path)
            except Exception as e:
                logger.error(f"Exception in merging pdf attachment '{pdf_attachment.get('doc_name')}': {e}")

    async def generate_aof_individual(self,pdf_path:str, kyc_data:dict, date_of_submission:str, application_no:str,author:str='',is_digilocker:bool=True):
        pdf_components = PdfComponents()
        pdf_tables = PdfTables()
        pdf_styles = PdfStyles()
        aof_ind = AOF_IND(data=kyc_data,application_no=application_no,is_digilocker=is_digilocker, date_of_submission = date_of_submission)

        doc = create_document(pdf_path,author=author)

        self.create_page_template(doc)
        self.create_subsequent_page_template(doc)
        self.create_subsequent_page_template(doc,margin=0)

        story = []

        kyc_pages = await aof_ind.get_pages(doc=doc)
        for item in kyc_pages:
            story.append(item)

        images:list[Image] = []

        imgs, pdfs = self._get_kyc_attachments_ids(kyc_data=kyc_data)
        
        for im in imgs:
            image_bytes = await pdf_components.fetch_image_bytes(file_id=list(im.keys())[0])
            _image = pdf_components.get_image_from_bytes(file_bytes=image_bytes,width=doc.width-doc.rightMargin*2-50, height=doc.height-doc.topMargin*2-50) if image_bytes else None

            if _image:
                _table = pdf_tables.create_table([[_image],[Paragraph(f'{list(im.values())[0]}',style=pdf_styles.normal_text_style(fontsize=9))]],col_widths=doc.width-doc.rightMargin*2,
                                                style=pdf_styles.padded_table_style(top=20))
                images.append(_table)

        # Add all IMAGEs to pdf
        for img in images:
            story.append(PageBreak())
            story.append(img)

        doc.build(story)

        # Merge all pdf attachments with generated pdf
        for pdf in pdfs:
            pdf_bytes = await pdf_components.fetch_image_bytes(file_id=list(pdf.keys())[0])
            try:
                if pdf_bytes:
                    merge_pdf_attachment(original_pdf_path=pdf_path, file_bytes=pdf_bytes, output_file_path=pdf_path)
            except Exception as e:
                logger.error(f"Exception in merging pdf attachment '{list(pdf.values())[0]}': {e}")



    def generate_cetdp(self,pdf_name:str, data:dict):
        cet_dp = CET_and_DP()
        pdf_components = PdfComponents()

        doc = create_document(pdf_name)
        # Get default stylesheet and modify the default style 

        self.create_page_template(doc)
        self.create_subsequent_page_template(doc)
        self.create_subsequent_page_template(doc,margin=0)


        story = []

        page1 = cet_dp.get_page1(doc=doc)
        for item in page1:
            story.append(item)

        page2 = cet_dp.get_page2(doc=doc)
        for item in page2:
            story.append(item)

        doc.build(story)

    def generate_ddpi(self,pdf_name:str,data:dict):

        ddpi = DDPI()
        doc = create_document(pdf_name)
        # Get default stylesheet and modify the default style 

        self.create_page_template(doc)
        self.create_subsequent_page_template(doc)
        self.create_subsequent_page_template(doc,margin=0)

        story = []

        page1 = ddpi.get_page1(doc=doc)
        for item in page1:
            story.append(item)

        # page2 = ddpi.get_page2(doc=doc)
        # for item in page2:
        #     story.append(item)

        doc.build(story)

    def _get_kyc_attachments_ids(self,kyc_data:dict):
        # Images to be added if available:
        #   1. PAN card: pan_card_image
        #   2. ovd front, back if ovd: ovd_front, ovd_back
        #   3. correspondence address proof: correspondence_address_proof
        #   4. Proof of signature: proof_of_signature

        # TODO: -- write method similar to 'get_all_file_ids' which takes list of keys, instead of hard coding for each kyc attachments!
        pan_card_image = kyc_data.get('pan_verification',{}).get('pan_card_image')
        ovd_front = kyc_data.get('identity_address_verification',{}).get('ovd',{}).get('ovd_front')
        ovd_back = kyc_data.get('identity_address_verification',{}).get('ovd',{}).get('ovd_back')
        correspondence_address_proof = kyc_data.get('identity_address_verification',{}).get('correspondence_address',{}).get('proof')
        proof_of_signature = kyc_data.get('signature_validation',{}).get('upload_images',{}).get('proof_of_signature')

        pdf_attachments: list[dict] = []
        images: list[dict] = []

        if pan_card_image and pan_card_image.get('doc_id',''):
             
            if pan_card_image.get('metadata',{}).get('doc_type','') and 'pdf' not in pan_card_image.get('metadata',{}).get('doc_type',''):
                images.append({pan_card_image.get('doc_id',''):'PAN Card'})
            else:
                pdf_attachments.append({pan_card_image.get('doc_id',''):'PAN Card'})

        if ovd_front and ovd_front.get('doc_id',''):
            if ovd_front.get('metadata',{}).get('doc_type','') and 'pdf' not in ovd_front.get('metadata',{}).get('doc_type',''):
                images.append({ovd_front.get('doc_id',''): 'OVD Front'})
            else:
                pdf_attachments.append({ovd_front.get('doc_id',''): 'OVD Front'})

        if ovd_back and ovd_back.get('doc_id',''):
            if ovd_back.get('metadata',{}).get('doc_type','') and 'pdf' not in ovd_back.get('metadata',{}).get('doc_type',''):
                images.append({ovd_back.get('doc_id',''): 'OCD Back'})
            else:
                pdf_attachments.append({ovd_back.get('doc_id',''): 'OVD Back'})

        if correspondence_address_proof and correspondence_address_proof.get('doc_id',''):
            if correspondence_address_proof.get('metadata',{}).get('doc_type','') and 'pdf' not in correspondence_address_proof.get('metadata',{}).get('doc_type',''):
                images.append({correspondence_address_proof.get('doc_id',''): 'Proof of Correspondence Address'})
            else:
                pdf_attachments.append({correspondence_address_proof.get('doc_id',''):'Proof of Correspondence Address'})

        if proof_of_signature and proof_of_signature.get('doc_id',''):
            if proof_of_signature.get('metadata',{}).get('doc_type','') and 'pdf' not in proof_of_signature.get('metadata',{}).get('doc_type',''):
                images.append({proof_of_signature.get('doc_id',''):'Proof of Signature'})
            else:
                pdf_attachments.append({proof_of_signature.get('doc_id',''):'Proof of Signature'})

        return (images, pdf_attachments)
        


# PdfGenerator().generate_aof(pdf_name='abc.pdf',data={})