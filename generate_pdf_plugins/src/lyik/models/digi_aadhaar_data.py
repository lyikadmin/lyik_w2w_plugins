from pydantic import BaseModel
import xml.etree.ElementTree as ET
import base64 


class Aadhaar(BaseModel):
    name: str | None
    dob: str | None
    gender: str | None
    co: str | None # care of
    address: str | None
    photo: bytes | None 

def extract_aadhaar_data(xml_data):
    try:
        root = ET.fromstring(xml_data)
        
        # Navigate through the XML structure to find the required data
        uid_data = root.find('.//UidData')
        poi = uid_data.find('Poi')
        poa = uid_data.find('Poa')
        pht = uid_data.find('Pht')  # Extracting Pht tag

        if pht is not None and pht.text:
            # Remove ALL newlines/whitespace from the text
            cleaned_text = pht.text.replace('\n', '').strip()
            # Decode Base64 to bytes (common for photo data)
            photo = base64.b64decode(cleaned_text)
        else:
            photo = None
        # Extract values
        name = poi.attrib.get('name')
        dob = poi.attrib.get('dob')
        gender = poi.attrib.get('gender')
        co = poa.attrib.get('co')
        house = poa.attrib.get('house')
        loc = poa.attrib.get('loc')
        vtc = poa.attrib.get('vtc')
        po = poa.attrib.get('po')
        subdist = poa.attrib.get('subdist')
        dist = poa.attrib.get('dist')
        state = poa.attrib.get('state')
        pc = poa.attrib.get('pc')

        # Form the address string
        address = f"{house} {loc} {vtc} {po} {subdist} {dist} {state} {pc}"

        # Create an instance of Adr
        aadhaar_instance = Aadhaar(
            name=name,
            dob=dob,
            gender=gender,
            co=co,
            address=address,
            photo=photo  # Replace with actual photo extraction logic if needed
        )
        
        return aadhaar_instance

    except ET.ParseError as e:
        print("Error parsing XML:", e)
        return None
