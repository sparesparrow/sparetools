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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
//********************************************************************************************
//
//
// File Name: tprocedure.py
//
// Program:   TITAN
//
// Purpose:   TProcedure functions covering running tests, doing verification and producing test results
//
// Notes: List of TODOs below:
// - Add SW versions from TIU (e.g. CMCF and other useful SWs)
// - Add SLDBs information to header (LDI)
// - Agreed, that configuration folder will have same position all time
// - Agreed, that result folder will have same position all time and decide where to store it (e.g. defined in config file)
// - After bench introduce load verification, information about correct bench load should be shown (verify_environment)
// - Currently it is not possible to verify load content (verify_package_load)
// - If supported by ATE, obtain SW faults for reporting (verify_sw_faults_inactive)
//
//********************************************************************************************
//********************************************************************************************
"""
import datetime
import inspect
import logging
import os
import pathlib
import sys
# standard
import platform
import threading
import time
# gui specific
import tkinter.filedialog
import tkinter.font
import traceback
from tkinter import *
from typing import Optional

import tkinterhtml

# external
import ngapy
import test_harness
from ngapy.util.file_operations import create_whole_dir_path
from sparetools.core.configuration.providers.env_provider import get_config_from_env
from test_harness import run_test, test_logging

th_logger = None
ngapy_th = None
dng_json = None
config_loader = None
debug_logs = False


def formatted_test_header(header_dict):
    """
    Generates basic Test case header. It prints various system variables.
    :param header_dict: dictionary containing Test case information
    :type header_dict: dict
    :return: formatted header text
    :rtype: str
    """

    header = f"""
==============================================================================
File Name               :  {header_dict.get('filename', '<UNKNOWN>')}
Program                 :  TITAN
Test Description        :  {header_dict.get('description', '<NO DESCRIPTION>')}
Notes                   :  {header_dict.get('notes', '<NO NOTES>')}

Machine Name            :  {os.getenv('COMPUTERNAME')}
Tester Name             :  {os.getenv('USERNAME')}
O/S Version             :  {platform.platform()}

Python Version          :  {sys.version}
Python Exe Location     :  {sys.executable}

NGAPy Version           :  {ngapy.__version__} ( {ngapy.__path__[0]} )
Test Harness Version    :  {test_harness.__version__} ( {test_harness.__path__[0]} )
=============================================================================="""

    return header


# Initialize private variables
__prompt_callback_function__ = None


def prompt_set_callback(func):
    """
    Registers custom callback.

    Example:

        tp.PromptSetCallback(myCallback)
        prompt = tp.Prompt("Is report printed?")

    :param func: prompt handling callback
    :type func: function
    :return: None
    :rtype: None
    """

    global __prompt_callback_function__
    __prompt_callback_function__ = func


def __prompt_default_callback(question):
    """
    Default callback question
    :param question: Question to be shown
    :type question: str
    :return: choice or None
    :rtype: bool
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}

    while True:
        print(question + " (Y/N):")
        choice = input().lower()
        if choice in valid:
            return valid[choice]


def __prompt_default_message_box_callback(question, buttons, timeout_value, title='TITAN Message Box'):
    """
    Message box definition for internal usage
    :param question: Question to be shown to user
    :type question: str
    :param buttons: Buttons to be shown
    :type buttons: list
    :param timeout_value: Timeout to close window automatically
    :type timeout_value: int
    :param title: Title of the message box
    :type title: str
    :return: Response from MSG box
    :rtype:
    """
    import pymsgbox
    if not buttons:
        buttons_selection = ["Yes", 'No']
    else:
        buttons_selection = buttons
    if timeout_value < 0:
        response = pymsgbox.confirm(question, title, buttons=buttons_selection)
    else:
        response = pymsgbox.confirm(question, title, buttons=buttons_selection,
                                    timeout=timeout_value * 1000)
    return response


def prompt_message_box(question, timeout=60, buttons=[], title='TITAN Message Box'):
    """
    Forces user to answer the prompt question using standard Y/N. It is possible to redirect
    prompt handling to different logic through callback (see PromptSetCallback)
    Example:

        prompt = tp.prompt_message_box("Is report printed?")
    :param question: Question to be asked
    :type question: str
    :param timeout: Timeout in seconds before msg box is closed
    :type timeout: int
    :param buttons: Buttons shown in msg box
    :type buttons: list
    :param title: Title of msg
    :type title: str
    :return: True if answer is yes, False if answer if no.
    :rtype: bool
    """
    if __prompt_callback_function__ is not None:
        return __prompt_callback_function__(question, buttons, timeout, title)
    else:
        return __prompt_default_message_box_callback(question, buttons, timeout, title)


