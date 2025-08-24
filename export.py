# -*- coding: utf-8 -*-

# from PySide.QtGui import *
# from PySide.QtCore import *
from PySide.QtGui import QFileDialog
import os
from functools import reduce

def getLastSaveDirectory(f):
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
        self.lastDirectory = getLastSaveDirectory(filename)
        exporter = pg.exporters.ImageExporter(self.p)
        exporter.parameters()['width'] = 1920   # (note this also affects height parameter)
        #exporter.parameters()['height'] = 600
        # save to file
        exporter.export(filename)

    def to_csv(self):
        filters = "txt(*.txt)"
        filename, _ = QFileDialog.getSaveFileName(self.widget, u'Export Spectrum',
                                                  self.lastDirectory, filters)

        if filename == '':
            return
        self.lastDirectory = getLastSaveDirectory(filename)
        A = self.widget.final_building.acc
        I = self.widget.final_building.importance_factor
        Rux = self.widget.final_building.x_system.Ru
        Ruy = self.widget.final_building.y_system.Ru
        data = []
        for c in self.p.curves:
            if c.name() == 'B':
                data.append(c.getData())

        sep = '\t'
        if Rux == Ruy:
            Rs = (Rux,)
            dirs = ('',)
        else:
            Rs = (Rux, Ruy)
            dirs = ('_x', '_y')
        for R, dir_ in zip(Rs, dirs):
            fname = f'{filename[:-4]}{dir_}{filename[-4:]}'
            fd = open(fname, 'w')
            i = 0
            numFormat = '%0.10g'
            numRows = reduce(max, [len(d[0]) for d in data])
            for i in range(numRows):
                for d in data:
                    if i < len(d[0]):
                        c = A * d[1][i] * I / R
                        fd.write(numFormat % d[0][i] + sep + numFormat % c)
                fd.write('\n')
            fd.close()
