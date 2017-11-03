# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
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


class Cfactor(QMainWindow):

    def __init__(self, filename=None, parent=None):
        super(Cfactor, self).__init__(parent)
        self.dirty = False
        self.lastDirectory = ''
        self.filename = filename
        self.html = ''
        self.printer = None
        self.create_widgets()
        self.final_building = self.current_building()
        self.structure_model = StructureModel(self.final_building)
        self.structure_properties_table.setModel(self.structure_model)
        #self.__userH = 200
        #self.setMaxAllowedHeight()
        self.create_connections()
        self.create_actions()
        # settings = QSettings()
        #self.load_settings()
        self.setWindowIcon(QIcon(":/icon.png"))
        # font = QFont()
        # font.setFamily("Tahoma")
        # if sys.platform.startswith('linux'):
        #     self.defaultPointsize = 10
        # else:
        #     self.defaultPointsize = 9
        # font.setPointSize(self.defaultPointsize)
        # self.setFont(font)
        # p = self.palette()
        # color = QColor()
        # color.setRgb(255, 255, 170)
        # p.setColor(self.backgroundRole(), color)
        # self.setPalette(p)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle("ضریب زلزله ویرایش چهارم ۲۸۰۰")
        #guirestore(self, settings)
        #self.updateFileMenu()
        #QTimer.singleShot(0, self.loadInitialFile)

    #def initialLoad(self):
        #if  QFile.exists(self.filename):
            #try:
                #self.load()
            #except IOError, err:
                #QMessageBox.warning(self, "Sections - Error",
                        #"Failed to load: {0}".format(err))

    def create_connections(self):
        self.soilType.currentIndexChanged.connect(self.accept)
        self.HSpinBox.valueChanged.connect(self.accept)
        ##self.connect(self.HSpinBox, SIGNAL(
                    ##"editingFinished()"), self.userInputHeight)
        self.xTAnalaticalSpinBox.valueChanged.connect(self.accept)
        self.yTAnalaticalSpinBox.valueChanged.connect(self.accept)
        self.infillCheckBox.stateChanged.connect(self.accept)
        self.tAnalaticalGroupBox.clicked.connect(self.accept)
        self.xSystemBox.currentIndexChanged.connect(self.insert_proper_lateral_resistance_systems_of_current_system_type_to_lateral_box)
        self.ySystemBox.currentIndexChanged.connect(self.insert_proper_lateral_resistance_systems_of_current_system_type_to_lateral_box)
        self.directionButtonGroup.buttonClicked.connect(self.setWidgetStack)
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

        # Label Widgets
        soil_type_label = QLabel("نوع خاک")
        height_label = QLabel('ارتفاع')
        height_label.setAlignment(Qt.AlignRight)
        story_label = QLabel('تعداد طبقات')
        story_label.setAlignment(Qt.AlignRight)
        analatical_period_x_label = QLabel('Tx<sub>an</sub>')
        analatical_period_y_label = QLabel('Ty<sub>an</sub>')
        system_label = QLabel('سیستم سازه')
        lateral_label = QLabel('سیستم مقاوم جانبی')
        ostan_label = QLabel("استان")
        shahr_label = QLabel("شهر")
        shahr_label.setAlignment(Qt.AlignRight)
        importance_factor_label = QLabel('ضریب اهمیت')

        # ComboBox Widgets
        self.soilType = QComboBox()
        self.soilType.addItems(['I', 'II', 'III', 'IV'])
        self.soilType.setCurrentIndex(2)
        self.soilType.setMaximumSize(90, 30)
        self.soilType.setObjectName('SOILTYPE')
        self.xSystemBox = QComboBox()
        self.xSystemBox.setFixedWidth(400)
        #self.xSystemBox.setObjectName('XSYSTEMBOX')
        self.xLateralBox = QComboBox()
        self.xLateralBox.setFixedWidth(400)
        #self.xLateralBox.setObjectName('XLATERALBOX')
        self.ySystemBox = QComboBox()
        self.ySystemBox.setFixedWidth(400)
        #self.ySystemBox.setObjectName('YSYSTEMBOX')
        self.yLateralBox = QComboBox()
        self.yLateralBox.setFixedWidth(400)
        #self.yLateralBox.setObjectName('YLATERALBOX')
        self.accText = QLineEdit()
        self.accText.setEnabled(False)
        #self.accText.setObjectName('ACCBOX')
        self.accText.setMaximumWidth(90)
        self.IBox = QComboBox()
        self.IBox.addItems(['0.8', '1.0', '1.2', '1.4'])
        self.IBox.setCurrentIndex(1)
        self.IBox.setMaximumWidth(90)
        self.IBox.setObjectName('IBOX')
        self.ostanBox = QComboBox()
        self.ostanBox.setObjectName('OSTANBOX')
        self.shahrBox = QComboBox()
        self.shahrBox.setObjectName('SHAHRBOX')
        ostans = ostanha.ostans.keys()
        #ostans.sort()
        self.ostanBox.addItems(ostans)
        self.set_shahrs_of_current_ostan()
        self.setA()

        for noesystem in systemTypes:
            self.xSystemBox.addItem(noesystem)
            self.ySystemBox.addItem(noesystem)

        # SpinBox Widgets
        self.HSpinBox = QDoubleSpinBox()
        self.HSpinBox.setMaximumSize(90, 30)
        self.HSpinBox.setSuffix(' متر')
        self.HSpinBox.setValue(10.0)
        self.HSpinBox.setMinimum(1)
        self.storySpinBox = QSpinBox()
        self.storySpinBox.setMaximumSize(90, 30)
        self.storySpinBox.setValue(3)
        self.storySpinBox.setRange(1, 100)
        self.xTAnalaticalSpinBox = QDoubleSpinBox()
        self.xTAnalaticalSpinBox.setDecimals(4)
        self.xTAnalaticalSpinBox.setMinimum(0.01)
        self.xTAnalaticalSpinBox.setSingleStep(0.05)
        self.xTAnalaticalSpinBox.setValue(0.56)
        self.xTAnalaticalSpinBox.setSuffix(' ثانیه')
        self.yTAnalaticalSpinBox = QDoubleSpinBox()
        self.yTAnalaticalSpinBox.setDecimals(4)
        self.yTAnalaticalSpinBox.setMinimum(0.01)
        self.yTAnalaticalSpinBox.setSingleStep(0.05)
        self.yTAnalaticalSpinBox.setValue(0.56)
        self.yTAnalaticalSpinBox.setSuffix(' ثانیه')

        # CheckBox Widgets
        self.infillCheckBox = QCheckBox('اثر میانقاب')
        self.infillCheckBox.setToolTip('فقط برای قابهای خمشی فعال می باشد.')

        # radio button widget
        directionGroupBox = QGroupBox('راستای نیروی مقاوم جانبی')
        font = QFont()
        font.setPointSize(12)
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
        self.tAnalaticalGroupBox = QGroupBox('زمان تناوب تحلیلی')
        self.tAnalaticalGroupBox.setCheckable(False)
        self.tAnalaticalGroupBox.setChecked(True)
        tAnalaticalLayout = QGridLayout()
        tAnalaticalLayout.addWidget(analatical_period_x_label, 0, 1)
        tAnalaticalLayout.addWidget(self.xTAnalaticalSpinBox, 0, 0)
        tAnalaticalLayout.addWidget(analatical_period_y_label, 1, 1)
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
        # curve widget
        self.curveBWidget = pl()
        self.curveBWidget.setMinimumSize(450, 300)

        self.structure_properties_table = QTableView()
        self.structure_properties_table.setLayoutDirection(Qt.LeftToRight)

        # soil properties table
        headers = ['soil', "T0", "Ts", "S", "S0", "B1", "N", "B"]
        self.soilPropertiesTable = QTableWidget(len(headers), 2)
        self.soilPropertiesTable.setAlternatingRowColors(True)
        self.soilPropertiesTable.setHorizontalHeaderLabels(["X", "Y"])
        self.soilPropertiesTable.setVerticalHeaderLabels(headers)
        for i in range(5):
            self.soilPropertiesTable.setSpan(i, 0, 1, 2)
        self.soilPropertiesTable.setLayoutDirection(Qt.LeftToRight)

        # LAYOUTS
        # main layout
        inputLayout = QGridLayout()
        inputLayout.addWidget(self.accText, 0, 4)
        inputLayout.addWidget(soil_type_label, 1, 0)
        inputLayout.addWidget(self.soilType, 1, 1)
        inputLayout.addWidget(importance_factor_label, 2, 0)
        inputLayout.addWidget(self.IBox, 2, 1)
        inputLayout.addWidget(ostan_label, 0, 0)
        inputLayout.addWidget(self.ostanBox, 0, 1)
        inputLayout.addWidget(shahr_label, 0, 2)
        inputLayout.addWidget(self.shahrBox, 0, 3)
        inputLayout.addWidget(height_label, 1, 2)
        inputLayout.addWidget(self.HSpinBox, 1, 3)
        inputLayout.addWidget(story_label, 2, 2)
        inputLayout.addWidget(self.storySpinBox, 2, 3)
        inputLayout.addWidget(self.infillCheckBox, 2, 4)
        inputLayout.setColumnStretch(2, 2)
        inputLayout.addWidget(directionGroupBox, 3, 0, 1, 3)
        inputLayout.addWidget(system_label, 4, 0)
        inputLayout.addWidget(lateral_label, 5, 0)
        inputLayout.addWidget(self.tAnalaticalGroupBox, 3, 3, 3, 2)

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

        inputGroupBox = QGroupBox('ورود داده ها')
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
        self.soilPropGroupBox = QGroupBox('مشخصات خاک')
        soilPropLayout = QVBoxLayout()
        soilPropLayout.addWidget(self.soilPropertiesTable)
        self.soilPropGroupBox.setLayout(soilPropLayout)
        #
        # structure properties group box
        self.structurePropGroupBox = QGroupBox('مشخصات سازه')
        structurePropLayout = QVBoxLayout()
        structurePropLayout.addWidget(self.structure_properties_table)
        self.structurePropGroupBox.setLayout(structurePropLayout)
        #
        # soil and structure properties splitter
        soilStrucPropertiesWidget = QWidget()
        soilStrucPropertiesLayout = QVBoxLayout()
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
        self.inputSplitter.setObjectName("InputSplitter2")
        self.mainSplitter.setObjectName("MainSplitter2")

        self.insert_proper_lateral_resistance_systems_of_current_system_type_to_lateral_box(self.xSystemBox, self.xLateralBox)
        self.insert_proper_lateral_resistance_systems_of_current_system_type_to_lateral_box(self.ySystemBox, self.yLateralBox)

        # TAB WIDGET
        self.tabWidget = QTabWidget()
        self.tabWidget.insertTab(0, self.mainSplitter, 'مشخصات ساختمان')
        #self.tabWidget.insertTab(2, self.rTableWidget, 'جدول ضریب رفتار')
        self.tabWidget.insertTab(1, self.textExport, 'word خروجی')

        #
        # central widget
        self.setCentralWidget(self.tabWidget)
        #
        # status bar
        self.statusbar = self.statusBar()

    def create_actions(self):
        # File Actions
        exportToPdfText = 'Pdf خروجی به'
        exportToWordText = 'Word خروجی به'
        exportToHtmlText = 'Html خروجی به'
        exportBCurveToImage = 'خروجی به تصویر'
        exportBCurveToCsv = 'خروجی به اکسل'

        filePdfAction = self.create_action(exportToPdfText, self.exportToPdf,
                QKeySequence.Print, "file_extension_pdf", exportToPdfText)
        fileOfficeAction = self.create_action(exportToWordText,
        self.exportToOffice, "Ctrl+W", "file_extension_doc", exportToWordText)
        fileHtmlAction = self.create_action(exportToHtmlText, self.exportToHtml,
                "Ctrl+H", "file_extension_html", exportToHtmlText)
        BCurveImageAction = self.create_action(exportBCurveToImage,
            self.exportBCurveToImage, "Ctrl+I", "file_extension_jpg")
        BCurveCsvAction = self.create_action(exportBCurveToCsv,
            self.exportBCurveToCsv, "Ctrl+X", "file_extension_xls")
        # Help Actions
        helpAboutAction = self.create_action("درباره نرم افزار",
                self.helpAbout, Qt.Key_F1)

        self.fileMenu = self.menuBar().addMenu('فایل')
        self.fileMenuActions = (filePdfAction, fileOfficeAction, fileHtmlAction)
        self.add_actions(self.fileMenu, self.fileMenuActions)
        fileToolbar = self.addToolBar("File")
        fileToolbar.setIconSize(QSize(32, 32))
        fileToolbar.setObjectName("FileToolBar")
        self.add_actions(fileToolbar, self.fileMenuActions)

        self.BCurveMenu = self.menuBar().addMenu("ضریب بازتاب")
        self.BCurveMenuActions = (BCurveImageAction, BCurveCsvAction)
        self.add_actions(self.BCurveMenu, self.BCurveMenuActions)
        BCurveToolbar = self.addToolBar("BCurve")
        BCurveToolbar.setIconSize(QSize(32, 32))
        BCurveToolbar.setObjectName("BCurveToolBar")
        self.add_actions(BCurveToolbar, self.BCurveMenuActions)

        helpMenu = self.menuBar().addMenu("راهنما")
        self.add_actions(helpMenu, (helpAboutAction, ))

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(
                settings.value("MainWindow/Geometry2").toByteArray())
        self.restoreState(settings.value("MainWindow/State2").toByteArray())
        self.inputSplitter.restoreState(settings.value("InputSplitter2").toByteArray())
        self.mainSplitter.restoreState(settings.value("MainSplitter2").toByteArray())

    def create_action(self, text, slot=None, shortcut=None, icon=None,
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

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

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

    def setWidgetStack(self):
        index = self.directionButtonGroup.checkedId() - 1
        self.stackedWidget.setCurrentIndex(index)

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

    def getDirectionProp(self):
        index = self.directionButtonGroup.checkedId() - 1
        if index == 0:
            systemBox = self.xSystemBox
            lateralBox = self.xLateralBox
        elif index == 1:
            systemBox = self.ySystemBox
            lateralBox = self.yLateralBox

        return systemBox, lateralBox

    def insert_proper_lateral_resistance_systems_of_current_system_type_to_lateral_box(
        self, systemBox=None, lateralBox=None):
        if (systemBox and lateralBox) is None:
            systemBox, lateralBox = self.getDirectionProp()
        systemType = systemBox.currentText()
        lateralTypes = rTable.getLateralTypes(systemType)
        #for i in lateralTypes:
        old_state = bool(lateralBox.blockSignals(True))
        lateralBox.clear()
        lateralBox.addItems(lateralTypes)
        lateralBox.blockSignals(old_state)

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

    def getA(self):
        return self.accText.text()

    def get_current_soil_type(self):
        return str(self.soilType.currentText())

    def set_default_values_of_analytical_period(self, build=None):
        if not build:
            build = self.current_building()
        exp_period_x = build.exp_period_x
        exp_period_y = build.exp_period_y
        #xTan = exp_period_x * 1.25
        #yTan = exp_period_y * 1.25
        self.xTAnalaticalSpinBox.setMinimum(exp_period_x)
        self.yTAnalaticalSpinBox.setMinimum(exp_period_y)
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
        risk_level = self.getA()
        city = self.get_current_shahr()
        height = self.getH()
        importance_factor = self.getI()
        soil = self.get_current_soil_type()
        noStory = self.getStory()
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
        is_infill = self.isInfill()
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
        self.set_default_values_of_analytical_period(self.final_building)
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
            self.html = self.final_building.__str__()
            self.dirty = True

        else:
            title, err, direction = results[1:]
            QMessageBox.critical(self, title % direction, err)
            return

    def showResult(self):
        #if self.tabWidget.currentIndex == 2:
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
    app.setWindowIcon(QIcon(":/icon.png"))
    window = Cfactor()
    p = window.palette()
    color = QColor()
    color.setRgb(255, 255, 170)
    p.setColor(window.backgroundRole(), color)
    window.setPalette(p)
    window.setLayoutDirection(Qt.RightToLeft)
    #window.setMaximumWidth(1000)
    window.show()
    app.exec_()
