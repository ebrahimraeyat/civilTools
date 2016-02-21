# -*- coding: utf-8 -*-
from soil import SoilTable
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

X, Y = range(2)
SYSTEM, LATERAL, HMAX, RU, OMEGA0, CD, TEXP, TEXP125, TAN, K, CFACTOR = range(11)
MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1

class Building(object):

    ID1 = (3, 23, 33, 36)
    #ID2 = (21, 25,28)
    #ID3 = (25,)
    specialIDs = (11, 21, 25, 28, 31, 34, 41, 42, 45, 46, 47, 48, 51)
    IDs3354 = (31, 34, 41, 42, 43, 44, 45, 46, 47, 48, 49)

    def __init__(self, risk, karbari, soilType, noStory, height,
                 infill, xSystem, ySystem, city, xTan=0, yTan=0, useTan=False):

        self.filename = ''
        self.risk = risk
        self.acc = self.acceleration()
        self.city = city
        self.karbari = karbari
        self.CMin = 0.12 * self.acc * self.karbari
        self.soilType = soilType
        self.soilProperties = SoilProperties(soilType, self.acc)
        self.noStory = noStory
        self.height = height
        self.infill = infill
        self.xSystem = xSystem
        self.ySystem = ySystem
        self.xTexp = self.period(xSystem)
        self.yTexp = self.period(ySystem)
        self.useTan = useTan
        self.xTan = xTan
        self.yTan = yTan
        if useTan:
            self.Tx = xTan
            self.Ty = yTan
        else:
            self.Tx = self.xTexp
            self.Ty = self.yTexp
        self.xReflectionFactor = ReflectionFactor(soilType, self.acc, self.Tx)
        self.yReflectionFactor = ReflectionFactor(soilType, self.acc, self.Ty)
        self.Bx = self.xReflectionFactor.B
        self.By = self.yReflectionFactor.B
        self.maxHeight = self.maxAllowedHeight()
        self.kx, self.ky = self.getK()
        self.results = self.calculateC()

    def acceleration(self):
        accs = {u'کم': 0.20,
                u'متوسط': 0.25,
                u'زیاد': 0.3,
                u'خیلی زیاد': 0.35}
        return accs[self.risk]

    def period(self, system):
        isInfill = self.infill
        alpha = system.alpha
        power = system.pow
        H = self.height

        if isInfill:
            return 0.8 * alpha * H ** power
        else:
            return alpha * H ** power

    def direction(self):
        pass

    def maxAllowedHeight(self):
        xMaxAllowedHeight = self.xSystem.maxHeight
        yMaxAllowedHeight = self.ySystem.maxHeight
        if (xMaxAllowedHeight and yMaxAllowedHeight) is None:
            maxAllowedHeight = 200
        elif xMaxAllowedHeight is None:
            maxAllowedHeight = yMaxAllowedHeight
        elif yMaxAllowedHeight is None:
            maxAllowedHeight = xMaxAllowedHeight
        else:
            maxAllowedHeight = min(xMaxAllowedHeight, yMaxAllowedHeight)
        return maxAllowedHeight

    def calculateK(self, T):
        if T < 0.5:
            self._kStr = u'T &#60 0.5 '
            return 1.0
        elif T > 2.5:
            self._kStr = u'T &#62 2.5 '
            return 2.0
        else:
            self._kStr = u' 0.5 &#60 T &#60 2.5 &#8658 k<sub>{0}</sub> = 0.5 &#215 T + 0.75'
            return 0.5 * T + 0.75

    def getK(self):
        kx = self.calculateK(self.Tx)
        self._kxStr = self._kStr.format('x')
        ky = self.calculateK(self.Ty)
        self._kyStr = self._kStr.format('y')
        return kx, ky

    def getDEngheta(self):
        if self.noStory <= 8 and not self.karbari in (1.2, 1.4):
            return 0.005 * self.height * 100
        return False

    def checkInputs(self):

        class StructureSystemError(Exception):
            pass

        title = u".را تغییر دهید '%s'سیستم مقاوم در برابر نیروی جانبی در راستای"
        #title = u' "%s" ایراد سیستم مقاوم در برابر نیروی جانبی در راستای'
        e1 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت خیلی زیاد و زیاد" در تمام مناطق لرزه خیزی مجاز نیست.'
        e2 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۱ و ۲ مجاز نیست.'
        e3 = u'ارتفاع حداکثر سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۳و ۴ به ۱۵ متر محدود میگردد.'
        e4 = u'در مناطق با خطر نسبی خیلی زیاد برای ساختمانهای با "اهمیت خیلی زیاد" فقط باید از سیستم هایی که عنوان "ویژه" دارند، استفاده شود.'
        e5 = u'در ساختمانهای با بیشتر از ۱۵ طبقه و یا بلندتر از ۵۰ متر، استفاده از سیستم قاب خمشی ویژه و یا سیستم دوگانه الزامی است.'

        ID1 = self.ID1
        specialIDs = self.specialIDs
        IDs3354 = self.IDs3354
        I = self.karbari
        A = self.acc
        H = self.height
        story = self.noStory

        for direction in ("X", "Y"):
            if direction == "X":
                ID = self.xSystem.ID
                lateralType = self.xSystem.lateralType
            else:
                ID = self.ySystem.ID
                lateralType = self.ySystem.lateralType
            try:
                if ID in ID1:
                    if I > 1.1:
                        raise StructureSystemError, (e1 % lateralType)

                    if I == 1.0 and A in (.3, .35):
                        raise StructureSystemError, (e2 % lateralType)

                    if I == 1.0 and A in (.2, .25) and H > 15:
                        raise StructureSystemError, (e3 % lateralType)

                if A == 0.35 and I == 1.4 and (not ID in specialIDs):
                    raise StructureSystemError, (e4)

                if (H > 50 or story > 15) and (not ID in IDs3354):
                    raise StructureSystemError, (e5)

            except StructureSystemError, err:
                return False, title, err, direction
        return [True]

    def calculateC(self):
        check_inputs = self.checkInputs()
        if check_inputs[0] is True:
            A = self.acc
            Bx = self.Bx
            By = self.By
            I = self.karbari
            Rux = self.xSystem.Ru
            Ruy = self.ySystem.Ru
            CxNotApproved = A * Bx * I / Rux
            CyNotApproved = A * By * I / Ruy
            if CxNotApproved < self.CMin:
                self.Cx = self.CMin
                self.cxStr = (u"{0:.4f} &#60 C<sub>min</sub> &#8658 Cx = {1}</p>"
                                ).format(CxNotApproved, self.CMin)
            else:
                self.Cx = CxNotApproved
                self.cxStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(CxNotApproved)
            if CyNotApproved < self.CMin:
                self.Cy = self.CMin
                self.cyStr = (u" {0:.4f} &#60 C<sub>min</sub> &#8658 Cy = {1}</p>"
                                ).format(CyNotApproved, self.CMin)
            else:
                self.Cy = CyNotApproved
                self.cyStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(CyNotApproved)
            return True, self.Cx, self.Cy
        else:
            return check_inputs

    def __str__(self):
        html = ''
        #stamp = QDateTime().currentDateTime().toString("ddMMyyyyhhmmss")
        html += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
        html += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        #html += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        #html += '<html>\n'
        html += '<html dir="rtl" align="right">\n'
        html += '<head>\n'
        html += '<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n'
        #html += '<meta name="stamp" content="' + stamp + '" /> \n'
        html += '<title>CFactor Calculation Results</title>\n'
        html += '<style type="text/css">\n'
        html += 'body {\n'
        html += 'font-size: 12pt;\n'
        html += '}\n'
        html += 'table {\n'
        html += 'border-collapse: collapse;\n'
        html += '}\n'
        html += 'p#pfarsi {font-size:120%;}'
        html += 'p#pmath {text-dir:ltr;text-align:left;font-size:120%;}'
        #html += 'p#pmath {text-dir:ltr;font-size:120%;}'
        html += '</style>\n'
        html += '</head>\n'

        html += '<body>\n'
        html += '<h2 align=left>CFactor Calculations</h2>\n'
        #html += 'Date: ' + QDateTime().currentDateTime().toString("dd MMM yyyy") + '\n'
        html += '<br />\n'

        html += u"<h1 align=center> مشخصات پروژه: </h1>\n"
        html += (u"<p id=pfarsi> تعداد طبقات: {0} طبقه</p>"
                u"<p id=pfarsi> ارتفاع ساختمان: {1} متر</p>"
                ).format(self.noStory,
                         self.height)
        html += (u"<p id=pfarsi><b>  مشخصات سازه در راستای X:</b> </p>"
                 u"<p id=pfarsi> {0}</p>"
                 u"<p id=pfarsi><b>  مشخصات سازه در راستای Y:</b> </p>"
                 u"<p id=pfarsi> {1}</p>").format(self.xSystem.__str__(),
                                                 self.ySystem.__str__())
        html += u"<p id=pfarsi><b>مشخصات ساختگاه:</b></p>"
        html += (u"<p id=pfarsi>  محل اجرای پروژه: شهر {0} </p>"
                 u"<p id=pfarsi> خطر نسبی زلزله: {1} </p>"
                 u"<p id=pfarsi> نسبت شتاب مبنای طرح : {2}</p>"
                 u"<p id=pfarsi> نوع خاک : تیپ {3} </p>"
                ).format(self.city,
                         self.risk,
                         self.acc,
                         self.soilType
                         )
        html += u"<p id=pfarsi><b> محاسبه زمان تناوب سازه:</b> </p>"
        if self.useTan:
            html += (u"<p id=pfarsi> از زمان تناوب تحلیلی استفاده میگردد: </p>"
                     u"<p id=pmath> T<sub>anx</sub>={0} Sec; T<sub>any</sub>={1} Sec</p>"
                     ).format(self.Tx, self.Ty)
        else:
            if self.infill:
                html += u"<p id=pfarsi>اثر میانقاب در نظر گرفته شده است.</p>"
                html += ("<p id=pmath> T<sub>x</sub> = 0.8 &#215 {0} &#215 H <sup>{2}</sup>"
                     " = 0.8 &#215 {0} &#215 ({1}) <sup>{2}</sup> = {3:.2f} Sec</p>").format(
                         self.xSystem.alpha, self.height, self.xSystem.pow, self.Tx)
                html += ("<p id=pmath> T<sub>y</sub> = 0.8 &#215 {0} &#215 H <sup>{2}</sup>"
                     " = 0.8 &#215 {0} &#215 ({1}) <sup>{2}</sup> = {3:.2f} Sec</p>").format(
                         self.ySystem.alpha, self.height, self.ySystem.pow, self.Ty)
            else:
                html += u"<p id=pfarsi>اثر میانقاب در نظر گرفته نشده است.</p>"
                html += ("<p id=pmath> T<sub>x</sub> = {0} &#215 H <sup>{2}</sup>"
                     " = {0} &#215 ({1}) <sup>{2}</sup> = {3:.2f} Sec</p>").format(
                         self.xSystem.alpha, self.height, self.xSystem.pow, self.Tx)
                html += ("<p id=pmath> T<sub>y</sub> = {0} &#215 H <sup>{2}</sup>"
                     " = {0} &#215 ({1}) <sup>{2}</sup> = {3:.2f} Sec</p>").format(
                         self.ySystem.alpha, self.height, self.ySystem.pow, self.Ty)
        html += (u"<p id=pfarsi><b> مشخصات خاک: </b> </p>"
                u"<p id=pfarsi> {0}</p>").format(self.soilProperties.__str__())
        html += (u"<p id=pfarsi><b> محاسبه ضریب بازتاب در راستای x: </b> {0}</p>"
                 u'<p id=pmath> <b>B<sub>x</sub> = {1:.2f}</b></p>'
                 ).format(self.xReflectionFactor.__str__(), self.Bx)
        html += (u"<p id=pfarsi><b> محاسبه ضریب بازتاب در راستای y: </b> {0}</p>"
                 u'<p id=pmath> <b>B<sub>y</sub> = {1:.2f}</b></p>'
                 ).format(self.yReflectionFactor.__str__(), self.By)
        #cx, cy = self.calculateC()
        html += u"<p id=pfarsi><b> محاسبه ضریب K: </b> </p>"
        html += (u"<p id=pmath> K<sub>x</sub>: {0} &#8658 <b>K<sub>x</sub> = {1:.2f}</b></p>"
                ).format(self._kxStr, self.kx)
        html += (u"<p id=pmath> K<sub>y</sub>: {0} &#8658 <b>K<sub>y</sub> = {1:.2f}</b></p>"
                ).format(self._kyStr, self.ky)
        html += u"<p id=pfarsi><b> محاسبه ضریب زلزله: </b> </p>"
        html += (u"<p id=pmath>C<sub>min</sub> = 0.12 &#215 A &#215 I = {0:.4f}</p>"
                        ).format(self.CMin)
        html += (u"<p id=pmath><b>C<sub>x</sub></b> = A &#215 B<sub>x</sub> &#215 I / R<sub>ux</sub>"
                 " = {0} &#215 {1:.2f} &#215 {2} / {3} = " + self.cxStr
                 ).format(self.acc, self.Bx, self.karbari, self.xSystem.Ru)
        html += (u"<p id=pmath><b>C<sub>y</sub></b> = A &#215 B<sub>y</sub> &#215 I / R<sub>uy</sub>"
                 " = {0} &#215 {1:.2f} &#215 {2} / {3} = " + self.cyStr
                 ).format(self.acc, self.By, self.karbari, self.ySystem.Ru)
        html += '<hr />\n'
        #html += '<b style="font-size: 8pt;">Cfactor Calculator ver. ' + __version__ + '</b>\n'
        #if ext != 'pdf':
            #html += u'     <a href="http://ebrahimraeyat.blog.ir"> دانلود آخرین ورژن نرم افزار</a> \n'
        html += '</body>\n'
        html += '</html>\n'
        #html = html.encode('utf-8')
        return html


