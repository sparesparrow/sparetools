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
import os
import sys

from ngapy.util.miscellaneous_functions import running_on_bench

if __name__ == "__main__":
    path = os.path.abspath(os.path.join(__file__, '../../../../../..'))
    sys.path.append(path)
    from tkinter import *
    import os
    import ngapy.util.run_as_admin as admin
    from sparetools_aerospace.products.ngaims.gui.devbar import devbar_window

    admin.check_if_admin_and_restart_if_not()
    window = Tk()
    window.call('wm', 'attributes', '.', '-topmost', '1')
    window.title(f"DevBar, Admin: {bool(admin.isUserAdmin())}")
    if running_on_bench():
        window.geometry('450x100')
    else:
        window.geometry('450x50')
    devbar_window.create_buttons(window)
    window.mainloop()
