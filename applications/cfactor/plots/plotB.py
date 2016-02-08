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

    #def updateBCurve(self, build):
        #self.p.setTitle(u'منحنی ضریب بازتاب، خاک نوع {0}، پهنه با خطر نسبی {1}'.format(
                            #build.soilType, build.risk))
        #penB1 = pg.mkPen('r', width=2, style=Qt.DashLine)
        #penN = pg.mkPen('g', width=2)
        #penB = pg.mkPen('b', width=5)
        #penTx = pg.mkPen((153, 0, 153), width=1, style=Qt.DashDotLine)
        #penTy = pg.mkPen((153, 0, 0), width=1, style=Qt.DashDotDotLine)
        #dt = build.xReflectionFactor.dt
        #x = np.arange(0, 4.5, dt)
        #B1 = build.xReflectionFactor.B1Curve()
        #N = build.xReflectionFactor.NCurve()
        #B = B1 * N
        #self.p.legend.items = []
        #self.p.plot(x, B1, pen=penB1, name="B1", clear=True)
        #self.p.plot(x, N, pen=penN, name="N")
        #self.p.plot(x, B, pen=penB, name="B")
        #if build.useTan:
            #self.p.addLine(x=build.xTan, pen=penTx)
            #self.p.addLine(x=build.yTan, pen=penTy)
        #else:
            #self.p.addLine(x=build.Tx, pen=penTx)
            #self.p.addLine(x=build.Ty, pen=penTy)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = PlotB()
    form.show()
    app.exec_()