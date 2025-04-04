from lyikpluginmanager import (
    DBDocumentModel,
    invoke
)
from ..models.document_plugin_config import DocPluginConfig
from ..models.geocode_location import GeocodeLocation
import logging
logger = logging.getLogger(__name__)
from jsonpath_ng import parse as jsonparse
from datetime import datetime
from dateutil.parser import parse

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from xml.dom.minidom import parseString
from pypdf import PdfWriter, PdfReader
from io import BytesIO

async def fetchFileBytes(file_id:str)->bytes:
    document_plugin_config = DocPluginConfig()
    if document_plugin_config.is_none():
        return None
    
    try:
        documents = await invoke.fetchDocument(
                config=document_plugin_config.context.config,
                org_id=document_plugin_config.context.org_id,
                file_id=file_id,
                coll_name=document_plugin_config.context.form_id,
                metadata_params=None
            )
        doc: DBDocumentModel = documents[0] if isinstance(documents, list) and all(isinstance(item, DBDocumentModel) for item in documents) else None
        if doc is None:
            raise Exception('error getting attachment from db!')
        
        return doc.doc_content
    except Exception as e:
        logger.error(f"Exception: {e}. Ignoring and continueing...")
        return None
    

def get_all_file_ids(record:dict, exclude_ids:list[str]=None):
    """
    This method returns a list of all the file references i.e 'doc_id's along with file name and file type.
    Excludes video file types and paths containing any strings in exclude_ids!    
    """
    jsonpath_expr = jsonparse('$..doc_id')
    matches = jsonpath_expr.find(record)
    values = []
    for match in matches:
        parent = match.context.value
        # Check if the path should be excluded
        full_path = str(match.full_path)
        if exclude_ids and any(exclude_id in full_path for exclude_id in exclude_ids):
            continue
        if 'doc_type' in parent['metadata'] and not parent['metadata']['doc_type'].startswith('video'):
            values.append({
                'doc_id': parent['doc_id'],
                'doc_name': parent.get('doc_name', ''),
                'doc_type': parent['metadata']['doc_type']
            })
    return values

def merge_pdf_attachment(original_pdf_path:str, file_bytes:bytes, output_file_path:str):
    """
    Merges the original PDF file with attachment PDF provided as bytes and writes the
    merged output to a specified file while preserving the original PDF's metadata.
    """
    writer = PdfWriter()

    # Append the original PDF file
    with open(original_pdf_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
        # preserve the metadata from the original PDF
        writer.add_metadata(reader.metadata)

    # Append PDF from bytes
    pdf_stream = BytesIO(file_bytes)
    reader = PdfReader(pdf_stream)
    for page in reader.pages:
        writer.add_page(page)

    # Write the merged PDF to the output file
    with open(output_file_path, 'wb') as f_out:
        writer.write(f_out)

def get_geo_location(lat:str, long:str)->GeocodeLocation | None:
    """
    Returns the city or state or country(whichever found) based on the latitude and longitude, else ''. # Eariler it was 'Unknow'
    """
    geolocator = Nominatim(user_agent="pdf_plugin")
    if lat and long:
        try:
            location = geolocator.reverse(lat + "," + long)
            address = location.raw['address']
            geo_loc = GeocodeLocation(
                suburb=address.get('suburb', ''),
                city_or_county=address.get('city', '') or address.get('county',''),
                state=address.get('state', ''),
                country=address.get('country', ''),
                pincode=address.get('postcode', ''),
                latitude=lat,
                longitude=long,
                formatted_address=None
            )
            formatted_address = ''
            if geo_loc.suburb:
                formatted_address += geo_loc.suburb + ', '
            if geo_loc.city_or_county:
                formatted_address += geo_loc.city_or_county + ', '
            if geo_loc.state:
                formatted_address += geo_loc.state + ', '
            if geo_loc.country:
                formatted_address += geo_loc.country + ', '
            if geo_loc.pincode:
                formatted_address += geo_loc.pincode

            geo_loc.formatted_address = formatted_address
        
            logger.debug(f'Location based on geocode {lat}, {long}: {geo_loc.formatted_address}.')
            return geo_loc

        except GeocoderServiceError as e:
            logger.error("Exception getting location of holder: ", e)
    return None


def format_xml(xml_str):
    """Format XML string with indentation."""
    dom = parseString(xml_str)
    return dom.toprettyxml(indent="  ")

def split_into_chunks(text, lines_per_chunk=10):
    """Split text into chunks of specified number of lines."""
    lines = text.split('\n')
    for i in range(0, len(lines), lines_per_chunk):
        yield ''.join(lines[i:i+lines_per_chunk])


def format_date(date_str: str, output_format: str = "%d/%m/%Y") -> str:
    """
    Format a date string to a specified output format.
    Args:
        - date_str: The date string to be formatted.
        - output_format: The desired format of the output date string.
    Returns:
        - The formatted date string.
    """
    try:
        # Parse the input date string to a datetime object
        date_obj = parse(date_str)
        # Format the datetime object to the desired output format
        formatted_date = date_obj.strftime(output_format)
        return formatted_date
    except ValueError as e:
        logger.error(f"Error: {e}")
        return date_str
