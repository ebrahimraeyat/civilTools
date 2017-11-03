# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebEngineWidgets import QWebEnginePage
import os
import pyqtgraph as pg


class Export:

    def __init__(self, widget, dirty, lastDirectory, html):
        self.widget = widget
        self.dirty = dirty
        self.lastDirectory = lastDirectory
        self.html = html

    def to_pdf(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد.')
            return

        filters = "pdf(*.pdf)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u' Pdf خروجی به',
                                               self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)
        printer.setResolution(300)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        web = QWebEnginePage()
        # web.setHtml(self.html)
        web.printToPdf(self.html)

    def to_word(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        html = self.html
        html = html.encode('utf-8')
        filters = "doc(*.doc);;odt(*.odt)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'OpenOffice & Word خروجی به',
                                               self.lastDirectory, filters)
        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        fileSave = QFile(filename)
        fileSave.open(QIODevice.WriteOnly)
        fileSave.writeData(html)
        fileSave.close()

    def to_html(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        html = self.html
        html = html.encode('utf-8')
        filters = "html(*.html)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u' Html خروجی به',
                                               self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        fileSave = QFile(filename)
        fileSave.open(QIODevice.WriteOnly)
        fileSave.writeData(html)
        fileSave.close()

    def getLastSaveDirectory(self, f):
        f = str(f)
        return os.sep.join(f.split(os.sep)[:-1])


class ExportGraph:
    def __init__(self, widget, lastDirectory, p):
        self.widget = widget
        self.lastDirectory = lastDirectory
        self.p = widget.p

    def to_image(self):
        filters = "png(*.png);;jpg(*.jpg);;bmp(*.bmp);;eps(*.eps);;tif(*.tif);;jpeg(*.jpeg)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'خروجی منحنی ضریب بازتاب',
                                               self.lastDirectory, filters)
        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        exporter = pg.exporters.ImageExporter(self.p)
        exporter.parameters()['width'] = 1920   # (note this also affects height parameter)
        #exporter.parameters()['height'] = 600
        # save to file
        exporter.export(filename)

    def to_csv(self):
        filters = "csv(*.csv)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'خروجی منحنی ضریب بازتاب',
                                               self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = self.getLastSaveDirectory(filename)
        exporter = pg.exporters.CSVExporter(self.p)
        # save to file
        exporter.export(filename)

    def getLastSaveDirectory(self, f):
        f = str(f)
        return os.sep.join(f.split(os.sep)[:-1])