def get_test_target_info():
    """
    Get test target info
    :return: Dict with header info
    :rtype: dict
    """
    header_dict = {}
    header_dict.update({"MachineName": os.getenv('COMPUTERNAME'),
                        "UserName": os.getenv('USERNAME'),
                        "OSVersion": platform.platform()})
    return header_dict


def _get_default_filename(routine):
    """
    Provides filename of currently executed script.
    :param routine: Executed script (function to be executed)
    :type routine: function
    :return: filename
    :rtype: str
    """
    return os.path.basename(inspect.getfile(routine))


def _get_default_desc(routine):
    """
    Provides default description of currently executed script.
    :param routine: function to be executed, usually RunTest in given module
    :type routine: funct
    :return: Description
    :rtype: str
    """
    try:
        module = inspect.getmodule(routine)
        description = module.run_test_description()
    except BaseException as e:
        description = "<NO DESCRIPTION>"

    return description


def exec(routine, header_dict=None):
    """
    Full independent execution of tp. This routine encapsulates logging, error handling and
    invokes Test case specific routine.

    Typical example would look like this:
        tp.exec(run_test, "PCAS File Integrity test")
    :param routine: function to be executed, usually RunTest in given module
    :type routine: function
    :param header_dict: dictionary with Test case information
    :type header_dict: dict
    :return: None
    :rtype: None
    """
    try:
        # Initialize the ConfigLoader with list of configuration paths
        global config_loader
        config_loader = get_repository_config()
        results_dir = None
        try:
            results_dir = config_loader.configuration.log_folder
        except AttributeError as e:
            logging.getLogger().warning(f"Missing configuration entry {e}")
        if not results_dir:
            results_dir = os.path.join(pathlib.Path(__file__).parent.parent, "results")

        create_whole_dir_path(results_dir)

        if not header_dict:
            header_dict = {'filename': _get_default_filename(routine),
                           'description': _get_default_desc(routine)}
        else:
            if not header_dict.get('filename', None):
                header_dict['filename'] = _get_default_filename(routine)
            if not header_dict.get('description', None):
                header_dict['description'] = _get_default_desc(routine)

        header_message = formatted_test_header(header_dict)

        _init()
        run_test(routine, results_dir_path=results_dir, header_message=header_message)

    except Exception as e:
        message(traceback.format_exc())

    return


def message(msg):
    """
    Writes test log message
    :param msg: Message
    :type msg: str
    :return: None
    :rtype: None
    """
    if debug_logs:
        th_logger.__test_log__.write_test_log(msg)
    else:
        return


def verify_local(actual, expected, operation, msg):
    """
    Local verification without caounting this result to final result
    :param actual: Actual parameter to verify
    :type actual: any
    :param expected: Expceted value
    :type expected: any
    :param operation: Operation to be used for comapring
    :type operation: str
    :param msg: Message to be shown with result
    :type msg: str
    :return: Result
    :rtype: bool
    """
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        verification_str = f'{actual}{operation}{expected}'
    else:
        verification_str = f'"{actual}"{operation}"{expected}"'

    result = eval(verification_str)
    message(msg=('MSG-INFO> Verify ' + msg))
    message(msg=('MSG-CHCK> ' + verification_str + ' with result ' + str(result)))
    return result


def _init():
    """
    nitializes the testharness utility.
    :return: None
    :rtype: None
    """
    global th_logger
    th_logger = test_harness.ThLogger()
    global ngapy_th
    ngapy_th = test_harness.NgapyTestHarnes()
    test_logging.__callback_function__ = None


def _on_verify(callback_function):
    """
    callback function to be called after each verification.
    :param callback_function: Callback function to be called
    :type callback_function: function
    :return: None
    :rtype: None
    """
    test_logging.__callback_function__ = callback_function


