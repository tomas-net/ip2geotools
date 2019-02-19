===========
ip2geotools
===========

Description
-----------

``ip2geotools`` is a simple tool for getting geolocation information on given IP address from various geolocation databases. This package provides an API for several geolocation databases.

Installation
------------

To install the ``ip2geotools`` module, type:

.. code-block:: bash

    $ pip install ip2geotools

Basic usage
-----------

.. code-block:: pycon

    >>> from ip2geotools.databases.noncommercial import DbIpCity
    >>> response = DbIpCity.get('147.229.2.90', api_key='free')
    >>> response.ip_address
    '147.229.2.90'
    >>> response.city
    'Brno (Brno střed)'
    >>> response.region
    'South Moravian'
    >>> response.country
    'CZ'
    >>> response.latitude
    49.1926824
    >>> response.longitude
    16.6182105
    >>> response.to_json()
    '{"ip_address": "147.229.2.90", "city": "Brno (Brno střed)", "region": "South Moravian", "country": "CZ", "latitude": 49.1926824, "longitude": 16.6182105}'
    >>> response.to_xml()
    '<?xml version="1.0" encoding="UTF-8" ?><ip_location><ip_address>147.229.2.90</ip_address><city>Brno (Brno střed)</city><region>South Moravian</region><country>CZ</country><latitude>49.1926824</latitude><longitude>16.6182105</longitude></ip_location>'
    >>> response.to_csv(',')
    '147.229.2.90,Brno (Brno střed),South Moravian,CZ,49.1926824,16.6182105'

Command-line usage
------------------

When installed, you can invoke ``ip2geotools`` from the command-line:

.. code:: bash

    ip2geotools [-h] -d {dbipcity,hostip,freegeoip,ipstack,maxmindgeolite2city,ip2location,dbipweb,maxmindgeoip2city,ip2locationweb,neustarweb,geobytescitydetails,skyhookcontextacceleratorip,ipinfo,eurek,ipdata}
                       [--api_key API_KEY] [--db_path DB_PATH] [-u USERNAME]
                       [-p PASSWORD] [-f {json,xml,csv-space,csv-tab,inline}] [-v]
                       IP_ADDRESS

Where:

* ``ip2geotools``: is the script when installed in your environment, in development you could use ``python -m ip2geotools`` instead

* ``IP_ADDRESS``: IP address to be checked

* ``-h``, ``--help``: show help message and exit

* ``-d {dbipcity,hostip,...,eurek}``: geolocation database to be used (case insesitive)

* ``--api_key API_KEY``: API key for given geolocation database (if needed)

* ``--db_path DB_PATH``: path to geolocation database file (if needed)

* ``-u USERNAME``, ``--username USERNAME``: username for accessing given geolocation database (if needed)

* ``-p PASSWORD``, ``--password PASSWORD``: password for accessing given geolocation database (if needed)

* ``-f {json,xml,csv-space,csv-tab,inline}``, ``--format {json,xml,csv-space,csv-tab,inline}``: output data format

* ``-v``, ``--version``: show program's version number and exit

Examples:

.. code:: bash

    $ ip2geotools 147.229.2.90 -d dbipcity -f json
    {"ip_address": "147.229.2.90", "city": "Brno (Brno st\u0159ed)", "region": "South Moravian", "country": "CZ", "latitude": 49.1926824, "longitude": 16.6182105}

Models
------

This module contains models for the data returned by geolocation databases
and these models are also used for comparison of given and provided data.

``ip2geotools.models.IpLocation``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Model for storing location of given IP address.

Attributes:

* ``ip_address``: IP address
* ``city``: city where IP address is located
* ``region``: region where IP address is located
* ``country``: country where IP address is located (two letters country code)
* ``latitude``: latitude where IP address is located
* ``longitude``: longitude where IP address is located

Methods:

* ``to_json``: returns model data in JSON format
* ``to_xml``: returns model data in XML format (root element: ``ip_location``)
* ``to_csv``: returns model data in CSV format separated by given delimiter
* ``__str__``: internal string representation of model, every single information on new line

Exceptions
----------

This module provides special exceptions used when accessing data from
third-party geolocation databases.

* ``ip2geotools.errors.LocationError``: a generic location error
* ``ip2geotools.errors.IpAddressNotFoundError``: the IP address was not found
* ``ip2geotools.errors.PermissionRequiredError``: problem with authentication or authorization of the request; check your permission for accessing the service
* ``ip2geotools.errors.InvalidRequestError``: invalid request
* ``ip2geotools.errors.InvalidResponseError``: invalid response
* ``ip2geotools.errors.ServiceError``: response from geolocation database is invalid (not accessible, etc.)
* ``ip2geotools.errors.LimitExceededError``: limits of geolocation database have been reached

Databases
---------

Following classes access many different noncommercial and commercial geolocation databases using defined interface.

``ip2geotools.databases.interfaces``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``IGeoIpDatabase``: interface for unified access to the data provided by various geolocation databases

``ip2geotools.databases.noncommercial``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``DbIpCity``: https://db-ip.com/api/
* ``HostIP``: http://hostip.info/
* ``Freegeoip``: http://freegeoip.net/ **Database is deprecated!**
* ``Ipstack``: https://ipstack.com/
* ``MaxMindGeoLite2City``: https://dev.maxmind.com/geoip/geoip2/geolite2/
* ``Ip2Location``: https://lite.ip2location.com/database/ip-country-region-city-latitude-longitude

``ip2geotools.databases.commercial``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``DbIpWeb``: https://db-ip.com/
* ``MaxMindGeoIp2City``: https://www.maxmind.com/
* ``Ip2LocationWeb``: https://www.ip2location.com/
* ``NeustarWeb``: https://www.neustar.biz/resources/tools/ip-geolocation-lookup-tool/
* ``GeobytesCityDetails``: http://geobytes.com/get-city-details-api/
* ``SkyhookContextAcceleratorIp``: http://www.skyhookwireless.com/
* ``IpInfo``: https://ipinfo.io/
* ``Eurek``: https://www.eurekapi.com/
* ``Ipdata``: https://ipdata.co/

Requirements
------------

This code requires Python 3.3+ and several other packages listed in ``requirements.txt``.

Support
-------

Please report all issues with this code using the `GitHub issue tracker
<https://github.com/tomas-net/ip2geotools/issues>`_

License
-------

``ip2geotools`` is released under the MIT License. See the bundled `LICENSE`_ file for details.

Author
------

``ip2geotools`` was written by Tomas Caha <tomas-net at seznam dot cz> for master\'s thesis at `FEEC <http://www.feec.vutbr.cz/>`_ `BUT <https://www.vutbr.cz/>`_  2018/2019.