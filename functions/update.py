import os
import sys
import subprocess
from pathlib import Path

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QSplashScreen, QMessageBox, QProgressBar

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))

from functions import progressbar
serial_base, serial_window = uic.loadUiType(str(civiltools_path / 'widgets' / 'serial.ui'))


class GitUpdate:

    def __init__(self,
                file_path,
                git_url="https://github.com/ebrahimraeyat/civilTools.git",
                branch='v5',
                ):
        self.file_Path = file_path
        self.git_url = git_url
        self.branch = branch

    def git_updates(self):
        if not internet():
            msg = "You are not connected to the Internet, please check your internet connection."
            QtWidgets.QMessageBox.warning(None, 'update', str(msg))
            return

        if not self.allowed_to_continue:
            return

        if (QMessageBox.question(self, "update", ("update to latest version?!"),
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            return

        import git
        from git import Repo, Git
        g = git.cmd.Git(str(civiltools_path))
        msg = ''
        window, app = progressbar.show("update takes some minutes, please be patient.")
        app.exec_()
        try:
            msg = g.pull('origin', self.branch, env={'GIT_SSL_NO_VERIFY': '1'})
            msg = 'update done successfully.'
        except:
            window.label.setText("update takes some minutes, please be patient.")
            # QMessageBox.information(self, "update", "update takes some minutes, please be patient.")
            import shutil
            import tempfile
            pkgs_dir = civiltools_path.parent
            default_tmp_dir = tempfile._get_default_tempdir()
            name = next(tempfile._get_candidate_names())
            civiltools_temp_dir = Path(default_tmp_dir) /  'civiltools' / name
            civiltools_temp_dir.mkdir()
            os.chdir(str(civiltools_temp_dir))
            git.Git('.').clone(self.git_url, branch=self.branch, env={'GIT_SSL_NO_VERIFY': '1'})
            shutil.rmtree(str(civiltools_path), onerror=onerror)
            src_folder = civiltools_temp_dir / 'civilTools'
            shutil.copytree(str(src_folder), str(civiltools_path))
            os.chdir(str(civiltools_path))
            msg = 'update done successfully.'
            
            
        # os.chdir(civiltools_path + '/..')
        # pip_install = f'pip install --upgrade  --install-option="--prefix={civiltools_path}/.." git+https://github.com/ebrahimraeyat/civilTools.git'
        # subprocess.Popen([python_exe, '-m', pip_install])
        else:
            if not msg:
                msg = 'error occured during update\nplease contact with @roknabadi\
                    Email: ebe79442114@yahoo.com, ebe79442114@gmail.com'

        g = Git(civiltools_path)
        if sys.platform == "win32":
            if serial_number(serial):
                result = g.execute(['git', 'checkout', self.branch])
            # else:
            #     result = g.execute(['git', 'checkout', 'master'])
        else:
            result = g.execute(['git', 'checkout', self.branch])
        # msg += '\n please restart the programm.'
        window.label.setText(msg)
        # QtWidgets.QMessageBox.information(None, 'update', msg)

    def allowed_to_continue(self):
        if sys.platform == "win32":
            if not is_registered(self.filename):
                serial = str(subprocess.check_output("wmic csproduct get uuid")).split("\\r\\r\\n")[1].split()[0]
                if not serial_number(serial):
                    serial_win = SerialForm(self)
                    serial_win.serial.setText(serial)
                    serial_win.exec_()
                    return
                else:
                    register(self.filename)
            return True

    def is_registered(self):
        import base64
        if not Path(self.filename).exists():
            with open(self.filename, 'wb') as f:
                b = base64.b64encode('0-0'.encode('utf-8'))
                f.write(b)
            return False
        else:
            with open(self.filename, 'rb') as f:
                b = f.read()
                text = base64.b64decode(b).decode('utf-8').split('-')
            if text[0] == 1 or text[1] <= 2:
                return True
            else:
                return False

    def add_using_feature(self):
        if  Path(self.filename).exists():
            with open(self.filename, 'rb') as f:
                b = f.read()
                text = base64.b64decode(b).decode('utf-8').split('-')
                text[1] += 1
                text = '-'.join(*[text])
            with open(self.filename, 'wb') as f:
                b = base64.b64encode(text.encode('utf-8'))
        return

    def register(self):
        if  Path(self.filename).exists():
            with open(self.filename, 'rb') as f:
                b = f.read()
                text = base64.b64decode(b).decode('utf-8').split('-')
                text[0] = 1
                text = '-'.join(*[text])
            with open(self.filename, 'wb') as f:
                b = base64.b64encode(text.encode('utf-8'))

def serial_number(serial, url):
    import urllib.request
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8')
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


class SerialForm(serial_base, serial_window):
    def __init__(self, parent=None):
        super(SerialForm, self).__init__()
        self.setupUi(self)
