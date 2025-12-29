import telnetlib


def read_telnet_window(host: str, port: int, command: bytes, until_read=b"Waiting For Command:"):
    with telnetlib.Telnet(host, port) as tn:
        telnet_data = tn.read_until(until_read).decode()
        tn.write(command)
        telnet_data = tn.read_until(until_read).decode()
        return telnet_data
