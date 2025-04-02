from pydantic import BaseModel

class GeocodeLocation(BaseModel):
    """
    Geocode location model.
    """
    suburb: str | None
    city_or_county: str | None
    state: str | None
    country: str | None
    pincode: str | None
    latitude: str | None
    longitude: str | None
    formatted_address: str | None # Address line made up of suburb, city, state, country, and pincode.

# geocode_address_sample = {
#         "amenity": "St. Joseph's Indian High School",
#         "road": "Vittal Mallya Road",
#         "neighbourhood": "D'Souza Layout",
#         "suburb": "Shanthala Nagar",
#         "city": "Bengaluru",
#         "county": "Bangalore North",
#         "state_district": "Bengaluru Urban",
#         "state": "Karnataka",
#         "ISO3166-2-lvl4": "IN-KA",
#         "postcode": "560001",
#         "country": "India",
#         "country_code": "in",
#     }