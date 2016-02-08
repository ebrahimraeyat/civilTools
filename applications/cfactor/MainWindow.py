# -*- coding: utf-8 -*-
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebView
#from PyQt4 import QtSql
import qrc_resources
from db import db, ostanha
#import building
from building.build import *
import pyqtgraph as pg
import pyqtgraph.exporters
from plots.plotB import PlotB as pl
#import numpy as np

rTable = RFactorTable()
systemTypes = rTable.getSystemTypes()

__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "4.1"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)


class Cfactor(QMainWindow):

    def __init__(self, filename=QString(), parent=None):
        super(Cfactor, self).__init__(parent)
        self.dirty = False
        self.lastDirectory = ''
        self.filename = filename
        self.printer = None
        self.create_widgets()
        self.finalBuilding = self.currentBuilding()
        self.structureModel = StructureModel(self.finalBuilding)
        self.structurePropertiesTable.setModel(self.structureModel)
        #self.__userH = 200
        #self.setMaxAllowedHeight()
        self.create_connections()
        self.create_actions()
        self.accept()
        self.load_settings()
        self.setWindowIcon(QIcon(":/icon.png"))
        font = QFont()
        font.setFamily("Tahoma")
        if sys.platform.startswith('linux'):
            self.defaultPointsize = 10
        else:
            self.defaultPointsize = 9
        font.setPointSize(self.defaultPointsize)
        self.setFont(font)
        p = self.palette()
        color = QColor()
        color.setRgb(255, 255, 215)
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle(u"ضریب زلزله ویرایش چهارم ۲۸۰۰")
        #self.updateFileMenu()
        #QTimer.singleShot(0, self.loadInitialFile)

    def initialLoad(self):
        if  QFile.exists(self.filename):
            try:
                self.load()
            except IOError, err:
                QMessageBox.warning(self, "Sections - Error",
                        "Failed to load: {0}".format(err))

    def create_connections(self):
        self.connect(self.soilType, SIGNAL(
                    "currentIndexChanged(QString)"), self.accept)
        self.connect(self.HSpinBox, SIGNAL(
                    "valueChanged(double)"), self.accept)
        #self.connect(self.HSpinBox, SIGNAL(
                    #"editingFinished()"), self.userInputHeight)
        self.connect(self.xTAnalaticalSpinBox, SIGNAL(
                    "valueChanged(double)"), self.accept)
        self.connect(self.yTAnalaticalSpinBox, SIGNAL(
                    "valueChanged(double)"), self.accept)
        self.connect(self.infillCheckBox, SIGNAL(
                    "stateChanged(int)"), self.accept)
        self.connect(self.tAnalaticalGroupBox, SIGNAL(
                    "clicked()"), self.accept)
        self.connect(self.tAnalaticalGroupBox, SIGNAL(
                    "clicked()"), self.accept)
        self.connect(self.directionButtonGroup, SIGNAL(
                    "buttonClicked(int)"), self.setWidgetStack)
        self.connect(self.xLateralBox, SIGNAL(
                    "currentIndexChanged(QString)"), self.accept)
        self.connect(self.yLateralBox, SIGNAL(
                    "currentIndexChanged(QString)"), self.accept)
        self.connect(self.storySpinBox, SIGNAL(
                    "valueChanged(int)"), self.accept)
        self.connect(self.IBox, SIGNAL(
            "currentIndexChanged(QString)"), self.accept)
        self.connect(self.xSystemBox, SIGNAL(
                    "currentIndexChanged(QString)"), self.setLateralTypes)
        self.connect(self.ySystemBox, SIGNAL(
                    "currentIndexChanged(QString)"), self.setLateralTypes)
        self.connect(self.tabWidget, SIGNAL(
                    "currentChanged(int)"), self.showResult)
        self.connect(self.ostanBox, SIGNAL(
                "currentIndexChanged(QString)"), self.setShahrs)
        self.connect(self.shahrBox, SIGNAL(
                "currentIndexChanged(QString)"), self.setA)
        self.connect(self.shahrBox, SIGNAL(
                "currentIndexChanged(QString)"), self.accept)

    def load(self):
        exception = None
        fh = None
        try:
            if self.filename.isEmpty():
                raise IOError, "no filename specified for loading"
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError, unicode(fh.errorString())
            stream = QDataStream(fh)
            magic = stream.readInt32()
            if magic != MAGIC_NUMBER:
                raise IOError, "unrecognized file type"
            fileVersion = stream.readInt16()
            if fileVersion != FILE_VERSION:
                raise IOError, "unrecognized file type version"

            stream.writeInt16(build.noStory)
            stream.writeFloat(build.height)
            stream.writeFloat(build.xTan)
            stream.writeFloat(build.yTan)
            risk = QString()
            soilType = QString()
            infill = QString()
            xSystem = QString()
            ySystem = QString()
            city = QString()
            useTan = QString()
            stream >> risk >> soilType >> infill
            stream >> xSystem >> ySystem >> city >> useTan
            karbari = stream.readFloat()
            noStory = stream.readInt16()
            height = stream.readFloat()
            xTan = stream.readFloat()
            yTan = stream.readFloat()
            self.build = Building(risk, karbari, soilType, noStory, height,
                 infill, xSystem, ySystem, city, xTan, yTan, useTan)
            self.systems.append(xSystem)
            self.systems.append(ySystem)
            self.dirty = False
        except IOError, err:
            exception = err
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


    def save(self):
        exception = None
        fh = None
        try:
            if self.filename.isEmpty():
                raise IOError, "no filename specified for saving"
            fh = QFile(self.filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError, unicode(fh.errorString())
            stream = QDataStream(fh)
            stream.writeInt32(MAGIC_NUMBER)
            stream.writeInt16(FILE_VERSION)
            stream.setVersion(QDataStream.Qt_4_7)
            stream << build.risk << build.soilType << build.infill
            stream << build.xSystem << build.ySystem << build.city << build.useTan
            stream.writeFloat(build.karbari)
            stream.writeInt16(build.noStory)
            stream.writeFloat(build.height)
            stream.writeFloat(build.xTan)
            stream.writeFloat(build.yTan)
            self.dirty = False
        except IOError, err:
            exception = err
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception

    def resizeColumns(self):
        for column in (X, Y):
            self.structurePropertiesTable.resizeColumnToContents(column)

    def create_widgets(self):

        # Label Widgets
        noeZaminLabel = QLabel(u"نوع خاک")
        HLabel = QLabel(u'ارتفاع')
        HLabel.setAlignment(Qt.AlignRight)
        storyLabel = QLabel(u'تعداد طبقات')
        storyLabel.setAlignment(Qt.AlignRight)
        xTAnalaticalLabel = QLabel('Tx<sub>an</sub>')
        yTAnalaticalLabel = QLabel('Ty<sub>an</sub>')
        systemLabel = QLabel(u'سیستم سازه')
        lateralLabel = QLabel(u'سیستم مقاوم جانبی')
        #accLabel = QLabel(u"شتاب مبنای طرح")
        ostanLabel = QLabel(u"استان")
        shahrLabel = QLabel(u"شهر")
        #ostanLabel.setAlignment(Qt.AlignRight)
        shahrLabel.setAlignment(Qt.AlignRight)
        ILabel = QLabel(u'ضریب اهمیت')
        self.resultX = QLabel()
        self.resultY = QLabel()

        # ComboBox Widgets
        self.soilType = QComboBox()
        self.soilType.addItems(['I', 'II', 'III', 'IV'])
        self.soilType.setCurrentIndex(2)
        self.soilType.setMaximumSize(90, 30)
        self.xSystemBox = QComboBox()
        self.xSystemBox.setFixedWidth(400)
        self.xLateralBox = QComboBox()
        self.xLateralBox.setFixedWidth(400)
        self.ySystemBox = QComboBox()
        self.ySystemBox.setFixedWidth(400)
        self.yLateralBox = QComboBox()
        self.yLateralBox.setFixedWidth(400)
        self.accText = QLineEdit()
        self.accText.setEnabled(False)
        self.accText.setMaximumWidth(90)
        self.IBox = QComboBox()
        self.IBox.addItems(['0.8', '1.0', '1.2', '1.4'])
        self.IBox.setCurrentIndex(1)
        self.IBox.setMaximumWidth(90)
        self.ostanBox = QComboBox()
        self.shahrBox = QComboBox()
        ostans = ostanha.ostans.keys()
        ostans.sort()
        self.ostanBox.addItems(ostans)
        self.setShahrs()
        self.setA()

        for noesystem in systemTypes:
            self.xSystemBox.addItem(noesystem)
            self.ySystemBox.addItem(noesystem)

        # SpinBox Widgets
        self.HSpinBox = QDoubleSpinBox()
        self.HSpinBox.setMaximumSize(90, 30)
        self.HSpinBox.setSuffix(u' متر')
        self.HSpinBox.setValue(10.0)
        self.HSpinBox.setMinimum(1)
        self.storySpinBox = QSpinBox()
        self.storySpinBox.setMaximumSize(90, 30)
        self.storySpinBox.setValue(3)
        self.storySpinBox.setRange(1, 100)
        self.xTAnalaticalSpinBox = QDoubleSpinBox()
        self.xTAnalaticalSpinBox.setMinimum(0.01)
        self.xTAnalaticalSpinBox.setSingleStep(0.05)
        self.xTAnalaticalSpinBox.setValue(0.56)
        self.xTAnalaticalSpinBox.setSuffix(u' ثانیه')
        self.yTAnalaticalSpinBox = QDoubleSpinBox()
        self.yTAnalaticalSpinBox.setMinimum(0.01)
        self.yTAnalaticalSpinBox.setSingleStep(0.05)
        self.yTAnalaticalSpinBox.setValue(0.56)
        self.yTAnalaticalSpinBox.setSuffix(u' ثانیه')

        # CheckBox Widgets
        self.infillCheckBox = QCheckBox(u'اثر میانقاب')
        self.infillCheckBox.setToolTip(u'فقط برای قابهای خمشی فعال می باشد.')
        self.tAnalaticalCheckBox = QCheckBox()

        # radio button widget
        directionGroupBox = QGroupBox(u'راستای نیروی مقاوم جانبی')
        font = QFont()
        font.setPointSize(13)
        directionGroupBox.setFont(font)
        self.directionButtonGroup = QButtonGroup()
        xDir = QRadioButton('X')
        yDir = QRadioButton('Y')
        xDir.setChecked(True)
        self.directionButtonGroup.addButton(xDir, 1)
        self.directionButtonGroup.addButton(yDir, 2)
        directionLayout = QHBoxLayout()
        directionLayout.addWidget(xDir)
        directionLayout.addWidget(yDir)
        directionWidget = QWidget()
        directionWidget.setLayout(directionLayout)
        dirGroupBoxLayout = QVBoxLayout()
        dirGroupBoxLayout.addWidget(directionWidget)
        directionGroupBox.setLayout(dirGroupBoxLayout)

        # Group Box Widgets
        self.tAnalaticalGroupBox = QGroupBox(u'زمان تناوب تحلیلی')
        self.tAnalaticalGroupBox.setCheckable(True)
        self.tAnalaticalGroupBox.setChecked(False)
        tAnalaticalLayout = QGridLayout()
        tAnalaticalLayout.addWidget(xTAnalaticalLabel, 0, 1)
        tAnalaticalLayout.addWidget(self.xTAnalaticalSpinBox, 0, 0)
        tAnalaticalLayout.addWidget(yTAnalaticalLabel, 1, 1)
        tAnalaticalLayout.addWidget(self.yTAnalaticalSpinBox, 1, 0)
        self.tAnalaticalGroupBox.setLayout(tAnalaticalLayout)

        # TextBrowser Widgets
        font = QFont()
        font.setPointSize(20)
        #align = Qt.Alignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.browser = QTextEdit()
        self.browser.setReadOnly(True)
        self.browser.setFont(font)
        self.browser.setMinimumWidth(180)
        #self.browser.setStyleSheet("font: 75 24pt \"B Nazanin\";\n"
#"alternate-background-color: rgb(255, 0, 255);\n")
#"background-color: rgb(85, 170, 127);\n")
        #
        # view result in text export format
        self.textExport = QTextEdit()
        self.textExport.setReadOnly(True)
        #
        # TABLE WIDGET
        self.rTableWidget = db.storeWindow()
        #self.rTableWidget.setStyleSheet("font: 75 12pt \"B Nazanin\";\n")
        #self.mapper = QDataWidgetMapper(self)
        #self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        #self.mapper.setModel(self.rTableWidget.model)
        #self.mapper.addMapping(self.systemBox, SYSTEM)
        #self.mapper.addMapping(self.lateralBox, LATERAL)
        #self.mapper.toFirst()
        #self.rTableWidget.setFixedHeight(300)

        #
        # curve widget
        self.curveBWidget = pl()
        self.curveBWidget.setMinimumSize(450, 300)

        # structure properties table
        headers = ['system', 'lateral', "Hmax", u'Ru', u"\u2126 0",
                    "Cd", "Texp", "1.25*Texp", "Tan", "K"]
        self.structurePropertiesTable = QTableView()
        #self.structurePropertiesTable = QTableWidget(len(headers), 2)
        #self.structurePropertiesTable.setAlternatingRowColors(True)
        #self.structurePropertiesTable.setHorizontalHeaderLabels(["X", "Y"])

        #self.structurePropertiesTable.setVerticalHeaderLabels(headers)
        #self.structurePropertiesTable.resizeColumnsToContents()
        self.structurePropertiesTable.setLayoutDirection(Qt.LeftToRight)

        # soil properties table
        headers = [u'soil', "T0", "Ts", "S", "S0", "B1", "N", "B"]
        self.soilPropertiesTable = QTableWidget(len(headers), 2)
        self.soilPropertiesTable.setAlternatingRowColors(True)
        self.soilPropertiesTable.setHorizontalHeaderLabels(["X", "Y"])
        self.soilPropertiesTable.setVerticalHeaderLabels(headers)
        for i in range(5):
            self.soilPropertiesTable.setSpan(i, 0, 1, 2)
        #self.soilPropertiesTable.resizeColumnsToContents()
        self.soilPropertiesTable.setLayoutDirection(Qt.LeftToRight)

        # LAYOUTS
        # main layout
        inputLayout = QGridLayout()
        inputLayout.addWidget(self.accText, 0, 4)
        inputLayout.addWidget(noeZaminLabel, 1, 0)
        inputLayout.addWidget(self.soilType, 1, 1)
        inputLayout.addWidget(ILabel, 2, 0)
        inputLayout.addWidget(self.IBox, 2, 1)
        inputLayout.addWidget(ostanLabel, 0, 0)
        inputLayout.addWidget(self.ostanBox, 0, 1)
        inputLayout.addWidget(shahrLabel, 0, 2)
        inputLayout.addWidget(self.shahrBox, 0, 3)
        inputLayout.addWidget(HLabel, 1, 2)
        inputLayout.addWidget(self.HSpinBox, 1, 3)
        inputLayout.addWidget(storyLabel, 2, 2)
        inputLayout.addWidget(self.storySpinBox, 2, 3)
        inputLayout.addWidget(self.infillCheckBox, 2, 4)
        inputLayout.setColumnStretch(2, 2)
        inputLayout.addWidget(directionGroupBox, 3, 0, 1, 3)
        inputLayout.addWidget(systemLabel, 4, 0)
        inputLayout.addWidget(lateralLabel, 5, 0)
        inputLayout.addWidget(self.tAnalaticalGroupBox, 3, 3, 3, 2)
        #inputLayout.addWidget(self.browser, 0, 5, 6, 1)

        # stacked widget
        self.stackedWidget = QStackedWidget()
        xDirWidget = QWidget()
        xDirLayout = QVBoxLayout()
        xDirLayout.addWidget(self.xSystemBox)
        xDirLayout.addWidget(self.xLateralBox)
        xDirWidget.setLayout(xDirLayout)
        self.stackedWidget.addWidget(xDirWidget)

        yDirWidget = QWidget()
        yDirLayout = QVBoxLayout()
        yDirLayout.addWidget(self.ySystemBox)
        yDirLayout.addWidget(self.yLateralBox)
        yDirWidget.setLayout(yDirLayout)
        self.stackedWidget.addWidget(yDirWidget)
        inputLayout.addWidget(self.stackedWidget, 4, 1, 2, 2)

        inputGroupBox = QGroupBox(u'ورود داده ها')
        #p = inputGroupBox.palette()
        #color = QColor()
        #color.setRgb(219, 236, 62)
        #p.setColor(inputGroupBox.backgroundRole(), color)
        #inputGroupBox.setPalette(p)
        #inputGroupBox.setBackgroundRole(QPalette.Button)
        #font = QFont()
        ##font.setBold(True)
        #font.setPointSize(13)
        #inputGroupBox.setFont(font)
        #inputGroupBox.setMaximumHeight(200)
        inputWidget = QWidget()
        inputWidget.autoFillBackground()
        inputWidget.setLayout(inputLayout)
        #inputGroupBox.setLayout(inputLayout)
        #inputGroupBox.addWidget(inputWidget)
        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(inputWidget)
        inputGroupBox.setLayout(groupBoxLayout)
        fontWidget = QFont()
        fontWidget.setBold(False)
        #fontWidget.setPointSize(self.defaultPointsize)
        #inputWidget.setFont(fontWidget)
        #
        # soil properties group box
        self.soilPropGroupBox = QGroupBox(u'مشخصات خاک')
        soilPropLayout = QVBoxLayout()
        soilPropLayout.addWidget(self.soilPropertiesTable)
        self.soilPropGroupBox.setLayout(soilPropLayout)
        #
        # structure properties group box
        self.structurePropGroupBox = QGroupBox(u'مشخصات سازه')
        structurePropLayout = QVBoxLayout()
        structurePropLayout.addWidget(self.structurePropertiesTable)
        self.structurePropGroupBox.setLayout(structurePropLayout)
        #
        # soil and structure properties splitter
        soilStrucPropertiesWidget = QWidget()
        soilStrucPropertiesLayout = QVBoxLayout()
        soilStrucPropertiesLayout.addWidget(self.resultX)
        soilStrucPropertiesLayout.addWidget(self.resultY)
        soilStrucPropertiesLayout.addWidget(self.structurePropGroupBox)
        soilStrucPropertiesLayout.addWidget(self.soilPropGroupBox)
        soilStrucPropertiesWidget.setLayout(soilStrucPropertiesLayout)

        #
        # splittters widget
        self.inputSplitter = QSplitter(Qt.Vertical)
        self.inputSplitter.addWidget(inputGroupBox)
        self.inputSplitter.addWidget(self.curveBWidget)
        self.mainSplitter = QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.inputSplitter)
        self.mainSplitter.addWidget(soilStrucPropertiesWidget)
        self.inputSplitter.setObjectName("InputSplitter")
        self.mainSplitter.setObjectName("MainSplitter")

        #mainLayout = QGridLayout()
        #mainLayout.addWidget(inputGroupBox, 0, 0)
        #mainLayout.addWidget(self.soilPropGroupBox, 0, 1)
        #mainLayout.addItem(outputLayout, 0, 2)
        #mainLayout.addWidget(self.curveBWidget, 1, 0)
        #mainLayout.addWidget(self.structurePropGroupBox, 1, 1, 1, 2)

        self.setLateralTypes(self.xSystemBox, self.xLateralBox)
        self.setLateralTypes(self.ySystemBox, self.yLateralBox)

        # TAB WIDGET
        #CFactorWidget = QWidget()
        #CFactorWidget.setLayout(mainLayout)
        self.tabWidget = QTabWidget()
        #self.tabWidget.setTabPosition(QTabWidget.East)
        self.tabWidget.insertTab(0, self.mainSplitter, u'مشخصات ساختمان')
        self.tabWidget.insertTab(1, self.rTableWidget, u'جدول ضریب رفتار')
        self.tabWidget.insertTab(2, self.textExport, u'خروجی word')

        #
        # central widget
        self.setCentralWidget(self.tabWidget)
        #
        # status bar
        self.statusbar = self.statusBar()

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
        settings.setValue("MainWindow/Geometry", QVariant(self.saveGeometry()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))
        settings.setValue("InputSplitter", QVariant(self.inputSplitter.saveState()))
        settings.setValue("MainSplitter", QVariant(self.mainSplitter.saveState()))

    def setWidgetStack(self):
        index = self.directionButtonGroup.checkedId() - 1
        self.stackedWidget.setCurrentIndex(index)

    def helpAbout(self):
        QMessageBox.about(self, u"درباره نرم افزار محاسبه ضریب زلزله",
                u"""<b>C Factor</b> v {0}   ۱۳۹۴/۰۸/۱۸
                <p>توسعه دهنده: ابراهیم رعیت رکن آبادی
                <p>این نرم افزار برای محاسبه ضریب زلزله مطابق ویرایش چهارم
                آیین نامه ۲۸۰۰ زلزله تهیه شده است.
                <p>از مهندسین عزیز خواهش میکنم با بررسی این برنامه ضعفها و ایرادات برنامه رو
                در وبلاگ من یادآوری کنند.
                <p>برای دریافت آخرین نسخه نرم افزار و مطالب مفید دیگر
                به وبلاگ زیر مراجعه نمایید:
                    <p> {1}""".format(__version__, link_ebrahim))

    def getDirectionProp(self):
        index = self.directionButtonGroup.checkedId() - 1
        if index == 0:
            systemBox = self.xSystemBox
            lateralBox = self.xLateralBox
        elif index == 1:
            systemBox = self.ySystemBox
            lateralBox = self.yLateralBox

        return systemBox, lateralBox

    def setLateralTypes(self, systemBox=None, lateralBox=None):
        if (systemBox and lateralBox) is None:
            systemBox, lateralBox = self.getDirectionProp()
        lateralBox.clear()
        systemType = unicode(systemBox.currentText())
        lateralTypes = rTable.getLateralTypes(systemType)
        for i in lateralTypes:
            lateralBox.addItem(i)

    def getSystemType(self, systemBox):
        return unicode(systemBox.currentText())

    def getLateralType(self, lateralBox):
        return unicode(lateralBox.currentText())

    def getOstan(self):
        return unicode(self.ostanBox.currentText())

    def getShahr(self):
        ostan = self.getOstan()
        shahr = unicode(self.shahrBox.currentText())
        return '%s, %s' % (shahr, ostan)

    def getShahrs(self, ostan):
        '''return shahrs of ostan'''
        return ostanha.ostans[ostan].keys()

    def setShahrs(self):
        self.shahrBox.clear()
        ostan = unicode(self.ostanBox.currentText())
        shahrs = self.getShahrs(ostan)
        shahrs.sort()
        self.shahrBox.addItems(shahrs)

    def setA(self):
        sotoh = [u'خیلی زیاد', u'زیاد', u'متوسط', u'کم']
        ostan = unicode(self.ostanBox.currentText())
        shahr = unicode(self.shahrBox.currentText())
        A = ostanha.ostans[ostan][shahr][0]
        self.accText.setText(sotoh[A - 1])

    def getA(self):
        return unicode(self.accText.text())

    def getSoilType(self):
        return str(self.soilType.currentText())

    def setTAnalaticalDefaultValue(self, build=None):
        if not build:
            build = self.currentBuilding()
        xTexp = build.xTexp
        yTexp = build.yTexp
        #xTan = xTexp * 1.25
        #yTan = yTexp * 1.25
        self.xTAnalaticalSpinBox.setMinimum(xTexp)
        self.yTAnalaticalSpinBox.setMinimum(yTexp)
        #self.xTAnalaticalSpinBox.setValue(xTan)
        #self.yTAnalaticalSpinBox.setValue(yTan)

    def getH(self):
        return self.HSpinBox.value()

    def getStory(self):
        return self.storySpinBox.value()

    def getI(self):
        return float(self.IBox.currentText())

    def isInfill(self):
        return self.infillCheckBox.isChecked()

    def setStructureProp(self, build):
        xSystem = build.xSystem
        ySystem = build.ySystem
        xSystemProp = [xSystem.systemType, xSystem.lateralType, xSystem.maxHeight, xSystem.Ru,
                       xSystem.phi0, xSystem.cd, build.xTexp, 1.25 * build.xTexp, build.xTan, build.kx]
        ySystemProp = [ySystem.systemType, ySystem.lateralType, ySystem.maxHeight, ySystem.Ru,
                       ySystem.phi0, ySystem.cd, build.yTexp, 1.25 * build.yTexp, build.yTan, build.ky]
        for row, item in enumerate(xSystemProp):
            if row < 3:
                item = QTableWidgetItem("%s " % item)
            else:
                item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.structurePropertiesTable.setItem(row, 0, item)

        for row, item in enumerate(ySystemProp):
            if row < 3:
                item = QTableWidgetItem("%s " % item)
            else:
                item = QTableWidgetItem("%.2f " % item)
            item.setTextAlignment(Qt.AlignCenter)
            self.structurePropertiesTable.setItem(row, 1, item)

        #xK, yK = xSystem.K, ySystem.k

    #def setDEngheta(self):
        #dEngheta = self.getDEngheta()
        #if dEngheta:
            #self.dEnghetaLineEdit.setText("%.1f Cm" % dEngheta)
        #else:
            #self.dEnghetaLineEdit.setText(u"مراجعه به بند ۳-۵-۶")

    def setInfillCheckBoxStatus(self, xSystem, ySystem):
        infill = xSystem.infill and ySystem.infill
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
            build = self.currentBuilding()
        xrf = build.xReflectionFactor
        yrf = build.yReflectionFactor
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
        self.p.setTitle(u'منحنی ضریب بازتاب، خاک نوع {0}، پهنه با خطر نسبی {1}'.format(
                            build.soilType, build.risk))
        penB1 = pg.mkPen('r', width=2, style=Qt.DashLine)
        penN = pg.mkPen('g', width=2)
        penB = pg.mkPen('b', width=3)
        penTx = pg.mkPen((153, 0, 153), width=1, style=Qt.DashDotLine)
        penTy = pg.mkPen((153, 0, 0), width=1, style=Qt.DashDotDotLine)
        dt = build.xReflectionFactor.dt
        B1 = build.xReflectionFactor.b1Curve
        N = build.xReflectionFactor.nCurve
        B = build.xReflectionFactor.bCurve
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

    def currentBuilding(self):
        risk = self.getA()
        city = self.getShahr()
        height = self.getH()
        karbari = self.getI()
        soil = self.getSoilType()
        noStory = self.getStory()
        xSystemType = self.getSystemType(self.xSystemBox)
        xLateralType = self.getLateralType(self.xLateralBox)
        ySystemType = self.getSystemType(self.ySystemBox)
        yLateralType = self.getLateralType(self.yLateralBox)
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
        isInfill = self.isInfill()
        build = Building(risk, karbari, soil, noStory, height, isInfill,
                              xSystem, ySystem, city, xTan, yTan, useTan)
        return build

    def reject(self):
        if (self.dirty and
            QMessageBox.question(self, "structure - Save?",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.save()
            except IOError, err:
                QMessageBox.warning(self, "structure - Error",
                        "Failed to save: {0}".format(err))
        QDialog.accept(self)

    def accept(self):
        self.dirty = False
        self.html = ''
        self.finalBuilding = self.currentBuilding()
        self.setSoilProperties(self.finalBuilding)
        self.structureModel.build = self.finalBuilding
        self.structureModel.reset()
        self.resizeColumns()
        #self.setStructureProp(self.finalBuilding)
        self.setTAnalaticalDefaultValue(self.finalBuilding)
        results = self.finalBuilding.results
        if results[0] is True:
            Cx, Cy = results[1], results[2]
            resultStrx = '<font size=24 color=blue>C<sub>x</sub> = %.4f </font>' % Cx
            resultStry = '<font size=24 color=blue>C<sub>y</sub> = %.4f </font>' % Cy
            self.resultX.setText(resultStrx)
            self.resultY.setText(resultStry)
            self.updateBCurve(self.finalBuilding)
            self.html = self.finalBuilding.__str__()
            self.dirty = True

        else:
            self.resultX.setText("")
            self.resultY.setText("")
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, unicode(err))
            return

    def showResult(self):
        #if self.tabWidget.currentIndex == 2:
        self.textExport.setHtml(self.html)

    def getLastSaveDirectory(self, f):
        f = str(f)
        return os.sep.join(f.split(os.sep)[:-1])

    def exportToPdf(self):

        if not self.dirty:
            QMessageBox.warning(self, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد.')
            return

        filters = "pdf(*.pdf)"
        filename = QFileDialog.getSaveFileName(self, u' Pdf خروجی به',
                                               self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)
        printer.setResolution(300)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        web = QWebView()
        web.setHtml(self.html)
        web.print_(printer)

    def exportToOffice(self):
        if not self.dirty:
            QMessageBox.warning(self, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        html = self.html
        html = html.encode('utf-8')
        filters = "doc(*.doc);;odt(*.odt)"
        filename = QFileDialog.getSaveFileName(self, u'OpenOffice & Word خروجی به',
                                               self.lastDirectory, filters)
        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        fileSave = QFile(filename)
        fileSave.open(QIODevice.WriteOnly)
        fileSave.writeData(html)
        fileSave.close()

    def exportToHtml(self):
        if not self.dirty:
            QMessageBox.warning(self, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        html = self.html
        html = html.encode('utf-8')
        filters = "html(*.html)"
        filename = QFileDialog.getSaveFileName(self, u' Html خروجی به',
                                               self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        fileSave = QFile(filename)
        fileSave.open(QIODevice.WriteOnly)
        fileSave.writeData(html)
        fileSave.close()

    def exportBCurveToImage(self):
        filters = "png(*.png);;jpg(*.jpg);;bmp(*.bmp);;eps(*.eps);;tif(*.tif);;jpeg(*.jpeg)"
        filename = QFileDialog.getSaveFileName(self, u'خروجی منحنی ضریب بازتاب',
                                               self.lastDirectory, filters)
        #filename = '1.odt'

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        exporter = pg.exporters.ImageExporter(self.p)
        # set export parameters if needed
        exporter.parameters()['width'] = 1920   # (note this also affects height parameter)
        #exporter.parameters()['height'] = 600
        # save to file
        exporter.export(filename)

    def exportBCurveToCsv(self):
        filters = "csv(*.csv)"
        filename = QFileDialog.getSaveFileName(self, u'خروجی منحنی ضریب بازتاب',
                                               self.lastDirectory, filters)
        #filename = '1.odt'

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        exporter = pg.exporters.CSVExporter(self.p)
        # set export parameters if needed
        #exporter.parameters()['width'] = 100   # (note this also affects height parameter)
        # save to file
        exporter.export(filename)

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
    app.setApplicationName("C Factor")
    app.setWindowIcon(QIcon(":/icon.png"))
    window = Cfactor()
    p = window.palette()
    color = QColor()
    color.setRgb(255, 255, 215)
    p.setColor(window.backgroundRole(), color)
    window.setPalette(p)
    window.setLayoutDirection(Qt.RightToLeft)
    #window.setMaximumWidth(1000)
    window.show()
    app.exec_()
