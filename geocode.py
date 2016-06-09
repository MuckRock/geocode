#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geojson import Point
import io
import json
import muckrock
import os
import re
import requests
import usaddress

def geocode_agencies(agencies):
    """Geocodes the addresses from a list of agencies."""
    agency_data = []
    for agency in agencies:
        agency_id = agency['id']
        agency_address = unicode(agency['address'])
        cleaned_address = clean_address(agency_address)
        tagged_address = tag_address(cleaned_address)
        recombined_address = recombine_address(tagged_address)
        try:
            geocoded_address = geocode_address(recombined_address)
        except requests.exceptions.ConnectionError:
            geocoded_address = ''
            print 'Connection error to geocoder for agency %d' % agency_id
        if agency_address:
            agency_data.append({
                'id': agency_id,
                'jurisdiction': agency['jurisdiction'],
                'original_address': agency_address,
                'cleaned_address': cleaned_address,
                'tagged_address': tagged_address,
                'recombined_address': recombined_address,
                'geocoded_address': geocoded_address,
            })
    return agency_data

def clean_address(address):
    """Removes multiline formatting on addresses."""
    address = unicode(address.strip())
    pattern = re.compile(ur'[\r\n]+', re.UNICODE)
    result = pattern.sub(', ', address)
    return result

def tag_address(address):
    """Tags address by its individual components."""
    tagged_address = None
    try:
        tagged_address = usaddress.tag(address)
    except (usaddress.RepeatedLabelError, UnicodeEncodeError):
        pass
    return tagged_address

def recombine_address(tagged_address):
    """Recombine a parsed address into a cleaner, simpler one for geocoding."""
    if not tagged_address:
        return ''
    data = tagged_address[0]
    street = ' '.join([
        data.get('AddressNumber', ''),
        data.get('StreetName', ''),
        data.get('StreetNamePostType', ''),
        data.get('StreetNamePostDirectional', '')
    ])
    place = ', '.join([data.get('PlaceName', ''), data.get('StateName', '')])
    return ', '.join([street.strip(), place.strip()])

def geocode_address(address):
    """Uses the OSM Nominatim to transform an address into a GeoJSON point."""
    url = 'http://nominatim.openstreetmap.org/search'
    headers = {'content-type': 'application/json'}
    params = {'q': address, 'format': 'json'}
    response = requests.get(url, params=params, headers=headers)
    point = ''
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            result = data[0]
            lon = float(result['lon'])
            lat = float(result['lat'])
            point = Point((lon, lat))
    return point

def patch_agencies(agency_data):
    """This touches the MuckRock API to add the location to the agency,
    if the location can be determined from the address."""
    for agency in agency_data:
        try:
            patch_agency(agency['id'], agency['geocoded_address'])
        except requests.exceptions.ConnectionError:
            print 'Connection error to MuckRock for agency %d' % agency['id']

def patch_agency(agency_id, geocoded_address):
    """Patches the agency with the new location."""
    if not geocoded_address or not agency_id:
        return False
    if not isinstance(agency_id, int):
        raise ValueError('Agency id must be an integer value')
    url = muckrock.API_URL + '/agency/%d/' % agency_id
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'location': geocoded_address})
    muckrock.patch(url, headers, data)

if __name__ == '__main__':
    agencies = muckrock.agencies({'jurisdiction': 10, 'status': 'approved'})
    print 'Obtained list of all agencies'
    agency_data = geocode_agencies(agencies)
    print 'Geocoded all agencies'
    # Write agency list to JSON for debugging
    data = json.dumps(agency_data, indent=2, ensure_ascii=False)
    with io.open('data.json', 'w', encoding='utf-8') as f:
        f.write(unicode(data))
    print 'Wrote agency data to JSON file'
    # Patch the data on the agencies in the list
    patch_agencies(agency_data)
    print 'Patched agency data into the API'
