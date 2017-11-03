#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim Löw for Secret Labs AB / PythonWare
#
# source:
# http://www.pythonware.com/products/works/articles/regpy20.htm

import sys

from _winreg import *

# tweak as necessary
version = '2.7'
installpath = 'C:\\Temp\\PortablePython\\App'

regpath = "SOFTWARE\\Python\\Pythoncore\\%s\\" % (version)
installkey = "InstallPath"
pythonkey = "PythonPath"
pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % (
    installpath, installpath, installpath
)

def UnRegisterPy():
    try:
        reg = OpenKey(HKEY_LOCAL_MACHINE, regpath)
    except EnvironmentError:
        print "*** Python not registered?!"
        return
    try:
        DeleteKey(reg, installkey)
        DeleteKey(reg, pythonkey)
        DeleteKey(HKEY_LOCAL_MACHINE, regpath)
    except:
        print "*** Unable to un-register!"
    else:
        print "--- Python", version, "is no longer registered!"

if __name__ == "__main__":
    UnRegisterPy()
