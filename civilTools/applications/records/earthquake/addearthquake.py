from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from ..accelerated import processaccelerated as accel

add_earthquake_win, base_win = uic.loadUiType('applications/records/widgets/earthquake.ui')


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
        settings = QSettings()
        self.restoreGeometry(settings.value("AddEarthquake\Geometry"))
        self.splitter.restoreState(settings.value("AddEarthquake\Splitter"))

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("AddEarthquake\Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("AddEarthquake\Splitter",
                QVariant(self.splitter.saveState()))
        
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

