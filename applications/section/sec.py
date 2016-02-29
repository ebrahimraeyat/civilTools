# -*- coding: utf-8 -*-

from __future__ import division
from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

NAME, TYPE, AREA, XM, YM, XMAX, YMAX, ASX, ASY, IX, IY, ZX, ZY, \
 SXPOS, SXNEG, SYPOS, SYNEG, RX, RY, BF, TF, H, TW = range(23)
MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1


class Section(object):
    sectionType = {'IPE': 'STEEL_I_SECTION',
                   'UNP': 'STEEL_DOUBLE_CHANNEL'}

    def __init__(self, **kwargs):
        self.type = QString(kwargs['_type'])
        self.name = QString(kwargs['name'])
        self.area = kwargs['area']
        self.xm = kwargs['xm']
        self.ym = kwargs['ym']
        self.xmax = kwargs['xmax']
        self.ymax = kwargs['ymax']
        self.ASy = kwargs['ASy']
        self.ASx = kwargs['ASx']
        self.Ix = kwargs['Ix']
        self.Iy = kwargs['Iy']
        self.Zx = kwargs['Zx']
        self.Zy = kwargs['Zy']
        self.bf = kwargs['bf']
        self.tf = kwargs['tf']
        self.h = kwargs['h']
        self.tw = kwargs['tw']
        self.calculateSectionProp()

    def calculateSectionProp(self):
        self.SxPOS = self.Ix / self.ym
        self.SxNEG = self.SxPOS
        self.SyPOS = self.Iy / self.xm
        self.SyNEG = self.SyPOS
        self.Rx = sqrt(self.Ix / self.area)
        self.Ry = sqrt(self.Iy / self.area)

    def __str__(self):
        secType = self.sectionType[str(self.type)]
        s = ('\n\n  <{}>\n'
               '\t<LABEL>{}</LABEL>\n'
               '\t<EDI_STD>{}</EDI_STD>\n'
               '\t<D>{}</D>\n'
               '\t<BF>{}</BF>\n'
               '\t<TF>{}</TF>\n'
               '\t<TW>{}</TW>\n'
               '\t<KDES>17</KDES>\n'
               '\t<A>{:.0f}</A>\n'
               '\t<AS2>{:.0f}</AS2>\n'
               '\t<AS3>{:.0f}</AS3>\n'
               '\t<I33>{:.0f}</I33>\n'
               '\t<I22>{:.0f}</I22>\n'
               '\t<S33POS>{:.0f}</S33POS>\n'
               '\t<S33NEG>{:.0f}</S33NEG>\n'
               '\t<S22POS>{:.0f}</S22POS>\n'
               '\t<S22NEG>{:.0f}</S22NEG>\n'
               '\t<R33>{:.1f}</R33>\n'
               '\t<R22>{:.1f}</R22>\n'
               '\t<Z33>{:.0f}</Z33>\n'
               '\t<Z22>{:.0f}</Z22>\n'
               '\t<J>0</J>\n'
               '  </{}>'
              ).format(secType, self.name, self.name, self.h, self.bf, self.tf,
                                       self.tw, self.area, self.ASy, self.ASx, self.Ix, self.Iy,
                                       self.SxPOS, self.SxNEG, self.SyPOS, self.SyNEG, self.Rx,
                                       self.Ry, self.Zx, self.Zy, secType)
        return s

    @staticmethod
    def exportXml(fname, sections):
        #error = None
        fh = None
        #try:
        fh = QFile(fname)
        if not fh.open(QIODevice.WriteOnly):
            raise IOError, unicode(fh.errorString())
        stream = QTextStream(fh)
        #stream.setCodec(CODEC)
        stream << ('<?xml version="1.0" encoding="utf-8"?>\n'
        '<PROPERTY_FILE xmlns="http://www.csiberkeley.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.csiberkeley.com CSIExtendedSectionPropertyFile.xsd">\n'
        '   <EbrahimRaeyat_Presents>\n'
        '      <Comment_on_CopyRight> This database is provided by: EbrahimRaeyat, (2016); http://www.ebrahimraeyat.blog.ir </Comment_on_CopyRight>\n'
        '   </EbrahimRaeyat_Presents>\n'
        '  <CONTROL>\n'
        '      <FILE_ID>CSI Frame Properties</FILE_ID>\n'
        '      <VERSION>1</VERSION>\n'
        '      <LENGTH_UNITS>mm</LENGTH_UNITS>\n'
        '      <FORCE_UNITS>kgf</FORCE_UNITS>\n'
        '  </CONTROL>\n\n')
        for section in sections:
            stream << section.__str__()
        stream << '\n</PROPERTY_FILE>'
        return True, "Exported section properties to %s" % (QFileInfo(fname).fileName())


