"""
Process Management Utilities

Based on ngapy-dev/ngapy/util/process.py
"""

import logging
import ctypes
import multiprocessing
import os
import queue
import signal
import threading
import time
from ctypes import Structure
from ctypes import c_long, c_uint, c_char
from ctypes import sizeof, pointer
from pathlib import Path

log = logging.getLogger(__name__)

# Windows-specific imports (with fallback)
try:
    import win32api
    import win32con
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    log.warning("psutil not available, some process functions will be limited")

try:
    Kernel32 = ctypes.WinDLL('kernel32.dll')
    HAS_KERNEL32 = True
except:
    HAS_KERNEL32 = False

# Constants
TH32CS_SNAPPROCESS = 2


# Copied from ngapy/util/process.py
class Logger(multiprocessing.Process):
    """
    Process logger for capturing output from subprocesses.
    
    Based on ngapy/util/process.py Logger class.
    """
    class LoggerWriter:
        def __init__(self, queue):
            self.queue = queue

        def write(self, message):
            for line in message.rstrip().splitlines():
                self.queue.put(line.rstrip())

        def flush(self):
            pass

    @staticmethod
    def logged_worker(logger_queue, log_level, worker, *args, **kwargs):
        import sys
        sys.stdout = sys.stderr = Logger.LoggerWriter(logger_queue)
        logging.basicConfig(format="%(message)s", level=log_level)
        try:
            worker(*args, **kwargs)
        except:
            pass
        logger_queue.put(None)

    @staticmethod
    def process_logger(level, process, logger_queue, name):
        log.log(level, f"[PROCESS {process.pid} {name}] Started process logging")
        while True:
            try:
                if not process.is_alive():
                    raise EOFError()
                msg = logger_queue.get(timeout=1)
                if msg is None:
                    raise EOFError()
                log.log(level, f"[PROCESS {process.pid} {name}] {msg}")
            except queue.Empty:
                pass  # timeout
            except (EOFError, OSError):
                break  # queue closed
            except Exception as e:
                log.log(level, f"[PROCESS {process.pid} {name}] Unexpected exception {e}")
                break

        log.log(level, f"[PROCESS {process.pid} {name}] Finished process logging")

    def __init__(self, target, log_name='', log_level=logging.DEBUG, args=(), kwargs={}):
        self.logger_queue = multiprocessing.Queue()
        self.log_name = log_name
        self.log_level = log_level
        super().__init__(target=self.logged_worker, args=(self.logger_queue, self.log_level, target, *args),
                         kwargs=kwargs)

    def start(self):
        super().start()
        logger_t = threading.Thread(target=self.process_logger,
                                    args=(logging.DEBUG, self, self.logger_queue, self.log_name))
        logger_t.setDaemon(True)
        logger_t.start()

    def terminate(self):
        super().terminate()
        super().join()
        self.logger_queue.put(None)


# Copied from ngapy/util/process.py
class PROCESSENTRY32(Structure):
    """Windows process entry structure."""
    _fields_ = [('dwSize', c_uint),
                ('cntUsage', c_uint),
                ('th32ProcessID', c_uint),
                ('th32DefaultHeapID', c_uint),
                ('th32ModuleID', c_uint),
                ('cntThreads', c_uint),
                ('th32ParentProcessID', c_uint),
                ('pcPriClassBase', c_long),
                ('dwFlags', c_uint),
                ('szExeFile', c_char * 260),
                ('th32MemoryBase', c_long),
                ('th32AccessKey', c_long)]


# Copied from ngapy/util/process.py
def __run_independent_process_internal(result, *args, **kwargs):
    from subprocess import Popen
    proc = Popen(*args, **kwargs)
    result['pid'] = proc.pid


# Copied from ngapy/util/process.py
def run_independent_process(*args, **kwargs):
    """
    Helper method for starting independent process (no child process indicated in process explorer).
    CAUTION: Calling of this method requires that very first script uses the if __main__ == .... idiom.
    
    Based on ngapy/util/process.py run_independent_process function.

    Args:
        args, kwargs: argument that would be otherwise passed to Popen

    Returns:
        Pid of the created process. None if process did not start for any reason.
    """
    from multiprocessing import Process, Manager

    # ensure the process is detached, so that it is not terminated
    # immediately after p.join()
    DETACHED_PROCESS = 0x00000008
    cf = kwargs.get("creationflags", 0)
    kwargs["creationflags"] = cf | DETACHED_PROCESS
    result = Manager().dict()

    # spawn Process() from which Popen() will be called. Popen process will be child of
    # Process process, but that one will terminate immediately, hence we end up
    # with process that has no traceable parent - an independent process
    p = Process(target=__run_independent_process_internal, args=(result, *args), kwargs=kwargs)
    p.start()
    p.join()

    # fetch the process id from shared queue
    return result.get('pid', None)


# Copied from ngapy/util/process.py
def get_processes_info_by_names(process_name=()):
    """
    Get process information by process names.
    
    Based on ngapy/util/process.py get_processes_info_by_names function.
    """
    if not HAS_KERNEL32:
        return {}
    
    h_process_snap = Kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)
    ret = Kernel32.Process32First(h_process_snap, pointer(pe32))

    if isinstance(process_name, str):
        process_name = {process_name}

    process_name = {name.lower() for name in process_name}

    info = {}
    while ret:
        process = pe32.szExeFile.decode('ascii').lower()

        if process in process_name or not process_name:
            if process not in info:
                info[process] = []
            info[process].append(
                dict(pid=pe32.th32ProcessID, threads=pe32.cntThreads, parent=pe32.th32ParentProcessID))
        ret = Kernel32.Process32Next(h_process_snap, pointer(pe32))
    return info


