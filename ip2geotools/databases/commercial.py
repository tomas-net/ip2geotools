# -*- coding: utf-8 -*-
"""
Commercial geolocation databases
===================================

These classes access many different commercial geolocation databases.

"""
# pylint: disable=line-too-long,invalid-name,W0702
from __future__ import absolute_import
import json
from urllib.parse import quote
import re
import requests
from requests.auth import HTTPBasicAuth
import pyquery
from selenium import webdriver # selenium for Ip2LocationWeb
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ip2geotools.databases.interfaces import IGeoIpDatabase
from ip2geotools.models import IpLocation
from ip2geotools.errors import IpAddressNotFoundError, PermissionRequiredError, \
                                InvalidRequestError, InvalidResponseError, \
                                ServiceError, LimitExceededError


class DbIpWeb(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by searching directly
    on https://db-ip.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.post('https://db-ip.com/',
                                    headers={'User-Agent': 'Mozilla/5.0'},
                                    data=[('address', ip_address)],
                                    timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            raise ServiceError()

        # check for errors
        if b'you have exceeded the daily query limit' in request.content.lower():
            raise LimitExceededError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            pq = pyquery.PyQuery(content)
            parsed_ip = pq('html > body div.container > h1') \
                        .remove('span') \
                        .text() \
                        .strip()
            parsed_country = pq('html > body > div.container table tr:contains("Country") td') \
                             .text() \
                             .strip()
            parsed_region = pq('html > body > div.container table tr:contains("State / Region") td') \
                            .text() \
                            .strip()
            parsed_city = pq('html > body > div.container table tr:contains("City") td') \
                          .text() \
                          .strip()
            parsed_coords = pq('html > body > div.container table tr:contains("Coordinates") td') \
                            .text() \
                            .strip() \
                            .split(',')
        except:
            raise InvalidResponseError()

        # check for errors
        if ip_address != parsed_ip:
            raise IpAddressNotFoundError(ip_address)

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        try:
            ip_location.country = parsed_country
            ip_location.region = parsed_region
            ip_location.city = parsed_city
            ip_location.latitude = float(parsed_coords[0].strip())
            ip_location.longitude = float(parsed_coords[1].strip())
        except:
            ip_location.country = None
            ip_location.region = None
            ip_location.city = None
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class MaxMindGeoIp2City(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by GeoIP2 database
    created by MaxMind, available from https://www.maxmind.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            # optional auth for increasing amount of queries per day
            if username != None and password != None:
                auth = HTTPBasicAuth(username, password)
            else:
                auth = None

            request = requests.get('https://www.maxmind.com/geoip/v2.1/city/'
                                   + quote(ip_address)
                                   + ('?demo=1' if auth == None else ''),
                                   auth=auth,
                                   timeout=62)
        except:
            raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 400:
                raise InvalidRequestError(content['code'])
            elif request.status_code == 401:
                raise PermissionRequiredError(content['code'])
            elif request.status_code == 402:
                raise LimitExceededError(content['code'])
            elif request.status_code == 403:
                raise PermissionRequiredError(content['code'])
            elif request.status_code == 404:
                raise IpAddressNotFoundError(ip_address)
            elif request.status_code == 500:
                raise InvalidRequestError()
            else:
                raise ServiceError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content.get('country'):
            if content['country'].get('iso_code'):
                ip_location.country = content['country']['iso_code']
            else:
                ip_location.country = None
        else:
            ip_location.country = None

        if content.get('subdivisions'):
            if content['subdivisions'][0].get('names'):
                if content['subdivisions'][0]['names'].get('en'):
                    ip_location.region = content['subdivisions'][0]['names']['en']
                else:
                    ip_location.region = None
            else:
                ip_location.region = None
        else:
            ip_location.region = None

        if content.get('city'):
            if content['city'].get('names'):
                if content['city']['names'].get('en'):
                    ip_location.city = content['city']['names']['en']
                else:
                    ip_location.city = None
            else:
                ip_location.city = None
        else:
            ip_location.city = None

        if content.get('location'):
            ip_location.latitude = float(content['location']['latitude'])
            ip_location.longitude = float(content['location']['longitude'])
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class Ip2LocationWeb(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by searching directly
    on https://www.ip2location.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # initiate headless Firefox using selenium to pass through Google reCAPTCHA
        options = Options()
        options.headless = True
        browser = webdriver.Firefox(options=options)

        try:
            browser.get('http://www.ip2location.com/demo/' + ip_address)
            element = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.NAME, 'ipAddress'))
            )

            if not element:
                raise Exception
        except:
            raise ServiceError()

        # parse current limit
        current_limit = 0
        body = browser.find_element_by_tag_name('body').text

        try:
            limit = re.search(r'You still have.*?([\d]{1,2})/50.* query limit',
                              body,
                              re.DOTALL)

            if limit != None:
                current_limit = int(limit.group(1))
        except:
            raise InvalidResponseError()

        # check if limit is exceeded
        if current_limit == 0:
            raise LimitExceededError()

        # parse content
        try:
            table = browser.find_element_by_xpath('//table[contains(.,"Permalink")]')

            parsed_ip = table.find_element_by_xpath('//tr[contains(.,"IP Address")]/td').text.strip()
            parsed_country = [class_name.replace('flag-icon-', '').upper() for class_name in table.find_element_by_class_name('flag-icon').get_attribute('class').split(' ') if class_name.startswith('flag-icon-')][0]
            parsed_region = table.find_element_by_xpath('//tr[contains(.,"Region")]/td').text.strip()
            parsed_city = table.find_element_by_xpath('//tr[contains(.,"City")]/td').text.strip()
            parsed_coords = table.find_element_by_xpath('//tr[contains(.,"Coordinates of City")]/td').text.strip()
        except:
            raise InvalidResponseError()

        # exit headless firefox
        browser.quit()

        # check for errors
        if ip_address != parsed_ip:
            raise IpAddressNotFoundError(ip_address)

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        try:
            ip_location.country = parsed_country
            ip_location.region = parsed_region
            ip_location.city = parsed_city

            parsed_coords = parsed_coords.split('(')[0].split(',')
            ip_location.latitude = float(parsed_coords[0].strip())
            ip_location.longitude = float(parsed_coords[1].strip())
        except:
            ip_location.country = None
            ip_location.region = None
            ip_location.city = None
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class NeustarWeb(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by searching directly
    on https://www.home.neustar/resources/tools/ip-geolocation-lookup-tool/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.post('https://www.home.neustar/resources/tools/ip-geolocation-lookup-tool',
                                    headers={'User-Agent': 'Mozilla/5.0'},
                                    data=[('ip', ip_address)],
                                    timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            raise ServiceError()

        # check for errors
        if b'rate limit exceeded' in request.content.lower():
            raise LimitExceededError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            pq = pyquery.PyQuery(content)
            parsed_ip = pq('html > body > section.full.resource article h2 > strong') \
                        .text() \
                        .strip()
            parsed_country = pq('html > body > section.full.resource article div.data >table:first tr:contains("Country Code:") td:not(.item)') \
                             .text() \
                             .strip() \
                             .upper()
            parsed_region = pq('html > body > section.full.resource article div.data >table:first tr:contains("Region:") td:not(.item)') \
                            .text() \
                            .strip() \
                            .title()
            parsed_state = pq('html > body > section.full.resource article div.data >table:first tr:contains("State:") td:not(.item)') \
                           .text() \
                           .strip() \
                           .title()
            parsed_city = pq('html > body > section.full.resource article div.data >table:first tr:contains("City:") td:not(.item)') \
                          .text() \
                          .strip() \
                          .title()
            parsed_latitude = pq('html > body > section.full.resource article div.data >table:first tr:contains("Latitude:") td:not(.item)') \
                              .text() \
                              .strip()
            parsed_longitude = pq('html > body > section.full.resource article div.data >table:first tr:contains("Longitude:") td:not(.item)') \
                               .text() \
                               .strip()
        except:
            raise InvalidResponseError()

        # check for errors
        if ip_address != parsed_ip:
            raise IpAddressNotFoundError(ip_address)

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        try:
            ip_location.country = parsed_country

            if parsed_region is None:
                ip_location.region = parsed_region
            else:
                ip_location.region = parsed_state

            ip_location.city = parsed_city
            ip_location.latitude = float(parsed_latitude)
            ip_location.longitude = float(parsed_longitude)
        except:
            ip_location.country = None
            ip_location.region = None
            ip_location.city = None
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class GeobytesCityDetails(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by
    http://geobytes.com/get-city-details-api/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('http://getcitydetails.geobytes.com/GetCityDetails?fqcn='
                                   + quote(ip_address),
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            raise ServiceError()

        # parse content
        try:
            content = request.content.decode('latin-1')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content.get('geobytesinternet'):
            ip_location.country = content['geobytesinternet']
        else:
            ip_location.country = None

        if content.get('geobytesregion'):
            ip_location.region = content['geobytesregion']
        else:
            ip_location.region = None

        if content.get('geobytescity'):
            ip_location.city = content['geobytescity']
        else:
            ip_location.city = None

        if content.get('geobyteslatitude') and content.get('geobyteslongitude'):
            ip_location.latitude = float(content['geobyteslatitude'])
            ip_location.longitude = float(content['geobyteslongitude'])
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class SkyhookContextAcceleratorIp(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by http://www.skyhookwireless.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('https://context.skyhookwireless.com/accelerator/ip?'
                                   + 'ip=' + quote(ip_address)
                                   + '&user=' + quote(username)
                                   + '&key=' + quote(password)
                                   + '&version=2.0',
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 400:
                raise InvalidRequestError()
            elif request.status_code == 401:
                raise PermissionRequiredError(ip_address)
            else:
                raise ServiceError()

        # content decode
        try:
            content = request.content.decode('utf-8')
        except:
            raise InvalidResponseError()

        # check for IP address not found error
        if content == '{"data":{"ip":"' + ip_address + '"}}':
            raise IpAddressNotFoundError(ip_address)

        # parse content
        try:
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content.get('data'):
            if content['data'].get('civic'):
                if content['data']['civic'].get('countryIso'):
                    ip_location.country = content['data']['civic']['countryIso']
                else:
                    ip_location.country = None

                if content['data']['civic'].get('state'):
                    ip_location.region = content['data']['civic']['state']
                else:
                    ip_location.region = None

                if content['data']['civic'].get('city'):
                    ip_location.city = content['data']['civic']['city']
                else:
                    ip_location.city = None
            else:
                ip_location.country = None
                ip_location.region = None
                ip_location.city = None

            if content['data'].get('location'):
                if content['data']['location'].get('latitude') \
                   and content['data']['location'].get('longitude'):
                    ip_location.latitude = content['data']['location']['latitude']
                    ip_location.longitude = content['data']['location']['longitude']
                else:
                    ip_location.latitude = None
                    ip_location.longitude = None
            else:
                ip_location.latitude = None
                ip_location.longitude = None
        else:
            ip_location.country = None
            ip_location.region = None
            ip_location.city = None
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class IpInfo(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by https://ipinfo.io/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('https://ipinfo.io/' + quote(ip_address) + '/geo/',
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 404:
                raise IpAddressNotFoundError(ip_address)
            elif request.status_code == 429:
                raise LimitExceededError()
            elif request.status_code == 500:
                raise InvalidRequestError()
            else:
                raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content.get('country'):
            ip_location.country = content['country']
        else:
            ip_location.country = None

        if content.get('region'):
            ip_location.region = content['region']
        else:
            ip_location.region = None

        if content.get('city'):
            ip_location.city = content['city']
        else:
            ip_location.city = None

        if content.get('loc'):
            location = content['loc'].split(',')
            ip_location.latitude = float(location[0])
            ip_location.longitude = float(location[1])
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class Eurek(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by https://www.eurekapi.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('https://https-api.eurekapi.com/iplocation/v1.8/locateip?'
                                   + 'ip=' + quote(ip_address)
                                   + '&key=' + quote(api_key)
                                   + '&format=JSON',
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 429:
                raise LimitExceededError()
            elif request.status_code == 500:
                raise InvalidRequestError()
            else:
                raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # check for errors
        if content['query_status']['query_status_code'] != 'OK':
            error_status = content['query_status']['query_status_code']
            error_status_desc = content['query_status']['query_status_description']

            if error_status == 'MISSING_SERVICE_ACCESS_KEY' \
               or error_status == 'INVALID_SERVICE_ACCESS_KEY' \
               or error_status == 'FREE_TRIAL_LICENSE_EXPIRED' \
               or error_status == 'SUBSCRIPTION_EXPIRED':
                raise PermissionRequiredError(error_status_desc)
            elif error_status == 'MISSING_IP_ADDRESS' \
                 or error_status == 'INVALID_IP_ADDRESS':
                raise IpAddressNotFoundError(ip_address)
            else:
                ip_location.country = None
                ip_location.region = None
                ip_location.city = None
                ip_location.latitude = None
                ip_location.longitude = None
                return ip_location

        # format data
        if content.get('geolocation_data'):
            if content['geolocation_data'].get('country_code_iso3166alpha2'):
                ip_location.country = content['geolocation_data']['country_code_iso3166alpha2']
            else:
                ip_location.country = None

            if content['geolocation_data'].get('region_name'):
                ip_location.region = content['geolocation_data']['region_name']
            else:
                ip_location.region = None

            if content['geolocation_data'].get('city'):
                ip_location.city = content['geolocation_data']['city']
            else:
                ip_location.city = None

            if content['geolocation_data'].get('latitude') \
               and content['geolocation_data'].get('longitude'):
                ip_location.latitude = float(content['geolocation_data']['latitude'])
                ip_location.longitude = float(content['geolocation_data']['longitude'])
            else:
                ip_location.latitude = None
                ip_location.longitude = None
        else:
            ip_location.country = None
            ip_location.region = None
            ip_location.city = None
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class Ipdata(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by https://ipdata.co/.

    """

    @staticmethod
    def get(ip_address, api_key='test', db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('https://api.ipdata.co/' + quote(ip_address)
                                   + '?api-key=' + quote(api_key),
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200 and request.status_code != 400:
            if request.status_code == 401:
                raise PermissionRequiredError()
            elif request.status_code == 403:
                raise LimitExceededError()
            else:
                raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # check for errors
        if content.get('message'):
            if 'private IP address' in content['message']:
                raise IpAddressNotFoundError(ip_address)
            else:
                raise InvalidRequestError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content['country_code'] == '':
            ip_location.country = None
        else:
            ip_location.country = content['country_code']

        if content['region'] == '':
            ip_location.region = None
        else:
            ip_location.region = content['region']

        if content['city'] == '':
            ip_location.city = None
        else:
            ip_location.city = content['city']

        if content['latitude'] != '-' and content['longitude'] != '-':
            ip_location.latitude = float(content['latitude'])
            ip_location.longitude = float(content['longitude'])
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location

