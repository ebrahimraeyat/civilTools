from pathlib import Path

from PySide2 import  QtWidgets
from PySide2.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    )
from PySide2.QtCore import QSettings, Qt

import FreeCADGui as Gui

from building.build import *
from models import StructureModel
from exporter import config
import civiltools_rc

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
        self.set_properties_from_json()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.form.structure_properties_table.setModel(self.structure_model)
        self.create_connections()
        # self.load_settings()
        self.calculate()
        self.fill_dialog()

    def create_connections(self):
        self.form.xTAnalaticalSpinBox.valueChanged.connect(self.calculate)
        self.form.yTAnalaticalSpinBox.valueChanged.connect(self.calculate)
        self.form.xTAnalaticalSpinBox.valueChanged.connect(self.set_bx)
        self.form.yTAnalaticalSpinBox.valueChanged.connect(self.set_by)
        self.form.apply_to_etabs.clicked.connect(self.apply_factors_to_etabs)
        self.form.export_to_word.clicked.connect(self.export_to_word)

    def set_bx(self):
        self.form.bx = self.final_building.Bx
    
    def set_by(self):
        self.form.by = self.final_building.By

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

    def set_properties_from_json(self):
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

    def fill_dialog(self):
        if self.city is not None:
            self.form.risk_level.setText(self.risk_level)
            self.form.importance_factor.setText(str(self.importance_factor))
            self.form.rx.setText(str(self.final_building.x_system.Ru))
            self.form.ry.setText(str(self.final_building.y_system.Ru))
            self.form.bx.setText(str(self.final_building.Bx))
            self.form.by.setText(str(self.final_building.By))



    def current_building(self):
        if self.city is None:
            return None
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
        self.save_config()
        QMessageBox.information(None, "done", msg)

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

    def export_to_word(self):
        filters = "docx(*.docx)"
        directory = str(self.json_file.parent)
        filename, _ = QFileDialog.getSaveFileName(None, 'Export To Word',
                                                  directory, filters)
        if filename == '':
            return
        if not filename.endswith(".docx"):
            filename += ".docx"
        from exporter import export_to_word as word
        word.export(self.final_building, filename)

