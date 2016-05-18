# -*- coding: utf-8 -*-

import pyqtgraph as pg
import numpy as np
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'c')


class PlotSectionAndEqSection(object):

    def __init__(self, section):

        self.section = section
        self.drawBaseSection = {'IPE': PlotSectionAndEqSection.drawIpe, 'UNP': PlotSectionAndEqSection.drawUnp}

    def plot(self):

        baseSection = self.section.baseSection
        baseSectionType = str(baseSection.type)
        #drawBaseSection = self.drawBaseSection[baseSectionType]
        xm = baseSection.xm
        ym = baseSection.ym
        xmax = baseSection.xmax
        ymax = baseSection.ymax

        win = pg.PlotWidget()
        win.setXRange(-0.2 * self.section.xmax, 2.4 * self.section.xmax)
        win.setYRange(-0.3 * self.section.ymax, 1.1 * self.section.ymax)
        win.showGrid(x=True, y=True)
        p1 = Point(0, 0)
        #pl1 = pg.PolyLineROI([[0,0], [10,10], [10,30], [30,10]], closed=True)
        #win.addItem(pl1)
        win.addItem(self.drawBaseSection[baseSectionType](baseSection, p1))
        ipeText = pg.TextItem(html=baseSection.name, anchor=(-0.3, 0), border='k', fill=(0, 0, 255, 100))

        if self.section.isSouble:
            p2 = Point(p1.x + 2 * baseSection.xm + self.section.cc, p1.y)
            win.addItem(self.drawBaseSection[baseSectionType](baseSection, p2, True))
            html = 'cc={}\tcm'.format(int(self.section.cc / 10))
            PlotSectionAndEqSection.textItem(win, html, pos=Point(xm, 0), anchor=(.5, -1))
            p21 = Point(p1.x + 2 * baseSection.xm + 2 * self.section.cc, p1.y)
            win.addItem(self.drawBaseSection[baseSectionType](baseSection, p21, True))
            xmax = 2 * baseSection.xm + 2 * self.section.cc
            xm = xmax / 2

        if self.section.isDouble:
            p2 = Point(p1.x + 2 * baseSection.xm + self.section.cc, p1.y)
            win.addItem(self.drawBaseSection[baseSectionType](baseSection, p2, True))
            xmax = 2 * baseSection.xm + self.section.cc
            xm = xmax / 2
            html = 'cc={}\tcm'.format(int(self.section.cc / 10))
            PlotSectionAndEqSection.textItem(win, html, pos=Point(xm, 0), anchor=(.5, -1))
            ipeText = pg.TextItem(html='2' + baseSection.name, anchor=(-.3, 0), border='k', fill=(0, 0, 255, 100))

        if self.section.TBPlate:
            p3 = Point(xm, ymax + self.section.TBPlate.tf / 2)
            p4 = Point(xm, - (self.section.TBPlate.tf / 2))
            win.addItem(PlotSectionAndEqSection.drawPlate(self.section.TBPlate, p3))
            win.addItem(PlotSectionAndEqSection.drawPlate(self.section.TBPlate, p4))
            ym = ymax / 2
            ymax = ymax + 2 * self.section.TBPlate.tf
            PlotSectionAndEqSection.textItem(win, html=self.section.TBPlate.name +
                                             ' mm', pos=Point(xm, ymax), anchor=(.5, 1))

        if self.section.LRPlate:
            p5 = Point(- (self.section.LRPlate.bf / 2), ym)
            p6 = Point(xmax + self.section.LRPlate.bf / 2, ym)
            win.addItem(PlotSectionAndEqSection.drawPlate(self.section.LRPlate, p5, 'g'))
            win.addItem(PlotSectionAndEqSection.drawPlate(self.section.LRPlate, p6, 'g'))
            ymax = max(ymax, self.section.LRPlate.tf)
            PlotSectionAndEqSection.textItem(win, html=self.section.LRPlate.name +
                                             ' mm', pos=Point(xmax, ym), anchor=(.5, 2), isRotate=True)
        xmax1 = self.section.xmax
        if self.section.TBPlate:
            xmax1 = max(self.section.xmax, self.section.TBPlate.xmax)

        p7 = Point(xmax1 + baseSection.bf, ym - self.section.d_equivalentI / 2)
        win.addItem(PlotSectionAndEqSection.drawIpe(self.section, p7, False, 'm'))

        win.addItem(ipeText)
        ipeText.setPos(baseSection.xm, ym)

        PlotSectionAndEqSection.textItem(win, html='bf={:.0f},\t tf={:.1f} mm'.format(
                                        self.section.bf_equivalentI, self.section.tf_equivalentI),
                                        pos=Point(p7.x + self.section.bf_equivalentI / 2,
                                        1.02 * self.section.d_equivalentI), anchor=(.5, 1))
        PlotSectionAndEqSection.textItem(win, html='d={:.0f},\ttw={:.1f} mm'.format(
                                        self.section.d_equivalentI, self.section.tw_equivalentI),
                                    pos=Point(p7.x + self.section.bf_equivalentI, ym), anchor=(.5, 1.2), isRotate=True)
        win.setAspectLocked()
        return win

    @staticmethod
    def textItem(win, html, pos=None, anchor=(0, 0), isFill=True, isRotate=False):
        if isFill:
            text = pg.TextItem(html=html, anchor=anchor, border='k', fill=(0, 0, 255, 100))
        else:
            text = pg.TextItem(html=html, anchor=anchor)
        if isRotate:
            text.setRotation(90)
        win.addItem(text)
        if pos:
            text.setPos(pos.x, pos.y)
        else:
            text.setPos(0, 0)

    @staticmethod
    def drawIpe(ipe, p1, isMirror=False, color='r', width=2):
        mirrorSingn = 1
        if isMirror:
            mirrorSingn = -1
        pen = pg.mkPen(color, width=width)
        x1 = p1.x
        x2 = p1.x + mirrorSingn * (ipe.bf_equivalentI - ipe.tw_equivalentI) / 2
        x3 = p1.x + mirrorSingn * (ipe.bf_equivalentI + ipe.tw_equivalentI) / 2
        x4 = p1.x + mirrorSingn * ipe.bf_equivalentI
        y1 = p1.y
        y2 = p1.y + ipe.tf_equivalentI
        y3 = p1.y + ipe.d_equivalentI - ipe.tf_equivalentI
        y4 = p1.y + ipe.d_equivalentI
        a = np.array([x1, x4, x4, x3, x3, x4, x4, x1, x1, x2, x2, x1, x1])
        b = np.array([y4, y4, y3, y3, y2, y2, y1, y1, y2, y2, y3, y3, y4])
        finitecurve = pg.PlotDataItem(a, b, connect="finite", pen=pen)
        return finitecurve

    @staticmethod
    def drawUnp(unp, p1, isMirror=False, color='r', width=2):
        mirrorSingn = 1
        if isMirror:
            mirrorSingn = -1
        pen = pg.mkPen(color, width=width)
        x1 = p1.x
        x2 = p1.x + unp.tw_equivalentI * mirrorSingn
        x3 = p1.x + unp.bf_equivalentI * mirrorSingn
        y1 = p1.y
        y2 = p1.y + unp.tf_equivalentI
        y3 = p1.y + unp.d_equivalentI - unp.tf_equivalentI
        y4 = p1.y + unp.d_equivalentI
        a = np.array([x1, x3, x3, x2, x2, x3, x3, x1, x1])
        b = np.array([y1, y1, y2, y2, y3, y3, y4, y4, y1])
        finitecurve = pg.PlotDataItem(a, b, connect="finite", pen=pen)
        return finitecurve

    @staticmethod
    def drawPlate(pl, cp, color='b', width=2):
        pen = pg.mkPen(color, width=width)
        x1 = cp.x - pl.bf / 2
        x2 = cp.x + pl.bf / 2
        y1 = cp.y - pl.tf / 2
        y2 = cp.y + pl.tf / 2
        a = np.array([x1, x2, x2, x1, x1])
        b = np.array([y1, y1, y2, y2, y1])
        finitecurve = pg.PlotDataItem(a, b, connect="finite", pen=pen)
        return finitecurve


class Point(object):

    def __init__(self, x, y):
        super(Point, self).__init__()
        self.x = x
        self.y = y