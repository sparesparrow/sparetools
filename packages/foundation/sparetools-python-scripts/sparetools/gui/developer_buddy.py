"""
Developer Buddy GUI Components

Reusable GUI components for developer tools.
Based on ngapy-dev/ngapy/gui/titan_developer_buddy.py
Adapted for SpareTools ecosystem.
"""

import logging
import os
import re
import threading
import tkinter.font as tk_font
import tkinter.scrolledtext as tk_scrolled
from queue import Queue, Empty
from subprocess import Popen
from tkinter import *
from tkinter.ttk import *

import yaml

from .gui_common import create_tool_tip, expand_and_fill_x
from ..util.execute_command import remove_console_color_codes

log = logging.getLogger(__name__)


# Copied from ngapy/gui/titan_developer_buddy.py
class Configuration:
    """
    Configuration manager for developer buddy.
    
    Based on ngapy/gui/titan_developer_buddy.py Configuration class.
    """
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.expanduser('~'), '.sparetools_buddy_config.yaml')
        self.data = {
            'version': '1.1',
            'rebuild_selection': '',
            'build_selection': '',
            'logging_selection': '20'
        }
        self.load_config()

    def load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as stream:
                try:
                    temp_data = yaml.safe_load(stream)
                    if temp_data and temp_data.get('version') != '1.1':
                        self.save_config()
                    elif temp_data:
                        self.data = temp_data
                except yaml.YAMLError as exc:
                    log.warning(f"Failed to load config: {exc}")

    def save_config(self):
        """Save configuration to YAML file."""
        with open(self.config_path, 'w') as stream:
            yaml.safe_dump(self.data, stream)


# Copied from ngapy/gui/titan_developer_buddy.py
class Checkbar(Frame):
    """
    Checkbox bar widget for multiple selections.
    
    Based on ngapy/gui/titan_developer_buddy.py Checkbar class.
    """
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=NW, callback=None):
        super(Checkbar, self).__init__(parent)
        self.check_boxes = []
        column_frame = None
        for index, pick in enumerate(picks):
            if index % 5 == 0:
                column_frame = Frame(parent)
                column_frame.pack(side=side, anchor=anchor, expand=YES)
            int_variable = IntVar()
            chk = Checkbutton(column_frame, text=pick, variable=int_variable, command=callback)
            self.check_boxes.append((pick, int_variable, chk))
            chk.pack(side=TOP, anchor=anchor)
            chk.invoke()


