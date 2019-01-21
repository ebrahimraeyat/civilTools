from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from accelerated import processaccelerated as accel
import os
records_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

add_earthquake_win, base_win = uic.loadUiType(os.path.join(records_path, 'widgets', 'earthquake.ui'))


class AddEarthquakeWin(base_win, add_earthquake_win):
    def __init__(self, parent=None):
        super(AddEarthquakeWin, self).__init__()
        self.setupUi(self)
        self.creat_connections()
        try:
            self.load_settings()
        except:
            pass
        self.accelerated = {}

    def load_settings(self):
        qsettings = QSettings("civiltools", "addearthquake")
        self.restoreGeometry(qsettings.value( "geometry", self.saveGeometry()))
        self.splitter.restoreState(qsettings.value("splitter", self.splitter.saveState()))

    def closeEvent(self, event):
        qsettings = QSettings("civiltools", "addearthquake")
        qsettings.setValue( "geometry", self.saveGeometry() )
        qsettings.setValue("splitter", self.splitter.saveState())
        QDialog.accept(self)

    def creat_connections(self):
    	self.x_push_button.clicked.connect(self.set_lineedit_text)
    	self.y_push_button.clicked.connect(self.set_lineedit_text)
    	self.z_push_button.clicked.connect(self.set_lineedit_text)
    	self.x_lineedit.textChanged.connect(self.add_accelerated)
    	self.y_lineedit.textChanged.connect(self.add_accelerated)
    	self.z_lineedit.textChanged.connect(self.add_accelerated)

    def set_lineedit_text(self):
    	button = self.sender()
    	direction = button.objectName()[0]
    	text = QFileDialog.getOpenFileName(filter='AT2(*.AT2)')[0]
    	if not text:
    		return
    	if direction == 'x':
    		self.x_lineedit.setText(text)
    	elif direction == 'y':
    		self.y_lineedit.setText(text)
    	if direction == 'z':
    		self.z_lineedit.setText(text)

    def add_accelerated(self):
    	lineedit = self.sender()
    	direction = lineedit.objectName()[0]
    	filename = lineedit.text()
    	if not filename:
    		return
    	accelerated = accel.Accelerated(filename, direction)
    	self.accelerated[direction] = accelerated
    	time, acc = accelerated.time, accelerated.acc
    	if direction == 'x':
    		self.x_accelerated.plot(time, acc, clear=True)
    	if direction == 'y':
    		self.y_accelerated.plot(time, acc, clear=True)
    	if direction == 'z':
    		self.z_accelerated.plot(time, acc, clear=True)

