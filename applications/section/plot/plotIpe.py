# -*- coding: utf-8 -*-

import pyqtgraph as pg
import numpy as np
import os
# from PyQt4.QtCore import QTextStream, QFile, QIODevice
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'c')

# from pre import sections


class PlotSectionAndEqSection(object):

    def __init__(self, section, row=0):
        self.row = row
        self.autocadScrText = 'textsize{0}20{0}'.format(os.linesep)
        self.section = section
        self.geometry_list = section.geometry_list

    def plot(self):
        n = 0
        baseSection = self.section.baseSection
        baseSectionType = str(baseSection.type)
        xm = baseSection.xm
        ym = baseSection.ym
        xmax = baseSection.xmax
        ymax = baseSection.ymax

        win = pg.PlotWidget()
        win.setXRange(-0.2 * self.section.xmax, 2.4 * self.section.xmax)
        win.setYRange(-0.3 * self.section.ymax, 1.1 * self.section.ymax)
        win.showGrid(x=False, y=False)
        p1 = Point(0, 0)

        ipeText = pg.TextItem(html=baseSection.name)
        if not baseSectionType == 'BOX':
            win.addItem(self.plot_item(self.geometry_list[n]))
            n += 1
            ipeText = pg.TextItem(html=baseSection.name, anchor=(-0.3, 0), border='k', fill=(0, 0, 255, 100))

        if self.section.isSouble:
            if baseSectionType == 'BOX':
                return
            # p2 = Point(p1.x + 2 * baseSection.xm + self.section.cc, p1.y)
            win.addItem(self.plot_item(self.geometry_list[n]))
            n += 1
            html = 'cc={}\tcm'.format(int(self.section.cc / 10))
            self.textItem(win, html, pos=Point(xm, -30), anchor=(.5, 0))
            p21 = Point(p1.x + 2 * baseSection.xm + 2 * self.section.cc, p1.y)
            win.addItem(self.plot_item(self.geometry_list[n]))
            n += 1
            xmax = 2 * baseSection.xm + 2 * self.section.cc
            xm = xmax / 2

        if self.section.isDouble:
            if baseSectionType == 'BOX':
                return
            p2 = Point(p1.x + 2 * baseSection.xm + self.section.cc, p1.y)
            win.addItem(self.plot_item(self.geometry_list[n]))
            n += 1
            xmax = 2 * baseSection.xm + self.section.cc
            xm = xmax / 2
            html = 'cc={}\tcm'.format(int(self.section.cc / 10))
            self.textItem(win, html, pos=Point(xm, -30), anchor=(.5, 0))
            ipeText = pg.TextItem(html='2' + baseSection.name, anchor=(-.3, 0), border='k', fill=(0, 0, 255, 100))

        if self.section.TBPlate:
            win.addItem(self.plot_item(self.geometry_list[n], 'b'))
            win.addItem(self.plot_item(self.geometry_list[n + 1], 'b'))
            n += 2
            ym = ymax / 2
            ymax = ymax + 2 * self.section.TBPlate.tf
            self.textItem(win, html=self.section.TBPlate.name +
                          ' mm', pos=Point(xm, ymax), anchor=(.5, 1))

        if self.section.LRPlate:
            win.addItem(self.plot_item(self.geometry_list[n], 'g'))
            win.addItem(self.plot_item(self.geometry_list[n + 1], 'g'))
            n += 2
            ymax = max(ymax, self.section.LRPlate.tf)
            self.textItem(win, html=self.section.LRPlate.name +
                          ' mm', pos=Point(xmax, ym), anchor=(.5, 2), isRotate=True)

        if self.section.webPlate:
            if baseSectionType == 'BOX':
                return
            win.addItem(self.plot_item(self.geometry_list[n], 'g'))
            win.addItem(self.plot_item(self.geometry_list[n + 1], 'g'))
            n += 2

            # self.textItem(win, html=self.section.LRPlate.name +
            #' mm', pos=Point(xmax, ym), anchor=(.5, 2), isRotate=True)
        xmax1 = self.section.xmax
        if self.section.TBPlate:
            xmax1 = max(self.section.xmax, self.section.TBPlate.xmax)

        p7 = Point(xmax1 + baseSection.bf, ym - self.section.d_equivalentI / 2)
        # win.addItem(self.drawIpe(self.section, p7, False, 'm'))

        win.addItem(ipeText)
        ipeText.setPos(baseSection.xm, ym)
        self.add_text_to_script_file(self.section.name, Point(0, -80))

        html = 'bf={:.0f},\t tf={:.1f} mm'.format(
            self.section.bf_equivalentI, self.section.tf_equivalentI)
        self.textItem(win, html=html, pos=Point(p7.x + self.section.bf_equivalentI / 2,
                                                1.02 * self.section.d_equivalentI), anchor=(.5, 1))

        html = 'd={:.0f},\ttw={:.1f} mm'.format(
            self.section.d_equivalentI, self.section.tw_equivalentI)
        self.textItem(win, html=html, pos=Point(p7.x + self.section.bf_equivalentI, ym),
                      anchor=(.5, 1.2), isRotate=True)
        win.setAspectLocked()
        return win

    def add_pline_to_script_file(self, a, b):
        self.autocadScrText += 'pline' + os.linesep
        for x, y in zip(a, b):
            self.autocadScrText += ('{},{}{}'.format(x, y + self.row * 550., os.linesep))
        self.autocadScrText += os.linesep

    def add_text_to_script_file(self, text, pos, isRotate=None):
        self.autocadScrText += 'text' + os.linesep
        self.autocadScrText += '{0},{1}{2}{2}{2}'.format(pos.x, pos.y + self.row * 550., os.linesep)
        # self.autocadScrText += '{}{}'.format('90' if isRotate else '0', os.linesep)
        self.autocadScrText += '{0}{1}'.format(text, os.linesep)

    def textItem(self, win, html, pos=None, anchor=(0, 0), isFill=True, isRotate=False):
        if isFill:
            text = pg.TextItem(html=html, anchor=anchor, border='k', fill=(0, 0, 255, 100))
        else:
            text = pg.TextItem(html=html, anchor=anchor)
        if isRotate:
            text.setRotation(90)
        win.addItem(text)
        if pos:
            text.setPos(pos.x, pos.y)
            pos = Point(pos.x, pos.y + anchor[1] * 20)
            self.add_text_to_script_file(html, pos, isRotate)
        else:
            text.setPos(0, 0)

    def plot_item(self, geometry, color='r'):
        pen = pg.mkPen(color, width=2)
        xs = [i[0] for i in geometry.points]
        ys = [i[1] for i in geometry.points]
        xs.append(xs[0])
        ys.append(ys[0])
        a = np.array(xs)
        b = np.array(ys)
        finitecurve = pg.PlotDataItem(a, b, connect="finite", pen=pen)
        return finitecurve

    def drawPlate(self, pl, cp, color='b', width=2):
        pen = pg.mkPen(color, width=width)
        x1 = cp.x - pl.bf / 2
        x2 = cp.x + pl.bf / 2
        y1 = cp.y - pl.tf / 2
        y2 = cp.y + pl.tf / 2
        xs = [x1, x2, x2, x1, x1]
        ys = [y1, y1, y2, y2, y1]
        a = np.array(xs)
        b = np.array(ys)
        finitecurve = pg.PlotDataItem(a, b, connect="finite", pen=pen)
        self.add_pline_to_script_file(a, b)
        return finitecurve


class Point(object):

    def __init__(self, x, y):
        super(Point, self).__init__()
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return 'x = {}, y = {}'.format(self.x, self.y)
