from pathlib import Path
import csv

import numpy as np

from PySide2 import  QtWidgets, QtCore
from PySide2.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    )
from PySide2.QtCore import QSettings, Qt

try:
    import pyqtgraph as pg
except ImportError:
    package = 'pyqtgraph'
    from freecad_funcs import install_package
    install_package(package)
    import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import FreeCADGui as Gui

from building.build import StructureSystem, Building
from building import spectral
from models import StructureModel
from exporter import civiltools_config
from qt_models import treeview_system
from db import ostanha
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'earthquake_factor.ui'))
        self.etabs = etabs_model
        self.stories = self.etabs.SapModel.Story.GetStories()[1]
        self.fill_cities()
        self.set_plot_widget()
        self.set_system_treeview()
        self.fill_height_and_no_of_stories()
        self.fill_top_bot_stories()
        self.create_connections()
        self.load_config()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.form.structure_properties_table.setModel(self.structure_model)
        self.update_sa_plot()
        self.calculate()
        self.set_bx_by()
        self.set_x_system_property()
        self.set_y_system_property()

    def create_connections(self):
        self.form.t_an_x.valueChanged.connect(self.calculate)
        self.form.t_an_y.valueChanged.connect(self.calculate)
        self.form.risk_level.currentIndexChanged.connect(self.calculate)
        self.form.soil_type.currentIndexChanged.connect(self.calculate)
        self.form.importance_factor.currentIndexChanged.connect(self.calculate)
        self.form.height_x.valueChanged.connect(self.calculate)

        self.form.apply_to_etabs.clicked.connect(self.apply_factors_to_etabs)
        self.form.export_to_word.clicked.connect(self.export_to_word)

        self.form.ostan.currentIndexChanged.connect(self.set_citys_of_current_ostan)
        self.form.city.currentIndexChanged.connect(self.setA)
        self.form.risk_level.currentIndexChanged.connect(self.update_sa_plot)
        self.form.importance_factor.currentIndexChanged.connect(self.update_sa_plot)
        self.form.soil_type.currentIndexChanged.connect(self.update_sa_plot)
        self.form.bot_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.form.top_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.form.save_pushbutton.clicked.connect(self.save)
        self.form.top_story_for_height_checkbox.clicked.connect(self.fill_height_and_no_of_stories)
        self.form.top_story_for_height.currentIndexChanged.connect(self.fill_height_and_no_of_stories)

        self.form.x_treeview.clicked.connect(self.set_x_system_property)
        self.form.y_treeview.clicked.connect(self.set_y_system_property)
        self.form.x_treeview.clicked.connect(self.calculate)
        self.form.y_treeview.clicked.connect(self.calculate)

    def set_plot_widget(self):
        self.graphWidget = pg.PlotWidget()
        # self.graphWidget.scene().sigMouseMoved.connect(self.mouse_moved)
        self.form.spectral.addWidget(self.graphWidget)
        self.graphWidget.setLabel('bottom', 'Period T', units='sec.')
        self.graphWidget.setLabel('left', 'Sa')
        self.graphWidget.setXRange(0, 4.5, padding=0)
        self.graphWidget.setYRange(0, 3.5, padding=0)
        self.graphWidget.showGrid(x=True, y=True, alpha=0.2)

    def update_sa_plot(self):
        soil_type = self.form.soil_type.currentText()
        sath = self.form.risk_level.currentText()
        acc = self.get_acc(sath)
        self.reflection_factor = spectral.ReflectionFactor(soilType=soil_type, acc=acc)

        self.graphWidget.clear()
        x = np.arange(0, self.reflection_factor.endT, self.reflection_factor.dt)
        self.graphWidget.addItem(self.plot_item(x, self.reflection_factor.BCurve()))
        # self.graphWidget.setYRange(0, sds * 1.05, padding=0)

    def plot_item(self, x, y, color='r'):
        pen = pg.mkPen(color, width=3)
        finitecurve = pg.PlotDataItem(x, y, connect="finite", pen=pen)
        return finitecurve

    def select_treeview_item(self, view, i, n):
        index = view.model().index(i, 0, QtCore.QModelIndex())
        index2 = view.model().index(n, 0, index)
        view.clearSelection()
        view.setCurrentIndex(index2)
        # view.setExpanded(index, False)
        view.setExpanded(index2, True)

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

    def get_system(self, view):
        ret = civiltools_config.get_treeview_item_prop(view)
        if ret is None:
            return
        system, lateral, *args = ret
        if 'x' in view.objectName():
            system = StructureSystem(system, lateral, 'X')
        elif 'y' in view.objectName():
            system = StructureSystem(system, lateral, 'Y')
        return system


    def set_x_system_property(self):
        index = self.form.x_treeview.selectedIndexes()[0]
        if index.isValid():
            data = index.internalPointer()._data
            if len(data) == 1:
                return
            try:
                r = float(data[1])
                self.form.rux.setValue(r)
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
                self.form.ruy.setValue(r)
            except:
                pass

    def set_bx(self):
        self.form.bx.setText(f'{self.final_building.Bx:0.3f}')
    
    def set_by(self):
        self.form.by.setText(f'{self.final_building.By:0.3f}')

    def fill_cities(self):
        ostans = ostanha.ostans.keys()
        self.form.ostan.addItems(ostans)
        self.set_citys_of_current_ostan()

    def fill_top_bot_stories(self):
        for combo_box in (
            self.form.bot_x_combo,
            self.form.top_x_combo,
            self.form.top_story_for_height,
            # self.form.bot_y_combo,
            # self.form.top_y_combo,
        ):
            combo_box.addItems(self.stories)
        n = len(self.stories)
        self.form.bot_x_combo.setCurrentIndex(0)
        self.form.top_x_combo.setCurrentIndex(n - 1)
        self.form.top_story_for_height.setCurrentIndex(n - 2)
        # self.form.bot_y_combo.setCurrentIndex(0)
        # self.form.top_y_combo.setCurrentIndex(n - 2)

    def fill_height_and_no_of_stories(self):
        if self.form.top_story_for_height_checkbox.isChecked():
            self.form.top_story_for_height.setEnabled(True)
            top_story_x = top_story_y = self.form.top_story_for_height.currentText()
        else:
            self.form.top_story_for_height.setEnabled(False)
            top_story_x = top_story_y = self.form.top_x_combo.currentText()
        bot_story_x = bot_story_y = self.form.bot_x_combo.currentText()
        # bot_story_y = self.form.bot_y_combo.currentText()
        # top_story_y = self.form.top_y_combo.currentText()
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.etabs.story.get_top_bot_levels(
                bot_story_x, top_story_x, bot_story_y, top_story_y, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x, top_story_x, bot_story_y, top_story_y, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x, top_level_x, bot_level_y, top_level_y)
        self.form.no_of_story_x.setValue(nx)
        # self.form.no_story_y_spinbox.setValue(ny)
        self.form.height_x.setValue(hx)
        # self.form.height_y_spinbox.setValue(hy)

    def get_acc(self, sath):
        sotoh = {'خیلی زیاد' : 0.35,
                'زیاد' : 0.30,
                'متوسط' : 0.25,
                'کم' : 0.20,
                }
        return sotoh[sath]

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
        
    def load_settings(self):
        qsettings = QSettings("civiltools", "cfactor")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.form.hsplitter1.restoreState(qsettings.value("hsplitter1", self.form.hsplitter1.saveState()))

    def load_config(self):  
        civiltools_config.load(self.etabs, self.form)
        
    def save_config(self):
        civiltools_config.save(self.etabs, self.form)

    def getTAnalatical(self):
        xTan = self.form.t_an_x.value()
        yTan = self.form.t_an_y.value()
        return xTan, yTan

    def setSoilProperties(self, build=None):
        if not build:
            build = self.current_building()
        xrf = build.soil_reflection_prop_x
        yrf = build.soil_reflection_prop_y
        soilProp = [build.soilType, xrf.T0, xrf.Ts, xrf.S, xrf.S0]
        xSoilProp = [xrf.B1, xrf.N, build.Bx]
        ySoilProp = [yrf.B1, yrf.N, build.By]
        for row, item in enumerate(soilProp):
            if row == 0:
                item = QTableWidgetItem("%s " % item)
            else:
                item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row, 0, item)

        for row, item in enumerate(xSoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row + len(soilProp), 0, item)

        for row, item in enumerate(ySoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row + len(soilProp), 1, item)

    def set_bx_by(self):
        if hasattr(self, 'final_building'):
            self.form.bx.setValue(self.final_building.Bx)
            self.form.by.setValue(self.final_building.By)

    def current_building(self):
        xTan, yTan = self.getTAnalatical()
        risk_level = self.form.risk_level.currentText()
        city = self.form.city.currentText()
        soil = self.form.soil_type.currentText()
        importance_factor = float(self.form.importance_factor.currentText())
        height_x = self.form.height_x.value()
        no_of_story = self.form.no_of_story_x.value()
        is_infill = self.form.infill.isChecked()
        x_system = self.get_system(self.form.x_treeview)
        y_system = self.get_system(self.form.y_treeview)
        if x_system is None or y_system is None:
            return
        build = Building(
                    risk_level,
                    importance_factor,
                    soil,
                    no_of_story,
                    height_x,
                    is_infill,
                    x_system,
                    y_system,
                    city,
                    xTan,
                    yTan,
                    )
        return build

    def calculate(self):
        self.final_building = self.current_building()
        if not self.final_building:
            return
        # self.setSoilProperties(self.final_building)
        self.structure_model.beginResetModel()
        self.structure_model.build = self.final_building
        self.structure_model.endResetModel()
        results = self.final_building.results
        if results[0] is False:
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, str(err))
        else:
            self.set_bx_by()

    def check_analytical_period(self):
        if self.final_building:
            message = '''
            Analytical Period in %s direction < 1.25 * Experimental,
            Do you want to continue?
            '''
            if self.final_building.x_period_an < 1.25 * self.final_building.exp_period_x:
                if QMessageBox.question(None, 'X Analytical Period', message % 'X') == QMessageBox.No:
                    return
            if self.final_building.y_period_an < 1.25 * self.final_building.exp_period_y:
                if QMessageBox.question(None, 'Y Analytical Period', message % 'Y') == QMessageBox.No:
                    return
        return True

    def apply_factors_to_etabs(self):
        ret = self.check_analytical_period()
        if not ret:
            return
        bot_story = self.form.bot_x_combo.currentText()
        top_story = self.form.top_x_combo.currentText()
        ret = self.etabs.apply_cfactor_to_edb(
                self.final_building,
                bot_story,
                top_story,
                )
        if ret == 1:
            msg = "Data can not be written to your Etabs file,\n If you want to correct this problem, try Run analysis."
            title = "Remove Error?"
            QMessageBox.information(None, title, msg)
            return
        msg = "Successfully written to Etabs."
        civiltools_config.save(self.etabs, self.form)
        QMessageBox.information(None, "done", msg)

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

    def export_to_word(self):
        filters = "docx(*.docx)"
        directory = str(self.etabs.get_filepath())
        filename, _ = QFileDialog.getSaveFileName(None, 'Export To Word',
                                                  directory, filters)
        if filename == '':
            return
        if not filename.endswith(".docx"):
            filename += ".docx"
        from exporter import export_to_word as word
        word.export(self.final_building, filename)

    def reject(self):
        self.form.reject()

