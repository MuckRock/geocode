#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getpass
import os
import requests

API_URL = 'https://www.muckrock.com/api_v1'
API_KEY = os.environ.get('MUCKROCK_API_TOKEN')

def agencies(filters=None):
    """Fetch the agencies from the API that match the filters."""
    starting_url = API_URL + '/agency/'
    headers = {'content-type': 'application/json'}
    params = None
    if filters:
        params = filters
    data = get(starting_url, headers, params)
    return data

def get(url, headers, params):
    """Constructs a request and turns a response from the provided endpoint.
    Recursively traverses paginated responses."""
    if not API_KEY:
        token = authenticate()
        if not token:
            raise ValueError('Missing MuckRock API token.')
    else:
        token = API_KEY
    headers.update({'Authorization': 'Token %s' % token})
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise AttributeError('Non 200 status encountered.')
    data = response.json()
    next_page = data['next']
    page_results = data['results']
    if next_page:
        # page results are always a list type, so we combine them with the + operator
        page_results += get(next_page, headers, params)
    return page_results

def patch(url, headers, data):
    """Make a patch request"""
    if not API_KEY:
        token = authenticate()
        if not token:
            raise ValueError('Missing MuckRock API token.')
    else:
        token = API_KEY
    headers.update({'Authorization': 'Token %s' % token})
    response = requests.patch(url, headers=headers, data=data)
    if response.status_code != 200:
        raise AttributeError('Non 200 status encountered.')

def authenticate():
    """Capture the username and password of the user, use it to generate a token."""
    print '\nLog in to your MuckRock account'
    username = raw_input('Username: ')
    password = getpass()
    response = requests.post('https://www.muckrock.com/api_v1/token-auth/', data={
        'username': username,
        'password': password
    })
    data = response.json()
    if 'token' in data:
        token = data['token']
        print '\nYour token is %s\n' % token
        return token
    else:
        print '\nCould not authenticate you.\n'
        return None

if __name__ == '__main__':
    token = authenticate()
    if token:
        print '\nYour API token: %s\n' % token
        print '\nSet your token with the command:'
        print '\nexport MUCKROCK_API_TOKEN="%s"' % token
