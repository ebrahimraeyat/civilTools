# -*- coding: utf-8 -*-
from os.path import dirname
import sys
import os
from pathlib import Path

from comtypes.typeinfo import ELEMDESC
abs_path = os.path.dirname(__file__)
sys.path.insert(0, abs_path)
civiltools_path = Path(__file__).absolute().parent.parent.parent
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from db import ostanha
from building.build import *
from models import *
import pyqtgraph as pg
from plots.plotB import PlotB as pl
import export
from exporter import config

rTable = RFactorTable()
systemTypes = rTable.getSystemTypes()

__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "5.0"
link_ebrahim = ('Website: <a href="%s"><span style=" '
                'text-decoration: underline; color:#0000ff;">'
                '%s</span></a>') % (__url__, __url__)

main_window = uic.loadUiType(os.path.join(abs_path, 'widgets', 'mainwindow.ui'))[0]
serial_base, serial_window = uic.loadUiType(civiltools_path / 'widgets' / 'serial.ui')


class Ui(QMainWindow, main_window):

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.dirty = False
        self.lastDirectory = ''
        self.printer = None
        self.create_widgets()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.structure_properties_table.setModel(self.structure_model)
        self.resizeColumns()
        self.create_connections()
        self.add_actions()
        self.load_settings()
        self.load_config()
        self.calculate()
        self.setWindowTitle(f"CFactor v{__version__}")

    def add_actions(self):
        self.action_to_etabs.triggered.connect(self.export_to_etabs)
        self.action_automatic_drift.triggered.connect(self.get_drift_automatically)
        self.action_open.triggered.connect(self.load)
        self.action_save.triggered.connect(self.save)
        self.action_save_spectrals.triggered.connect(self.exportBCurveToCsv)
        self.action_word.triggered.connect(self.export_to_word)
        self.action_torsion_table.triggered.connect(self.show_torsion_table)
        self.action_story_forces.triggered.connect(self.show_story_forces)
        self.action_get_weakness.triggered.connect(self.get_weakness_ratio)
        self.action_show_weakness.triggered.connect(self.show_weakness_ratio)
        self.action_get_story_stiffness.triggered.connect(self.get_story_stiffness_table)
        self.action_show_story_stiffness.triggered.connect(self.show_story_stiffness_table)
        self.action_get_irregularity_of_mass.triggered.connect(self.get_irregularity_of_mass)
        self.action_show_aj.triggered.connect(self.aj)
        self.action_correct_beams_j.triggered.connect(self.correct_torsion_stiffness_factor)
        self.action_offset_beam.triggered.connect(self.offset_beam)
        self.action_connect_beam.triggered.connect(self.connect_beam)
        self.action_remove_backups.triggered.connect(self.clear_backups)
        self.action_restore_backup.triggered.connect(self.restore_backup)
        self.action_scale_response_spec.triggered.connect(self.scale_response_spectrums)
        self.action_create_section_cuts.triggered.connect(self.create_section_cuts)
        self.action_create_period_file.triggered.connect(self.create_period_file)
        self.action_wall_loads.triggered.connect(self.wall_load_on_frames)
        self.action_frame_sections.triggered.connect(self.assign_frame_sections)

    def create_connections(self):
        self.calculate_button.clicked.connect(self.calculate)
        self.x_treeWidget.itemActivated.connect(self.xactivate)
        self.ostanBox.currentIndexChanged.connect(self.set_shahrs_of_current_ostan)
        self.shahrBox.currentIndexChanged.connect(self.setA)

    def resizeColumns(self):
        for column in (X, Y):
            self.structure_properties_table.resizeColumnToContents(column)

    def create_widgets(self):
        ostans = ostanha.ostans.keys()
        self.ostanBox.addItems(ostans)
        self.set_shahrs_of_current_ostan()
        self.setA()
        #
        # curve widget
        self.curveBWidget = pl()
        self.p = self.curveBWidget.p
        self.curveBWidget.setMinimumSize(450, 300)
        draw_layout = QVBoxLayout()
        draw_layout.addWidget(self.curveBWidget)
        self.draw_frame.setLayout(draw_layout)

        for i in range(5):
            self.soilPropertiesTable.setSpan(i, 0, 1, 2)
        iterator = QTreeWidgetItemIterator(self.x_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.x_treeWidget.setCurrentItem(item, 0)
                break
            i += 1
        iterator = QTreeWidgetItemIterator(self.y_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.y_treeWidget.setCurrentItem(item, 0)
                break
            i += 1

    def closeEvent(self, event):
        qsettings = QSettings("civiltools", "cfactor")
        qsettings.setValue("geometry", self.saveGeometry())
        qsettings.setValue("saveState", self.saveState())
        qsettings.setValue("pos", self.pos())
        qsettings.setValue("size", self.size())
        qsettings.setValue("hsplitter", self.hsplitter.saveState())
        qsettings.setValue("v1splitter", self.v1splitter.saveState())
        qsettings.setValue("v2splitter", self.v2splitter.saveState())
        ret = self.ok_to_continue()
        if ret == QMessageBox.Yes:
            self.save_config()
        elif ret == QMessageBox.No:
            event.accept()
        elif ret == QMessageBox.Cancel:
            event.ignore()

    def load_settings(self):
        qsettings = QSettings("civiltools", "cfactor")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.restoreState(qsettings.value("saveState", self.saveState()))
        self.move(qsettings.value("pos", self.pos()))
        self.resize(qsettings.value("size", self.size()))
        self.hsplitter.restoreState(qsettings.value("hsplitter", self.hsplitter.saveState()))
        self.v1splitter.restoreState(qsettings.value("v1splitter", self.v1splitter.saveState()))
        self.v2splitter.restoreState(qsettings.value("v2splitter", self.v2splitter.saveState()))

    def load_config(self, json_file=None):
        if not json_file:
            appdata_dir = Path(os.getenv('APPDATA'))
            cfactor_dir = appdata_dir / 'civiltools' / 'cfactor'
            if not cfactor_dir.exists():
                return
            else:
                json_file = cfactor_dir / 'cfactor.json'
                if not json_file.exists():
                    return
        config.load(self, json_file)

    def save_config(self, json_file=None):
        if not json_file:
            appdata_dir = Path(os.getenv('APPDATA'))
            civiltoos_dir = appdata_dir / 'civiltools'
            if not civiltoos_dir.exists():
                civiltoos_dir.mkdir()
            cfactor_dir = civiltoos_dir / 'cfactor'
            if not cfactor_dir.exists():
                cfactor_dir.mkdir()
            json_file = cfactor_dir / 'cfactor.json'
        config.save(self, json_file)

    def ok_to_continue(self, title='save config?', message='save configuration file?'):
        return QMessageBox.question(self, title, message,
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

    def helpAbout(self):
        QMessageBox.about(self, "درباره نرم افزار محاسبه ضریب زلزله",
                          """<b>C Factor</b> v {0}   ۱۳۹۶/۰۱/۰۳
                <p>توسعه دهنده: ابراهیم رعیت رکن آبادی
                <p>این نرم افزار برای محاسبه ضریب زلزله مطابق ویرایش چهارم
                آیین نامه ۲۸۰۰ زلزله تهیه شده است.
                <p>از مهندسین عزیز خواهش میکنم با بررسی این برنامه ضعفها و ایرادات برنامه رو
                در وبلاگ من یادآوری کنند.
                <p>برای دریافت آخرین نسخه نرم افزار و مطالب مفید دیگر
                به وبلاگ زیر مراجعه نمایید:
                    <p> {1}""".format(__version__, link_ebrahim))

    def xactivate(self):
        if self.x_treeWidget.currentItem().parent():
            system = self.x_treeWidget.currentItem().parent().text(0)
            lateral = self.x_treeWidget.currentItem().text(0)
            self.y_treeWidget.scrollToItem(self.x_treeWidget.currentItem())
            return (system, lateral)
        return None

    def yactivate(self):
        if self.y_treeWidget.currentItem().parent():
            system = self.y_treeWidget.currentItem().parent().text(0)
            lateral = self.y_treeWidget.currentItem().text(0)
            return (system, lateral)
        return None

    def get_current_ostan(self):
        return self.ostanBox.currentText()

    def get_current_shahr(self):
        return self.shahrBox.currentText()

    def get_shahrs_of_current_ostan(self, ostan):
        '''return shahrs of ostan'''
        return ostanha.ostans[ostan].keys()

    def set_shahrs_of_current_ostan(self):
        self.shahrBox.clear()
        ostan = self.get_current_ostan()
        shahrs = self.get_shahrs_of_current_ostan(ostan)
        # shahrs.sort()
        self.shahrBox.addItems(shahrs)

    def setA(self):
        sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
        ostan = self.get_current_ostan()
        shahr = self.get_current_shahr()
        try:
            A = int(ostanha.ostans[ostan][shahr][0])
            self.accText.setText(sotoh[A - 1])
        except KeyError:
            pass

    def get_current_soil_type(self):
        return str(self.soilType.currentText())

    def setInfillCheckBoxStatus(self, xSystem, ySystem):
        infill = xSystem.is_infill and ySystem.is_infill
        if infill is None:
            self.infillCheckBox.setEnabled(False)
            self.infillCheckBox.setCheckState(False)
        else:
            self.infillCheckBox.setEnabled(True)

    def getTAnalatical(self):
        useTan = True
        xTan = self.xTAnalaticalSpinBox.value()
        yTan = self.yTAnalaticalSpinBox.value()
        return useTan, xTan, yTan

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
            self.soilPropertiesTable.setItem(row, 0, item)

        for row, item in enumerate(xSoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.soilPropertiesTable.setItem(row + len(soilProp), 0, item)

        for row, item in enumerate(ySoilProp):
            item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.soilPropertiesTable.setItem(row + len(soilProp), 1, item)

    def updateBCurve(self, build):
        self.p.clear()
        self.p.addLegend()
        self.p.legend.anchor((-9, 0), (0, 0))
        self.p.setTitle('منحنی ضریب بازتاب، خاک نوع {0}، پهنه با خطر نسبی {1}'.format(
            build.soilType, build.risk_level))
        penB1 = pg.mkPen('r', width=2, style=Qt.DashLine)
        penN = pg.mkPen('g', width=2)
        penB = pg.mkPen('b', width=3)
        penTx = pg.mkPen((153, 0, 153), width=1, style=Qt.DashDotLine)
        penTy = pg.mkPen((153, 0, 0), width=1, style=Qt.DashDotDotLine)
        dt = build.soil_reflection_prop_x.dt
        B1 = build.soil_reflection_prop_x.b1Curve
        N = build.soil_reflection_prop_x.nCurve
        B = build.soil_reflection_prop_x.bCurve
        x = np.arange(0, 4.5, dt)
        self.p.plot(x, B1, pen=penB1, name="B1", clear=True)
        self.p.plot(x, N, pen=penN, name="N")
        self.p.plot(x, B, pen=penB, name="B")
        self.p.addLine(x=build.Tx, pen=penTx)
        self.p.addLine(x=build.Ty, pen=penTy)
        Tx, Ty = build.Tx, build.Ty
        THtml = 'T<sub>{0}</sub> = {1:.2f}'
        TxHtml, TyHtml = THtml.format('x', Tx), THtml.format('y', Ty)
        text = pg.TextItem(html=TxHtml, anchor=(0, 1.5), border='k', fill=(0, 0, 255, 100))
        self.p.addItem(text)
        text.setPos(Tx, B.max())
        text = pg.TextItem(html=TyHtml, anchor=(0, 3), border='k', fill=(0, 0, 255, 100))
        self.p.addItem(text)
        text.setPos(Ty, B.max())
        self.p.setYRange(0, B.max() + 1, padding=0)

    def current_building(self):
        risk_level = self.accText.text()
        city = self.get_current_shahr()
        height = self.HSpinBox.value()
        importance_factor = float(self.IBox.currentText())
        soil = self.get_current_soil_type()
        noStory = self.storySpinBox.value()
        x_system = self.xactivate()
        y_system = self.yactivate()
        if not x_system and y_system:
            return None
        xSystemType, xLateralType = x_system[0], x_system[1]
        ySystemType, yLateralType = y_system[0], y_system[1]
        xSystem = StructureSystem(xSystemType, xLateralType, "X")
        ySystem = StructureSystem(ySystemType, yLateralType, "Y")
        self.setInfillCheckBoxStatus(xSystem, ySystem)
        Tan = self.getTAnalatical()
        useTan = Tan[0]
        xTan = Tan[1]
        yTan = Tan[2]
        is_infill = self.infillCheckBox.isChecked()
        build = Building(risk_level, importance_factor, soil, noStory, height, is_infill,
                         xSystem, ySystem, city, xTan, yTan, useTan)
        return build

    def calculate(self):
        self.dirty = False
        self.final_building = self.current_building()
        if not self.final_building:
            return
        self.setSoilProperties(self.final_building)
        self.structure_model.beginResetModel()
        self.structure_model.build = self.final_building
        self.structure_model.endResetModel()
        self.resizeColumns()
        results = self.final_building.results
        if results[0] is True:
            Cx, Cy = results[1], results[2]
            resultStrx = '<font size=6 color=blue>C<sub>x</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cx, self.final_building.kx)
            resultStrx_drift = '<font size=6 color=blue>C<sub>xdrift</sub> = %.4f , K<sub>xdrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[1], self.final_building.kx_drift)
            resultStry = '<font size=6 color=blue>C<sub>y</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cy, self.final_building.ky)
            resultStry_drift = '<font size=6 color=blue>C<sub>ydrift</sub> = %.4f , K<sub>ydrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[2], self.final_building.ky_drift)
            self.updateBCurve(self.final_building)
            self.dirty = True
            self.action_to_etabs.setEnabled(True)
            self.action_word.setEnabled(True)
            self.action_save.setEnabled(True)

        else:
            self.action_to_etabs.setEnabled(False)
            self.action_word.setEnabled(False)
            self.action_save.setEnabled(False)
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, str(err))
            return

    def export_to_word(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.final_building)
        export_result.to_word()

    def export_to_etabs(self):
        allow, check = self.allowed_to_continue(
            'export_to_etabs.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        ret = etabs.apply_cfactor_to_edb(self.final_building)
        if ret == 1:
            msg = "Data can not be written to your Etabs file,\n If you want to correct this problem, try Run analysis."
            title = "Remove Error?"
            QMessageBox.information(None, title, msg)
            return
        msg = "Successfully written to Etabs."
        QMessageBox.information(None, "done", msg)
        self.show_warning_about_number_of_use(check)

    def show_torsion_table(self):
        allow, check = self.allowed_to_continue(
            'torsion.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/d1591790a52a62b3e66bb70f45738105/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        df = etabs.get_diaphragm_max_over_avg_drifts(only_ecc=True)
        data, headers = df.values, list(df.columns)
        table_model.show_results(data, headers, table_model.TorsionModel, etabs.view.show_point)
        self.show_warning_about_number_of_use(check)
    
    def show_aj_table(self):
        allow, check = self.allowed_to_continue(
            'torsion.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/d1591790a52a62b3e66bb70f45738105/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        df = etabs.get_magnification_coeff_aj()
        data, headers = df.values, list(df.columns)
        table_model.show_results(data, headers, table_model.AjModel)
        self.show_warning_about_number_of_use(check)
    
    def get_weakness_ratio(self):
        allow, check = self.allowed_to_continue(
            'weakness.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/3c8c1d0229dc76ec23982af1173aa46a/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import weakness
        weakness_win = weakness.WeaknessForm(etabs, table_model)
        if weakness_win.exec_():
            self.show_warning_about_number_of_use(check)
    
    def show_weakness_ratio(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import show_weakness
        weakness_win = show_weakness.WeaknessForm(etabs, table_model)
        weakness_win.exec_()
    
    def get_story_stiffness_table(self):
        allow, check = self.allowed_to_continue(
            'stiffness.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/e5635c17392c73540a46761a7247836e/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import get_siffness_story_way as stiff
        stiffness_win = stiff.ChooseStiffnessForm(self)
        if stiffness_win.exec_():
            if stiffness_win.radio_button_2800.isChecked():
                way = '2800'
            if stiffness_win.radio_button_modal.isChecked():
                way = 'modal'
            if stiffness_win.radio_button_earthquake.isChecked():
                way = 'earthquake'
        ret = etabs.get_story_stiffness_table(way)
        if not ret:
            err = "Please Activate Calculate Diaphragm Center of Rigidity in ETABS!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        data, headers = ret
        table_model.show_results(data, headers, table_model.StoryStiffnessModel)
        self.show_warning_about_number_of_use(check)
    
    def show_story_stiffness_table(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import show_siffness_story_way as stiff
        stiffness_win = stiff.ChooseStiffnessForm(self)
        e_name = etabs.get_file_name_without_suffix()
        way_radio_button = {'2800': stiffness_win.radio_button_2800,
                            'modal': stiffness_win.radio_button_modal,
                            'earthquake': stiffness_win.radio_button_earthquake}
        for w, rb in way_radio_button.items():
            name = f'{e_name}_story_stiffness_{w}_table.json'
            json_file = Path(etabs.SapModel.GetModelFilepath()) / name
            if not json_file.exists():
                rb.setChecked(False)
                rb.setEnabled(False)
        if stiffness_win.exec_():
            if stiffness_win.radio_button_2800.isChecked():
                way = '2800'
            elif stiffness_win.radio_button_modal.isChecked():
                way = 'modal'
            elif stiffness_win.radio_button_earthquake.isChecked():
                way = 'earthquake'
            elif stiffness_win.radio_button_file.isChecked():
                way = 'file'
        if way != 'file':
            name = f'{e_name}_story_stiffness_{way}_table.json'
            json_file = Path(etabs.SapModel.GetModelFilepath()) / name
        else:
            json_file = stiffness_win.json_line_edit.text()
        ret = etabs.load_from_json(json_file)
        if not ret:
            err = "Can not find the results!"
            QMessageBox.critical(self, "Error", str(err))
            return None
        data, headers = ret
        table_model.show_results(data, headers, table_model.StoryStiffnessModel)

    def get_irregularity_of_mass(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        data, headers = etabs.get_irregularity_of_mass()
        table_model.show_results(data, headers, table_model.IrregularityOfMassModel)

    def show_story_forces(self):
        allow, check = self.allowed_to_continue(
            'torsion.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/d1591790a52a62b3e66bb70f45738105/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        data, headers = etabs.get_story_forces_with_percentages()
        table_model.show_results(data, headers, table_model.StoryForcesModel)
        self.show_warning_about_number_of_use(check)

    def get_drift_automatically(self):
        allow, check = self.allowed_to_continue(
            'show_drifts.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        stories = etabs.SapModel.Story.GetStories()[1]
        from py_widget import drift
        drift_win = drift.StoryForm(etabs, stories)
        if drift_win.exec_():
            no_of_stories = drift_win.no_story_x_spinbox.value()
            height = drift_win.height_x_spinbox.value()
            create_t_file = drift_win.create_t_file_box.isChecked()
            loadcases = []
            for lw in (drift_win.x_loadcase_list, drift_win.y_loadcase_list):
                for i in range(lw.count()):
                    item = lw.item(i)
                    if item.checkState() == Qt.Checked:
                        loadcases.append(item.text())
            self.storySpinBox.setValue(no_of_stories)
            self.HSpinBox.setValue(height)
            if create_t_file:
                drifts, headers = etabs.calculate_drifts(self, no_of_stories, loadcases=loadcases)
            else:
                cdx = self.final_building.x_system.cd
                cdy = self.final_building.y_system.cd
                drifts, headers = etabs.get_drifts(no_of_stories, cdx, cdy, loadcases)
            table_model.show_results(drifts, headers, table_model.DriftModel)
            self.show_warning_about_number_of_use(check)
        else:
            return
    
    def aj(self):
        allow, self.check = self.allowed_to_continue(
            'export_to_etabs.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import aj_correction
        aj_win = aj_correction.AjForm(etabs, parent=self)
        aj_win.exec_()
            # num_err, ret = functions.apply_aj_df(SapModel, aj_win.aj_apply_model.df)
            # print(num_err, ret)
            # msg = "Successfully written to Etabs."
            # QMessageBox.information(None, "done", msg)
            # self.show_warning_about_number_of_use(check)
        # else:
        #     return

    def correct_torsion_stiffness_factor(self):
        allow, check = self.allowed_to_continue(
            'correct_j.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/98b4863d25f0779dce2347d73a99212b/raw',
            'cfactor',
            )
        if not allow:
            return
        from etabs_api import etabs_obj, table_model
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import beam_j
        j_win = beam_j.BeamJForm(etabs, table_model)
        if j_win.exec_():
            self.show_warning_about_number_of_use(check)

    def scale_response_spectrums(self):
        allow, check = self.allowed_to_continue(
            'response_spectrum.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/2370d564be6b4ba2508f8314a3358970/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import response_spectrum as rs
        rs_win = rs.ResponseSpectrumForm(etabs)
        rs_win.exec_()
        self.show_warning_about_number_of_use(check)
    
    def wall_load_on_frames(self):
        allow, check = self.allowed_to_continue(
            'wall_load.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/ff63d2d84e77947103e9ca2db6a03f68/raw',
            'cfactor',
            n=2,
            )
        if not allow:
            return
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget.assign import wall_load_on_frames as wl
        win = wl.WallLoadForm(etabs)
        win.exec_()
        self.show_warning_about_number_of_use(check)

    def offset_beam(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import offset
        offset_win = offset.OffsetForm(etabs)
        offset_win.exec_()
    
    def connect_beam(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget import connect
        connect_win = connect.ConnectForm(etabs)
        connect_win.exec_()
    
    def create_section_cuts(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel()
        if not self.is_etabs_running(etabs):
            return
        from py_widget.define import create_section_cuts
        win = create_section_cuts.SectionCutForm(etabs)
        win.exec_()

    def create_period_file(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not self.is_etabs_running(etabs):
            return
        tx, ty, _ = etabs.get_drift_periods()
        self.xTAnalaticalSpinBox.setValue(tx)
        self.yTAnalaticalSpinBox.setValue(ty)
        self.calculate()
    
    def assign_frame_sections(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not self.is_etabs_running(etabs):
            return
        from py_widget.assign import assign_frame_sections
        win = assign_frame_sections.Dialog(etabs)
        win.exec_()
        

    def clear_backups(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not self.is_etabs_running(etabs):
            return
        from py_widget import delete_backups as db
        db_win = db.ListForm(etabs)
        db_win.exec_()
    
    def restore_backup(self):
        sys.path.insert(0, str(civiltools_path))
        from etabs_api import etabs_obj
        etabs = etabs_obj.EtabsModel(backup=False)
        if not self.is_etabs_running(etabs):
            return
        from py_widget import restore_backup as rb
        db_win = rb.ListForm(etabs)
        db_win.exec_()

    def allowed_to_continue(self,
                            filename,
                            gist_url,
                            dir_name,
                            n=5,
                            ):
        sys.path.insert(0, str(civiltools_path))
        from functions import check_legal
        check = check_legal.CheckLegal(
                                    filename,
                                    gist_url,
                                    dir_name,
                                    n,
        )
        allow, text = check.allowed_to_continue()
        if allow and not text:
            return True, check
        else:
            if text in ('INTERNET', 'SERIAL'):
                serial_win = SerialForm(self)
                serial_win.serial.setText(check.serial)
                serial_win.exec_()
                return False, check
            elif text == 'REGISTERED':
                msg = "Congrajulation! You are now registered, enjoy using this features!"
                QMessageBox.information(None, 'Registered', str(msg))
                return True, check
        return False, check

    def show_warning_about_number_of_use(self, check):
        if check.is_civiltools_registered:
            return
        elif check.is_registered:
            check.add_using_feature()
            _, no_of_use = check.get_registered_numbers()
            n = check.n - no_of_use
            msg = ''
            if n == 0:
                msg = f"You can't use this feature any more times!\n please register the software."
            elif n > 0:
                msg = f"You can use this feature {n} more times!\n then you must register the software."
            if msg:
                QMessageBox.warning(None, 'Not registered!', str(msg))
            return

    def save(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, None)
        export_result.to_json()

    def load(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'load project',
                                                  self.lastDirectory, "json(*.json)")
        if filename == '':
            return
        config.load(self, filename)
        self.calculate()

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

    def is_etabs_running(self, etabs=None):
        if etabs is None:
            sys.path.insert(0, str(civiltools_path))
            from etabs_api import etabs_obj
            etabs = etabs_obj.EtabsModel()
        success = etabs.success
        if not success:
            QMessageBox.warning(self, 'ETABS', 'Please open etabs file!')
            return False
        return True

class SerialForm(serial_base, serial_window):
    def __init__(self, parent=None):
        super(SerialForm, self).__init__()
        self.setupUi(self)


def main():
    app = QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
    pg.exit()


if __name__ == '__main__':
    main()
