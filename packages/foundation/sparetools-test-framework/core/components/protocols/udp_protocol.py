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
import logging
import queue
import socket
import time
from threading import Thread

log = logging.getLogger('__main__.' + __name__)


class UdpClientSocket:
    def __init__(self, addr, new_data_notification):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(addr)
        self.queue = queue.Queue()
        self.addr = addr
        self.new_data_notification = new_data_notification
        Thread(target=self.datagram_received, name='IO UDP Client thread', daemon=True).start()

    def get_queue(self):
        return self.queue

    def send_data(self, message):
        try:
            log.debug(f'UdpClient: Send: {message} with size: {len(message)}')
            self.socket.sendto(message, self.addr)
        except Exception as e:
            log.exception(e)

    def datagram_received(self):
        while 1:
            while 1:
                try:
                    message, remote_node = self.socket.recvfrom(10 * 1024)
                    break
                except ConnectionResetError:
                    self.socket.connect(self.addr)
                    time.sleep(1)
            log.debug(f'UdpServer: Received data with size: {len(message)} data: {message}  from {remote_node}')
            self.queue.put(message)
            if self.new_data_notification:
                self.new_data_notification()


class UDPProtocol:
    """
    Thin wrapper around existing UdpClientSocket class.
    Provides protocol interface while preserving 100% of existing UDP logic.
    """

    def __init__(self, address, new_data_notification=None, **kwargs):
        self._impl = UdpClientSocket(address, new_data_notification)

    def connect(self, address, **kwargs):
        # UDP is connectionless, but we can store the address
        self._impl.addr = address
        return True

    def disconnect(self):
        # UDP doesn't have explicit disconnect, but we can close the socket
        if hasattr(self._impl, 'socket'):
            self._impl.socket.close()
        return True

    def send_data(self, data):
        return self._impl.send_data(data)

    def receive_data(self):
        # UDP is asynchronous, return queue for data
        return self._impl.get_queue()

    def upload_file(self, local_path, remote_path):
        raise NotImplementedError("UDP protocol doesn't support file operations")

    def download_file(self, remote_path, local_path):
        raise NotImplementedError("UDP protocol doesn't support file operations")

    def delete_file(self, remote_path):
        raise NotImplementedError("UDP protocol doesn't support file operations")

    def list_directory(self, remote_path):
        raise NotImplementedError("UDP protocol doesn't support file operations")
