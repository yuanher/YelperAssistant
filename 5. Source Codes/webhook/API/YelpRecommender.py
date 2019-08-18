# -*- coding: utf-8 -*-
"""
Yelp Recommender API code.
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib

# This client code can run on Python 2.x or 3.x.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

API_KEY="XFnIw20KhkELYfmjwr9T-QKQAjbeCfJ6CXUi5mBcFz_oesBBucWutod7choZcFNS8K1ZVc5q-w9fS34_otV1v2M-ku1sawIMYQCPuKiQfwZXqwvGlwI9HHohxpfJXHYx"


# API constants, you shouldn't have to change these.
API_HOST = 'https://yelperassistant-rec.herokuapp.com:5001'
SEARCH_PATH = '/api/v1/recommend/'

# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3

class YelpRecommender(object):
    """The YelpRecommender object implements interaction with Yelp Recommender API.
    """

    def __init__(self, params):
        #Initializes the YelpRecommender object

        self.user_id = params['user_id']

    def request(self, host, path, url_params=None):
        """Given your API_KEY, send a GET request to the API.
        Args:
            host (str): The domain host of the API.
            path (str): The path of the API after the domain.
            url_params (dict): An optional set of query parameters in the request.
        Returns:
            dict: The JSON response from the request.
        Raises:
            HTTPError: An error occurs from the HTTP request.
        """
        url_params = url_params or {}
        url = '{0}{1}{2}'.format(host, quote(path.encode('utf8')), url_params)
        headers = {
            'Authorization': 'Bearer %s' % API_KEY,
        }

        print(u'Querying {0} ...'.format(url))

        response = requests.request('GET', url, headers=headers, params={})

        return response.json()

    def getReommendations(self):
        """Returns recommendations by user-ID
        Args:
            user_id     Specify the user_id.
        Returns:
            dict: user recommendations
        """

        url_params = "userid=" + self.user_id

        return self.request(API_HOST, SEARCH_PATH, url_params=url_params)

def validate_params(parameters):
    """Takes a list of parameters from a HTTP request and validates them

    Returns a string of errors (or empty string) and a list of params
    """

    # Initialize error and params
    error_response = ''
    params = {}

    # User ID
    params['user_id'] = parameters.get('user_id')

    return error_response.strip(), params