def verify_environment(bench_instance, tp_input_files):
    """
    Verifies the environment is ready for test execution
    :param bench_instance: Bench instance
    :type bench_instance: Bench
    :param tp_input_files: List of files TP requires
    :type tp_input_files: list
    :return: Boolean depending on existence of input files, TP platform being running
    :rtype: bool
    """
    # TODO: this needs supported code in NGAPy bench instance - will be covered by NGAIMS-1230
    expected_env_vector = [True] * 2
    actual_env_vector = []

    required_files_exist = True
    for tc, files_dict in tp_input_files.items():
        for file, path in files_dict.items():
            file_exist = os.path.exists(path)
            logging.getLogger().info(f"Checking existence of file: {file} for TC '{tc}':" + str(file_exist))
            required_files_exist = file_exist and required_files_exist

    actual_env_vector.append(verify_local(required_files_exist, True, '==', 'Required files exist'))

    bench_status = bench_instance.verify_up_and_running()

    actual_env_vector.append(verify_local(bench_status, True, '==', 'Target device is operational'))

    env_success = verify_local(expected_env_vector, actual_env_vector, '==',
                               "Test environment is ready")

    return env_success


def verify_package_load(bench_instance):
    """
    Verifies loading of provided package was successful
    :param bench_instance: bench instance
    :return: Boolean depending on success of checks of individual parameters
    """
    # TODO: this needs supported code in NGAPy bench instance  - will be covered by NGAIMS-1230
    # TODO: needs to check version of CMCF, LDI, etc.  - will be covered by NGAIMS-1230
    raise NotImplementedError


def get_th() -> Optional[test_harness.NgapyTestHarnes]:
    """
    Gets Test Harness instance
    :return: Test harness
    :rtype: test_harness.NgapyTestHarnes
    """
    return ngapy_th


