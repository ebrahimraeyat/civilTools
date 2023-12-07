# -*- coding: utf-8 -*-
from .soil import SoilTable
import numpy as np


class Building(object):

    ID1 = (3, 23, 33, 36)
    #ID2 = (21, 25,28)
    #ID3 = (25,)
    specialIDs = (11, 21, 25, 28, 31, 34, 41, 42, 45, 46, 47, 48, 51)
    IDs3354 = (31, 34, 41, 42, 43, 44, 45, 46, 47, 48, 49)
    moment_frames = range(31, 37)

    def __init__(self,
                 risk_level,
                 importance_factor,
                 soilType,
                 number_of_story,
                 height,
                 is_infill,
                 x_system,
                 y_system,
                 city,
                 x_period_an,
                 y_period_an,
                 x_system2= None,
                 y_system2= None,
                 height2: float=0,
                 is_infill2: bool=False,
                 ):

        self.filename = ''
        self.risk_level = risk_level
        self.acc = self.acceleration
        self.city = city
        self.importance_factor = importance_factor
        self.CMin = 0.12 * self.acc * self.importance_factor
        self.soilType = soilType
        self.soilProperties = SoilProperties(soilType, self.acc)
        self.number_of_story = number_of_story
        self.height = height
        self.height2 = height2
        self.is_infill = is_infill
        self.is_infill2 = is_infill2
        self.x_system = x_system
        self.y_system = y_system
        self.exp_period_x = self.period(x_system, height, is_infill)
        self.exp_period_y = self.period(y_system, height, is_infill)
        self.x_system2 = x_system2
        if x_system2:
            self.y_system2 = y_system2
            self.exp_period_x2 = self.period(x_system2, height2, is_infill2)
            self.exp_period_y2 = self.period(y_system2, height2, is_infill2)
            tx = (self.exp_period_x * height + self.exp_period_x2 * height2) / (height + height2)
            ty = (self.exp_period_y * height + self.exp_period_y2 * height2) / (height + height2)
            self.tx = max(min(x_period_an, 1.25 * tx), tx)
            self.ty = max(min(y_period_an, 1.25 * ty), ty)
        else:
            self.tx = max(min(x_period_an, 1.25 * self.exp_period_x), self.exp_period_x)
            self.ty = max(min(y_period_an, 1.25 * self.exp_period_y), self.exp_period_y)
        self.x_period_an = x_period_an
        self.y_period_an = y_period_an
        if np.isclose(importance_factor, 1.4, atol=.01):
            self.x_period_an = self.tx
            self.y_period_an = self.ty

        self.soil_reflection_prop_x = ReflectionFactor(soilType, self.acc, self.tx)
        self.soil_reflection_prop_y = ReflectionFactor(soilType, self.acc, self.ty)
        self.Bx = self.soil_reflection_prop_x.B
        self.By = self.soil_reflection_prop_y.B
        self.maxHeight = self.maxAllowedHeight()
        self.kx, self.ky = self.getK(self.tx, self.ty)
        self.results = self.calculateC(self.Bx, self.By)
        # analytical calculations for drift
        self.soil_reflection_drift_prop_x = ReflectionFactor(soilType, self.acc, self.x_period_an)
        self.soil_reflection_drift_prop_y = ReflectionFactor(soilType, self.acc, self.y_period_an)
        self.Bx_drift = min(self.Bx, self.soil_reflection_drift_prop_x.B)
        self.By_drift = min(self.By, self.soil_reflection_drift_prop_y.B)
        self.kx_drift, self.ky_drift = self.getK(self.x_period_an, self.y_period_an)
        self.results_drift = self.calculateC(self.Bx_drift, self.By_drift)

    @property
    def acceleration(self):
        accs = {u'کم': 0.20,
                u'متوسط': 0.25,
                u'زیاد': 0.3,
                u'خیلی زیاد': 0.35}
        return accs[self.risk_level]

    def period(self,
               system,
               height: float=0,
               is_infill: bool=False,
               ):
        alpha = system.alpha
        power = system.pow
        if height == 0:
            height = self.height

        if is_infill and system.ID in self.moment_frames:
            return 0.8 * alpha * height ** power
        else:
            return alpha * height ** power

    def direction(self):
        pass

    def maxAllowedHeight(self):
        xMaxAllowedHeight = self.x_system.maxHeight
        yMaxAllowedHeight = self.y_system.maxHeight
        if (xMaxAllowedHeight and yMaxAllowedHeight) is None:
            maxAllowedHeight = 200
        elif xMaxAllowedHeight is None:
            maxAllowedHeight = yMaxAllowedHeight
        elif yMaxAllowedHeight is None:
            maxAllowedHeight = xMaxAllowedHeight
        else:
            maxAllowedHeight = min(xMaxAllowedHeight, yMaxAllowedHeight)
        return maxAllowedHeight
    
    def max_allowed_height_x(self):
        x_max_allowed_height = self.x_system.maxHeight
        if x_max_allowed_height is None:
            x_max_allowed_height = 200
        return x_max_allowed_height
    
    def max_allowed_height_y(self):
        y_max_allowed_height = self.y_system.maxHeight
        if y_max_allowed_height is None:
            y_max_allowed_height = 200
        return y_max_allowed_height

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

    def getK(self, Tx, Ty):
        kx = self.calculateK(Tx)
        self._kxStr = self._kStr.format('x')
        ky = self.calculateK(Ty)
        self._kyStr = self._kStr.format('y')
        return kx, ky

    def getDEngheta(self):
        if self.number_of_story <= 8 and not self.importance_factor in (1.2, 1.4):
            return 0.005 * self.height * 100
        return False

    def checkInputs(self):

        class StructureSystemError(Exception):
            pass

        title = u"سیستم مقاوم در برابر نیروی جانبی در راستای '%s' را تغییر دهید."
        e1 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت خیلی زیاد و زیاد" در تمام مناطق لرزه خیزی مجاز نیست.'
        e2 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۱ و ۲ مجاز نیست.'
        e3 = u'ارتفاع حداکثر سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۳و ۴ به ۱۵ متر محدود میگردد.'
        e4 = u'در مناطق با خطر نسبی خیلی زیاد برای ساختمانهای با "اهمیت خیلی زیاد" فقط باید از سیستم هایی که عنوان "ویژه" دارند، استفاده شود.'
        e5 = u'در ساختمانهای با بیشتر از ۱۵ طبقه و یا بلندتر از ۵۰ متر، استفاده از سیستم قاب خمشی ویژه و یا سیستم دوگانه الزامی است.'
        e6 = 'حداکثر ارتفاع مجاز سازه %i متر می باشد.'

        ID1 = self.ID1
        specialIDs = self.specialIDs
        IDs3354 = self.IDs3354
        I = self.importance_factor
        A = self.acc
        H = self.height
        story = self.number_of_story
        max_height_x = self.max_allowed_height_x()
        max_height_y = self.max_allowed_height_y()

        for direction in ("X", "Y"):
            if direction == "X":
                ID = self.x_system.ID
                # systemType = self.x_system.systemType
                lateralType = self.x_system.lateralType
            else:
                ID = self.y_system.ID
                # systemType = self.y_system.systemType
                lateralType = self.y_system.lateralType
            try:
                if direction == 'X' and self.height > max_height_x:
                    raise StructureSystemError(e6 % max_height_x)
                elif direction == 'Y' and self.height > max_height_y:
                    raise StructureSystemError(e6 % max_height_y)
                if ID in ID1:
                    if I > 1.1:
                        raise StructureSystemError(e1 % lateralType)

                    if I == 1.0 and A in (.3, .35):
                        raise StructureSystemError(e2 % lateralType)

                    if I == 1.0 and A in (.2, .25) and H > 15:
                        raise StructureSystemError(e3 % lateralType)

                if A == 0.35 and I == 1.4 and (ID not in specialIDs):
                    raise StructureSystemError(e4)

                if (H > 50 or story > 15) and (ID not in IDs3354):
                    raise StructureSystemError(e5)

            except StructureSystemError as err:
                return False, title, err, direction
        return [True]

    def calculateC(self, Bx, By):
        check_inputs = self.checkInputs()
        # TODO
        if check_inputs[0] is False:
            return check_inputs
        A = self.acc
        I = self.importance_factor
        if self.x_system2:
            if self.x_system.Ru >= self.x_system2.Ru:
                Rux = self.x_system2.Ru
            if self.y_system.Ru >= self.y_system2.Ru:
                Ruy = self.y_system2.Ru
        else:
            Rux = self.x_system.Ru
            Ruy = self.y_system.Ru
        CxNotApproved = A * Bx * I / Rux
        CyNotApproved = A * By * I / Ruy
        if CxNotApproved < self.CMin:
            Cx = self.CMin
            self.cxStr = (u"{0:.4f} &#60 C<sub>min</sub> &#8658 Cx = {1}</p>"
                          ).format(CxNotApproved, self.CMin)
        else:
            Cx = CxNotApproved
            self.cxStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(CxNotApproved)
        if CyNotApproved < self.CMin:
            Cy = self.CMin
            self.cyStr = (u" {0:.4f} &#60 C<sub>min</sub> &#8658 Cy = {1}</p>"
                          ).format(CyNotApproved, self.CMin)
        else:
            Cy = CyNotApproved
            self.cyStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(CyNotApproved)
        return True, Cx, Cy
        # else:
        #     return check_inputs

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
        self.is_infill = Rus[6]
        self.ID = Rus[7]

    def __eq__(self, another):
        if self.systemType == another.systemType and \
                self.lateralType == another.lateralType:
            return True
        return False

    def __str__(self):
        return f'''
            system type is {self.systemType}\n
            lateral system is {self.lateralType}\n
            Ru = {self.Ru}\n
            omega = {self.phi0}\n
            cd = {self.cd}\n
            maximum height = {self.maxHeight}\n
            '''


class RFactorTable(object):

    def __init__(self):
        from . import RuTable
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