#class Sections(object):

    #def __init__(self, filename=QString()):
        #self.filename = QString(filename)
        #self.dirty = False
        #self.sections = {}
        #self.names = set()
        #self.types = set()

    #def section(self, identity):
        #return self.sections.get(identity)

    #def addSection(self, section):
        #self.sections[id(section)] = section
        #self.names.add(unicode(section.name))
        #self.types.add(unicode(section._type))
        #self.dirty = True

    #def removeSection(self, section):
        #del self.sections[id(section)]
        #del section
        #self.dirty = True

    #def __len__(self):
        #return len(self.sections)

    #def __iter__(self):
        #for section in self.sections.values():
            #yield section

    ##def inOrder(self):
        ##return sorted(self.sections.values())

    ##def inCountryOwnerOrder(self):
        ##return sorted(self.sections.values(),
                      ##key=lambda x: (x.country, x.owner, x.name))

    #def load(self):
        #exception = None
        #fh = None
        #try:
            #if self.filename.isEmpty():
                #raise IOError, "no filename specified for loading"
            #fh = QFile(self.filename)
            #if not fh.open(QIODevice.ReadOnly):
                #raise IOError, unicode(fh.errorString())
            #stream = QDataStream(fh)
            #magic = stream.readInt32()
            #if magic != MAGIC_NUMBER:
                #raise IOError, "unrecognized file type"
            #fileVersion = stream.readInt16()
            #if fileVersion != FILE_VERSION:
                #raise IOError, "unrecognized file type version"
            #self.sections = []
            #while not stream.atEnd():
                #_type = QString()
                #name = QString()
                #stream >> _type >> name
                #area = stream.readFloat()
                #xm = stream.readFloat()
                #ym = stream.readFloat()
                #xmax = stream.readFloat()
                #ymax = stream.readFloat()
                #ASy = stream.readFloat()
                #ASx = stream.readFloat()
                #Ix = stream.readFloat()
                #Iy = stream.readFloat()
                #Zx = stream.readFloat()
                #Zy = stream.readFloat()
                #BF = stream.readFloat()
                #TF = stream.readFloat()
                #H = stream.readFloat()
                #TW = stream.readFloat()
                #section = Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                             #xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                             #Zx=Zx, Zy=Zy, bf=BF, tf=TF, h=H, tw=TW)
                #self.sections.append(section)
                #self.names.add(unicode(name))
                #self.types.add(unicode(_type))
            #self.dirty = False
        #except IOError, err:
            #exception = err
        #finally:
            #if fh is not None:
                #fh.close()
            #if exception is not None:
                #raise exception
        #return self.sections


    #def save(self):
        #exception = None
        #fh = None
        #try:
            #if self.filename.isEmpty():
                #raise IOError, "no filename specified for saving"
            #fh = QFile(self.filename)
            #if not fh.open(QIODevice.WriteOnly):
                #raise IOError, unicode(fh.errorString())
            #stream = QDataStream(fh)
            #stream.writeInt32(MAGIC_NUMBER)
            #stream.writeInt16(FILE_VERSION)
            #stream.setVersion(QDataStream.Qt_4_7)
            #for section in self.sections:
                #stream << section.type << section.name
                #stream.writeFloat(section.area)
                #stream.writeFloat(section.xm)
                #stream.writeFloat(section.ym)
                #stream.writeFloat(section.xmax)
                #stream.writeFloat(section.ymax)
                #stream.writeFloat(section.ASy)
                #stream.writeFloat(section.ASx)
                #stream.writeFloat(section.Ix)
                #stream.writeFloat(section.Iy)
                #stream.writeFloat(section.Zx)
                #stream.writeFloat(section.Zy)
                #stream.writeFloat(section.bf)
                #stream.writeFloat(section.tf)
                #stream.writeFloat(section.h)
                #stream.writeFloat(section.tw)
            #self.dirty = False
        #except IOError, err:
            #exception = err
        #finally:
            #if fh is not None:
                #fh.close()
            #if exception is not None:
                #raise exception


