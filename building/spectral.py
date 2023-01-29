# -*- coding: utf-8 -*-
from .soil import SoilTable
import numpy as np


class SoilProperties(object):

    def __init__(self, soilType, acc):
        soilTable = SoilTable()
        self.soilType = soilType
        self.T0 = soilTable.T0s[soilType]
        self.Ts = soilTable.Tss[soilType]
        self.S = soilTable.Ss[(soilType, acc)]
        self.S0 = soilTable.S0s[(soilType, acc)]

class ReflectionFactor(object):

    def __init__(self, soilType, acc):
        soilProperties = SoilProperties(soilType, acc)
        self.soilType = soilType
        self.A = acc
        self.T0 = soilProperties.T0
        self.Ts = soilProperties.Ts
        self.S = soilProperties.S
        self.S0 = soilProperties.S0
        self.dt = 0.01
        self.endT = 4.5
        self.numberOfSamples = self.endT // self.dt - 1

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
        self.b1_curve = self.B1Curve()
        self.n_curve = self.NCurve()
        return self.b1_curve * self.n_curve
    
    def calculatB1(self, T):
        # calculating B1
        if 0 < T < self.T0:
            return self.S0 + (self.S - self.S0 + 1) * (T / self.T0)
        elif self.T0 <= T < self.Ts:
            return self.S + 1
        else:
            return (self.S + 1) * (self.Ts / T)

    def calculatN(self, T):

        # calculating N
        if self.A > 0.27:
            if T < self.Ts:
                N = 1
            elif self.Ts <= T < 4:
                N = .7 * (T - self.Ts) / (4 - self.Ts) + 1
            else:
                N = 1.7
        else:
            if T < self.Ts:
                N = 1
            elif self.Ts <= T < 4:
                N = .4 * (T - self.Ts) / (4 - self.Ts) + 1
            else:
                N = 1.4
        return N
    
    def calculatB(self, T):
        return self.calculatB1(T) * self.calculatN(T)
