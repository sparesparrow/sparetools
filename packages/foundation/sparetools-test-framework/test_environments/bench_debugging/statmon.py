from sparetools.test_environments.bench_debugging.telnet import read_telnet_window
import re

class StatmonReader:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def read_process_list(self):
        processes = {}
        read_data = read_telnet_window(self.host, self.port, b'r s p \n')
        for line in read_data.splitlines()[2:-1]:
            line = re.sub(' +', ' ', line)
            parts = line.split(' ')
            processes[parts[1]] = parts
        return processes
