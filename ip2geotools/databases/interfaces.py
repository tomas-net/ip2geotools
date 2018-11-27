# -*- coding: utf-8 -*-
"""
Interfaces
==========

These classes provide interfaces for unifying access to the data provided
by geolocation databases.

"""
from abc import ABCMeta, abstractmethod


class IGeoIpDatabase:
    """
    Interface for unified access to the data provided by geolocation databases.

    """

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get(ip_address, api_key, db_path, username, password):
        """
        Method for getting location of given IP address.

        """

        raise NotImplementedError

