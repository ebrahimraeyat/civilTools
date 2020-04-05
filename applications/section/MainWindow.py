# -*- coding: utf-8 -*-

import re
import sys
import os
import copy
import pickle
from functools import partial
import itertools
abs_path = os.path.dirname(__file__)
sys.path.insert(0, abs_path)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import ezdxf

import sec
from plot.plotIpe import PlotSectionAndEqSection, PlotMainSection
from exporter import exporttoxmldlg as xml


__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "3.0"
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
        self.new_dwg = ezdxf.readfile(abs_path + '/TEMPLATE.dxf')
        self.msp = self.new_dwg.modelspace()
        self.createWidgetsOne()
        self.add_actions()
        self.updateSectionShape()
        self.create_connections()
        self.load_settings()

    def add_actions(self):
        self.toolbar.addAction(self.action_Xml)
        self.toolbar.addAction(self.action_Autocad_scr)
        self.toolbar.addAction(self.action_Excel)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_Remove_Section)
        self.toolbar.addAction(self.action_Delete)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_Open)
        self.toolbar.addAction(self.action_Save)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_Shear)

        # self.action_Xml.triggered.connect(self.saveToXml1)
        self.action_Xml.triggered.connect(self.save_to_xml)
        self.action_Autocad_scr.triggered.connect(self.save_to_autocad_script_format)
        self.action_Excel.triggered.connect(self.save_to_excel)
        self.action_Delete.triggered.connect(self.clearSectionOne)
        self.action_Remove_Section.triggered.connect(self.removeSection)
        self.action_Save.triggered.connect(self.export_to_dat)
        self.action_Open.triggered.connect(self.load_from_dat)
        self.action_Shear.triggered.connect(self.convert_all_section_to_shear)

    def closeEvent(self, event):
        qsettings = QSettings("civiltools", "section")
        qsettings.setValue("geometry", self.saveGeometry())
        qsettings.setValue("saveState", self.saveState())
        # qsettings.setValue( "maximized", self.isMaximized() )
        qsettings.setValue("MainSplitter", self.mainSplitter.saveState())
        qsettings.setValue("splitter", self.splitter.saveState())
        qsettings.setValue("splitter2", self.splitter2.saveState())
        # if not self.isMaximized() == True :
        qsettings.setValue("pos", self.pos())
        qsettings.setValue("size", self.size())
        self.accept(event)

    def load_settings(self):
        qsettings = QSettings("civiltools", "section")
        self.restoreGeometry(qsettings.value("geometry", self.saveGeometry()))
        self.restoreState(qsettings.value("saveState", self.saveState()))
        self.move(qsettings.value("pos", self.pos()))
        self.resize(qsettings.value("size", self.size()))
        self.mainSplitter.restoreState(qsettings.value("MainSplitter", self.mainSplitter.saveState()))
        self.splitter.restoreState(qsettings.value("splitter", self.splitter.saveState()))
        self.splitter2.restoreState(qsettings.value("splitter2", self.splitter2.saveState()))

    def resizeColumns(self, tableView=None):
        for column in (sec.NAME, sec.AREA,
                       sec.ASY, sec.ASX, sec.IX, sec.IY, sec.ZX, sec.ZY,
                       sec.BF, sec.TF, sec.D, sec.TW, sec.Sx, sec.Sy, sec.RX, sec.RY):
            tableView.resizeColumnToContents(column)

    def reject(self):
        self.accept(event)

    def accept(self, event):
        # if self.model1.dirty:
        reply = QMessageBox.question(self, "sections - Save?",
                                     "Save unsaved changes?",
                                     QMessageBox.Yes | QMessageBox.Cancel | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.export_to_dat()
                event.accept()
            except(IOError, err):
                QMessageBox.warning(self, "sections - Error", f"Failed to save: {err}")
        elif reply == QMessageBox.No:
            event.accept()

        else:
            event.ignore()

    def sortTable(self, section):
        # if section == sec.AREA:
        #     self.model1.sortByArea()
        if section == sec.NAME:
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
        self.ductilityList.itemPressed.connect(self.updateSectionShape)
        self.useAsList.itemPressed.connect(self.updateSectionShape)
        self.equivalent_type_list.itemPressed.connect(self.updateSectionShape)
        self.tableView1.horizontalHeader().sectionClicked.connect(self.sortTable)
        # self.up_button.clicked.connect(partial(self.move_current_rows, self.UP))
        # self.down_button.clicked.connect(partial(self.move_current_rows, self.DOWN))
        # self.connect(self.tableView1.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sortTable)

    def createWidgetsOne(self):
        self.model1 = sec.SectionTableModel("section.dat")
        self.tableView1.setLayoutDirection(Qt.LeftToRight)
        self.tableView1.setModel(self.model1)
        self.tableView1.setItemDelegate(sec.SectionDelegate(self))
        self.calculate_Button.clicked.connect(self.acceptOne)
        sectionType = self.currentSectionType()
        self.sectionsBox.addItems(self.getSectionLabels(sectionType))
        self.sectionsBox.setCurrentIndex(4)
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)
        self.splitter2.setStretchFactor(0, 1)
        self.splitter2.setStretchFactor(1, 1)
        self.tableView1.verticalHeader().setSectionsMovable(True)
        self.tableView1.verticalHeader().setDragEnabled(True)
        self.tableView1.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        self.tableView1.clicked.connect(self.draw_main_section)
        # for i in (1, 2):
        #     self.convert_to_box.model().item(i).setEnabled(False)

        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.mesh_and_equal_layout.addWidget(self.canvas)

    def draw_main_section(self):
        row = self.tableView1.currentIndex().row()
        section = self.model1.sections[row]
        main_section_plot = PlotMainSection(section.geometry_list)
        win = main_section_plot.plot()
        self.main_section_draw.addWidget(win, 0, 0)

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
        if len(items) >= index + 1:
            self.doubleBox.setCurrentIndex(index)
        else:
            self.doubleBox.setCurrentIndex(0)
        self.doubleBox.blockSignals(False)
        if sectionType in ('UNP', 'BOX', 'UPA'):
            self.addWebPL.blockSignals(True)
            self.addWebPL.setChecked(False)
            self.addWebPL.blockSignals(False)
            self.frame_web.setEnabled(False)
            if sectionType == 'BOX':
                self.addLRPL.blockSignals(True)
                self.addTBPL.blockSignals(True)
                self.addLRPL.setChecked(True)
                self.addTBPL.setChecked(True)
                self.addLRPL.blockSignals(False)
                self.addTBPL.blockSignals(False)
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
        useAs = self.useAsDict[self.useAsList.currentItem().text()]
        ductility = self.ductilityDict[self.ductilityList.currentItem().text()]
        isDouble = self.doubleDict[self.doubleBox.currentText()][0]
        isSouble = self.doubleDict[self.doubleBox.currentText()][1]
        sectionSize = int(re.sub("[^0-9]", "", self.sectionsBox.currentText()))
        sectionType = self.currentSectionType()
        convert_type = self.equivalent_type_list.currentItem().text()
        return [lh, th, lv, tv, lw, tw, dist, isTBPlate, isLRPlate, isWebPlate, useAs, ductility, isDouble, isSouble, sectionSize, sectionType, convert_type]

    def acceptOne(self):
        self.figure.clear()
        if not self.j_calculated():
            if self.currentSection.is_closed and self.currentSection.J == 0:
                self.currentSection.create_warping_section()
                self.plot_mesh()
                self.currentSection.j_func()
        ductilities = [self.ductilityDict[item.text()] for item in self.ductilityList.selectedItems()]
        useAss = [self.useAsDict[item.text()] for item in self.useAsList.selectedItems()]
        base_name = self.base_name()
        self.model1.beginResetModel()
        states = [f'{state[0]}{state[1]}' for state in itertools.product(useAss, ductilities)]
        for state in states:
            name = f'{base_name}{state}'
            n = len(self.model1.names)
            self.model1.names.add(name)
            if len(self.model1.names) == n:
                continue
            new_section = sec.SectionProperties(self.currentSection, name)
            self.model1.sections.append(new_section)
        self.model1.endResetModel()
        # del section

        self.resizeColumns(self.tableView1)
        self.model1.dirty = True

    def base_name(self):
        shear_name = self.currentSection.shear_name
        return shear_name[:-2]

    def j_calculated(self):
        for section in self.model1.sections:
            if section.shear_name == self.currentSection.shear_name:
                if section.J != 0:
                    self.currentSection.J = section.J
                    return True
                else:
                    return False
        return False

    def addSection(self):
        row = self.model1.rowCount()
        self.model1.insertRows(row)
        index = self.model1.index(row, 1)
        self.tableView1.setCurrentIndex(index)
        self.tableView1.edit(index)

    def removeSection(self):
        indexes = [QPersistentModelIndex(index) for index in self.tableView1.selectionModel().selectedRows()]
        if not indexes:
            QMessageBox.warning(self, "sections - selection", f"you have to select entire row/rows, not only cell/cells.")
            return
        if (QMessageBox.question(self, "sections - Remove",
                                 (f"Remove selected sections?"),
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.No):
            return

        for index in indexes:
            name = self.model1.data(self.model1.index(index.row(), sec.NAME))
            self.model1.names.remove(name)
            self.model1.removeRow(index.row())
        self.resizeColumns(self.tableView1)
        self.model1.dirty = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.removeSection()
        QMainWindow.keyPressEvent(self, event)

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

    def updateSectionShape(self):
        self.currentSection = sec.createSection(self.currentSectionOne())
        plotWidget = PlotSectionAndEqSection(self.currentSection, self.new_dwg, len(self.model1.sections))
        self.drawLayout.addWidget(plotWidget.plot(), 0, 0)
        self.currentSection.autocadScrText = plotWidget.autocadScrText

    def plot_mesh(self):
        ax = self.figure.add_subplot(111, aspect=1)
        self.currentSection.warping_section.plot_mesh(ax=ax)
        self.canvas.draw()

    def convert_all_section_to_shear(self):
        self.model1.beginResetModel()
        sections = self.model1.sections
        for section in sections:
            names = self.model1.names
            name = section.shear_name
            if not name in names:
                new_section = copy.deepcopy(section)
                new_section.name = name
                new_section.equivalent_dims()

                # prop = section.prop
                # prop[-1] = 'Shear'
                # shear_section = sec.createSection(prop)
                # shear_section.name += 'S'
                self.model1.sections.append(new_section)
                self.model1.names.add(name)
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

    # def saveToXml1(self):
    #     filename = self.getFilename(['xml'])
    #     if not filename:
    #         return
    #     if not filename.endswith('xml'):
    #         filename += '.xml'
    #     sec.Section.exportXml(filename, self.model1.sections)

    def save_to_xml(self):
        self.child_export_xml_win = xml.ExportToXml(self.model1.sections, self)
        if self.child_export_xml_win.exec_():
            title = "Seccess"
            text = f"Export Sections to {self.child_export_xml_win.xml_path_line.text()}"
            QMessageBox.information(self, title, text)
        else:
            return

    def save_to_excel(self):
        filename = self.getFilename(['xlsx'])
        if not filename:
            return
        if not filename.endswith('xlsx'):
            filename += '.xlsx'
        sec.Section.export_to_excel(filename, self.model1.sections)

    def save_to_autocad_script_format(self):
        filename = self.getFilename(['dxf'])
        if not filename:
            return
        if not filename.endswith('dxf'):
            filename += '.dxf'
        for i, section in enumerate(self.model1.sections):
            self.msp.add_blockref(section.uid, (0, 550. * i))
        self.new_dwg.saveas(filename)

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
            'names': self.model1.names,
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
        self.model1.names = sections['names']
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
