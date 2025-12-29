import importlib
import os
import sys
import threading
import tkinter as tk
import win32api
import win32event
from multiprocessing import Process
from pathlib import Path
from time import sleep
from tkinter import messagebox
from winerror import ERROR_ALREADY_EXISTS

from sparetools_aerospace.products.ngaims.constants import EXIT_CODE_REBOOT



def mutex_test():
    """
    Try to create new mutex for SimTool. If not possible another instance is running
    :return: Mutex if no other SimTool is running, None otherwise
    """
    # create partially unique mutex name
    local_mutex = win32event.CreateMutex(None, False, "OpYtE_MuTeXaMs")
    last_error = win32api.GetLastError()

    if last_error == ERROR_ALREADY_EXISTS:
        return None
    else:
        return local_mutex


def show_tk_error(msg_text):
    """
    Shows error message using TK framework
    :param msg_text: Error to be shown
    :return: N/A
    """
    # hide main window
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("SimTool", msg_text)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, target_function):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()
        self.function_name = target_function

    def run(self):
        my_terminating_thread(self, self.function_name)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def my_terminating_thread(stoppable_thr, target_function):
    thread = Process(target=target_function)
    thread.daemon = True
    thread.start()

    while not stoppable_thr.stopped():
        sleep(0.250)
    thread.terminate()



def main():
    mutex = mutex_test()
    if not mutex:
        msg = "Could not start SimTool.\nAnother instance of SimTool is running."
        print(msg)
        show_tk_error(msg)
    else:

        try:
            if len(sys.argv) > 1:
                os.chdir(sys.argv[1])

            import sparetools_aerospace.products.ngaims.sim_tool
            import sparetools_aerospace.products.ngaims.sim_tool.cmcfgui as cmcf_gui
            

            cmcf_gui.run_cmcf_gui()
        except Exception as e:
            print(e)
            show_tk_error("Error in starting SimTool:\n" + str(e))
        finally:
            # do mutex cleanup
            try:
                win32event.ReleaseMutex(mutex)
            except Exception as e:
                # uncomment for debugging
                # print(e)
                pass


if __name__ == '__main__':
    main()
