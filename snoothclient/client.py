# -*- coding: utf-8 -*-
import os
import sys
import requests
from errors import SnoothError
from handlers import http_error_handler, snooth_error_handler, timeout_handler
from utils import wineify

try:
    API_KEY = os.environ['API_KEY']
except KeyError:
    API_KEY = None
    sys.stderr.write('Please set os.environ["API_KEY"] = yourapikey, '
                     'or pass api_key param in SnoothClient')


class SnoothClient(object):
    WINE_SEARCH_URL = 'https://api.snooth.com/wines/'
    STORE_SEARCH_URL = 'https://api.snooth.com/stores/'
    CREATE_ACCOUNT_URL = 'https://api.snooth.com/create-account/'
    RATE_WINE_URL = 'http://api.snooth.com/rate/'

    def __init__(self, api_key=API_KEY, format='json', ip=None,
                 username=None, password=None, timeout=None):
        self.api_key = API_KEY
        self.format = format
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout

    # Need more control over output. JSON, Full python, python wine_dict, wine.
    # Translate bool here
    @timeout_handler
    def wine_search(self, q='wine', wineify=False, count=10, page=1,
                    first_result=None, available=1, prod_type=None,
                    color=None, store_id=None, country=None,
                    zipcode=None, lat=None, lng=None, sort=None,
                    min_price=None, max_price=None, min_rank=None,
                    max_rank=None, lang=None, timeout=None):
        if lat and not lng or lng and not lat:
            raise SnoothError('Must pass both lat and lng')
        if first_result is None:
            first_result = page * count + 1
        query = {
            'akey': self.api_key, 'format': self.format, 'ip': self.ip,
            'u': self.username, 'p': self.password, 'q': q, 'f': first_result,
            'n': count, 'a': available, 't': prod_type, 'color': color,
            'm': store_id, 'c': country, 'z': zipcode, 'lat': lat, 'lng': lng,
            's': sort, 'mp': min_price, 'xp': max_price, 'mr': min_rank,
            'xr': max_rank, 'lang': lang
        }
        response = self.get(self.WINE_SEARCH_URL, query, timeout=timeout)
        python_response = self.parse_response(response)
        if wineify is True:
            python_response = self._wineify_wine_search(response)
        return python_response

    def _wineify_wine_search(self, python_response):
        wines = python_response['wines']
        return wineify(wines)

    @timeout_handler
    def store_search(self, country=None, zipcode=None,
                     lat=None, lng=None, timeout=None):
        if lat and not lng or lng and not lat:
            raise SnoothError('Must pass both lat and lng')
        query = {
            'akey': self.api_key, 'format': self.format, 'ip': self.ip,
            'u': self.username, 'p': self.password, 'c': country,
            'z': zipcode, 'lat': lat, 'lng': lng
        }
        response = self.get(self.STORE_SEARCH_URL, query, timeout)
        python_response = self.parse_response(response)
        return python_response

    @timeout_handler
    def create_account(self, email=None, screen_name=None,
                       password=None, timeout=None):
        query = {
            'akey': self.api_key,
            'format': self.format,
            'ip': self.ip,
            'e': email,
            's': screen_name,
            'p': password
        }
        response = self.post(self.CREATE_ACCOUNT_URL, query, timeout)
        python_response = self.parse_response(response)
        return python_response

    @timeout_handler
    def rate_wine(self, wine_id, username=None,
                  password=None, rating=None, review=None,
                  private=False, tags=None, wishlist=False,
                  cellar_count=None, timeout=None):
        bools = translate_bool(private, wishlist)
        return bools

    @http_error_handler
    def get(self, url, query, timeout):
        response = requests.get(
            url,
            params=query,
            verify=True,
            timeout=timeout
        )
        return response

    @http_error_handler
    def post(self, url, query, timeout):
        response = requests.post(
            url,
            params=query,
            verify=True,
            timeout=timeout
        )
        return response

    @snooth_error_handler
    def parse_response(self, response):
        return response.json()


def translate_bool(*args):
    results = []
    for arg in args:
        if arg is False:
            arg = 0
        else:
            arg = 1
        results.append(arg)
    return results

