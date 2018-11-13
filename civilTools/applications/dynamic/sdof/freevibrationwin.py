from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from .freevibration import Vibration as fv
import pyqtgraph as pg
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
free_vib_win, base_win = uic.loadUiType('applications/dynamic/widgets/sdof_free_vibration.ui')


class FreeVibrationWin(base_win, free_vib_win):
    def __init__(self, parent=None):
        super(FreeVibrationWin, self).__init__()
        self.setupUi(self)
        self.fv_plot.setLabel('bottom', 'Time', units='Sec')
        self.fv_plot.setLabel('left', 'Disp', units='Cm')
        self.creat_connections()
        try:
            self.load_settings()
        except:
            pass
        self.free_items = []
        self.sin_items = []
        self.constant_items = []

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("FreeVibration\Geometry"))

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("FreeVibration\Geometry",
                          QVariant(self.saveGeometry()))
        
    def creat_connections(self):
        self.draw_free_button.clicked.connect(self.plot_free)
        self.clear_free_button.clicked.connect(self.clear_free)
        self.draw_sin_button.clicked.connect(self.plot_sin)
        self.clear_sin_button.clicked.connect(self.clear_sin)
        self.draw_constant_button.clicked.connect(self.plot_constant)
        self.clear_constant_button.clicked.connect(self.clear_constant)
        self.free_undo_button.clicked.connect(self.free_undo)
        self.sin_undo_button.clicked.connect(self.sin_undo)
        self.constant_undo_button.clicked.connect(self.constant_undo)

    def current_sdof(self):
        m = self.m_spinbox.value()
        k = self.k_spinbox.value()
        xi = self.xi_spinbox.value()
        u0 = self.u0_spinbox.value()
        v0 = self.v0_spinbox.value() * 100
        duration = self.duration_spinbox.value()
        return m, k, xi, u0, v0, duration

    def plot_free(self):
        items = []
        m, k, xi, u0, v0, duration = self.current_sdof()
        self.fv_plot.setXRange(0, duration)
        vibration = fv(m, k, xi, u0, v0, duration)
        t = vibration.t
        disp, push = vibration.free_output()
        pen = pg.mkPen('b', width=2)
        disp_item = pg.PlotDataItem(t, disp, connect="finite", pen=pen)
        self.fv_plot.addItem(disp_item)
        items.append(disp_item)
        if self.push_checkbox.isChecked():
            pen = pg.mkPen('r', width=2)
            push_item_pos = pg.PlotDataItem(t, push, connect="finite", pen=pen)
            push_item_neg = pg.PlotDataItem(t, -push, connect="finite", pen=pen)
            items.append(push_item_pos)
            items.append(push_item_neg)
            self.fv_plot.addItem(push_item_pos)
            self.fv_plot.addItem(push_item_neg)
        self.free_items.append(items)
        # self.fv_plot.addLegend()

    def plot_sin(self):
        items = []
        m, k, xi, u0, v0, duration = self.current_sdof()
        self.sin_plot.setXRange(0, duration)
        p0 = self.p0_spinbox.value()
        w = self.w_spinbox.value()
        vibration = fv(m, k, xi, u0, v0, duration, p0, w)
        t = vibration.t
        transient, steady_state, ut = vibration.sin_output()
        pen = pg.mkPen('b', width=2)
        disp_item = pg.PlotDataItem(t, ut, connect="finite", pen=pen)
        self.sin_plot.addItem(disp_item)
        if self.steady_checkbox.isChecked():
            pen = pg.mkPen('r', width=2)
            steady_item = pg.PlotDataItem(t, steady_state, connect="finite", pen=pen)
            self.sin_plot.addItem(steady_item)
            items.append(steady_item)
        if self.transient_checkbox.isChecked():
            pen = pg.mkPen('k', width=2)
            transient_item = pg.PlotDataItem(t, transient, connect="finite", pen=pen)
            self.sin_plot.addItem(transient_item)
            items.append(transient_item)
        tn = 2 * np.pi / vibration.wn
        var = 2 * np.pi * t / tn
        relativ_sin = -.5 * (var * np.cos(var) - np.sin(var))
        relativ_sin_item = pg.PlotDataItem(t/tn, relativ_sin, pen=pen)
        self.sin_plot2.addItem(relativ_sin_item)
        items.append(disp_item)
        items.append(relativ_sin_item)
        self.sin_items.append(items)

    def plot_constant(self):
        m, k, xi, u0, v0, duration = self.current_sdof()
        self.constant_plot.setXRange(0, duration)
        p0 = self.cp0_spinbox.value()
        vibration = fv(m, k, xi, u0, v0, duration, p0=None, w=None, cp0=p0)
        t = vibration.t
        ut = vibration.constant_output()
        pen = pg.mkPen('b', width=2)
        item = pg.PlotDataItem(t, ut, connect="finite", pen=pen)
        self.constant_plot.addItem(item)
        self.constant_items.append(item)

    def free_undo(self):
        if not self.free_items:
            return
        items = self.free_items.pop()
        for item in items:
            self.fv_plot.removeItem(item)

    def sin_undo(self):
        if not self.sin_items:
            return
        items = self.sin_items.pop()
        item = items.pop()
        self.sin_plot2.removeItem(item)
        for item in items:
            self.sin_plot.removeItem(item)

    def constant_undo(self):
        if not self.constant_items:
            return
        item = self.constant_items.pop()
        self.constant_plot.removeItem(item)


    def clear_free(self):
        self.fv_plot.clear()

    def clear_sin(self):
        self.sin_plot.clear()
        self.sin_plot2.clear()

    def clear_constant(self):
        self.constant_plot.clear()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = FreeVibrationWin()
    window.show()
    app.exec_()

