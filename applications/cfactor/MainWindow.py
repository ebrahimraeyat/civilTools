# -*- coding: utf-8 -*-
from os.path import dirname
import sys
import os
from pathlib import Path
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
        #self.__userH = 200
        # self.setMaxAllowedHeight()
        self.create_connections()
        self.add_actions()
        # self.create_actions()
        self.load_settings()
        self.load_config()
        self.calculate()
        self.setWindowTitle(f"CFactor v{__version__}")

    def add_actions(self):
        self.toolbar.addAction(self.action_to_etabs)
        self.toolbar.addAction(self.action_show_drift)
        self.toolbar.addAction(self.action_automatic_drift)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_open)
        self.toolbar.addAction(self.action_save)
        self.toolbar.addAction(self.action_save_spectrals)
        self.toolbar.addAction(self.action_word)

        self.action_to_etabs.triggered.connect(self.export_to_etabs)
        self.action_show_drift.triggered.connect(self.show_drifts)
        self.action_open.triggered.connect(self.load)
        self.action_save.triggered.connect(self.save)
        self.action_save_spectrals.triggered.connect(self.exportBCurveToCsv)
        self.action_word.triggered.connect(self.export_to_word)

    def create_connections(self):
        self.calculate_button.clicked.connect(self.calculate)
        self.x_treeWidget.itemActivated.connect(self.xactivate)
        # self.y_treeWidget.itemActivated.connect(self.yactivate)
        # self.connect(self.HSpinBox, SIGNAL(
        # "editingFinished()"), self.userInputHeight)
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
        # self.tAnalaticalGroupBox.setChecked(True)
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
        # self.x_treeWidget.setCurrentItem(0,0)
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
        # qsettings.setValue( "maximized", self.isMaximized() )
        # if not self.isMaximized() == True :
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
            # self.y_treeWidget.setCurrentItem(self.y_treeWidget.topLevelItem(0), 0)
            self.y_treeWidget.scrollToItem(self.x_treeWidget.currentItem())
            # print(self.y_treeWidget.indexFromItem(self.x_treeWidget.currentItem()))
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

    # def setDEngheta(self):
        #dEngheta = self.getDEngheta()
        # if dEngheta:
        #self.dEnghetaLineEdit.setText("%.1f Cm" % dEngheta)
        # else:
        #self.dEnghetaLineEdit.setText("مراجعه به بند ۳-۵-۶")

    def setInfillCheckBoxStatus(self, xSystem, ySystem):
        infill = xSystem.is_infill and ySystem.is_infill
        # if self.tAnalaticalGroupBox.isChecked() or infill is None:
        if infill is None:
            self.infillCheckBox.setEnabled(False)
            self.infillCheckBox.setCheckState(False)
        else:
            self.infillCheckBox.setEnabled(True)

    # def userInputHeight(self):
    #     self.__userH = self.HSpinBox.value()

    # def setMaxHeightAllowed(self, xSystem, ySystem):
    #     xMaxAllowedHeight = xSystem.maxHeight
    #     yMaxAllowedHeight = ySystem.maxHeight
    #     if (xMaxAllowedHeight and yMaxAllowedHeight) is None:
    #         maxAllowedHeight = 200
    #     elif xMaxAllowedHeight is None:
    #         maxAllowedHeight = yMaxAllowedHeight
    #     elif yMaxAllowedHeight is None:
    #         maxAllowedHeight = xMaxAllowedHeight
    #     else:
    #         maxAllowedHeight = min(xMaxAllowedHeight, yMaxAllowedHeight)
    #     self.HSpinBox.setMaximum(maxAllowedHeight)

    def getTAnalatical(self):
        useTan = True
        # useTan = self.tAnalaticalGroupBox.isChecked()
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
        # THtml = '<div style="text-align: center"><span style="color: #FFF;">T<sub>{0}</sub> = '
        # THtml += '{1:.2f} </span><br><span style="color: #FF0; font-size: 16pt;"></span></div>'
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
        # self.setMaxHeightAllowed(xSystem, ySystem)
        # if self.__userH < self.HSpinBox.maximum() and self.__userH > height:
        # self.HSpinBox.setValue(self.__userH)
        #height = self.getH()
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
        if not self.is_etabs_running():
            return
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.final_building)
        ret = export_result.to_etabs()
        if ret == 1:
            msg = "Data can not be written to your Etabs file,\n If you want to correct this problem, try Run analysis."
            title = "Remove Error?"
            QMessageBox.information(None, title, msg)
            return
        msg = "Successfully writed to Etabs."
        QMessageBox.information(None, "done", msg)
        self.show_warning_about_number_of_use(check)

    def show_drifts(self):
        allow, check = self.allowed_to_continue(
            'show_drifts.bin',
            'https://gist.githubusercontent.com/ebrahimraeyat/7f10571fab2a08b7a17ab782778e53e1/raw',
            'cfactor'
            )
        if not allow:
            return
        if not self.is_etabs_running():
            return
        from etabs_api import functions, table_model
        no_story = self.storySpinBox.value()
        cdx = self.final_building.x_system.cd
        cdy = self.final_building.y_system.cd
        data, headers = functions.get_drifts(no_story, cdx, cdy)
        if data == 'not analyzed':
            text = "Structure did not analyzed, Do you want to run analysis?"
            title = "analysis"
            ret = self.ok_to_continue(title, text)
            if ret == QMessageBox.Yes:
                import comtypes.client
                etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
                SapModel = etabs.SapModel
                SapModel.Analyze.RunAnalysis()
            return None
        elif not data:
            err = "Please select at least one load case in ETABS table"
            QMessageBox.critical(self, "Error", str(err))
            return None
        table_model.show_results(data, headers, table_model.DriftModel)
        self.show_warning_about_number_of_use(check)

    def allowed_to_continue(self,
                            filename,
                            gist_url,
                            dir_name,
                            ):
        sys.path.insert(0, str(civiltools_path))
        from functions import check_legal
        check = check_legal.CheckLegal(
                                    filename,
                                    gist_url,
                                    dir_name,
        )
        allow, text = check.allowed_to_continue()
        if allow and not text:
            return True, check
        else:
            if text in ('INTERNET', 'SERIAL'):
                # msg = "You must register to continue, but you are not connected to the Internet, please check your internet connection."
                # QMessageBox.warning(None, 'Register!', str(msg))
                # return False
            # elif text == 'SERIAL':
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
        check.add_using_feature()
        _, no_of_use = check.get_registered_numbers()
        n = check.n - no_of_use
        if n > 0:
            msg = f"You can use this feature {n} more times!\n then you must register the software."
            QMessageBox.warning(None, 'Not registered!', str(msg))

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
        # from pyqtgraph.GraphicsScene import exportDialog
        # exportDialog = exportDialog.ExportDialog(self.p.scene())
        # exportDialog.show(self.p)

    # def export_to_etabs(self):
        # TODO
        # results = self.final_building.results
        # if results[0] is True:
        # self.child_export_etabs_win = etabs.ExportToEtabs(self.final_building, self)
        # if self.child_export_etabs_win.exec_():
        #     title = 'Seccess'
        #     text = 'Export File to {}'.format(self.child_export_etabs_win.output_path_line.text())
        #     QMessageBox.information(self, title, text)
        # else:
        #     return

    def is_etabs_running(self):
        from etabs_api import functions
        etabs = functions.is_etabs_running()
        if not etabs:
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
