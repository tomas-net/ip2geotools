# -*- coding: utf-8 -*-
"""
Errors
======

These classes provide special exceptions used when accessing data from
third-party geolocation databases.

"""


class LocationError(RuntimeError):
    """
    This class represents a generic location error. It extends
    :py:exc:`RuntimeError` and does not add any additional attributes.

    """


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