class SectionTableModel(QAbstractTableModel):

    def __init__(self, filename=QString()):
        super(SectionTableModel, self).__init__()
        self.filename = filename
        self.dirty = False
        self.sections = []
        self.names = set()
        self.types = set()

    def sortByName(self):
        self.sections = sorted(self.sections)
        self.reset()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) |
                Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < len(self.sections))):
            return QVariant()
        section = self.sections[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return QVariant(section.name)
            elif column == TYPE:
                return QVariant(section.type)
            elif column == AREA:
                return QVariant(QString("%L1").arg(section.area))
            elif column == XM:
                return QVariant(QString("%L1").arg(section.xm))
            elif column == YM:
                return QVariant(QString("%L1").arg(section.ym))
            elif column == XMAX:
                return QVariant(QString("%L1").arg(section.xmax))
            elif column == YMAX:
                return QVariant(QString("%L1").arg(section.ymax))
            elif column == ASY:
                return QVariant(QString("%L1").arg(section.ASy))
            elif column == ASX:
                return QVariant(QString("%L1").arg(section.ASx))
            elif column == IX:
                return QVariant(QString("%L1").arg(section.Ix))
            elif column == IY:
                return QVariant(QString("%L1").arg(section.Iy))
            elif column == ZX:
                return QVariant(QString("%L1").arg(section.Zx))
            elif column == ZY:
                return QVariant(QString("%L1").arg(section.Zy))
            elif column == BF:
                return QVariant(QString("%L1").arg(section.bf))
            elif column == TF:
                return QVariant(QString("%L1").arg(section.tf))
            elif column == H:
                return QVariant(QString("%L1").arg(section.h))
            elif column == TW:
                return QVariant(QString("%L1").arg(section.tw))
            elif column == SXPOS:
                return QVariant(QString("%L1").arg(section.SxPOS))
            elif column == SXNEG:
                return QVariant(QString("%L1").arg(section.SxNEG))
            elif column == SYPOS:
                return QVariant(QString("%L1").arg(section.SyPOS))
            elif column == SYNEG:
                return QVariant(QString("%L1").arg(section.SyNEG))
            elif column == RX:
                return QVariant(QString("%L1").arg(section.Rx))
            elif column == RY:
                return QVariant(QString("%L1").arg(section.Ry))

        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if 'IPE14' in section.name:
                return QVariant(QColor(150, 200, 150))
            elif 'IPE16' in section.name:
                return QVariant(QColor(150, 200, 250))
            elif 'IPE18' in section.name:
                return QVariant(QColor(250, 200, 250))
            elif 'IPE20' in section.name:
                return QVariant(QColor(250, 250, 130))
            elif 'IPE22' in section.name:
                return QVariant(QColor(10, 250, 250))
            elif 'IPE24' in section.name:
                return QVariant(QColor(210, 230, 230))
            elif 'IPE27' in section.name:
                return QVariant(QColor(110, 230, 230))
            elif 'IPE30' in section.name:
                return QVariant(QColor(210, 130, 230))
            else:
                return QVariant(QColor(150, 150, 250))

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == NAME:
                return QVariant("Name")
            elif section == TYPE:
                return QVariant("Type")
            elif section == XM:
                return QVariant("Xm")
            elif section == YM:
                return QVariant("Ym")
            elif section == AREA:
                return QVariant("A (mm2)")
            elif section == XMAX:
                return QVariant("Xmax")
            elif section == YMAX:
                return QVariant("Ymax")
            elif section == ASY:
                return QVariant("ASy (mm3)")
            elif section == ASX:
                return QVariant("ASx (mm3)")
            elif section == IX:
                return QVariant("Ix (mm4)")
            elif section == IY:
                return QVariant("Iy (mm4)")
            elif section == ZX:
                return QVariant("Zx (mm3)")
            elif section == ZY:
                return QVariant("Zy (mm3)")
            elif section == BF:
                return QVariant("bf (mm)")
            elif section == TF:
                return QVariant("tf (mm)")
            elif section == H:
                return QVariant("h (mm)")
            elif section == TW:
                return QVariant("tw (mm)")
            elif section == SXPOS:
                return QVariant("Sx (mm3)")
            elif section == SXNEG:
                return QVariant("SxNEG")
            elif section == SYPOS:
                return QVariant("Sy (mm3)")
            elif section == SYNEG:
                return QVariant("SyNEG")
            elif section == RX:
                return QVariant("rx (mm)")
            elif section == RY:
                return QVariant("ry (mm)")

        return QVariant(int(section + 1))

    def rowCount(self, index=QModelIndex()):
        return len(self.sections)

    def columnCount(self, index=QModelIndex()):
        return 23

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.sections):
            section = self.sections[index.row()]
            column = index.column()
            if column == NAME:
                section.name = value.toString()
            elif column == TYPE:
                section.type = value.toString()
            elif column == AREA:
                value, ok = value.toFloat()
                if ok:
                    section.area = value
            elif column == XM:
                value, ok = value.toFloat()
                if ok:
                    section.xm = value
            elif column == YM:
                value, ok = value.toFloat()
                if ok:
                    section.ym = value
            elif column == XMAX:
                value, ok = value.toFloat()
                if ok:
                    section.xmax = value
            elif column == YMAX:
                value, ok = value.toFloat()
                if ok:
                    section.ymax = value
            self.dirty = True
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.sections.insert(position + row,
                              Ipe("IPE18", 2390, 91, 180, 13170000, 1010000, 166000, 34600, 8.0, 5.3))
        self.endInsertRows()
        self.dirty = True
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.sections = (self.sections[:position] +
                      self.sections[position + rows:])
        self.endRemoveRows()
        self.dirty = True
        return True

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
            self.sections = []
            while not stream.atEnd():
                name = QString()
                _type = QString()
                stream >> _type >> name
                area = stream.readFloat()
                xm = stream.readFloat()
                ym = stream.readFloat()
                xmax = stream.readFloat()
                ymax = stream.readFloat()
                ASy = stream.readFloat()
                ASx = stream.readFloat()
                Ix = stream.readFloat()
                Iy = stream.readFloat()
                Zx = stream.readFloat()
                Zy = stream.readFloat()
                BF = stream.readFloat()
                TF = stream.readFloat()
                H = stream.readFloat()
                TW = stream.readFloat()
                section = Section(_type=_type, name=name, area=area, xm=xm, ym=ym,
                             xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                             Zx=Zx, Zy=Zy, bf=BF, tf=TF, h=H, tw=TW)
                self.sections.append(section)
                self.names.add(unicode(name))
                self.types.add(unicode(_type))
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
            for section in self.sections:
                stream << section.type << section.name
                stream.writeFloat(section.area)
                stream.writeFloat(section.xm)
                stream.writeFloat(section.ym)
                stream.writeFloat(section.xmax)
                stream.writeFloat(section.ymax)
                stream.writeFloat(section.ASy)
                stream.writeFloat(section.ASx)
                stream.writeFloat(section.Ix)
                stream.writeFloat(section.Iy)
                stream.writeFloat(section.Zx)
                stream.writeFloat(section.Zy)
                stream.writeFloat(section.bf)
                stream.writeFloat(section.tf)
                stream.writeFloat(section.h)
                stream.writeFloat(section.tw)
                stream.writeFloat(section.SxPOS)
                stream.writeFloat(section.SxNEG)
                stream.writeFloat(section.SyPOS)
                stream.writeFloat(section.SyNEG)
                stream.writeFloat(section.Rx)
                stream.writeFloat(section.Ry)
            self.dirty = False
        except IOError, err:
            exception = err
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


