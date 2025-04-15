from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

import fitz  # PyMuPDF
from datetime import datetime
import io
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def stamp_pdf(
    pdf_bytes: bytes,
    signing_text: str = 'Signed by Way2Wealth',
    page_number: int = 0, # Zero based index
    rect_coords=(350, 600, 470, 700)
) -> bytes:
    """
    Stamps a PDF (provided as bytes) with a signature image and text.
    Returns the stamped PDF as bytes.
    """
    # Open the PDF from bytes
    pdf_stream = io.BytesIO(pdf_bytes)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")

    # Select the page
    page = doc[page_number]
    rect = fitz.Rect(*rect_coords)

    image_path = os.getenv("W2W_DIGITAL_SIGN_STAMP_IMAGE")
    base_path = os.getenv("CRED_FILES_MOUNT_PATH")
    
    signature_image_path = os.path.join(base_path, image_path)

    # Insert signature image
    page.insert_image(rect, filename=signature_image_path)

    # Insert text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page.insert_text((rect.x0, rect.y0 + 30), f"Signed by: {signing_text}", fontsize=8, color=(0, 0, 0))
    page.insert_text((rect.x0, rect.y0 + 50), f"Timestamp: {timestamp}", fontsize=8, color=(0, 0, 0))

    # Save to bytes
    output_stream = io.BytesIO()
    doc.save(output_stream, garbage=4, clean=True)
    doc.close()
    output_stream.seek(0)
    return output_stream.read()


def digitally_sign_pdf(
    pdf_bytes: bytes,
    field_name: str = "Signature",
    signing_text: str = 'Signed by Way2Wealth'
) -> bytes:
    """
    Digitally signs PDF bytes using a PKCS#12 certificate.
    Returns signed PDF as bytes.
    
    Args:
        - pdf_bytes: Input PDF as bytes
        - pfx_file: Path to .p12/.pfx certificate file
        - passphrase: Certificate passphrase as bytes
        - field_name: Signature field name (default: 'Signature')
        - signing_text: Text to display on the signature field (default: 'Signed by Way2Wealth')
    """
    
    pfx_file = os.getenv("PROTEAN_ESIGN_PFX")
    base_path = os.getenv("CRED_FILES_MOUNT_PATH")
    password = os.getenv('PROTEAN_ESIGN_PFX_PASSWORD')
    passphrase = password.encode("utf-8")
    pfx_file_path = os.path.join(base_path, pfx_file)

    # Load the certificate
    signer = signers.SimpleSigner.load_pkcs12(
        pfx_file=pfx_file_path, passphrase=passphrase
    )

    # Configure signature metadata
    signature_meta = signers.PdfSignatureMetadata(
        field_name=field_name,
        signinig_text=signing_text
    )

    # Create in-memory PDF stream
    pdf_stream = io.BytesIO(pdf_bytes)
    
    # Prepare PDF writer
    writer = IncrementalPdfFileWriter(pdf_stream)

    # Sign the PDF in memory
    signed_stream = signers.sign_pdf(
        writer,
        signature_meta=signature_meta,
        signer=signer,
        output=None  # Returns BytesIO object
    )

    # Return signed PDF bytes
    signed_stream.seek(0)
    return signed_stream.read()

def obfuscate_string(data_str: str, static_key: str) -> str:
        # Ensure the key is exactly 16 bytes long
        key = static_key.encode().ljust(16, b"\0")

        # Data to encrypt
        data = data_str.encode()

        # Create cipher and encrypt the data with padding
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))

        # Encode the encrypted data with Base64
        obfuscated_string = base64.urlsafe_b64encode(encrypted_data).decode()
        return obfuscated_string
