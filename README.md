# Geocode

A small tool to geocode the addresses of agencies in the MuckRock database.
Uses the API to collect a group of agencies, then for each agency it:

- cleans the existing address
- tags the address using the `usaddress` module
- rewrites the address using the individual tags
- geocodes the rewritten address by using an external geocoding service

Then, using this data it:

- writes the agency data to a `.json` file for debugging or other processing
- patches each agency in the MuckRock API with the geocoded location

This script currently requires a MuckRock account.
An account can be created on the MuckRock website.

The script will ask you to login each time it's run, unless your MuckRock API token exists in your environment.
To set that up, run `python muckrock.py` to authenticate and get instructions on adding your token to your environment.

To run the geocode script on all agencies, run `python geocode.py`.
The current external geocoding service is the OSM Nominatim, since it returned the best results.
To use a different geocoder, replace the URL and the query arguments in the `geocode.geocode_address` method.

To run the goecode script on a subset of agencies, provide additional params to the `muckrock.agencies` method.
For example, to limit the geocoding to just approved federal agencies, supply the parameter `{'jurisdiction': 10, 'status': 'approved'}`.

## Install and Run

1. `pip install -r requirements.txt`
2. `python geocode.py`
