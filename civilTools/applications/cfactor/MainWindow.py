# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from . import qrc_resources
from .db import ostanha
from .building.build import *
from .models import *
import pyqtgraph as pg
from .plots.plotB import PlotB as pl
#from guiSaveRestore import *
from . import export


rTable = RFactorTable()
systemTypes = rTable.getSystemTypes()

__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "4.5"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)


class Ui(QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('applications/cfactor/mainwindow.ui', self)
        self.dirty = False
        self.lastDirectory = ''
        self.html = ''
        self.printer = None
        self.create_widgets()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.structure_properties_table.setModel(self.structure_model)
        #self.__userH = 200
        #self.setMaxAllowedHeight()
        self.create_connections()
        self.accept()
        # self.create_actions()
        # settings = QSettings()
        #self.load_settings()
        #guirestore(self, settings)
        #self.updateFileMenu()

    def create_connections(self):
        self.soilType.currentIndexChanged.connect(self.accept)
        self.HSpinBox.valueChanged.connect(self.accept)
        ##self.connect(self.HSpinBox, SIGNAL(
                    ##"editingFinished()"), self.userInputHeight)
        self.xTAnalaticalSpinBox.valueChanged.connect(self.accept)
        self.yTAnalaticalSpinBox.valueChanged.connect(self.accept)
        self.infillCheckBox.stateChanged.connect(self.accept)
        self.tAnalaticalGroupBox.clicked.connect(self.accept)
        self.xSystemBox.currentIndexChanged.connect(self.insert_xlaterals)
        self.ySystemBox.currentIndexChanged.connect(self.insert_ylaterals)
        self.xLateralBox.currentIndexChanged.connect(self.accept)
        self.yLateralBox.currentIndexChanged.connect(self.accept)
        self.storySpinBox.valueChanged.connect(self.accept)
        self.IBox.currentIndexChanged.connect(self.accept)
        self.tabWidget.currentChanged.connect(self.showResult)
        self.ostanBox.currentIndexChanged.connect(self.set_shahrs_of_current_ostan)
        self.shahrBox.currentIndexChanged.connect(self.setA)
        self.shahrBox.currentIndexChanged.connect(self.accept)

    def resizeColumns(self):
        for column in (X, Y):
            self.structure_properties_table.resizeColumnToContents(column)

    def create_widgets(self):
        ostans = ostanha.ostans.keys()
        self.ostanBox.addItems(ostans)
        self.set_shahrs_of_current_ostan()
        self.setA()

        for noesystem in systemTypes:
            self.xSystemBox.addItem(noesystem)
            self.ySystemBox.addItem(noesystem)
        self.tAnalaticalGroupBox.setChecked(True)
        #
        # curve widget
        self.curveBWidget = pl()
        self.curveBWidget.setMinimumSize(450, 300)
        draw_layout = QVBoxLayout()
        draw_layout.addWidget(self.curveBWidget)
        self.draw_frame.setLayout(draw_layout)

        for i in range(5):
            self.soilPropertiesTable.setSpan(i, 0, 1, 2)
    
        self.insert_xlaterals()
        self.insert_ylaterals()

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(
                settings.value("MainWindow/Geometry2").toByteArray())
        self.restoreState(settings.value("MainWindow/State2").toByteArray())
        self.inputSplitter.restoreState(settings.value("InputSplitter2").toByteArray())
        self.mainSplitter.restoreState(settings.value("MainSplitter2").toByteArray())

    #def closeEvent(self, event):
        #settings = QSettings()
        #guisave(self, settings)
        ##self.deleteLater()
        ##if self.okToContinue():
        ##settings = QSettings()
        ##filename = (QVariant(QString(self.filename))
                    ##if self.filename is not None else QVariant())
        ##settings.setValue("LastFile", filename)
        ##recentFiles = (QVariant(self.recentFiles)
                       ##if self.recentFiles else QVariant())
        ##settings.setValue("RecentFiles", Files)
        #settings.setValue("MainWindow/Geometry2", QVariant(self.saveGeometry()))
        #settings.setValue("MainWindow/State2", QVariant(self.saveState()))
        #settings.setValue("InputSplitter2", QVariant(self.inputSplitter.saveState()))
        #settings.setValue("MainSplitter2", QVariant(self.mainSplitter.saveState()))

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

    def insert_xlaterals(self):
        systemType = self.xSystemBox.currentText()
        lateralTypes = rTable.getLateralTypes(systemType)
        old_state = bool(self.xLateralBox.blockSignals(True))
        print(old_state)
        self.xLateralBox.clear()
        self.xLateralBox.addItems(lateralTypes)
        self.xLateralBox.blockSignals(old_state)

    def insert_ylaterals(self):
        systemType = self.ySystemBox.currentText()
        lateralTypes = rTable.getLateralTypes(systemType)
        old_state = bool(self.yLateralBox.blockSignals(True))
        self.yLateralBox.clear()
        self.yLateralBox.addItems(lateralTypes)
        self.yLateralBox.blockSignals(old_state)

    def get_current_system_type(self, systemBox):
        return systemBox.currentText()

    def get_lateral_system_type(self, lateralBox):
        return lateralBox.currentText()

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
        #shahrs.sort()
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

    #def setDEngheta(self):
        #dEngheta = self.getDEngheta()
        #if dEngheta:
            #self.dEnghetaLineEdit.setText("%.1f Cm" % dEngheta)
        #else:
            #self.dEnghetaLineEdit.setText("مراجعه به بند ۳-۵-۶")

    def setInfillCheckBoxStatus(self, xSystem, ySystem):
        infill = xSystem.is_infill and ySystem.is_infill
        if self.tAnalaticalGroupBox.isChecked() or infill is None:
            self.infillCheckBox.setEnabled(False)
            self.infillCheckBox.setCheckState(False)
        else:
            self.infillCheckBox.setEnabled(True)

    def userInputHeight(self):
        self.__userH = self.HSpinBox.value()

    def setMaxHeightAllowed(self, xSystem, ySystem):
        xMaxAllowedHeight = xSystem.maxHeight
        yMaxAllowedHeight = ySystem.maxHeight
        if (xMaxAllowedHeight and yMaxAllowedHeight) is None:
            maxAllowedHeight = 200
        elif xMaxAllowedHeight is None:
            maxAllowedHeight = yMaxAllowedHeight
        elif yMaxAllowedHeight is None:
            maxAllowedHeight = xMaxAllowedHeight
        else:
            maxAllowedHeight = min(xMaxAllowedHeight, yMaxAllowedHeight)
        self.HSpinBox.setMaximum(maxAllowedHeight)

    def getTAnalatical(self):
        useTan = self.tAnalaticalGroupBox.isChecked()
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
        self.p = self.curveBWidget.p
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
        self.p.legend.items = []
        self.p.plot(x, B1, pen=penB1, name="B1", clear=True)
        self.p.plot(x, N, pen=penN, name="N")
        self.p.plot(x, B, pen=penB, name="B")
        self.p.addLine(x=build.Tx, pen=penTx)
        self.p.addLine(x=build.Ty, pen=penTy)
        Tx, Ty = build.Tx, build.Ty
        #THtml = '<div style="text-align: center"><span style="color: #FFF;">T<sub>{0}</sub> = '
        #THtml += '{1:.2f} </span><br><span style="color: #FF0; font-size: 16pt;"></span></div>'
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
        xSystemType = self.get_current_system_type(self.xSystemBox)
        xLateralType = self.get_lateral_system_type(self.xLateralBox)
        ySystemType = self.get_current_system_type(self.ySystemBox)
        yLateralType = self.get_lateral_system_type(self.yLateralBox)
        xSystem = StructureSystem(xSystemType, xLateralType, "X")
        ySystem = StructureSystem(ySystemType, yLateralType, "Y")
        self.setInfillCheckBoxStatus(xSystem, ySystem)
        self.setMaxHeightAllowed(xSystem, ySystem)
        #if self.__userH < self.HSpinBox.maximum() and self.__userH > height:
            #self.HSpinBox.setValue(self.__userH)
        #height = self.getH()
        Tan = self.getTAnalatical()
        useTan = Tan[0]
        xTan = Tan[1]
        yTan = Tan[2]
        is_infill = self.infillCheckBox.isChecked()
        build = Building(risk_level, importance_factor, soil, noStory, height, is_infill,
                              xSystem, ySystem, city, xTan, yTan, useTan)
        return build

    def accept(self):
        self.dirty = False
        self.html = ''
        self.final_building = self.current_building()
        self.setSoilProperties(self.final_building)
        self.structure_model.beginResetModel()
        self.structure_model.build = self.final_building
        self.structure_model.endResetModel()
        # self.resizeColumns()
        results = self.final_building.results
        print(results)
        if results[0] is True:
            Cx, Cy = results[1], results[2]
            resultStrx = '<font size=6 color=blue>C<sub>x</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cx, self.final_building.kx)
            resultStrx_drift = '<font size=6 color=blue>C<sub>xdrift</sub> = %.4f , K<sub>xdrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[1], self.final_building.kx_drift)
            resultStry = '<font size=6 color=blue>C<sub>y</sub> = %.4f , K<sub>x</sub> = %.2f</font>' % (Cy, self.final_building.ky)
            resultStry_drift = '<font size=6 color=blue>C<sub>ydrift</sub> = %.4f , K<sub>ydrift</sub> = %.2f</font>' % (
                self.final_building.results_drift[2], self.final_building.ky_drift)
            self.updateBCurve(self.final_building)
            self.html = self.final_building.__str__()
            self.dirty = True

        else:
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, err)
            return

    def showResult(self):
        self.textExport.setHtml(self.html)

    def exportToPdf(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.html)
        export_result.to_pdf()

    def exportToOffice(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.html)
        export_result.to_word()

    def exportToHtml(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.html)
        export_result.to_html()

    def exportBCurveToImage(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_image()

    def exportBCurveToCsv(self):
        export_graph = export.ExportGraph(self, self.lastDirectory, self.p)
        export_graph.to_csv()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
