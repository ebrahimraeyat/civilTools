import csv
from pathlib import Path

import numpy as np

from PySide2 import  QtWidgets
# from PySide2.QtCore import Qt
# from PySide2 import QtCore
from PySide2.QtWidgets import QFileDialog

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
from qt_models import treeview_system
from building import spectral

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self,
        etabs_model=None,
        ):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'define' / 'create_spectral.ui'))
        self.etabs = etabs_model
        self.set_plot_widget()
        self.set_system_treeview()
        self.fill_cities()
        self.create_connections()
        self.load_config()
        self.setA()
        self.set_x_system_property()
        self.set_y_system_property()
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
        self.form.x_treeview.clicked.connect(self.set_x_system_property)
        self.form.y_treeview.clicked.connect(self.set_y_system_property)
        self.form.create_pushbutton.clicked.connect(self.create_spectral)
        self.form.cancel_pushbutton.clicked.connect(self.reject)
    
    def create_spectral(self):
        filters = "txt(*.txt)"
        filename, _ = QFileDialog.getSaveFileName(self.form, u'Export Spectrum',
                            '', filters)

        if filename == '':
            return
        A = self.get_acc(self.form.risk_level.currentText())
        I = float(self.form.importance_factor.currentText())
        Rux = self.form.rux.value()
        Ruy = self.form.ruy.value()
        c_min = 0.12 * A * I
        t = np.array(self.b_curve.xData)

        if Rux == Ruy:
            Rs = (Rux,)
            dirs = ('',)
        else:
            Rs = (Rux, Ruy)
            dirs = ('_x', '_y')
        for R, dir_ in zip(Rs, dirs):
            fname = f'{filename[:-4]}{dir_}{filename[-4:]}'
            sa = [A * B * I / R if B / R >= 0.12 else c_min for B in self.b_curve.yData]
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
            

    def fill_cities(self):
        ostans = ostanha.ostans.keys()
        self.form.ostan.addItems(ostans)
        self.set_citys_of_current_ostan()
    
    def set_x_system_property(self):
        index = self.form.x_treeview.selectedIndexes()[0]
        if index.isValid():
            data = index.internalPointer()._data
            if len(data) == 1:
                return
            try:
                r = float(data[1])
                # omega = float(data[3])
                # cd = float(data[4])
                self.form.rux.setValue(r)
                # if self.form.simtValue(r)

                # self.omega.setValue(omega)
                # self.cd.setValue(cd)
            except:
                pass
    
    def set_y_system_property(self):
        index = self.form.y_treeview.selectedIndexes()[0]
        if index.isValid():
            data = index.internalPointer()._data
            if len(data) == 1:
                return
            try:
                r = float(data[1])
                # omega = float(data[3])
                # cd = float(data[4])
                self.form.ruy.setValue(r)
                # self.omega.setValue(omega)
                # self.cd.setValue(cd)
            except:
                pass

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
        
    def load_config(self):
        if self.etabs is None:
            return
        try:
            etabs_filename = self.etabs.get_filename()
        except:
            return
        civiltools_config.load(self.etabs, self.form)

    def update_sa_plot(self):
        soil_type = self.form.soil_type.currentText()
        sath = self.form.risk_level.currentText()
        acc = self.get_acc(sath)
        # importance_factor = self.form.importance_factor.currentText()
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
    
    def set_system_treeview(self):
        items = {}

        # Set some random data:
        csv_path =  civiltools_path / 'db' / 'systems.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if (
                    row[0][1] in ['ا', 'ب', 'پ', 'ت', 'ث'] or
                    row[0][0] in ['ا', 'ب', 'پ', 'ت', 'ث']
                    ):
                    i = row[0]
                    # root = items.get(i, None)
                    # if root is None:
                    root = treeview_system.CustomNode(i)
                    items[i] = root
                else:
                    root.addChild(treeview_system.CustomNode(row))
        headers = ('System', 'Ru', 'Omega', 'Cd', 'H_max', 'alpha', 'beta', 'note', 'ID')
        self.form.x_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.x_treeview.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.x_treeview.setColumnWidth(i, 40)
        self.form.y_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
        self.form.y_treeview.setColumnWidth(0, 400)
        for i in range(1,len(headers)):
            self.form.y_treeview.setColumnWidth(i, 40)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mytree = Form()
    mytree.show()
    sys.exit(app.exec_())