'''
--------------------------------------------------------------------------
Copyright (C) 2015-2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-03-06

This file is part of Struthon.
Struthon is a range of free open source structural engineering design 
Python applications.
https://bitbucket.org/lukaszlaba/py4structure/wiki/Home

Struthon is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Struthon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import pip
import sys
from io import StringIO

def check_one(package='civiltools'):
    f = StringIO()
    sys.stdout = f
    pip.main(["search", package])
    sys.stdout = sys.__stdout__
    #---
    instaled = next((line.split(":", 1)[1].strip()
                 for line in f.getvalue().splitlines() if line.startswith("  INSTALLED")), None)
    latest= next((line.split(":", 1)[1].strip()
                 for line in f.getvalue().splitlines() if line.startswith("  LATEST")), None) 
    #---
    is_update = True
    if latest:
         is_update = False
    if (instaled==None) and (latest==None):
        is_update = False
    #---
    report_text = ''
    if is_update:
        report_text = '%s %s up-to-date' %(package, instaled)
    elif (instaled==None) and (latest==None):
        report_text = '%s not instaled!!!!!!!' %(package)
    else:
        report_text = '%s %s out-to-date (latest %s)!!!!!!!' %(package, instaled, latest)
    return [is_update, instaled, latest, report_text]

def check_few(tocheck=['section', 'cfactor']):
    all_update = True
    report = ''
    pip_command = 'pip install --upgrade'
    for i in tocheck:
        icheck = check_one(i)
        report += icheck[3] + '\n'
        if not icheck[0]:
             all_update = False
             pip_command += ' %s' %i
    if not all_update:
        report += '------------\n'
        report += 'to upgrade use command:\n%s' %pip_command 
        
    return [all_update, report, pip_command]
        
# Test if main
if __name__ == '__main__':
    #print check_one('fifostr')
    # out = check_few(['struthon', 'strupy', 'seepy', 'visdom', 'dxfwrite'])
    out = check_one()
    print(out)