# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
# from . import qrc_resources
from .db import ostanha
from .building.build import *
from .models import *
import pyqtgraph as pg
from .plots.plotB import PlotB as pl
#from guiSaveRestore import *
from . import export
from .exporter import exporttoetabsdlg1 as etabs
from .exporter import config

rTable = RFactorTable()
systemTypes = rTable.getSystemTypes()

__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "4.5"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)

main_window = uic.loadUiType('applications/cfactor/widgets/mainwindow.ui')[0]


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
        #self.setMaxAllowedHeight()
        self.create_connections()
        # self.create_actions()
        try:
            self.load_settings()
        except:
            pass

        self.load_config()
        self.calculate()

    def load_config(self, json_file='applications/cfactor/exporter/config.json'):
        config.load(self, json_file)


    def create_connections(self):
        self.calculate_button.clicked.connect(self.calculate)
        self.x_treeWidget.itemActivated.connect(self.xactivate)
        # self.y_treeWidget.itemActivated.connect(self.yactivate)
        ##self.connect(self.HSpinBox, SIGNAL(
                    ##"editingFinished()"), self.userInputHeight)
        self.ostanBox.currentIndexChanged.connect(self.set_shahrs_of_current_ostan)
        self.shahrBox.currentIndexChanged.connect(self.setA)
        self.pushButton_etabs.clicked.connect(self.export_to_etabs)
        self.pushButton_word.clicked.connect(self.export_to_word)
        self.save_button.clicked.connect(self.save)
        self.load_button.clicked.connect(self.load)

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
            i +=1
        iterator = QTreeWidgetItemIterator(self.y_treeWidget)
        i = 0
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if i == 2:
                self.y_treeWidget.setCurrentItem(item, 0)
                break
            i +=1
    
    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("CfactorMainWindow\Geometry"))
        self.restoreState(settings.value("CfactorMainWindow\State"))
        # self.splitter.restoreState(settings.value("CfactorMainWindow\Splitter"))
        # self.splitter_2.restoreState(settings.value("CfactorMainWindow\Splitter2"))

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("CfactorMainWindow\Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("CfactorMainWindow\State",
                          QVariant(self.saveState()))
        # settings.setValue("CfactorMainWindow\Splitter",
        #         QVariant(self.splitter.saveState()))
        # settings.setValue("CfactorMainWindow\Splitter2",
        #         QVariant(self.splitter_2.saveState()))
        if self.ok_to_continue():
            self.save_config()

    def save_config(self, json_file='applications/cfactor/exporter/config.json'):
        config.save(self, json_file)

    def ok_to_continue(self):
        return bool(QMessageBox.question(self, 'save config?', 'save configuration file?', 
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes)


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
        # if self.tAnalaticalGroupBox.isChecked() or infill is None:
        if infill is None:
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
        x_system = self.xactivate()
        y_system = self.yactivate()
        if not x_system and y_system:
            return None
        xSystemType, xLateralType = x_system[0], x_system[1]
        ySystemType, yLateralType = y_system[0], y_system[1]
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

        else:
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, err)
            return

    def export_to_word(self):
        export_result = export.Export(self, self.dirty, self.lastDirectory, self.final_building)
        export_result.to_word()

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

    def export_to_etabs(self):
        # TODO 
        # results = self.final_building.results
        # if results[0] is True:
        self.child_export_etabs_win = etabs.ExportToEtabs(self.final_building, self)
        # self.child_export_etabs_win.number_of_story_spinox.setValue(self.storySpinBox.value())
        if self.child_export_etabs_win.exec_():
            title = 'Seccess'
            text = 'Export File to {}'.format(self.child_export_etabs_win.output_path_line.text())
            QMessageBox.information(self, title, text)
        else:
            return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