# Copied from ngapy/gui/titan_developer_buddy.py
class Console(Frame):
    """
    Console widget with colored output and logging integration.
    
    Based on ngapy/gui/titan_developer_buddy.py Console class.
    """
    p = None
    captured_output = []
    command = None
    activity_callback = None

    def __init__(self, master, initial_log_level=logging.INFO):
        super(Console, self).__init__(master)
        myFont = tk_font.Font(family="Consolas", size=10)
        self.text = tk_scrolled.ScrolledText(master, wrap='word', background='gray13', fg='white', font=myFont)
        self.text.pack(expand=True, fill="both")
        self.text.tag_config('success', font=myFont, foreground='green')
        self.text.tag_config('failure', font=myFont, foreground='red')
        self.text.tag_config('warning', font=myFont, foreground='yellow')
        self.text.tag_config('command', font=myFont, foreground='orange')
        self.redirect_logging(initial_log_level)
        self.load_tags()
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[([0-?]*)[ -/]*[@-~])')

    def load_tags(self):
        """Load text formatting tags."""
        font_name = self.text['font']
        bold_font = tk_font.nametofont(font_name).copy()
        bold_font.config(weight="bold")
        italic_font = tk_font.nametofont(font_name).copy()
        italic_font.config(slant="italic")
        self.text.tag_config('1', font=("Consolas", "10", "bold"))
        self.text.tag_config('3', font=italic_font)
        self.text.tag_config('4', underline=1)
        self.text.tag_config('9', overstrike=1)
        self.text.tag_config('bulleted', lmargin1=30, lmargin2=40)
        self.pallet8 = [
            "black", "red", "green", "yellow", "blue", "magenta",
            "cyan", "white", "magic", "default",  # magic: enable 256 color
        ]
        for i in range(8):  # pallet8
            self.text.tag_config(str(i + 30), foreground=self.pallet8[i])
            self.text.tag_config(str(i + 40), background=self.pallet8[i])

    def redirect_logging(self, initial_log_level):
        """Redirect logging output to console widget."""
        logging.getLogger('git').setLevel(logging.CRITICAL + 1)
        self.logging_handler = logging.StreamHandler()
        self.logging_handler.setStream(self)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logging_handler.setFormatter(formatter)
        logging.getLogger('__main__').addHandler(self.logging_handler)
        os.environ['SPARETOOLS_LOGGING_LEVEL'] = str(initial_log_level)
        self.logging_handler.setLevel(int(initial_log_level))

    def set_logging_level(self, level):
        """Set logging level."""
        self.logging_handler.setLevel(level)

    @staticmethod
    def enqueue_output(out, queue):
        """Enqueue output lines from subprocess."""
        while (line := out.readline()) != '':
            queue.put(line)
        out.close()

    def display_text(self, kwargs):
        """Display command output in console."""
        os.environ['CONAN_COLOR_DISPLAY'] = '1'
        log.info(f'Executing command: {self.command}, args: {kwargs}')

        self.p = Popen(self.command, universal_newlines=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ, **kwargs)
        self.captured_output = []

        self.q = Queue()
        t = threading.Thread(target=self.enqueue_output, args=(self.p.stdout, self.q))
        t.daemon = True  # thread dies with the program
        t.start()

        while t.is_alive():
            self.after(100, self.consume_queue)
        self.p.wait()
        self.after(0, self.consume_queue)
        log.info(f'Executing result code: {self.p.returncode}')

    def consume_queue(self):
        """Consume queued output lines."""
        current_lines = []
        try:
            while 1:
                current_lines.append(self.q.get_nowait())
        except Empty:
            if current_lines:
                self.put_to_read_only('\n'.join(current_lines), tag_all=True)
                self.captured_output.extend([remove_console_color_codes(line) for line in current_lines])

    def put_to_read_only(self, text, tag_all=False):
        """Insert text into console with color coding."""
        self.text.config(state=NORMAL)
        for line_index, lines in enumerate(text.splitlines(True)):
            line_start = str(float(self.text.index(END)) - 1)
            m = re.search('.*Executing result code: ([0-9]*)', lines)
            m2 = re.search('completed with result (.*)', lines)
            if (m and m.group(1) == '0') or (m2 and m2.group(1) == '0') or ('Step build result: Success!' in lines) or \
                    ('All built steps were OK!' in lines):
                self.text.insert(END, lines, 'success')
            elif m or m2 or 'Step build result: Failed!' in lines or 'At least one build step Failed!' in lines \
                    or ('- WARNING -' in lines) or ('- ERROR -' in lines):
                self.text.insert(END, lines, 'failure')
            elif 'Executing command' in lines or 'Command finished' in lines or 'Executing command:' in lines:
                self.text.insert(END, lines, 'command')
            else:
                if remove_console_color_codes(lines).rstrip() == '':
                    continue
                col = 0
                current_end = line_start
                for splits in lines.split('\u001b[0m'):
                    col += len(remove_console_color_codes(splits))
                    self.text.insert(END, remove_console_color_codes(splits))
                    new_end = f'{line_start} + {col} chars'
                    for match in self.ansi_escape.findall(splits):
                        self.text.tag_add(match, current_end, new_end)
                    current_end = new_end
            line_end = str(int(float(self.text.index(END)))) + '.end'
            if line_index > 0 or tag_all:
                self.text.tag_add('bulleted', line_start, line_end)
        self.text.see(END)
        self.text.config(state=DISABLED)

    def run_process_in_thread(self, command, **kwargs):
        """Run a process in a separate thread and display output."""
        self.activity_callback_run(True)
        self.command = command
        t = threading.Thread(target=self.display_text, args=[kwargs])
        t.start()
        t.join()
        self.activity_callback_run(False)
        return self.p.returncode, self.captured_output

    def kill_running_process(self):
        """Kill the currently running process."""
        if self.p and self.p.poll() is None:
            self.p.kill()

    def write(self, text: str):
        """Write text to console (for logging StreamHandler)."""
        self.put_to_read_only(text)

    def flush(self):
        """Flush output (for logging StreamHandler)."""
        pass

    def activity_callback_run(self, active):
        """Call activity callback when process state changes."""
        if self.activity_callback:
            self.activity_callback(active)


# Copied from ngapy/gui/titan_developer_buddy.py
def remove_files(files_to_delete, folder):
    """
    Remove files from a folder.
    
    Based on ngapy/gui/titan_developer_buddy.py remove_files function.
    """
    for file in files_to_delete:
        try:
            os.remove(os.path.join(folder, file))
        except:
            pass


# Copied from ngapy/gui/titan_developer_buddy.py
def check_git_repository_validity(folder_path):
    """
    Check if folder is a valid git repository with conanfile.
    
    Based on ngapy/gui/titan_developer_buddy.py check_git_repository_validity function.
    """
    return os.path.isdir(folder_path) and \
           os.path.isfile(os.path.join(folder_path, 'conanfile.py'))
