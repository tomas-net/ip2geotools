# -*- coding: utf-8 -*-
"""
Noncommercial geolocation databases
===================================

These classes access many different free geolocation databases.

"""
# pylint: disable=no-member
from __future__ import absolute_import
import json
from urllib.parse import quote
import requests
import geocoder
import geoip2.database
import IP2Location

from ip2geotools.databases.interfaces import IGeoIpDatabase
from ip2geotools.models import IpLocation
from ip2geotools.errors import IpAddressNotFoundError, PermissionRequiredError, \
                                InvalidRequestError, InvalidResponseError, ServiceError, \
                                LimitExceededError


class DbIpCity(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by https://db-ip.com/api/.

    """

    @staticmethod
    def get(ip_address, api_key='free', db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('http://api.db-ip.com/v2/'
                                   + quote(api_key)
                                   + '/' + quote(ip_address),
                                   timeout=62)
        except:
            raise ServiceError()
        
        # check for HTTP errors
        if request.status_code != 200:
            raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # check for errors
        if content.get('error'):
            if content['error'] == 'invalid address':
                raise IpAddressNotFoundError(ip_address)
            elif content['error'] == 'invalid API key':
                raise PermissionRequiredError()
            else:
                raise InvalidRequestError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        ip_location.country = content['countryCode']
        ip_location.region = content['stateProv']
        ip_location.city = content['city']

        # get lat/lon from OSM
        osm = geocoder.osm(ip_location.city + ', '
                           + ip_location.region + ' '
                           + ip_location.country,
                           timeout=62)

        if osm.ok:
            osm = osm.json
            ip_location.latitude = float(osm['lat'])
            ip_location.longitude = float(osm['lng'])
        else:
            osm = geocoder.osm(ip_location.city + ', ' + ip_location.country, timeout=62)

            if osm.ok:
                osm = osm.json
                ip_location.latitude = float(osm['lat'])
                ip_location.longitude = float(osm['lng'])
            else:
                ip_location.latitude = None
                ip_location.longitude = None

        return ip_location


class HostIP(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by http://hostip.info/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('http://api.hostip.info/get_json.php?position=true&ip='
                                   + quote(ip_address),
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 404:
                raise IpAddressNotFoundError(ip_address)
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
        if content['country_code'] == 'XX':
            ip_location.country = None
        else:
            ip_location.country = content['country_code']

        ip_location.region = None

        if content['city'] == '(Unknown City?)' \
           or content['city'] == '(Unknown city)' \
           or content['city'] == '(Private Address)':
            ip_location.city = None
        else:
            ip_location.city = content['city']

        if content.get('lat') and content.get('lng'):
            ip_location.latitude = float(content['lat'])
            ip_location.longitude = float(content['lng'])
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class Freegeoip(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by http://freegeoip.net/.
    Freegeoip database is deprecated!

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        """
        # process request
        try:
            request = requests.get('http://freegeoip.net/json/' + quote(ip_address),
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            if request.status_code == 404:
                raise IpAddressNotFoundError(ip_address)
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
        if content['country_code'] == '':
            ip_location.country = None
        else:
            ip_location.country = content['country_code']

        if content['region_name'] == '':
            ip_location.region = None
        else:
            ip_location.region = content['region_name']

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

        """
        raise ServiceError('Freegeoip database is deprecated!')


class Ipstack(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by http://ipstack.com/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = requests.get('http://api.ipstack.com/' + quote(ip_address)
                                   + '?access_key=' + quote(api_key),
                                   timeout=62)
        except:
            raise ServiceError()

        # check for HTTP errors
        if request.status_code != 200:
            raise ServiceError()

        # parse content
        try:
            content = request.content.decode('utf-8')
            content = json.loads(content)
        except:
            raise InvalidResponseError()

        # check for errors
        if content.get('error'):
            if content['error']['code'] == 101 \
                or content['error']['code'] == 102 \
                or content['error']['code'] == 105:
                raise PermissionRequiredError()
            elif content['error']['code'] == 104:
                raise LimitExceededError()
            else:
                raise InvalidRequestError()

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if content['country_code'] == '':
            ip_location.country = None
        else:
            ip_location.country = content['country_code']

        if content['region_name'] == '':
            ip_location.region = None
        else:
            ip_location.region = content['region_name']

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


class MaxMindGeoLite2City(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by GeoLite2 database
    created by MaxMind, available from https://www.maxmind.com/.
    Downloadable from https://dev.maxmind.com/geoip/geoip2/geolite2/.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            request = geoip2.database.Reader(db_path)
        except:
            raise ServiceError()

        # content
        try:
            res = request.city(ip_address)
        except TypeError:
            raise InvalidRequestError()
        except geoip2.errors.AddressNotFoundError:
            raise IpAddressNotFoundError(ip_address)

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if res.country:
            ip_location.country = res.country.iso_code
        else:
            ip_location.country = None

        if res.subdivisions:
            ip_location.region = res.subdivisions[0].names['en']
        else:
            ip_location.region = None

        if res.city.names:
            ip_location.city = res.city.names['en']
        else:
            ip_location.city = None

        if res.location:
            ip_location.latitude = float(res.location.latitude)
            ip_location.longitude = float(res.location.longitude)
        else:
            ip_location.latitude = None
            ip_location.longitude = None

        return ip_location


class Ip2Location(IGeoIpDatabase):
    """
    Class for accessing geolocation data provided by IP2Location,
    available from https://www.ip2location.com/.
    Downloadable from http://lite.ip2location.com/database/ip-country-region-city-latitude-longitude.

    """

    @staticmethod
    def get(ip_address, api_key=None, db_path=None, username=None, password=None):
        # process request
        try:
            ip2loc = IP2Location.IP2Location()
            ip2loc.open(db_path)
        except:
            raise ServiceError()

        # content
        res = ip2loc.get_all(ip_address)

        if res is None:
            raise IpAddressNotFoundError(ip_address)

        # prepare return value
        ip_location = IpLocation(ip_address)

        # format data
        if res.country_short != ' ' \
           or res.country_short == 'N/A' \
           or res.country_short == '??':
            ip_location.country = res.country_short.decode('utf-8')
        else:
            ip_location.country = None

        if res.region != ' ' \
           or res.region == 'N/A':
            ip_location.region = res.region.decode('utf-8')
        else:
            ip_location.region = None

        if res.city != ' ' \
           or res.city == 'N/A':
            ip_location.city = res.city.decode('utf-8')
        else:
            ip_location.city = None

        if res.latitude != ' ' \
           or res.latitude == 'N/A':
            ip_location.latitude = float(res.latitude)
        else:
            ip_location.latitude = None

        if res.longitude != ' ' \
           or res.longitude == 'N/A':
            ip_location.longitude = float(res.longitude)
        else:
            ip_location.longitude = None

        return ip_location

