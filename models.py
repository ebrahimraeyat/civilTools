from PySide2.QtCore import QAbstractTableModel, Qt, QSettings, QModelIndex
from PySide2.QtWidgets import QDoubleSpinBox, QItemDelegate, QComboBox, QMessageBox
from PySide2.QtGui import QFont, QColor
from PySide2 import  QtWidgets


X, Y = range(2)
CFACTOR, K, TAN, CDRIFT, KDRIFT, TEXP125, TEXP, SYSTEM, LATERAL, RU, HMAX, OMEGA0, CD = range(13)
MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1

QVariant = str


class StructureModel(QAbstractTableModel):

    def __init__(self, build):
        # super(StructureModel, self).__init__()
        QAbstractTableModel.__init__(self)
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
            return ''
        row = index.row()
        column = index.column()
        c = ''
        c_drift = ''
        if column == X:
            system = self.build.x_system
            Texp = self.build.exp_period_x
            Tan = self.build.x_period_an
            k = self.build.kx
            k_drift = self.build.kx_drift
            if self.build.results[0]:
                c = self.build.results[1]
            if self.build.results_drift[0]:
                c_drift = self.build.results_drift[1]

        if column == Y:
            system = self.build.y_system
            Texp = self.build.exp_period_y
            Tan = self.build.y_period_an
            k = self.build.ky
            k_drift = self.build.ky_drift
            if self.build.results[0]:
                c = self.build.results[2]
            if self.build.results_drift[0]:
                c_drift = self.build.results_drift[2]
        if role == Qt.DisplayRole:
            if row == SYSTEM:
                return system.systemType
            if row == LATERAL:
                return system.lateralType
            if row == HMAX:
                return str(system.maxHeight)
            if row == RU:
                return str(system.Ru)
            if row == OMEGA0:
                return str(system.phi0)
            if row == CD:
                return str(system.cd)
            if row == TEXP:
                return '{0:.4f}'.format(Texp)
            if row == TEXP125:
                return '{0:.4f}'.format(Texp * 1.25)
            if row == TAN:
                return '{0:.4f}'.format(Tan)
            if row == K:
                return '{0:.4f}'.format(k)
            if row == CFACTOR:
                try:
                    return '{0:.4f}'.format(c)
                except:
                    pass
            if row == KDRIFT:
                return '{0:.4f}'.format(k_drift)
            if row == CDRIFT:
                try:
                    return '{0:.4f}'.format(c_drift)
                except:
                    pass
        if role == Qt.BackgroundColorRole:
            # if row == HMAX:
            #     return QColor(255, 140, 140)
            if row in (K, CFACTOR):
                return QColor(100, 255, 100)
            if row in (KDRIFT, CDRIFT):
                return QColor(100, 100, 255)
            if row == TAN:
                return QColor(255, 255, 20)
            else:
                return QColor(230, 230, 250)
        if role == Qt.FontRole:
            if row in (K, CFACTOR, KDRIFT, CDRIFT):
                font = QFont()
                font.setBold(True)
                font.setItalic(True)
                font.setPointSize(12)
                return font
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if orientation == Qt.Vertical:
                # if section == HMAX:
                #     return QColor(255, 80, 80)
                if section in (K, CFACTOR):
                    return QColor(120, 255, 120)
                elif section in (KDRIFT, CDRIFT):
                    return QColor(120, 120, 255)
                elif section == TAN:
                    return QColor(250, 250, 100)
                else:
                    return QColor(230, 230, 250)
        elif role == Qt.ToolTipRole:
            if section == TEXP125:
                return 'مقدار حداکثر زمان تناوب تحلیلی که در محاسبه نیروی زلزله میتوان استفاده کرد.'
            elif section == HMAX:
                return 'حداکثر ارتفاع مجاز سیستم مقاوم نیروی جانبی'
        elif role == Qt.WhatsThisRole:
            if section == TEXP125:
                return 'حداکثر زمان تناوبی که میتوان برای '
        elif role == Qt.FontRole:
            if orientation == Qt.Vertical:
                if section in (K, CFACTOR, KDRIFT, CDRIFT):
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(12)
                    return font
        elif role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                if section == SYSTEM:
                    return "سیستم سازه"
                elif section == LATERAL:
                    return 'سیستم جانبی'
                elif section == HMAX:
                    return 'H_max'
                elif section == RU:
                    return 'Ru'
                elif section == CD:
                    return 'Cd'
                elif section == TEXP:
                    return 'زمان تناوب تجربی'
                elif section == TEXP125:
                    return '۱.۲۵ * زمان تناوب تجربی'
                elif section == TAN:
                    return 'زمان تناوب تحلیلی'
                elif section == K:
                    return 'K'
                elif section == CFACTOR:
                    return 'C'
                elif section == OMEGA0:
                    return 'omega_0'
                elif section == KDRIFT:
                    return 'K_drift'
                elif section == CDRIFT:
                    return 'C_drift'
            elif orientation == Qt.Horizontal:
                if section == X:
                    return 'X راستای'
                elif section == Y:
                    return 'Y راستای'

    def rowCount(self, index=QModelIndex()):
        return 13

    def columnCount(self, index=QModelIndex()):
        return 2

    