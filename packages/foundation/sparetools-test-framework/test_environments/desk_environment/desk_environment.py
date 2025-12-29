#!/usr/bin/env python
"""
Copyright Honeywell International Inc 2008-2011
Copyright DDC-I, Inc. 2011, 2018, 2021
All Rights Reserved

This material is a trade secret of Honeywell International Inc.
and/or DDC-I, Inc. and may not be used, disclosed or copied
in any form outside of Honeywell International Inc. without the
explicit written permission of Honeywell International Inc.
or DDC-I, Inc. or it's authorized distributors.

This material is distributed WITHOUT ANY WARRANTY; without
even  the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
from pathlib import Path

try:
    import ngapy.bench.desk_environment
except ImportError:
    # ngapy not available, continue without it
    pass

PATHSEP = os.path.pathsep
# If running native windows, then there will be no cygwin paths,
# and on Linux/MacOS there will never be windows paths.
ensureWindowsPath = lambda x: x

import sys


def setup_gcc(installRoot):
    args = sys.argv[1:]
    # if len(args) == 0 or args[0] in ("-h", "--help"):
    #    sys.exit(__doc__)

    # Nominally __file__ should be /desk/bin/gcc-environment.py, so on Cygwin installRoot will
    # be the parent of "/".  On Linux, installRoot will be "/".
    # installRoot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    PATH = os.environ["PATH"].split(os.path.pathsep)

    def maybeAddToPath(path):
        if os.path.isdir(path):
            PATH.insert(0, path)

    # Put windows python on the PATH
    maybeAddToPath(os.path.join(installRoot, "python"))

    # Add compilers to the path
    # This should contain all gcc-x.y.z folders (ie gcc-4.6.1 and/or gcc-5.3.0)
    for dir in os.listdir(os.path.join(installRoot, "usr", "local", "cross-compilers")):
        maybeAddToPath(os.path.join(installRoot, "usr", "local", "cross-compilers", dir, "bin"))

    for product in ("GCC", "TRAC"):
        productRoot = os.path.join(installRoot, product)
        try:
            for item in os.listdir(productRoot):
                maybeAddToPath(os.path.join(productRoot, item, "bin"))
        except OSError:
            pass

    # Ensure /bin and /usr/bin are on the PATH
    maybeAddToPath(os.path.join(installRoot, "bin"))
    maybeAddToPath(os.path.join(installRoot, "usr", "bin"))

    # Put OpenArbor JRE on the PATH
    maybeAddToPath(os.path.join(installRoot, "OpenArbor", "jre", "bin"))

    os.environ["PATH"] = os.path.pathsep.join(PATH)

    # disable dosfilewarning if it's not off already
    try:
        cygwinValue = os.environ["CYGWIN"]
    except KeyError:
        cygwinValue = ""
    cygwinList = [item for item in cygwinValue.split(" ") if item != ""]
    if "nodosfilewarning" not in cygwinList:
        cygwinList.append("nodosfilewarning")
        os.environ["CYGWIN"] = " ".join(cygwinList)


def setup_desk_environment(ddci_root):
    ddci_root = Path(ddci_root)
    desk_root = ddci_root / 'desk'
    os.environ["DESKHOME"] = str(ensureWindowsPath(desk_root))
    os.environ["ABCHOME"] = str(ensureWindowsPath(desk_root))

    # Add desk bin to the python path
    sys.path += [os.path.join(desk_root, "bin")]

    # Put desk bin on the PATH
    os.environ["PATH"] = os.path.pathsep.join(
        [os.path.join(desk_root, "bin")] + os.environ["PATH"].split(os.path.pathsep))

    # This should be set to the IP address (or DNS name) of the Deos
    # target you will use most often.
    try:
        os.environ["DESK_IP_ADDR"]
    except KeyError:
        # default
        os.environ["DESK_IP_ADDR"] = "192.168.18.100"

    setup_gcc(ddci_root)


if __name__ == "__main__":
    print(os.environ)
    setup_desk_environment(r'c:\DDCI\DDC-I_20210624')
    print(os.environ)
    pass
