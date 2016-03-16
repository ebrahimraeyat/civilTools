# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import QWidget, QVBoxLayout, QApplication
from PyQt4.QtCore import Qt
import numpy as np
import pyqtgraph as pg
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class PlotB(QWidget):

    def __init__(self, parent=None):
        super(PlotB, self).__init__(parent)

        self.win = pg.GraphicsWindow()
        self.p = self.createAxis(self.win)
        my_layout = QVBoxLayout()
        my_layout.addWidget(self.win)
        self.setLayout(my_layout)

    def createAxis(self, window):
        p = window.addPlot()
        p.setLabel('bottom', text='T', units='Sec')
        p.setLabel('left', text='B1')
        p.showGrid(x=True, y=True)
        p.addLegend()
        p.legend.anchor((-9, 0), (0, 0))
        p.setXRange(0, 4.5, padding=0)
        p.setYRange(0, 4, padding=0)
        return p


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = PlotB()
    form.show()
    app.exec_()