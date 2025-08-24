from pathlib import Path

import numpy as np

from PySide import QtGui
from PySide.QtGui import QFileDialog

try:
    import pyqtgraph as pg
except ImportError:
    import subprocess
    import sys
    package = 'pyqtgraph'
    subprocess.check_call(['python', "-m", "pip", "install", package])

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import FreeCADGui as Gui

from db import ostanha
from exporter import civiltools_config
from building import spectral

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtGui.QWidget):
    def __init__(self,
        etabs_model,
        d: dict,
        ):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_spectral.ui'))
        self.etabs = etabs_model
        self.set_plot_widget()
        self.create_connections()
        self.load_config(d)
        self.update_sa_plot()
        self.text_pos = None
        self.line_x = None
        self.line_y = None
        self.circle = None

    def create_connections(self):
        self.form.ostan.currentIndexChanged.connect(self.set_citys_of_current_ostan)
        self.form.city.currentIndexChanged.connect(self.setA)
        self.form.risk_level.currentIndexChanged.connect(self.update_sa_plot)
        self.form.importance_factor.currentIndexChanged.connect(self.update_sa_plot)
        self.form.soil_type.currentIndexChanged.connect(self.update_sa_plot)
        self.form.create_pushbutton.clicked.connect(self.create_spectral)
        self.form.abir_groupbox.clicked.connect(self.abir_groupbox_clicked)
        self.form.cancel_pushbutton.clicked.connect(self.reject)
    
    def abir_groupbox_clicked(self, check):
        self.form.importance_factor_label.setEnabled(check)
        self.form.rux_label.setEnabled(check)
        self.form.ruy_label.setEnabled(check)
        self.form.importance_factor.setEnabled(check)
        self.form.rux.setEnabled(check)
        self.form.ruy.setEnabled(check)
        self.form.tabWidget.setEnabled(check)


    def create_spectral(self):
        filters = "txt(*.txt)"
        filename, _ = QFileDialog.getSaveFileName(self.form, u'Export Spectrum',
                            '', filters)

        if filename == '':
            return
        A = self.get_acc(self.form.risk_level.currentText())
        importance_factor = float(self.form.importance_factor.currentText())
        rux = self.form.rux.value()
        ruy = self.form.ruy.value()
        g = 981
        c_min = 0.12 * A * g * importance_factor
        t = np.array(self.b_curve.xData)
        abir = self.form.abir_groupbox.isChecked()
        if rux == ruy or not abir:
            Rs = (rux,)
            dirs = ('',)
        else:
            Rs = (rux, ruy)
            dirs = ('_x', '_y')
        for R, dir_ in zip(Rs, dirs):
            fname = f'{filename[:-4]}{dir_}{filename[-4:]}'
            if not abir:
                sa = [A * B for B in self.b_curve.yData]
            else:
                sa = [A * g * B * importance_factor / R  if B / R >= 0.12 else c_min for B in self.b_curve.yData]
            sa = np.array(sa)
            data = np.column_stack([t, sa])
            np.savetxt(fname , data, fmt=['%0.10g','%0.10g'])

    def set_plot_widget(self):
        self.graphWidget = pg.PlotWidget()
        # self.graphWidget.scene().sigMouseMoved.connect(self.mouse_moved)
        self.form.spectral.addWidget(self.graphWidget)
        self.graphWidget.setLabel('bottom', 'Period T', units='sec.')
        self.graphWidget.setLabel('left', 'Sa')
        self.graphWidget.setXRange(0, 4.5, padding=0)
        self.graphWidget.setYRange(0, 3.5, padding=0)
        self.graphWidget.showGrid(x=True, y=True, alpha=0.2)

    def mouse_moved(self, evt):
        self.graphWidget.removeItem(self.text_pos)
        # self.graphWidget.removeItem(self.line_x)
        # self.graphWidget.removeItem(self.line_y)
        self.graphWidget.removeItem(self.circle)
        vb = self.graphWidget.plotItem.vb
        mouse_point = vb.mapSceneToView(evt)
        x = mouse_point.x()
        if 0 <= x <= self.reflection_factor.endT:
            sa = self.reflection_factor.calculatB(x)
            THtml = f'(T = {x:.2f}, S<sub>a</sub> = {sa:.2f}'
            self.text_pos = pg.TextItem(html=THtml, anchor=(0, 1.5), border='k', fill=(0, 0, 255, 100))
            self.graphWidget.addItem(self.text_pos)
            self.text_pos.setPos(x, sa)
            # penTx = pg.mkPen((0, 0, 255), width=1, style=Qt.DashLine)
            # self.line_x = self.graphWidget.addLine(x=x, pen=penTx)
            # self.line_y = self.graphWidget.addLine(y=sa, pen=penTx)
            self.circle = pg.CircleROI([x - .01, sa - .01], [.02, .02], pen=pg.mkPen('b',width=2))
            self.graphWidget.addItem(self.circle)

    def get_current_ostan(self):
        return self.form.ostan.currentText()

    def get_current_city(self):
        return self.form.city.currentText()

    def get_citys_of_current_ostan(self, ostan):
        '''return citys of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_citys_of_current_ostan(self):
        self.form.city.clear()
        ostan = self.get_current_ostan()
        citys = self.get_citys_of_current_ostan(ostan)
        # citys.sort()
        self.form.city.addItems(citys)
        
    def load_config(self, d):
        civiltools_config.load(self.etabs, self.form, d)

    def update_sa_plot(self):
        soil_type = self.form.soil_type.currentText()
        sath = self.form.risk_level.currentText()
        acc = self.get_acc(sath)
        self.reflection_factor = spectral.ReflectionFactor(soilType=soil_type, acc=acc)

        self.graphWidget.clear()
        x = np.arange(0, self.reflection_factor.endT, self.reflection_factor.dt)
        self.b_curve = self.plot_item(x, self.reflection_factor.BCurve())
        self.graphWidget.addItem(self.b_curve)
        # self.graphWidget.setYRange(0, sds * 1.05, padding=0)

    def plot_item(self, x, y, color='r'):
        pen = pg.mkPen(color, width=3)
        finitecurve = pg.PlotDataItem(x, y, connect="finite", pen=pen)
        return finitecurve

    def reject(self):
        self.form.reject()

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        city = self.get_current_city()
        try:
            A = int(ostanha.ostans[ostan][city][0])
            i = self.form.risk_level.findText(sotoh[A - 1])
            self.form.risk_level.setCurrentIndex(i)
        except KeyError:
            pass
    
    def get_acc(self, sath):
        sotoh = {'خیلی زیاد' : 0.35,
                'زیاد' : 0.30,
                'متوسط' : 0.25,
                'کم' : 0.20,
                }
        return sotoh[sath]

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mytree = Form()
    mytree.show()
    sys.exit(app.exec_())