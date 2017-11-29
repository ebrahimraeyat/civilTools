import sys
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
import checkupdate

_appname = 'civiltools'
_version = '1.3'
_civiltools_mainpackages = ['civiltools']
_about = '''
-------------Licence-------------
civiltools is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
            
civiltools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
            
You should have received a copy of the GNU General Public License along with Foobar; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
            
Copyright (C) 2015-2017 Roknabadi Ebrahim (e-mail : ebe79442114@gmail.com)

-------------Project info-------------
http://ebrahimraeyat.blog.ir/
https://pypi.python.org/pypi/civiltools

-------------Contact-------------
ebe79442114@gmail.com
@roknabadi
'''

class FormWidget(QtWidgets.QWidget):

    def __init__(self):
        super(FormWidget, self).__init__()
        uic.loadUi('main_form.ui', self)
        #---Button clicked events
        self.section_Button.clicked.connect(self.run_section)
        self.cfactor_Button.clicked.connect(self.run_cfactor)
        self.punch_Button.clicked.connect(self.run_punch)
        self.record_Button.clicked.connect(self.run_record)
        self.about_Button.clicked.connect(self.about)
        self.update_Button.clicked.connect(self.check_for_updates)
        # self.exit_Button.clicked.connect(self.exit)
    #----
    def run_section(self):
        subprocess.Popen(['python', '-m', 'applications.section.MainWindow'])
        
    def run_cfactor(self): 
        subprocess.Popen(['python', '-m', 'applications.cfactor.MainWindow'])   
           
    def run_punch(self):
        subprocess.Popen(['python', '-m', 'applications.punch.mainwindow']) 
        
    def run_record(self):
        subprocess.Popen(['python', '-m', 'applications.records.records.MainWindow']) 

    def about(self):
        QtWidgets.QMessageBox.information(None, 'Info', _about)
        # w = uic.loadUi('about.ui', self)
        # w.show()

    def check_for_updates(self):
        try:
            status = checkupdate.check_few(_civiltools_mainpackages)
            if status[0]:
                msg_info = 'Check for packages update - OK'
                msg_text = status[1]
            else:
                msg_info = 'Check for packages update - !!! out to date !!!'
                msg_text = status[1]
            QtWidgets.QMessageBox.information(None, msg_info, status[1])
        except:
            QtWidgets.QMessageBox.information(None, 'Check for packages update', 'Checking failed !! ')

    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # translator = QtCore.QTranslator()
    # translator.load("main_form.qm")
    # app.installTranslator(translator)
    window = FormWidget()
    window.setWindowTitle(_appname + ' ' + _version)
    window.show()
    sys.exit(app.exec_())