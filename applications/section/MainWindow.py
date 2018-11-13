# -*- coding: utf-8 -*-

import re
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from . import sec
from .plot.plotIpe import PlotSectionAndEqSection


__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "0.8"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)

ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()
cpesProp = sec.Cpe.createStandardCpes()

main_window = uic.loadUiType('applications/section/mainwindow.ui')[0]


class Ui(QMainWindow, main_window):

    sectionProp = {'IPE': ipesProp, 'UNP': unpsProp, 'CPE': cpesProp}
    useAsDict = {'تیر': 'B', 'ستون': 'C'}
    ductilityDict = {'متوسط': 'M', 'زیاد': 'H'}
    doubleList1 = ['تک', 'دوبل', 'سوبل']
    doubleList2 = [[False, False], [True, False], [False, True]]
    doubleDict = dict(zip(doubleList1, doubleList2))

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.dirty = False
        self.lastDirectory = ''
        self.last_sectionBox_index = {'IPE': 4, 'UNP': 4, 'CPE':4}
        self.currentSectionProp = None
        #self.filename = None
        self.printer = None
        self.createWidgetsOne()
        self.updateSectionShape()
        self.create_connections()
        
        
        #self.accept()
        try:
            self.load_settings()
        except:
            pass
        #QTimer.singleShot(0, self.initialLoad)

    #def initialLoad(self):
        #if  QFile.exists(self.model1.filename):
            #try:
                #self.model1.load()
                #self.model1.sortByName()
                #self.resizeColumns(self.tableView1)
            #except IOError, err:
                #QMessageBox.warning(self, "Sections - Error",
                        #"Failed to load: {0}".format(err))

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("MainWindow/State",
                          QVariant(self.saveState()))
        settings.setValue("MainSplitter",
                QVariant(self.mainSplitter.saveState()))

    def resizeColumns(self, tableView=None):
        for column in (sec.NAME, sec.AREA,
                       sec.ASY, sec.ASX, sec.IX, sec.IY, sec.ZX, sec.ZY,
                         sec.BF, sec.TF, sec.D, sec.TW, sec.Sx, sec.Sy, sec.RX, sec.RY):
            tableView.resizeColumnToContents(column)

    def reject(self):
        self.accept()

    #def accept(self):
        #if (self.model.dirty and
            #QMessageBox.question(self, "sections - Save?",
                    #"Save unsaved changes?",
                    #QMessageBox.Yes | QMessageBox.No) ==
                    #QMessageBox.Yes):
            #try:
                #self.model.save()
            #except IOError, err:
                #QMessageBox.warning(self, "sections - Error",
                        #"Failed to save: {0}".format(err))
        #QDialog.accept(self)

    def sortTable(self, section):
        if section == sec.AREA:
            self.model1.sortByArea()
        #self.model.sortByName();
        self.resizeColumns(self.tableView1)

    def addSection(self):
        row = self.model1.rowCount()
        self.model1.insertRows(row)
        index = self.model1.index(row, 1)
        self.tableView1.setCurrentIndex(index)
        self.tableView1.edit(index)

    def removeSection(self):
        index = self.tableView1.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        name = self.model1.data(
                        self.model1.index(row, sec.NAME))
        if (QMessageBox.question(self, "sections - Remove",
                ("Remove section {}?".format(name)),
                QMessageBox.Yes|QMessageBox.No) ==
                QMessageBox.No):
            return

        self.model1.removeRows(row)
        self.resizeColumns(self.tableView1)

    def create_connections(self):
        self.sectionTypeBox.currentIndexChanged.connect(self.setSectionLabels)
        self.sectionTypeBox.currentIndexChanged.connect(self.updateGui)
        self.lhSpinBox.valueChanged.connect(self.updateSectionShape)
        self.thSpinBox.valueChanged.connect(self.updateSectionShape)
        self.lwSpinBox.valueChanged.connect(self.updateSectionShape)
        self.twSpinBox.valueChanged.connect(self.updateSectionShape)
        self.lvSpinBox.valueChanged.connect(self.updateSectionShape)
        self.tvSpinBox.valueChanged.connect(self.updateSectionShape)
        self.distSpinBox.valueChanged.connect(self.updateSectionShape)
        self.addTBPLGroupBox.clicked.connect(self.updateSectionShape)
        self.addLRPLGroupBox.clicked.connect(self.updateSectionShape)
        self.addWebPLGroupBox.toggled.connect(self.updateSectionShape)
        self.sectionsBox.currentIndexChanged.connect(self.updateSectionShape)
        self.doubleBox.currentIndexChanged.connect(self.updateSectionShape)
        self.ductilityBox.currentIndexChanged.connect(self.updateSectionShape)
        self.useAsBox.currentIndexChanged.connect(self.updateSectionShape)
        self.convert_type_radio_button.toggled.connect(self.updateSectionShape)
        #self.tableView1.horizontalHeader.sectionClicked.connect(self.sortTable)

    def createWidgetsOne(self):
        self.model1 = sec.SectionTableModel("section.dat")
        self.tableView1.setLayoutDirection(Qt.LeftToRight)
        self.tableView1.setModel(self.model1)
        self.clear_all_Button.clicked.connect(self.clearSectionOne)
        self.deleteSectionButton.clicked.connect(self.removeSection)
        self.saveToXml1Button.clicked.connect(self.saveToXml1)
        self.save_to_autocad_Button.clicked.connect(self.save_to_autocad_script_format)
        self.saveToFileButton.clicked.connect(self.export_to_dat)
        self.load_from_dat_button.clicked.connect(self.load_from_dat)
        self.addSectionButton.clicked.connect(self.addSection)
        self.calculate_Button.clicked.connect(self.acceptOne)
        self.doubleBox.addItems(self.doubleList1)
        self.doubleBox.setCurrentIndex(1)
        self.sectionTypeBox.addItems(sorted(self.sectionProp.keys()))
        sectionType = self.currentSectionType()
        self.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.sectionsBox.setCurrentIndex(4)
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 3)

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("MainWindow/Geometry"))
        self.restoreState(settings.value("MainWindow/State"))
        self.mainSplitter.restoreState(settings.value("MainSplitter"))

    def setSectionLabels(self):
        sectionType = self.currentSectionType()
        #self.last_sectionBox_index[sectionType] = self.sectionsBox.currentIndex()
        old_state = bool(self.sectionsBox.blockSignals(True))
        self.sectionsBox.clear()
        self.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.sectionsBox.blockSignals(old_state)
        self.sectionsBox.setCurrentIndex(self.last_sectionBox_index[sectionType])
        #print self.last_sectionBox_index

    def updateGui(self):
        index = self.doubleBox.currentIndex()
        sectionType = self.currentSectionType()
        if sectionType == 'UNP':
            self.doubleBox.removeItem(2)
            if index == 2:
                self.doubleBox.setCurrentIndex(index - 1)
            self.addWebPLGroupBox.setChecked(False)
            self.addWebPLGroupBox.setEnabled(False)

        elif sectionType == 'IPE' or 'CPE':
            if self.doubleBox.count() < 3:
                self.doubleBox.addItem(self.doubleList1[-1])
            self.addWebPLGroupBox.setEnabled(True)

    def getSectionLabels(self, sectionType='IPE'):
        if sectionType == 'IPE':
            sections = ipesProp.values()
        elif sectionType == 'UNP':
            sections = unpsProp.values()
        elif sectionType == 'CPE':
            sections = cpesProp.values()

        sectionNames = [section.name for section in sections]
        return sorted(sectionNames)

    def currentSectionType(self):
        return str(self.sectionTypeBox.currentText())

    def currentSection(self):
        sectionIndex = self.sectionsBox.currentIndex()
        sectionType = self.currentSectionType()
        return self.sectionProp[sectionType].values()[sectionIndex]

    def ipesProp(self):
        return sec.Ipe.createStandardIpes()

    def unpsProp(self):
        return sec.Unp.createStandardUnps()

    def currentSectionOne(self):
        lh = self.lhSpinBox.value() * 10
        th = self.thSpinBox.value()
        lv = self.lvSpinBox.value() * 10
        tv = self.tvSpinBox.value()
        lw = self.lwSpinBox.value() * 10
        tw = self.twSpinBox.value()
        dist = self.distSpinBox.value()
        isTBPlate = self.addTBPLGroupBox.isChecked()
        isLRPlate = self.addLRPLGroupBox.isChecked()
        isWebPlate = self.addWebPLGroupBox.isChecked()
        useAs = self.useAsDict[self.useAsBox.currentText()]
        ductility = self.ductilityDict[self.ductilityBox.currentText()]
        isDouble = self.doubleDict[self.doubleBox.currentText()][0]
        isSouble = self.doubleDict[self.doubleBox.currentText()][1]
        sectionSize = int(re.sub("[^0-9]", "", self.sectionsBox.currentText()))
        sectionType = self.currentSectionType()
        convert_type = 'slender'
        if self.convert_type_radio_button.isChecked():
            convert_type = "shear"
        return (lh, th, lv, tv, lw, tw, dist, isTBPlate, isLRPlate, isWebPlate, useAs, ductility, isDouble,
        isSouble, sectionSize, sectionType, convert_type)

    def acceptOne(self):
        #section = self.currentSectionOne()
        #if not section.name in self.model1.names:
        self.model1.beginResetModel()
        self.model1.sections.append(self.currentSection)
        self.model1.endResetModel()
        #del section

        self.resizeColumns(self.tableView1)
        self.model1.dirty = True

    def clearSectionOne(self):
        if self.model1.sections == []:
            return
        if (QMessageBox.question(self, "sections - Remove", ("همه مقاطع حذف شوند؟"),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            return
        self.model1.beginResetModel()
        self.model1.sections = []
        self.model1.endResetModel()
        self.model1.names = set()

        self.model1.dirty = False

    def multiAccept(self):
        self.model.sections = []
        sections = self.sectionsList.selectedItems()
        dists = self.distsList.selectedItems()
        platesWidth = self.plateWidthList.selectedItems()
        platesThick = self.plateThickList.selectedItems()
        sectionsName = re.sub("[^A-Z]", "", str(sections[0].text()))
        for sectionName in sections:
            sectionSize = int(re.sub("[^0-9]", "", str(sectionName.text())))
            section = self.sectionProp[sectionsName][sectionSize]

            for dist in dists:
                dist = int(dist.text())
                section2 = sec.DoubleSection(section, dist)

                if len(platesWidth) == 0:
                    for plateThick in platesThick:
                        plateThick = int(plateThick.text())
                        if plateThick == 0:
                            self.model.sections.append(section2)
                        else:
                            sectionPL = sec.AddPlateTBThick(section2, plateThick)
                            self.model.sections.append(sectionPL)
                else:
                    for plateThick in platesThick:
                        plateThick = int(plateThick.text())
                        if plateThick == 0:
                            self.model.sections.append(section2)
                        else:
                            for plateWidth in platesWidth:
                                plateWidth = int(plateWidth.text()) * 10
                                plate = sec.Plate(plateWidth, plateThick)
                                sectionPL = sec.AddPlateTB(section2, plate)
                                self.model.sections.append(sectionPL)
        for i, section in enumerate(self.model.sections):
            self.model.sections[i] = sec.equivalentSectionI(section)
        self.model.reset()
        self.resizeColumns(self.tableView)
        self.model.dirty = True

    def updateSectionShape(self):
        self.currentSection = sec.createSection(self.currentSectionOne())
        plotWidget = PlotSectionAndEqSection(self.currentSection, len(self.model1.sections))
        self.drawLayout.addWidget(plotWidget.plot(), 0, 0)
        self.currentSection.autocadScrText = plotWidget.autocadScrText

    #def acceptSave(self):
        ##if (self.model.dirty and
        #if QMessageBox.question(self, "sections - Save?",
                    #"Save unsaved changes?",
                    #QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            #try:
                #sec.Sections.save(self.sectionsResults)
            #except IOError, err:
                #QMessageBox.warning(self, "sections - Error",
                        #"Failed to save: {0}".format(err))
        #QDialog.accept(self)

    #def load(self):
        #try:
            #self.model1.load()
        #except IOError, err:
            #QMessageBox.warning(self, "Sections - Error",
                    #"Failed to load: {0}".format(err))

    def saveToXml1(self):
        #if not self.model1.dirty:
            #QMessageBox.warning(self, 'خروجی', 'نتیجه ای جهت ارسال وجود ندارد')
            #return
        filename = self.getFilename(['xml'])
        if not filename:
            return
        if not filename.endswith('xml'):
            filename += '.xml'
        sec.Section.exportXml(filename , self.model1.sections)

    def save_to_autocad_script_format(self):
        filename = self.getFilename(['scr'])
        if not filename:
            return
        if not filename.endswith('scr'):
            filename += '.scr'
        sec.Section.export_to_autocad(filename, self.model1.sections)

    def getLastSaveDirectory(self, f):
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = ''
        for prefix in prefixes:
            filters += "{}(*.{})".format(prefix, prefix)
        filename, _ = QFileDialog.getSaveFileName(self, ' خروجی ',
                                               self.lastDirectory, filters)

        if not filename:
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

    def export_to_dat(self):

        filename = self.getFilename(['dat'])
        if not filename:
            return
        if not filename.endswith('dat'):
            filename += '.dat'

        self.model1.filename = filename
        self.model1.save()

    def load_from_dat(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'بازکردن فایل مقاطع',
                                               self.lastDirectory, "dat (*.dat)")

        if not filename:
            return
        else:
            self.model1.filename = filename
            self.model1.load()
            self.model1.sortByName()
            self.resizeColumns(self.tableView1)

    def helpAbout(self):
        QMessageBox.about(self, u"درباره نرم افزار محاسبه مشخصات مقاطع",
                u"""<b>SectionPro</b> v {0}   ۱۳۹۵/۰۵/۱۱
                <p>توسعه دهنده: ابراهیم رعیت رکن آبادی
                <p>این نرم افزار برای محاسبه مشخصات مقاطع برای استفاده در ایتبز ۲۰۱۳ و ۲۰۱۵ تهیه شده است.
                <p>از مهندسین عزیز خواهش میکنم با بررسی این برنامه ضعفها و ایرادات برنامه رو
                در وبلاگ من یادآوری کنند.
                <p>برای دریافت آخرین نسخه نرم افزار و مطالب مفید دیگر
                به وبلاگ زیر مراجعه نمایید:
                    <p> {1}""".format(__version__, link_ebrahim))


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # translator = QtCore.QTranslator()
    # translator.load("applications/section/mainwindow.qm")
    # app.installTranslator(translator)
    window = Ui()
    window.show()
    app.exec_()