class DoubleSection(Section):

    def __init__(self, section, dist=0):
        '''dist = distance between two sections, 0 mean that there is no
        distance between sections'''
        _type = section.type
        if dist == 0:
            name = '2' + section.name
        else:
            name = '2' + section.name + 'c{}'.format(dist)
        dist *= 10
        area = 2 * section.area
        xm = section.xmax + dist / 2
        ym = section.ym
        xmax = 2 * section.xmax + dist
        ymax = section.ymax
        ASy = 2 * section.ASy
        ASx = 2 * section.ASx
        Ix = 2 * section.Ix
        Iy = 2 * (section.Iy + section.area * (section.xm + dist / 2) ** 2)
        Zx = 2 * section.Zx
        af = section.bf * section.tf
        aw = section.tw * (section.h - 2 * section.tf)
        Zy = 2 * (2 * af * (section.bf + dist) / 2) + 2 * aw * (section.xm + dist / 2)
        BF = 2 * section.bf
        TF = 2 * section.tf
        H = 2 * section.h
        TW = 2 * section.tw
        super(DoubleSection, self).__init__(_type=_type, name=name, area=area, xm=xm, ym=ym,
                             xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                             Zx=Zx, Zy=Zy, bf=BF, tf=TF, h=H, tw=TW)


class AddPlateTB(Section):
    '''add plate to Top and Botton of section, center of palate in x direction
       is equal to center of section.
       bf times to 2 beacuse section equal to I_STEEL_SECTION and b/t in I
       section equal to bf/(2*tf)'''

    def __init__(self, section, plate):
        _type = section.type
        name = section.name + 'F' + plate.name
        area = section.area + 2 * plate.area
        xmax = max(section.xmax, plate.xmax)
        ymax = section.ymax + 2 * plate.ymax
        xm = xmax / 2
        ym = ymax / 2
        ASy = section.tw * ymax
        ASx = section.ASx + 5 / 3 * plate.area
        Ix = section.Ix + 2 * (plate.Ix + plate.area * (section.ym + plate.ym) ** 2)
        Iy = section.Iy + 2 * plate.Iy
        Zx = section.Zx + 2 * (plate.area * (section.ym + plate.ym))
        Zy = section.Zy + 2 * plate.Zy
        tf = plate.tf
        bf = 2 * min(section.xmax, plate.bf)
        h = section.h
        tw = section.tw
        super(AddPlateTB, self).__init__(_type=_type, name=name, area=area, xm=xm, ym=ym,
            xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
            Zx=Zx, Zy=Zy, bf=bf, tf=tf, h=h, tw=tw)


