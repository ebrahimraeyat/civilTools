# -*- coding: utf-8 -*-

import re
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#import qrc_resources
from . import sec
from .plot.plotIpe import PlotSectionAndEqSection


__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "0.8"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)

ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()


class Window(QMainWindow):

    sectionProp = {'IPE': ipesProp, 'UNP': unpsProp}
    useAsDict = {'تیر': 'B', 'ستون': 'C'}
    ductilityDict = {'متوسط': 'M', 'زیاد': 'H'}
    doubleList1 = ['تک', 'دوبل', 'سوبل']
    doubleList2 = [[False, False], [True, False], [False, True]]
    doubleDict = dict(zip(doubleList1, doubleList2))

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.dirty = False
        self.lastDirectory = ''
        self.last_sectionBox_index = {'IPE': 4, 'UNP': 4}
        self.currentSectionProp = None
        #self.filename = None
        self.printer = None
        self.createWidgetsOne()
        self.updateSectionShape()
        self.createWidgets()
        self.create_connections()
        self.create_actions()
        #self.accept()
        #self.load_settings()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('محاسبه مشخصات پروفیلهای ساختمانی')
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
        #print 'indexes is:{}'.format(indexes)
        #print 'len indexes is{}'.format(len(indexes))
        #for i in range(len(indexes)):

        self.model1.removeRows(row)
        self.resizeColumns(self.tableView1)

    def create_connections(self):
        self.sectionTypeBox1.currentIndexChanged.connect(self.setSectionLabels)
        self.sectionTypeBox1.currentIndexChanged.connect(self.updateGui)
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
        self.tableView1 = QTableView()
        self.tableView1.setLayoutDirection(Qt.LeftToRight)
        self.tableView1.setModel(self.model1)

        sectionLabel = QLabel('مقطع انتخابی')
        distLable = QLabel('فاصله لب به لب مقطع')
        ductilityLabel = QLabel('شکل پذیری')
        useAsLabel = QLabel('موقعیت')
        calculateOneButton = Window.create_pushButton_icon('F5 محاسبه', ":/main_resources/icons/main/run.png")
        calculateOneButton.clicked.connect(self.acceptOne)
        clearSectionButton = Window.create_pushButton_icon('حذف همه', ":/main_resources/icons/main/clear.png")
        clearSectionButton.clicked.connect(self.clearSectionOne)

        deleteSectionButton = Window.create_pushButton_icon('حذف مقطع', ":/main_resources/icons/main/remove.png")
        deleteSectionButton.clicked.connect(self.removeSection)

        saveToXml1Button = Window.create_pushButton_icon(' xml ذخیره در', ":/section_resources/icons/section/xml.png")
        saveToXml1Button.clicked.connect(self.saveToXml1)

        save_to_autocad_script_format_button = Window.create_pushButton_icon(
                                'ذخیره به فرمت اتوکد', ":/section_resources/icons/section/autocad.png")
        save_to_autocad_script_format_button.clicked.connect(self.save_to_autocad_script_format)

        saveToFileButton = Window.create_pushButton_icon('ذخیره مقاطع', ":/main_resources/icons/main/save.png")
        saveToFileButton.clicked.connect(self.export_to_dat)

        load_from_dat_button = Window.create_pushButton_icon('بارگذاری مقاطع', ":/main_resources/icons/main/load.png")
        load_from_dat_button.clicked.connect(self.load_from_dat)

        addSectionButton = Window.create_pushButton_icon('اضافه کردن مقطع', ":/main_resources/icons/main/add.png")
        addSectionButton.clicked.connect(self.addSection)

        self.addTBPLGroupBox = QGroupBox('ورق بالا و پایین')
        self.addTBPLGroupBox.setCheckable(True)
        self.addTBPLGroupBox.setChecked(True)
        self.addLRPLGroupBox = QGroupBox('ورق چپ و راست')
        self.addLRPLGroupBox.setCheckable(True)
        self.addLRPLGroupBox.setChecked(True)
        self.addWebPLGroupBox = QGroupBox('ورق جان')
        self.addWebPLGroupBox.setCheckable(True)
        self.addWebPLGroupBox.setChecked(True)
        self.lhSpinBox = QSpinBox()
        self.lhSpinBox.setSuffix(' cm')
        self.lhSpinBox.setValue(25)
        self.thSpinBox = QSpinBox()
        self.thSpinBox.setSuffix(' mm')
        self.thSpinBox.setValue(12)
        self.lvSpinBox = QSpinBox()
        self.lvSpinBox.setSuffix(' cm')
        self.lvSpinBox.setValue(25)
        self.tvSpinBox = QSpinBox()
        self.tvSpinBox.setSuffix(' mm')
        self.tvSpinBox.setValue(12)

        self.lwSpinBox = QSpinBox()
        self.lwSpinBox.setSuffix(' cm')
        self.lwSpinBox.setValue(15)
        self.twSpinBox = QSpinBox()
        self.twSpinBox.setSuffix(' mm')
        self.twSpinBox.setValue(10)

        self.distSpinBox = QSpinBox()
        self.distSpinBox.setSuffix(' cm')
        self.distSpinBox.setValue(9)
        self.ductilityBox = QComboBox()
        self.ductilityBox.addItems(['متوسط', 'زیاد'])
        self.useAsBox = QComboBox()
        self.useAsBox.addItems(['تیر', 'ستون'])
        self.useAsBox.setCurrentIndex(1)
        self.doubleBox = QComboBox()
        self.doubleBox.addItems(self.doubleList1)
        self.doubleBox.setCurrentIndex(1)

        self.sectionTypeBox1 = QComboBox()
        self.sectionTypeBox1.addItems(sorted(self.sectionProp.keys()))
        self.sectionsBox = QComboBox()
        self.sectionsBox.addItems(self.getSectionLabels())
        self.sectionsBox.setCurrentIndex(4)

        frameGroup = QGroupBox('مشخصات عضو')
        frameLayout = QGridLayout()
        frameLayout.addWidget(useAsLabel, 0, 0)
        frameLayout.addWidget(self.useAsBox, 0, 1)
        frameLayout.addWidget(ductilityLabel, 1, 0)
        frameLayout.addWidget(self.ductilityBox, 1, 1)
        frameGroup.setLayout(frameLayout)
        inputPropGroup = QGroupBox('مشخصات مقطع')
        inputPropLayout = QGridLayout()
        inputPropLayout.addWidget(self.sectionTypeBox1, 0, 0)
        inputPropLayout.addWidget(self.sectionsBox, 0, 1)
        inputPropLayout.addWidget(sectionLabel, 0, 2)
        tbPlateLayout = QVBoxLayout()
        tbPlateLayout.addWidget(self.lhSpinBox)
        tbPlateLayout.addWidget(self.thSpinBox)
        self.addTBPLGroupBox.setLayout(tbPlateLayout)
        inputPropLayout.addWidget(self.addTBPLGroupBox, 1, 2)
        lrPlateLayout = QVBoxLayout()
        lrPlateLayout.addWidget(self.lvSpinBox)
        lrPlateLayout.addWidget(self.tvSpinBox)
        self.addLRPLGroupBox.setLayout(lrPlateLayout)
        inputPropLayout.addWidget(self.addLRPLGroupBox, 1, 1)
        webPlateLayout = QVBoxLayout()
        webPlateLayout.addWidget(self.lwSpinBox)
        webPlateLayout.addWidget(self.twSpinBox)
        self.addWebPLGroupBox.setLayout(webPlateLayout)
        inputPropLayout.addWidget(self.addWebPLGroupBox, 1, 0)
        inputPropLayout.addWidget(self.doubleBox, 4, 0)
        inputPropLayout.addWidget(self.distSpinBox, 4, 1)
        inputPropLayout.addWidget(distLable, 4, 2)

        self.convert_type_radio_button = QRadioButton('معادل سازی برشی')
        inputPropLayout.addWidget(self.convert_type_radio_button, 5, 0)
        inputPropGroup.setLayout(inputPropLayout)

        # curve widget
        drawWidget = QWidget()
        self.drawLayout = QGridLayout()
        drawWidget.setLayout(self.drawLayout)
        drawWidget.setMaximumWidth(800)

        pushButtonFrame = QFrame()
        pushButtonLayout = QGridLayout()
        pushButtonLayout.addWidget(addSectionButton, 0, 0)
        pushButtonLayout.addWidget(deleteSectionButton, 0, 1)
        pushButtonLayout.addWidget(saveToFileButton, 1, 0)
        pushButtonLayout.addWidget(load_from_dat_button, 1, 1)

        #pushButtonLayout.addStretch()
        pushButtonLayout.addWidget(saveToXml1Button, 2, 0)
        pushButtonLayout.addWidget(save_to_autocad_script_format_button, 2, 1)
        pushButtonLayout.addWidget(calculateOneButton, 3, 0)
        pushButtonLayout.addWidget(clearSectionButton, 3, 1)
        pushButtonFrame.setLayout(pushButtonLayout)

        inputWidget = QWidget()
        inputLayout = QGridLayout()
        inputLayout.addWidget(inputPropGroup, 0, 0)
        inputLayout.addWidget(frameGroup, 1, 0)
        inputLayout.addWidget(drawWidget, 0, 1, 2, 1)
        inputLayout.addWidget(pushButtonFrame, 0, 2)
        inputWidget.setLayout(inputLayout)


        # splittters widget
        #self.inputSplitter = QSplitter(Qt.Horizontal)
        #self.inputSplitter.addWidget(inputWidget)
        #self.inputSplitter.addWidget(pushButtonFrame)
        self.mainSplitter = QSplitter(Qt.Vertical)
        self.mainSplitter.addWidget(inputWidget)
        self.mainSplitter.addWidget(self.tableView1)
        #self.inputSplitter.setObjectName = 'InputSplitter'
        self.mainSplitter.setObjectName = 'MainSplitter1'

    @staticmethod
    def create_pushButton_icon(text, icon_address):
        icon = QIcon(icon_address)
        button = QPushButton(icon, text)
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(size_policy)
        btn_size = QSize(120, 60)
        icon_size = QSize(60, 60)
        button.setMinimumSize(btn_size)
        button.setIconSize(icon_size)
        return button

    def createWidgets(self):
        #self.model = sec.SectionTableModel(QString("sections.dat"))
        #self.tableView = QTableView()
        #self.tableView.setLayoutDirection(Qt.LeftToRight)
        #self.tableView.setModel(self.model)

        #sectionLabel = QLabel('مقطع انتخابی')
        #doubleDistLabel = QLabel('(cm) فاصله لب به لب مقاطع')
        #self.img = QLabel()
        #self.img.setMinimumSize(400, 400)
        #self.img.setAlignment(Qt.AlignCenter)
        #plateWidthLabel = QLabel('(cm) عرض ورق')
        #plateThickLabel = QLabel('(mm) ضخامت ورق')
        #self.fileNameLine = QLineEdit()
        #fileOpen = QPushButton('بازکردن')
        #exportXml = QPushButton(' xml ذخیره در')
        #self.sectionTypeBox = QComboBox()
        #self.sectionTypeBox.addItems(['IPE', 'UNP'])
        #self.doubleDistSpinBox = QSpinBox()
        #self.doubleDistSpinBox.setSuffix(' cm')
        #self.plateWidthSpinBox = QSpinBox()
        #self.plateWidthSpinBox.setSuffix(' cm')
        #self.plateThickSpinBox = QSpinBox()
        #self.plateThickSpinBox.setSuffix(' mm')
        #self.result = QTextEdit()

        #self.sectionsList = Window.creatList(self.getSectionLabels())
        #self.sectionsList.sortItems()
        #self.distsList = Window.creatList([str(i) for i in range(21)])
        #self.plateWidthList = Window.creatList([str(i) for i in range(5, 41)])
        #self.plateThickList = Window.creatList([str(i) for i in (0, 4, 5, 6, 8, 9, 10, 12, 15)])
        #calculateButton = QPushButton('محاسبه')
        #saveToXmlButton = QPushButton(' xml ذخیره در')
        #saveToFileButton = QPushButton('دخیره')
        #saveToFileButton.clicked.connect(self.save)
        #loadButton = QPushButton('بارگذاری')
        #addButton = QPushButton('اضافه')
        #removeButton = QPushButton('حذف مقطع')
        #loadButton.clicked.connect(self.load)
        #fileOpen.clicked.connect(self.getXmlFilename)
        #exportXml.clicked.connect(self.exportToXml)
        #calculateButton.clicked.connect(self.multiAccept)
        #saveToXmlButton.clicked.connect(self.saveToXml)
        #addButton.clicked.connect(self.addSection)
        #removeButton.clicked.connect(self.removeSection)

        #sectionButtonLayout = QVBoxLayout()
        #sectionButtonLayout.addWidget(self.sectionTypeBox)
        #sectionButtonLayout.addWidget(calculateButton)
        #sectionButtonLayout.addWidget(saveToFileButton)
        #sectionButtonLayout.addWidget(saveToXmlButton)
        #sectionButtonLayout.addStretch()

        #tableButtonLayout = QVBoxLayout()
        #tableButtonLayout.addWidget(addButton)
        #tableButtonLayout.addWidget(removeButton)
        #tableButtonLayout.addStretch()

        #tableWidget = QWidget()
        #tableLayout = QHBoxLayout()
        #tableLayout.addWidget(self.tableView)
        #tableLayout.addItem(tableButtonLayout)
        #tableWidget.setLayout(tableLayout)

        #multiSectionLayout = QGridLayout()
        #multiSectionLayout.addWidget(sectionLabel, 0, 0)
        #multiSectionLayout.addWidget(doubleDistLabel, 0, 1)
        #multiSectionLayout.addWidget(plateWidthLabel, 0, 2)
        #multiSectionLayout.addWidget(plateThickLabel, 0, 3)
        #multiSectionLayout.addWidget(self.sectionsList, 1, 0)
        #multiSectionLayout.addWidget(self.distsList, 1, 1)
        #multiSectionLayout.addWidget(self.plateWidthList, 1, 2)
        #multiSectionLayout.addWidget(self.plateThickList, 1, 3)
        #multiSectionLayout.addItem(sectionButtonLayout, 1, 4)
        #multiSectionWidget = QWidget()
        #multiSectionWidget.setLayout(multiSectionLayout)
        #multiSectionSplitter = QSplitter(Qt.Vertical)
        #multiSectionSplitter.addWidget(multiSectionWidget)
        #multiSectionSplitter.addWidget(tableWidget)

        tabWidget = QTabWidget()
        #tabWidget.addTab(multiSectionSplitter, 'محاسبات چندین مقطع')
        tabWidget.addTab(self.mainSplitter, 'محاسبات یک مقطع')

        self.setCentralWidget(tabWidget)

    @staticmethod
    def creatList(listItems):
        _list = QListWidget()
        _list.addItems(listItems)
        _list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        return _list

    def create_actions(self):
        # File Actions
        exportToXmlText = 'xml خروجی به'
        runText = 'محاسبه'
        fileXmlAction = self.createAction(exportToXmlText, self.saveToXml1,
                "Ctrl+x", "", exportToXmlText)
        runAction = self.createAction(runText, self.acceptOne,
                "F5", "", runText)
        # Help Actions
        helpAboutAction = self.createAction(u"درباره نرم افزار",
                self.helpAbout, Qt.Key_F1)

        self.fileMenu = self.menuBar().addMenu('فایل')
        self.fileMenuActions = (fileXmlAction, runAction)
        self.addActions(self.fileMenu, self.fileMenuActions)
        #fileToolbar = self.addToolBar("File")
        #fileToolbar.setIconSize(QSize(32, 32))
        #fileToolbar.setObjectName("FileToolBar")
        #self.addActions(fileToolbar, self.fileMenuActions)

        helpMenu = self.menuBar().addMenu(u"راهنما")
        self.addActions(helpMenu, (helpAboutAction, ))

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(
                settings.value("MainWindow" + os.sep + "Geometry1").toByteArray())
        self.restoreState(settings.value("MainWindow" + os.sep + "State1").toByteArray())
        #self.inputSplitter.restoreState(settings.value("InputSplitter").toByteArray())
        self.mainSplitter.restoreState(settings.value("MainSplitter1").toByteArray())

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def closeEvent(self, event):
        #if self.okToContinue():
        settings = QSettings()
        #filename = (QVariant(QString(self.filename))
                    #if self.filename is not None else QVariant())
        #settings.setValue("LastFile", filename)
        #recentFiles = (QVariant(self.recentFiles)
                       #if self.recentFiles else QVariant())
        #settings.setValue("RecentFiles", recentFiles)
        settings.setValue("MainWindow" + os.sep + "Geometry1", QVariant(self.saveGeometry()))
        settings.setValue("MainWindow" + os.sep + "State1", QVariant(self.saveState()))
        #settings.setValue("InputSplitter", QVariant(self.inputSplitter.saveState()))
        settings.setValue("MainSplitter1", QVariant(self.mainSplitter.saveState()))

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
            self.addWebPLGroupBox.setCheckable(False)

        elif sectionType == 'IPE':
            self.doubleBox.addItem(self.doubleList1[-1])
            self.addWebPLGroupBox.setCheckable(True)

    def getSectionLabels(self, sectionType='IPE'):
        if sectionType == 'IPE':
            sections = ipesProp.values()
        elif sectionType == 'UNP':
            sections = unpsProp.values()

        sectionNames = [section.name for section in sections]
        return sorted(sectionNames)

    def currentSectionType(self):
        return str(self.sectionTypeBox1.currentText())

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
    pixmap = QPixmap(":/splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()
    global defaultPointsize
    font = QFont()
    font.setFamily("Tahoma")
    if sys.platform.startswith('linux'):
        defaultPointsize = 10
        font.setPointSize(defaultPointsize)
    else:
        defaultPointsize = 9
        font.setPointSize(defaultPointsize)
    app.setFont(font)
    app.setOrganizationName("Ebrahim Raeyat")
    app.setOrganizationDomain("ebrahimraeyat.blog.ir")
    app.setApplicationName("section prop")
    #app.setWindowIcon(QIcon(":/icon.png"))
    window = Window()
    p = window.palette()
    color = QColor()
    color.setRgb(255, 255, 215)
    p.setColor(window.backgroundRole(), color)
    window.setPalette(p)
    window.setLayoutDirection(Qt.RightToLeft)
    #window.setMaximumWidth(1000)
    window.show()
    app.exec_()