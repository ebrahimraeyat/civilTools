import sys
import os
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt

_appname = 'civiltools'
_version = '5.0'
branch = 'v5'
civiltools_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, civiltools_path)
main_window = uic.loadUiType(civiltools_path + '/widgets' + '/main_form.ui')[0]
about_window, about_base = uic.loadUiType(civiltools_path + '/widgets' + '/about.ui')
update_window, update_base = uic.loadUiType(civiltools_path + '/widgets' + '/update.ui')
serial_base, serial_window = uic.loadUiType(civiltools_path + '/widgets' + '/serial.ui')
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
        self.help_button.clicked.connect(self.help)
        self.register_button.clicked.connect(self.register)

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

    def register(self):
        serial_win = SerialForm(self)
        serial = str(subprocess.check_output("wmic csproduct get uuid")).split("\\r\\r\\n")[1].split()[0]
        serial_win.serial.setText(serial)
        serial_win.exec_()

    def help(self):
        import webbrowser
        path = civiltools_path +  "/help" + "/help.pdf"
        webbrowser.open_new(path)

    def git_updates(self):
        from functions import update, progressbar
        if not update.internet():
            msg = "You are not connected to the Internet, please check your internet connection."
            QMessageBox.warning(None, 'update', str(msg))
            return
        if (QMessageBox.question(self, "update", ("update to latest version?!"),
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            return
        self.update_win = progressbar.UpdateWindow(self)
        self.update_win.show()
        msg = 'Please wait...'
        up = update.GitUpdate(branch)
        msg = up.git_update()
        self.update_win.label.setText(msg)


class AboutForm(about_base, about_window):
    def __init__(self, parent=None):
        super(AboutForm, self).__init__()
        self.setupUi(self)

class SerialForm(serial_base, serial_window):
    def __init__(self, parent=None):
        super().__init__()
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
