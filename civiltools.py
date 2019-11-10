import sys
import os
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt

_appname = 'civiltools'
_version = '3.0'
_civiltools_mainpackages = ['civiltools']
civiltools_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, civiltools_path)
main_window = uic.loadUiType(civiltools_path + '/main_form.ui')[0]
about_window, about_base = uic.loadUiType(civiltools_path + '/about.ui')
update_window, update_base = uic.loadUiType(civiltools_path + '/update.ui')
serial_base, serial_window = uic.loadUiType(civiltools_path + '/serial.ui')
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
        os.chdir(civiltools_path + "/applications/records")
        subprocess.Popen([python_exe, 'MainWindow.py'])

    def run_dynamic(self):
        directory = os.path.join(civiltools_path, 'applications', 'dynamic')
        os.chdir(directory)
        subprocess.Popen([python_exe, 'freevibrationwin.py'])

    def about(self):
        self.child_win = AboutForm(self)
        self.child_win.show()

    def git_updates(self):
        if not internet():
            msg = "You are not connected to the Internet, please check your internet connection."
            QtWidgets.QMessageBox.warning(None, 'update', str(msg))
            return

        if sys.platform == "win32":
            serial = str(subprocess.check_output("wmic csproduct get uuid")).split("\\r\\r\\n")[1].split()[0]
            if not serial_number(serial):
                serial_win = SerialForm(self)
                serial_win.serial.setText(serial)
                serial_win.exec_()
                return

        update_win = UpdateForm(self)
        from git import Repo, Git
        repo = Repo(civiltools_path)
        tags = repo.git.tag(l=True).split('\n')
        update_win.tag_list.addItems(tags)
        if update_win.exec_():
            tag = update_win.tag_list.currentItem().text()
        else:
            return
        if tag != 'Latest':
            g = Git(civiltools_path)
            result = g.execute(['git', 'checkout', '-f', tag])
            msg = f'You have successfully move to {tag}'
            QtWidgets.QMessageBox.information(None, 'update', str(msg))
            return

        if (QMessageBox.question(self, "update", ("update to latest version?!"),
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            return

        import git
        g = git.cmd.Git(civiltools_path)
        msg = ''
        try:
            msg = g.pull(env={'GIT_SSL_NO_VERIFY': '1'})
        except:
            QMessageBox.information(self, "update", "update takes some minutes, please be patient.")
            import shutil
            import tempfile
            pkgs_dir = os.path.abspath(os.path.join(civiltools_path, os.path.pardir))
            default_tmp_dir = tempfile._get_default_tempdir()
            name = next(tempfile._get_candidate_names())
            civiltools_temp_dir = os.path.join(default_tmp_dir, 'civiltools' + name)
            os.mkdir(civiltools_temp_dir)
            os.chdir(civiltools_temp_dir)
            git.Git('.').clone("https://github.com/ebrahimraeyat/civilTools.git", env={'GIT_SSL_NO_VERIFY': '1'})
            shutil.rmtree(civiltools_path, onerror=onerror)
            src_folder = os.path.join(civiltools_temp_dir, 'civilTools')
            shutil.copytree(src_folder, civiltools_path)
            os.chdir(civiltools_path)
            msg = 'update done successfully.'

        # os.chdir(civiltools_path + '/..')
        # pip_install = f'pip install --upgrade  --install-option="--prefix={civiltools_path}/.." git+https://github.com/ebrahimraeyat/civilTools.git'
        # subprocess.Popen([python_exe, '-m', pip_install])
        else:
            if not msg:
                msg = 'error occured during update\nplease contact with @roknabadi'
        # msg += '\n please restart the programm.'
        QtWidgets.QMessageBox.information(None, 'update', msg)


def serial_number(serial):
    import urllib.request
    url = 'https://gist.githubusercontent.com/ebrahimraeyat/1ca5731b3761a3c9c47147d4d3b482d1/raw'
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8')
    print(text)
    return serial in text


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


class UpdateForm(update_base, update_window):
    def __init__(self, parent=None):
        super(UpdateForm, self).__init__()
        self.setupUi(self)


class SerialForm(serial_base, serial_window):
    def __init__(self, parent=None):
        super(SerialForm, self).__init__()
        self.setupUi(self)


def main():
    import time
    os.chdir(civiltools_path)
    app = QtWidgets.QApplication(sys.argv)
    splash_pix = QPixmap("./images/civil-engineering.jpg")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(50, splash_pix.height() - 30, splash_pix.width() - 100, 20)

    splash.show()
    splash.showMessage("<h1><font color='DarkRed'>civiltools by Ebrahim Raeyat Roknabadi </font></h1>", Qt.AlignCenter | Qt.AlignCenter, Qt.black)

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
