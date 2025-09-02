from pathlib import Path

import numpy as np

from PySide import QtGui, QtCore
from PySide.QtGui import (
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    )
from PySide.QtCore import QSettings, Qt

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
from db import ostanha
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent


class Form(QtGui.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'earthquake_factor.ui'))
        self.etabs = etabs_model
        self.stories = self.etabs.SapModel.Story.GetStories()[1]
        # self.fill_cities()
        self.set_plot_widget()
        # self.fill_height_and_no_of_stories()
        # self.fill_top_bot_stories()
        self.create_connections()
        self.load_config()
        self.final_building = civiltools_config.current_building_from_widget(self.form)
        if self.final_building.building2 is None:
            self.set_enabled_tan(False)
        self.structure_model = StructureModel(self.final_building)
        self.form.structure_properties_table.setModel(self.structure_model)
        self.update_sa_plot()
        self.calculate()

    def create_connections(self):
        # self.form.risk_level.currentIndexChanged.connect(self.calculate)
        # self.form.soil_type.currentIndexChanged.connect(self.calculate)
        # self.form.importance_factor.currentIndexChanged.connect(self.calculate)
        # self.form.height_x.valueChanged.connect(self.calculate)
        # self.form.tx_an.valueChanged.connect(self.calculate)
        # self.form.ty_an.valueChanged.connect(self.calculate)
        # self.form.tx1_an.valueChanged.connect(self.calculate)
        # self.form.ty1_an.valueChanged.connect(self.calculate)
        self.form.activate_second_system.clicked.connect(self.second_system_clicked)

        self.form.apply_to_etabs.clicked.connect(self.apply_factors_to_etabs)
        self.form.export_to_word.clicked.connect(self.export_to_word)
        self.form.calculate.clicked.connect(self.calculate)

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
        self.form.top_story_for_height_checkbox_1.clicked.connect(self.fill_height_and_no_of_stories)
        self.form.top_story_for_height1.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.form.x_treeview.clicked.connect(self.calculate)
        # self.form.y_treeview.clicked.connect(self.calculate)
        # self.form.x_treeview_1.clicked.connect(self.calculate)
        # self.form.y_treeview_1.clicked.connect(self.calculate)

    def second_system_clicked(self, checked:bool):
        self.form.x_system_label.setEnabled(checked)
        self.form.y_system_label.setEnabled(checked)
        self.form.x_treeview_1.setEnabled(checked)
        self.form.y_treeview_1.setEnabled(checked)
        self.form.stories_for_apply_earthquake_groupox.setEnabled(checked)
        self.form.stories_for_height_groupox.setEnabled(checked)
        self.form.infill_1.setEnabled(checked)
        self.form.top_story_for_height_checkbox.setEnabled(not checked)
        self.form.top_story_for_height_checkbox.setChecked(not checked)
        self.form.top_story_for_height.setEnabled(not checked)
        self.form.second_earthquake_properties.setEnabled(checked)
        self.form.second_system_group_x.setEnabled(checked)
        self.form.second_system_group_y.setEnabled(checked)
        self.form.special_case.setEnabled(checked)
        self.set_enabled_tan(checked)
        if checked:
            i = self.form.top_x_combo.currentIndex()
            self.form.bot_x1_combo.setCurrentIndex(i)
            i = self.form.top_x_combo.count()
            if i >= 2:
                i -= 2
            else:
                i -= 1
            self.form.top_x1_combo.setCurrentIndex(i)
    
    def set_enabled_tan(self, checked):
        self.form.tx1_an.setEnabled(checked)
        self.form.ty1_an.setEnabled(checked)
        self.form.tan_sec_label.setEnabled(checked)
        self.form.tx_all_an.setEnabled(checked)
        self.form.ty_all_an.setEnabled(checked)
        self.form.tan_all_label.setEnabled(checked)

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


    def get_system(self, view):
        ret = civiltools_config.get_treeview_item_prop(view)
        if ret is None:
            return
        system, lateral, *_ = ret
        if 'x' in view.objectName():
            system = StructureSystem(system, lateral, 'X')
        elif 'y' in view.objectName():
            system = StructureSystem(system, lateral, 'Y')
        return system

    # def fill_cities(self):
    #     ostans = ostanha.ostans.keys()
    #     self.form.ostan.addItems(ostans)
    #     self.set_citys_of_current_ostan()

    # def fill_top_bot_stories(self):
    #     for combo_box in (
    #         self.form.bot_x_combo,
    #         self.form.top_x_combo,
    #         self.form.top_story_for_height,
    #         self.form.bot_x1_combo,
    #         self.form.top_x1_combo,
    #         self.form.top_story_for_height1,
    #         # self.form.bot_y_combo,
    #         # self.form.top_y_combo,
    #     ):
    #         combo_box.addItems(self.stories)
    #     n = len(self.stories)
    #     self.form.bot_x_combo.setCurrentIndex(0)
    #     self.form.top_x_combo.setCurrentIndex(n - 1)
    #     if n > 1:
    #         self.form.top_story_for_height.setCurrentIndex(n - 2)
    #     else:
    #         self.form.top_story_for_height.setCurrentIndex(n - 1)
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

        # second system 
        if self.form.top_story_for_height_checkbox_1.isChecked():
            self.form.top_story_for_height1.setEnabled(True)
            top_story_x1 = top_story_y1 = self.form.top_story_for_height1.currentText()
        else:
            self.form.top_story_for_height1.setEnabled(False)
            top_story_x1 = top_story_y1 = self.form.top_x1_combo.currentText()
        bot_story_x1 = bot_story_y1 = self.form.bot_x1_combo.currentText()
        # bot_story_y = self.form.bot_y_combo.currentText()
        # top_story_y = self.form.top_y_combo.currentText()
        bot_level_x1, top_level_x1, bot_level_y1, top_level_y1 = self.etabs.story.get_top_bot_levels(
                bot_story_x1, top_story_x1, bot_story_y1, top_story_y1, False
                )
        hx, hy = self.etabs.story.get_heights(bot_story_x1, top_story_x1, bot_story_y1, top_story_y1, False)
        nx, ny = self.etabs.story.get_no_of_stories(bot_level_x1, top_level_x1, bot_level_y1, top_level_y1)
        self.form.no_of_story_x1.setValue(nx)
        # self.form.no_story_y_spinbox.setValue(ny)
        self.form.height_x1.setValue(hx)
        # self.form.height_y_spinbox.setValue(hy)

    def get_acc(self, sath):
        sotoh = {'خیلی زیاد' : 0.35,
                'زیاد' : 0.30,
                'متوسط' : 0.25,
                'کم' : 0.20,
                }
        acc = sotoh.get(sath, 0.30)
        return acc

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
    
    def closeEvent(self, event):
        print('close event')
        qsettings = QSettings("civiltools", "cfactor")
        qsettings.setValue("geometry", self.saveGeometry())
        qsettings.setValue("saveState", self.saveState())
        # qsettings.setValue( "maximized", self.isMaximized() )
        qsettings.setValue("splitter", self.form.splitter.saveState())
        # if not self.isMaximized() == True :
        qsettings.setValue("pos", self.pos())
        qsettings.setValue("size", self.size())
        self.accept(event)
        
    def load_settings(self):
        qsettings = QSettings("civiltools", "cfactor")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.form.splitter.restoreState(qsettings.value("splitter", self.form.splitter.saveState()))

    def load_config(self):  
        civiltools_config.load(self.etabs, self.form)
        
    def save_config(self):
        civiltools_config.save(self.etabs, self.form)

    def setSoilProperties(self, build=None):
        if not build:
            build = civiltools_config.current_building_from_widget(self.form)
        xrf = build.soil_reflection_prop_x
        yrf = build.soil_reflection_prop_y
        soil_prop = [build.soilType, xrf.T0, xrf.Ts, xrf.S, xrf.S0]
        xsoil_prop = [xrf.B1, xrf.N, build.bx]
        ysoil_prop = [yrf.B1, yrf.N, build.by]
        for row, item in enumerate(soil_prop):
            if row == 0:
                item = QTableWidgetItem("%s " % item)
            else:
                item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row, 0, item)

        for row, item in enumerate(xsoil_prop):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row + len(soil_prop), 0, item)

        for row, item in enumerate(ysoil_prop):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.form.soilPropertiesTable.setItem(row + len(soil_prop), 1, item)

    def calculate(self):
        self.final_building = civiltools_config.current_building_from_widget(self.form)
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

    def check_analytical_period(self):
        if self.final_building:
            message = '''
            Analytical Period in %s direction < 1.25 * Experimental,
            Do you want to continue?
            '''
            if self.final_building.tx_an < 1.25 * self.final_building.tx_exp:
                if QMessageBox.question(None, 'X Analytical Period', message % 'X') == QMessageBox.No:
                    return
            if self.final_building.ty_an < 1.25 * self.final_building.ty_exp:
                if QMessageBox.question(None, 'Y Analytical Period', message % 'Y') == QMessageBox.No:
                    return
        return True

    def apply_factors_to_etabs(self):
        d = civiltools_config.save(self.etabs, self.form)
        ret = self.check_analytical_period()
        if not ret:
            return
        data = self.get_data_for_apply_earthquakes(d)
        if data is None:
            return
        ret = self.etabs.apply_cfactors_to_edb(data, d=d)
        if ret == 1:
            msg = "Data can not be written to your Etabs file,\nIf you want to correct this problem, try Run analysis."
            title = "Remove Error!"
            QMessageBox.information(None, title, msg)
            return
        msg = "Successfully written to Etabs."
        QMessageBox.information(None, "done", msg)
        self.reject()

    def get_data_for_apply_earthquakes(self, d: dict):
        data = civiltools_config.get_data_for_apply_earthquakes(
            self.final_building,
            etabs=self.etabs,
            d=d,
            )
        if data is None:
            QMessageBox.warning(None, "Not Implemented", "Can not apply earthquake for your systems")
            return None
        return data

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

