import sys
import os
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QMessageBox

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
