# -*- coding: utf-8 -*-
"""
Errors
======

These classes provide special exceptions used when accessing data from
third-party geolocation databases.

"""
# pylint: disable=missing-docstring

import json
import dicttoxml


class LocationError(RuntimeError):
    """
    This class represents a generic location error. It extends
    :py:exc:`RuntimeError` and does not add any additional attributes.

    """

    def to_json(self):
        return json.dumps(
            {
                'error_type': type(self).__name__,
                'error_message': self.__str__()
            })

    def to_xml(self):
        return dicttoxml.dicttoxml(
            {
                'error_type': type(self).__name__,
                'error_message': self.__str__()
            },
            custom_root='ip_location_error',
            attr_type=False).decode()

    def to_csv(self, delimiter):
        return '%s%s%s' % (type(self).__name__, delimiter, self.__str__())


class IpAddressNotFoundError(LocationError):
    """
    The IP address was not found.

    """

    pass


class PermissionRequiredError(LocationError):
    """
    Problem with authentication or authorization of the request.
    Check your permission for accessing the service.

    """

    pass


class InvalidRequestError(LocationError):
    """
    Invalid request.

    """

    pass


class InvalidResponseError(LocationError):
    """
    Invalid response.

    """

    pass


class ServiceError(LocationError):
    """
    Response from geolocation database is invalid (not accessible, etc.)

    """

    pass


class LimitExceededError(LocationError):
    """
    Limits of geolocation database have been reached.

    """

    pass
