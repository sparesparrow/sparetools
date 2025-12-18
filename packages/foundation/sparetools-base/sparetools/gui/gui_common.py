"""
GUI Common Utilities

Common GUI utilities for tkinter applications.
Based on ngapy-dev/ngapy/gui/gui_common.py
"""

from tkinter import *
from tkinter import Toplevel, TclError, Label, LEFT, SOLID
from tkinter.ttk import *

expand_and_fill_x = {'expand': 1, 'fill': BOTH}


# Copied from ngapy/gui/gui_common.py
class ToolTip(object):
    """
    Tooltip widget for tkinter.
    
    Based on ngapy/gui/gui_common.py ToolTip class.
    """
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.text = ''

    def showtip(self, text):
        self.text = text
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# Copied from ngapy/gui/gui_common.py
def create_tool_tip(widget, text):
    """
    Create a tooltip for a widget.
    
    Based on ngapy/gui/gui_common.py create_tool_tip function.
    
    Args:
        widget: Tkinter widget to attach tooltip to
        text: Tooltip text to display
    """
    tool_tip = ToolTip(widget)

    def enter(event):
        tool_tip.showtip(text)

    def leave(event):
        tool_tip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
