from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    )
from PySide2.QtCore import QSettings, Qt

import FreeCADGui as Gui

from building.build import *
from models import StructureModel
from exporter import config

civiltools_path = Path(__file__).absolute().parent.parent

# rTable = RFactorTable()
# systemTypes = rTable.getSystemTypes()


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model, json_file):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'earthquake_factor.ui'))
        self.json_file = json_file
        self.city = None
        self.etabs = etabs_model
        self.load_config()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.form.structure_properties_table.setModel(self.structure_model)
        self.create_connections()
        # self.load_settings()
        self.calculate()

    def create_connections(self):
        self.form.xTAnalaticalSpinBox.valueChanged.connect(self.calculate)
        self.form.yTAnalaticalSpinBox.valueChanged.connect(self.calculate)

    def create_widgets(self):
        self.load_config()
        #
        # # curve widget
        # self.curveBWidget = pl()
        # self.p = self.curveBWidget.p
        # self.curveBWidget.setMinimumSize(450, 300)
        # draw_layout = QVBoxLayout()
        # draw_layout.addWidget(self.curveBWidget)
        # self.draw_frame.setLayout(draw_layout)


    def accept(self):
        # qsettings = QSettings("civiltools", "cfactor")
        # qsettings.setValue("geometry", self.saveGeometry())
        # qsettings.setValue("hsplitter1", self.form.hsplitter1.saveState())
        self.save_config()
        self.apply_factors_to_etabs()
        Gui.Control.closeDialog()
        
    def load_settings(self):
        qsettings = QSettings("civiltools", "cfactor")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.form.hsplitter1.restoreState(qsettings.value("hsplitter1", self.form.hsplitter1.saveState()))

    def load_config(self):
        if self.json_file.exists():
            tx, ty = config.get_analytical_periods(self.json_file)
            self.form.xTAnalaticalSpinBox.setValue(tx)
            self.form.yTAnalaticalSpinBox.setValue(ty)

    def save_config(self):
        tx = self.form.xTAnalaticalSpinBox.value()
        ty = self.form.yTAnalaticalSpinBox.value()
        config.save_analytical_periods(self.json_file, tx, ty)

    def getTAnalatical(self):
        xTan = self.form.xTAnalaticalSpinBox.value()
        yTan = self.form.yTAnalaticalSpinBox.value()
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

    def current_building(self):
        if self.city is None:
            if self.json_file is None:
                etabs_filename = self.etabs.get_filename()
                self.json_file = etabs_filename.with_suffix('.json')
            d = config.load(self.json_file)
            self.risk_level = d['risk_level']
            self.height_x = d['height_x']
            self.importance_factor = float(d['importance_factor'])
            self.soil = d['soil_type']
            self.city = d['city']
            self.noStory = d['no_of_story_x']
            self.xSystemType = d['x_system_name']
            self.xLateralType = d['x_lateral_name']
            self.ySystemType = d['y_system_name']
            self.yLateralType = d['y_lateral_name']
            self.is_infill = d['infill']
            self.xSystem = StructureSystem(self.xSystemType, self.xLateralType, "X")
            self.ySystem = StructureSystem(self.ySystemType, self.yLateralType, "Y")
        xTan, yTan = self.getTAnalatical()
        build = Building(
                    self.risk_level,
                    self.importance_factor,
                    self.soil,
                    self.noStory,
                    self.height_x,
                    self.is_infill,
                    self.xSystem,
                    self.ySystem,
                    self.city,
                    xTan,
                    yTan,
                    )
        return build

    def calculate(self):
        self.dirty = False
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

    def apply_factors_to_etabs(self):
        ret = self.etabs.apply_cfactor_to_edb(self.final_building)
        if ret == 1:
            msg = "Data can not be written to your Etabs file,\n If you want to correct this problem, try Run analysis."
            title = "Remove Error?"
            QMessageBox.information(None, title, msg)
            return
        msg = "Successfully written to Etabs."
        QMessageBox.information(None, "done", msg)

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

