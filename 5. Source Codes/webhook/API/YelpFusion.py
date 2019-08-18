# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
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


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY="XFnIw20KhkELYfmjwr9T-QKQAjbeCfJ6CXUi5mBcFz_oesBBucWutod7choZcFNS8K1ZVc5q-w9fS34_otV1v2M-ku1sawIMYQCPuKiQfwZXqwvGlwI9HHohxpfJXHYx"


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
PHONE_PATH = '/v3/businesses/search/phone'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TRANSACTION_PATH = '/v3/transactions/delivery/search'
MATCH_PATH = '/v3/businesses/matches'
AUTOCOMPLETE_PATH = '/v3/autocomplete'
EVENT_PATH = '/v3/events' 
CATEGORY_PATH = '/v3/categories'

# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3

class YelpFusion(object):
    """The YelpFusion object implements interaction with YelpFusion API.

    Attributes:
        city (str): the city for the weather forecast
    """

    def __init__(self, params):
        #Initializes the YelpFusion object

        self.businessID = params['businessID']
        self.term = params['term']
        self.location = params['location']
        self.latitude = str(params['latitude'])
        self.longitude = str(params['longitude'])
        self.radius = str(params['radius'])
        self.categories = params['categories']
        self.locale = params['locale']
        self.offset = params['offset']
        self.sort_by = params['sort_by']
        self.price = str(params['price'])
        self.open_now = params['open_now']
        self.open_at = params['open_at']
        self.attributes = params['attributes']
        self.name = params['name']
        self.address1 = params['address1']
        self.address2 = params['address2']
        self.address3 = params['address3']
        self.city = params['city']
        self.state = params['state']
        self.country = params['country']
        self.phone = params['phone']
        self.zip_code = params['zip_code']
        self.yelp_business_id = params['yelp_business_id']
        self.match_threshold = params['match_threshold']
        self.text = params['text']
        self.eventID = params['eventID']
        self.sort_on = params['sort_on']
        self.start_date = params['start_date']
        self.end_date = params['end_date']
        self.is_free = params['is_free']
        self.excluded_events = params['excluded_events']

        print(self.yelp_business_id)

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
        url = '{0}{1}'.format(host, quote(path.encode('utf8')))
        headers = {
            'Authorization': 'Bearer %s' % API_KEY,
        }

        print(u'Querying {0} ...'.format(url))

        response = requests.request('GET', url, headers=headers, params=url_params)

        return response.json()
 
    def query_api(self, term, location):
        """Queries the API by the input values from the user.
        Args:
            term (str): The search term to query.
            location (str): The location of the business to query.
        """
        response = self.search(API_KEY, term, location)

        businesses = response.get('businesses')

        if not businesses:
            print(u'No businesses for {0} in {1} found.'.format(term, location))
            return

            business_id = businesses[0]['id']

            print(u'{0} businesses found, querying business info ' \
                'for the top result "{1}" ...'.format(
                    len(businesses), business_id))
            response = get_business(business_id)

            print(u'Result for business "{0}" found:'.format(business_id))
            pprint.pprint(response, indent=2)

    def searchBusiness(self):
        """Query the Search API by a search term and location.
        Args:
            term (str): The search term passed to the API.
            location (str): The search location passed to the API.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': self.term.replace(' ', '+'),
            'location': self.location.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longitude': self.longitude.replace(' ', '+'),
            'radius': self.radius.replace(' ', '+'),
            'categories': self.categories.replace(' ', '+'),
            'offset': self.offset.replace(' ', '+'),
            'sort_by': self.sort_by.replace(' ', '+'),
            'price': self.price.replace(' ', '+'),
            'open_now': self.open_now.replace(' ', '+'),
            'open_at': self.open_at.replace(' ', '+'),
            'attributes': self.attributes.replace(' ', '+'),
            'limit': SEARCH_LIMIT
        }
        return self.request(API_HOST, SEARCH_PATH, url_params=url_params)

    def getBusiness(self):
        """Returns detailed business content by ID
        Args:
            locale	Specify the locale into which to localize the business information.
        Returns:
            dict: Business with matching ID
        """
        business_path = BUSINESS_PATH + self.businessID

        url_params = {}

        return self.request(API_HOST, business_path, url_params=url_params)

    def searchBusinessByPhone(self):
        """Returns a list of businesses based on the provided phone number.
        Args:
            phone	Phone number of the business to search for.
        Returns:
            dict: List of matching businesses by phone
        """
        url_params = {
            'phone': self.phone.replace(' ', '+')
        }
        return self.request(API_HOST, PHONE_PATH, url_params=url_params)

    def searchFoodDeliveryBusinesses(self):
        """Returns a list of businesses which support food delivery transactions.
        Args:
            latitude	Latitude of the location to deliver to.
            longitude	Longitude of the location to deliver to.
            location	Address of the location to deliver to.
        Returns:
            dict: List of Food Delivery Businesses
        """
        url_params = {
            'location': self.location.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longitude': self.longitude.replace(' ', '+')
        }
        return self.request(API_HOST, TRANSACTION_PATH, url_params=url_params)

    def matchBusiness(self):
        """Matches business data from other sources against businesses on Yelp, based on provided business information
        Args:
            name	            Name of the business. Maximum length is 64.
            address1	        First line of the business’s address. Maximum length is 64.
            address2	        Second line of the business’s address. Maximum length is 64.
            address3	        Third line of the business’s address. Maximum length is 64.
            city	            City of the business. Maximum length is 64.
            state	            ISO 3166-2 state code of this business. Maximum length is 3.
            country	            ISO 3166-1 alpha-2 country code of this business. Maximum length is 2.
            latitude	        Latitude of the business in decimal degrees. Must be between ­-90 and +90.
            longitude	        Longitude of the business in decimal degrees. Must be between ­-180 and +180.
            phone	            Phone number of the business. Maximum length is 32.
            zip_code	        Zip code of this business.
            yelp_business_id	Unique Yelp identifier of the business if available.
            limit	            Maximum number of business results to return. 
            match_threshold	    Specifies whether a match quality threshold should be applied to the matched                              businesses. Must be one of 'none', 'default' or 'strict'.
                                none: Do not apply any match quality threshold; all potential business matches will be returned.
                                default: Apply a match quality threshold such that only very closely matching businesses will be returned.
                                strict: Apply a very strict match quality threshold.
        Returns:
            dict: List of matching businesses.
        """
        url_params = {
            'name': self.name.replace(' ', '+'),
            'address1': self.address1.replace(' ', '+'),
            'address2': self.address2.replace(' ', '+'),
            'address3': self.address3.replace(' ', '+'),
            'city': self.city.replace(' ', '+'),
            'state': self.state.replace(' ', '+'),
            'country': self.country.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longitude': self.longitude.replace(' ', '+'),
            'phone': self.phone.replace(' ', '+'),
            'zip_code': self.zip_code.replace(' ', '+'),
            'yelp_business_id': self.yelp_business_id.replace(' ', '+'),
            'match_threshold': self.match_threshold.replace(' ', '+'),
            'limit': SEARCH_LIMIT
        }
        return self.request(API_HOST, MATCH_PATH, url_params=url_params)

    def getBusinessReviews(self):
        """Returns up to three review excerpts for a given business ordered by Yelp's default sort orde
        Args:
            None
        Returns:
            dict: Reviews of matching business
        """
        review_path = BUSINESS_PATH + self.businessID + "/reviews"

        url_params = {}

        return self.request(API_HOST, review_path, url_params=url_params)

    def getAutocompleteSuggestions(self):
        """Returns up to three review excerpts for a given business ordered by Yelp's default sort orde
        Args:
            text	    Text to return autocomplete suggestions for.
            latitude	Latitude of the location to look for business autocomplete suggestions.
            longitude	Longitude of the location to look for business autocomplete suggestions.
        Returns:
            dict: Autocopmlete suggestions for search text.
        """

        url_params = {
            'text': self.text.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longtiude': self.longtiude.replace(' ', '+')
        }

        return self.request(API_HOST, AUTOCOMPLETE_PATH, url_params=url_params)

    def getEvent(self):
        """Returns detailed event content by ID
        Args:
            None
        Returns:
            dict: Event with matching ID
        """
        event_path = EVENT_PATH + "/" + self.eventID

        url_params = {}

        return self.request(API_HOST, event_path, url_params=url_params)

    def searchEvent(self):
        """Query the Search API by a search term and location.
        Args:
            
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'offset': self.offset.replace(' ', '+'),
            'sort_by': self.sort_by.replace(' ', '+'),
            'sort_on': self.sort_on.replace(' ', '+'),
            'start_date': self.start_date.replace(' ', '+'),
            'end_date': self.end_date.replace(' ', '+'),
            'categories': self.categories.replace(' ', '+'),
            'is_free': self.is_free.replace(' ', '+'),
            'location': self.location.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longitude': self.longitude.replace(' ', '+'),
            'radius': self.radius.replace(' ', '+'),
            'excluded_events': self.excluded_events.replace(' ', '+'),
            'limit': SEARCH_LIMIT
        }
        return self.request(API_HOST, EVENT_PATH, url_params=url_params)

    def getFeaturedEvents(self):
        """Returns the featured event for a given location
        Args:
            location    Specifies the combination of "address, neighborhood, city, state or zip, optional country" to             be used while searching for events.
            latitude	Latitude of the location to search from.
            longitude	Longitude of the location to search from.
        Returns:
            dict: Featured events for a given location.
        """

        featured_path = EVENT_PATH + "/featured"

        url_params = {
            'location': self.location.replace(' ', '+'),
            'latitude': self.latitude.replace(' ', '+'),
            'longitude': self.longitude.replace(' ', '+')
        }

        return self.request(API_HOST, featured_path, url_params=url_params)

    def searchCategories(self):
        """Returns all Yelp business categories across all locales by default.
        Args:
            None
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {}

        return self.request(API_HOST, CATEGORY_PATH, url_params=url_params)

    def getCategory(self):
        """Returns detailed information about the Yelp category specified by a Yelp category alias
        Args:
            alias   Specify the alias of the category.
        Returns:
            dict: Category with matching ID
        """
        category_path = CATEGORY_PATH + "/" + self.businessID

        url_params = {
            'alias': self.alias.replace(' ', '+')
        }

        return self.request(API_HOST, category_path, url_params=url_params)

def validate_params(parameters):
    """Takes a list of parameters from a HTTP request and validates them

    Returns a string of errors (or empty string) and a list of params
    """

    # Initialize error and params
    error_response = ''
    params = {}

    # Business ID
    params['businessID'] = parameters.get('businessID')

    # Term
    params['term'] = parameters.get('term')

    # Location
    params['location'] = parameters.get('location')

    # Latitude
    params['latitude'] = parameters.get('latitude')

    # Longitude
    params['longitude'] = parameters.get('longitude')

    # Radius
    params['radius'] = parameters.get('radius')

    # Categories
    params['categories'] = parameters.get('categories')

    # Locale
    params['locale'] = parameters.get('locale')
    if(params['locale'] == ""):
        params['locale'] = 'en_US'

    # Offset
    params['offset'] = parameters.get('offset')

    # Sort_by
    params['sort_by'] = parameters.get('sort_by')
    if(params['sort_by'] == ""):
        params['sort_by'] = 'best_match'

    # Locale
    params['locale'] = parameters.get('locale')

    # Price
    params['price'] = parameters.get('price')
    if(params['price'] in ["", "5"]):
        params['price'] = "1, 2, 3, 4"

    # Open_now
    params['open_now'] = parameters.get('open_now')

    # Open_at
    params['open_at'] = parameters.get('open_at')

    # Attributes
    params['attributes'] = parameters.get('attributes')
    if(params['attributes'] == "1"):
        params['attributes'] = "hot_and_new"
    elif(params['attributes'] == "2"):
        params['attributes'] = "cashback"      
    elif(params['attributes'] == "3"):
        params['attributes'] = "deals" 
    elif(params['attributes'] == "4"):
        params['attributes'] = "wheelchair_accessible" 
    elif(params['attributes'] == "5"):
        params['attributes'] = "reservation" 
    elif(params['attributes'] == "6"):
        params['attributes'] = "waitlist_reservation" 
    else:
        params['attributes'] = "" 
        
    # Name
    params['name'] = parameters.get('name')

    # Address1
    params['address1'] = parameters.get('address1')

    # Address2
    params['address2'] = parameters.get('address2')

    # Address3
    params['address3'] = parameters.get('address3')

    # City
    params['city'] = parameters.get('city')

    # State
    params['state'] = parameters.get('state')

    # Country
    params['country'] = parameters.get('country')

    # Phone
    params['phone'] = parameters.get('phone')

    # Zip_code
    params['zip_code'] = parameters.get('zip_code')

    # Yelp_business_id
    params['yelp_business_id'] = parameters.get('yelp_business_id')

    # Match_threshold
    params['match_threshold'] = parameters.get('match_threshold')
    if(params['match_threshold'] == ""):
        params['match_threshold'] = "None"

    # Text
    params['text'] = parameters.get('text')

    # Event ID
    params['eventID'] = parameters.get('eventID')

    # Sort_on
    params['sort_on'] = parameters.get('sort_on')
 
    # Start_date
    params['start_date'] = parameters.get('start_date')

    # End_date
    params['end_date'] = parameters.get('end_date')

    # Is_free
    params['is_free'] = parameters.get('is_free')

    # Excluded_events
    params['excluded_events'] = parameters.get('excluded_events')

    return error_response.strip(), params