import sys
import os
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt

_appname = 'civiltools'
_version = '1.6'
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
        directory = os.path.join(civiltools_path, 'applications', 'dynamic')
        os.chdir(directory)
        dynamic = 'sdof' + os.sep + 'freevibrationwin.py'
        subprocess.Popen([python_exe, dynamic])

    def about(self):
        self.child_win = AboutForm(self)
        self.child_win.show()

    def git_updates(self):
        if (QMessageBox.question(self, "update", ("update to latest version?!"),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            return
        if not internet():
            msg = "You are not connected to the Internet, please check your internet connection."
            QtWidgets.QMessageBox.warning(None, 'update', str(msg))
            return

        import git
        g = git.cmd.Git(civiltools_path)
        msg = ''
        try:
            msg = g.pull()
        except:
            import shutil
            pkgs_dir = os.path.abspath(os.path.join(civiltools_path, os.path.pardir))
            temp_dir = os.path.join(pkgs_dir, 'temp')
            os.mkdir(temp_dir)
            os.chdir(temp_dir)
            git.Git('.').clone("https://github.com/ebrahimraeyat/civilTools.git")
            shutil.rmtree(civiltools_path, onerror=onerror)
            src_folder = os.path.join(temp_dir, 'civilTools')
            shutil.copytree(src_folder, civiltools_path)
            os.chdir(civiltools_path)
            shutil.rmtree(temp_dir, onerror=onerror)
            msg = 'update done successfully'

        # os.chdir(civiltools_path + '/..')
        # pip_install = f'pip install --upgrade  --install-option="--prefix={civiltools_path}/.." git+https://github.com/ebrahimraeyat/civilTools.git'
        # subprocess.Popen([python_exe, '-m', pip_install])
        else:
            if not msg:
                msg = 'error occured during update\nplease contact with @roknabadi'
        # msg += '\n please restart the programm.'
        QtWidgets.QMessageBox.information(None, 'update', msg)


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        print('another error')
        raise

def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
#         print(ex.message)
        return False

class AboutForm(about_base, about_window):
    def __init__(self, parent=None):
        super(AboutForm, self).__init__()
        self.setupUi(self)

def main():
    import time
    os.chdir(civiltools_path)
    app = QtWidgets.QApplication(sys.argv)
    splash_pix = QPixmap("./images/civil-engineering.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(50, splash_pix.height() - 30, splash_pix.width() - 100, 15)

    splash.show()
    splash.showMessage("<h2><font color='brown'>civiltools by Ebrahim Raeyat Roknabadi </font></h2>", Qt.AlignTop | Qt.AlignCenter, Qt.black)

    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
           app.processEvents()

    # Simulate something that takes time
    time.sleep(1)
    # translator = QtCore.QTranslator()
    # translator.load("main_form.qm")
    # app.installTranslator(translator)
    window = FormWidget()
    window.setWindowTitle(_appname + ' ' + _version)
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