class Application(Frame):
    def __init__(self, parent, input_htmls, tp_hndl):
        threading.Thread.__init__(self)
        Frame.__init__(self, parent)
        self.parent = parent
        self.processThreadSet = False
        self.today = datetime.date.today()
        self.startdate = self.today  # + datetime.timedelta(days=-self.today.isoweekday() + 1) # get past Sunday date
        # self.enddate = self.startdate + datetime.timedelta(days=6) # get past-past Sunday date
        self.issues = []
        self.text_wrap_len = 40
        self.status_message = "No activity"
        # shall be at the end
        self.datetime_format = '%b %d %Y %I:%M%p'
        self.html_pages = input_htmls
        self.html_page_idx = 0
        self.html_pages_len = len(self.html_pages)
        self.response_vector = []
        self.buttons_vector = []
        self.createWidgets()
        self.but_font = tkinter.font.Font(size=14)
        self.tp = tp_hndl

    def createWidgets(self):
        self.parent.title(f"TITAN Analysis Frame for: {__file__}")
        menubar = Menu(self.parent)
        padxValue = 15
        but_font = tkinter.font.Font(size=14)
        space_font = tkinter.font.Font(size=1)
        font_big = tkinter.font.Font(size=8)

        # Parent
        self.parent.config(menu=menubar)

        # Analysis Title
        self.analysis_title = LabelFrame(self.parent, text="Analysis/Test Content", padx=5, pady=5)
        self.analysis_title.grid(row=0, column=0, padx=10, pady=10, sticky='NEW')

        # Sub-Analysis Frame Content
        self.group_text_html = tkinterhtml.HtmlFrame(self.analysis_title, horizontal_scrollbar="auto")
        self.group_text_html.grid(in_=self.analysis_title, sticky='NWES')

        # Commands frame
        self.group_buttons = LabelFrame(self.parent, text="User Entries", padx=5, pady=5)
        self.group_buttons.grid(row=1, column=0, padx=10, pady=10, sticky='NEWS')

        # # Status frame
        # self.status = LabelFrame(self.parent, text="Status")
        # self.status.grid(row=2, column=0, padx=10, pady=10, sticky='NEW', columnspan=2)

        ##########################
        # Add always  quit button
        self.add_exit_button()

        ##########################
        # Fill in html
        self.load_next_page()

        #####################################
        # Fill in status portion
        # self.status_empty = Label(self.parent, text=self.status_message)
        # self.status_empty.grid(in_=self.status, sticky='NWES')

        # threading._start_new_thread(self.check_status, ())

    def load_next_page(self):
        if self.is_final_page():
            self.set_final_page()
            return
        # Increment number of pages:
        self.analysis_title["text"] = f"Analysis/Test Content Step ({self.html_page_idx + 1}/{self.html_pages_len})"

        # Sub-Analysis Frame Content
        html_data = ""
        html_filename = os.path.abspath(self.html_pages[self.html_page_idx]["html_file"])
        with open(html_filename) as html_ro_file:  # Use file to refer to the file object
            html_data = html_ro_file.read()
        self.group_text_html.set_content(html_data)

        for button in self.html_pages[self.html_page_idx]["buttons"]:
            if button == "PASS":
                self.add_pass_button()
            elif button == "FAIL":
                self.add_fail_button()
            elif button == "NEXT":
                self.add_next_button()
            else:
                print("UNKNOWN BUTTON")

        self.html_page_idx += 1

        # create buttons

    def add_pass_button(self):
        but_font = tkinter.font.Font(size=14)
        self.pass_button = Button(self.parent, width=10, font=but_font, height=2)
        self.pass_button["text"] = "PASS"
        self.pass_button["command"] = self.interrupt_pass_button_pressed
        self.pass_button.grid(in_=self.group_buttons, row=0, column=0, padx=10, pady=10, sticky='NWES')
        self.buttons_vector.append(self.pass_button)

    def add_fail_button(self):
        but_font = tkinter.font.Font(size=14)
        self.fail_button = Button(self.parent, width=10, font=but_font, height=2)
        self.fail_button["text"] = "FAIL"
        self.fail_button["command"] = self.interrupt_fail_button_pressed
        self.fail_button.grid(in_=self.group_buttons, row=0, column=1, padx=10, pady=10, sticky='NWES')
        self.buttons_vector.append(self.fail_button)

    def add_next_button(self):
        but_font = tkinter.font.Font(size=14)
        self.next_button = Button(self.parent, width=10, font=but_font, height=2)
        self.next_button["text"] = "NEXT"
        self.next_button["command"] = self.interrupt_next_button_pressed
        self.next_button.grid(in_=self.group_buttons, row=0, column=2, padx=10, pady=10, sticky='NWES')

    def add_exit_button(self):
        but_font = tkinter.font.Font(size=14)
        self.QUIT = Button(self.parent, width=10, font=but_font, height=2)
        self.QUIT["text"] = "EXIT"
        self.QUIT["command"] = self.on_exit
        self.QUIT.grid(in_=self.group_buttons, row=0, column=3, padx=10, pady=10)

    def is_final_page(self):
        return self.html_page_idx == self.html_pages_len

    def set_final_page(self):
        import __main__
        html_data = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>ANALYSIS 233019</title>
        </head>
        <h1><p style="text-align: center;"><strong>ANALYSIS SEQUENCE {os.path.basename(__main__.__file__)} COMPLETED. </strong></p>
        <p style="text-align: center;"><strong>SEE DOCUMENTED EVIDENCE IN RESULTS FOLDER</strong></p>
        </h1>
        <body>
            <p style="text-align: center;"><strong>TIMESTAMP {datetime.datetime.now().strftime(self.datetime_format)}</strong></p>
        </body>
        </html>"""

        self.group_text_html.set_content(html_data)
        for button in self.buttons_vector:
            button.destroy()
        # self.add_exit_button()

    def interrupt_next_button_pressed(self):
        print("Next button pressed")
        self.response_vector.append("NEXT")
        self.load_next_page()

    def interrupt_pass_button_pressed(self):
        print("Pass button pressed")
        self.response_vector.append("PASS")
        self.tp.ngapy_th.verify("PASS", self.html_pages[self.html_page_idx - 1]["expected"],
                                msg="User interactive selected response",
                                test_num=self.html_pages[self.html_page_idx - 1]["tc_id"])
        self.load_next_page()

    def interrupt_fail_button_pressed(self):
        print("Fail button pressed")
        self.response_vector.append("FAIL")
        self.tp.ngapy_th.verify("FAIL", self.html_pages[self.html_page_idx - 1]["expected"],
                                msg="User interactive selected response",
                                test_num=self.html_pages[self.html_page_idx - 1]["tc_id"])
        self.load_next_page()

    def check_status(self):
        while (True):
            # self.status_empty.config(text="Test Ready")
            time.sleep(0.2)

    def on_exit(self):
        if self.processThreadSet:
            self.processThread.join()

        self.quit()
