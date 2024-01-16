# -*- coding: utf-8 -*-
from .soil import SoilTable
import numpy as np


class Building(object):

    ID1 = (3, 23, 33, 36)
    #ID2 = (21, 25,28)
    #ID3 = (25,)
    special_ids = (11, 21, 25, 28, 31, 34, 41, 42, 45, 46, 47, 48, 51)
    ids_3354 = (31, 34, 41, 42, 43, 44, 45, 46, 47, 48, 49)
    moment_frames = range(31, 37)

    def __init__(self,
                 risk_level,
                 importance_factor,
                 soil_type,
                 city,
                 number_of_story_1,
                 height_1,
                 is_infill_1,
                 x_system_1,
                 y_system_1,
                 tx_an_1,
                 ty_an_1,
                 x_system_2= None,
                 y_system_2= None,
                 height_2: float=0,
                 is_infill_2: bool=False,
                 number_of_story_2: int=0,
                 tx_an_2: float=4,
                 ty_an_2: float=4,
                 tx_an_all: float=4,
                 ty_an_all: float=4,
                 ):
        self.risk_level = risk_level
        self.acc = self.acceleration
        self.city = city
        self.importance_factor = importance_factor
        self.soil_type = soil_type
        self.c_min = 0.12 * self.acc * self.importance_factor
        self.soil_properties = SoilProperties(soil_type, self.acc)
        self.number_of_story = number_of_story_1
        self.height = height_1
        self.is_infill = is_infill_1
        self.x_system = x_system_1
        self.y_system = y_system_1
        self.tx_an = tx_an_1
        self.ty_an = ty_an_1

        self.tx_exp = self.period(x_system_1, height_1, is_infill_1)
        self.ty_exp = self.period(y_system_1, height_1, is_infill_1)
        if np.isclose(importance_factor, 1.4, atol=.01):
            self.tx_an = self.tx_exp
            self.ty_an = self.ty_exp
        self.tx = max(min(self.tx_an, 1.25 * self.tx_exp), self.tx_exp)
        self.ty = max(min(self.ty_an, 1.25 * self.ty_exp), self.ty_exp)

        self.soil_reflection_prop_x = ReflectionFactor(self.soil_type, self.acc, self.tx)
        self.soil_reflection_prop_y = ReflectionFactor(self.soil_type, self.acc, self.ty)
        self.bx = self.soil_reflection_prop_x.B
        self.by = self.soil_reflection_prop_y.B
        self.max_height = self.max_allowed_height_systems(self.x_system, self.y_system)
        self.kx, self.ky = self.get_k(self.tx, self.ty)
        self.results = self.calculate_c(self.bx, self.by, self.x_system, self.y_system, self.height, self.number_of_story)
        self.soil_reflection_drift_prop_x = ReflectionFactor(self.soil_type, self.acc, self.tx_an)
        self.soil_reflection_drift_prop_y = ReflectionFactor(self.soil_type, self.acc, self.ty_an)
        self.bx_drift = min(self.bx, self.soil_reflection_drift_prop_x.B)
        self.by_drift = min(self.by, self.soil_reflection_drift_prop_y.B)
        self.kx_drift, self.ky_drift = self.get_k(self.tx_an, self.ty_an)
        self.results_drift = self.calculate_c(self.bx_drift, self.by_drift, self.x_system, self.y_system, self.height, self.number_of_story)
        self.building2 = None
        if x_system_2 is not None:
            self.building2 = Building(
                risk_level,
                importance_factor,
                soil_type,
                city,
                number_of_story_2,
                height_2,
                is_infill_2,
                x_system_2,
                y_system_2,
                tx_an_2,
                ty_an_2,
            )
            self.tx_an_all = tx_an_all
            self.ty_an_all = ty_an_all
            self.tx_exp_all = (self.tx_exp * height_1 + self.building2.tx_exp * self.building2.height) / (height_1 + self.building2.height)
            self.ty_exp_all = (self.ty_exp * height_1 + self.building2.ty_exp * self.building2.height) / (height_1 + self.building2.height)
            self.tx_all = max(min(self.tx_an_all, 1.25 * self.tx_exp_all), self.tx_exp_all)
            self.ty_all = max(min(self.ty_an_all, 1.25 * self.ty_exp_all), self.ty_exp_all)
            if np.isclose(importance_factor, 1.4, atol=.01):
                self.tx_an_all = self.tx_all
                self.ty_an_all = self.ty_all
            self.soil_reflection_prop_all_x = ReflectionFactor(self.soil_type, self.acc, self.tx_all)
            self.soil_reflection_prop_all_y = ReflectionFactor(self.soil_type, self.acc, self.ty_all)
            self.bx_all = self.soil_reflection_prop_all_x.B
            self.by_all = self.soil_reflection_prop_all_y.B
            self.kx_all, self.ky_all = self.get_k(self.tx_all, self.ty_all)
            self.results_all_bot = self.calculate_c(self.bx_all, self.by_all, x_system_1, y_system_1, height_1, number_of_story_1)
            self.results_all_top = self.calculate_c(self.bx_all, self.by_all, x_system_2, y_system_2, height_2, number_of_story_2)
            # analytical calculations for drift
            self.soil_reflection_drift_prop_all_x = ReflectionFactor(self.soil_type, self.acc, self.tx_an_all)
            self.soil_reflection_drift_prop_all_y = ReflectionFactor(self.soil_type, self.acc, self.ty_an_all)
            self.bx_drift_all = min(self.bx_all, self.soil_reflection_drift_prop_all_x.B)
            self.by_drift_all = min(self.by_all, self.soil_reflection_drift_prop_all_y.B)
            self.kx_drift_all, self.ky_drift_all = self.get_k(self.tx_an_all, self.ty_an_all)
            self.results_drift_all_bot = self.calculate_c(self.bx_drift_all, self.by_drift_all, x_system_1, y_system_1, height_1, number_of_story_1)
            self.results_drift_all_top = self.calculate_c(self.bx_drift_all, self.by_drift_all, x_system_2, y_system_2, height_2, number_of_story_2)

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

    def max_allowed_height_systems(self, x_system, y_system):
        x_max_allowed_height = x_system.max_height
        y_max_allowed_height = y_system.max_height
        if (x_max_allowed_height and y_max_allowed_height) is None:
            max_allowed_height = 200
        elif x_max_allowed_height is None:
            max_allowed_height = y_max_allowed_height
        elif y_max_allowed_height is None:
            max_allowed_height = x_max_allowed_height
        else:
            max_allowed_height = min(x_max_allowed_height, y_max_allowed_height)
        return max_allowed_height
    
    def max_allowed_height_system(self, system):
        x_max_allowed_height = system.max_height
        if x_max_allowed_height is None:
            x_max_allowed_height = 200
        return x_max_allowed_height
    
    def calculate_k(self, t):
        if t < 0.5:
            self._kStr = u'T &#60 0.5 '
            return 1.0
        elif t > 2.5:
            self._kStr = u'T &#62 2.5 '
            return 2.0
        else:
            self._kStr = u' 0.5 &#60 T &#60 2.5 &#8658 k<sub>{0}</sub> = 0.5 &#215 T + 0.75'
            return 0.5 * t + 0.75

    def get_k(self, tx, ty):
        kx = self.calculate_k(tx)
        self._kxStr = self._kStr.format('x')
        ky = self.calculate_k(ty)
        self._kyStr = self._kStr.format('y')
        return kx, ky

    def get_engheta(self):
        if self.number_of_story <= 8 and self.importance_factor not in (1.2, 1.4):
            return 0.005 * self.height * 100
        return False

    def check_inputs(self, x_system, y_system, height, number_of_story):

        class StructureSystemError(Exception):
            pass

        title = u"سیستم مقاوم در برابر نیروی جانبی در راستای '%s' را تغییر دهید."
        e1 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت خیلی زیاد و زیاد" در تمام مناطق لرزه خیزی مجاز نیست.'
        e2 = u'استفاده از سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۱ و ۲ مجاز نیست.'
        e3 = u'ارتفاع حداکثر سیستم "%s" برای ساختمانهای "با اهمیت متوسط" در مناطق لرزه خیزی ۳و ۴ به ۱۵ متر محدود میگردد.'
        e4 = u'در مناطق با خطر نسبی خیلی زیاد برای ساختمانهای با "اهمیت خیلی زیاد" فقط باید از سیستم هایی که عنوان "ویژه" دارند، استفاده شود.'
        e5 = u'در ساختمانهای با بیشتر از ۱۵ طبقه و یا بلندتر از ۵۰ متر، استفاده از سیستم قاب خمشی ویژه و یا سیستم دوگانه الزامی است.'
        e6 = 'حداکثر ارتفاع مجاز سازه %i متر می باشد.'

        max_height_x = self.max_allowed_height_system(x_system)
        max_height_y = self.max_allowed_height_system(y_system)

        for direction in ("X", "Y"):
            if direction == "X":
                ID = x_system.ID
                lateral_type = x_system.lateral_type
            else:
                ID = y_system.ID
                lateral_type = y_system.lateral_type
            try:
                if direction == 'X' and height > max_height_x:
                    raise StructureSystemError(e6 % max_height_x)
                elif direction == 'Y' and height > max_height_y:
                    raise StructureSystemError(e6 % max_height_y)
                if ID in self.ID1:
                    if self.importance_factor > 1.1:
                        raise StructureSystemError(e1 % lateral_type)

                    if np.isclose(self.importance_factor, 1.0, atol=1e-09) and self.acc in (.3, .35):
                        raise StructureSystemError(e2 % lateral_type)

                    if np.isclose(self.importance_factor, 1.0, atol=1e-09) and self.acc in (.2, .25) and height > 15:
                        raise StructureSystemError(e3 % lateral_type)

                if np.isclose(self.acc, 0.35, atol=1e-09) and np.isclose(self.importance_factor, 1.4, atol=1e-09) and (ID not in self.special_ids):
                    raise StructureSystemError(e4)

                if (height > 50 or number_of_story > 15) and (ID not in self.ids_3354):
                    raise StructureSystemError(e5)

            except StructureSystemError as err:
                return False, title, err, direction
        return [True]

    def calculate_c(self, bx, by, x_system, y_system, height, number_of_story):
        check_inputs = self.check_inputs(x_system, y_system, height, number_of_story)
        if check_inputs[0] is False:
            return check_inputs
        cx_not_approved = self.acc * bx * self.importance_factor / x_system.Ru
        cy_not_approved = self.acc * by * self.importance_factor / y_system.Ru
        if cx_not_approved < self.c_min:
            cx = self.c_min
            self.cxStr = (u"{0:.4f} &#60 C<sub>min</sub> &#8658 Cx = {1}</p>"
                          ).format(cx_not_approved, self.c_min)
        else:
            cx = cx_not_approved
            self.cxStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(cx_not_approved)
        if cy_not_approved < self.c_min:
            cy = self.c_min
            self.cyStr = (u" {0:.4f} &#60 C<sub>min</sub> &#8658 Cy = {1}</p>"
                          ).format(cy_not_approved, self.c_min)
        else:
            cy = cy_not_approved
            self.cyStr = (u"{0:.4f} &#62 C<sub>min</sub>  O.K</p>").format(cy_not_approved)
        return True, cx, cy


