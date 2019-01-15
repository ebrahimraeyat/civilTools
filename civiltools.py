import sys
import os
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QMessageBox

_appname = 'civiltools'
_version = '1.5'
_civiltools_mainpackages = ['civiltools']
civiltools_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, civiltools_path)
main_window = uic.loadUiType(civiltools_path + '/main_form.ui')[0]
about_window, about_base = uic.loadUiType(civiltools_path + '/about.ui')
python_exe = 'pythonw'
if sys.platform.startswith('linux'):
    python_exe = 'python'


class FormWidget(QtWidgets.QWidget, main_window):

    def __init__(self):
        super(FormWidget, self).__init__()
        self.setupUi(self)
        self.about_Button.clicked.connect(self.about)
        self.section_Button.clicked.connect(self.run_section)
        self.cfactor_Button.clicked.connect(self.run_cfactor)
        self.punch_Button.clicked.connect(self.run_punch)
        self.record_Button.clicked.connect(self.run_record)
        self.dynamic_button.clicked.connect(self.run_dynamic)
        self.about_Button.clicked.connect(self.about)
        self.update_Button.clicked.connect(self.git_updates)
    #----
    def run_section(self):
        os.chdir(civiltools_path + "/applications/section")
        subprocess.Popen([python_exe, 'MainWindow.py'])

    def run_cfactor(self):
        os.chdir(civiltools_path + "/applications/cfactor")
        subprocess.Popen([python_exe, 'MainWindow.py'])

    def run_punch(self):
        os.chdir(civiltools_path + "/applications/punch")
        subprocess.Popen([python_exe, 'mainwindow.py'])

    def run_record(self):
        subprocess.Popen([python_exe, '-m', 'applications.records.MainWindow'])

    def run_dynamic(self):
        os.chdir(civiltools_path + "/applications/dynamic")
        subprocess.Popen([python_exe, 'sdof/freevibrationwin.py'])

    def about(self):
        self.child_win = AboutForm(self)
        self.child_win.show()

    def git_updates(self):
        if (QMessageBox.question(self, "update", ("update to latest version?!"),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            return
        import git
        import shutil
        shutil.rmtree(civiltools_path)
        git.Git(civiltools_path + '/..').clone("https://github.com/ebrahimraeyat/civilTools.git")
        QtWidgets.QMessageBox.information(None, 'update', 'update done successfully')


class AboutForm(about_base, about_window):
    def __init__(self, parent=None):
        super(AboutForm, self).__init__()
        self.setupUi(self)

def main():
    os.chdir(civiltools_path)
    app = QtWidgets.QApplication(sys.argv)
    # pixmap = QPixmap("./images/civil-engineering.png")
    # splash = QSplashScreen(pixmap)
    # splash.show()
    # app.processEvents()
    # translator = QtCore.QTranslator()
    # translator.load("main_form.qm")
    # app.installTranslator(translator)
    window = FormWidget()
    window.setWindowTitle(_appname + ' ' + _version)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
