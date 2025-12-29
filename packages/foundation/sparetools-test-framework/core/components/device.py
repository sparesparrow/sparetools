#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
"""
//********************************************************************************************
//
//
// File Name: device.py
//
// Program:   TITAN
//
// Purpose:   Device abstract class.
//
// Notes:  This module defines generic Device interface supporting things such as Start(), Stop(), ...
// Todo:   * Consider moving TIU Server Device to separate module
//
// .. _Google Python Style Guide:  http://google.github.io/styleguide/pyguide.html
//********************************************************************************************
//********************************************************************************************
"""

import abc


class IDevice(object, metaclass=abc.ABCMeta):
    """Interface class for all devices that can be Started, Stopped, Restarted, etc.
    """

    # An abstract base class for handling window navigation
    @abc.abstractmethod
    def init(self):
        """Initializes the device.
        """
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def start(self, delay=-1):
        """Starts the device.
        """
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def stop(self):
        """Stops the device.
        """
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def restart(self):
        """Restart the device.
        """
        raise NotImplementedError("Method not implemented.")


# base test object implementing all common methods
class DeviceConfig(object):
    """Base class for all classes having certain configuration.

    It internally maintains the configuration and provides generic methods
    for setting/getting such configuration..
    """

    def __init__(self):
        self.configuration = {}

    def set_configuration(self, configuration):
        """Sets given configuration.

        Args:
            configuration (dict): Dictionary of string keys and any values.
        """
        self.configuration.update(configuration)

    def get_configuration(self):
        """Prints all the configuration.
        """
        for key, val in list(self.configuration.items()):
            print(key + ": " + str(val))


# this could be updated by ENUM package approach introduced in Python 3
# Constants
EASE_TYPE = 0
MINI_BENCH_TYPE = 1
eBenchType = {'EASE': 0, 'BENCH': 1}

if __name__ == '__main__':
    print("Main of module: " + __file__ + "entered")