class AddPlateLR(Section):

    def __init__(self, section, plate):
        _type = section.type
        name = section.name + 'W' + plate.name
        area = section.area + 2 * plate.area
        ymax = max(section.ymax, plate.ymax)
        xmax = section.xmax + 2 * plate.xmax
        xm = xmax / 2
        ym = ymax / 2
        ASx = section.ASx
        ASy = section.ASy + 2 * plate.area
        Iy = section.Iy + 2 * (plate.Iy + plate.area * (section.xm + plate.xm) ** 2)
        Ix = section.Ix + 2 * plate.Ix
        Zy = section.Zy + 2 * (plate.area * (section.xm + plate.xm))
        Zx = section.Zx + 2 * plate.Zx
        tw = section.tw
        h = section.h
        if plate.bf < tw:
            tw = 2 * plate.bf
        bf = section.bf
        tf = section.tf
        super(AddPlateLR, self).__init__(_type=_type, name=name, area=area, xm=xm, ym=ym,
            xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
            Zx=Zx, Zy=Zy, bf=bf, tf=tf, h=h, tw=tw)


class AddPlateTBThick(AddPlateTB):

    def __init__(self, section, thick):
        plateWidth = section.xmax - 40
        plate = Plate(plateWidth, thick)
        super(AddPlateTBThick, self).__init__(section, plate)


class Ipe(Section):

    def __init__(self, name, area, xmax, ymax, Ix, Iy, Zx, Zy, tf, tw):
        xm = xmax / 2
        ym = ymax / 2
        bf = xmax
        h = ymax
        ASy = ymax * tw
        ASx = 5 / 3 * bf * tf
        super(Ipe, self).__init__(_type='IPE', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, h=h, tw=tw)

    @staticmethod
    def createStandardIpes():
        IPE14 = Ipe("IPE14", 1640, 73, 140, 5410000, 449000, 88300, 19200, 6.9, 4.7)
        IPE16 = Ipe("IPE16", 2010, 82, 160, 8690000, 683000, 124000, 26100, 7.4, 5.0)
        IPE18 = Ipe("IPE18", 2390, 91, 180, 13170000, 1010000, 166000, 34600, 8.0, 5.3)
        IPE20 = Ipe("IPE20", 2850, 100, 200, 19400000, 1420000, 221000, 44600, 8.5, 5.6)
        IPE22 = Ipe("IPE22", 3340, 110, 220, 27770000, 2050000, 285000, 58100, 9.2, 5.9)
        IPE24 = Ipe("IPE24", 3910, 120, 240, 38900000, 2840000, 367000, 73900, 9.8, 6.2)
        IPE27 = Ipe("IPE27", 4590, 135, 270, 57900000, 4200000, 484000, 96900, 10.2, 6.6)
        IPE30 = Ipe("IPE30", 5380, 150, 300, 83600000, 6040000, 628000, 125000, 10.7, 7.1)
        IPE = {14: IPE14, 16: IPE16, 18: IPE18, 20: IPE20, 22: IPE22, 24: IPE24, 27: IPE27, 30: IPE30}
        return IPE

    #def double(self, dist=0):
        #return DoubleSection(self, dist)

    #def addPlateTB(self, plate):
        #return AddPlateTB(self, plate)