class StructureSystem(object):

    def __init__(self, system, lateral, direction='X'):

        self.systemType = system
        self.lateralType = lateral
        self.direction = direction
        rFactorTable = RFactorTable()
        rTable = rFactorTable.structureSystems
        Rus = rTable[system][lateral]
        self.Ru = Rus[0]
        self.phi0 = Rus[1]
        self.cd = Rus[2]
        self.maxHeight = Rus[3]
        self.alpha = Rus[4]
        self.pow = Rus[5]
        self.infill = Rus[6]
        self.ID = Rus[7]

    def __str__(self):
        structure = ''
        structure += u"<p id=pfarsi> سیستم سازه: {0} </p>"
        structure += u"<p id=pfarsi> سیستم مقاوم در برابر نیروهای جانبی: {1} </p>"
        structure += u'<p id=pmath>R<sub>u</sub>={2}; H<sub>m</sub>={3} m; '
        structure += u'\u2126<sub>0</sub>={4}; C<sub>d</sub>={5}</p>'
        structure = structure.format(self.systemType, self.lateralType,
                                     self.Ru, self.maxHeight, self.phi0, self.cd)
        #structure = structure.encode('utf-8')
        return structure


class RFactorTable(object):

    def __init__(self):
        import RuTable
        self.structureSystems = RuTable.Ru

    def getSystemTypes(self):
        systemTypes = self.structureSystems.keys()
        return systemTypes

    def getLateralTypes(self, system):
        return self.structureSystems[system].keys()