class StructureSystem(object):

    def __init__(self, system, lateral, direction='X'):
        self.systemType = system
        self.lateral_type = lateral
        self.direction = direction
        rFactorTable = RFactorTable()
        rTable = rFactorTable.structureSystems
        Rus = rTable[system][lateral]
        self.Ru = Rus[0]
        self.phi0 = Rus[1]
        self.cd = Rus[2]
        self.max_height = Rus[3]
        self.alpha = Rus[4]
        self.pow = Rus[5]
        self.is_infill = Rus[6]
        self.ID = Rus[7]

    def __eq__(self, another):
        if self.systemType == another.systemType and \
                self.lateral_type == another.lateral_type:
            return True
        return False

    def __str__(self):
        return f'''
            system type is {self.systemType}\n
            lateral system is {self.lateral_type}\n
            Ru = {self.Ru}\n
            omega = {self.phi0}\n
            cd = {self.cd}\n
            maximum height = {self.max_height}\n
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

    def __init__(self, soil_type, acc):
        soilTable = SoilTable()
        self.soil_type = soil_type
        self.T0 = soilTable.T0s[soil_type]
        self.Ts = soilTable.Tss[soil_type]
        self.S = soilTable.Ss[(soil_type, acc)]
        self.S0 = soilTable.S0s[(soil_type, acc)]

class ReflectionFactor(object):

    def __init__(self, soil_type, acc, period):
        soil_properties = SoilProperties(soil_type, acc)
        self.soil_type = soil_type
        self.A = acc
        self.T = period
        self.T0 = soil_properties.T0
        self.Ts = soil_properties.Ts
        self.S = soil_properties.S
        self.S0 = soil_properties.S0
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
        if self.soil_type == "I":
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