class Unp(Section):

    def __init__(self, name, area, xmax, ymax, Ix, Iy, tf, tw):
        xm = xmax / 2
        ym = ymax / 2
        bf = xmax
        tf = tf
        h = ymax
        tw = tw
        ASy = ymax * tw
        ASx = 5 / 3 * bf * tf
        af = bf * tf
        Zx = 2 * (af * (ymax - tf) / 2 + tw * (ymax / 2 - tf) ** 2)
        Zy = 2 * (tf * bf ** 2 / 4) + (ymax - 2 * tf) * tw ** 2 / 4

        super(Unp, self).__init__(_type='UNP', name=name, area=area, xm=xm, ym=ym,
                                  xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
                                  Zx=Zx, Zy=Zy, bf=bf, tf=tf, h=h, tw=tw)

    @staticmethod
    def createStandardUnps():
        UNP8 = Unp("UNP8", 2390, 91, 180, 13170000, 1010000, 8.0, 5.3)
        UNP10 = Unp("UNP10", 2850, 100, 200, 19400000, 1420000, 8.5, 5.6)
        UNP12 = Unp("UNP12", 3340, 110, 220, 27770000, 2050000, 9.2, 5.9)
        UNP14 = Unp("UNP14", 3910, 120, 240, 38900000, 2840000, 9.8, 6.2)
        UNP = {8: UNP8, 10: UNP10, 12: UNP12, 14: UNP14}
        return UNP

    def double(self, dist=0):
        return DoubleSection(self, dist)

    def addPlateTB(self, plate):
        return AddPlateTB(self, plate)


class Plate(Section):

    def __init__(self, xmax, ymax):
        name = 'PL%sX%s' % (xmax, ymax)
        area = xmax * ymax
        xm = xmax / 2
        ym = ymax / 2
        ASy = 0
        ASx = area
        Ix = xmax * ymax ** 3 / 12
        Iy = ymax * xmax ** 3 / 12
        Zy = ymax * xmax ** 2 / 4
        bf = xmax
        tf = ymax
        super(Plate, self).__init__(_type='PLATE', name=name, area=area, xm=xm, ym=ym,
            xmax=xmax, ymax=ymax, ASy=ASy, ASx=ASx, Ix=Ix, Iy=Iy,
            Zx=0, Zy=Zy, bf=bf, tf=tf, h=0, tw=0)


if __name__ == '__main__':

    IPE = Ipe.createStandardIpes()
    IPE18 = IPE[18]

    IPE18_2 = IPE18.double(6)
    #IPE20_2 = IPE20.doubleIpe()
    #IPE22_2 = IPE22.doubleIpe()
    #IPE24_2 = IPE24.doubleIpe()
    #IPE27_2 = IPE27.doubleIpe()

    plate1 = Plate(150, 8)
    IPE18PL = AddPlateTB(IPE18_2, plate1)
    plate2 = Plate(8, 240)
    IPE18PL2 = AddPlateLR(IPE18PL, plate2)

    #IPE_2 = [IPE18_2, IPE20_2, IPE22_2, IPE24_2, IPE27_2]

    print IPE18PL2
    #IPE18_2PL8 = AddPlateTBThick(IPE18_2, 8)
    #IPE20_2PL8 = IPE20_2.addPlateTBThick(8)
    #IPE22_2PL8 = IPE22_2.addPlateTBThick(8)
    #IPE24_2PL8 = IPE24_2.addPlateTBThick(8)
    #IPE27_2PL8 = IPE27_2.addPlateTBThick(8)
    #print IPE18_2PL8

    #IPE_2PL8 = [IPE18_2PL8, IPE20_2PL8, IPE22_2PL8, IPE24_2PL8, IPE27_2PL8]

    #sections = IPE + IPE_2 + IPE_2PL8

    ##for section in sections:
        ##

    ##IPE2PLATE6 = IPE18_2.addPlateTB(plate6)
    #Section.exportXml("2IPE.xml", sections)
    ##print IPE2PLATE6