class SoilProperties(object):

    def __init__(self, soilType, acc):
        soilTable = SoilTable()
        self.soilType = soilType
        self.T0 = soilTable.T0s[soilType]
        self.Ts = soilTable.Tss[soilType]
        self.S = soilTable.Ss[(soilType, acc)]
        self.S0 = soilTable.S0s[(soilType, acc)]

    def __str__(self):
        soilProp = u'<p id=pmath>soil type <b>{0}</b>: '
        soilProp += u'<b>T<sub>0</sub></b>={1}; '
        soilProp += u'<b>T<sub>s</sub></b>={2}; '
        soilProp += u'<b>S=</b>{3}; '
        soilProp += u'<b>S<sub>0</sub>=</b>{4}</p>'
        soilProp = soilProp.format(self.soilType, self.T0,
                                   self.Ts, self.S, self.S0)
        return soilProp


class ReflectionFactor(object):

    def __init__(self, soilType, acc, period):
        soilProperties = SoilProperties(soilType, acc)
        self.soilType = soilType
        self.A = acc
        self.T = period
        self.T0 = soilProperties.T0
        self.Ts = soilProperties.Ts
        self.S = soilProperties.S
        self.S0 = soilProperties.S0
        self.B1 = self.calculatB1()
        self.N = self.calculatN()
        self.B = self.B1 * self.N
        self.dt = 0.01
        self.endT = 4.5
        self.numberOfSamples = self.endT // self.dt - 1
        self.b1Curve = self.B1Curve()
        self.nCurve = self.NCurve()
        self.bCurve = self.BCurve()

    def __str__(self):
        rf = u'<p id=pmath>' + self.B1str1 + '= {0:.2f}</p>'
        rf += u'<p id=pmath>' + self.Nstr + ' &#8658 N = {1:.2f}</p>'
        #rf += u'<p id=pmath> B = {2:.2f}</p>'
        rf = rf.format(self.B1, self.N)
        return rf

    def calculatB1(self):
        T = self.T
        T0 = self.T0
        Ts = self.Ts
        S = self.S
        S0 = self.S0
        # calculating B1
        if 0 < T < T0:
            self.B1str1 = '0 &#x227A T &#60 T0 &#8658 B1 = S0 + (S - S0 + 1) &#215 (T / T0)'
            return S0 + (S - S0 + 1) * (T / T0)
        elif T0 <= T < Ts:
            self.B1str1 = "T0 &#x2264 T &#60 Ts &#8658 B1 = S + 1"
            return S + 1
        else:
            self.B1str1 = 'T &#62 Ts &#8658 B1 = (S + 1) &#215 (Ts / T)'
            return (S + 1) * (Ts / T)

    def calculatN(self):
        Ts = self.Ts
        T = self.T

        # calculating N
        if self.A > 0.27:
            if T < Ts:
                self.Nstr = ('A = {0}, T &#60 TS ').format(self.A)
                N = 1
            elif Ts <= T < 4:
                self.Nstr = ('A = {0}, Ts &#x2264 T &#60 4 &#8658').format(self.A)
                self.Nstr += 'N = .7 &#215 (T - Ts) / (4 - Ts) + 1'
                N = .7 * (T - Ts) / (4 - Ts) + 1
            else:
                self.Nstr = ('A = {0}, T &#62 4 ').format(self.A)
                N = 1.7
        else:
            if T < Ts:
                self.Nstr = ('A = {0}, T &#60 TS ').format(self.A)
                N = 1
            elif Ts <= T < 4:
                self.Nstr = ('A = {0}, Ts &#x2264 T &#60 4 &#8658').format(self.A)
                self.Nstr += 'N = 0.4 &#215 (T - Ts) / (4 - Ts) + 1'
                N = .4 * (T - Ts) / (4 - Ts) + 1
            else:
                self.Nstr = ('A = {0}, T &#62 4 ').format(self.A)
                N = 1.4
        return N

    def B1Curve(self):
        T0 = self.T0
        Ts = self.Ts
        S = self.S
        S0 = self.S0
        dt = self.dt
        B11Curve = S0 + (S - S0 + 1) * (np.arange(0, T0, dt) / T0)
        B12Curve = np.full((len(np.arange(T0, Ts, dt))), S + 1)
        if self.soilType == "I":
            B13Curve = (S + 1) * (Ts / np.arange(Ts + dt, self.endT, dt))
        else:
            B13Curve = (S + 1) * (Ts / np.arange(Ts, self.endT, dt))
        b1Curve = np.concatenate([B11Curve, B12Curve, B13Curve])
        return b1Curve

    def NCurve(self):
        Ts = self.Ts
        dt = self.dt
        if self.A > 0.27:
            N1Curve = np.full((len(np.arange(0, Ts, dt))), 1)
            N2Curve = .7 * (np.arange(Ts, 4, dt) - Ts) / (4 - Ts) + 1
            N3Curve = np.full((len(np.arange(4, self.endT, dt))), 1.7)
        else:
            N1Curve = np.full((len(np.arange(0, Ts, dt))), 1)
            N2Curve = .4 * (np.arange(Ts, 4, dt) - Ts) / (4 - Ts) + 1
            N3Curve = np.full((len(np.arange(4, self.endT, dt))), 1.4)
        nCurve = np.concatenate([N1Curve, N2Curve, N3Curve])
        return nCurve

    def BCurve(self):
        return self.b1Curve * self.nCurve


