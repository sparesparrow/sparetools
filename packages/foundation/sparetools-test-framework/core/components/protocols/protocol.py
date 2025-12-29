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
/
// File Name: protocol.py
//
// Program:   TITAN
//
// Purpose:   Abstract protocol base class for communication protocols.
//
// Notes:     Defines common interface for all communication protocols.
//            Implementations should preserve existing logic.
//
//********************************************************************************************
//********************************************************************************************
"""

import abc
import logging

log = logging.getLogger('__main__.' + __name__)


class CommunicationProtocol(metaclass=abc.ABCMeta):
    """
    Abstract base class for communication protocols.
    All protocol implementations should inherit from this class.
    """

    @abc.abstractmethod
    def __init__(self, address, **kwargs):
        """Initialize the protocol with connection parameters."""
        pass

    @abc.abstractmethod
    def connect(self, address, **kwargs):
        """Establish connection to the target."""
        pass

    @abc.abstractmethod
    def disconnect(self):
        """Close the connection."""
        pass

    @abc.abstractmethod
    def send_data(self, data):
        """Send data through the protocol."""
        pass

    @abc.abstractmethod
    def receive_data(self):
        """Receive data through the protocol."""
        pass

    @abc.abstractmethod
    def upload_file(self, local_path, remote_path):
        """Upload a file to the remote system."""
        pass

    @abc.abstractmethod
    def download_file(self, remote_path, local_path):
        """Download a file from the remote system."""
        pass

    @abc.abstractmethod
    def delete_file(self, remote_path):
        """Delete a file on the remote system."""
        pass

    @abc.abstractmethod
    def list_directory(self, remote_path):
        """List contents of a remote directory."""
        pass