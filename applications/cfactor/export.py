# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebEngineWidgets import QWebEnginePage
import os
import pyqtgraph as pg
from exporter import export_to_word as word
from exporter import config

def getLastSaveDirectory(f):
    f = str(f)
    return os.sep.join(f.split(os.sep)[:-1])

class Export:

    def __init__(self, widget, dirty, lastDirectory, building):
        self.widget = widget
        self.dirty = dirty
        self.lastDirectory = lastDirectory
        self.building = building

    def to_word(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        filters = "docx(*.docx)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, 'Word خروجی به',
                                               self.lastDirectory, filters)
        if filename == '': return
        if not filename.endswith(".docx"): filename += ".docx"
        self.lastDirectory = getLastSaveDirectory(filename)
        word.export(self.building, filename)

    def to_json(self):
        if not self.dirty:
            QMessageBox.warning(self.widget, u'خروجی', u'نتیجه ای جهت ارسال وجود ندارد')
            return

        filters = "json(*.json)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, 'save project',
                                               self.lastDirectory, filters)
        if filename == '':
            return
        if not filename.endswith('.json'): filename += '.json'
        self.lastDirectory = getLastSaveDirectory(filename)
        config.save(self.widget, filename)


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
        self.lastDirectory = getLastSaveDirectory(filename)
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
        self.lastDirectory = getLastSaveDirectory(filename)
        exporter = pg.exporters.CSVExporter(self.p)
        # save to file
        exporter.export(filename)
    