# Copied from ngapy/util/process.py
def get_processes_info_by_pids(process_id=()):
    """
    Get process information by process IDs.
    
    Based on ngapy/util/process.py get_processes_info_by_pids function.
    """
    if not HAS_KERNEL32:
        return {}
    
    h_process_snap = Kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)
    ret = Kernel32.Process32First(h_process_snap, pointer(pe32))

    if isinstance(process_id, int):
        process_id = {process_id}

    info = {}
    while ret:
        process = pe32.szExeFile.decode('utf-8').lower()
        if pe32.th32ProcessID in process_id or not process_id:
            if pe32.th32ProcessID not in info:
                info[pe32.th32ProcessID] = []
            info[pe32.th32ProcessID].append(
                dict(name=process, threads=pe32.cntThreads, parent=pe32.th32ParentProcessID))
        ret = Kernel32.Process32Next(h_process_snap, pointer(pe32))
    return info


# Copied from ngapy/util/process.py
def is_process_running_by_pid(pid):
    """
    Helper method to detect whether process is running or not (no taskkill).
    
    Based on ngapy/util/process.py is_process_running_by_pid function.

    Args:
        pid (int): pid of the process

    Returns:
        True if process has been found, False otherwise
    """
    processes = get_processes_info_by_pids(pid)
    return pid in processes


# Copied from ngapy/util/process.py
def is_process_running_by_name(process_name):
    """
    Helper method to detect whether process is running or not (no taskkill).
    
    Based on ngapy/util/process.py is_process_running_by_name function.

    Args:
        process_name (str): name of the process (e.g. 'MIS_RT.exe')

    Returns:
        True if process has been found, False otherwise
    """
    processes = get_processes_info_by_names(process_name)
    return process_name.lower() in processes


# Copied from ngapy/util/process.py
def kill_proc_tree(pid=os.getpid(), sig=signal.SIGTERM, include_parent=False,
                   timeout=None, on_terminate=None, exceptions=[]):
    """
    Kill a process tree.
    
    Based on ngapy/util/process.py kill_proc_tree function.
    """
    if not HAS_PSUTIL:
        log.warning("psutil not available, kill_proc_tree not supported")
        return [], []
    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    children = list(filter(lambda p: p.name() != 'conhost.exe', children))
    if include_parent:
        children.append(parent)
    for p in children:
        if p.name() in exceptions:
            continue
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return gone, alive


# Copied from ngapy/util/process.py
def kill_processes_by_name(process_name):
    """
    Helper method for killing process from within python (no taskkill).
    
    Based on ngapy/util/process.py kill_processes_by_name function.

    Args:
        process_name (str, iterable): name of the process (e.g. 'MIS_RT.exe') or list of names

    Returns:
        True if process has been killed, False otherwise
    """
    sucess_indicator = 0
    taskkill_string = r'taskkill /f '
    for process in process_name:
        taskkill_string += f" /im  {process}"
    taskkill_string += r' 2>NUL'

    sucess_indicator = + os.system(taskkill_string)

    return sucess_indicator != 0


# Copied from ngapy/util/process.py
def kill_processes_by_pid(pid):
    """
    Helper method for killing process from within python (no taskkill).
    
    Based on ngapy/util/process.py kill_processes_by_pid function.

    Args:
        pid (int): id of the process

    Returns:
        True if process has been killed, False otherwise
    """
    if not HAS_WIN32:
        log.warning("win32api not available, kill_processes_by_pid not supported")
        return False
    
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
        win32api.TerminateProcess(handle, 0)
        win32api.CloseHandle(handle)
        log.info(f"Successfully killed process PID:{pid}")
        return True
    except Exception as e:
        log.warning(f"Could not kill process PID:{pid} ({str(e)})")
        return False


# Copied from ngapy/util/process.py
def get_process_windows_titles(pid):
    """
    Method to get list of window titles (captions) for given process id.
    
    Based on ngapy/util/process.py get_process_windows_titles function.

    Args:
        pid (int): process id

    Returns:
        (list): List of titles
    """
    if not HAS_WIN32:
        return []
    
    test_titles = []

    def check_title_callback(hwnd, procid):
        """Callback necessary for getting title from enumerated windows."""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        ignores = ['MSCTFIME ui', 'Default IME']
        if pid == procid:

            title = win32gui.GetWindowText(hwnd)
            if title not in ignores:
                test_titles.append(title)

    win32gui.EnumWindows(check_title_callback, pid)
    return test_titles


# Copied from ngapy/util/process.py
def get_process_by_name(process_name: str, cmd_args=None) -> int:
    """
    Get process by name.
    
    Based on ngapy/util/process.py get_process_by_name function.
    """
    def make_list_from_variable(var):
        """Convert variable to list if not already."""
        if isinstance(var, (list, tuple)):
            return var
        return [var]
    
    if not HAS_PSUTIL:
        return None
    
    if cmd_args:
        cmd_args = make_list_from_variable(cmd_args)
    else:
        cmd_args = []
    for process in psutil.process_iter():
        if process.name() == process_name:
            if cmd_args:
                if cmd_args == [process.cmdline()[-len(cmd_args)]]:
                    return process.pid
            else:
                return process.pid
    return None


# Copied from ngapy/util/process.py
def wait_for_application_start(application, timeout=10, cmd_args=None) -> bool:
    """
    Wait for application to start.
    
    Based on ngapy/util/process.py wait_for_application_start function.
    """
    application_name = Path(application).name
    for timeout in range(timeout):
        if get_process_by_name(application_name, cmd_args):
            return True
        time.sleep(1)
    else:
        return False
