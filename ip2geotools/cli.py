# -*- coding: utf-8 -*-
"""
Cli
======

This module and its class `Command` and function `execute_from_command_line`
handle running basic functions of `ip2geotools` from command line interface.

"""
# pylint: disable=invalid-name

from __future__ import print_function
import argparse
import codecs
import os
import sys
import json
import dicttoxml

import ip2geotools
from ip2geotools.databases.noncommercial import DbIpCity, \
                                                HostIP, \
                                                Freegeoip, \
                                                Ipstack, \
                                                MaxMindGeoLite2City, \
                                                Ip2Location
from ip2geotools.databases.commercial import DbIpWeb, \
                                             MaxMindGeoIp2City, \
                                             Ip2LocationWeb, \
                                             NeustarWeb, \
                                             GeobytesCityDetails, \
                                             SkyhookContextAcceleratorIp, \
                                             IpInfo, \
                                             Eurek, \
                                             Ipdata
from ip2geotools.models import IpLocation
from ip2geotools.errors import LocationError


class Command(object):
    """
    Class for running ip2geotools from cli.

    """

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def execute(self):
        """
        Given the command-line arguments, this creates a parser appropriate
        to that command and runs it.

        """

        # args parser
        parser = argparse.ArgumentParser(
            prog=self.prog_name,
            description='{0} version {1}'.format(self.prog_name, ip2geotools.__version__) + \
                        '\n\n{0}'.format(ip2geotools.__description__),
            epilog=('\n\nexample:' + \
                   '\n  get information on 147.229.2.90 from DB-IP API in JSON format' + \
                   '\n    {prog_name} 147.229.2.90 -d dbipcity -f json' + \
                   '\n\nauthor:' + \
                   '\n  {prog_name} was written by {author} <{author_email}> ' + \
                   'for master\'s thesis at FEEC BUT 2018/2019').format(
                       prog_name=self.prog_name,
                       author=ip2geotools.__author__,
                       author_email=ip2geotools.__author_email__),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=True)

        parser.add_argument('IP_ADDRESS',
                            help='IP address to be checked')

        parser.add_argument('-d', '--database',
                            help='geolocation database to be used (case insesitive)',
                            dest='database',
                            required=True,
                            type=str.lower,
                            choices=[
                                #'all',

                                # noncommercial
                                'dbipcity',
                                'hostip',
                                'freegeoip',
                                'ipstack',
                                'maxmindgeolite2city',
                                'ip2location',

                                # commercial
                                'dbipweb',
                                'maxmindgeoip2city',
                                'ip2locationweb',
                                'neustarweb',
                                'geobytescitydetails',
                                'skyhookcontextacceleratorip',
                                'ipinfo',
                                'eurek',
                                'ipdata',
                            ])

        parser.add_argument('--api_key',
                            help='API key for given geolocation database (if needed)',
                            dest='api_key')

        parser.add_argument('--db_path',
                            help='path to geolocation database file (if needed)',
                            dest='db_path')

        parser.add_argument('-u', '--username',
                            help='username for accessing given geolocation database (if needed)',
                            dest='username')

        parser.add_argument('-p', '--password',
                            help='password for accessing given geolocation database (if needed)',
                            dest='password')

        parser.add_argument('-f', '--format',
                            help='output data format',
                            dest='format',
                            required=False,
                            default='inline',
                            type=str.lower,
                            choices=[
                                'json',
                                'xml',
                                'csv-space',
                                'csv-tab',
                                'inline'
                            ])

        parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s {0}'.format(ip2geotools.__version__))

        # parse cli arguments
        arguments = parser.parse_args(self.argv[1:])

        # process requests
        ip_location = IpLocation('0.0.0.0')

        try:
            # noncommercial databases
            if arguments.database == 'dbipcity':
                if arguments.api_key:
                    ip_location = DbIpCity.get(arguments.IP_ADDRESS,
                                               api_key=arguments.api_key)
                else:
                    ip_location = DbIpCity.get(arguments.IP_ADDRESS)
            elif arguments.database == 'hostip':
                ip_location = HostIP.get(arguments.IP_ADDRESS)
            elif arguments.database == 'freegeoip':
                ip_location = Freegeoip.get(arguments.IP_ADDRESS)
            elif arguments.database == 'ipstack':
                ip_location = Ipstack.get(arguments.IP_ADDRESS,
                                          api_key=arguments.api_key)
            elif arguments.database == 'maxmindgeolite2city':
                ip_location = MaxMindGeoLite2City.get(arguments.IP_ADDRESS,
                                                      db_path=arguments.db_path)
            elif arguments.database == 'ip2location':
                ip_location = Ip2Location.get(arguments.IP_ADDRESS,
                                              db_path=arguments.db_path)

            # commercial databases
            elif arguments.database == 'dbipweb':
                ip_location = DbIpWeb.get(arguments.IP_ADDRESS)
            elif arguments.database == 'maxmindgeoip2city':
                ip_location = MaxMindGeoIp2City.get(arguments.IP_ADDRESS)
            elif arguments.database == 'ip2locationweb':
                ip_location = Ip2LocationWeb.get(arguments.IP_ADDRESS)
            elif arguments.database == 'neustarweb':
                ip_location = NeustarWeb.get(arguments.IP_ADDRESS)
            elif arguments.database == 'geobytescitydetails':
                ip_location = GeobytesCityDetails.get(arguments.IP_ADDRESS)
            elif arguments.database == 'skyhookcontextacceleratorip':
                ip_location = SkyhookContextAcceleratorIp.get(arguments.IP_ADDRESS,
                                                              username=arguments.username,
                                                              password=arguments.password)
            elif arguments.database == 'ipinfo':
                ip_location = IpInfo.get(arguments.IP_ADDRESS)
            elif arguments.database == 'eurek':
                ip_location = Eurek.get(arguments.IP_ADDRESS,
                                        api_key=arguments.api_key)
            elif arguments.database == 'ipdata':
                if arguments.api_key:
                    ip_location = Ipdata.get(arguments.IP_ADDRESS,
                                               api_key=arguments.api_key)
                else:
                    ip_location = Ipdata.get(arguments.IP_ADDRESS)

            # print formatted output
            if arguments.format == 'json':
                print(ip_location.to_json())
            elif arguments.format == 'xml':
                print(ip_location.to_xml())
            elif arguments.format == 'csv-space':
                print(ip_location.to_csv(' '))
            elif arguments.format == 'csv-tab':
                print(ip_location.to_csv('\t'))
            elif arguments.format == 'inline':
                print(ip_location)
        except LocationError as e:
            # print formatted output
            if arguments.format == 'json':
                print(e.to_json())
            elif arguments.format == 'xml':
                print(e.to_xml())
            elif arguments.format == 'csv-space':
                print(e.to_csv(' '))
            elif arguments.format == 'csv-tab':
                print(e.to_csv('\t'))
            elif arguments.format == 'inline':
                print('%s: %s' % (type(e).__name__, e.__str__()))


def execute_from_command_line(argv=None):
    """
    A simple method that runs a Command.

    """

    if sys.stdout.encoding is None:
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    if sys.version_info.major != 3:
        print('Error: This script is intended to be run with Python 3', file=sys.stderr)
        sys.exit(1)

    command = Command(argv)
    command.execute()
