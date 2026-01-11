"""
Networking Core

Network utilities for IP management, socket operations, and port checking.
Based on ngapy-dev/ngapy/util/net.py, ngapy/util/sockets.py, and ngapy/core/utilities.py
Extended with additional network utilities.
"""

import logging
import socket
import struct
import subprocess
from typing import Optional

log = logging.getLogger(__name__)

try:
    import netifaces as ni
    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False
    log.warning("netifaces not available, some network functions may be limited")


# Copied from ngapy/core/utilities.py
def find_address(address: str) -> bool:
    """
    Find if an IP address exists on any network interface.
    
    Based on ngapy/core/utilities.py find_address function.

    Args:
        address: IP address to check

    Returns:
        True if address found, False otherwise
    """
    if not HAS_NETIFACES:
        # Fallback: try basic socket check
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False

    for interface in ni.interfaces():
        settings = ni.ifaddresses(interface)
        if ni.AF_INET in settings:
            for ip4settings in settings[ni.AF_INET]:
                if ip4settings.get('addr') == address:
                    return True
    return False


# Copied from ngapy/util/net.py
def add_ip_to_adapter(ip_address: str, mask: str = "255.255.255.0",
                     adapter_name: str = "OPyTEe EPIC Sim Connection"):
    """
    Add IP address to a network adapter (Windows-specific).
    
    Based on ngapy/util/net.py add_ip_to_adapter function.

    Args:
        ip_address: IP address to add
        mask: Subnet mask
        adapter_name: Name of the network adapter

    Raises:
        EnvironmentError: If adapter not found or operation fails
    """
    if find_address(ip_address):
        return

    log.info("Address %s not found on the adapter, adding..." % ip_address)
    netsh = subprocess.Popen('netsh interface ipv4 add address "%s" %s %s'
                             % (adapter_name, ip_address, mask),
                             shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, errors = netsh.communicate()
    if output is not None and output.strip():
        # this might not be necessary an issue, the addresses might be already added
        # but due to VPN issues we cannot correctly detect it
        if 'already exists' in output.decode('UTF8').lower():
            # everything seems fine
            return

        # addition failed for another reason than already having the address registered, report...
        log.error("Failed to add address %s to the sim adapter (%s)" %
                                  (ip_address, output.strip()))
        raise EnvironmentError("Could not add address to \"%s\" adapter,"
                               " ensure the adapter is correctly installed" % adapter_name)


# Copied from ngapy/util/sockets.py
def send_to_socket_with_size(message: bytes, send_socket: socket.socket):
    """
    Send a message to socket with size prefix.
    
    Based on ngapy/util/sockets.py send_to_socket_with_size function.

    Args:
        message: Bytes to send
        send_socket: Socket to send to
    """
    total_send = 0
    message_with_len = struct.pack('I', len(message)) + message
    while total_send < len(message_with_len):
        total_send += send_socket.send(message_with_len[total_send:])


# Copied from ngapy/util/sockets.py
def recv_from_socket_with_size(recv_socket: socket.socket) -> bytes:
    """
    Receive a message from socket with size prefix.
    
    Based on ngapy/util/sockets.py recv_from_socket_with_size function.

    Args:
        recv_socket: Socket to receive from

    Returns:
        Received bytes
    """
    msg_size = recv_socket.recv(4)
    msg_size_decoded = struct.unpack('I', msg_size)[0]
    total_recv = b''
    while len(total_recv) < msg_size_decoded:
        total_recv += recv_socket.recv(msg_size_decoded - len(total_recv))
    return total_recv


def validate_ip_address(ip_address: str) -> bool:
    """
    Validate if a string is a valid IPv4 or IPv6 address.

    Args:
        ip_address: IP address string to validate

    Returns:
        True if valid IP address, False otherwise
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_address)
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip_address)
            return True
        except socket.error:
            return False


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Check if a port is open on a given host.

    Args:
        host: Hostname or IP address
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        log.warning(f"Error checking port {port} on {host}: {e}")
        return False


def find_available_port(start_port: int = 1024, end_port: int = 65535,
                       host: str = 'localhost') -> Optional[int]:
    """
    Find an available port in the given range.

    Args:
        start_port: Starting port number
        end_port: Ending port number
        host: Host to check against

    Returns:
        Available port number or None if none found
    """
    for port in range(start_port, end_port + 1):
        if not is_port_open(host, port):
            return port
    return None


def get_network_interfaces() -> dict:
    """
    Get information about all network interfaces.

    Returns:
        Dictionary mapping interface names to their IP addresses
    """
    interfaces = {}

    if HAS_NETIFACES:
        for interface in ni.interfaces():
            settings = ni.ifaddresses(interface)
            if ni.AF_INET in settings:
                interfaces[interface] = [
                    ip4.get('addr') for ip4 in settings[ni.AF_INET]
                    if ip4.get('addr')
                ]
    else:
        # Fallback: try to get hostname IPs
        try:
            hostname = socket.gethostname()
            interfaces['localhost'] = [socket.gethostbyname(hostname)]
        except Exception as e:
            log.warning(f"Failed to get network interfaces: {e}")

    return interfaces


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve a hostname to an IP address.

    Args:
        hostname: Hostname to resolve

    Returns:
        IP address string or None if resolution fails
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror as e:
        log.warning(f"Failed to resolve hostname {hostname}: {e}")
        return None


def create_tcp_server(host: str = 'localhost', port: int = 0) -> tuple[socket.socket, int]:
    """
    Create a TCP server socket bound to the given host and port.

    Args:
        host: Host to bind to
        port: Port to bind to (0 for auto-assign)

    Returns:
        Tuple of (socket, actual_port)
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    actual_port = server_socket.getsockname()[1]
    server_socket.listen(5)
    return server_socket, actual_port