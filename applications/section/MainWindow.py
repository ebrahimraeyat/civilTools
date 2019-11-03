# -*- coding: utf-8 -*-

import re
import sys
import os
import copy
import pickle
from functools import partial
abs_path = os.path.dirname(__file__)
sys.path.insert(0, abs_path)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
import sec
from plot.plotIpe import PlotSectionAndEqSection


__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "0.8"
link_ebrahim = ('Website: <a href="%s"><span style=" '
                'text-decoration: underline; color:#0000ff;">'
                '%s</span></a>') % (__url__, __url__)

ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()
upasProp = sec.Upa.createStandardUpas()
cpesProp = sec.Cpe.createStandardCpes()
boxProp = sec.Box.createStandardBox()

main_window = uic.loadUiType(os.path.join(abs_path, 'mainwindow.ui'))[0]


class Ui(QMainWindow, main_window):

    main_sections = ['IPE', 'CPE', 'UNP', 'UPA', 'BOX']

    sectionProp = {
        'IPE': ipesProp,
        'UNP': unpsProp,
        'CPE': cpesProp,
        'BOX': boxProp,
        'UPA': upasProp,
    }
    double_box = {
        'IPE': ['single', 'double', 'souble'],
        'CPE': ['single', 'double', 'souble'],
        'UNP': ['single', 'double'],
        'UPA': ['single', 'double'],
        'BOX': ['single'],
    }
    useAsDict = {'Beam': 'B', 'Column': 'C', 'Brace': 'C'}
    ductilityDict = {'Medium': 'M', 'High': 'H'}
    doubleList1 = ['single', 'double', 'souble']
    doubleList2 = [[False, False], [True, False], [False, True]]
    doubleDict = dict(zip(doubleList1, doubleList2))
    DOWN = 1
    UP = -1

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.dirty = False
        self.lastDirectory = ''
        self.last_sectionBox_index = {
            'IPE': 4,
            'UNP': 4,
            'CPE': 4,
            'BOX': 0,
            'UPA': 4,
        }

        self.currentSectionProp = None
        # self.filename = None
        self.printer = None
        self.createWidgetsOne()
        self.updateSectionShape()
        self.create_connections()
        self.load_settings()

    def closeEvent(self, event):
        qsettings = QSettings("civiltools", "section")
        qsettings.setValue("geometry", self.saveGeometry())
        qsettings.setValue("saveState", self.saveState())
        # qsettings.setValue( "maximized", self.isMaximized() )
        qsettings.setValue("MainSplitter", self.mainSplitter.saveState())
        qsettings.setValue("splitter", self.splitter.saveState())
        # if not self.isMaximized() == True :
        qsettings.setValue("pos", self.pos())
        qsettings.setValue("size", self.size())
        self.accept()
        event.accept()

    def load_settings(self):
        qsettings = QSettings("civiltools", "section")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.restoreState(qsettings.value("saveState", self.saveState()))
        self.move(qsettings.value("pos", self.pos()))
        self.resize(qsettings.value("size", self.size()))
        self.mainSplitter.restoreState(qsettings.value("MainSplitter", self.mainSplitter.saveState()))
        self.splitter.restoreState(qsettings.value("splitter", self.splitter.saveState()))

    def resizeColumns(self, tableView=None):
        for column in (sec.NAME, sec.AREA,
                       sec.ASY, sec.ASX, sec.IX, sec.IY, sec.ZX, sec.ZY,
                       sec.BF, sec.TF, sec.D, sec.TW, sec.Sx, sec.Sy, sec.RX, sec.RY):
            tableView.resizeColumnToContents(column)

    def reject(self):
        self.accept()

    def accept(self):
        if (self.model1.dirty and
            QMessageBox.question(self, "sections - Save?",
                                 "Save unsaved changes?",
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.Yes):
            try:
                self.export_to_dat()
            except(IOError, err):
                QMessageBox.warning(self, "sections - Error", f"Failed to save: {err}")

    def sortTable(self, section):
        if section == sec.AREA:
            self.model1.sortByArea()
        elif section == sec.NAME:
            self.model1.sortByName()
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
        self.addTBPL.stateChanged.connect(self.updateSectionShape)
        self.addLRPL.stateChanged.connect(self.updateSectionShape)
        self.addWebPL.stateChanged.connect(self.updateSectionShape)
        self.sectionsBox.currentIndexChanged.connect(self.updateSectionShape)
        self.doubleBox.currentIndexChanged.connect(self.updateSectionShape)
        self.ductilityBox.currentIndexChanged.connect(self.updateSectionShape)
        self.useAsBox.currentIndexChanged.connect(self.updateSectionShape)
        self.equivalent_type_box.currentIndexChanged.connect(self.updateSectionShape)
        self.shear_button.clicked.connect(self.convert_all_section_to_shear)
        self.tableView1.horizontalHeader().sectionClicked.connect(self.sortTable)
        # self.up_button.clicked.connect(partial(self.move_current_rows, self.UP))
        # self.down_button.clicked.connect(partial(self.move_current_rows, self.DOWN))
        # self.connect(self.tableView1.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sortTable)

    def createWidgetsOne(self):
        self.model1 = sec.SectionTableModel("section.dat")
        self.tableView1.setLayoutDirection(Qt.LeftToRight)
        self.tableView1.setModel(self.model1)
        self.clear_all_Button.clicked.connect(self.clearSectionOne)
        self.deleteSectionButton.clicked.connect(self.removeSection)
        self.saveToXml1Button.clicked.connect(self.saveToXml1)
        self.excel_button.clicked.connect(self.save_to_excel)
        self.save_to_autocad_Button.clicked.connect(self.save_to_autocad_script_format)
        self.saveToFileButton.clicked.connect(self.export_to_dat)
        self.load_from_dat_button.clicked.connect(self.load_from_dat)
        self.calculate_Button.clicked.connect(self.acceptOne)
        sectionType = self.currentSectionType()
        self.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.sectionsBox.setCurrentIndex(4)
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.tableView1.verticalHeader().setSectionsMovable(True)
        self.tableView1.verticalHeader().setDragEnabled(True)
        self.tableView1.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)

    def setSectionLabels(self):
        sectionType = self.currentSectionType()
        # self.last_sectionBox_index[sectionType] = self.sectionsBox.currentIndex()
        old_state = bool(self.sectionsBox.blockSignals(True))
        self.sectionsBox.clear()
        self.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.sectionsBox.blockSignals(old_state)
        self.sectionsBox.setCurrentIndex(self.last_sectionBox_index[sectionType])
        # print self.last_sectionBox_index

    def updateGui(self):
        sectionType = self.currentSectionType()
        index = self.doubleBox.currentIndex()
        items = self.double_box[sectionType]
        self.doubleBox.blockSignals(True)
        for i, item in enumerate(self.doubleList1):
            if not item in items:
                self.doubleBox.model().item(i).setEnabled(False)
            else:
                self.doubleBox.model().item(i).setEnabled(True)
        self.doubleBox.blockSignals(False)
        if len(items) >= index + 1:
            self.doubleBox.setCurrentIndex(index)
        else:
            self.doubleBox.setCurrentIndex(0)

        if sectionType in ('UNP', 'BOX', 'UPA'):
            self.addWebPL.setChecked(False)
            self.frame_web.setEnabled(False)
            if sectionType == 'BOX':
                self.addLRPL.setChecked(True)
                self.addTBPL.setChecked(True)
                self.updateSectionShape()

        elif sectionType in ('IPE', 'CPE'):
            self.frame_web.setEnabled(True)

    def getSectionLabels(self, sectionType='IPE'):
        if sectionType == 'IPE':
            sections = ipesProp.values()
        elif sectionType == 'UNP':
            sections = unpsProp.values()
        elif sectionType == 'UPA':
            sections = upasProp.values()
        elif sectionType == 'CPE':
            sections = cpesProp.values()
        elif sectionType == 'BOX':
            sections = boxProp.values()

        sectionNames = [section.name for section in sections]
        return sorted(sectionNames)

    def currentSectionType(self):
        return str(self.sectionTypeBox.currentText())

    def currentSection(self):
        sectionIndex = self.sectionsBox.currentIndex()
        sectionType = self.currentSectionType()
        return self.sectionProp[sectionType].values()[sectionIndex]

    def currentSectionOne(self):
        lh = self.lhSpinBox.value() * 10
        th = self.thSpinBox.value()
        lv = self.lvSpinBox.value() * 10
        tv = self.tvSpinBox.value()
        lw = self.lwSpinBox.value() * 10
        tw = self.twSpinBox.value()
        dist = self.distSpinBox.value()
        isTBPlate = self.addTBPL.isChecked()
        isLRPlate = self.addLRPL.isChecked()
        isWebPlate = self.addWebPL.isChecked()
        useAs = self.useAsDict[self.useAsBox.currentText()]
        ductility = self.ductilityDict[self.ductilityBox.currentText()]
        isDouble = self.doubleDict[self.doubleBox.currentText()][0]
        isSouble = self.doubleDict[self.doubleBox.currentText()][1]
        sectionSize = int(re.sub("[^0-9]", "", self.sectionsBox.currentText()))
        sectionType = self.currentSectionType()
        convert_type = self.equivalent_type_box.currentText()
        return [lh, th, lv, tv, lw, tw, dist, isTBPlate, isLRPlate, isWebPlate, useAs, ductility, isDouble, isSouble, sectionSize, sectionType, convert_type]

    def acceptOne(self):
        # section = self.currentSectionOne()
        # if not section.name in self.model1.names:
        self.model1.beginResetModel()
        self.model1.sections.append(self.currentSection)
        self.model1.endResetModel()
        # del section

        self.resizeColumns(self.tableView1)
        self.model1.dirty = True

    def addSection(self):
        row = self.model1.rowCount()
        self.model1.insertRows(row)
        index = self.model1.index(row, 1)
        self.tableView1.setCurrentIndex(index)
        self.tableView1.edit(index)

    def removeSection(self):
        indices = self.tableView1.selectionModel().selectedIndexes()
        rows_number = set()
        for i in indices:
            rows_number.add(i.row())
        if not indices:
            return
        first = sorted(indices)[0].row()
        rows = len(rows_number)
        if (QMessageBox.question(self, "sections - Remove",
                                 (f"Remove {rows} sections?"),
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.No):
            return
        self.model1.beginResetModel()
        self.model1.removeRows(first, rows)
        self.model1.endResetModel()
        self.resizeColumns(self.tableView1)

    def clearSectionOne(self):
        if self.model1.sections == []:
            return
        if (QMessageBox.question(self, "sections - Remove", ("همه مقاطع حذف شوند؟"),
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            return
        self.model1.beginResetModel()
        self.model1.sections = []
        self.model1.endResetModel()
        self.model1.names = set()
        self.model1.dirty = False

    # def current_section_prop(self):
    #     [lh, th, lv, tv, lw, tw, dist, isTBPlate, isLRPlate, isWebPlate, useAs, ductility, isDouble, isSouble, sectionSize, sectionType, convert_type] = self.currentSectionOne()

    #     class Plate:
    #         def __init__(self, b, t):
    #             self.bf = b
    #             self.tf = t
    #             self.name = f"Plate{b}X{t}"

    #     class Section:

    #         def __init__(self):
    #             self.isSouble = isSouble
    #             self.cc = dist
    #             self.isDouble = isDouble
    #             self.TBPlate = Plate(lh, th)
    #             self.LRPlate = Plate(lv, tv)
    #             self.webPlate = Plate(lw

    #     return Section()

    def updateSectionShape(self):
        self.currentSection = sec.createSection(self.currentSectionOne())
        plotWidget = PlotSectionAndEqSection(self.currentSection, len(self.model1.sections))
        self.drawLayout.addWidget(plotWidget.plot(), 0, 0)
        self.currentSection.autocadScrText = plotWidget.autocadScrText

    def convert_all_section_to_shear(self):
        self.model1.beginResetModel()
        sections = copy.deepcopy(self.model1.sections)
        for section in sections:
            if not section.convert_type == 'Shear':
                prop = section.prop
                prop[-1] = 'Shear'
                shear_section = sec.createSection(prop)
                shear_section.name += 'S'
                self.model1.sections.append(shear_section)
        self.model1.endResetModel()

    # def move_current_rows(self, direction=DOWN):
        # if direction not in (self.DOWN, self.UP):
        #     return

        # model = self.model1
        # print(help(model.moveRows))
        # selModel = self.tableView1.selectionModel()
        # selected = selModel.selectedRows()
        # if not selected:
        #     return

        # items = []
        # indexes = sorted(selected, key=lambda x: x.row(), reverse=(direction == self.DOWN))

        # for idx in indexes:
        #     items.append(model.itemFromIndex(idx))
        #     rowNum = idx.row()
        #     newRow = rowNum + direction
        #     if not (0 <= newRow < model.rowCount()):
        #         continue

        #     rowItems = model.takeRow(rowNum)
        #     model.insertRow(newRow, rowItems)

        # selModel.clear()
        # for item in items:
        #     selModel.select(item.index(), selModel.Select | selModel.Rows)
        # return

    def saveToXml1(self):
        filename = self.getFilename(['xml'])
        if not filename:
            return
        if not filename.endswith('xml'):
            filename += '.xml'
        sec.Section.exportXml(filename, self.model1.sections)

    def save_to_excel(self):
        filename = self.getFilename(['xlsx'])
        if not filename:
            return
        if not filename.endswith('xlsx'):
            filename += '.xlsx'
        sec.Section.export_to_excel(filename, self.model1.sections)

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
        sections = {
            'sections': self.model1.sections,
        }
        pickle.dump(sections, open(filename, "wb"))
        self.model1.dirty = False

    def load_from_dat(self):
        filename, _ = QFileDialog.getOpenFileName(self, "select section's filename",
                                                  self.lastDirectory, "dat (*.dat)")
        if not filename:
            return
        sections = pickle.load(open(filename, "rb"))
        self.model1.beginResetModel()
        self.model1.sections = sections['sections']
        self.model1.endResetModel()
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


def main():
    app = QApplication(sys.argv)
    # translator = QtCore.QTranslator()
    # translator.load("applications/section/mainwindow.qm")
    # app.installTranslator(translator)
    window = Ui()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
