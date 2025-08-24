from pathlib import Path
import sys

from PySide.QtGui import QMessageBox
from PySide import QtGui
from PySide import QtCore
import FreeCADGui as Gui

civiltools_path = Path(__file__).absolute().parent.parent

import find_etabs

version = sys.version.split()[0]
if version == '3.8.6+':
    from functions import check_legal
elif version == '3.12.10':
    from functions import check_legal_12 as check_legal


def allowed_to_continue(
                        filename,
                        gist_url,
                        dir_name,
                        n=5,
                        ):
    check = check_legal.CheckLegalUse(
                                filename,
                                gist_url,
                                dir_name,
                                n,
    )
    allow, text = check.allowed_to_continue()
    if allow and not text:
        return True, check
    else:
        if text in ('INTERNET', 'SERIAL'):
            serial_win = SerialForm()
            serial_win.form.serial.setText(check.serial)
            serial_win.form.exec_()
            return False, check
        elif text == 'REBOOT':
            msg = "Please reboot your computer and try again!"
            QMessageBox.information(None, 'Reboot', str(msg))
            return False, check
        elif text == 'REGISTERED':
            msg = "Congrajulation! You are now registered, enjoy using this features!"
            QMessageBox.information(None, 'Registered', str(msg))
            return True, check
    return False, check

def show_warning_about_number_of_use(check):
    if check.is_civiltools_registered:
        return
    elif check.is_registered:
        check.add_using_feature()
        _, no_of_use = check.get_registered_numbers()
        n = check.n - no_of_use
        msg = ''
        if n == 0:
            msg = f"You can't use this feature any more times!\n please register the software."
        elif n > 0:
            msg = f"You can use this feature {n} more times!\n then you must register the software."
        if msg:
            QMessageBox.warning(None, 'Not registered!', str(msg))


class SerialForm(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SerialForm, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'serial.ui'))
        # self.setupUi(self)
        self.form.submit_button.clicked.connect(submit)


def submit():
    check = check_legal.CheckLegalUse(
        'civiltools5.bin',
        'https://gist.githubusercontent.com/ebrahimraeyat/b8cbd078eb7b211e3154804a8bb77633/raw',
        'cfactor',
        )
    text = check.submit()

    if text == 'INTERNET':
        msg = 'Please connect to the internet!'
    elif text == 'SERIAL':
        msg = 'You are not registered, Please Contact author to buy the software.'
    elif text == 'REBOOT':
        msg = "Please reboot your computer and try again!"
    elif text == 'REGISTERED':
        msg = "Congrajulation! You are now registered, enjoy using CivilTools."
    QMessageBox.information(None, 'Registeration', msg)


class CivilToolsRegister:

    def GetResources(self):
        menu_text = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Activate CivilTools")
        tooltip = QtCore.QT_TRANSLATE_NOOP(
            "civiltools",
            "Activate CivilTools")
        path = str(
                   Path(__file__).parent.absolute().parent / "images" / "register.png"
                   )
        return {'Pixmap': path,
                'MenuText': menu_text,
                'ToolTip': tooltip}
    
    def Activated(self):
        from py_widget.tools import register
        win = register.Form()
        find_etabs.show_win(win, in_mdi=False)
        
    def IsActive(self):
        return True