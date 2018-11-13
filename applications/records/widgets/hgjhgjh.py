import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import os

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

pg.mkQApp()

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'earthquake.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

class MainWindow(TemplateBaseClass):  
    def __init__(self):
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('pyqtgraph example: Qt Designer')
        
        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.ui.x_accelerated.setTitle('My Graph')
        self.ui.x_accelerated.setLabel('bottom', 'X axis')
        self.ui.x_accelerated.setLabel('left', 'Y axis')
        self.ui.x_accelerated.showGrid(x=True, y=True)
        # self.ui.plotBtn.clicked.connect(self.plot)
        
        self.show()
        
    def plot(self):
        self.ui.plot.plot(np.random.normal(size=100), clear=True)
        
win = MainWindow()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_() 
