# -*- coding: utf-8 -*-

#import re
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#import qrc_resources
from .plot.plot_record import *
import pandas as pd
#from pandas.tools.plotting import table
##matplotlib.use("Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')


__url__ = "http://ebrahimraeyat.blog.ir"
__version__ = "0.1"
link_ebrahim = ('Website: <a href="%s"><span style=" '
    'text-decoration: underline; color:#0000ff;">'
    '%s</span></a>') % (__url__, __url__)


class Record(QMainWindow):

    def __init__(self, parent=None):
        super(Record, self).__init__(parent)
        self.dirty = False
        self.lastDirectory = ''
        self.filename = None
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.createWidgets()
        self.updateSectionShape()
        self.create_connections()
        #self.create_actions()
        #self.accept()
        #self.load_settings()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle('کار با رکوردهای زلزله')
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

    #def resizeColumns(self, tableView=None):
        #for column in (sec.NAME, sec.AREA,
                       #sec.ASY, sec.ASX, sec.IX, sec.IY, sec.ZX, sec.ZY,
                         #sec.BF, sec.TF, sec.D, sec.TW, sec.Sx, sec.Sy, sec.RX, sec.RY):
            #tableView.resizeColumnToContents(column)

    #def reject(self):
        #self.accept()

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

    #def sortTable(self, section):
        #if section == sec.AREA:
            #self.model1.sortByArea()
        ##self.model.sortByName();
        #self.resizeColumns(self.tableView1)

    #def addSection(self):
        #row = self.model1.rowCount()
        #self.model1.insertRows(row)
        #index = self.model1.index(row, 1)
        #self.tableView1.setCurrentIndex(index)
        #self.tableView1.edit(index)

    #def removeSection(self):
        #index = self.tableView1.currentIndex()
        #if not index.isValid():
            #return
        #row = index.row()
        #name = self.model1.data(
                        #self.model1.index(row, sec.NAME)).toString()
        #if (QMessageBox.question(self, "sections - Remove",
                #(QString("Remove section {}?".format(name))),
                #QMessageBox.Yes|QMessageBox.No) ==
                #QMessageBox.No):
            #return
        ##print 'indexes is:{}'.format(indexes)
        ##print 'len indexes is{}'.format(len(indexes))
        ##for i in range(len(indexes)):

        #self.model1.removeRows(row)
        #self.resizeColumns(self.tableView1)

    def create_connections(self):
        pass
        #self.connect(self.sectionsBox, SIGNAL(
                    #"currentIndexChanged(QString)"), self.accept)
        #self.connect(self.sectionTypeBox1, SIGNAL(
                    #"currentIndexChanged(QString)"), self.setSectionLabels)
        #self.connect(self.sectionTypeBox1, SIGNAL(
                    #"currentIndexChanged(QString)"), self.updateGui)
        #self.connect(self.lhSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.thSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.lwSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.twSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.lvSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.tvSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.distSpinBox, SIGNAL(
                #"valueChanged(int)"), self.updateSectionShape)
        #self.connect(self.addTBPLGroupBox, SIGNAL(
                #"clicked()"), self.updateSectionShape)
        #self.connect(self.addLRPLGroupBox, SIGNAL(
                #"clicked()"), self.updateSectionShape)
        #self.connect(self.addWebPLGroupBox, SIGNAL(
                #"toggled(bool)"), self.updateSectionShape)
        #self.connect(self.sectionsBox, SIGNAL(
                #"currentIndexChanged(int)"), self.updateSectionShape)
        #self.connect(self.doubleBox, SIGNAL(
                #"currentIndexChanged(int)"), self.updateSectionShape)
        #self.connect(self.ductilityBox, SIGNAL(
                #"currentIndexChanged(int)"), self.updateSectionShape)
        #self.connect(self.useAsBox, SIGNAL(
                #"currentIndexChanged(int)"), self.updateSectionShape)
        #self.connect(self.tableView1.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sortTable)

    def createWidgets(self):
        #self.model1 = sec.SectionTableModel(QString("section.dat"))
        #self.tableView1 = QTableView()
        #self.tableView1.setLayoutDirection(Qt.LeftToRight)
        #self.tableView1.setModel(self.model1)

        main_widget = QWidget()
        load_record_button = Record.create_pushButton_icon('بارگذاری شتابنگاشت', ":/main_resources/icons/main/load.png")
        load_record_button.clicked.connect(self.load_record)
        run_button = Record.create_pushButton_icon('ترسیم', ":/main_resources/icons/main/load.png")
        run_button.clicked.connect(self.updateSectionShape)
        self.info_text_browser = QTextBrowser()
        self.info_text_browser.setFixedWidth(200)
        #self.dx_spinbox = QDoubleSpinBox()
        #self.dx_spinBox.setRange(.001, .5)

        buttons_layout = QVBoxLayout()
        self.drawLayout = QGridLayout()
        buttons_layout.addWidget(load_record_button)
        buttons_layout.addWidget(run_button)
        buttons_layout.addWidget(self.info_text_browser)
        buttons_layout.addStretch()
        self.drawLayout.addLayout(buttons_layout, 0, 0)
        self.drawLayout.addWidget(self.canvas, 0, 1)

        main_widget.setLayout(self.drawLayout)
        self.setCentralWidget(main_widget)

        ## splittters widget
        ##self.inputSplitter = QSplitter(Qt.Horizontal)
        ##self.inputSplitter.addWidget(inputWidget)
        ##self.inputSplitter.addWidget(pushButtonFrame)
        ##self.mainSplitter = QSplitter(Qt.Vertical)
        ##self.mainSplitter.addWidget(inputWidget)
        ##self.mainSplitter.addWidget(self.tableView1)
        ###self.inputSplitter.setObjectName = 'InputSplitter'
        ##self.mainSplitter.setObjectName = 'MainSplitter1'

    @staticmethod
    def create_pushButton_icon(text, icon_address):
        #icon = QIcon(icon_address)
        #button = QPushButton(icon, text)
        button = QPushButton(text)
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(size_policy)
        btn_size = QSize(120, 60)
        #icon_size = QSize(60, 60)
        button.setMinimumSize(btn_size)
        #button.setIconSize(icon_size)
        return button

    @staticmethod
    def creatList(listItems):
        _list = QListWidget()
        _list.addItems(listItems)
        _list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        return _list

    def updateSectionShape(self):
        plt.clf()
        if self.filename:
            ax = self.figure.add_subplot(311)
            plotWidget = Work_on_record_file(self.filename, .005)
            plotWidget.acc.plot(title='Acceleration', ax=ax, legend=None)
            ax = self.figure.add_subplot(312)
            plotWidget.density_function.plot(title='density function', ax=ax, kind='bar', legend=None)
            ax = self.figure.add_subplot(313)
            #table(ax, sr_info, loc='center right', fontsize=30, colWidths=[0.1])
            plotWidget.distribute_function.plot(title='distribute function', ax=ax, legend=None)
            self.canvas.draw()

            sr_info = pd.Series(plotWidget.return_dict)
            html = ''
            for key, value in sr_info.iteritems():
                html += '<p>{}: {}</p>\n'.format(key, value)
            self.info_text_browser.setHtml(html)

    def getLastSaveDirectory(self, f):
        #f = unicode(f)
        return os.sep.join(f.split(os.sep)[:-1])

    def getFilename(self, prefixes):
        filters = ''
        for prefix in prefixes:
            filters += "{}(*.{})".format(prefix, prefix)
        filename = QFileDialog.getSaveFileName(self, ' خروجی ',
                                               self.lastDirectory, filters)
        #filename = unicode(filename)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        return filename

    def load_record(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'بارگذاری شتابنگاشت',
                                               self.lastDirectory, "AT2 (*.AT2)")
        #filename = unicode(filename)

        if filename == '':
            return
        else:
            self.filename = filename


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
    window = Record()
    p = window.palette()
    color = QColor()
    color.setRgb(255, 255, 215)
    p.setColor(window.backgroundRole(), color)
    window.setPalette(p)
    window.setLayoutDirection(Qt.RightToLeft)
    #window.setMaximumWidth(1000)
    window.show()
    app.exec_()