class StructureModel(QAbstractTableModel):

    def __init__(self, build):
        super(StructureModel, self).__init__()
        #self.filename = filename
        self.dirty = False
        self.build = build

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index) |
                Qt.ItemIsEditable)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = index.row()
        column = index.column()
        system = self.build.xSystem
        Texp = self.build.xTexp
        Tan = self.build.xTan
        k = self.build.kx
        c = ''
        if self.build.results[0] == True:
            c = self.build.results[1]

        if column == Y:
            system = self.build.ySystem
            Texp = self.build.yTexp
            Tan = self.build.yTan
            k = self.build.ky
            if self.build.results[0] == True:
                c = self.build.results[2]
        if role == Qt.DisplayRole:
            if row == SYSTEM:
                return QVariant(system.systemType)
            if row == LATERAL:
                return QVariant(system.lateralType)
            if row == HMAX:
                return QVariant(system.maxHeight)
            if row == RU:
                return QVariant(system.Ru)
            if row == OMEGA0:
                return QVariant(system.phi0)
            if row == CD:
                return QVariant(system.cd)
            if row == TEXP:
                return QString.number(Texp, 'f', 2)
            if row == TEXP125:
                return QString.number(Texp * 1.25, 'f', 2)
            if row == TAN:
                return QString.number(Tan, 'f', 2)
            if row == K:
                return QString.number(k, 'f', 2)
            if row == CFACTOR:
                return QString.number(c, 'f', 4)
        if role == Qt.BackgroundColorRole:
            if row in (HMAX, TEXP125):
                return QVariant(QColor(250, 60, 0))
            if row in (K, CFACTOR):
                return QVariant(QColor(Qt.green))
            if row == TAN:
                if Tan <= 1.25 * Texp:
                    return QVariant(QColor(50, 120, 230))
                else:
                    return QVariant(QColor(Qt.yellow))
            #else:
                #return QVariant(QColor(Qt.cyan))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
        if role == Qt.ToolTipRole:
            if section == TEXP125:
                return QVariant(u'مقدار حداکثر زمان تناوب تحلیلی که در محاسبه نیروی زلزله میتوان استفاده کرد.')
            if section == HMAX:
                return QVariant(u'حداکثر ارتفاع مجاز سیستم مقاوم نیروی جانبی')
        if role == Qt.WhatsThisRole:
            if section == TEXP125:
                return QVariant(u'حداکثر زمان تناوبی که میتوان برای ')
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            if section == SYSTEM:
                return QVariant(u"سیستم سازه")
            if section == LATERAL:
                return QVariant(u'سیستم جانبی')
            if section == HMAX:
                return QVariant('Hm')
            if section == RU:
                return QVariant('Ru')
            if section == CD:
                return QVariant('Cd')
            if section == TEXP:
                return QVariant(u'زمان تناوب تجربی')
            if section == TEXP125:
                return QVariant(u'۱.۲۵ * زمان تناوب تجربی')
            if section == TAN:
                return QVariant(u'زمان تناوب تحلیلی')
            if section == K:
                return QVariant(u'K')
            if section == CFACTOR:
                return QVariant(u'ضریب زلزله')
            if section == OMEGA0:
                return QVariant(u'\omega 0')
        elif orientation == Qt.Horizontal:
            if section == X:
                return QVariant(u'X راستای')
            if section == Y:
                return QVariant(u'Y راستای')

    def rowCount(self, index=QModelIndex()):
        return 11

    def columnCount(self, index=QModelIndex()):
        return 2

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



if __name__ == '__main__':

    #app = QApplication(sys.argv)
    rf = ReflectionFactor("I", .35, 1)
    print
    #form = Form(rf)
    #form.show()

    #app.exec_()

    #x = StructureSystem(u'سیستم قاب ساختمانی', u'مهاربندی همگرای معمولی فولادی', "X")
    #y = StructureSystem(u'سیستم قاب خمشی', u'قاب خمشی فولادی ویژه', "Y")

    #print x.__str__()

    #myBuilding = Building(.3, 1.0, 'III', 3,
                        #10, None, x, y, u'تهران')

    #print myBuilding.maxHeight

    #print myBuilding
    #print html.encode(html)
    #result = type(myBuilding.checkInputs())



    #result = myBuilding.calculateC()
    #print result

    #Rux = myBuilding.xSystem.Ru
    #Ruy = myBuilding.ySystem.Ru

    #Cx = A * B * I / Rux
    #Cy = A * B * I / Ruy
    #A = myBuilding.calculateC()
    #print A


    ##print Cx, Cy
    #print myBuilding
    #print u'مشخصات سیستم در راستای x\n'
    #print myBuilding.xSystem
    #print u'مشخصات سیستم در راستای y\n'
    #print myBuilding.ySystem





