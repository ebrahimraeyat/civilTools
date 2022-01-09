from pathlib import Path
from PySide2 import  QtWidgets
from PySide2.QtWidgets import QMessageBox
import FreeCADGui as Gui
import subprocess

import civiltools_rc


civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'serial.ui'))
        self.fill_serial()
        self.create_connections()
        
    def create_connections(self):
        self.form.submit_button.clicked.connect(self.register)


    def fill_serial(self):
        serial = str(subprocess.check_output("wmic csproduct get uuid")).split("\\r\\r\\n")[1].split()[0]
        self.form.serial.setText(serial)

    def register(self):
        from functions import check_legal
        check = check_legal.CheckLegalUse(
            'civiltools5.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/b8cbd078eb7b211e3154804a8bb77633/raw',
            'cfactor',
            serial = self.form.serial.text()
            )
        text = check.submit()

        if text == 'INTERNET':
            msg = 'Please connect to the internet!'
        elif text == 'SERIAL':
            msg = 'You are not registered, Please Contact author to buy the software.'
        elif text == 'REGISTERED':
            msg = "Congrajulation! You are now registered, enjoy using CivilTools."
        QMessageBox.information(None, 'Registeration', msg)


    def accept(self):
        Gui.Control.closeDialog()



