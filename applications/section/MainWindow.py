# -*- coding: utf-8 -*-


import re
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sec

ipesProp = sec.Ipe.createStandardIpes()
unpsProp = sec.Unp.createStandardUnps()


class Window(QMainWindow):

    sectionProp = {'IPE': ipesProp, 'UNP': unpsProp}

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.dirty = False
        self.lastDirectory = ''
        #self.filename = None
        self.printer = None
        self.createWidgets()
        self.create_connections()
        #self.create_actions()
        #self.accept()
        #self.load_settings()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle(u'محاسبه مشخصات پروفیلهای ساختمانی')
        QTimer.singleShot(0, self.initialLoad)

    def initialLoad(self):
        if  QFile.exists(self.model.filename):
            try:
                self.model.load()
                self.model.sortByName()
                self.resizeColumns()
            except IOError, err:
                QMessageBox.warning(self, "Sections - Error",
                        "Failed to load: {0}".format(err))

    def resizeColumns(self):
        for column in (sec.NAME, sec.TYPE, sec.AREA,
                       sec.XM, sec.YM, sec.XMAX, sec.YMAX, sec.AS2, sec.AS3, sec.I33, sec.I22, sec.Z33, sec.Z22, \
 sec.BF, sec.TF, sec.H, sec.TW, sec.S33POS, sec.S33NEG, sec.S22POS, sec.S22NEG, sec.R33, sec.R22):
            self.tableView.resizeColumnToContents(column)

    def reject(self):
        self.accept()

    def accept(self):
        if (self.model.dirty and
            QMessageBox.question(self, "sections - Save?",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.model.save()
            except IOError, err:
                QMessageBox.warning(self, "sections - Error",
                        "Failed to save: {0}".format(err))
        QDialog.accept(self)

    def sortTable(self):
        self.model.sortByName()
        self.resizeColumns()

    def addSection(self):
        row = self.model.rowCount()
        self.model.insertRows(row)
        index = self.model.index(row, 0)
        self.tableView.setCurrentIndex(index)
        self.tableView.edit(index)

    def removeSection(self):
        #index = self.tableView.currentIndex()
        #name = self.model.data(
                        #self.model.index(row, sec.NAME)).toString()
        #if (QMessageBox.question(self, "sections - Remove",
                #(QString("Remove section?")),
                #QMessageBox.Yes|QMessageBox.No) ==
                #QMessageBox.No):
            #return
        index = self.tableView.currentIndex()
        #print 'indexes is:{}'.format(indexes)
        #print 'len indexes is{}'.format(len(indexes))
        #for i in range(len(indexes)):
        if not index.isValid():
            return
        row = index.row()
        print row
        self.model.removeRows(row)
        self.resizeColumns()

    def create_connections(self):
        #self.connect(self.sectionsBox, SIGNAL(
                    #"currentIndexChanged(QString)"), self.accept)
        self.connect(self.sectionTypeBox, SIGNAL(
                    "currentIndexChanged(QString)"), self.setSectionLabels)

    def createWidgets(self):
        self.model = sec.SectionTableModel(QString("sections.dat"))
        self.tableView = QTableView()
        self.tableView.setLayoutDirection(Qt.LeftToRight)
        self.tableView.setModel(self.model)
        self.tableView.setColumnHidden(sec.TYPE, True)
        self.tableView.setColumnHidden(sec.XM, True)
        self.tableView.setColumnHidden(sec.YM, True)
        self.tableView.setColumnHidden(sec.XMAX, True)
        self.tableView.setColumnHidden(sec.YMAX, True)
        self.tableView.setColumnHidden(sec.S33NEG, True)
        self.tableView.setColumnHidden(sec.S22NEG, True)

        sectionLabel = QLabel(u'مقطع انتخابی')
        doubleDistLabel = QLabel(u'(cm) فاصله لب به لب مقاطع')
        self.img = QLabel()
        self.img.setMinimumSize(400, 400)
        self.img.setAlignment(Qt.AlignCenter)
        plateWidthLabel = QLabel(u'(cm) عرض ورق')
        plateThickLabel = QLabel(u'(mm) ضخامت ورق')
        self.fileNameLine = QLineEdit()
        fileOpen = QPushButton(u'بازکردن')
        exportXml = QPushButton(u' xml ذخیره در')
        self.sectionTypeBox = QComboBox()
        self.sectionTypeBox.addItems(['IPE', 'UNP'])
        self.sectionsBox = QComboBox()
        self.sectionsBox.addItems(self.getSectionLabels())
        self.doubleDistSpinBox = QSpinBox()
        self.doubleDistSpinBox.setSuffix(' cm')
        self.plateWidthSpinBox = QSpinBox()
        self.plateWidthSpinBox.setSuffix(' cm')
        self.plateThickSpinBox = QSpinBox()
        self.plateThickSpinBox.setSuffix(' mm')
        self.result = QTextEdit()

        self.sectionsList = Window.creatList(self.getSectionLabels())
        self.sectionsList.sortItems()
        self.distsList = Window.creatList([str(i) for i in range(21)])
        self.plateWidthList = Window.creatList([str(i) for i in range(5, 41)])
        self.plateThickList = Window.creatList([str(i) for i in (0, 4, 5, 6, 8, 9, 10, 12, 15)])
        calculateButton = QPushButton(u'محاسبه')
        saveToXmlButton = QPushButton(u' xml ذخیره در')
        saveToFileButton = QPushButton(u'دخیره')
        saveToFileButton.clicked.connect(self.save)
        loadButton = QPushButton(u'بارگذاری')
        addButton = QPushButton(u'اضافه')
        removeButton = QPushButton(u'حذف مقطع')
        loadButton.clicked.connect(self.load)
        fileOpen.clicked.connect(self.getXmlFilename)
        exportXml.clicked.connect(self.exportToXml)
        calculateButton.clicked.connect(self.multiAccept)
        saveToXmlButton.clicked.connect(self.saveToXml)
        addButton.clicked.connect(self.addSection)
        removeButton.clicked.connect(self.removeSection)

        sectionButtonLayout = QVBoxLayout()
        sectionButtonLayout.addWidget(self.sectionTypeBox)
        sectionButtonLayout.addWidget(calculateButton)
        sectionButtonLayout.addWidget(saveToFileButton)
        sectionButtonLayout.addWidget(saveToXmlButton)
        sectionButtonLayout.addStretch()

        tableButtonLayout = QVBoxLayout()
        tableButtonLayout.addWidget(addButton)
        tableButtonLayout.addWidget(removeButton)
        tableButtonLayout.addStretch()

        tableWidget = QWidget()
        tableLayout = QHBoxLayout()
        tableLayout.addWidget(self.tableView)
        tableLayout.addItem(tableButtonLayout)
        tableWidget.setLayout(tableLayout)

        multiSectionLayout = QGridLayout()
        multiSectionLayout.addWidget(sectionLabel, 0, 0)
        multiSectionLayout.addWidget(doubleDistLabel, 0, 1)
        multiSectionLayout.addWidget(plateWidthLabel, 0, 2)
        multiSectionLayout.addWidget(plateThickLabel, 0, 3)
        multiSectionLayout.addWidget(self.sectionsList, 1, 0)
        multiSectionLayout.addWidget(self.distsList, 1, 1)
        multiSectionLayout.addWidget(self.plateWidthList, 1, 2)
        multiSectionLayout.addWidget(self.plateThickList, 1, 3)
        multiSectionLayout.addItem(sectionButtonLayout, 1, 4)
        multiSectionWidget = QWidget()
        multiSectionWidget.setLayout(multiSectionLayout)
        multiSectionSplitter = QSplitter(Qt.Vertical)
        multiSectionSplitter.addWidget(multiSectionWidget)
        multiSectionSplitter.addWidget(tableWidget)

        #tabWidget = QTabWidget()
        #tabWidget.addTab(multiSectionSplitter, u'محاسبات چندین مقطع')
        #tabWidget.addTab(oneSectionWidget, u'محاسبات یک مقطع')

        self.setCentralWidget(multiSectionSplitter)

    @staticmethod
    def creatList(listItems):
        _list = QListWidget()
        _list.addItems(listItems)
        _list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        return _list

    def create_actions(self):
        # File Actions
        exportToPdfText = u'Pdf خروجی به'
        exportToWordText = u'Word خروجی به'
        exportToHtmlText = u'Html خروجی به'
        exportBCurveToImage = u'خروجی به تصویر'
        exportBCurveToCsv = u'خروجی به اکسل'
        filePdfAction = self.createAction(exportToPdfText, self.exportToPdf,
                QKeySequence.Print, "file_extension_pdf", exportToPdfText)
        fileOfficeAction = self.createAction(exportToWordText,
        self.exportToOffice, "Ctrl+W", "file_extension_doc", exportToWordText)
        fileHtmlAction = self.createAction(exportToHtmlText, self.exportToHtml,
                "Ctrl+H", "file_extension_html", exportToHtmlText)
        BCurveImageAction = self.createAction(exportBCurveToImage,
            self.exportBCurveToImage, "Ctrl+I", "file_extension_jpg")
        BCurveCsvAction = self.createAction(exportBCurveToCsv,
            self.exportBCurveToCsv, "Ctrl+X", "file_extension_xls")
        # Help Actions
        helpAboutAction = self.createAction(u"درباره نرم افزار",
                self.helpAbout, Qt.Key_F1)

        self.fileMenu = self.menuBar().addMenu(u'فایل')
        self.fileMenuActions = (filePdfAction, fileOfficeAction, fileHtmlAction)
        self.addActions(self.fileMenu, self.fileMenuActions)
        fileToolbar = self.addToolBar("File")
        fileToolbar.setIconSize(QSize(32, 32))
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, self.fileMenuActions)

        self.BCurveMenu = self.menuBar().addMenu(u"ضریب بازتاب")
        self.BCurveMenuActions = (BCurveImageAction, BCurveCsvAction)
        self.addActions(self.BCurveMenu, self.BCurveMenuActions)
        BCurveToolbar = self.addToolBar("BCurve")
        BCurveToolbar.setIconSize(QSize(32, 32))
        BCurveToolbar.setObjectName("BCurveToolBar")
        self.addActions(BCurveToolbar, self.BCurveMenuActions)

        helpMenu = self.menuBar().addMenu(u"راهنما")
        self.addActions(helpMenu, (helpAboutAction, ))

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(
                settings.value("MainWindow/Geometry").toByteArray())
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        self.inputSplitter.restoreState(settings.value("InputSplitter").toByteArray())
        self.mainSplitter.restoreState(settings.value("MainSplitter").toByteArray())

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
        #settings.setValue("MainWindow/Geometry", QVariant(self.saveGeometry()))
        #settings.setValue("MainWindow/State", QVariant(self.saveState()))
        #settings.setValue("InputSplitter", QVariant(self.inputSplitter.saveState()))
        #settings.setValue("MainSplitter", QVariant(self.mainSplitter.saveState()))

    def setSectionLabels(self):
        self.sectionsList.clear()
        sectionType = self.currentSectionType()
        ##if sectionType == 'IPE':
        self.sectionsList.addItems(self.getSectionLabels(sectionType))

        #elif sectionType == 'UNP':
            #self.sectionsBox.addItems([unp.name for unp in unpsProp])

    def getSectionLabels(self, sectionType='IPE'):
        if sectionType == 'IPE':
            sections = ipesProp.values()
        elif sectionType == 'UNP':
            sections = unpsProp.values()

        sectionNames = [section.name for section in sections]
        #print sectionNames
        #sectionNames = sectionNames.sort()
        #print sectionNames
        return sectionNames

    def currentSectionType(self):
        return self.sectionTypeBox.currentText()

    def currentSection(self):
        sectionIndex = self.sectionsBox.currentIndex()
        sectionType = self.currentSectionType()
        if sectionType == 'IPE':
            return ipesProp.values()[sectionIndex]
        elif sectionType == 'UNP':
            return unpsProp[sectionIndex]

    def ipesProp(self):
        return sec.Ipe.createStandardIpes()

    def unpsProp(self):
        return sec.Unp.createStandardUnps()

    #def accept(self):

        #self.dirty = False
        #section = self.currentSection()
        #dist = self.doubleDistSpinBox.value() * 10
        #section2 = section.double(dist)
        #plateWidth = self.plateWidthSpinBox.value() * 10
        #plateThick = self.plateThickSpinBox.value()
        #if not plateThick == 0:
            #if plateWidth == 0:
                #section2 = sec.AddPlateTBThick(section2, plateThick)
            #else:
                #plate = sec.Plate(plateWidth, plateThick)
                #section2 = sec.ThickAddPlateTB(section2, plate)
        #self.result.setText(section2.__str__())
        #self.section = section2
        #self.dirty = True

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
                dist = int(dist.text()) * 10
                section2 = section.double(dist)

                if len(platesWidth) == 0:
                    for plateThick in platesThick:
                        plateThick = int(plateThick.text())
                        if plateThick == 0:
                            self.model.sections.append(section2)
                        else:
                            section2PL = sec.AddPlateTBThick(section2, plateThick)
                            self.model.sections.append(section2PL)
                else:
                    for plateThick in platesThick:
                        plateThick = int(plateThick.text())
                        if plateThick == 0:
                            self.model.sections.append(section2)
                        else:
                            for plateWidth in platesWidth:
                                plateWidth = int(plateWidth.text()) * 10
                                plate = sec.Plate(plateWidth, plateThick)
                                section2PL = sec.AddPlateTB(section2, plate)
                                self.model.sections.append(section2PL)
        self.model.reset()
        self.resizeColumns()
        self.model.dirty = True

    def acceptSave(self):
        #if (self.model.dirty and
        if QMessageBox.question(self, "sections - Save?",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try:
                sec.Sections.save(self.sectionsResults)
            except IOError, err:
                QMessageBox.warning(self, "sections - Error",
                        "Failed to save: {0}".format(err))
        QDialog.accept(self)

    def load(self):
        try:
            self.model.load()
        except IOError, err:
            QMessageBox.warning(self, "Sections - Error",
                    "Failed to load: {0}".format(err))

    def save(self):
        if (self.model.dirty and
            QMessageBox.question(self, "Section - Save?",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.model.save()
            except IOError, err:
                QMessageBox.warning(self, "Sections - Error",
                        "Failed to save: {0}".format(err))

    def saveToXml(self):
        fname = self.getXmlFilename()
        sec.Section.exportXml(fname, self.model.sections)

    def getLastSaveDirectory(self, f):
        f = str(f)
        return os.sep.join(f.split(os.sep)[:-1])

    def getXmlFilename(self):
        filters = "xml(*.xml)"
        filename = QFileDialog.getSaveFileName(self, u' xml خروجی به',
                                               self.lastDirectory, filters)
        filename = str(filename)
        if not filename.endswith('xml'):
            filename += '.xml'

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        #self.fileNameLine.setText(filename)
        return filename

    def exportToXml(self):
        if not self.dirty:
            QMessageBox.warning(self, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        filename = self.fileNameLine.text()
        if filename == '':
            return
        sec.Section.exportXml(filename, [self.section])

    def helpAbout(self):
        QMessageBox.about(self, u"درباره نرم افزار محاسبه مشخصات مقاطع",
                u"""<b>C Factor</b> v {0}   ۱۳۹۴/۱۰/۰۳
                <p>توسعه دهنده: ابراهیم رعیت رکن آبادی
                <p>این نرم افزار برای محاسبه مشخصات مقاطع برای استفاده در ایتبز ۲۰۱۳ و ۲۰۱۵ تهیه شده است.
                <p>از مهندسین عزیز خواهش میکنم با بررسی این برنامه ضعفها و ایرادات برنامه رو
                در وبلاگ من یادآوری کنند.
                <p>برای دریافت آخرین نسخه نرم افزار و مطالب مفید دیگر
                به وبلاگ زیر مراجعه نمایید:
                    <p> {1}""".format(__version__, link_ebrahim))


if __name__ == "__main__":

    app = QApplication(sys.argv)
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